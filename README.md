# Text-to-image Prompt Enhancer

LLM-driven prompt enhancement for text-to-image and video generation models.\
Ships 13 enhancement presets (general, model-format and style), talks to a local ollama by default, and can be pointed at ollama cloud, the WaveSpeed LLM API, or any OpenAI-compatible or Anthropic endpoint.\
Usable as a Python library or as the `prompt-enhancer` command.\
Zero runtime dependencies, Python 3.11+.

## Installation

```sh
# As a command-line tool
uv tool install git+https://github.com/Wujidadi/text-to-image-prompt-enhancer

# As a command-line tool from a checkout, tracking the working tree without reinstalling
uv tool install --editable .

# As a dependency of a script (PEP 723 inline metadata)
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "text-to-image-prompt-enhancer @ git+https://github.com/Wujidadi/text-to-image-prompt-enhancer@v0.1.0",
# ]
# ///

# As a dependency of a project
uv add "text-to-image-prompt-enhancer @ git+https://github.com/Wujidadi/text-to-image-prompt-enhancer@v0.1.0"
```

Without any configuration, enhancement runs against a local [ollama](https://ollama.com) at `http://localhost:11434` with `qwen3.5:4b`.\
Thinking is disabled there: 4B-scale thinking was measured slower and no better for this task.

## Command Line

```sh
prompt-enhancer "a fox in snow"                          # default preset z-image
prompt-enhancer -p ghibli-watercolor "a fox in snow"     # named preset
prompt-enhancer -i "add a straw hat" "a fox in snow"     # custom-instruction mode
prompt-enhancer -p ernie -l zh "一隻橘貓在窗台上睡覺"    # Simplified Chinese output
echo "a fox in snow" | prompt-enhancer -P claude         # provider profile, stdin
prompt-enhancer -f prompts/fox.txt                       # prompt file, comment lines dropped
prompt-enhancer --list-presets
prompt-enhancer --list-providers
```

Choosing the model, with the profiles from the [configuration](#configuration) example below:

```sh
prompt-enhancer -P gemma4 "a fox in snow"                                  # another local ollama model, by profile
prompt-enhancer -m qwen3.6:35b "a fox in snow"                             # or by model name on the default profile
prompt-enhancer -P ollama-cloud "a fox in snow"                            # ollama cloud through the signed-in local server
prompt-enhancer -P ollama-cloud -m gpt-oss:20b-cloud "a fox in snow"       # any tag ending in -cloud
prompt-enhancer -P wavespeed "a fox in snow"                               # WaveSpeed LLM API
prompt-enhancer -P wavespeed -m google/gemini-2.5-flash "a fox in snow"
```

| Option                       | Description                                                           |
| ---------------------------- | --------------------------------------------------------------------- |
| `text`                       | Prompt text; read from stdin when omitted                             |
| `--file`, `-f`               | Read the prompt from a UTF-8 file instead, dropping comment lines     |
| `--preset`, `-p`             | Preset name (subdirectories allowed) or plain path; default `z-image` |
| `--instruction`, `-i`        | Ad-hoc instruction; appended to the preset, or custom mode when alone |
| `--language`, `-l`           | Output language `en` (default) or `zh` (Simplified Chinese)           |
| `--provider`, `-P`           | Provider profile from the config file                                 |
| `--type`, `--model`, `--url` | Override the chosen profile's type, model or endpoint                 |
| `--preset-dir`               | Extra preset directory searched first (repeatable)                    |
| `--config`                   | Config file path                                                      |
| `--show-system`              | Print the assembled system instruction to stderr                      |
| `--quiet`, `-q`              | Suppress the progress line on stderr                                  |
| `--list-presets`             | List visible presets with their source path                           |
| `--list-providers`           | List provider profiles (`*` marks the default)                        |

In a prompt file, a line that is `#` alone, or starts with `# ` or `//` after any indentation, is a comment and never reaches the model;\
`#hashtag` is kept as prompt text, since tags are part of some prompts.

The enhanced prompt goes to stdout; everything else goes to stderr.\
Exit status is 1 on any failure.

## Library

```python
from prompt_enhancer import Enhancer, PromptEnhancerError

enhancer = Enhancer.from_config()                  # default profile
enhancer = Enhancer.from_config("claude")          # named profile
enhancer = Enhancer.from_config(overrides={"model": "qwen3.5:8b"}, language="zh")

try:
    result = enhancer.enhance("a fox in snow", preset="space-epic")
    result = enhancer.enhance(result, instruction="make it night")   # appended to z-image
    result = enhancer.enhance("a fox", preset=None, instruction="add a hat")  # custom mode
except PromptEnhancerError as e:
    ...
```

- `Enhancer(provider, language=None, preset_dirs=())` takes any `Provider`.\
  `Enhancer.from_config(provider=None, overrides=None, *, language=None, preset_dirs=(), config_path=None)` builds one from the config file.
- `enhance(text, *, preset=None, instruction=None, language=None) -> str` performs a single pass and raises a `PromptEnhancerError` subclass (`ConfigError`, `PresetNotFoundError`, `ProviderError`) on failure.\
  `preset=None` means the default preset, unless an instruction is given, which selects custom-instruction mode.
- `prepare(preset, instruction, language)` returns the assembled system instruction without calling the model.
- `enhancer.provider.describe()` gives a short `"<type> <model>"` label.
- `enhance(...)` at module level wraps both steps in one call.
- Also exported for callers that need the pieces:
  - `list_presets(extra_dirs=())`
  - `load_preset(name, extra_dirs=())`
  - `load_config(path=None)`
  - `create_provider(settings)`
  - `clean_output(text, strip_markers=False)`
  - `to_simplified(text)`

Interactive review loops belong to the caller: the library is single-pass.

## Configuration

The config file is `~/.config/prompt-enhancer/config.toml`, or the file named by `$PROMPT_ENHANCER_CONFIG`; see [config.example.toml](config.example.toml).\
The file is optional.

A convenient way to keep the local config next to a checkout, where `config.toml` is git-ignored:

```sh
cp config.example.toml config.toml
mkdir -p ~/.config/prompt-enhancer
ln -s "$PWD/config.toml" ~/.config/prompt-enhancer/config.toml
```

```toml
default_provider = "ollama"
language = "en"
preset_dirs = []

[providers.ollama]
type = "ollama"
url = "http://localhost:11434"
model = "qwen3.5:4b"

[providers.gemma4]
type = "ollama"
model = "gemma4:26b"

[providers.ollama-cloud]        # needs "ollama signin"; -cloud tags run on ollama.com
type = "ollama"
model = "gpt-oss:120b-cloud"

[providers.openrouter]
type = "openai"
url = "https://openrouter.ai/api/v1"
model = "deepseek/deepseek-chat"
api_key_env = "OPENROUTER_API_KEY"

[providers.wavespeed]
type = "wavespeed"
model = "deepseek/deepseek-v4-flash"

[providers.claude]
type = "anthropic"
model = "claude-sonnet-5"
api_key_env = "ANTHROPIC_API_KEY"
```

| Type        | Endpoint                      | Default `url`                  | Notes                                                     |
| ----------- | ----------------------------- | ------------------------------ | --------------------------------------------------------- |
| `ollama`    | `POST {url}/api/chat`         | `http://localhost:11434`       | `think` (default `false`)                                 |
| `openai`    | `POST {url}/chat/completions` | `https://api.openai.com/v1`    | LM Studio, llama.cpp, vLLM, OpenRouter...                 |
| `wavespeed` | `POST {url}/chat/completions` | `https://llm.wavespeed.ai/v1`  | key from `$WAVESPEED_API_KEY` unless `api_key_env` is set |
| `anthropic` | `POST {url}/v1/messages`      | `https://api.anthropic.com`    | `max_tokens` (default 4096)                               |

Keys common to every profile:

- `model`
- `url`
- `timeout`: seconds, default 300
- `api_key_env`: environment variable holding the key; an `api_key` literal also works but is discouraged
- `extra`: a table merged verbatim into the request body, e.g. `temperature` or vendor-specific options

Callers may pass any of these as overrides on top of a profile.

## Presets

A preset file is the complete system instruction sent to the model.\
Lookup order for a name such as `z-image` or `styles/mine`:

1. directories passed by the caller (`--preset-dir` / `preset_dirs`)
2. `~/.config/prompt-enhancer/enhancers/` (next to the config file)
3. the bundled presets

Names starting with `/`, `~`, `./` or `../` are plain file paths.\
`.txt` is appended when the last segment has no extension.\
A name found in an earlier directory shadows the same name later on, so a bundled preset can be overridden by dropping a file into the user directory.

| Preset                | Type    | Description                            |
| --------------------- | ------- | -------------------------------------- |
| `ernie`               | General | Detailed objective image description   |
| `z-image`             | General | Faithful, aesthetic visual description |
| `anima`               | Model   | Anima tag-format prompt rules          |
| `ltx-video`           | Model   | LTX-2.3 audio-video cinematic prompt   |
| `leica-portrait`      | Style   | Cinematic photorealistic portrait      |
| `ghibli-watercolor`   | Style   | Studio Ghibli watercolor painting      |
| `cyberpunk-mecha`     | Style   | Futuristic cyberpunk concept art       |
| `monet-impressionist` | Style   | Monet-like Impressionist oil painting  |
| `vaporwave-surreal`   | Style   | Vaporwave retro-futurism aesthetic     |
| `space-epic`          | Style   | Sci-fi space art with epic scale       |
| `chinoiserie-ink`     | Style   | Modern Chinese splash-ink style        |
| `vinyl-toy`           | Style   | Cute 3D Pop Mart vinyl toy style       |
| `wabi-sabi-minimal`   | Style   | Wabi-sabi architectural minimalism     |

### Output Language

A language directive (`en` or `zh`) is placed ahead of the preset rule;\
placing it after a long rule loses to input-script copying on small models.\
`zh` deliberately means Simplified Chinese, because Chinese-capable image models are trained mostly on Simplified corpora.\
Simplified output is additionally guaranteed by a deterministic char-level Traditional-to-Simplified pass (`data/t2s.txt`, distilled from OpenCC), since small models ignore the directive on long Traditional input.

Presets whose target requires a specific language declare `# prompt-enhancer:fixed-language` as their first line:\
the line is stripped, no directive is added, and the language selection is ignored.\
`anima` and `ltx-video` ship with the pragma.

### Custom-Instruction Mode

With an instruction and no preset, a built-in editing rule merges the instruction into the original prompt (e.g. "add a straw hat") while keeping everything else intact.\
With a preset, the instruction is appended to the preset as an overriding requirement.

Markdown code fences and wrapping quotes are always stripped from the model output;\
in custom mode, leading "Enhanced Prompt:"-style headings are stripped too.

## Development

```sh
uv sync
uv run pytest
uv run prompt-enhancer --list-presets
```
