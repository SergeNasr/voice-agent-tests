import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class ProviderType(str, Enum):
    OPENAI_REALTIME = "openai_realtime"
    DEEPGRAM = "deepgram"
    ELEVENLABS = "elevenlabs"
    CARTESIA = "cartesia"


class Config:
    ASR_PROVIDER: ProviderType = ProviderType(
        os.getenv("ASR_PROVIDER", ProviderType.OPENAI_REALTIME.value)
    )

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_REALTIME_MODEL: str = os.getenv(
        "OPENAI_REALTIME_MODEL", "gpt-4o-realtime-preview-2024-12-17"
    )
    OPENAI_TRANSCRIPTION_MODEL: str = os.getenv(
        "OPENAI_TRANSCRIPTION_MODEL", "automatic"
    )
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    CARTESIA_API_KEY: str = os.getenv("CARTESIA_API_KEY", "")

    @classmethod
    def get_api_key(cls, provider: ProviderType) -> str:
        key_map = {
            ProviderType.OPENAI_REALTIME: cls.OPENAI_API_KEY,
            ProviderType.DEEPGRAM: cls.DEEPGRAM_API_KEY,
            ProviderType.ELEVENLABS: cls.ELEVENLABS_API_KEY,
            ProviderType.CARTESIA: cls.CARTESIA_API_KEY,
        }
        return key_map.get(provider, "")


config = Config()
