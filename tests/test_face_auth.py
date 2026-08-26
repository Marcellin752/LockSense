#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## Unit tests for the facial authentication and security modules
##

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from auth.face_auth import FaceAuthenticator
from security.input_monitor import InputActivityMonitor

def build_authenticator():
    """Builds an authenticator without touching on-disk configuration."""
    with patch.object(FaceAuthenticator, "load_config", lambda self: None):
        return FaceAuthenticator(config_path="unused.json")

class ClassifyFacesTest(unittest.TestCase):
    """Pure decision logic of classify_faces."""

    def setUp(self):
        self.reference = np.zeros(128)
        self.encoding = np.ones(128)
        self.threshold = 0.6

    def test_owner_recognized(self):
        with patch("face_recognition.face_distance", side_effect=[[0.3]]):
            owner_present, strangers = FaceAuthenticator.classify_faces(
                [self.encoding], self.reference, self.threshold)
        self.assertTrue(owner_present)
        self.assertEqual(strangers, 0)

    def test_stranger_only(self):
        with patch("face_recognition.face_distance",
                   side_effect=[[0.9], [0.8]]):
            owner_present, strangers = FaceAuthenticator.classify_faces(
                [self.encoding, self.encoding], self.reference, self.threshold)
        self.assertFalse(owner_present)
        self.assertEqual(strangers, 2)

    def test_owner_next_to_a_stranger(self):
        with patch("face_recognition.face_distance",
                   side_effect=[[0.95], [0.2]]):
            owner_present, strangers = FaceAuthenticator.classify_faces(
                [self.encoding, self.encoding], self.reference, self.threshold)
        self.assertTrue(owner_present)
        self.assertEqual(strangers, 1)

    def test_no_reference_profile(self):
        owner_present, strangers = FaceAuthenticator.classify_faces(
            [self.encoding, self.encoding], None, self.threshold)
        self.assertFalse(owner_present)
        self.assertEqual(strangers, 2)

class AuthenticateTest(unittest.TestCase):
    """Full pipeline behavior with mocked face_recognition calls."""

    def test_no_face_in_frame_returns_no_strangers(self):
        auth = build_authenticator()
        auth.reference_encoding = np.zeros(128)
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with patch("face_recognition.face_encodings", return_value=[]):
            owner_present, strangers = auth.authenticate(blank_frame)
        self.assertFalse(owner_present)
        self.assertEqual(strangers, 0)

    def test_none_frame_is_rejected_safely(self):
        auth = build_authenticator()
        auth.reference_encoding = np.zeros(128)
        owner_present, strangers = auth.authenticate(None)
        self.assertFalse(owner_present)
        self.assertEqual(strangers, 0)

class VerifyThrottlingTest(unittest.TestCase):
    """Cached verdict must spare the expensive recognition pass."""

    def test_full_check_runs_once_per_interval(self):
        auth = build_authenticator()
        auth.check_interval = 3
        auth.reference_encoding = np.zeros(128)
        with patch.object(FaceAuthenticator, "authenticate",
                          return_value=(True, 0)) as mock_auth:
            for _ in range(4):
                auth.verify(np.zeros((10, 10, 3), dtype=np.uint8))
            self.assertEqual(mock_auth.call_count, 2)
            for _ in range(3):
                auth.verify(np.zeros((10, 10, 3), dtype=np.uint8))
            self.assertEqual(mock_auth.call_count, 3)

    def test_first_call_always_checks(self):
        auth = build_authenticator()
        auth.check_interval = 5
        auth.reference_encoding = np.zeros(128)
        with patch.object(FaceAuthenticator, "authenticate",
                          return_value=(False, 1)) as mock_auth:
            result = auth.verify(np.zeros((10, 10, 3), dtype=np.uint8))
        mock_auth.assert_called_once()
        self.assertEqual(result, (False, 1))

class ConfigLoadingTest(unittest.TestCase):
    """Configuration file values must override fallbacks."""

    def test_settings_are_loaded_from_json(self):
        config = {
            "security": {
                "reference_image_path": "/tmp/fake_owner.jpeg",
                "face_distance_threshold": 0.45
            },
            "optimizations": {
                "auth_check_interval": 2
            }
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            path = f.name
        try:
            auth = FaceAuthenticator(config_path=path)
            self.assertEqual(auth.reference_image_path, "/tmp/fake_owner.jpeg")
            self.assertAlmostEqual(auth.distance_threshold, 0.45)
            self.assertEqual(auth.check_interval, 2)
        finally:
            os.unlink(path)

class InputMonitorTest(unittest.TestCase):
    """The monitor must degrade gracefully when idle time is unavailable."""

    def test_idle_seconds_is_none_or_positive_float(self):
        monitor = InputActivityMonitor()
        value = monitor.get_idle_seconds()
        self.assertTrue(value is None or (isinstance(value, float) and value >= 0))

if __name__ == "__main__":
    unittest.main()
