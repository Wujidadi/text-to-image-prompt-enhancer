# text-to-image-prompt-enhancer

LLM-driven prompt enhancement for text-to-image and video generation models, packaged as a Python library plus the `prompt-enhancer` CLI.\
See [README.md](README.md) for usage;\
this file only records what matters for development and maintenance.

## Architecture and Files

- `pyproject.toml`: distribution name `text-to-image-prompt-enhancer`, import name `prompt_enhancer`, hatchling build, no runtime dependencies (`pytest` is the only dev dependency).\
  Python 3.11+ is required for `tomllib`.
- `src/prompt_enhancer/__init__.py`: the public API.\
  `Enhancer` performs a single enhancement pass;\
  `Enhancer.from_config()` builds one from the user config, and the module-level `enhance()` wraps both.\
  Interactive review loops are deliberately left to callers (e.g. `dtgen`).
- `presets.py`: preset lookup in the order caller directories, `~/.config/prompt-enhancer/enhancers/`, bundled `enhancers/`;\
  a name found earlier shadows the same name later.
- `prompt.py`: language directives, the custom-instruction rule and `build_system()`.\
  The language directive must lead the system instruction:\
  appended after a long rule it loses to the model's input-script copying (measured with qwen3.5:4b on Traditional Chinese input).\
  A preset whose first line is `# prompt-enhancer:fixed-language` gets no directive and ignores the language selection (`anima`, `ltx-video`).
- `postprocess.py`: `clean_output()` (code fences, wrapping quotes, "Enhanced Prompt:"-style markers in custom mode) and `to_simplified()`, a deterministic char-level Traditional-to-Simplified pass over `data/t2s.txt` (distilled from OpenCC, Apache 2.0, attribution kept in the file header).\
  `zh` deliberately means Simplified Chinese because Chinese-capable image models are trained mostly on Simplified corpora, and small models ignore the directive on long Traditional input.
- `config.py`: `~/.config/prompt-enhancer/config.toml` (or `$PROMPT_ENHANCER_CONFIG`), optional;\
  provider profiles under `[providers.<name>]`, `default_provider`, `language`, `preset_dirs`.\
  The built-in `ollama` profile (`http://localhost:11434`, `qwen3.5:4b`) always exists.
- `providers/`: one class per backend type, all raw HTTP via `urllib` (no SDKs, to keep the package dependency-free).\
  `ollama` (`/api/chat`, thinking disabled by default: 4B-scale thinking was measured slower and no better for this task), `openai` (Chat Completions, covers LM Studio, llama.cpp, vLLM, OpenRouter and similar hosts), `wavespeed` (the same Chat Completions request against `llm.wavespeed.ai`, keyed by `$WAVESPEED_API_KEY` by default, the route the maintainer actually pays for), `anthropic` (Messages API, default model `claude-sonnet-5`, chosen over Opus 5 because the measured quality gain did not justify the cost).\
  Add a backend by subclassing `Provider` and registering it in `PROVIDER_TYPES`;\
  `default_api_key_env` on the class names the environment variable consulted when the profile sets neither `api_key` nor `api_key_env`.
- `enhancers/`: the bundled presets, one file per preset, each being the complete system instruction.\
  `z-image` is the default.
- `config.example.toml`: annotated example of every provider type.
- `CHANGELOG.md`: release history in Keep a Changelog format, the only document in this repository that records history.
- `tests/`: pytest;\
  `conftest.py` provides `FakeProvider` and the `isolated_config` fixture, which points the user config at an empty temp directory so tests never read the developer's real config or presets.

## Development and Testing

```sh
uv sync
uv run pytest
uv run prompt-enhancer --list-presets
uv run prompt-enhancer -q "a fox in snow"      # real call against local ollama
```

- Provider request shapes are tested by monkeypatching `Provider._post_json`;\
  network calls are never made in tests.
- There is no CI, but the suite must pass before every commit:\
  run `uv run pytest` and never commit on red.
- Tests live in `tests/test_<module>.py`, one file per source module;\
  add or extend tests for any change that alters observable behavior (new preset, provider, config key, post-processing rule, CLI flag).\
  A change that does not affect coverage, such as a docstring or a comment, does not require a test, but prefer adding one whenever a cheap assertion exists.
- The real-call examples above (`prompt-enhancer -q ...` against local ollama) are manual checks and not part of the suite.
- To test a consumer such as `dtgen` against this checkout before a tag exists:\
  `uv run --no-project --with <this directory> python <script> ...`.

## Releases

- Version numbers follow `x.y.z`:
  - bump `z` for the usual change, including new presets, providers and options;
  - bump `y` for a breaking change to the public API, the config schema or a preset name;
  - bumping `x` (in particular `0` to `1`) is decided explicitly by the maintainer, never by an agent.
- `version` in `pyproject.toml` and `__version__` in `src/prompt_enhancer/__init__.py` must match;\
  `tests/test_version.py` fails when they drift.
- `CHANGELOG.md` follows Keep a Changelog;\
  every behavior change adds a line under `[Unreleased]` in the same commit.
- Release steps, in order:
  1. finish and commit all code changes, with `README.md` updated in sync and the suite green;
  2. bump the two version numbers, rename `[Unreleased]` in `CHANGELOG.md` to the new version with the release date and update the comparison links, and commit these release-only changes as `chore: release vX.Y.Z`;
  3. create an annotated tag `vX.Y.Z` whose message briefly lists the changes since the previous tag, mirroring the changelog entry;
  4. push the branch and the tag only when the maintainer asks.
- Consumers pin a release tag, so after a release tell the maintainer which consumers must move their pin and which changelog entries are breaking for them.\
  The known consumer is `dtgen` (`~/Documents/Workspaces/AI/Draw Things/custom/dtgen`), a PEP 723 script whose inline `dependencies` pins `text-to-image-prompt-enhancer @ git+https://github.com/Wujidadi/text-to-image-prompt-enhancer@vX.Y.Z`;\
  moving the pin means editing that line, with no lock file to regenerate.
- The surface `dtgen` depends on, all imported from the `prompt_enhancer` top level, and therefore breaking when changed:
  - `DEFAULT_PRESET`;
  - `Enhancer.from_config(provider, overrides, language=...)` with the positional `provider` and `overrides` and the keyword `language`;
  - `Enhancer.enhance(text, preset=..., instruction=...)`, including `preset=None` for custom-instruction mode;
  - `enhancer.provider.describe()`;
  - `PromptEnhancerError` as the base class of every error raised by `from_config()` and `enhance()`;
  - the language set `en` and `zh`, which `dtgen` hard-codes as CLI choices.

## Conventions

- Everything in this repository is written in English:\
  code, comments, documentation, commit messages.
- Markdown prose is wrapped by meaning, not by column width:
  - one sentence per line, however long;\
    break only at a sentence end, at a semicolon joining two substantial clauses, or at a colon or dash that introduces a clause or list;
  - never break after a comma, unless a single sentence is long enough to span three or four displayed lines;
  - inside a paragraph or a list item, every line except the last ends with a `\` hard break, so GitHub renders the line breaks instead of collapsing them into spaces;
  - a comma-separated enumeration with long or many items becomes a Markdown list;
  - tables and code blocks are left as they are;\
    re-align tables by display width after editing (CJK characters count as two columns).
- Documents describe the current state only;\
  history belongs to Git, not to the documents.
