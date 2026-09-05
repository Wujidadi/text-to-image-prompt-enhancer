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
  `ollama` (`/api/chat`, thinking disabled by default: 4B-scale thinking was measured slower and no better for this task), `openai` (Chat Completions, covers LM Studio, llama.cpp, vLLM, OpenRouter and similar hosts), `anthropic` (Messages API, default model `claude-sonnet-5`, chosen over Opus 5 because the measured quality gain did not justify the cost).\
  Add a backend by subclassing `Provider` and registering it in `PROVIDER_TYPES`.
- `enhancers/`: the bundled presets, one file per preset, each being the complete system instruction.\
  `z-image` is the default.
- `config.example.toml`: annotated example of every provider type.
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
- After a behavior change, update `README.md` in sync and bump `version` in `pyproject.toml` and `__init__.py`;\
  consumers pin a release tag (`vX.Y.Z`), so tag releases.
- To test a consumer such as `dtgen` against this checkout before a tag exists:\
  `uv run --no-project --with <this directory> python <script> ...`.

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
