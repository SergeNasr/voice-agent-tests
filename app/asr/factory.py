from app.config import Config, ProviderType
from app.asr.base import ASRProvider
from app.asr.openai_provider import OpenAIRealtimeProvider


def _create_openai_provider() -> ASRProvider:
    """Factory function for OpenAI Realtime provider."""
    api_key = Config.get_api_key(ProviderType.OPENAI_REALTIME)
    return OpenAIRealtimeProvider(
        api_key,
        model=Config.OPENAI_REALTIME_MODEL,
        transcription_model=Config.OPENAI_TRANSCRIPTION_MODEL,
    )


# Mapping of provider types to their factory functions
_PROVIDER_FACTORIES = {
    ProviderType.OPENAI_REALTIME: _create_openai_provider,
    # ProviderType.DEEPGRAM: _create_deepgram_provider,  # Add when implemented
    # ProviderType.ELEVENLABS: _create_elevenlabs_provider,  # Add when implemented
    # ProviderType.CARTESIA: _create_cartesia_provider,  # Add when implemented
}


def create_provider() -> ASRProvider:
    """Create ASR provider instance based on configuration."""
    provider_type = Config.ASR_PROVIDER
    factory = _PROVIDER_FACTORIES.get(provider_type)

    if factory is None:
        raise ValueError(f"Provider {provider_type.value} not implemented")

    return factory()
