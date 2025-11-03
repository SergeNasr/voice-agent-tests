from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
from app.asr.factory import create_provider
from app.config import config

app = FastAPI(title="ASR Provider Testing MVP")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def read_root():
    """Serve the main HTML page."""
    return FileResponse("app/static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for audio streaming and transcription.

    Receives audio chunks from client and streams transcription results back.
    """
    await websocket.accept()

    # Create provider instance
    provider = create_provider()

    try:
        # Initialize provider
        await provider.initialize()

        # Send connection confirmation
        await websocket.send_json(
            {"type": "connected", "provider": provider.provider_type.value}
        )

        # Handle audio stream
        while True:
            # Receive audio chunk from client
            data = await websocket.receive()

            if "bytes" in data:
                # Binary audio data (WebM/Opus from browser)
                # Note: Some providers may require PCM16 format conversion
                audio_chunk = data["bytes"]

                # Get transcription from provider
                transcription = await provider.transcribe_stream(audio_chunk)

                # Send transcription back if available
                if transcription:
                    await websocket.send_json(
                        {"type": "transcription", "text": transcription}
                    )

            elif "text" in data:
                # Text message (for control commands)
                message = data["text"]
                if message == "close":
                    break

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        # Cleanup provider
        await provider.cleanup()
        try:
            await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
