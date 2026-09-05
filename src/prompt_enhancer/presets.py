"""Preset lookup: caller directories, then the user directory, then bundled"""

from dataclasses import dataclass
from pathlib import Path

from .config import user_preset_dir
from .errors import PresetNotFoundError
from .prompt import split_pragma

BUNDLED_DIR = Path(__file__).parent / "enhancers"
DEFAULT_PRESET = "z-image"
PRESET_EXT = ".txt"


@dataclass(frozen=True)
class Preset:
    name: str
    path: Path
    rule: str
    fixed_language: bool


def search_dirs(extra_dirs=()):
    return [Path(d).expanduser() for d in extra_dirs] + [user_preset_dir(), BUNDLED_DIR]


def _is_plain_path(value):
    return value.startswith(("/", "~", "./", "../"))


def find_preset(name, extra_dirs=()):
    """Values starting with "/", "~", "./" or "../" are plain paths;
    anything else (subdirectories allowed) is searched in order under the
    caller's directories, the user directory and the bundled directory,
    appending .txt when the last segment has no extension"""
    if _is_plain_path(name):
        path = Path(name).expanduser()
        if path.is_file():
            return path
        raise PresetNotFoundError(f"preset not found: {path}")
    relative = Path(name)
    if not relative.suffix:
        relative = relative.with_suffix(PRESET_EXT)
    for base in search_dirs(extra_dirs):
        candidate = base / relative
        if candidate.is_file():
            return candidate
    raise PresetNotFoundError(f"preset not found: {name}")


def load_preset(name, extra_dirs=()):
    path = find_preset(name, extra_dirs)
    rule, fixed = split_pragma(path.read_text(encoding="utf-8"))
    return Preset(name=name, path=path, rule=rule, fixed_language=fixed)


def list_presets(extra_dirs=()):
    """All presets visible through the search order; a name shadowed by an
    earlier directory is listed once, from the directory that wins"""
    seen = {}
    for base in search_dirs(extra_dirs):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*" + PRESET_EXT)):
            name = path.relative_to(base).with_suffix("").as_posix()
            if name not in seen:
                rule, fixed = split_pragma(path.read_text(encoding="utf-8"))
                seen[name] = Preset(name, path, rule, fixed)
    return [seen[k] for k in sorted(seen)]
