from time import time
import numpy as np

# Global variables
pushup_correct_count = 0
pushup_incorrect_count = 0
pushup_state = None
pushup_prev_state = None
pushup_last_active_time = time()
pushup_state_sequence = []

last_feedback_time = 0
FEEDBACK_COOLDOWN = 2  # seconds

def get_pushup_state(elbow_angle):
    if elbow_angle > 160:
        return 'up'
    elif elbow_angle < 90:
        return 'down'
    else:
        return 'middle'

def analyze_pushup(joint_angles):
    global pushup_correct_count, pushup_incorrect_count, pushup_state, pushup_prev_state, pushup_last_active_time, pushup_state_sequence, last_feedback_time

    # Extract angles
    left_elbow_angle = joint_angles.get('left_elbow_angle', 0)
    right_elbow_angle = joint_angles.get('right_elbow_angle', 0)
    elbow_angle = (left_elbow_angle + right_elbow_angle) / 2

    left_hip_angle_pushup = joint_angles.get('left_hip_angle_pushup', 0)
    right_hip_angle_pushup = joint_angles.get('right_hip_angle_pushup', 0)
    hip_angle = (left_hip_angle_pushup + right_hip_angle_pushup) / 2

    left_hand_to_shoulder_angle = joint_angles.get('left_hand_to_shoulder_angle', 0)
    right_hand_to_shoulder_angle = joint_angles.get('right_hand_to_shoulder_angle', 0)
    hand_to_shoulder_angle = (left_hand_to_shoulder_angle + right_hand_to_shoulder_angle) / 2

    # Determine current state
    current_state = get_pushup_state(elbow_angle)

    # Update state sequence
    if pushup_state != current_state:
        pushup_prev_state = pushup_state
        pushup_state = current_state
        pushup_state_sequence.append(current_state)
        if len(pushup_state_sequence) > 3:
            pushup_state_sequence.pop(0)

    # Count reps
    feedback = []
    if pushup_prev_state == 'down' and pushup_state == 'up':
        # Completed a pushup
        if 165 <= hip_angle <= 195:
            pushup_correct_count += 1
            feedback.append("Good pushup!")
        else:
            pushup_incorrect_count += 1
            feedback.append("Keep body straight during pushup.")

    # Provide feedback based on current state
    if current_state == 'down':
        if elbow_angle > 140:
            feedback.append("Lower chest more")
    elif current_state == 'up':
        if elbow_angle < 160:
            feedback.append("Extend arms fully")

    # Form feedback (applicable in any state)
    if hip_angle < 165:
        feedback.append("Raise hips")
    elif hip_angle > 195:
        feedback.append("Lower hips slightly")

    if hand_to_shoulder_angle < 50:
        feedback.append("Widen hand placement")
    elif hand_to_shoulder_angle > 130:
        feedback.append("Narrow hand placement")

    # Progress calculation based on elbow angle
    per = np.interp(elbow_angle, (90, 160), (100, 0))
    bar = np.interp(elbow_angle, (90, 160), (50, 380))

    # Debug information
    debug_info = f"Reps: {pushup_correct_count}, State: {current_state}, Elbow: {elbow_angle:.1f}°, Hip: {hip_angle:.1f}°, Hand-Shoulder: {hand_to_shoulder_angle:.1f}°"

    # Update last active time
    pushup_last_active_time = time()
    print(f"Hip Angle: {hip_angle}")

    # Feedback cooldown
    current_time = time()
    if current_time - last_feedback_time >= FEEDBACK_COOLDOWN:
        last_feedback_time = current_time
        if feedback:
            feedback_message = ". ".join(feedback)
            print(f"Exercise Feedback: {feedback_message}")
        else:
            feedback_message = "Maintain current form"
    else:
        feedback_message = ""  # No feedback during cooldown

    return feedback_message, debug_info, per, bar
