from abc import ABC, abstractmethod
from app.config import ProviderType


class ASRProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider connection and authentication."""
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_chunk: bytes) -> str | None:
        """
        Process an audio chunk and return transcription if available.

        Args:
            audio_chunk: Raw audio bytes

        Returns:
            Transcription text if available, None otherwise
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Close connections and clean up resources."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type enum."""
        pass
