#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Generate amazon_cart.html and ebay_cart.html from one verified product model.
# Data sourced 2026-06-26 by research agents (see cart/research/*.md). Prices:
#   v=verified off live page; e=estimate (listing real, price not rendered to fetch).
import html, json

A="https://www.amazon.com"; E="https://www.ebay.com"
# fields: name, qty, phase, amazon(url,price,verified,note), ebay(...), direct(url,price,note)
P = [
 # ---------------- PHASE 1: drive + safety ----------------
 dict(name="Flight controller — Holybro Pixhawk 6C", qty=1, phase=1,
   amazon=("https://www.amazon.com/dp/B0C3LH2V45",165.99,False,"Amazon listing exists but OUT OF STOCK"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=Holybro+Pixhawk+6C&_sop=15",103,False,"CAUTION: cheap China units likely CLONES — avoid for safety-critical"),
   direct=("https://holybro.com/products/pixhawk-6c",165.99,"BUY GENUINE from Holybro — $165.99 verified, in stock")),
 dict(name="RTK GPS — ArduSimple simpleRTK2B (ZED-F9P)", qty=1, phase=1,
   amazon=None, ebay=("https://www.ebay.com/itm/227233677533",None,False,"sibling listing; verify genuine"),
   direct=("https://www.ardusimple.com/product/simplertk2b/",186.0,"€172 vendor-direct (≈$186). Also Mouser. Rarely on Amazon US")),
 dict(name="RTK antenna — u-blox ANN-MB-00 multiband IP67", qty=1, phase=1,
   amazon=None, ebay=None,
   direct=("https://www.ardusimple.com/product/ann-mb-00-ip67/",58.0,"€53.80 vendor-direct (≈$58). Survey-grade upgrade €149 available")),
 dict(name="Linear actuator 12V 100mm, potentiometer feedback, IP66, ≥150N", qty=2, phase=1,
   amazon=("https://www.amazon.com/Actuator-Potentiometer-Position-Feedback-2640LBS/dp/B0D91XZ167",70.0,False,"pick 100mm/12V variant; feedback+IP66+force all met. Cleaner-force alt B0FLCBKKCH (1500N)"),
   ebay=("https://www.ebay.com/b/100mm-4-in-Stroke-12V-Linear-Actuators/55826/bn_93703772",None,False,"WEAK on eBay: 100mm units lack feedback. BUY ON AMAZON"),
   direct=None),
 dict(name="Motor driver — BTS7960 (IBT-2) 43A dual H-bridge (2-pack)", qty=1, phase=1,
   amazon=("https://www.amazon.com/BTS7960-Current-Half-Bridge-Configuration-Driver/dp/B0BGR92TCD",15.0,False,"2-pack = both actuators"),
   ebay=("https://www.ebay.com/itm/326872824950",13.0,False,"single; 5-pack cheaper/ea"), direct=None),
 dict(name="RC radio — FlySky FS-i6X + iA6B receiver (override + kill)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Flysky-FS-i6X-Transmitter-FS-iA6B-Receiver/dp/B0744DPPL8",65.0,False,"canonical combo listing"),
   ebay=("https://www.ebay.com/itm/325478132146",None,False,"TX+iA6B combo"), direct=None),
 dict(name="E-stop — 22mm latching mushroom, IP65, 1NC", qty=1, phase=1,
   amazon=("https://www.amazon.com/dstfuy-Emergency-Stop-Button-Switch/dp/B0CG1CL41W",9.96,True,"IP65 + NC both stated"),
   ebay=("https://www.ebay.com/itm/800021703014",13.67,True,"NC stated; IP not in title"), direct=None),
 dict(name="Relay — 40A 5-pin SPDT + sockets + fuse holders (2-pack)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Recoil-Automotive-Interlocking-Sockets-Holders/dp/B08BHR2RM7",13.99,True,"2 relays+sockets = PTO + ignition kill"),
   ebay=("https://www.ebay.com/itm/235177758973",12.99,True,"single; buy 2"), direct=None),
 dict(name="Throttle servo — ANNIMOS 25kg metal-gear waterproof", qty=1, phase=1,
   amazon=("https://www.amazon.com/ANNIMOS-Digital-Waterproof-Crawler-Control/dp/B07GK1G5FV",17.99,True,"25kg-cm, needs 5-6V"),
   ebay=("https://www.ebay.com/itm/333763351400",29.99,False,"DS3225 2-pack, approx price"), direct=None),
 dict(name="Buck converter 12V→5V 5A (Pi power)", qty=1, phase=1,
   amazon=("https://www.amazon.com/GoHz-DC-Buck-Converter-Regulator/dp/B0DZNSMJFW",11.0,False,"2-pack; 5A/25W"),
   ebay=("https://www.ebay.com/itm/201847763020",None,False,"12V→5V 5A"), direct=None),
 dict(name="Buck converter 12V→adjustable (use XL4015 if 5A needed)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Maxmoral-Converter-Adjustable-Step-Down-Regulator/dp/B07MKQXNWG",8.0,False,"LM2596 = 3A max; XL4015 for 5A"),
   ebay=("https://www.ebay.com/itm/224796559843",None,False,"LM2596 3A"), direct=None),
 dict(name="Fuse block — 12-way ATC/ATO + ground bus", qty=1, phase=1,
   amazon=("https://www.amazon.com/Block-Ground-Negative-Busbar-Automotive/dp/B07PK6H148",22.0,False,"central distribution; get clear cover"),
   ebay=("https://www.ebay.com/itm/236124498049",None,False,"Recoil AFG12 12-way"), direct=None),
 dict(name="Inline waterproof fuse holders + ATC/ATO fuse assortment", qty=1, phase=1,
   amazon=("https://www.amazon.com/Anyongora-Inline-Waterproof-Automotive-Standard/dp/B0CL7MLY6T",13.0,False,"4 holders + 40 fuses 2-40A"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=inline+ATC+ATO+waterproof+fuse+holder+12+AWG",None,False,"(search)"), direct=None),
 dict(name="IP67 ABS enclosure ~200×150×100mm (brain box)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Taiss-Waterproof-Electrical-Electronics-200x150x100mm/dp/B0BHWCVYRT",20.0,False,"printed equipment plate goes inside"),
   ebay=("https://www.ebay.com/itm/294268994917",18.49,False,"snippet price"), direct=None),
 dict(name="Cable glands — mixed PG7/PG9/PG11 IP68 kit (50pc)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Bates-Choice-Pro-Waterproof-connector/dp/B09W9Q5HMH",12.0,False,"covers PG9 need"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=PG7+PG9+PG11+cable+gland+waterproof+kit",None,False,"(search)"), direct=None),
 dict(name="Conformal coating — MG Chemicals 422B aerosol", qty=1, phase=1,
   amazon=("https://www.amazon.com/MG-Chemicals-422B-340G-Silicone-Conformal/dp/B008O9YGQI",18.0,False,"coat all PCBs"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=MG+Chemicals+422B+conformal+coating",None,False,"(search)"), direct=None),
 dict(name="Dielectric grease — Permatex 22058 3oz", qty=1, phase=1,
   amazon=("https://www.amazon.com/Permatex-22058-Dielectric-Tune-Up-Grease/dp/B000AL8VD2",7.0,False,"every gland/connector"),
   ebay=None, direct=None),
 dict(name="10 AWG tinned duplex marine wire (battery feed, ~15ft)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Duplex-Tinned-Marine-Wire-Black/dp/B00MI5I98K",40.0,False,"50ft red/black bonded"),
   ebay=("https://www.ebay.com/itm/388775320598",None,False,"tinned duplex"), direct=None),
 dict(name="14 AWG tinned duplex wire (actuator/motor power, ~50ft)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Duplex-Tinned-Marine-Wire-Black/dp/B00MI59JD4",28.0,False,"≤15A runs"),
   ebay=("https://www.ebay.com/b/10-awg-marine-wire/bn_7023356847",None,False,"(search)"), direct=None),
 dict(name="22 AWG 6-color stranded hookup wire (signals)", qty=1, phase=1,
   amazon=("https://www.amazon.com/LotFancy-Stranded-Colors-Electrical-Flexible/dp/B08JGRP6NH",14.0,False,"tinned, 6×26ft"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=22+awg+stranded+hook+up+wire+kit+6+color+tinned",None,False,"(search)"), direct=None),
 dict(name="XT60 connector pairs (genuine Amass)", qty=1, phase=1,
   amazon=("https://www.amazon.com/Amass-Female-Connector-Battery-Charge/dp/B00RVM93LW",9.0,False,"3-5 pairs; bulk avail"),
   ebay=("https://www.ebay.com/itm/364269671670",None,False,"10 pairs"), direct=None),
 dict(name="Heat-shrink terminal kit — Wirefy 540pc marine", qty=1, phase=1,
   amazon=("https://www.amazon.com/stores/Wirefy/page/130CEBB7-80AB-4780-B406-7557A17C09F7",22.0,False,"ring/spade/butt, adhesive-lined"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=heat+shrink+wire+connector+kit+marine+ring+spade+butt",None,False,"(search)"), direct=None),
 dict(name="20mm OD aluminium tube (GPS+LiDAR masts)", qty=1, phase=1,
   amazon=("https://www.amazon.com/uxcell-Aluminum-Round-Length-Tubing/dp/B09FNX7BRX",15.0,False,"Amazon mostly 200-300mm"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=20mm+OD+aluminium+round+tube+1m",None,False,"true 1m here / Online Metals"), direct=None),
 dict(name="304 stainless M3/M4/M5 fastener kit", qty=1, phase=1,
   amazon=("https://www.amazon.com/Stainless-Washers-Assortment-Wrenches-Included/dp/B08XYTRTZ5",23.0,False,"304 SS for outdoors"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=stainless+m3+m4+m5+bolt+nut+washer+assortment+kit",None,False,"(search)"), direct=None),
 dict(name="Brass heat-set inserts M3/M4 (for 3D prints)", qty=1, phase=1,
   amazon=("https://www.amazon.com/m3-heat-set-inserts/s?k=m3+heat+set+inserts",13.0,False,"ruthex M3 100pc"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=M3+M4+brass+heat+set+insert",None,False,"(search)"), direct=None),
 dict(name="Ratchet straps + wire loom + UV zip ties + rubber feet", qty=1, phase=1,
   amazon=("https://www.amazon.com/Assorted-Split-Flex-Guard-Convoluted-Tubing/dp/B07JR7727L",25.0,False,"loom 3-pack; add straps/ties/feet"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=split+wire+loom+kit+automotive",None,False,"(search)"), direct=None),
 # ---------------- PHASE 2: perception ----------------
 dict(name="Raspberry Pi 5, 8GB (board)", qty=1, phase=2,
   amazon=("https://www.amazon.com/CanaKit-Raspberry-Starter-Kit-PRO/dp/B0CRSNCJ6Y",None,False,"CanaKit listing; CONFIRM bare board vs kit"),
   ebay=("https://www.ebay.com/sch/i.html?_nkw=Raspberry+Pi+5+8GB+board",None,False,"verify genuine"),
   direct=("https://www.canakit.com/raspberry-pi-5-8gb.html",80.0,"Official MSRP ~$80; CanaKit/Adafruit listings read higher — confirm SKU. PiShop also")),
 dict(name="microSD 64GB A2 (SanDisk Extreme)", qty=1, phase=2,
   amazon=("https://www.amazon.com/SanDisk-Extreme-microSD-UHS-I-Adapter/dp/B07FCMBLV6",13.0,False,"A2 rated"),
   ebay=("https://www.ebay.com/itm/325491376713",None,False,"verify genuine"), direct=None),
 dict(name="RPLidar A1M8 360° 2D lidar", qty=1, phase=2,
   amazon=("https://www.amazon.com/Slamtec-RPLIDAR-Scanning-Avoidance-Navigation/dp/B07TJW5SXF",99.0,False,"obstacle stop"),
   ebay=None,
   direct=("https://www.adafruit.com/product/4010",99.95,"Adafruit $99.95 (92 in stock) / DFRobot $99")),
 # ---------------- PHASE 3: AI ----------------
 dict(name="Raspberry Pi AI HAT+ (Hailo-8L 13 TOPS)", qty=1, phase=3,
   amazon=("https://www.amazon.com/AI-HAT-Intelligence-Accelerator-8L-13TOP/dp/B0DM956761",110.0,False,"3rd-party markup — prefer reseller"),
   ebay=None,
   direct=("https://www.pishop.us/product/raspberry-pi-ai-hat-13-tops/",76.95,"PiShop $76.95 verified. Adafruit AI Kit $109.90 alt")),
 dict(name="Raspberry Pi Camera Module 3", qty=1, phase=3,
   amazon=None, ebay=None,
   direct=("https://www.pishop.us/product/raspberry-pi-camera-module-3/",29.25,"PiShop $29.25 verified / Adafruit #5657. Wide variant OOS at Adafruit")),
]

PHASE={1:"Phase 1 — Drive + Safety",2:"Phase 2 — Perception",3:"Phase 3 — AI Vision"}

def price_of(item, market):
    src=item.get(market);
    if src and src[1] is not None: return src[1], src[2]
    if item.get("direct") and item["direct"][1] is not None: return item["direct"][1], False
    o=item.get("amazon") or item.get("ebay")
    if o and o[1] is not None: return o[1], False
    return None, False

def est_total(market):
    t=0.0
    for it in P:
        p,_=price_of(it, market)
        if p: t+=p*it["qty"]
    return t

CSS="""
:root{--bg:#0e1116;--card:#161b22;--card2:#1c232c;--ink:#e8edf2;--mut:#94a3b1;--line:#283139;--acc:#36c08a;--amz:#ff9900;--ebay:#3a8ddb;--warn:#e0a23a;--danger:#e0584a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
header{padding:24px 22px 16px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,#131922,#0e1116)}
h1{margin:0 0 3px;font-size:21px}.sub{color:var(--mut);font-size:13px}
.wrap{max-width:1080px;margin:0 auto;padding:20px}
.tot{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}
.pill{background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:9px 13px;font-size:13px}.pill b{font-size:17px;color:var(--acc)}
.phase{margin:24px 0 8px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);display:flex;gap:10px;align-items:center}.phase .ln{flex:1;height:1px;background:var(--line)}
.row{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:12px 14px;margin:8px 0;display:flex;gap:14px;align-items:flex-start}
.row .main{flex:1}.name{font-weight:600;font-size:14px}.qty{color:var(--mut);font-size:12px;margin-left:6px}
.note{color:var(--mut);font-size:12.5px;margin-top:3px}
.right{text-align:right;white-space:nowrap;min-width:150px}
.price{font-variant-numeric:tabular-nums;font-size:15px}.vbadge{font-size:10px;color:#bfe9d6;border:1px solid #2c5b48;background:#13241d;border-radius:20px;padding:1px 7px;margin-left:5px}
.ebadge{font-size:10px;color:#e8d3a6;border:1px solid #4a3a1c;background:#1a1410;border-radius:20px;padding:1px 7px;margin-left:5px}
a.buy{display:inline-block;margin-top:7px;font-size:12px;text-decoration:none;border-radius:7px;padding:6px 11px;border:1px solid var(--line);background:var(--card2);color:var(--ink)}
a.buy.amz{border-color:#5a4413;color:#ffcf80}a.buy.ebay{border-color:#244660;color:#9fd0f5}a.buy.dir{border-color:#2c5b48;color:#bfe9d6}
a.buy:hover{filter:brightness(1.3)}
.miss{color:#f0b9b1;font-size:12.5px;margin-top:6px}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 2px}
button{font-size:12px;border-radius:8px;padding:8px 12px;border:1px solid var(--line);background:var(--card2);color:var(--ink);cursor:pointer}button:hover{border-color:var(--acc)}
.note2{background:#1a1410;border:1px solid #4a3a1c;color:#e8d3a6;border-radius:10px;padding:11px 13px;font-size:13px;margin:16px 0}
.foot{color:var(--mut);font-size:12px;margin-top:24px;line-height:1.7}code{background:#10151b;border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:12px}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--acc);color:#04130c;font-weight:600;padding:9px 16px;border-radius:8px;opacity:0;transition:.2s;pointer-events:none}.toast.show{opacity:1}
"""

def render(market):
    mname="Amazon" if market=="amazon" else "eBay"
    accent="--amz" if market=="amazon" else "--ebay"
    rows=[]; links=[]
    cur=None
    for it in P:
        if it["phase"]!=cur:
            cur=it["phase"]; rows.append(f'<div class="phase">{PHASE[cur]}<span class="ln"></span></div>')
        src=it.get(market); direct=it.get("direct")
        qty=f'<span class="qty">×{it["qty"]}</span>' if it["qty"]>1 else ""
        right=""; buy=""; miss=""
        if src:
            url,price,verified,note=src
            pr=f'${price:,.2f}' if price is not None else '—'
            badge='<span class="vbadge">verified</span>' if verified else '<span class="ebadge">est / confirm</span>'
            right=f'<div class="price">{pr}{badge}</div>'
            cls="amz" if market=="amazon" else "ebay"
            buy=f'<a class="buy {cls}" href="{html.escape(url)}" target="_blank" rel="noopener">Open on {mname}</a>'
            if note: miss=f'<div class="note">{html.escape(note)}</div>'
            if not url.startswith("http"): pass
            if "http" in url: links.append(url)
        elif direct:
            url,price,note=direct
            pr=f'${price:,.2f}' if price is not None else '—'
            right=f'<div class="price">{pr}<span class="ebadge">direct</span></div>'
            buy=f'<a class="buy dir" href="{html.escape(url)}" target="_blank" rel="noopener">Buy direct (not on {mname})</a>'
            miss=f'<div class="miss">Not reliably on {mname} — {html.escape(note)}</div>'
        else:
            right='<div class="price">—</div>'
            miss=f'<div class="miss">Not available on {mname} — see the other cart / vendor.</div>'
        notes=(f'<div class="note">{html.escape(it["amazon"][3])}</div>' if False else "")
        rows.append(f'<div class="row"><div class="main"><div class="name">{html.escape(it["name"])}{qty}</div>{miss}{buy}</div><div class="right">{right}</div></div>')
    total=est_total(market)
    body="\n".join(rows)
    linkjs=json.dumps(links)
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Autonomous ZTR Retrofit — {mname} Cart</title><style>{CSS}
header{{border-bottom:3px solid var({accent})}}</style></head><body>
<header><div class="wrap" style="padding:0">
<h1>Autonomous ZTR Retrofit — {mname} Cart</h1>
<div class="sub">Gravely ZT 52" · real listings sourced 2026-06-26 · <b style="color:var({accent})">{mname}</b> focus · prices: <span class="vbadge">verified</span> read live · <span class="ebadge">est / confirm</span> listing real, confirm price at link</div>
<div class="tot"><div class="pill">Est. {mname} subtotal <b>${total:,.0f}</b></div><div class="pill">Items {sum(1 for x in P)}</div></div>
<div class="bar"><button onclick="openAll()">Open all {mname} items in tabs</button><button onclick="copyList()">Copy list</button>
<a class="buy" href="amazon_cart.html">Amazon cart</a><a class="buy" href="ebay_cart.html">eBay cart</a></div>
</div></header>
<div class="wrap">
<div class="note2"><b>This is a MIXED-sourcing build — not everything is on {mname}.</b> Items marked "Buy direct" must come from the manufacturer/authorized reseller (RTK GPS, genuine Pixhawk, Hailo HAT+, Pi Camera). Actuators are an <b>Amazon</b> buy (no eBay listing meets feedback+IP66+100mm). Always confirm the live price + that the seller is genuine before buying — especially anything safety-critical.</div>
{body}
<div class="note2">Totals are estimates (many marketplace prices wouldn't render to the research fetcher). The verified-badge items are exact. Full per-item research: <code>cart/research/parts-*.md</code> · BOM + trim levers: <code>cart/BOM.md</code> · safety spec: <code>docs/BUILD.md</code></div>
<div class="foot">Free (not in cart): ArduPilot Rover firmware · Mission Planner/QGroundControl · NTRIP RTK corrections (often free via state CORS). You print the brackets/enclosure plate yourself (ASA/PETG). The mower's 12V battery powers everything.</div>
</div>
<div class="toast" id="toast">Copied</div>
<script>
const L={linkjs};
function openAll(){{L.forEach((u,i)=>setTimeout(()=>window.open(u,'_blank'),i*250));}}
function toast(m){{const t=document.getElementById('toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),1100);}}
function copyList(){{navigator.clipboard.writeText(L.join("\\n")).then(()=>toast('{mname} links copied'));}}
</script></body></html>"""

for market,fn in [("amazon","amazon_cart.html"),("ebay","ebay_cart.html")]:
    open(f"/Users/zohebalvi2/autonomous-mower/cart/{fn}","w").write(render(market))
    print(f"wrote {fn}  (est subtotal ${est_total(market):,.0f})")
