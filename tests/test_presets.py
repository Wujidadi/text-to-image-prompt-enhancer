import pytest

from prompt_enhancer import DEFAULT_PRESET, PresetNotFoundError, list_presets, load_preset
from prompt_enhancer.presets import BUNDLED_DIR


def test_bundled_default(isolated_config):
    preset = load_preset(DEFAULT_PRESET)
    assert preset.path == BUNDLED_DIR / "z-image.txt"
    assert not preset.fixed_language
    assert preset.rule


def test_fixed_language_presets(isolated_config):
    for name in ("anima", "ltx-video"):
        preset = load_preset(name)
        assert preset.fixed_language
        assert not preset.rule.startswith("#")


def test_user_dir_shadows_bundled(isolated_config):
    user_dir = isolated_config.parent / "enhancers"
    user_dir.mkdir()
    (user_dir / "z-image.txt").write_text("MINE", encoding="utf-8")
    assert load_preset("z-image").rule == "MINE"
    names = {p.name: p for p in list_presets()}
    assert names["z-image"].path == user_dir / "z-image.txt"
    assert "anima" in names


def test_caller_dir_and_subdirectory(isolated_config, tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "mine.txt").write_text("SUB", encoding="utf-8")
    assert load_preset("sub/mine", [tmp_path]).rule == "SUB"
    assert load_preset(str(tmp_path / "sub" / "mine.txt")).rule == "SUB"


def test_missing(isolated_config):
    with pytest.raises(PresetNotFoundError):
        load_preset("does-not-exist")


def test_bundled_count(isolated_config):
    assert len(list_presets()) == 13
