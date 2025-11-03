# ASR Provider Testing MVP

A minimal viable product for testing and comparing real-time Automatic Speech Recognition (ASR) providers.

## Supported Providers

- **OpenAI Realtime** (GPT-4o Realtime API)
- DeepGram (coming soon)
- ElevenLabs (coming soon)
- Cartesia (coming soon)

## Features

- Real-time audio transcription via WebSocket
- Easy provider swapping via `.env` configuration
- Clean, modular architecture with provider abstraction
- Simple web interface for testing

## Setup

1. **Install dependencies**:
   ```bash
   just install
   # or
   uv sync
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Set provider** (in `.env`):
   ```
   ASR_PROVIDER=openai_realtime
   ```

4. **Run the server**:
   ```bash
   just dev
   # or
   uv run uvicorn app.main:app --reload
   ```

5. **Open browser**:
   Navigate to `http://localhost:8000`

## Usage

1. Click "Start Recording" to begin
2. Speak into your microphone
3. Transcription appears in real-time
4. Click "Stop Recording" when done

## Notes

- **Audio Format**: The frontend sends WebM/Opus audio. Some providers may require PCM16 format conversion, which will be handled automatically in future updates.
- **Provider Selection**: Change `ASR_PROVIDER` in `.env` to switch providers (requires server restart).

## Project Structure

```
voice-agent-tests/
├── app/
│   ├── main.py              # FastAPI app with WebSocket endpoint
│   ├── config.py            # Configuration & provider enum
│   ├── asr/
│   │   ├── base.py          # Abstract ASR provider base class
│   │   ├── factory.py       # Provider factory
│   │   └── openai_provider.py  # OpenAI Realtime implementation
│   └── static/              # Frontend files
├── pyproject.toml           # Dependencies
├── justfile                 # Common commands
└── .env                     # API keys (not in git)
```

## Adding New Providers

1. Create a new provider class in `app/asr/` that inherits from `ASRProvider`
2. Implement `initialize()`, `transcribe_stream()`, and `cleanup()` methods
3. Add provider type to `ProviderType` enum in `app/config.py`
4. Add provider creation logic to `app/asr/factory.py`

## Justfile Commands

- `just install` - Install dependencies
- `just dev` - Run development server with auto-reload
- `just run` - Run production server
- `just fmt` - Format code
- `just lint` - Lint code

