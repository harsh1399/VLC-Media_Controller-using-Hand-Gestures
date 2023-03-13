import cv2
import mediapipe as mp
import vlc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import math
import numpy as np


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volper = 0
volume.GetMute()
volume.GetMasterVolumeLevel()
volume_range = volume.GetVolumeRange()
media = vlc.MediaPlayer("bbt.avi")
pause_flag = True
media.play()

vol = 0
volbar = 350
wCam,hCam = 640,480
cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.rectangle(image, (380, 75), (630, 350), (153, 255, 204), 1)
        x_roi1, y_roi1 = 380, 75
        x_roi2, y_roi2 = 630, 350

        cv2.rectangle(image, (125, 75), (225, 350), (153, 255, 204), 1)
        x_roi3, y_roi3 = 125, 75
        x_roi4, y_roi4 = 225, 350

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

            pinky_finger_x, pinky_finger_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x*wCam), int(
                hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y*hCam)
            thumb_x, thumb_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x*wCam), int(
                hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y*hCam)

            if (x_roi1 < thumb_x) and (pinky_finger_x < x_roi2):
                cv2.putText(image, 'Play/Pause controller', (355, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (26, 26, 26), 2)
                wrist_x, wrist_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * wCam), int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y *hCam)
                middle_finger_x, middle_finger_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x *wCam), int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * hCam)

                cv2.line(image, (wrist_x, wrist_y), (middle_finger_x, middle_finger_y), (159, 226, 191), 3)
                length1 = math.hypot(wrist_x - middle_finger_x, wrist_y - middle_finger_y)
                print(length1)
                if length1 > 120 and pause_flag == False:
                    pause_flag = True
                    media.play()
                    cv2.putText(image, 'Play ', (390, 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (26, 26, 26), 2)
                elif length1 < 110 and pause_flag == True:
                    pause_flag = False
                    media.pause()
                    cv2.putText(image, 'Pause', (390, 150), cv2.FONT_HERSHEY_COMPLEX, 0.7, (26, 26, 26), 2)

            elif (x_roi3 < thumb_x) and (pinky_finger_x < x_roi4):
                cv2.putText(image, 'Volume controller', (125, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (26, 26, 26), 2)
                thumb_x, thumb_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * wCam ), int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * hCam)
                index_finger_x, index_finger_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * wCam), int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * hCam)
                cx = int((thumb_x + index_finger_x) / 2)
                cy = int((thumb_y + index_finger_y) / 2)

                cv2.circle(image, (thumb_x, thumb_y), 15, (204, 204, 255), cv2.FILLED)
                cv2.circle(image, (index_finger_x, index_finger_y), 15, (204, 204, 255), cv2.FILLED)
                cv2.circle(image, (cx, cy), 15, (204, 204, 255), cv2.FILLED)

                cv2.line(image, (thumb_x, thumb_y), (index_finger_x, index_finger_y), (159, 226, 191), 3)
                length = math.hypot(index_finger_x - thumb_x, index_finger_y - thumb_y)

                if length < 30:
                    cv2.circle(image, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

                vol = np.interp(length*2, [30, 200], [volume_range[0], volume_range[1]])
                volbar = np.interp(length, [30, 200], [350, 100])
                volper = np.interp(length, [30, 200], [0, 100])
                # print(vol)
                volume.SetMasterVolumeLevel(vol, None)

            cv2.rectangle(image, (50, 100), (85, 350), (153, 204, 255), 3)
            cv2.rectangle(image, (50, int(volbar)), (85, 350), (102, 255, 255), cv2.FILLED)
            cv2.putText(image, f'{int(volper)}%', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (26, 26, 26), 2)
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('VLC Media Player Controller', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break

# cap.release()