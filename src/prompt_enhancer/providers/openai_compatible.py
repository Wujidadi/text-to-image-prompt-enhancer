from ..errors import ProviderError
from .base import Provider


class OpenAICompatibleProvider(Provider):
    """Chat Completions API as served by OpenAI, OpenRouter, DeepSeek,
    LM Studio, llama.cpp server, vLLM and most other hosts.
    `url` is the API base, e.g. https://api.openai.com/v1"""

    type_name = "openai"
    default_url = "https://api.openai.com/v1"

    def complete(self, system, prompt):
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}],
            **self.extra,
        }
        headers = {}
        key = self.api_key
        if key:
            headers["Authorization"] = f"Bearer {key}"
        reply = self._post_json(self.url + "/chat/completions", payload, headers)
        try:
            content = reply["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise ProviderError(f"{self.describe()}: unexpected response shape") from None
        if not isinstance(content, str):
            raise ProviderError(f"{self.describe()}: empty response")
        return content
