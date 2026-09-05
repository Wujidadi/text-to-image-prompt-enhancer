"""System-instruction assembly"""

FIXED_LANGUAGE_PRAGMA = "# prompt-enhancer:fixed-language"

# Chinese deliberately means Simplified: Chinese-capable image models are
# trained mostly on Simplified corpora, so it prompts better
LANGUAGE_DIRECTIVES = {
    "en": "Regardless of the input language, write the final prompt in English.",
    "zh": "Regardless of the input language, the final prompt MUST be written "
          "entirely in Simplified Chinese (简体中文); convert any Traditional "
          "Chinese characters to their Simplified forms.",
}
DEFAULT_LANGUAGE = "en"

CUSTOM_RULE = """You are a professional prompt editor for image and video generation models.

Your task:
1. Produce exactly one final prompt from the original prompt and the custom instruction.
2. When the instruction asks for a local change (e.g. "add a hat to the character"), merge that change into the original prompt and keep everything else intact; never produce multiple versions.
3. The output must be a complete prompt that can directly replace the original.

Do not output the original prompt, headings such as "Enhanced Prompt", explanations, comparisons, lists, Markdown, code blocks, or quotes wrapping the result."""


def split_pragma(text):
    """Return (rule, fixed_language) for a preset file's text"""
    text = text.strip()
    first, _, rest = text.partition("\n")
    if first.strip() == FIXED_LANGUAGE_PRAGMA:
        return rest.strip(), True
    return text, False


def build_system(rule, fixed_language, language, instruction=None):
    """Assemble the system instruction sent to the model.

    The language directive must lead: appended after a long rule it loses
    to the model's input-script copying (measured with qwen3.5:4b on
    Traditional Chinese input)"""
    if language not in LANGUAGE_DIRECTIVES:
        raise ValueError(f"unknown language: {language}")
    system = "" if fixed_language else LANGUAGE_DIRECTIVES[language] + "\n\n"
    system += rule
    if instruction:
        system += ("\n\nCustom instruction (takes precedence over the rules "
                   f"above): {instruction}")
    return system
