import math
import time
from dataclasses import dataclass

import cv2

# 0 = default webcam. Change to 1/2/etc if you use another camera.
CAMERA_INDEX = 0

# Optional calibration. Leave as None for pixels/second only.
# Example: 0.001 means 1 pixel = 1 millimeter.
METERS_PER_PIXEL = None


@dataclass
class TrackingState:
    bbox: tuple[int, int, int, int] | None = None
    previous_center: tuple[int, int] | None = None
    previous_time: float | None = None


def create_tracker():
    """Create a CSRT tracker, handling OpenCV version differences."""
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create()
    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
        return cv2.legacy.TrackerCSRT_create()
    raise RuntimeError(
        "CSRT tracker is unavailable. Install opencv-contrib-python: "
        "pip install opencv-contrib-python"
    )


def select_object(frame):
    bbox = cv2.selectROI(
        "Select object to track",
        frame,
        fromCenter=False,
        showCrosshair=True,
    )
    cv2.destroyWindow("Select object to track")
    if bbox == (0, 0, 0, 0):
        return None
    return tuple(int(v) for v in bbox)


def center_of_bbox(bbox):
    x, y, w, h = bbox
    return (x + w // 2, y + h // 2)


def draw_velocity(frame, velocity_px_s):
    lines = [f"Velocity: {velocity_px_s:.2f} px/s"]
    if METERS_PER_PIXEL is not None:
        lines.append(f"Velocity: {velocity_px_s * METERS_PER_PIXEL:.3f} m/s")

    for index, line in enumerate(lines):
        cv2.putText(
            frame,
            line,
            (20, 40 + index * 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Could not read from camera")

    bbox = select_object(frame)
    if bbox is None:
        print("No object selected. Exiting.")
        cap.release()
        return

    tracker = create_tracker()
    tracker.init(frame, bbox)
    state = TrackingState(bbox=bbox, previous_center=center_of_bbox(bbox), previous_time=time.time())

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        success, bbox = tracker.update(frame)
        current_time = time.time()

        if success:
            bbox = tuple(int(v) for v in bbox)
            x, y, w, h = bbox
            center = center_of_bbox(bbox)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            velocity_px_s = 0.0
            if state.previous_center is not None and state.previous_time is not None:
                dt = current_time - state.previous_time
                if dt > 0:
                    dx = center[0] - state.previous_center[0]
                    dy = center[1] - state.previous_center[1]
                    distance_pixels = math.hypot(dx, dy)
                    velocity_px_s = distance_pixels / dt

            draw_velocity(frame, velocity_px_s)
            state.previous_center = center
            state.previous_time = current_time
        else:
            cv2.putText(
                frame,
                "Tracking lost - press r to reselect",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        cv2.putText(
            frame,
            "q: quit | r: reselect",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("Object Velocity Tracker", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        if key == ord("r"):
            bbox = select_object(frame)
            if bbox is not None:
                tracker = create_tracker()
                tracker.init(frame, bbox)
                state = TrackingState(
                    bbox=bbox,
                    previous_center=center_of_bbox(bbox),
                    previous_time=time.time(),
                )

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
