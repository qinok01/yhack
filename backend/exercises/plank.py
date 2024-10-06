from time import time

last_alert_time = {}
ALERT_COOLDOWN = 3  # Seconds between alerts

def analyze_plank(joint_angles):
    hip_angle = joint_angles.get('hip_angle', 0)
    shoulder_angle = joint_angles.get('shoulder_angle', 0)

    feedback = []
    if hip_angle < 160:
        feedback.append("Raise hips slightly.")
    elif hip_angle > 170:
        feedback.append("Lower hips slightly.")

    if shoulder_angle < 70:
        feedback.append("Move shoulders forward.")
    elif shoulder_angle > 110:
        feedback.append("Move shoulders back.")

    if not feedback:
        feedback.append("Maintain current form.")

    current_time = time()
    if current_time - last_alert_time.get('plank', 0) > ALERT_COOLDOWN:
        last_alert_time['plank'] = current_time
        return ". ".join(feedback)
    return ""