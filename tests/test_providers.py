import pytest

from prompt_enhancer import ConfigError, ProviderError
from prompt_enhancer.providers import create_provider


def capture(monkeypatch, provider, reply):
    calls = []

    def fake_post(url, payload, headers=None):
        calls.append((url, payload, headers or {}))
        return reply

    monkeypatch.setattr(provider, "_post_json", fake_post)
    return calls


def test_ollama(monkeypatch):
    p = create_provider({"type": "ollama"})
    calls = capture(monkeypatch, p, {"message": {"content": "out"}})
    assert p.complete("S", "U") == "out"
    url, payload, _ = calls[0]
    assert url == "http://localhost:11434/api/chat"
    assert payload["think"] is False and payload["stream"] is False
    assert payload["messages"][0] == {"role": "system", "content": "S"}


def test_openai(monkeypatch):
    p = create_provider({"type": "openai", "model": "m", "api_key": "k",
                         "url": "https://h/v1/", "extra": {"temperature": 0.2}})
    calls = capture(monkeypatch, p, {"choices": [{"message": {"content": "out"}}]})
    assert p.complete("S", "U") == "out"
    url, payload, headers = calls[0]
    assert url == "https://h/v1/chat/completions"
    assert headers["Authorization"] == "Bearer k"
    assert payload["temperature"] == 0.2


def test_wavespeed(monkeypatch):
    monkeypatch.setenv("WAVESPEED_API_KEY", "ws")
    p = create_provider({"type": "wavespeed"})
    calls = capture(monkeypatch, p, {"choices": [{"message": {"content": "out"}}]})
    assert p.complete("S", "U") == "out"
    url, payload, headers = calls[0]
    assert url == "https://llm.wavespeed.ai/v1/chat/completions"
    assert headers["Authorization"] == "Bearer ws"
    assert payload["model"] == "deepseek/deepseek-v4-flash"


def test_wavespeed_key_env_override(monkeypatch):
    monkeypatch.delenv("WAVESPEED_API_KEY", raising=False)
    monkeypatch.setenv("OTHER_KEY", "o")
    assert create_provider({"type": "wavespeed", "api_key_env": "OTHER_KEY"}).api_key == "o"
    with pytest.raises(ConfigError, match="WAVESPEED_API_KEY"):
        create_provider({"type": "wavespeed"}).api_key


def test_anthropic(monkeypatch):
    p = create_provider({"type": "anthropic", "api_key": "k"})
    calls = capture(monkeypatch, p, {"stop_reason": "end_turn",
                                     "content": [{"type": "text", "text": "out"}]})
    assert p.complete("S", "U") == "out"
    url, payload, headers = calls[0]
    assert url == "https://api.anthropic.com/v1/messages"
    assert headers["x-api-key"] == "k" and "anthropic-version" in headers
    assert payload["system"] == "S" and payload["model"] == "claude-sonnet-5"
    assert payload["messages"] == [{"role": "user", "content": "U"}]


def test_anthropic_refusal(monkeypatch):
    p = create_provider({"type": "anthropic", "api_key": "k"})
    capture(monkeypatch, p, {"stop_reason": "refusal", "content": [],
                             "stop_details": {"category": "x"}})
    with pytest.raises(ProviderError, match="refused"):
        p.complete("S", "U")


def test_bad_shape(monkeypatch):
    p = create_provider({"type": "openai", "model": "m"})
    capture(monkeypatch, p, {"error": "x"})
    with pytest.raises(ProviderError):
        p.complete("S", "U")
