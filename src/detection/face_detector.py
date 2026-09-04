#!/usr/bin/env python3
##
## PROJECT, 2026
## LockSense
## File description:
## Face detection module using MediaPipe
##

import cv2
import mediapipe as mp
import json
import os

class FaceDetector:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.tolerance_seconds = 3
        
        # Initialize MediaPipe Face Mesh components
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))
        
        self.load_config()
        
        # Setup the MediaPipe Face Mesh model
        # Multiple faces are tracked so that an intruder next to the owner is seen
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

    def load_config(self):
        """Loads face detection parameters from the JSON configuration file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.tolerance_seconds = config.get("security", {}).get("tolerance_seconds", 3)
            except Exception as e:
                print(f"[Warning] Failed to load config in FaceDetector. Error: {e}")

    def detect_face(self, frame, draw_mesh=False):
        """
        Analyzes a single frame to locate faces.
        Returns:
            bool: True if at least one face is detected.
            list: Face bounding boxes as (left, top, right, bottom) pixel tuples.
            numpy.ndarray: The processed frame (with mesh drawing if enabled).
        """
        if frame is None:
            return False, [], None

        height, width = frame.shape[:2]

        # MediaPipe requires RGB images, while OpenCV reads in BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        face_detected = False
        face_boxes = []

        if results.multi_face_landmarks:
            face_detected = True

            for face_landmarks in results.multi_face_landmarks:
                # Derive a padded pixel bounding box from the mesh landmarks:
                # reused downstream to skip expensive face re-detection.
                xs = [landmark.x * width for landmark in face_landmarks.landmark]
                ys = [landmark.y * height for landmark in face_landmarks.landmark]
                pad_x = (max(xs) - min(xs)) * 0.08
                pad_y = (max(ys) - min(ys)) * 0.08

                left = max(0, int(min(xs) - pad_x))
                top = max(0, int(min(ys) - pad_y))
                right = min(width, int(max(xs) + pad_x))
                bottom = min(height, int(max(ys) + pad_y))
                face_boxes.append((left, top, right, bottom))

                # Draw the face mesh for debugging / visual feedback if requested
                if draw_mesh:
                    self.mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=self.drawing_spec
                    )

        return face_detected, face_boxes, frame

    def close(self):
        """Properly closes the MediaPipe model resources."""
        self.face_mesh.close()
        print("[LockSense] MediaPipe Face Mesh resources closed.")
