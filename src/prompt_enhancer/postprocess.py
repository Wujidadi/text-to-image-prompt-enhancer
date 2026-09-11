"""Cleanup of raw model output"""

import re
from pathlib import Path

T2S_MAP_PATH = Path(__file__).parent / "data" / "t2s.txt"

ENHANCE_MARKERS = (
    "Enhanced Prompt", "Modified Prompt", "Final Prompt",
    "Rewritten Prompt", "Optimized Prompt", "Updated Prompt",
)

_t2s_table = None


def to_simplified(text):
    """Deterministic char-level Traditional-to-Simplified conversion:
    small models ignore the zh directive when the input is long Traditional
    Chinese, and model-side conversion can silently rewrite wording"""
    global _t2s_table
    if _t2s_table is None:
        lines = [l for l in T2S_MAP_PATH.read_text(encoding="utf-8").splitlines()
                 if l and not l.startswith("#")]
        _t2s_table = str.maketrans(lines[0], lines[1])
    return text.translate(_t2s_table)


def clean_output(text, strip_markers=False):
    """Strip code fences, wrapping quotes and (optionally) "Enhanced Prompt:"
    style headings that models tend to add in custom-instruction mode"""
    text = text.strip()
    fenced = re.search(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    else:
        text = re.sub(r"^```[^\n]*\n|\n?```$", "", text).strip()
    if strip_markers:
        best, best_len = -1, 0
        for marker in ENHANCE_MARKERS:
            index = text.rfind(marker)
            if index > best:
                best, best_len = index, len(marker)
        if best != -1:
            text = text[best + best_len:].strip()
            text = re.sub(r"^[^\n]*[:：]\s*", "", text).strip()
            text = re.sub(r"^[\s*#-]+", "", text).strip()
    while len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].strip()
    return text
