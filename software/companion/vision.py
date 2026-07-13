# SPDX-License-Identifier: MIT
"""
Camera-AI vision — front-camera obstacle/grass detection feeding the safety layer.

Two interchangeable detector backends behind one interface:
  - HailoDetector : runs a compiled model (.hef) on the Pi AI HAT+ (Hailo-8L) over a
                    picamera2 frame. Real hardware. Imports are lazy/guarded.
  - SimDetector   : synthesizes plausible detections so the pipeline runs with no hardware.

The pure `evaluate()` maps a detection list → a safety verdict (hazard in the stop-zone →
obstacle). That function is unit-tested; the model/camera I/O is validated on hardware.
Detections flow into the shared State (obstacle / obstacle_range / objects / grass_pct),
which `safety.py` already consumes.
"""
import math, time

# hazard classes that must stop the mower if they're in the path
HAZARD = {"person", "animal", "pet", "child", "vehicle", "obstacle", "toy"}
# stop-zone in normalized frame coords (cx,cy): centred horizontally, lower half = close ahead
ZONE_X = (0.28, 0.72)
ZONE_Y_NEAR = 0.55
CONF_MIN = 0.40

def _in_stop_zone(box):
    """box = [cx, cy, w, h] normalized (0..1). True if its centre is in the path stop-zone."""
    cx, cy = box[0], box[1]
    return ZONE_X[0] <= cx <= ZONE_X[1] and cy >= ZONE_Y_NEAR

def evaluate(detections):
    """PURE. detections: [{cls, conf, box:[cx,cy,w,h]}, ...].
    Returns (obstacle: bool, range_m: float|None, objects: [str], grass_pct: int)."""
    hazards = [d for d in detections
               if d.get("cls") in HAZARD and d.get("conf", 1.0) >= CONF_MIN and _in_stop_zone(d["box"])]
    objects = sorted({d["cls"] for d in detections if d.get("conf", 1.0) >= CONF_MIN})
    grass = [d for d in detections if d.get("cls") == "grass"]
    grass_pct = int(round(sum(d["box"][2] * d["box"][3] for d in grass) * 100)) if grass else 0
    grass_pct = max(0, min(100, grass_pct))
    if hazards:
        nearest = max(hazards, key=lambda d: d["box"][1])      # largest cy ≈ closest
        range_m = round((1.0 - nearest["box"][1]) * 6.0 + 0.4, 1)
        return True, range_m, objects, grass_pct
    return False, None, objects, grass_pct


class SimDetector:
    """Synthetic detections so the vision pipeline runs without a camera/Hailo."""
    name = "sim"
    def detect(self, t):
        dets = [{"cls": "grass", "conf": 0.95, "box": [0.5, 0.8, 0.9, 0.45]}]
        # a person wanders into the path every ~40 s for a few seconds
        if int(t) % 40 < 4:
            cx = 0.5 + 0.05 * math.sin(t)
            dets.append({"cls": "person", "conf": 0.88, "box": [cx, 0.62, 0.18, 0.4]})
        elif int(t) % 67 < 3:
            dets.append({"cls": "obstacle", "conf": 0.7, "box": [0.46, 0.6, 0.2, 0.25]})
        return dets


class HailoDetector:
    """Hardware backend: Hailo-8L (.hef) + picamera2. Lazy imports so this file always loads."""
    name = "hailo"
    def __init__(self, hef_path, labels):
        from picamera2 import Picamera2                # noqa
        from hailo_platform import (HEF, VDevice, ConfigureParams,        # noqa
                                    HailoStreamInterface, InferVStreams,
                                    InputVStreamParams, OutputVStreamParams)
        self.labels = labels
        self.cam = Picamera2()
        self.cam.configure(self.cam.create_preview_configuration(main={"size": (640, 640)}))
        self.cam.start()
        self.hef = HEF(hef_path)
        self.target = VDevice()
        cfg = ConfigureParams.create_from_hef(self.hef, interface=HailoStreamInterface.PCIe)
        self.net = self.target.configure(self.hef, cfg)[0]
        self.in_params = InputVStreamParams.make(self.net)
        self.out_params = OutputVStreamParams.make(self.net)

    def detect(self, t):
        frame = self.cam.capture_array()              # HWC uint8
        from hailo_platform import InferVStreams
        with InferVStreams(self.net, self.in_params, self.out_params) as pipe:
            raw = pipe.infer({list(self.in_params)[0]: frame[None, ...]})
        return self._postprocess(raw)                  # → [{cls,conf,box}] (model-specific)

    def _postprocess(self, raw):
        # Map the model's raw output to {cls,conf,box[cx,cy,w,h]}. Fill in for your .hef
        # (e.g. a YOLOv8n trained on grass/person/obstacle, compiled with the Hailo DFC).
        return []


def make_detector(hef_path=None, labels=None):
    if hef_path:
        try:
            return HailoDetector(hef_path, labels or [])
        except Exception as e:
            print(f"[vision] Hailo unavailable ({e}); using sim detector")
    return SimDetector()


def run_vision(S, detector, hz=5):
    """Loop: pull detections → write obstacle/objects/grass_pct into the shared State."""
    print(f"[vision] running ({detector.name})")
    t = 0.0
    while True:
        t += 1.0 / hz
        obstacle, rng, objects, grass = evaluate(detector.detect(t))
        S.update(obstacle=obstacle, obstacle_range=rng, objects=objects, grass_pct=grass)
        time.sleep(1.0 / hz)
