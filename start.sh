#!/bin/bash
# Run this script by typing "bash start.sh" in the terminal

# Clone the repository
git clone https://github.com/yourusername/fivi-ai-trainer.git
cd fivi-ai-trainer

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start frontend in the background
npm run dev &

# Start backend servers
cd ../backend
source venv/bin/activate
python main.py &
python query.py &
python find_keyword.py &
python realtime.py &

# Print instructions for opening the web app
echo "All services have been started."
echo "Please open your browser and navigate to http://localhost:5173 to access the web app."

# Keep the script running
wait