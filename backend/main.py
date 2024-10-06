from flask import Flask, request, jsonify, Response
import mediapipe as mp
from flask_cors import CORS
import cv2
import math
from exercises.squat import analyze_squat
from exercises.pushup import analyze_pushup
from exercises.plank import analyze_plank
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# Configuration
SERVER_PORT = 5001
current_exercise = 'Squats'  # Default exercise

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
    lmList = detector.findPosition(img)
    if not lmList:
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
        'back_angle': detector.findAngle(img, 7, 11, 23, draw=False),  # Using left side for back angle
    }

def analyze_current_exercise(detector, img):
    global current_exercise
    try:
        joint_angles = get_joint_angles(detector, img)
        if current_exercise == 'Squats':
            feedback, debug_info, per, bar = analyze_squat(joint_angles)
        elif current_exercise == 'Pushups':
            feedback, debug_info, per, bar = analyze_pushup(joint_angles)
        elif current_exercise == 'Plank':
            feedback, debug_info, per, bar = analyze_plank(joint_angles)
        else:
            feedback, debug_info, per, bar = "Select an exercise.", "", 0, 0

        if feedback:
            print(f"Exercise Feedback: {feedback}")
        return feedback, debug_info, per, bar
    except ValueError:
        return "No pose detected.", "", 0, 0

# Global variables for video capture and pose detector
cap = None
detector = None

def initialize_capture():
    global cap, detector
    if cap is None:
        cap = cv2.VideoCapture(0)
    if detector is None:
        detector = PoseDetector()

@app.route('/start_capture', methods=['POST'])
def start_capture():
    global current_exercise, cap, detector
    try:
        initialize_capture()
        
        data = request.json
        user_query = data.get('user_query', '')

        # Capture a frame from the video feed
        success, img = cap.read()
        if not success:
            return jsonify({"error": "Failed to capture video frame"}), 500

        img = detector.findPose(img)
        payload = {
            "joint_angles": get_joint_angles(detector, img),
            "user_query": user_query
        }
        
        try:
            response = requests.post('http://localhost:5005/analyze', headers={"Content-Type": "application/json"}, json=payload)
            response.raise_for_status()
            print("Payload sent to endpoint:")
            print(json.dumps(payload, indent=4))
            return jsonify(response.json())
        except requests.RequestException as e:
            return jsonify({"error": f"Failed to send data to analysis endpoint: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def generate_frames(view_mode):
    global cap, detector
    initialize_capture()
    
    last_request_time = time.time()
    
    while True:
        success, img = cap.read()
        if not success:
            break
        img = detector.findPose(img)
        feedback, debug_info, per, bar = analyze_current_exercise(detector, img)

        # Calculate progress bar dimensions and position
        bar_width = 30
        bar_max_height = img.shape[0] - 100
        bar_current_height = int(bar_max_height * (per / 100))

        # Adjust bar position based on view mode
        if view_mode == 'split':
            bar_x = img.shape[1] // 2 - bar_width - 20
        else:  # full view
            bar_x = img.shape[1] - bar_width - 20

        # Display feedback and debug info
        cv2.putText(img, feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, debug_info, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Draw progress bar
        if current_exercise in ['Squats', 'Pushups', 'Plank']:
            cv2.rectangle(img, (bar_x, 50), (bar_x + bar_width, 50 + bar_max_height), (0, 255, 0), 3)
            cv2.rectangle(img, (bar_x, 50 + bar_max_height - bar_current_height), 
                          (bar_x + bar_width, 50 + bar_max_height), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (bar_x, 40), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

        # Send POST request every 30 seconds
        current_time = time.time()
        if current_time - last_request_time >= 30:
            prompt = f"The current exercise is: {current_exercise} The feedback for {current_exercise} is: {feedback}"
            payload = {"prompt": prompt, "exercise": current_exercise}
            try:
                response = requests.post('http://localhost:8080/prompt', 
                                         headers={"Content-Type": "application/json"}, 
                                         json=payload, 
                                         timeout=5)  # 5 seconds timeout
                response.raise_for_status()
                print(f"Sent POST request to 8080/prompt: {payload}")
            except requests.RequestException as e:
                print(f"Failed to send POST request: {str(e)}")
            
            last_request_time = current_time

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<view_mode>')
def video_feed(view_mode):
    return Response(generate_frames(view_mode), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_exercise', methods=['POST'])
def current_exercise_route():
    global current_exercise
    current_exercise = request.json.get('exercise', 'Squats')
    print(f"Exercise changed to: {current_exercise}")  # Console log the exercise change
    return jsonify({"message": "Exercise updated", "current_exercise": current_exercise}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)