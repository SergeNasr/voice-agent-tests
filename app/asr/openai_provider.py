import json
import base64
import asyncio
from typing import Optional
import websockets
from app.asr.base import ASRProvider
from app.config import ProviderType, Config
from app.prompts import load_prompt


class OpenAIRealtimeProvider(ASRProvider):
    """
    OpenAI Realtime API provider using WebSocket streaming.

    The Realtime API uses WebSocket connections for bidirectional
    audio streaming and transcription.
    """

    def __init__(
        self, api_key: str, model: str = None, transcription_model: str = None
    ):
        super().__init__(api_key)
        self.model = model or Config.OPENAI_REALTIME_MODEL
        self.transcription_model = (
            transcription_model or Config.OPENAI_TRANSCRIPTION_MODEL
        )
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self._transcription_queue: asyncio.Queue[str] = asyncio.Queue()
        self._audio_buffer: bytearray = bytearray()
        self._session_id: Optional[str] = None
        self._listener_task: Optional[asyncio.Task] = None

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI_REALTIME

    async def initialize(self) -> None:
        """Initialize OpenAI Realtime API WebSocket connection."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1",
        }

        # Build WebSocket URL with model
        ws_url = f"wss://api.openai.com/v1/realtime?model={self.model}"

        self.websocket = await websockets.connect(ws_url, extra_headers=headers)

        # Start listener task for incoming messages
        self._listener_task = asyncio.create_task(self._listen_for_messages())

        # Load prompt from file
        instructions = load_prompt("openai_realtime")

        # Build session config
        session_config = {
            "modalities": ["text", "audio"],
            "instructions": instructions,
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
        }

        # Only add input_audio_transcription if not "automatic" (automatic is default)
        if self.transcription_model != "automatic":
            session_config["input_audio_transcription"] = {
                "model": self.transcription_model
            }

        # Initialize session
        await self._send_event({"type": "session.update", "session": session_config})

        self.initialized = True

    async def transcribe_stream(self, audio_chunk: bytes) -> str | None:
        """
        Send audio chunk to OpenAI Realtime API and return transcription if available.
        """
        if not self.initialized:
            await self.initialize()

        if not self.websocket:
            return None

        # Send audio input event
        audio_base64 = base64.b64encode(audio_chunk).decode("utf-8")
        await self._send_event(
            {"type": "input_audio_buffer.append", "audio": audio_base64}
        )

        # Request transcription
        await self._send_event({"type": "input_audio_buffer.commit"})

        # Check for transcription in queue (non-blocking)
        try:
            transcription = self._transcription_queue.get_nowait()
            return transcription
        except asyncio.QueueEmpty:
            return None

    async def _send_event(self, event: dict) -> None:
        """Send event to OpenAI Realtime API."""
        if self.websocket:
            await self.websocket.send(json.dumps(event))

    async def _listen_for_messages(self) -> None:
        """Listen for messages from OpenAI Realtime API."""
        if not self.websocket:
            return

        async for message in self.websocket:
            event = json.loads(message)
            await self._handle_event(event)

    async def _handle_event(self, event: dict) -> None:
        """Handle events from OpenAI Realtime API."""
        event_type = event.get("type")

        if event_type == "response.audio_transcript.delta":
            # Partial transcription
            delta = event.get("delta", "")
            if delta:
                await self._transcription_queue.put(delta)

        elif event_type == "response.audio_transcript.done":
            # Final transcription
            transcript = event.get("text", "")
            if transcript:
                await self._transcription_queue.put(transcript)

        elif event_type == "session.created":
            self._session_id = event.get("session", {}).get("id")

        elif event_type == "error":
            error = event.get("error", {})
            print(f"OpenAI Realtime API error: {error}")

    async def cleanup(self) -> None:
        """Clean up resources and close WebSocket connection."""
        # Cancel listener task
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None

        if self.websocket:
            await self._send_event(
                {"type": "session.update", "session": {"expires_at": 0}}
            )
            await self.websocket.close()

        self.websocket = None
        self._session_id = None
        self._audio_buffer.clear()
        self.initialized = False
