from ..errors import ProviderError
from .base import Provider

API_VERSION = "2023-06-01"


class AnthropicProvider(Provider):
    """Anthropic Messages API (raw HTTP, no SDK dependency)"""

    type_name = "anthropic"
    default_url = "https://api.anthropic.com"
    default_model = "claude-sonnet-5"

    def complete(self, system, prompt):
        payload = {
            "model": self.model,
            "max_tokens": self.settings.get("max_tokens", 4096),
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
            **self.extra,
        }
        headers = {"anthropic-version": API_VERSION}
        key = self.api_key
        if key:
            headers["x-api-key"] = key
        reply = self._post_json(self.url + "/v1/messages", payload, headers)
        if reply.get("stop_reason") == "refusal":
            details = reply.get("stop_details") or {}
            raise ProviderError(f"{self.describe()}: request refused "
                                f"({details.get('category') or 'unspecified'})")
        blocks = reply.get("content")
        if not isinstance(blocks, list):
            raise ProviderError(f"{self.describe()}: unexpected response shape")
        return "".join(b.get("text", "") for b in blocks
                       if isinstance(b, dict) and b.get("type") == "text")
