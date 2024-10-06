import cv2
import mediapipe as mp
import math
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import time
import numpy as np
import requests
import json

app = Flask(__name__)
CORS(app)

class PoseDetector:
    def __init__(self, mode=False, complexity=1, smooth_landmarks=True,
                 enable_segmentation=False, smooth_segmentation=True,
                 detectionCon=0.5, trackCon=0.5):
        
        self.mode = mode 
        self.complexity = complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.complexity, self.smooth_landmarks,
                                     self.enable_segmentation, self.smooth_segmentation,
                                     self.detectionCon, self.trackCon)
        
    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
                
        return img
    
    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255,0,0), cv2.FILLED)
        return self.lmList

# Global storage for captured data
landmark_storage = []
user_query = ""

def capture_landmarks_for_duration(duration=3):
    global landmark_storage
    landmark_storage = []  # Reset storage
    
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, img = cap.read()
        if not ret:
            break
        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        if lmList:
            landmark_storage.append(lmList)  # Collect the landmarks

    cap.release()

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

import numpy as np

def process_landmarks():
    if not landmark_storage:
        return None

    # Calculate average position for each landmark
    avg_landmarks = np.mean(landmark_storage, axis=0)

    # Define landmark indices
    NOSE = 0
    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    def get_point(index):
        return avg_landmarks[index][1:]

    def calculate_angle(a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        return angle if angle <= 180.0 else 360 - angle

    # Calculate knee angle (average of left and right)
    left_knee_angle = calculate_angle(get_point(LEFT_HIP), get_point(LEFT_KNEE), get_point(LEFT_ANKLE))
    right_knee_angle = calculate_angle(get_point(RIGHT_HIP), get_point(RIGHT_KNEE), get_point(RIGHT_ANKLE))
    knee_angle = (left_knee_angle + right_knee_angle) / 2

    # Calculate back angle
    # Using the angle between the line from hip to shoulder and the vertical
    mid_hip = (get_point(LEFT_HIP) + get_point(RIGHT_HIP)) / 2
    mid_shoulder = (get_point(LEFT_SHOULDER) + get_point(RIGHT_SHOULDER)) / 2
    vertical_point = [mid_hip[0], mid_hip[1] - 100]  # A point directly above mid_hip
    back_angle = calculate_angle(vertical_point, mid_hip, mid_shoulder)

    # Calculate hip angle (average of left and right)
    left_hip_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_HIP), get_point(LEFT_KNEE))
    right_hip_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_HIP), get_point(RIGHT_KNEE))
    hip_angle = (left_hip_angle + right_hip_angle) / 2

    # Calculate additional angles for more comprehensive analysis
    # Ankle angle (average of left and right)
    left_ankle_angle = calculate_angle(get_point(LEFT_KNEE), get_point(LEFT_ANKLE), [get_point(LEFT_ANKLE)[0], get_point(LEFT_ANKLE)[1]+100])
    right_ankle_angle = calculate_angle(get_point(RIGHT_KNEE), get_point(RIGHT_ANKLE), [get_point(RIGHT_ANKLE)[0], get_point(RIGHT_ANKLE)[1]+100])
    ankle_angle = (left_ankle_angle + right_ankle_angle) / 2

    # Shoulder alignment (angle between shoulders and horizontal)
    horizontal_point = [get_point(LEFT_SHOULDER)[0] + 100, get_point(LEFT_SHOULDER)[1]]
    shoulder_alignment = calculate_angle(horizontal_point, get_point(LEFT_SHOULDER), get_point(RIGHT_SHOULDER))

    angles = {
        "knee_angle": knee_angle,
        "back_angle": back_angle,
        "hip_angle": hip_angle,
        "ankle_angle": ankle_angle,
        "shoulder_alignment": shoulder_alignment
    }

    return angles

@app.route('/start_capture', methods=['POST'])
def start_capture():
    global user_query
    data = request.json
    user_query = data.get('user_query')
    
    # Capture landmarks for 5 seconds
    capture_landmarks_for_duration(3)
    
    # Process landmarks and send to analysis endpoint
    angles = process_landmarks()
    if angles is None:
        return jsonify({"error": "No landmarks captured"}), 400
    
    payload = {
        "joint_angles": angles,
        "user_query": user_query
    }
    
    try:
        response = requests.post('http://localhost:5005/analyze', json=payload)
        pretty_json = json.dumps(payload, indent=4)
        print(pretty_json)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to send data to analysis endpoint: {str(e)}"}), 500

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    while True: 
        ret, img = cap.read()
        if not ret:
            break
        img = detector.findPose(img)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)