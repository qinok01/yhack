from flask import Flask, request, jsonify
import requests
from exercises.squat import analyze_squat
from exercises.pushup import analyze_pushup
from exercises.plank import analyze_plank
app = Flask(__name__)

# Configuration
SERVER_PORT = 5005
OUTPUT_URL = 'http://localhost:8080/prompt'
HEADERS = {'Content-Type': 'application/json'}

@app.route('/analyze/<exercise_type>', methods=['POST'])
def analyze_exercise(exercise_type):
    try:
        data = request.json
        joint_angles = data.get('joint_angles', {})
        user_query = data.get('user_query', '')

        if exercise_type == 'squat':
            form_feedback, feedback_summary = analyze_squat(joint_angles)
        elif exercise_type == 'pushup':
            form_feedback, feedback_summary = analyze_pushup(joint_angles)
        elif exercise_type == 'plank':
            form_feedback, feedback_summary = analyze_plank(joint_angles)
        else:
            return jsonify({"error": "Unsupported exercise type"}), 400

        prompt = f"""
        The user asked: "{user_query}"
        {feedback_summary}
        Instructions for response:
        1. If the user asks specifically about one feature, only provide the relevant feedback for that feature.
        2. If the user asks a general question about their form, provide feedback for all the features analyzed.
        3. If the user asks a question unrelated to form analysis, ignore the form feedback and answer accordingly.
        """

        output_data = {
            'prompt': prompt,
            'form_feedback': form_feedback,
            'feedback_summary': feedback_summary
        }

        response = requests.post(OUTPUT_URL, headers=HEADERS, json=output_data)

        if response.status_code == 200:
            return jsonify({"message": "Analysis completed and sent to output server", "data": output_data}), 200
        else:
            return jsonify({"error": f"Failed to send data to the output server. Status code: {response.status_code}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=SERVER_PORT, debug=True)