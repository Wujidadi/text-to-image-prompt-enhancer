# Changelog

All notable changes to this project are documented in this file.\
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-09-11

### Added

- CLI option `--file`/`-f` reading the prompt from a file, where lines that are `#` alone or start with `# ` or `//` are comments and dropped.

## [0.2.0] - 2026-09-06

### Added

- Provider type `wavespeed` for the WaveSpeed LLM API (`https://llm.wavespeed.ai/v1`, Chat Completions), reading the key from `$WAVESPEED_API_KEY` unless the profile says otherwise.
- `Provider.default_api_key_env`, the per-type fallback environment variable for the API key.
- `tests/test_version.py`, asserting that `__version__` matches `pyproject.toml`.
- `CHANGELOG.md` and the testing and release process in `AGENTS.md`.

## [0.1.0] - 2026-09-05

### Added

- Initial import of the `prompt_enhancer` library and the `prompt-enhancer` CLI.
- Bundled presets under `enhancers/`, with `z-image` as the default.
- Providers `ollama`, `openai` (Chat Completions compatible hosts) and `anthropic`, all over `urllib`.
- User config at `~/.config/prompt-enhancer/config.toml` with provider profiles, default language and extra preset directories.
- Deterministic Traditional-to-Simplified post-processing for `zh` output.

[Unreleased]: https://github.com/Wujidadi/text-to-image-prompt-enhancer/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/Wujidadi/text-to-image-prompt-enhancer/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Wujidadi/text-to-image-prompt-enhancer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Wujidadi/text-to-image-prompt-enhancer/releases/tag/v0.1.0
