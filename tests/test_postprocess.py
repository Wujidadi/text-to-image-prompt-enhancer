from prompt_enhancer.postprocess import clean_output, to_simplified


def test_strip_fence_and_quotes():
    assert clean_output('```text\n"a cat"\n```') == "a cat"


def test_markers_only_in_custom_mode():
    raw = "Original: x\n\n**Enhanced Prompt:** a cat with a hat"
    assert clean_output(raw, strip_markers=True) == "a cat with a hat"
    assert clean_output(raw) == raw


def test_to_simplified():
    assert to_simplified("一隻橘貓在窗臺上睡覺") == "一只橘猫在窗台上睡觉"
    assert to_simplified("plain ascii") == "plain ascii"
