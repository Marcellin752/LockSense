#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## Enrollment utility: capture the owner reference photo from the webcam
##

import os
import sys

# Allow running this script from any working directory
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

import cv2
from capture.camera import CameraManager
from detection.face_detector import FaceDetector

def main():
    """Captures a live webcam snapshot and stores it as the owner reference."""
    print("--- LOCKSENSE OWNER ENROLLMENT ---")
    print("Position yourself in front of the webcam.")
    print("SPACE: save reference photo | Q: cancel\n")

    camera = CameraManager("config/settings.json")
    detector = FaceDetector("config/settings.json")

    if not camera.initialize():
        print("[Error] Could not access the webcam.")
        return 1

    saved = False
    try:
        while True:
            success, frame = camera.get_frame()
            if not success:
                continue

            face_detected, face_boxes, frame = detector.detect_face(frame, draw_mesh=False)

            if face_detected:
                hint, color = "PRESS SPACE TO SAVE", (0, 255, 0)
            else:
                hint, color = "NO FACE DETECTED", (0, 0, 255)

            cv2.putText(frame, hint, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.imshow('LockSense - Owner Enrollment', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("[Enrollment] Cancelled by user.")
                break
            if key == ord(' ') and face_detected:
                reference_path = "data/reference/owner.jpeg"
                os.makedirs(os.path.dirname(reference_path), exist_ok=True)
                if cv2.imwrite(reference_path, frame):
                    print(f"[Enrollment] Reference photo saved to '{reference_path}'.")
                    print("[Enrollment] Done. Restart LockSense to apply the new profile.")
                    saved = True
                else:
                    print("[Error] Failed to write the reference image on disk.")
                break
            if key == ord(' ') and not face_detected:
                print("[Warning] Cannot enroll without a visible face.")

    except KeyboardInterrupt:
        print("\n[Enrollment] Interrupted.")

    finally:
        camera.release()
        detector.close()

    return 0 if saved else 1

if __name__ == "__main__":
    sys.exit(main())
