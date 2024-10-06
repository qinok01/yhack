# AI-Powered Personal Trainer

## Project Overview
We developed an AI-powered personal trainer that provides real-time feedback on exercise form by using computer vision to analyze body movements. The project was built as a web app that runs on laptops equipped with webcams, allowing users to access personalized fitness coaching anywhere. This AI trainer helps correct users' form, provides actionable tips, and adapts workout difficulty based on user performance. Additionally, it includes an integrated voice-guidance system to make the interaction more intuitive and accessible.

## Inspiration
Our team, passionate about fitness, saw an opportunity to build a tool that leverages state-of-the-art technologies like computer vision and text-to-speech APIs to make personalized training more accessible and effective for everyone. We aimed to revolutionize fitness training by combining our technical skills with our shared goal of building a product that could empower individuals to maintain their fitness from any location.

## Features
1. **Real-time Form Feedback**: The AI personal trainer uses computer vision to analyze exercise form in real-time, offering feedback in both text and audio formats.
2. **Pose Detection**: Using MediaPipe's Pose Landmarks, the AI accurately detects body posture and angles to assess exercise form.
3. **Speech Recognition & Guidance**: We implemented a hybrid audio interface, initially aiming to use OpenAI's real-time API for seamless text-to-speech and speech-to-text integration. Due to time constraints, we instead used Vosk API for real-time speech recognition.
4. **Progress Tracking**: The AI trainer monitors the user's performance over time, providing personalized workout recommendations and adjusting difficulty based on improvement.
5. **Cross-Platform Web App**: Built with React and Flask, the system runs smoothly on laptops with webcams, ensuring easy access to real-time feedback without requiring specialized hardware.

## Tech Stack

### Frontend
- **React**: The user interface was developed with React for a responsive, modern design.
- **TensorFlow.js**: Integrated into the frontend to run machine learning models in the browser, enabling real-time feedback without needing high-end hardware.

### Backend
- **Flask**: Handles communication between the computer vision model, the real-time audio system, and user data storage.
- **Python**: Used for backend development, interfacing with Flask and the deep learning models.

### Computer Vision
- **MediaPipe Pose Landmarks**: Used for pose detection and analysis of body movements during exercises. MediaPipe provides lightweight real-time tracking that is essential for posture correction.
  
### Audio Interface
- **Vosk API**: Used for real-time speech recognition as a backup solution when OpenAI’s real-time API documentation was not fully available. It processes the audio commands from users and provides speech feedback.
- **OpenAI Text-to-Speech API**: Planned future integration to replace Vosk and streamline audio interaction with lower latency and smoother operation.

## Challenges
