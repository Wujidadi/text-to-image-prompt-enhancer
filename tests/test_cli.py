import pytest

from prompt_enhancer import Enhancer, cli


@pytest.fixture
def run(isolated_config, fake, monkeypatch):
    """Run the CLI against a FakeProvider; returns the provider"""
    provider = fake("enhanced")
    monkeypatch.setattr(Enhancer, "from_config",
                        classmethod(lambda cls, *a, **kw: Enhancer(provider)))

    def _run(*argv):
        cli.main(["-q", *argv])
        return provider
    return _run


@pytest.mark.parametrize("line", ["#", "//", "# note", "// note", "//x",
                                  "   # indented", "\t// tabbed"])
def test_comment_lines(line):
    assert cli.is_comment_line(line)


@pytest.mark.parametrize("line", ["#hashtag", "text", "", "a # b", "a // b"])
def test_non_comment_lines(line):
    assert not cli.is_comment_line(line)


def test_file_drops_comment_lines(run, tmp_path, capsys):
    path = tmp_path / "p.txt"
    path.write_text("# header\n\nfirst line\n// note\n\nsecond line\n# 中文註釋\n",
                    encoding="utf-8")
    provider = run("-f", str(path))
    assert provider.calls[0][1] == "first line\n\nsecond line"
    assert capsys.readouterr().out == "enhanced\n"


def test_file_with_only_comments_is_empty(run, tmp_path, capsys):
    path = tmp_path / "p.txt"
    path.write_text("# only a comment\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        run("--file", str(path))
    assert "empty prompt" in capsys.readouterr().err


def test_missing_file(run, tmp_path, capsys):
    with pytest.raises(SystemExit):
        run("-f", str(tmp_path / "missing.txt"))
    assert "cannot read prompt file" in capsys.readouterr().err


def test_file_and_text_conflict(run, tmp_path, capsys):
    path = tmp_path / "p.txt"
    path.write_text("a cat", encoding="utf-8")
    with pytest.raises(SystemExit):
        run("-f", str(path), "a dog")
    assert "not both" in capsys.readouterr().err


def test_text_argument_keeps_hash_lines(run):
    provider = run("# not a comment here")
    assert provider.calls[0][1] == "# not a comment here"
