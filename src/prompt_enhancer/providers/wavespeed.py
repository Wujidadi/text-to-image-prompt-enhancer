from .openai_compatible import OpenAICompatibleProvider


class WaveSpeedProvider(OpenAICompatibleProvider):
    """WaveSpeed LLM API: Chat Completions served at llm.wavespeed.ai,
    with provider-prefixed model ids such as deepseek/deepseek-v4-flash.
    The key is the same WaveSpeed key used for image generation"""

    type_name = "wavespeed"
    default_url = "https://llm.wavespeed.ai/v1"
    default_model = "deepseek/deepseek-v4-flash"
    default_api_key_env = "WAVESPEED_API_KEY"
