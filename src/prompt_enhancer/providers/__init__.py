from ..errors import ConfigError
from .anthropic import AnthropicProvider
from .base import Provider
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider
from .wavespeed import WaveSpeedProvider

PROVIDER_TYPES = {
    OllamaProvider.type_name: OllamaProvider,
    OpenAICompatibleProvider.type_name: OpenAICompatibleProvider,
    WaveSpeedProvider.type_name: WaveSpeedProvider,
    AnthropicProvider.type_name: AnthropicProvider,
}


def create_provider(settings):
    kind = settings.get("type")
    cls = PROVIDER_TYPES.get(kind)
    if cls is None:
        raise ConfigError(f'unknown provider type "{kind}" '
                          f"(known: {', '.join(sorted(PROVIDER_TYPES))})")
    return cls(settings)


__all__ = ["Provider", "PROVIDER_TYPES", "create_provider",
           "OllamaProvider", "OpenAICompatibleProvider", "WaveSpeedProvider",
           "AnthropicProvider"]
