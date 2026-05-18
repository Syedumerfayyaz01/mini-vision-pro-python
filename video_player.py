from pathlib import Path

import cv2
import numpy as np

from config import VIDEO_PATHS
from vision_utils import rounded_rect


class VideoPlayerWindow:
    def __init__(self):
        self.is_open = False
        self.is_playing = True
        self.behind_body = False
        self.capture = None
        self.video_path = None
        self.frame = None
        self.rect = (220, 96, 840, 520)
        self.min_width = 420
        self.max_width = 1120

    def toggle(self):
        self.is_open = not self.is_open
        if self.is_open:
            self._ensure_video_loaded()

    def _find_video(self):
        for path in VIDEO_PATHS:
            candidate = Path(path)
            if candidate.exists():
                return candidate
        return None

    def _ensure_video_loaded(self):
        found_path = self._find_video()
        if found_path == self.video_path and self.capture is not None:
            return

        if self.capture is not None:
            self.capture.release()

        self.video_path = found_path
        self.capture = None
        self.frame = None

        if found_path is not None:
            self.capture = cv2.VideoCapture(str(found_path))

    def update(self):
        if not self.is_open or not self.is_playing:
            return

        self._ensure_video_loaded()
        if self.capture is None:
            return

        success, frame = self.capture.read()
        if not success:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.capture.read()

        if success:
            self.frame = frame

    def draw(self, img):
        if not self.is_open:
            return

        self._keep_inside(img.shape[1], img.shape[0])
        x, y, panel_w, panel_h = self.rect

        overlay = img.copy()
        rounded_rect(overlay, (x, y), (x + panel_w, y + panel_h), (18, 22, 30), radius=30)
        cv2.addWeighted(overlay, 0.66, img, 0.34, 0, img)
        rounded_rect(img, (x, y), (x + panel_w, y + panel_h), (250, 252, 255), radius=30, thickness=1)

        header_h = 54
        cv2.circle(img, (x + 28, y + 27), 7, (82, 82, 255), cv2.FILLED)
        cv2.circle(img, (x + 50, y + 27), 7, (86, 205, 255), cv2.FILLED)
        cv2.circle(img, (x + 72, y + 27), 7, (110, 235, 150), cv2.FILLED)
        cv2.putText(img, "Video", (x + 98, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.66, (250, 252, 255), 2)
        depth_text = "Behind" if self.behind_body else "Front"
        rounded_rect(img, (x + panel_w - 124, y + 12), (x + panel_w - 18, y + 42), (58, 66, 78), radius=15)
        cv2.putText(img, depth_text, (x + panel_w - 105, y + 33), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (235, 242, 250), 1)

        video_area = (x + 22, y + header_h, panel_w - 44, panel_h - header_h - 58)
        self._draw_video_area(img, video_area)
        self._draw_controls(img, x, y, panel_w, panel_h)

    def _draw_video_area(self, img, area):
        x, y, w, h = area
        rounded_rect(img, (x, y), (x + w, y + h), (6, 9, 14), radius=20)

        if self.frame is None:
            message = "Add video.mp4 here"
            hint = "or use assets/video.mp4 / videos/video.mp4"
            cv2.putText(img, message, (x + 42, y + h // 2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (245, 250, 255), 2)
            cv2.putText(img, hint, (x + 42, y + h // 2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 192, 208), 1)
            return

        video = cv2.resize(self.frame, self._cover_size(self.frame, w, h))
        vh, vw, _ = video.shape
        crop_x = max((vw - w) // 2, 0)
        crop_y = max((vh - h) // 2, 0)
        video = video[crop_y : crop_y + h, crop_x : crop_x + w]
        img[y : y + h, x : x + w] = video
        rounded_rect(img, (x, y), (x + w, y + h), (255, 255, 255), radius=20, thickness=2)

    def _draw_controls(self, img, x, y, w, h):
        control_y = y + h - 32
        play_x = x + 34

        cv2.circle(img, (play_x, control_y), 15, (245, 250, 255), cv2.FILLED)
        if self.is_playing:
            cv2.rectangle(img, (play_x - 5, control_y - 7), (play_x - 2, control_y + 7), (16, 22, 32), cv2.FILLED)
            cv2.rectangle(img, (play_x + 3, control_y - 7), (play_x + 6, control_y + 7), (16, 22, 32), cv2.FILLED)
        else:
            points = [(play_x - 5, control_y - 10), (play_x - 5, control_y + 10), (play_x + 11, control_y)]
            cv2.fillConvexPoly(img, np.array(points), (16, 22, 32))

        cv2.line(img, (x + 66, control_y), (x + w - 34, control_y), (145, 158, 176), 4)
        cv2.line(img, (x + 66, control_y), (x + min(w - 34, 250), control_y), (245, 250, 255), 4)

    def resize_from_width(self, target_width, frame_w, frame_h):
        old_x, old_y, old_w, _ = self.rect
        new_w = int(max(self.min_width, min(target_width, min(self.max_width, frame_w - 80))))
        new_h = int(new_w * 0.62)
        center_x = old_x + old_w // 2
        self.rect = (center_x - new_w // 2, old_y, new_w, min(new_h, frame_h - 140))
        self._keep_inside(frame_w, frame_h)

    def toggle_depth(self):
        self.behind_body = not self.behind_body

    def controls_hit(self, point):
        x, y, w, _ = self.rect
        depth_rect = (x + w - 128, y + 8, 110, 38)
        close_rect = (x + 14, y + 10, 28, 28)
        return {
            "depth": depth_rect,
            "close": close_rect,
        }

    def _keep_inside(self, frame_w, frame_h):
        x, y, w, h = self.rect
        x = max(28, min(x, frame_w - w - 28))
        y = max(44, min(y, frame_h - h - 120))
        self.rect = (x, y, w, h)

    def _cover_size(self, frame, target_w, target_h):
        source_h, source_w, _ = frame.shape
        scale = max(target_w / source_w, target_h / source_h)
        return int(source_w * scale), int(source_h * scale)

    def release(self):
        if self.capture is not None:
            self.capture.release()
