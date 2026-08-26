#!/usr/bin/env python3
##
## EPITECH PROJECT, 2026
## LockSense
## File description:
## Keyboard/mouse activity monitor used as an anti-false-positive gate
##

import platform
import shutil
import subprocess

class InputActivityMonitor:
    def __init__(self):
        # Detect the operating system during initialization
        self.current_os = platform.system()

    def get_idle_seconds(self):
        """
        Returns the number of seconds elapsed since the last keyboard/mouse
        activity, or None when the feature is unavailable on this system.
        """
        try:
            if self.current_os == "Windows":
                return self._idle_windows()
            if self.current_os == "Darwin":
                return self._idle_mac()
            if self.current_os == "Linux":
                return self._idle_linux()
        except Exception:
            return None
        return None

    @staticmethod
    def _idle_windows():
        """Reads the idle time from the Win32 last-input API."""
        import ctypes

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint),
                        ("dwTime", ctypes.c_uint)]

        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return None
        millis = ctypes.windll.kernel32.GetTickCount() - info.dwTime
        return millis / 1000.0

    @staticmethod
    def _idle_mac():
        """Reads the HIDIdleTime value exposed by the IOHIDSystem registry."""
        result = subprocess.run(["ioreg", "-c", "IOHIDSystem"],
                                capture_output=True, text=True, timeout=2)
        for line in result.stdout.splitlines():
            if "HIDIdleTime" in line:
                nanoseconds = int(line.strip().rstrip(",").split("=")[-1])
                return nanoseconds / 1_000_000_000.0
        return None

    @staticmethod
    def _idle_linux():
        """Relies on xprintidle when available (X11 sessions)."""
        if not shutil.which("xprintidle"):
            return None
        result = subprocess.run(["xprintidle"],
                                capture_output=True, text=True, timeout=2)
        millis = float(result.stdout.strip())
        return millis / 1000.0
