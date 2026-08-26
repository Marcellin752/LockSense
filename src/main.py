#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## Main orchestrator and core loop for LockSense
##

import cv2
import json
import time
import os
from capture.camera import CameraManager
from detection.face_detector import FaceDetector
from auth.face_auth import FaceAuthenticator
from security.os_trigger import OSTrigger

class LockSenseApp:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path

        # Core modules
        self.camera = CameraManager(self.config_path)
        self.detector = FaceDetector(self.config_path)
        self.auth = FaceAuthenticator(self.config_path)
        self.trigger = OSTrigger()
        
        # Security tracking states
        self.tolerance_seconds = 3
        self.last_seen_time = time.time()
        self.is_locked = False
        
        self.load_config()

    def load_config(self):
        """Loads runtime configurations from the JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.tolerance_seconds = config.get("security", {}).get("tolerance_seconds", 3)
            except Exception as e:
                print(f"[Warning] Failed to load config in Main. Error: {e}")

    def run(self):
        """Main execution loop for LockSense continuous monitoring."""
        print("\n--- LOCKSENSE: SMART SECURITY ACTIVE ---")
        
        if not self.camera.initialize():
            print("[Critical] Could not start LockSense due to camera initialization failure.")
            return

        if not self.auth.load_reference_profile():
            print("[Critical] Owner profile unavailable: LockSense cannot authenticate users.")
            return

        try:
            while True:
                # Fetch optimized frame from camera manager
                success, frame = self.camera.get_frame()
                if not success:
                    print("[Warning] Failed to grab frame from webcam stream.")
                    continue

                current_time = time.time()

                # Run lightweight MediaPipe face detection
                face_detected, frame = self.detector.detect_face(frame, draw_mesh=True)

                # Secure presence requires the OWNER to be recognized,
                # a bare face or an intruder is treated as an absence.
                owner_present = False
                if face_detected:
                    owner_present, distance = self.auth.authenticate(frame)

                if owner_present:
                    # Authorized user in front of the screen: reset security timers
                    self.last_seen_time = current_time
                    self.is_locked = False  # Reset lock state when user returns
                    status_text = "USER PROTECTED"
                    color = (0, 255, 0)  # Green
                elif face_detected:
                    # A face is visible but it is NOT the owner: immediate threat
                    absence_duration = current_time - self.last_seen_time
                    remaining_time = max(0, int(self.tolerance_seconds - absence_duration))
                    status_text = f"INTRUDER DETECTED - LOCKING IN {remaining_time}s"
                    color = (0, 0, 255)  # Red
                else:
                    # No one in front of the screen
                    absence_duration = current_time - self.last_seen_time
                    remaining_time = max(0, int(self.tolerance_seconds - absence_duration))
                    status_text = f"USER AWAY - LOCKING IN {remaining_time}s"
                    color = (0, 0, 255)  # Red

                # Trigger locking condition if tolerance threshold is breached
                absence_duration = current_time - self.last_seen_time
                if absence_duration >= self.tolerance_seconds and not self.is_locked:
                    self.trigger.lock_session()
                    self.is_locked = True

                #  Render security HUD overlay on monitor window
                cv2.putText(frame, status_text, (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                cv2.imshow('LockSense - Security Monitor', frame)

                # Break loop immediately if 'q' key is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[LockSense] Manual exit triggered by user.")
                    break

        except KeyboardInterrupt:
            print("\n[LockSense] Execution interrupted via terminal (Ctrl+C).")
        
        finally:
            # Clean up resources safely on exit
            self.camera.release()
            self.detector.close()
            print("--- LOCKSENSE: PROGRAM EXIT ---\n")

if __name__ == "__main__":
    # Initialize and run the application
    app = LockSenseApp()
    app.run()
