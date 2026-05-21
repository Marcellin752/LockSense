#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## camera management and optimization module
##

import cv2
import json
import time
import os

class CameraManager:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self.cap = None
        
        # Default fallback values if settings.json is missing
        self.device_index = 0
        self.width = 640
        self.height = 480
        self.target_fps = 5
        
        self.load_config()

    def load_config(self):
        """Loads camera and optimization settings from the JSON configuration file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.device_index = config.get("camera", {}).get("device_index", 0)
                    self.width = config.get("camera", {}).get("width", 640)
                    self.height = config.get("camera", {}).get("height", 480)
                    self.target_fps = config.get("optimizations", {}).get("target_fps", 5)
            except Exception as e:
                print(f"[Warning] Failed to load config, using defaults. Error: {e}")

    def initialize(self):
        """Initializes the webcam stream with optimized resolution settings."""
        self.cap = cv2.VideoCapture(self.device_index)
        
        if not self.cap.isOpened():
            print(f"[Error] Camera not found (index {self.device_index})")
            return False
        
        # Enforce low resolution to drastically optimize CPU usage
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        print(f"[LockSense] Camera ready: {self.width}x{self.height} @ {self.target_fps} target FPS.")
        return True

    def get_frame(self):
        """
        Retrieves a frame, resizes it if needed, and applies a calculated sleep delay 
        to match the target_fps and free up CPU cycles.
        """
        if not self.cap:
            return False, None

        start_time = time.time()
        ret, frame = self.cap.read()
        
        if not ret:
            return False, None

        # Safety fallback: If OpenCV forces a higher resolution, resize it manually
        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            frame = cv2.resize(frame, (self.width, self.height))

        # --- CPU OPTIMIZATION CHRONO ---
        # Calculate theoretical frame duration time
        time_per_frame = 1.0 / self.target_fps
        elapsed_time = time.time() - start_time
        sleep_time = time_per_frame - elapsed_time
        
        # If processing was faster than our target interval, let the thread sleep
        if sleep_time > 0:
            time.sleep(sleep_time)

        return True, frame

    def release(self):
        """Properly releases webcam resources and closes active windows."""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            print("[LockSense] Camera resources released successfully.")
