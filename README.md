# Object Velocity Tracker

Python/OpenCV project that uses your webcam, lets you select an object, tracks it, and estimates the object's velocity across the screen.

By default velocity is shown in pixels/second. If you know the real-world scale of your camera view, set `METERS_PER_PIXEL` in `main.py` to show m/s too.

## Setup

```bash
cd ~/Desktop/object-velocity-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Controls:
- Drag a box around the object in the first frame, then press Enter/Space.
- Press `r` to reselect the object.
- Press `q` to quit.

## Calibration

If you can measure something in frame, estimate meters per pixel:

```text
METERS_PER_PIXEL = real_distance_meters / measured_distance_pixels
```

Example: if 0.10 m appears as 100 px, use `0.001`.
# Accelerate
