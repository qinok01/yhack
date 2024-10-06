from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration
SERVER_PORT = 5005  # This script will run on port 5005
OUTPUT_URL = 'http://localhost:8080/prompt'  # The server to send processed data to
HEADERS = {'Content-Type': 'application/json'}

# Functions to analyze angles
def analyze_squat_depth(knee_angle):
    if knee_angle < 120:
        return "depth is not deep enough"
    else:
        return "depth is at point"

def analyze_back_position(back_angle):
    if back_angle < 160:
        return "back is rounded"
    else:
        return "back is straight"

def analyze_hip_alignment(hip_angle):
    if -15 < hip_angle < 15:
        return "hips are aligned"
    else:
        return "hips are not aligned"

@app.route('/analyze', methods=['POST'])
def analyze_squat():
    try:
        # Get joint angles from the POST request
        data = request.json
        joint_angles = data.get('joint_angles', {})
        user_query = data.get('user_query', '')

        # Validate input
        required_angles = ['knee_angle', 'back_angle', 'hip_angle']
        if not all(angle in joint_angles for angle in required_angles):
            return jsonify({"error": "Missing required joint angles"}), 400

        # Generate feedback based on joint angles
        form_feedback = {
            'squat_depth': analyze_squat_depth(joint_angles['knee_angle']),
            'back_position': analyze_back_position(joint_angles['back_angle']),
            'hip_alignment': analyze_hip_alignment(joint_angles['hip_angle'])
        }

        # Summarize the feedback
        feedback_summary = f"""
        The system has analyzed the user's form and generated the following feedback:
        - Squat Depth: {form_feedback['squat_depth']}
        - Back Position: {form_feedback['back_position']}
        - Hip Alignment: {form_feedback['hip_alignment']}
        """

        # Prepare the prompt with conditional feedback logic
        prompt = f"""
        The user asked: "{user_query}"
        {feedback_summary}

        Instructions for response:
        1. If the user asks specifically about one feature (e.g., squat depth, back position, or hip alignment), only provide the relevant feedback for that feature.
        2. If the user asks a general question about their form, provide feedback for all the features analyzed.
        3. If the user asks a question unrelated to form analysis, ignore the form feedback and answer accordingly.
        """

        # Prepare the output JSON
        output_data = {
            'prompt': prompt,
            'form_feedback': form_feedback,
            'feedback_summary': feedback_summary
        }

        # Send the output to the specified endpoint
        response = requests.post(OUTPUT_URL, headers=HEADERS, json=output_data)

        # Handle the response
        if response.status_code == 200:
            return jsonify({"message": "Analysis completed and sent to output server", "data": output_data}), 200
        else:
            return jsonify({"error": f"Failed to send data to the output server. Status code: {response.status_code}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=SERVER_PORT, debug=True)