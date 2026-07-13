# Hailo-8L model zoo — what runs, what to train (design doc; validation needs hardware)

## Use today (pre-compiled, Hailo Model Zoo)
| Model | Why here | Notes |
|---|---|---|
| yolov8s (COCO) | person/dog/cat detection = the safety classes | compile to .hef with the Hailo Dataflow Compiler; COCO classes cover the stop-list |
| yolov8n | same, more FPS headroom | headroom for the rear camera too |
| scdepth/fast-depth class | monocular depth to complement LiDAR | LiDAR remains the stop authority |

`vision.py` consumes any .hef whose output maps to `[{cls, conf, box}]` — see `make_detector()`.

## The custom 2-head net (the plan)
MobileNetV3-lite backbone → detection head (person/pet/obstacle) + monocular-depth head,
trained on frames auto-labeled by the LiDAR (range = depth supervision, clusters = boxes).
Pipeline: record rosbag-style frame+scan pairs during MANUAL mowing → auto-label →
train (PyTorch) → ONNX → Hailo DFC → .hef → `--vision-hef`.

## Rules
LiDAR keeps stop authority. Camera AI only ADDS stops (person/pet at range, grass-vs-obstacle);
it can never veto a LiDAR stop. That's `safety.evaluate`'s priority order and it doesn't change.
