// SPDX-License-Identifier: MIT
/* =============================================================================
 * LAP-BAR ACTUATOR CONTROLLER  —  ESP32  (autonomous ZT X 52 retrofit)
 *
 * Closes the position loop ArduPilot can't: the Pixhawk outputs a throttle PWM
 * per side (skid-steer); this reads those, reads each actuator's feedback pot,
 * runs a PID, and drives a BTS7960 H-bridge until each lap bar is at position.
 *
 * FAIL-TO-NEUTRAL (safety): if the e-stop opens OR the FC pulse train is lost
 * (> FAILSAFE_MS), both bars are driven to NEUTRAL (center) and the drivers are
 * disabled, so the hydros return to neutral and the machine coasts to a stop.
 *
 * Board: ESP32 DevKit (38-pin).  Drivers: 2x BTS7960 (IBT-2).
 * See docs/WIRING.md for the full harness + pinout.  Tune the *_CAL + PID below.
 * ============================================================================= */
#include <Arduino.h>

// ---- pin map (must match docs/WIRING.md) -----------------------------------
// FC throttle PWM inputs (input-only GPIOs, interrupt-capable)
const int PIN_PWM_L = 34;
const int PIN_PWM_R = 35;
// Actuator feedback pots (ADC1, input-only). Wiper -> these; ends to 3V3 / GND.
const int PIN_POT_L = 36;   // VP
const int PIN_POT_R = 39;   // VN
// E-stop sense: e-stop NC contact between this pin and GND. OK=LOW, tripped=HIGH.
const int PIN_ESTOP = 25;
// BTS7960 #1 (LEFT):  RPWM, LPWM (PWM via LEDC), R_EN, L_EN (digital enable)
const int L_RPWM = 16, L_LPWM = 17, L_REN = 18, L_LEN = 19;
// BTS7960 #2 (RIGHT)
const int R_RPWM = 26, R_LPWM = 27, R_REN = 14, R_LEN = 12;
const int PIN_LED = 2;      // onboard status LED

// ---- tuning ----------------------------------------------------------------
const int   PWM_MIN = 1000, PWM_MID = 1500, PWM_MAX = 2000;  // FC servo PWM (us)
const int   PWM_DEADBAND = 25;          // us around mid = neutral
const int   POT_L_MIN = 200, POT_L_MAX = 3900;   // CAL: pot raw at full-retract/extend
const int   POT_R_MIN = 200, POT_R_MAX = 3900;   // CAL each actuator
const float KP = 6.0, KI = 0.0, KD = 0.4;        // PID (start P-only; add D to damp)
const int   POS_DEADBAND = 30;          // raw counts: stop hunting near target
const int   DUTY_MAX = 230;             // cap H-bridge duty (0-255)
const int   DUTY_MIN = 40;              // overcome stiction
const unsigned long FAILSAFE_MS = 400;  // no FC pulse this long -> neutral

// ---- PWM input capture (ISR) ----------------------------------------------
volatile unsigned long riseL = 0, riseR = 0, pulseL = PWM_MID, pulseR = PWM_MID;
volatile unsigned long lastEdgeL = 0, lastEdgeR = 0;
void IRAM_ATTR isrL() {
  if (digitalRead(PIN_PWM_L)) riseL = micros();
  else { unsigned long w = micros() - riseL; if (w > 700 && w < 2300) { pulseL = w; lastEdgeL = millis(); } }
}
void IRAM_ATTR isrR() {
  if (digitalRead(PIN_PWM_R)) riseR = micros();
  else { unsigned long w = micros() - riseR; if (w > 700 && w < 2300) { pulseR = w; lastEdgeR = millis(); } }
}

// ---- LEDC PWM channels for the 4 BTS7960 PWM pins --------------------------
const int CH_L_R = 0, CH_L_L = 1, CH_R_R = 2, CH_R_L = 3;
void setupDriver(int rpwm, int lpwm, int ren, int len, int chR, int chL) {
  pinMode(ren, OUTPUT); pinMode(len, OUTPUT);
  digitalWrite(ren, HIGH); digitalWrite(len, HIGH);     // enable both half-bridges
  ledcSetup(chR, 20000, 8); ledcAttachPin(rpwm, chR);   // 20 kHz, 8-bit
  ledcSetup(chL, 20000, 8); ledcAttachPin(lpwm, chL);
}
// duty: -255..255  (+ = extend, - = retract)
void drive(int chR, int chL, int duty) {
  duty = constrain(duty, -DUTY_MAX, DUTY_MAX);
  if (duty >= 0) { ledcWrite(chR, duty); ledcWrite(chL, 0); }
  else           { ledcWrite(chR, 0);    ledcWrite(chL, -duty); }
}
void disableAll() { ledcWrite(CH_L_R,0); ledcWrite(CH_L_L,0); ledcWrite(CH_R_R,0); ledcWrite(CH_R_L,0);
  digitalWrite(L_REN,LOW); digitalWrite(L_LEN,LOW); digitalWrite(R_REN,LOW); digitalWrite(R_LEN,LOW); }
void enableAll() { digitalWrite(L_REN,HIGH); digitalWrite(L_LEN,HIGH); digitalWrite(R_REN,HIGH); digitalWrite(R_LEN,HIGH); }

// ---- per-side PID ----------------------------------------------------------
struct PID { float i=0, prev=0; } pidL, pidR;
int step(PID &s, int target, int actual) {
  if (abs(target - actual) < POS_DEADBAND) { s.i = 0; return 0; }
  float e = target - actual;
  s.i = constrain(s.i + e, -2000, 2000);
  float d = e - s.prev; s.prev = e;
  float u = KP*e + KI*s.i + KD*d;
  int duty = (int)(u * 0.06);                 // scale error(counts)->duty
  if (duty != 0 && abs(duty) < DUTY_MIN) duty = (duty>0?DUTY_MIN:-DUTY_MIN);
  return duty;
}

int targetFromPwm(int us, int potMin, int potMax) {
  if (abs(us - PWM_MID) < PWM_DEADBAND) return (potMin + potMax) / 2;   // neutral
  return map(constrain(us, PWM_MIN, PWM_MAX), PWM_MIN, PWM_MAX, potMin, potMax);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_PWM_L, INPUT); pinMode(PIN_PWM_R, INPUT);
  pinMode(PIN_ESTOP, INPUT_PULLUP); pinMode(PIN_LED, OUTPUT);
  attachInterrupt(PIN_PWM_L, isrL, CHANGE);
  attachInterrupt(PIN_PWM_R, isrR, CHANGE);
  setupDriver(L_RPWM, L_LPWM, L_REN, L_LEN, CH_L_R, CH_L_L);
  setupDriver(R_RPWM, R_LPWM, R_REN, R_LEN, CH_R_R, CH_R_L);
  Serial.println("lapbar_controller ready");
}

void loop() {
  unsigned long now = millis();
  bool estop = digitalRead(PIN_ESTOP);                 // HIGH = tripped (NC opened)
  bool lostL = (now - lastEdgeL) > FAILSAFE_MS;
  bool lostR = (now - lastEdgeR) > FAILSAFE_MS;
  bool fail  = estop || lostL || lostR;

  int potL = analogRead(PIN_POT_L), potR = analogRead(PIN_POT_R);
  int tgtL = fail ? (POT_L_MIN+POT_L_MAX)/2 : targetFromPwm(pulseL, POT_L_MIN, POT_L_MAX);
  int tgtR = fail ? (POT_R_MIN+POT_R_MAX)/2 : targetFromPwm(pulseR, POT_R_MIN, POT_R_MAX);

  if (fail) {                                          // FAIL-TO-NEUTRAL
    enableAll();                                       // keep bridges live just long enough
    drive(CH_L_R, CH_L_L, step(pidL, tgtL, potL));     // drive bars to center
    drive(CH_R_R, CH_R_L, step(pidR, tgtR, potR));
    bool centered = abs(tgtL-potL)<POS_DEADBAND && abs(tgtR-potR)<POS_DEADBAND;
    if (centered) disableAll();                        // then cut power (coast to neutral)
    digitalWrite(PIN_LED, (now/120)%2);                // fast blink = failsafe
  } else {
    enableAll();
    drive(CH_L_R, CH_L_L, step(pidL, tgtL, potL));
    drive(CH_R_R, CH_R_L, step(pidR, tgtR, potR));
    digitalWrite(PIN_LED, HIGH);                       // solid = armed/ok
  }

  static unsigned long tlog = 0;
  if (now - tlog > 500) { tlog = now;
    Serial.printf("L pwm%lu pot%d tgt%d | R pwm%lu pot%d tgt%d | %s\n",
      pulseL, potL, tgtL, pulseR, potR, tgtR, fail ? "FAILSAFE" : "run"); }
  delay(10);                                           // ~100 Hz loop
}
