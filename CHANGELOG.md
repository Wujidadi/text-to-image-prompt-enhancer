# Changelog

All notable changes to this project are documented in this file.\
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `tests/test_version.py`, asserting that `__version__` matches `pyproject.toml`.
- `CHANGELOG.md` and the testing and release process in `AGENTS.md`.

## [0.1.0] - 2026-09-05

### Added

- Initial import of the `prompt_enhancer` library and the `prompt-enhancer` CLI.
- Bundled presets under `enhancers/`, with `z-image` as the default.
- Providers `ollama`, `openai` (Chat Completions compatible hosts) and `anthropic`, all over `urllib`.
- User config at `~/.config/prompt-enhancer/config.toml` with provider profiles, default language and extra preset directories.
- Deterministic Traditional-to-Simplified post-processing for `zh` output.

[Unreleased]: https://github.com/Wujidadi/text-to-image-prompt-enhancer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Wujidadi/text-to-image-prompt-enhancer/releases/tag/v0.1.0
