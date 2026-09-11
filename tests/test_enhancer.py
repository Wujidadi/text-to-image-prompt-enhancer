import pytest

from prompt_enhancer import CUSTOM_RULE, Enhancer, ProviderError, enhance
from prompt_enhancer.prompt import LANGUAGE_DIRECTIVES


def test_preset_mode_default(isolated_config, fake):
    provider = fake("  a cat  ")
    assert Enhancer(provider).enhance("cat") == "a cat"
    system, prompt = provider.calls[0]
    assert system.startswith(LANGUAGE_DIRECTIVES["en"])
    assert "visual artist" in system
    assert prompt == "cat"


def test_custom_mode_strips_markers(isolated_config, fake):
    provider = fake("Enhanced Prompt: a cat with a hat")
    result = Enhancer(provider).enhance("a cat", instruction="add a hat")
    assert result == "a cat with a hat"
    assert CUSTOM_RULE in provider.calls[0][0]


def test_zh_forces_simplified(isolated_config, fake):
    provider = fake("一隻橘貓")
    assert Enhancer(provider, language="zh").enhance("x") == "一只橘猫"


def test_fixed_language_ignores_zh(isolated_config, fake):
    provider = fake("一隻橘貓")
    result = Enhancer(provider).enhance("x", preset="anima", language="zh")
    assert result == "一隻橘貓"
    assert LANGUAGE_DIRECTIVES["zh"] not in provider.calls[0][0]


def test_empty_reply(isolated_config, fake):
    with pytest.raises(ProviderError, match="empty"):
        Enhancer(fake("```\n```")).enhance("x")


def test_from_config_language_precedence(isolated_config):
    isolated_config.write_text('language = "zh"\n', encoding="utf-8")
    assert Enhancer.from_config().language == "zh"
    assert Enhancer.from_config(language="en").language == "en"
    assert Enhancer.from_config(overrides={"model": "m2"}).provider.model == "m2"


def test_convenience_wrapper(isolated_config, monkeypatch, fake):
    provider = fake("done")
    monkeypatch.setattr("prompt_enhancer.create_provider", lambda s: provider)
    assert enhance("x", preset="ernie") == "done"
