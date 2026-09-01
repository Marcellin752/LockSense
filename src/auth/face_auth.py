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

        # Performance throttling state (full check on first verify call)
        self.check_interval = 5
        self._frames_since_check = 0
        self._cached_result = (False, 0)

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

    @staticmethod
    def classify_faces(face_encodings, reference_encoding, distance_threshold):
        """
        Pure decision helper: classifies every detected face against the owner profile.
        Returns:
            bool: True if the authorized owner is among the faces.
            int: Number of unrecognized (stranger) faces.
        """
        if reference_encoding is None:
            return False, len(face_encodings)

        owner_present = False
        strangers = 0

        for encoding in face_encodings:
            distance = face_recognition.face_distance(
                [reference_encoding], encoding)[0]
            if distance <= distance_threshold:
                owner_present = True
            else:
                strangers += 1

        return owner_present, strangers

    # Low-res webcam frames (640x480) produce tiny faces that dlib fails to
    # match: magnifying the face crops before encoding fixes reliability.
    UPSCALE_FACTOR = 2.0

    def authenticate(self, frame, face_boxes=None):
        """
        Runs a full biometric analysis of every visible face in the frame.
        When MediaPipe bounding boxes are provided they are reused directly,
        skipping the costly dlib face detector entirely.
        Returns:
            bool: True if the authorized owner is recognized.
            int: Number of stranger faces detected.
        """
        if frame is None or self.reference_encoding is None:
            return False, 0

        # face_recognition expects RGB while OpenCV provides BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        known_locations = None
        if face_boxes:
            rgb_frame = cv2.resize(
                rgb_frame, None, fx=self.UPSCALE_FACTOR, fy=self.UPSCALE_FACTOR)
            known_locations = [
                (int(left * self.UPSCALE_FACTOR), int(top * self.UPSCALE_FACTOR),
                 int(right * self.UPSCALE_FACTOR), int(bottom * self.UPSCALE_FACTOR))
                for left, top, right, bottom in face_boxes
            ]

        if known_locations:
            face_encodings = face_recognition.face_encodings(
                rgb_frame, known_face_locations=known_locations)
        else:
            face_encodings = face_recognition.face_encodings(rgb_frame)

        return self.classify_faces(
            face_encodings, self.reference_encoding, self.distance_threshold)

    def verify(self, frame, face_boxes=None, force=False):
        """
        Throttled authentication: runs the expensive recognition only once
        every 'check_interval' calls and serves the cached verdict in between.
        MediaPipe face detection still runs on every frame as a fast gate.
        A 'force' call bypasses the cache (used when a face just reappeared).
        Returns:
            bool: True if the authorized owner is recognized.
            int: Number of stranger faces detected.
        """
        if self.reference_encoding is None:
            return False, 0

        if force or self._frames_since_check == 0 or \
                self._frames_since_check >= self.check_interval:
            self._cached_result = self.authenticate(frame, face_boxes)
            self._frames_since_check = 1
        else:
            self._frames_since_check += 1

        return self._cached_result
