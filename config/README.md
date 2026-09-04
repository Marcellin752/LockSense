# config/

Configuration files for LockSense.

## Files

| File | Description |
|------|-------------|
| `settings.json` | Runtime configuration: camera, optimizations, security, and logging parameters. |

## settings.json

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
