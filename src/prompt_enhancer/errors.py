class PromptEnhancerError(Exception):
    """Base class for every error raised by prompt_enhancer"""


class ConfigError(PromptEnhancerError):
    """Invalid configuration file or provider settings"""


class PresetNotFoundError(PromptEnhancerError):
    """The named preset could not be found in any search directory"""


class ProviderError(PromptEnhancerError):
    """The model backend failed or returned an unusable response"""
