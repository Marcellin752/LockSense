# Lock Sense 

**Lock Sense** is a local, lightweight software solution designed to automate workstation security through real-time face recognition and presence analysis.
Initially developed to mitigate the risks of session compromise in shared academic environments (such as the busy open spaces at Epitech), the system instantly locks the machine as soon as the authorized user steps away.

##  The Concept

By continuously analyzing the webcam feed, your machine becomes "aware" of your physical presence:
- **Are you in front of your screen?** The system remains active.
- **Do you step away or does a stranger sit down?** The script detects the anomaly and instantly locks the session.

##  Features

- **Zero Human Error:** No more relying on memory to hit `Win + L` or `Ctrl + Alt + L` every time you stand up.
- **Rapid Response:** Locks the workstation within seconds, closing the vulnerability window left by standard OS idle-time sleep settings.
- **100% Local Processing:** Absolute privacy. No images or biometric data ever leave your machine or get uploaded to third-party servers.
- **Smart Delay (Anti-False Positives):** Features a 3-second tolerance threshold to prevent accidental locking during natural head movements or blinking.

## Technical Stack

- **Language:** Python 3.x
- **Key Libraries:**
  - `OpenCV`: Handles the webcam video stream capture and downsampling optimizations.
  - `MediaPipe` (Face Detection): Highly optimized first-level filtering to detect a human face with minimal CPU impact.
  - `Face Recognition` (dlib): Extracts facial landmarks and performs continuous biometric verification against the authorized profile.

##  Pipeline Architecture

1. **Capture & Downsampling (OpenCV):** Acquires the webcam video stream and resizes it to a lower resolution to preserve CPU cycles.
2. **Detection (MediaPipe):** Rapidly checks for the presence of any human face.
3. **Authentication (Face Recognition):** Compares facial features with the pre-registered owner's profile if a face is detected.
4. **System Action:** Triggers a native OS command to lock the session immediately if the user is absent or unrecognized.

## Installation & Setup

### Prerequisites

Ensure you have Python 3 installed, along with the compilation tools required for `dlib` (such as CMake).

```bash
# On Ubuntu / Debian
sudo apt-get install cmake build-essential libgtk-3-dev libboost-python-dev
```
## Installation

### Clone the repository:

```bash
git clone [https://github.com/your-username/lock-sense.git](https://github.com/your-username/lock-sense.git)
cd lock-sense
```

### Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Run the application:

```bash
python3 src/main.py
```

## Current Challenges & Optimizations

The project is currently focusing on reducing its CPU footprint. Real-time image processing is computationally expensive.

👤 Author

[Marcellin SAMBIENI](https://github.com/Marcellin752) - Epitech Student