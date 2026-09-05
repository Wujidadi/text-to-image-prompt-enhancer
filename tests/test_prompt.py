import pytest

from prompt_enhancer.prompt import (FIXED_LANGUAGE_PRAGMA, LANGUAGE_DIRECTIVES,
                                    build_system, split_pragma)


def test_language_directive_leads():
    system = build_system("RULE", False, "zh", None)
    assert system.startswith(LANGUAGE_DIRECTIVES["zh"])
    assert system.endswith("RULE")


def test_fixed_language_omits_directive():
    assert build_system("RULE", True, "zh", None) == "RULE"


def test_instruction_appended():
    system = build_system("RULE", False, "en", "add a hat")
    assert system.endswith("Custom instruction (takes precedence over the rules above): add a hat")


def test_unknown_language():
    with pytest.raises(ValueError):
        build_system("RULE", False, "fr", None)


def test_split_pragma():
    assert split_pragma(f"{FIXED_LANGUAGE_PRAGMA}\nRULE\n") == ("RULE", True)
    assert split_pragma("RULE\nmore") == ("RULE\nmore", False)
