import pyaudio
import queue
import threading
from vosk import Model, KaldiRecognizer
import json
import requests
import os
import wget
import zipfile
from openai import OpenAI
from dotenv import load_dotenv
import time
import numpy as np
from collections import deque

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

CATEGORIES = ["coherent_english", "fitness_form", "incoherent"]

# Constants for audio processing
RATE = 16000
CHUNK = 1024
MIN_PHRASE_LENGTH = 3
SILENCE_THRESHOLD = 500
MIN_CONFIDENCE_THRESHOLD = 0.7
SLIDING_WINDOW_SIZE = 5
END_OF_SPEECH_SILENCE_DURATION = 1.0  # seconds of silence to mark end of speech
PROCESSING_TIMEOUT = 5.0  # seconds to wait before processing anyway

def download_model():
    model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
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
    """Improved silence detection using RMS with safeguards against invalid values."""
    audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)
    if len(audio_array) == 0:
        return True
    squared = np.square(audio_array)
    mean_squared = np.mean(squared)
    if mean_squared <= 0:
        return True
    rms = np.sqrt(mean_squared)
    return rms < SILENCE_THRESHOLD

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
                q.put((data, time.time()))  # Add timestamp to each chunk
            except Exception as e:
                print(f"Error reading audio stream: {e}")
    except KeyboardInterrupt:
        print("Stopping audio stream.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def trigger_action(category, text):
    action_map = {
        "fitness_form": {
            "url": "http://localhost:5001/start_capture",
            "headers": {"Content-Type": "application/json"},
            "payload": lambda t: {"user_query": t}
        },
        "coherent_english": {
            "url": "http://localhost:8080/prompt",
            "headers": {"Content-Type": "application/json"},
            "payload": lambda t: {"prompt": t}
        }
    }

    action = action_map.get(category)
    if not action:
        print(f"No action defined for category: {category}")
        return

    try:
        payload = action["payload"](text)
        response = requests.post(action["url"], headers=action["headers"], json=payload)
        
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
                "1. 'How does my form look?' -> fitness_form\n"
        
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
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=5,
            temperature=0.0,
            n=1
        )
        response = completion.choices[0].message.content.strip().lower()
        
        return response if response in CATEGORIES else None
    except Exception as e:
        print(f"Error in categorization: {e}")
        return None

def process_speech(full_text):
    print(f"\nProcessing: {full_text}")
    category = categorize_input(full_text)
    if category in ["coherent_english", "fitness_form"]:
        print(f"Category '{category}' detected!")
        trigger_action(category, full_text)
    else:
        print("Input is incoherent or not relevant.")

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

    sliding_window = deque(maxlen=SLIDING_WINDOW_SIZE)
    silence_start = None
    last_process_time = time.time()
    accumulated_text = ""

    while True:
        if not q.empty():
            data, timestamp = q.get()
            if recognizer.AcceptWaveform(data):
                try:
                    result = json.loads(recognizer.Result())
                    if 'result' in result:
                        words = [word for word in result['result'] if word['conf'] >= MIN_CONFIDENCE_THRESHOLD]
                        if words:
                            text = ' '.join(word['word'] for word in words)
                            sliding_window.append(text)
                            accumulated_text += " " + text
                            silence_start = None  # Reset silence start time
                            last_process_time = timestamp  # Update last process time
                        else:
                            if silence_start is None:
                                silence_start = timestamp
                    else:
                        if silence_start is None:
                            silence_start = timestamp
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                except Exception as e:
                    print(f"Error processing recognition result: {e}")
            else:
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    print(f"Partial: {partial_text}", end="\r")
                elif silence_start is None:
                    silence_start = timestamp

            # Check for end of speech or timeout
            current_time = time.time()
            if silence_start and (current_time - silence_start >= END_OF_SPEECH_SILENCE_DURATION):
                if accumulated_text.strip():
                    process_speech(accumulated_text.strip())
                    accumulated_text = ""
                silence_start = None
                last_process_time = current_time
            elif current_time - last_process_time >= PROCESSING_TIMEOUT:
                if accumulated_text.strip():
                    process_speech(accumulated_text.strip())
                    accumulated_text = ""
                silence_start = None
                last_process_time = current_time

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