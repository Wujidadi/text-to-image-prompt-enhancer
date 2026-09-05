import pytest

from prompt_enhancer import ConfigError, load_config
from prompt_enhancer.providers import create_provider


def test_missing_file_gives_builtin(isolated_config):
    config = load_config()
    settings = config.provider_settings()
    assert settings["type"] == "ollama"
    assert settings["model"] == "qwen3.5:4b"
    assert settings["name"] == "ollama"


def test_profiles_and_overrides(isolated_config):
    isolated_config.write_text("""
default_provider = "cloud"
language = "zh"
[providers.cloud]
type = "openai"
url = "https://example.test/v1"
model = "m"
api_key_env = "EXAMPLE_KEY"
""", encoding="utf-8")
    config = load_config()
    assert config.language == "zh"
    assert config.provider_settings()["model"] == "m"
    assert config.provider_settings("ollama")["type"] == "ollama"
    assert config.provider_settings(overrides={"model": "n"})["model"] == "n"
    with pytest.raises(ConfigError):
        config.provider_settings("nope")


def test_bad_default(isolated_config):
    isolated_config.write_text('default_provider = "x"\n', encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config()


def test_api_key_env(isolated_config, monkeypatch):
    provider = create_provider({"type": "openai", "model": "m", "api_key_env": "K"})
    with pytest.raises(ConfigError):
        provider.api_key
    monkeypatch.setenv("K", "secret")
    assert provider.api_key == "secret"


def test_unknown_type():
    with pytest.raises(ConfigError):
        create_provider({"type": "nope", "model": "m"})
