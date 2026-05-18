<div align="center">

# Mini Vision Pro

**A webcam-based vision interface controlled with hand gestures.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-00A67E?style=for-the-badge)](https://developers.google.com/mediapipe)
[![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)](LICENSE)

Mini Vision Pro turns your webcam into a small spatial interface. Move your hand to control a cursor, pinch to select, open a floating app dock, and control a video window that can appear in front of or behind your body.

</div>

---

## Overview

Mini Vision Pro is built with Python, OpenCV, MediaPipe, and cvzone. It tracks your hand in real time, draws a smooth cursor over the camera feed, and gives you a simple gesture-driven desktop-style experience.

The project currently includes:

- A hand-tracked cursor
- Pinch-to-click interaction
- A floating mini app dock
- A gesture-controlled video player
- Two-hand resize for the video window
- Person segmentation for front or behind-body video depth

## Demo Video

Watch the demo here: [Mini Vision Pro Demo](http://youtube.com/watch?v=uohsfJN9cBo)

## Preview

```text
Webcam Feed
    |
    |-- Hand Tracking
    |-- Gesture Detection
    |-- Floating Cursor
    |-- Mini App Dock
    |-- Video Player Window
```

## Tech Stack

| Tool | Purpose |
| --- | --- |
| Python | Main application language |
| OpenCV | Webcam feed, drawing, video processing |
| MediaPipe | Person segmentation |
| cvzone | Hand tracking helpers |
| NumPy | Geometry and drawing support |

## Requirements

- Python 3.10 or newer
- A working webcam
- Camera permission enabled
- A local video file named `video.mp4`

The video file can be placed in any of these locations:

```text
video.mp4
assets/video.mp4
videos/video.mp4
```

## Installation

Clone or open the project, then install the Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with:

```bash
venv\Scripts\activate
```

## Run The App

```bash
python app.py
```

Press `q` anytime to close the camera window.

## Gesture Controls

| Action | Gesture |
| --- | --- |
| Move cursor | Move your index finger |
| Click or select | Pinch index finger and thumb |
| Open or close dock | Pinch on the menu button |
| Open video player | Pinch the Video app icon |
| Close video player | Pinch the close control |
| Change video depth | Pinch the Front or Behind control |
| Resize video player | Pinch with both hands and move hands apart or together |

## Project Structure

```text
mini_vision/
├── app.py              # Main camera loop and gesture logic
├── config.py           # App constants and video paths
├── ui.py               # Dock, cursor, icons, and visual controls
├── video_player.py     # Floating video player behavior
├── vision_utils.py     # Shared geometry and drawing helpers
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT license
└── README.md           # Project documentation
```

## How It Works

1. OpenCV reads frames from your webcam.
2. cvzone detects hand landmarks from the frame.
3. The index finger position becomes the on-screen cursor.
4. The distance between index finger and thumb decides whether you are pinching.
5. Pinch events trigger dock, app, and video controls.
6. MediaPipe segmentation allows the video layer to appear behind the detected person.

## Configuration

You can adjust the core app settings in `config.py`:

```python
WINDOW_NAME = "Mini Vision Pro"
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
PINCH_DISTANCE = 42
```

Increase `PINCH_DISTANCE` if clicking feels too strict. Decrease it if clicks trigger too easily.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Camera does not open | Check webcam permissions and make sure no other app is using the camera |
| Video player shows a missing-video message | Add `video.mp4` to the project root, `assets/`, or `videos/` |
| Pinch is hard to trigger | Increase `PINCH_DISTANCE` in `config.py` |
| Pinch triggers too often | Decrease `PINCH_DISTANCE` in `config.py` |
| App feels slow | Try lowering `CAMERA_WIDTH` and `CAMERA_HEIGHT` in `config.py` |

## Author

**Syed Umer Fayyaz**

- X: [@official_SUmerF](https://x.com/official_SUmerF)
- LinkedIn: [syed-umer-fayyaz](https://www.linkedin.com/in/syed-umer-fayyaz/)
- Website: [syedumerfayyaz.com](http://syedumerfayyaz.com/)

## License

This project is licensed under the [MIT License](LICENSE).
