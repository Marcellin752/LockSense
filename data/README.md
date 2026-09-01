# data/

Local runtime data for LockSense. **Never commit the contents of this folder** (except this README): it may contain biometric material.

## Contents

| File | Description |
|------|-------------|
| `reference/owner.jpeg` | Reference photo of the authorized user, used to compute the face encoding for authentication. |
| `reference/session_current.jpg` | Snapshot of the current face in front of the webcam, captured at runtime for comparison. |

These files are generated/managed locally by the application and are excluded via `.gitignore`. LockSense is 100% local: no image or biometric data ever leaves this machine.
