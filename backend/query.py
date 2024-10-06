from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration
SERVER_PORT = 5005
OUTPUT_URL = 'http://localhost:8080/prompt'
HEADERS = {'Content-Type': 'application/json'}

def analyze_squat(angles):
    issues = []
    
    # Calculate average angles for bilateral joints
    knee_angle = (angles['left_knee_angle'] + angles['right_knee_angle']) / 2
    hip_angle = (angles['left_hip_angle'] + angles['right_hip_angle']) / 2
    ankle_angle = (angles['left_ankle_angle'] + angles['right_ankle_angle']) / 2
    shoulder_angle = (angles['left_shoulder_angle'] + angles['right_shoulder_angle']) / 2
    back_angle = angles['back_angle']
    
    # Analyze squat depth
    if knee_angle < 90:
        depth = "too deep"
    elif 90 <= knee_angle < 110:
        depth = "proper depth"
    elif 110 <= knee_angle < 130:
        depth = "borderline depth"
    else:
        depth = "not deep enough"
    
    if depth != "proper depth":
        issues.append(f"Squat {depth}")
    
    # Analyze back position
    if back_angle < 150:
        back_status = "significantly rounded"
        issues.append("Back is significantly rounded")
    elif 150 <= back_angle < 170:
        back_status = "slightly rounded"
        issues.append("Back is slightly rounded")
    else:
        back_status = "straight"
    
    # Analyze hip alignment
    if 80 <= hip_angle <= 100:
        hip_status = "well aligned"
    elif 70 <= hip_angle < 80 or 100 < hip_angle <= 110:
        hip_status = "slightly misaligned"
        issues.append("Hips are slightly misaligned")
    else:
        hip_status = "significantly misaligned"
        issues.append("Hips are significantly misaligned")
    
    # Analyze ankle mobility
    if ankle_angle < 30:
        ankle_status = "limited mobility"
        issues.append("Limited ankle mobility")
    elif 30 <= ankle_angle < 40:
        ankle_status = "moderate mobility"
    else:
        ankle_status = "good mobility"
    
    # Analyze shoulder alignment
    if 85 <= shoulder_angle <= 95:
        shoulder_status = "well aligned"
    elif 80 <= shoulder_angle < 85 or 95 < shoulder_angle <= 100:
        shoulder_status = "slightly misaligned"
        issues.append("Shoulders are slightly misaligned")
    else:
        shoulder_status = "significantly misaligned"
        issues.append("Shoulders are significantly misaligned")
    
    # Determine overall squat quality
    if not issues:
        quality = "Excellent"
    elif len(issues) == 1:
        quality = "Good"
    elif len(issues) == 2:
        quality = "Fair"
    else:
        quality = "Poor"
    
    # Prepare the analysis report
    report = f"""
Squat Analysis:
- Depth: {depth}
- Back position: {back_status}
- Hip alignment: {hip_status}
- Ankle mobility: {ankle_status}
- Shoulder alignment: {shoulder_status}
- Overall quality: {quality}

Issues to address:
{"- " + "- ".join(issues) if issues else "None"}

Recommendations:
{"- Focus on maintaining proper form and addressing the identified issues." if issues else "- Keep up the good work and maintain consistent form."}
"""
    
    return report.strip()

@app.route('/analyze', methods=['POST'])
def analyze_squat_route():
    try:
        data = request.json
        joint_angles = data.get('joint_angles', {})
        user_query = data.get('user_query', '')

        required_angles = [
            'left_shoulder_angle', 'right_shoulder_angle',
            'left_hip_angle', 'right_hip_angle',
            'left_knee_angle', 'right_knee_angle',
            'left_ankle_angle', 'right_ankle_angle',
            'back_angle'
        ]
        if not all(angle in joint_angles for angle in required_angles):
            return jsonify({"error": "Missing required joint angles"}), 400

        feedback = analyze_squat(joint_angles)

        prompt = f"""
        The user asked: "{user_query}"

        {feedback}

        Instructions for response:
        1. If the user asks specifically about one feature (e.g., squat depth, back position, hip alignment, ankle mobility, or shoulder alignment), focus on the relevant part of the feedback.
        2. If the user asks a general question about their form, provide a summary of all the features analyzed.
        3. If the user asks a question unrelated to form analysis, ignore the form feedback and answer accordingly.
        4. Include information about the correct positioning for squat analysis: The user should face the camera sideways (profile view) for the most accurate analysis of squat depth, back angle, and hip alignment. This allows for better visibility of the knee bend, back curvature, and hip position throughout the movement.
        """

        output_data = {
            'prompt': prompt,
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