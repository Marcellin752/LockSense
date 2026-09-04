#!/usr/bin/env python3
##
## PROJECT, 2026
## LockSense
## File description:
## Operating system security lock trigger module
##

import os
import platform
import subprocess

class OSTrigger:
    def __init__(self):
        # Detect the operating system during initialization
        self.current_os = platform.system()
        print(f"[LockSense] Security trigger initialized for OS: {self.current_os}")

    def lock_session(self):
        """
        Triggers the native system command to lock the workstation 
        based on the detected operating system.
        """
        try:
            if self.current_os == "Linux":
                self._lock_linux()
            elif self.current_os == "Windows":
                self._lock_windows()
            elif self.current_os == "Darwin":  # macOS fallback
                self._lock_mac()
            else:
                print(f"[Error] Unsupported operating system: {self.current_os}")
        except Exception as e:
            print(f"[Error] Failed to execute lock command. Exception: {e}")

    def _lock_linux(self):
        """Executes the locking command for Linux environments."""
        print("[LockSense] Triggering Linux session lock...")
        
        # Priority 1: Standard XDG screensaver (commonly used in test scripts)
        # Priority 2: GNOME environments (Ubuntu standard)
        # Priority 3: Cinnamon / Mint environments fallback
        commands = [
            "xdg-screensaver lock",
            "gnome-screensaver-command -l",
            "cinnamon-screensaver-command -l"
        ]
        
        for cmd in commands:
            # Using subprocess with shell=True to easily pipe environment desk commands
            result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return
        
        print("[Warning] Standard Linux lock commands failed. Attempting alternative window manager bypass.")

    def _lock_windows(self):
        """Executes the locking command for Windows environments."""
        print("[LockSense] Triggering Windows workstation lock...")
        # Calls the system user32.dll API to lock the workstation instantly
        ctypes_lock_cmd = "rundll32.exe user32.dll,LockWorkStation"
        subprocess.run(ctypes_lock_cmd, shell=True)

    def _lock_mac(self):
        """Executes the locking command for macOS environments."""
        print("[LockSense] Triggering macOS session lock...")
        mac_lock_cmd = "pmset displaysleepnow"
        subprocess.run(mac_lock_cmd, shell=True)
