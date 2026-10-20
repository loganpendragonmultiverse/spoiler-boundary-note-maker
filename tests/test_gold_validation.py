import json

import pytest

from spoiler_boundary_note_maker.cli import main
from spoiler_boundary_note_maker.core import analyze


def test_fresh_outputs_and_input_preservation(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text(json.dumps({"works": [{"name": "Harbor", "through": 3}]}), encoding="utf-8")
    before = source.read_bytes()
    output = tmp_path / "report.json"
    assert main([str(source), "--format", "json", "--output", str(output)]) == 0
    assert (
        json.loads(output.read_text(encoding="utf-8"))["project"] == "spoiler-boundary-note-maker"
    )
    assert source.read_bytes() == before
    assert main([str(source), "--output", str(output)]) == 2
    assert "error:" in capsys.readouterr().err
    assert (
        json.loads(output.read_text(encoding="utf-8"))["project"] == "spoiler-boundary-note-maker"
    )
    assert main([str(source), "--output", str(source)]) == 2
    assert source.read_bytes() == before


def test_dangling_output_link_is_not_followed(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text(json.dumps({"works": [{"name": "Harbor", "through": 3}]}), encoding="utf-8")
    target = tmp_path / "must-not-be-created.txt"
    link = tmp_path / "report.json"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("creating symbolic links is not available to this user")
    assert main([str(source), "--output", str(link)]) == 2
    assert "error:" in capsys.readouterr().err
    assert link.is_symlink() and not target.exists()


def test_cli_io_and_json_errors(tmp_path, capsys):
    source = tmp_path / "bad.json"
    for contents in [b"{", b"\xff"]:
        source.write_bytes(contents)
        assert main([str(source)]) == 2
        assert "error:" in capsys.readouterr().err
    assert main([str(tmp_path / "missing.json")]) == 2
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("value", [None, [], "text", 42, True])
def test_invalid_roots_are_actionable(value, tmp_path, capsys):
    with pytest.raises(TypeError, match="JSON object"):
        analyze(value)
    source = tmp_path / "input.json"
    source.write_text(json.dumps(value), encoding="utf-8")
    assert main([str(source)]) == 2
    assert "JSON object" in capsys.readouterr().err


@pytest.mark.parametrize(
    "patch",
    [
        {"name": "   "},
        {"name": 42},
        {"people": []},
        {"people": [None]},
        {"people": [{"name": [], "boundary": 2}]},
        {"people": [{"name": "  ", "boundary": 2}]},
        {"people": [{"name": "A"}]},
        {"exclusions": {}},
        {"exclusions": [None]},
        {"exclusions": [{"category": "identity"}]},
        {"exclusions": [{"category": [], "text": "the keeper"}]},
        {"exclusions": [{"text": []}]},
        {"exclusions": ["  "]},
    ],
)
def test_invalid_work_fields_fail_closed(patch, tmp_path, capsys):
    data = {"works": [{"name": "Harbor", "through": 2, **patch}]}
    with pytest.raises((ValueError, TypeError)):
        analyze(data)
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert main([str(source)]) == 2
    assert "error:" in capsys.readouterr().err


def test_legacy_and_categorized_exclusions_and_presets():
    for preset in ["friends", "private", "public"]:
        report = analyze(
            {
                "preset": preset,
                "works": [
                    {
                        "name": "Harbor",
                        "through": "Chapter 2",
                        "exclusions": ["the keeper", {"text": "the ending"}],
                    }
                ],
            }
        )
        assert report["boundaries"][0]["safe_boundary"] == "Chapter 2"
        assert report["boundaries"][0]["exclusions"][1] == {
            "category": "general",
            "text": "the ending",
        }
        assert "the keeper" in report["combined_note"]
