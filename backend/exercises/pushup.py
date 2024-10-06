from time import time

last_alert_time = {}
ALERT_COOLDOWN = 3  # Seconds between alerts

def analyze_pushup(joint_angles):
    elbow_angle = joint_angles.get('elbow_angle', 0)
    hip_angle = joint_angles.get('hip_angle', 0)
    hand_to_shoulder_angle = joint_angles.get('hand_to_shoulder_angle', 0)

    feedback = []
    if elbow_angle > 160:
        feedback.append("Lower chest more.")
    elif elbow_angle < 90:
        feedback.append("Push up slightly.")

    if hip_angle < 160:
        feedback.append("Raise hips.")
    elif hip_angle > 170:
        feedback.append("Lower hips slightly.")

    if hand_to_shoulder_angle < 80:
        feedback.append("Widen hand placement.")
    elif hand_to_shoulder_angle > 100:
        feedback.append("Narrow hand placement.")

    if not feedback:
        feedback.append("Maintain current form.")

    current_time = time()
    if current_time - last_alert_time.get('pushup', 0) > ALERT_COOLDOWN:
        last_alert_time['pushup'] = current_time
        return ". ".join(feedback)
    return ""