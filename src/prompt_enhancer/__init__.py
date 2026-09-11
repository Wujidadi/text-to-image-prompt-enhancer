"""LLM-driven prompt enhancement for text-to-image and video models"""

from .config import Config, load_config
from .errors import ConfigError, PresetNotFoundError, PromptEnhancerError, ProviderError
from .postprocess import clean_output, to_simplified
from .presets import DEFAULT_PRESET, Preset, list_presets, load_preset
from .prompt import CUSTOM_RULE, DEFAULT_LANGUAGE, LANGUAGE_DIRECTIVES, build_system
from .providers import Provider, create_provider

__version__ = "0.2.1"


class Enhancer:
    """Single-pass prompt enhancement against one provider.

    `language` is the default output language; `preset_dirs` are searched
    before the user and bundled preset directories"""

    def __init__(self, provider, *, language=None, preset_dirs=()):
        self.provider = provider
        self.language = language or DEFAULT_LANGUAGE
        self.preset_dirs = list(preset_dirs)
        if self.language not in LANGUAGE_DIRECTIVES:
            raise ConfigError(f'unknown language "{self.language}" '
                              f"(known: {', '.join(sorted(LANGUAGE_DIRECTIVES))})")

    @classmethod
    def from_config(cls, provider=None, overrides=None, *, language=None,
                    preset_dirs=(), config_path=None):
        """Build from the user config file: `provider` names a profile
        (the configured default when None), `overrides` patch its settings.
        Language precedence: argument > config file > en"""
        config = load_config(config_path)
        settings = config.provider_settings(provider, overrides)
        return cls(create_provider(settings),
                   language=language or config.language,
                   preset_dirs=list(preset_dirs) + config.preset_dirs)

    def prepare(self, preset=None, instruction=None, language=None):
        """Resolve preset and language into (system, fixed_language,
        custom_mode); exposed so callers can show or log the instruction"""
        language = language or self.language
        if language not in LANGUAGE_DIRECTIVES:
            raise ConfigError(f'unknown language "{language}"')
        custom_mode = preset is None and bool(instruction)
        if custom_mode:
            rule, fixed = CUSTOM_RULE, False
        else:
            loaded = load_preset(preset or DEFAULT_PRESET, self.preset_dirs)
            rule, fixed = loaded.rule, loaded.fixed_language
        return build_system(rule, fixed, language, instruction), fixed, custom_mode

    def enhance(self, text, *, preset=None, instruction=None, language=None):
        """Return the enhanced prompt.

        preset=None with an instruction runs custom-instruction mode
        (merge the instruction into the prompt); preset=None without one
        uses DEFAULT_PRESET. Raises PromptEnhancerError subclasses"""
        language = language or self.language
        system, fixed, custom_mode = self.prepare(preset, instruction, language)
        raw = self.provider.complete(system, text)
        result = clean_output(raw or "", strip_markers=custom_mode)
        if not result:
            raise ProviderError(f"{self.provider.describe()}: empty response")
        if language == "zh" and not fixed:
            result = to_simplified(result)
        return result


def enhance(text, *, preset=None, instruction=None, language=None,
            provider=None, overrides=None, preset_dirs=(), config_path=None):
    """One-call convenience wrapper around Enhancer.from_config().enhance()"""
    enhancer = Enhancer.from_config(provider, overrides, language=language,
                                    preset_dirs=preset_dirs, config_path=config_path)
    return enhancer.enhance(text, preset=preset, instruction=instruction)


__all__ = [
    "Enhancer", "enhance", "Config", "load_config", "Provider", "create_provider",
    "Preset", "list_presets", "load_preset", "DEFAULT_PRESET", "DEFAULT_LANGUAGE",
    "LANGUAGE_DIRECTIVES", "CUSTOM_RULE", "build_system", "clean_output",
    "to_simplified", "PromptEnhancerError", "ConfigError", "PresetNotFoundError",
    "ProviderError", "__version__",
]
