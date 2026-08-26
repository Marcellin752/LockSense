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
from security.input_monitor import InputActivityMonitor

class LockSenseApp:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path

        # Core modules
        self.camera = CameraManager(self.config_path)
        self.detector = FaceDetector(self.config_path)
        self.auth = FaceAuthenticator(self.config_path)
        self.trigger = OSTrigger()
        self.input_monitor = InputActivityMonitor()

        # Security tracking states
        self.tolerance_seconds = 3
        self.last_seen_time = time.time()
        self.is_locked = False
        self.locked_at = 0.0

        # Keyboard/mouse gating (anti-false-positive) settings
        self.gating_mouse_keyboard = True
        self.inactivity_trigger_seconds = 10

        self.load_config()

    def load_config(self):
        """Loads runtime configurations from the JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    security = config.get("security", {})
                    optimizations = config.get("optimizations", {})
                    self.tolerance_seconds = security.get("tolerance_seconds", 3)
                    self.gating_mouse_keyboard = optimizations.get(
                        "gating_mouse_keyboard", True)
                    self.inactivity_trigger_seconds = optimizations.get(
                        "inactivity_trigger_seconds", 10)
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

        # Re-arm the absence timer NOW: camera startup and model loading above
        # took several seconds and must not count as an absence (otherwise
        # LockSense would lock the session instantly on launch).
        self.last_seen_time = time.time()

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
                # Recognition is throttled internally to spare CPU cycles.
                owner_present = False
                strangers = 0
                if face_detected:
                    owner_present, strangers = self.auth.verify(frame)

                # Anti-false-positive gate: recent keyboard/mouse activity
                # proves the legitimate user is still working even when their
                # face goes undetected. Never applies while a stranger is seen.
                input_active = False
                if self.gating_mouse_keyboard and not owner_present and strangers == 0:
                    idle_seconds = self.input_monitor.get_idle_seconds()
                    input_active = (idle_seconds is not None
                                    and idle_seconds < self.inactivity_trigger_seconds)

                secure_presence = owner_present or input_active

                if secure_presence:
                    # Authorized user in front of the screen: reset security timers
                    self.last_seen_time = current_time
                    self.is_locked = False  # Reset lock state when user returns
                    status_text = ("USER PROTECTED" if owner_present
                                   else "USER ACTIVE (INPUT GATE)")
                    color = (0, 255, 0)  # Green
                elif strangers > 0:
                    # Unrecognized face(s) visible: immediate threat
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
                    self.locked_at = current_time

                # Re-arm the lock trigger after a cooldown: if the user manually
                # unlocks the session while still away (or hidden from the camera),
                # protection must resume instead of staying disabled forever.
                if self.is_locked and current_time - self.locked_at >= self.tolerance_seconds:
                    self.is_locked = False

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
