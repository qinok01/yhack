import pyaudio
import queue
import threading
from vosk import Model, KaldiRecognizer
import json
import requests
import re
import os
import wget
import zipfile
from openai import OpenAI
from dotenv import load_dotenv
import time
import numpy as np

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

CATEGORIES = ["coherent_english", "fitness_form", "incoherent"]

# Constants for audio processing
RATE = 16000
CHUNK = 1024
MIN_PHRASE_LENGTH = 3  # Minimum number of words to process
SILENCE_THRESHOLD = 100  # Adjust this value based on your microphone and environment
MIN_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence score for recognized words

def download_model():
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_path = "model"
    zip_path = "model.zip"

    if not os.path.exists(model_path):
        print("Downloading the Vosk model...")
        wget.download(model_url, zip_path)
        print("\nExtracting the model...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        extracted_folders = [name for name in os.listdir('.') if name.startswith("vosk-model")]
        if extracted_folders:
            os.rename(extracted_folders[0], model_path)
        else:
            raise Exception("Vosk model folder not found after extraction.")
        os.remove(zip_path)
        print("Model downloaded and extracted successfully.")
    else:
        print("Vosk model already exists.")

def is_silence(audio_chunk):
    """Check if the audio chunk is silence."""
    return np.max(np.abs(np.frombuffer(audio_chunk, dtype=np.int16))) < SILENCE_THRESHOLD

def audio_stream(q):
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"Error opening audio stream: {e}")
        return

    print("Listening for phrases...")
    try:
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                if not is_silence(data):
                    q.put(data)
            except Exception as e:
                print(f"Error reading audio stream: {e}")
    except KeyboardInterrupt:
        print("Stopping audio stream.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def trigger_action(category, text, joint_angles):
    action_map = {
        "fitness_form": {
            "url": "http://localhost:5005/analyze",
            "headers": {"Content-Type": "application/json"},
            "payload": lambda t, j: {"category": "fitness_form", "user_query": t, "joint_angles": j}
        },
        "coherent_english": {
            "url": "http://localhost:8080/prompt",
            "headers": {"Content-Type": "application/json"},
            "payload": lambda t, _: {"prompt": t}
        }
    }

    action = action_map.get(category)
    if not action:
        print(f"No action defined for category: {category}")
        return

    try:
        payload = action["payload"](text, joint_angles)
        response = requests.post(action["url"], headers=action["headers"], json=payload, timeout=5)
        if response.status_code == 200:
            print(f"Request sent successfully for category: '{category}'")
            print(f"Response: {response.json()}")
        else:
            print(f"Failed to send request for category '{category}'. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request for category '{category}': {e}")

def categorize_input(text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that categorizes user input. "
                "Determine if the input is coherent English, asking about fitness form, or incoherent. "
                "Respond with either 'coherent_english', 'fitness_form', or 'incoherent'.\n\n"
                "Examples:\n"
                "1. 'How does my squat look?' -> fitness_form\n"
                "2. 'The sky is blue.' -> coherent_english\n"
                "3. 'Can you check my deadlift form?' -> fitness_form\n"
                "4. 'I like to eat pizza.' -> coherent_english\n"
                "5. 'Is my back straight enough during this exercise?' -> fitness_form\n"
                "6. 'The quick brown fox jumps over the lazy dog.' -> coherent_english\n"
                "7. 'What's the proper technique for a bench press?' -> fitness_form\n"
                "8. 'Hello, how are you today?' -> coherent_english\n"
                "9. 'Blah blah goop goop' -> incoherent\n"
                "10. 'Colorless green ideas sleep furiously.' -> incoherent"
            )
        },
        {
            "role": "user",
            "content": (
                f"Categorize this input: \"{text}\"\n"
                f"Response (coherent_english/fitness_form/incoherent):"
            )
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=5,
            temperature=0.0,
            n=1
        )
        response = completion.choices[0].message.content.strip().lower()
        
        if response in CATEGORIES:
            return response
        else:
            return None
    except Exception as e:
        print(f"Error in categorization: {e}")
        return None

def keyword_detector(q, model_path="model"):
    if not os.path.exists(model_path):
        download_model()

    try:
        model = Model(model_path)
    except Exception as e:
        print(f"Error loading Vosk model: {e}")
        return

    recognizer = KaldiRecognizer(model, RATE)
    recognizer.SetWords(True)

    def get_current_joint_angles():
        return {
            "knee_angle": 130,
            "back_angle": 170,
            "hip_angle": 10
        }

    buffer = ""
    while True:
        if not q.empty():
            data = q.get()
            if recognizer.AcceptWaveform(data):
                try:
                    result = json.loads(recognizer.Result())
                    if 'result' in result:
                        words = [word for word in result['result'] if word['conf'] >= MIN_CONFIDENCE_THRESHOLD]
                        if words:
                            text = ' '.join(word['word'] for word in words)
                            buffer += text + " "
                            
                            # Check if we have a complete phrase
                            if len(buffer.split()) >= MIN_PHRASE_LENGTH:
                                print(f"\nRecognized: {buffer.strip()}")
                                category = categorize_input(buffer.strip())
                                if category in ["coherent_english", "fitness_form"]:
                                    print(f"Category '{category}' detected!")
                                    joint_angles = get_current_joint_angles()
                                    trigger_action(category, buffer.strip(), joint_angles)
                                else:
                                    print("Input is incoherent or not relevant.")
                                buffer = ""  # Reset buffer after processing
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                except Exception as e:
                    print(f"Error processing recognition result: {e}")
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    print(f"Partial: {partial_text}", end="\r")
        else:
            time.sleep(0.1)  # Prevent busy waiting

def main():
    q = queue.Queue()

    audio_thread = threading.Thread(target=audio_stream, args=(q,), daemon=True)
    detector_thread = threading.Thread(target=keyword_detector, args=(q,), daemon=True)

    audio_thread.start()
    detector_thread.start()

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()