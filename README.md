# Lock Sense

**Lock Sense** is a local, lightweight software solution designed to automate workstation security through real-time face recognition and presence analysis.
Initially developed to mitigate the risks of session compromise in shared academic environments (such as the busy open spaces at Epitech), the system instantly locks the machine as soon as the authorized user steps away.

## The Concept

By continuously analyzing the webcam feed, your machine becomes "aware" of your physical presence:
- **Are you in front of your screen?** The system remains active.
- **Do you step away or does a stranger sit down?** The script detects the anomaly and instantly locks the session.

## Features

- **Zero Human Error:** No more relying on memory to hit `Win + L` or `Ctrl + Alt + L` every time you stand up.
- **Rapid Response:** Locks the workstation within seconds, closing the vulnerability window left by standard OS idle-time sleep settings.
- **100% Local Processing:** Absolute privacy. No images or biometric data ever leave your machine or get uploaded to third-party servers.
- **Biometric Authentication:** Only the authorized owner is recognized as "protected" — a stranger in front of the screen triggers an immediate lock.
- **Multi-Face Detection:** Up to 5 faces are tracked simultaneously. An intruder next to the owner is detected and locks the session.
- **Anti-False-Positives:** Recent keyboard/mouse activity extends the tolerance window while the face is undetected.
- **Smart Delay:** Configurable tolerance threshold (default 5s) to prevent accidental locking during natural head movements or blinking.
- **CPU Optimization:** Low-resolution capture (640x480), throttled biometric checks (1 frame on 5), and idle mode while locked.

## Technical Stack

- **Language:** Python 3.x
- **Key Libraries:**
  - `OpenCV`: Handles the webcam video stream capture and downsampling optimizations.
  - `MediaPipe` (Face Detection): Highly optimized first-level filtering to detect a human face with minimal CPU impact.
  - `Face Recognition` (dlib): Extracts facial landmarks and performs continuous biometric verification against the authorized profile.
  - `Pillow` (PIL): Required by MediaPipe's drawing utilities.

## Pipeline Architecture

1. **Capture & Downsampling (OpenCV):** Acquires the webcam video stream and resizes it to a lower resolution to preserve CPU cycles.
2. **Detection (MediaPipe):** Rapidly checks for the presence of any human face and derives bounding boxes.
3. **Authentication (Face Recognition):** Compares facial features with the pre-registered owner's profile if a face is detected. Bounding boxes are reused to skip the expensive face detector.
4. **System Action:** Triggers a native OS command to lock the session immediately if the user is absent or unrecognized.

## Installation & Setup

### Prerequisites

Ensure you have Python 3 installed, along with the compilation tools required for `dlib` (such as CMake).

```bash
# On Ubuntu / Debian
sudo apt-get install cmake build-essential libgtk-3-dev libboost-python-dev
```

> For keyboard/mouse activity gating on Linux, install `xprintidle`:
> ```bash
> sudo apt-get install xprintidle
> ```

### Clone the repository:

```bash
git clone git@github.com:Marcellin752/LockSense.git
cd LockSense
```

### Install the required dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Enroll the owner profile:

Before the first run, capture your reference photo (used for biometric verification):

```bash
python3 scripts/enroll_owner.py
```

Position yourself in front of the webcam, then press `SPACE` to save (`Q` to cancel). The photo is stored locally in `data/reference/` and never leaves your machine.

## Run the application:

```bash
python3 src/main.py
```

## Configuration

All runtime parameters are centralized in `config/settings.json`. See `config/README.md` for the full reference:

| Section | Key | Default | Description |
|---------|-----|---------|-------------|
| `camera` | `device_index` | `0` | Webcam index (change if multiple cameras). |
| `camera` | `width` / `height` | `640` / `480` | Capture resolution. |
| `optimizations` | `target_fps` | `5` | Target frame rate for the capture loop. |
| `optimizations` | `auth_check_interval` | `5` | Run biometric verification once every N frames. |
| `optimizations` | `draw_face_mesh` | `false` | Render MediaPipe face mesh on the video feed. |
| `optimizations` | `gating_mouse_keyboard` | `true` | Extend tolerance when recent keyboard/mouse activity is detected. |
| `optimizations` | `inactivity_trigger_seconds` | `10` | Idle threshold for input gating (seconds). |
| `security` | `tolerance_seconds` | `5` | Absence duration before the session is locked (seconds). |
| `security` | `reference_image_path` | `data/reference/owner.jpeg` | Path to the owner reference photo. |
| `security` | `face_distance_threshold` | `0.6` | Biometric match threshold (lower = stricter, 0.6 is typical). |
| `logging` | `level` | `INFO` | Log verbosity: DEBUG, INFO, WARNING, ERROR, CRITICAL. |
| `logging` | `retention_days` | `7` | Number of rotated log files to keep. |

## Logging

LockSense writes structured logs to `logs/locksense.log` with daily rotation at midnight.
Rotated files are kept for up to `retention_days` days (default: 7).

```
2026-09-08 15:23:00 [INFO] locksense.main - Logger initialized (level=INFO, retention=7 days)
2026-09-08 15:23:00 [INFO] locksense.main - === LockSense initializing ===
```

## Data Privacy

- Biometric data (owner photo, live snapshots) is stored locally in `data/` and **never leaves your machine**.
- `data/` is git-ignored by default; only `data/README.md` is tracked.
- `logs/` is git-ignored by default; only `logs/README.md` is tracked.

## Current Challenges & Optimizations

The project is currently focusing on reducing its CPU footprint and optimising the Face Recognition system. Real-time image processing is computationally expensive.

## Author

[Marcellin SAMBIENI](https://github.com/Marcellin752) - Eitech Student