#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## Facial authentication module comparing live frames with the owner profile
##

import cv2
import json
import os
import face_recognition

class FaceAuthenticator:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path

        # Authentication state (fallback values if settings.json is missing)
        self.reference_encoding = None
        self.reference_image_path = "data/reference/owner.jpeg"
        self.distance_threshold = 0.6

        # Performance throttling state
        self.check_interval = 5
        self._frames_since_check = 0
        self._cached_result = False
        self._cached_distance = 1.0

        self.load_config()

    def load_config(self):
        """Loads authentication parameters from the JSON configuration file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    security = config.get("security", {})
                    self.reference_image_path = security.get(
                        "reference_image_path", self.reference_image_path)
                    self.distance_threshold = security.get(
                        "face_distance_threshold", self.distance_threshold)
                    optimizations = config.get("optimizations", {})
                    self.check_interval = optimizations.get(
                        "auth_check_interval", self.check_interval)
            except Exception as e:
                print(f"[Warning] Failed to load config in FaceAuthenticator. Error: {e}")

    def load_reference_profile(self):
        """
        Loads the owner reference image and computes its biometric encoding.
        Returns True if a usable profile was loaded.
        """
        if not os.path.exists(self.reference_image_path):
            print(f"[Error] Owner reference image not found: {self.reference_image_path}")
            return False

        try:
            image = face_recognition.load_image_file(self.reference_image_path)
            encodings = face_recognition.face_encodings(image)
        except Exception as e:
            print(f"[Error] Failed to process the reference image. Exception: {e}")
            return False

        if not encodings:
            print("[Error] No face found in the owner reference image.")
            return False

        self.reference_encoding = encodings[0]
        print(f"[LockSense] Owner profile loaded from '{self.reference_image_path}'.")
        return True

    def authenticate(self, frame):
        """
        Compares the main face of the frame against the owner profile.
        Returns:
            bool: True if the authorized owner is recognized.
            float: Face distance against the profile (lower is closer).
        """
        if frame is None or self.reference_encoding is None:
            return False, 1.0

        # face_recognition expects RGB while OpenCV provides BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_frame)

        if not face_encodings:
            return False, 1.0

        distance = face_recognition.face_distance(
            [self.reference_encoding], face_encodings[0])[0]
        return bool(distance <= self.distance_threshold), float(distance)

    def verify(self, frame):
        """
        Throttled authentication: runs the expensive recognition only once
        every 'check_interval' calls and serves the cached verdict in between.
        MediaPipe face detection still runs on every frame as a fast gate.
        Returns:
            bool: True if the authorized owner is recognized.
            float: Face distance of the last full check (lower is closer).
        """
        if self.reference_encoding is None:
            return False, 1.0

        if self._cached_distance is None or \
                self._frames_since_check >= self.check_interval:
            self._cached_result, self._cached_distance = self.authenticate(frame)
            self._frames_since_check = 0
        else:
            self._frames_since_check += 1

        return self._cached_result, self._cached_distance
