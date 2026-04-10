import cv2
import numpy as np
from datetime import datetime

# Load OpenCV face and eye detectors (no mediapipe needed)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)


def analyze_frame(frame):
    result = {
        "face_count": 0,
        "alert"     : None,
        "gaze"      : "CENTER",
        "head_pose" : "CENTER",
        "frame"     : frame,
        "timestamp" : datetime.now().strftime("%H:%M:%S")
    }

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
    )

    result["face_count"] = len(faces)

    if len(faces) == 0:
        result["alert"] = "NO_FACE"
        cv2.putText(frame, "NO FACE DETECTED", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        result["frame"] = frame
        return result

    if len(faces) > 1:
        result["alert"] = "MULTIPLE_FACES"
        cv2.putText(frame, "MULTIPLE FACES!", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        result["frame"] = frame
        return result

    # Single face — analyze eyes
    for (fx, fy, fw, fh) in faces:
        cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (0, 255, 0), 2)

        # Region of interest — face only
        roi_gray  = gray[fy:fy+fh, fx:fx+fw]
        roi_color = frame[fy:fy+fh, fx:fx+fw]

        # Detect eyes within face
        eyes = eye_cascade.detectMultiScale(
            roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(20, 20)
        )

        eye_centers = []
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey),
                          (ex+ew, ey+eh), (255, 0, 0), 2)
            eye_center_x = ex + ew // 2
            eye_center_y = ey + eh // 2
            eye_centers.append((eye_center_x, eye_center_y))

        # Gaze estimation based on eye positions
        if len(eye_centers) >= 2:
            face_center_x = fw // 2
            avg_eye_x = np.mean([e[0] for e in eye_centers])

            offset = avg_eye_x - face_center_x
            if offset < -fw * 0.15:
                result["gaze"] = "LOOKING LEFT"
                result["alert"] = "EYE_LOOKING_LEFT"
            elif offset > fw * 0.15:
                result["gaze"] = "LOOKING RIGHT"
                result["alert"] = "EYE_LOOKING_RIGHT"
            else:
                result["gaze"] = "CENTER"

        elif len(eye_centers) == 0:
            result["alert"] = "EYES_NOT_VISIBLE"
            result["gaze"]  = "UNKNOWN"

        # Head pose — based on face position in frame
        frame_h, frame_w = frame.shape[:2]
        face_center_x = fx + fw // 2
        face_center_y = fy + fh // 2

        if face_center_x < frame_w * 0.35:
            result["head_pose"] = "LEFT"
            if not result["alert"]:
                result["alert"] = "HEAD_LEFT"
        elif face_center_x > frame_w * 0.65:
            result["head_pose"] = "RIGHT"
            if not result["alert"]:
                result["alert"] = "HEAD_RIGHT"
        elif face_center_y > frame_h * 0.70:
            result["head_pose"] = "DOWN"
            if not result["alert"]:
                result["alert"] = "HEAD_DOWN"
        else:
            result["head_pose"] = "CENTER"

    # Draw status text
    color = (0, 255, 0) if not result["alert"] else (0, 165, 255)
    cv2.putText(frame, f"Gaze: {result['gaze']}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(frame, f"Head: {result['head_pose']}",
                (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.putText(frame, f"Faces: {result['face_count']}",
                (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if result["alert"]:
        cv2.putText(frame, f"ALERT: {result['alert']}",
                    (10, 110), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 255), 2)

    result["frame"] = frame
    return result


def get_violation_message(alert_type):
    messages = {
        "NO_FACE"          : "Candidate not visible in frame",
        "MULTIPLE_FACES"   : "Multiple persons detected",
        "EYE_LOOKING_LEFT" : "Candidate looking left",
        "EYE_LOOKING_RIGHT": "Candidate looking right",
        "EYES_NOT_VISIBLE" : "Eyes not visible",
        "HEAD_LEFT"        : "Head turned left",
        "HEAD_RIGHT"       : "Head turned right",
        "HEAD_DOWN"        : "Head looking down",
        "TAB_SWITCH"       : "Candidate switched browser tab",
    }
    return messages.get(alert_type, "Suspicious activity detected")