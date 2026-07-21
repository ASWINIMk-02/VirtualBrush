"""
Air Draw — draw on screen using hand/finger tracking, no touch required.

Pipeline:
  Webcam frame -> MediaPipe Hands (21 landmarks) -> gesture classification
  -> stroke logic on a persistent canvas -> alpha-blended output.

Controls (once running):
  - Index finger up only        -> draw
  - Index + middle finger up    -> hover mode (move without drawing; use to pick a color)
  - Fist / other poses          -> idle
  - Hover fingertip over the top color swatches to change color
  - Hover over the "ERASE" swatch to switch to eraser mode
  - Press 'c'  -> clear canvas
  - Press 's'  -> save canvas as PNG
  - Press 'q'  -> quit

Install deps:
    pip install opencv-python mediapipe numpy
"""

import cv2
import numpy as np
import mediapipe as mp
import time
import os

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CAM_INDEX = 0
FRAME_W, FRAME_H = 1280, 720
BRUSH_THICKNESS = 8
ERASER_THICKNESS = 40
SMOOTHING = 0.55          # 0 = no smoothing (jittery), closer to 1 = smoother but laggier
SAVE_DIR = "air_draw_saves"

COLORS = {
    "Red":    (0, 0, 255),
    "Green":  (0, 200, 0),
    "Blue":   (255, 100, 0),
    "Yellow": (0, 220, 220),
    "Purple": (200, 0, 150),
}
SWATCH_W = FRAME_W // (len(COLORS) + 1)  # +1 slot reserved for ERASE

# ---------------------------------------------------------------------------
# MediaPipe setup
# ---------------------------------------------------------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6,
)

# Landmark indices for fingertips and their PIP (lower) joints
TIP_IDS = [4, 8, 12, 16, 20]


def fingers_up(landmarks, handedness_label):
    """Return a list [thumb, index, middle, ring, pinky] of booleans."""
    up = []

    # Thumb: compare x, direction depends on which hand it is
    if handedness_label == "Right":
        up.append(landmarks[4].x < landmarks[3].x)
    else:
        up.append(landmarks[4].x > landmarks[3].x)

    # Other four fingers: tip above (smaller y) than the PIP joint
    for tip_id in TIP_IDS[1:]:
        up.append(landmarks[tip_id].y < landmarks[tip_id - 2].y)

    return up


def draw_toolbar(frame, active_color_name, eraser_active):
    """Draw the color palette + eraser swatch at the top of the frame."""
    x = 0
    for name, bgr in COLORS.items():
        cv2.rectangle(frame, (x, 0), (x + SWATCH_W, 80), bgr, -1)
        if name == active_color_name and not eraser_active:
            cv2.rectangle(frame, (x, 0), (x + SWATCH_W, 80), (255, 255, 255), 4)
        cv2.putText(frame, name, (x + 10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 2, cv2.LINE_AA)
        x += SWATCH_W

    # Eraser swatch
    cv2.rectangle(frame, (x, 0), (x + SWATCH_W, 80), (50, 50, 50), -1)
    if eraser_active:
        cv2.rectangle(frame, (x, 0), (x + SWATCH_W, 80), (255, 255, 255), 4)
    cv2.putText(frame, "ERASE", (x + 10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2, cv2.LINE_AA)


def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

    canvas = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)

    active_color_name = "Red"
    eraser_active = False
    prev_x, prev_y = None, None
    smooth_x, smooth_y = None, None
    prev_time = 0

    os.makedirs(SAVE_DIR, exist_ok=True)

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Camera read failed — check CAM_INDEX / permissions.")
            break

        frame = cv2.resize(frame, (FRAME_W, FRAME_H))
        frame = cv2.flip(frame, 1)  # mirror for natural interaction
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        drawing_now = False

        if result.multi_hand_landmarks and result.multi_handedness:
            lm = result.multi_hand_landmarks[0]
            handedness = result.multi_handedness[0].classification[0].label
            landmarks = lm.landmark
            up = fingers_up(landmarks, handedness)

            ix = int(landmarks[8].x * FRAME_W)
            iy = int(landmarks[8].y * FRAME_H)

            index_up, middle_up = up[1], up[2]
            others_down = not up[3] and not up[4]

            if index_up and middle_up and others_down:
                # Hover / selection mode
                prev_x, prev_y = None, None
                if iy < 80:
                    idx = min(ix // SWATCH_W, len(COLORS))
                    if idx < len(COLORS):
                        active_color_name = list(COLORS.keys())[idx]
                        eraser_active = False
                    else:
                        eraser_active = True
                cv2.circle(frame, (ix, iy), 15, (255, 255, 255), 2)

            elif index_up and not middle_up:
                # Draw mode — smooth the point to reduce jitter
                if smooth_x is None:
                    smooth_x, smooth_y = ix, iy
                else:
                    smooth_x = int(SMOOTHING * smooth_x + (1 - SMOOTHING) * ix)
                    smooth_y = int(SMOOTHING * smooth_y + (1 - SMOOTHING) * iy)

                if prev_x is not None and iy > 80:
                    color = (0, 0, 0) if eraser_active else COLORS[active_color_name]
                    thickness = ERASER_THICKNESS if eraser_active else BRUSH_THICKNESS
                    cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y),
                              color, thickness, lineType=cv2.LINE_AA)
                    drawing_now = True

                prev_x, prev_y = smooth_x, smooth_y
                cv2.circle(frame, (ix, iy), 10,
                           (0, 0, 0) if eraser_active else COLORS[active_color_name], -1)
            else:
                prev_x, prev_y = None, None
                smooth_x, smooth_y = None, None

            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
        else:
            prev_x, prev_y = None, None
            smooth_x, smooth_y = None, None

        # Blend canvas onto live frame
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
        fg = cv2.bitwise_and(canvas, canvas, mask=mask)
        output = cv2.add(bg, fg)

        draw_toolbar(output, active_color_name, eraser_active)

        # FPS counter
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        cv2.putText(output, f"FPS: {int(fps)}", (FRAME_W - 150, FRAME_H - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        status = "DRAWING" if drawing_now else "IDLE"
        cv2.putText(output, status, (20, FRAME_H - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Air Draw", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            canvas[:] = 0
        elif key == ord('s'):
            filename = os.path.join(SAVE_DIR, f"drawing_{int(time.time())}.png")
            cv2.imwrite(filename, canvas)
            print(f"Saved: {filename}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()