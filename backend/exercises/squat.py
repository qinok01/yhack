from time import time

last_alert_time = {}

def analyze_squat_depth(knee_angle):
    if knee_angle < 120:
        return "depth is not deep enough", False
    else:
        return "depth is at point", True

def analyze_back_position(back_angle):
    if back_angle < 160:
        return "back is rounded", False
    else:
        return "back is straight", True

def analyze_hip_alignment(hip_angle):
    if -15 < hip_angle < 15:
        return "hips are aligned", True
    else:
        return "hips are not aligned", False

def should_alert(feature, is_correct):
    current_time = time()
    if not is_correct:
        if feature not in last_alert_time or (current_time - last_alert_time[feature]) > 2:
            last_alert_time[feature] = current_time
            return True
    return False

def analyze_squat(joint_angles):
    required_angles = ['knee_angle', 'back_angle', 'hip_angle']
    if not all(angle in joint_angles for angle in required_angles):
        raise ValueError("Missing required joint angles")

    form_feedback = {}
    alerts = []

    depth_feedback, depth_correct = analyze_squat_depth(joint_angles['knee_angle'])
    form_feedback['squat_depth'] = depth_feedback
    if should_alert('squat_depth', depth_correct):
        alerts.append(depth_feedback)

    back_feedback, back_correct = analyze_back_position(joint_angles['back_angle'])
    form_feedback['back_position'] = back_feedback
    if should_alert('back_position', back_correct):
        alerts.append(back_feedback)

    hip_feedback, hip_correct = analyze_hip_alignment(joint_angles['hip_angle'])
    form_feedback['hip_alignment'] = hip_feedback
    if should_alert('hip_alignment', hip_correct):
        alerts.append(hip_feedback)

    feedback_summary = f"""
    The system has analyzed the user's squat form and generated the following feedback:
    - Squat Depth: {form_feedback['squat_depth']}
    - Back Position: {form_feedback['back_position']}
    - Hip Alignment: {form_feedback['hip_alignment']}
    """

    if alerts:
        # Here you would trigger your text-to-speech function with the alerts
        print(f"Text-to-speech alerts: {', '.join(alerts)}")

    return form_feedback, feedback_summary