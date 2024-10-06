import asyncio
import websockets
import json
import sounddevice as sd
import numpy as np
import base64
import logging
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Audio configuration
CHANNELS = 1
RATE = 24000
CHUNK = 960

# WebSocket configuration
WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class TextToSpeechAgent:
    def __init__(self):
        self.ws = None
        self.audio_buffer = bytearray()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.prompt_queue = asyncio.Queue()
        self.current_exercise = "squats"
        logger.debug("TextToSpeechAgent initialized")

    async def connect(self):
        logger.debug("Attempting to connect to OpenAI Realtime API")
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        try:
            self.ws = await websockets.connect(WS_URL, extra_headers=headers)
            logger.info("Connected to OpenAI Realtime API")
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Realtime API: {e}")
            raise

    async def send_event(self, event):
        logger.debug(f"Sending event: {event}")
        await self.ws.send(json.dumps(event))
        logger.debug("Event sent successfully")

    async def receive_events(self):
        logger.debug("Starting to receive events")
        try:
            async for message in self.ws:
                logger.debug(f"Received raw message: {message}")
                event = json.loads(message)
                await self.handle_event(event)
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"WebSocket error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    async def handle_event(self, event):
        event_type = event.get("type")
        logger.debug(f"Handling event of type: {event_type}")

        if event_type == "error":
            logger.error(f"Error from OpenAI: {event['error']['message']}")
        elif event_type == "response.text.delta":
            delta = event.get("delta", "")
            logger.info(f"Assistant text delta: {delta}")
        elif event_type == "response.text.done":
            logger.info("Assistant text response complete")
        elif event_type == "response.audio.delta":
            logger.debug("Received audio data chunk")
            audio_data = base64.b64decode(event["delta"])
            self.audio_buffer.extend(audio_data)
        elif event_type == "response.audio.done":
            logger.info("Audio response complete, playing audio")
            audio_data = bytes(self.audio_buffer)
            self.audio_buffer.clear()
            await self.play_audio_async(audio_data)
        else:
            logger.debug(f"Unhandled event type: {event_type}")

    async def play_audio_async(self, audio_data):
        logger.debug(f"Playing audio of length: {len(audio_data)}")
        def play_audio():
            sd.play(np.frombuffer(audio_data, dtype=np.int16), RATE)
            sd.wait()
        await asyncio.get_running_loop().run_in_executor(self.executor, play_audio)
        logger.debug("Audio playback complete")

    async def send_text(self, text):
        logger.info(f"Sending text: {text}")
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}]
            }
        }
        await self.send_event(event)
        # Request the assistant's response
        await self.send_event({"type": "response.create"})
        logger.debug("Text sent and response requested")

    async def update_instructions(self):
        logger.info(f"Updating instructions for exercise: {self.current_exercise}")
        event = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": (
                    "You are a cheerful AI fitness coach. Your primary job is to encourage your client but "
                    "also critique the form when needed. If you are prompted with something you should say, "
                    "you should say something along those lines but also feel free to expand upon it and add "
                    "your own twist. Keep responses pretty brief. You are currently coaching for "
                    f"{self.current_exercise}."
                ),
                "voice": "alloy"
            }
        }
        await self.send_event(event)
        logger.info(f"Instructions updated for workout: {self.current_exercise}")

    async def run(self):
        logger.info("Starting TextToSpeechAgent")
        await self.connect()
        receive_task = asyncio.create_task(self.receive_events())
        
        logger.info("Sending initial instructions")
        await self.update_instructions()
        
        try:
            while True:
                logger.debug("Waiting for prompt from queue")
                prompt_data = await self.prompt_queue.get()
                logger.info(f"Received prompt data: {prompt_data}")
                new_exercise = prompt_data.get('exercise')
                prompt_text = prompt_data.get('text')

                if new_exercise and new_exercise != self.current_exercise:
                    logger.info(f"Switching exercise to: {new_exercise}")
                    self.current_exercise = new_exercise
                    await self.update_instructions()

                if prompt_text:
                    if prompt_text.lower() == 'q':
                        logger.info("Quit command received, breaking loop")
                        break
                    await self.send_text(prompt_text)
        except Exception as e:
            logger.error(f"An error occurred in run loop: {e}")
        finally:
            logger.info("Shutting down")
            receive_task.cancel()
            await self.ws.close()
            self.executor.shutdown()

async def handle_prompt(request):
    logger.debug("Received HTTP request")
    try:
        data = await request.json()
        logger.debug(f"Parsed JSON data: {data}")
        prompt = data.get('prompt')
        exercise = data.get('exercise')
        
        if not prompt and not exercise:
            logger.warning("Invalid request: missing prompt and exercise")
            return web.Response(status=400, text="At least one of 'prompt' or 'exercise' must be provided in JSON body")
        
        queue_item = {}
        if prompt:
            queue_item['text'] = prompt
        if exercise:
            queue_item['exercise'] = exercise
        
        logger.info(f"Queueing prompt: {queue_item}")
        await agent.prompt_queue.put(queue_item)
        return web.json_response({"status": "success", "message": "Request received"})
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON in request")
        return web.Response(status=400, text="Invalid JSON")

async def start_server(agent):
    logger.info("Starting HTTP server")
    app = web.Application()
    app.router.add_post("/prompt", handle_prompt)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logger.info("HTTP server started on http://localhost:8080")
    # Keep the server running
    await asyncio.Event().wait()

async def main():
    global agent
    logger.info("Initializing TextToSpeechAgent")
    agent = TextToSpeechAgent()
    logger.info("Starting agent run loop and HTTP server")
    await asyncio.gather(
        agent.run(),
        start_server(agent)
    )

if __name__ == "__main__":
    logger.info("Script started")
    asyncio.run(main())