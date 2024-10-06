from flask import Flask, request, jsonify, Response
import mediapipe as mp
from flask_cors import CORS
import cv2
import math
import numpy as np
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
SERVER_PORT = 5001
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TTS_SERVER_URL = 'http://localhost:8080/prompt'
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class PoseDetector:
    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=False, model_complexity=1, 
                                     smooth_landmarks=True, min_detection_confidence=0.5, 
                                     min_tracking_confidence=0.5)

    def findPose(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            self.mpDraw.draw_landmarks(
                img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mpDraw.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=1),
                connection_drawing_spec=self.mpDraw.DrawingSpec(color=(255, 255, 255), thickness=2)
            )
            for landmark in self.results.pose_landmarks.landmark:
                h, w, _ = img.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(img, (cx, cy), 10, (0, 0, 255), 2)  # Red outer circle
                cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)  # Green inner circle
        return img

    def findPosition(self, img):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        if len(self.lmList) < max(p1, p2, p3):
            return 0

        coords = [(self.lmList[p][1], self.lmList[p][2]) for p in [p1, p2, p3]]
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        x3, y3 = coords[2]

        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        angle = angle if angle >= 0 else angle + 360
        angle = min(angle, 360 - angle)

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            for x, y in coords:
                cv2.circle(img, (x, y), 10, (0, 0, 255), cv2.FILLED)
            cv2.putText(img, f"{int(angle)}", (x2 - 50, y2 + 50), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        return angle

def get_joint_angles(detector, img):
    lmDict = detector.findPosition(img)
    if not lmDict:
        raise ValueError("No pose detected")
    return {
        'left_shoulder_angle': detector.findAngle(img, 13, 11, 23, draw=False),
        'right_shoulder_angle': detector.findAngle(img, 14, 12, 24, draw=False),
        'left_hip_angle': detector.findAngle(img, 11, 23, 25, draw=False),
        'right_hip_angle': detector.findAngle(img, 12, 24, 26, draw=False),
        'left_knee_angle': detector.findAngle(img, 23, 25, 27, draw=False),
        'right_knee_angle': detector.findAngle(img, 24, 26, 28, draw=False),
        'left_ankle_angle': detector.findAngle(img, 25, 27, 31, draw=False),
        'right_ankle_angle': detector.findAngle(img, 26, 28, 32, draw=False),
        'back_angle': detector.findAngle(img, 7, 11, 23, draw=False),
        'left_elbow_angle': detector.findAngle(img, 11, 13, 15, draw=False),
        'right_elbow_angle': detector.findAngle(img, 12, 14, 16, draw=False),
        'left_hand_to_shoulder_angle': detector.findAngle(img, 15, 13, 11, draw=False),
        'right_hand_to_shoulder_angle': detector.findAngle(img, 16, 14, 12, draw=False),
    }

def analyze_pose(joint_angles, exercise):
    # Prepare the prompt for OpenAI
    prompt = f"""
    Analyze the following joint angles for a {exercise} exercise:
    {joint_angles}

    Provide a brief feedback on the form, highlighting:
    1. What the person is doing correctly
    2. Any issues with their form
    3. Specific suggestions for improvement

    Keep the response concise and actionable, suitable for real-time audio feedback.
    """

    # Send to OpenAI for analysis
    response = openai_client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are a fitness expert providing real-time feedback on exercise form."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150  # Adjust as needed for concise responses
    )

    feedback = response.choices[0].message.content.strip()
    return feedback, exercise

def send_to_tts(feedback, exercise):
    try:
        response = requests.post(TTS_SERVER_URL, json={
            'prompt': feedback,
            'exercise': exercise
        })
        if response.status_code == 200:
            print("Feedback sent to text-to-speech server")
        else:
            print(f"Failed to send feedback to text-to-speech server. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending feedback to text-to-speech server: {e}")

@app.route('/analyze', methods=['POST'])
def analyze_exercise():
    data = request.json
    joint_angles = data.get('joint_angles', {})
    exercise = data.get('exercise', 'unknown')
    
    feedback, exercise = analyze_pose(joint_angles, exercise)
    send_to_tts(feedback, exercise)
    
    return jsonify({"feedback": feedback})

@app.route('/video_feed')
def video_feed():
    exercise = request.args.get('exercise', 'Squats')  # Get exercise from query parameter
    def generate_frames():
        detector = PoseDetector()
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                frame = detector.findPose(frame)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_exercise', methods=['POST'])
def current_exercise_route():
    exercise = request.json.get('exercise', 'Squats')
    print(f"Exercise changed to: {exercise}")
    return jsonify({"message": "Exercise updated", "current_exercise": exercise}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)