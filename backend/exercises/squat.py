import numpy as np
from time import time

# Configuration
STATE_THRESH = {
    's1': 160,  # Standing straight
    's2': (110, 150),  # Transition
    's3': (70, 100)  # Squat position
}
FEEDBACK_THRESH = {
    'bend_forward': 70,
    'bend_backward': 100,
    'lower_hips': (100, 140),
    'knee_over_toes': 80,
    'deep_squat': 60
}
INACTIVE_THRESH = 15  # Seconds

# Global variables
correct_count = 0
incorrect_count = 0
state_sequence = []
last_active_time = time()
last_feedback_time = 0
FEEDBACK_COOLDOWN = 3  # Seconds

def get_state(hip_angle):
    if hip_angle >= STATE_THRESH['s1']:
        return 's1'
    elif STATE_THRESH['s2'][0] <= hip_angle < STATE_THRESH['s2'][1]:
        return 's2'
    elif STATE_THRESH['s3'][0] <= hip_angle < STATE_THRESH['s3'][1]:
        return 's3'
    return 'unknown'

def get_feedback(shoulder_angle, hip_angle, knee_angle, back_angle, current_state, prev_state):
    feedback = []
    
    if back_angle < FEEDBACK_THRESH['bend_forward']:
        feedback.append("Bend forward slightly")
    elif back_angle > FEEDBACK_THRESH['bend_backward']:
        feedback.append("Lean back slightly")
    
    if current_state == 's2' and prev_state == 's1':
        if FEEDBACK_THRESH['lower_hips'][0] <= hip_angle <= FEEDBACK_THRESH['lower_hips'][1]:
            feedback.append("Lower your hips more")
    
    if knee_angle > FEEDBACK_THRESH['knee_over_toes']:
        feedback.append("Keep knees behind toes")
    
    if current_state == 's3' and hip_angle < FEEDBACK_THRESH['deep_squat']:
        feedback.append("Squat is too deep")
    
    return ". ".join(feedback)

def analyze_squat(joint_angles):
    global correct_count, incorrect_count, state_sequence, last_active_time, last_feedback_time
    
    left_hip_angle = joint_angles['left_hip_angle']
    right_hip_angle = joint_angles['right_hip_angle']
    left_knee_angle = joint_angles['left_knee_angle']
    right_knee_angle = joint_angles['right_knee_angle']
    back_angle = joint_angles['back_angle']

    # Use average of left and right for symmetry
    hip_angle = (left_hip_angle + right_hip_angle) / 2
    knee_angle = (left_knee_angle + right_knee_angle) / 2

    # Get current state
    current_state = get_state(hip_angle)
    
    # Update state sequence
    if current_state != 'unknown':
        if not state_sequence or current_state != state_sequence[-1]:
            state_sequence.append(current_state)
        if len(state_sequence) > 3:
            state_sequence.pop(0)

    # Count reps and reset state sequence
    if current_state == 's1' and len(state_sequence) == 3:
        if state_sequence == ['s2', 's3', 's2']:
            correct_count += 1
        else:
            incorrect_count += 1
        state_sequence = []

    # Get feedback
    prev_state = state_sequence[-2] if len(state_sequence) >= 2 else 's1'
    feedback = get_feedback(0, hip_angle, knee_angle, back_angle, current_state, prev_state)

    # Check for inactivity
    current_time = time()
    if current_time - last_active_time > INACTIVE_THRESH:
        correct_count = 0
        incorrect_count = 0
        state_sequence = []
        feedback = "Inactive for too long. Counters reset."
    last_active_time = current_time

    # Prepare debug info
    debug_info = f"State: {current_state}, Hip: {hip_angle:.1f}°, Knee: {knee_angle:.1f}°, Back: {back_angle:.1f}°"

    # Calculate percentage for progress bar
    per = np.interp(hip_angle, (STATE_THRESH['s3'][0], STATE_THRESH['s1']), (100, 0))
    bar = np.interp(hip_angle, (STATE_THRESH['s3'][0], STATE_THRESH['s1']), (50, 380))

    # Throttle feedback
    if current_time - last_feedback_time > FEEDBACK_COOLDOWN and feedback:
        last_feedback_time = current_time
        return f"Rep count: {correct_count} (Incorrect: {incorrect_count}). {feedback}", debug_info, per, bar
    else:
        return "", debug_info, per, bar

print("Squat analysis function initialized. Ready to analyze squat form.")