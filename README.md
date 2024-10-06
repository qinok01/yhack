# Fivi - The Personal Trainer Breaking Down Barriers

## Project Overview
We developed an AI-powered personal trainer that provides real-time feedback on exercise form by using computer vision to analyze body movements. The project was built as a web app that runs on laptops equipped with webcams, allowing users to access personalized fitness coaching anywhere. This AI trainer helps correct users' form, provides actionable tips, and adapts workout difficulty based on user performance. Additionally, it includes an integrated voice-guidance system to make the interaction more intuitive and accessible.

## Features
1. **Real-time Form Feedback**: 
- Analyzes exercise form in real-time using computer vision
- Provides instant feedback via text and audio
- Helps correct posture and movement for optimal results and injury prevention
2. **Pose Detection**: 
- Utilizes MediaPipe's Pose Landmarks for accurate body posture and angle detection
- Tracks 33 key body points for comprehensive form assessment
3. **Speech Recognition & Guidance**:
- Features a hybrid audio interface for natural, hands-free interaction
- Employs Vosk API for real-time speech recognition and voice commands
- Delivers audio feedback and instructions for an immersive experience
4. **Cross-Platform Web App**:
- Built with React and Flask for smooth performance on laptops with webcams
- Ensures easy access to real-time feedback without specialized hardware

## Tech Stack

### Frontend
- **React**: Develops a responsive, modern user interface
- **Tailwind CSS**: Provides utility-first CSS framework for rapid UI development
- **HTML5 / CSS3**: Ensures a sleek, accessible design
- **JavaScript (ES6+)**: Enables dynamic client-side interactions

### Backend
- **Flask**: Handles communication between the computer vision model, the real-time audio system, and user data storage.
- **Python**: Used for backend development, interfacing with Flask and the deep learning models.

### Computer Vision
- **MediaPipe Pose Landmarks**: Used for pose detection and analysis of body movements during exercises. MediaPipe provides lightweight real-time tracking that is essential for posture correction.
- **OpenCV**: Processes video streams and enhances image analysis capabilities
  
### Audio Interface
- **Vosk API**: Used for real-time speech recognition as a partial solution when OpenAI’s real-time API documentation was not fully available. It processes the audio commands from users and provides speech feedback.
- **OpenAI Realtime API**: Provides human like responses and emotion to engage people in thier workouts.

##Installation

# Clone the repository
git clone https://github.com/yourusername/fivi-ai-trainer.git

# Navigate to the project directory
cd fivi-ai-trainer

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Return to the root directory
cd ..
