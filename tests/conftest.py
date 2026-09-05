import pytest

from prompt_enhancer.providers.base import Provider


class FakeProvider(Provider):
    type_name = "fake"
    default_model = "fake-model"

    def __init__(self, reply="", settings=None):
        super().__init__(settings or {})
        self.reply = reply
        self.calls = []

    def complete(self, system, prompt):
        self.calls.append((system, prompt))
        return self.reply


@pytest.fixture
def fake():
    return FakeProvider


@pytest.fixture
def isolated_config(tmp_path, monkeypatch):
    """Point the user config at an empty temp directory"""
    path = tmp_path / "config.toml"
    monkeypatch.setenv("PROMPT_ENHANCER_CONFIG", str(path))
    return path
