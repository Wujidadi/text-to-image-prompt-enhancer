import tomllib
from pathlib import Path

import prompt_enhancer


def test_version_matches_pyproject():
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    with pyproject.open("rb") as f:
        assert prompt_enhancer.__version__ == tomllib.load(f)["project"]["version"]
