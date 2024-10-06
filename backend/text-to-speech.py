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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Audio configuration
CHANNELS = 1
RATE = 24000
CHUNK = 960

# WebSocket configuration
WS_URL = "wss://api.openai.com/v1/realtime"
MODEL = "gpt-4o-realtime-preview-2024-10-01"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class TextToSpeechAgent:
    def __init__(self):
        self.ws = None
        self.audio_buffer = bytearray()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.prompt_queue = asyncio.Queue()

    async def connect(self):
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
        self.ws = await websockets.connect(f"{WS_URL}?model={MODEL}", extra_headers=headers)
        logger.info("Connected to OpenAI Realtime API")

    async def send_event(self, event):
        await self.ws.send(json.dumps(event))

    async def receive_events(self):
        async for message in self.ws:
            event = json.loads(message)
            await self.handle_event(event)

    async def handle_event(self, event):
        event_type = event.get("type")
        
        if event_type == "error":
            logger.error(f"Error: {event['error']['message']}")
        elif event_type == "response.text.delta":
            logger.info(f"Text response: {event['delta']}")
        elif event_type == "response.audio.delta":
            audio_data = base64.b64decode(event["delta"])
            self.audio_buffer.extend(audio_data)
        elif event_type == "response.audio.done":
            audio_data = bytes(self.audio_buffer)
            self.audio_buffer.clear()
            await self.play_audio_async(audio_data)

    async def play_audio_async(self, audio_data):
        def play_audio():
            sd.play(np.frombuffer(audio_data, dtype=np.int16), RATE)
            sd.wait()
        
        await asyncio.get_event_loop().run_in_executor(self.executor, play_audio)

    async def send_text(self, text):
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}]
            }
        }
        await self.send_event(event)
        await self.send_event({"type": "response.create"})

    async def run(self):
        await self.connect()
        receive_task = asyncio.create_task(self.receive_events())
        
        await self.send_event({
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],
                "instructions": "You are a cheerful AI fitness coach. Your primary job is to encourage your client but also critque the form when needed. If you are prompted with something you should say, you should say something along those lines but also feel free to exapnd upon it and add your own twist. Keep Responses relatively brief",
            }
        })
        
        try:
            while True:
                text = await self.prompt_queue.get()
                if text.lower() == 'q':
                    break
                await self.send_text(text)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            receive_task.cancel()
            await self.ws.close()
            self.executor.shutdown()

async def handle_prompt(request):
    try:
        data = await request.json()
        prompt = data.get('prompt')
        if not prompt:
            return web.Response(status=400, text="Missing 'prompt' in JSON body")
        await agent.prompt_queue.put(prompt)
        return web.json_response({"status": "success", "message": "Prompt received"})
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

async def start_server(agent):
    app = web.Application()
    app.router.add_post("/prompt", handle_prompt)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    logger.info("HTTP server started on http://localhost:8080")

async def main():
    global agent
    agent = TextToSpeechAgent()
    server_task = asyncio.create_task(start_server(agent))
    await agent.run()
    await server_task

if __name__ == "__main__":
    asyncio.run(main())