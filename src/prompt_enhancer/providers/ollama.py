from ..errors import ProviderError
from .base import Provider


class OllamaProvider(Provider):
    """ollama /api/chat. Thinking is disabled by default: 4B-scale thinking
    was measured slower and no better for prompt rewriting"""

    type_name = "ollama"
    default_url = "http://localhost:11434"
    default_model = "qwen3.5:4b"

    def complete(self, system, prompt):
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": prompt}],
            "stream": False,
            "think": self.settings.get("think", False),
            **self.extra,
        }
        reply = self._post_json(self.url + "/api/chat", payload)
        message = reply.get("message")
        if not isinstance(message, dict) or "content" not in message:
            raise ProviderError(f"{self.describe()}: unexpected response shape")
        return message["content"]
