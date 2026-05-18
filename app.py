import cv2
import mediapipe as mp
from cvzone.HandTrackingModule import HandDetector

from config import CAMERA_HEIGHT, CAMERA_WIDTH, PINCH_DISTANCE, WINDOW_NAME
from ui import draw_app_dock, draw_cursor, draw_menu_button, draw_quit_hint, menu_button_rect
from video_player import VideoPlayerWindow
from vision_utils import distance, lerp, point_inside


def create_apps():
    return [
        {"name": "Browser", "active": False, "rect": (0, 0, 0, 0)},
        {"name": "Photos", "active": False, "rect": (0, 0, 0, 0)},
        {"name": "Video", "active": False, "rect": (0, 0, 0, 0)},
        {"name": "Music", "active": False, "rect": (0, 0, 0, 0)},
        {"name": "Notes", "active": False, "rect": (0, 0, 0, 0)},
        {"name": "Focus", "active": False, "rect": (0, 0, 0, 0)},
    ]


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    detector = HandDetector(detectionCon=0.75, maxHands=2)
    segmenter = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
    video_player = VideoPlayerWindow()
    apps = create_apps()

    cursor_x = CAMERA_WIDTH // 2
    cursor_y = CAMERA_HEIGHT // 2
    pinch_locked = False
    dock_open = False
    resize_start_gap = None
    resize_start_width = None

    while True:
        success, frame = cap.read()
        if not success:
            print("Camera frame not available. Check webcam permissions or camera index.")
            break

        frame = cv2.flip(frame, 1)
        camera_frame = frame.copy()
        hands, frame = detector.findHands(frame, draw=False)

        is_pinching = False

        if hands:
            hand = hands[0]
            lm_list = hand["lmList"]
            index_tip = lm_list[8]
            thumb_tip = lm_list[4]

            cursor_x = int(lerp(cursor_x, index_tip[0], 0.32))
            cursor_y = int(lerp(cursor_y, index_tip[1], 0.32))
            pinch_gap = distance(index_tip, thumb_tip)
            is_pinching = pinch_gap < PINCH_DISTANCE

            if video_player.is_open and len(hands) >= 2 and both_hands_pinching(hands):
                left_index = hands[0]["lmList"][8]
                right_index = hands[1]["lmList"][8]
                current_gap = distance(left_index, right_index)
                if resize_start_gap is None:
                    resize_start_gap = current_gap
                    resize_start_width = video_player.rect[2]
                target_width = resize_start_width + (current_gap - resize_start_gap)
                video_player.resize_from_width(target_width, frame.shape[1], frame.shape[0])
                pinch_locked = True
            else:
                resize_start_gap = None
                resize_start_width = None

            if is_pinching and not pinch_locked:
                cursor = (cursor_x, cursor_y)
                if point_inside(cursor, menu_button_rect(frame)):
                    dock_open = not dock_open
                elif video_player.is_open and handle_video_pinch(cursor, video_player):
                    sync_video_app_state(apps, video_player)
                elif dock_open:
                    handle_app_pinch(apps, cursor, video_player)
                pinch_locked = True
            elif not is_pinching:
                pinch_locked = False

        frame = cv2.GaussianBlur(frame, (0, 0), 0.18)
        cursor = (cursor_x, cursor_y)

        video_player.update()
        if video_player.behind_body:
            video_layer = frame.copy()
            video_player.draw(video_layer)
            frame = place_layer_behind_person(camera_frame, video_layer, segmenter)
        else:
            video_player.draw(frame)

        draw_app_dock(frame, apps, cursor, dock_open)
        draw_menu_button(frame, dock_open, hover=point_inside(cursor, menu_button_rect(frame)))
        draw_cursor(frame, cursor_x, cursor_y, is_pinching)
        draw_quit_hint(frame)

        cv2.imshow(WINDOW_NAME, frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video_player.release()
    segmenter.close()
    cap.release()
    cv2.destroyAllWindows()


def handle_app_pinch(apps, cursor, video_player):
    for app in apps:
        if not point_inside(cursor, app["rect"]):
            continue

        if app["name"] == "Video":
            video_player.toggle()
            app["active"] = video_player.is_open
        else:
            app["active"] = not app["active"]


def handle_video_pinch(cursor, video_player):
    controls = video_player.controls_hit(cursor)
    if point_inside(cursor, controls["close"]):
        video_player.is_open = False
        return True

    if point_inside(cursor, controls["depth"]):
        video_player.toggle_depth()
        return True

    return False


def sync_video_app_state(apps, video_player):
    for app in apps:
        if app["name"] == "Video":
            app["active"] = video_player.is_open


def both_hands_pinching(hands):
    if len(hands) < 2:
        return False

    for hand in hands[:2]:
        landmarks = hand["lmList"]
        if distance(landmarks[8], landmarks[4]) >= PINCH_DISTANCE:
            return False
    return True


def place_layer_behind_person(camera_frame, layer_frame, segmenter):
    rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    result = segmenter.process(rgb)
    if result.segmentation_mask is None:
        return layer_frame

    mask = result.segmentation_mask
    mask = cv2.GaussianBlur(mask, (21, 21), 0)
    person_mask = mask > 0.52
    composed = layer_frame.copy()
    composed[person_mask] = camera_frame[person_mask]
    return composed


if __name__ == "__main__":
    main()
