import math

import cv2
import numpy as np

from vision_utils import point_inside, rounded_rect


def menu_button_rect(img):
    h, _, _ = img.shape
    return 38, h - 96, 74, 56


def draw_menu_button(img, is_open, hover=False):
    x, y, w, h = menu_button_rect(img)
    overlay = img.copy()
    fill = (250, 252, 255) if hover or is_open else (235, 240, 246)
    cv2.circle(overlay, (x + w // 2, y + h // 2), h // 2, fill, cv2.FILLED)
    cv2.addWeighted(overlay, 0.58, img, 0.42, 0, img)
    cv2.circle(img, (x + w // 2, y + h // 2), h // 2, (255, 255, 255), 1)

    line_color = (18, 22, 28)
    center_x = x + w // 2
    center_y = y + h // 2
    if is_open:
        cv2.line(img, (center_x - 10, center_y - 10), (center_x + 10, center_y + 10), line_color, 3)
        cv2.line(img, (center_x + 10, center_y - 10), (center_x - 10, center_y + 10), line_color, 3)
    else:
        for offset in (-9, 0, 9):
            cv2.line(img, (center_x - 13, center_y + offset), (center_x + 13, center_y + offset), line_color, 3)


def draw_app_icon(img, center, app_name, active=False):
    x, y = center
    radius = 31
    base_colors = {
        "Browser": (255, 154, 64),
        "Photos": (255, 94, 138),
        "Video": (112, 88, 255),
        "Music": (255, 62, 92),
        "Notes": (245, 218, 72),
        "Focus": (70, 210, 255),
    }
    color = base_colors.get(app_name, (230, 236, 244))

    cv2.circle(img, center, radius + (4 if active else 1), (255, 255, 255), cv2.FILLED)
    cv2.circle(img, center, radius, color, cv2.FILLED)

    if app_name == "Browser":
        cv2.circle(img, center, 20, (255, 255, 255), 2)
        cv2.line(img, (x - 12, y + 14), (x + 15, y - 14), (255, 255, 255), 3)
        cv2.circle(img, (x + 12, y - 11), 4, (255, 255, 255), cv2.FILLED)
    elif app_name == "Photos":
        for angle in range(0, 360, 45):
            dx = int(math.cos(math.radians(angle)) * 15)
            dy = int(math.sin(math.radians(angle)) * 15)
            cv2.circle(img, (x + dx, y + dy), 8, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, center, 8, color, cv2.FILLED)
    elif app_name == "Video":
        points = np.array([(x - 10, y - 17), (x - 10, y + 17), (x + 20, y)])
        cv2.fillConvexPoly(img, points, (255, 255, 255))
    elif app_name == "Music":
        cv2.line(img, (x + 8, y - 18), (x + 8, y + 11), (255, 255, 255), 4)
        cv2.line(img, (x + 8, y - 18), (x - 10, y - 14), (255, 255, 255), 4)
        cv2.circle(img, (x - 8, y + 14), 9, (255, 255, 255), cv2.FILLED)
    elif app_name == "Notes":
        rounded_rect(img, (x - 17, y - 21), (x + 17, y + 21), (255, 255, 255), radius=6)
        for offset in (-8, 2, 12):
            cv2.line(img, (x - 10, y + offset), (x + 10, y + offset), color, 2)
    elif app_name == "Focus":
        cv2.circle(img, center, 20, (255, 255, 255), 2)
        cv2.circle(img, center, 7, (255, 255, 255), cv2.FILLED)


def draw_app_dock(img, apps, cursor, is_open):
    if not is_open:
        return

    h, w, _ = img.shape
    dock_w = min(560, w - 190)
    dock_h = 94
    x = (w - dock_w) // 2
    y = h - dock_h - 28

    overlay = img.copy()
    rounded_rect(overlay, (x, y), (x + dock_w, y + dock_h), (238, 244, 250), radius=34)
    cv2.addWeighted(overlay, 0.46, img, 0.54, 0, img)
    rounded_rect(img, (x, y), (x + dock_w, y + dock_h), (255, 255, 255), radius=34, thickness=1)

    gap = dock_w // (len(apps) + 1)
    for index, app in enumerate(apps, start=1):
        center = (x + gap * index, y + 42)
        app["rect"] = (center[0] - 40, center[1] - 40, 80, 80)
        hover = point_inside(cursor, app["rect"])
        draw_app_icon(img, center, app["name"], active=hover or app["active"])
        cv2.putText(img, app["name"], (center[0] - 26, y + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (245, 250, 255), 1)


def draw_quit_hint(img):
    h, w, _ = img.shape
    cv2.putText(img, "q", (w - 34, h - 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (245, 250, 255), 1)


def draw_cursor(img, x, y, is_pinching):
    color = (84, 210, 255) if is_pinching else (255, 255, 255)
    radius = 18 if is_pinching else 13
    cv2.circle(img, (x, y), radius + 9, color, 1)
    cv2.circle(img, (x, y), radius, color, cv2.FILLED)
    cv2.circle(img, (x, y), 4, (25, 35, 45), cv2.FILLED)
