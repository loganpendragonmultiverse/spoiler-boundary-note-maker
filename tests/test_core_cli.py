import json
from pathlib import Path

import pytest

from spoiler_boundary_note_maker.cli import main
from spoiler_boundary_note_maker.core import PROJECT, analyze, render_json, render_markdown


def test_representative_sample_has_expected_result():
    data = json.loads(
        (Path(__file__).parents[1] / "examples" / "sample.json").read_text(encoding="utf-8")
    )
    report = analyze(data)
    assert report["version"] == 2 and report["project"] == PROJECT
    assert "Do not discuss the lighthouse identity" in report["combined_note"]
    assert f'"project": "{PROJECT}"' in render_json(report)
    assert PROJECT.replace("-", " ").title() in render_markdown(report)


def test_missing_required_input_is_rejected():
    with pytest.raises(ValueError):
        analyze({})


def test_multi_person_safe_boundary_and_validation():
    report = analyze(
        {
            "preset": "public",
            "works": [
                {
                    "name": "Harbor",
                    "people": [
                        {"name": "A", "boundary_type": "chapter", "boundary": 8},
                        {"name": "B", "boundary_type": "chapter", "boundary": 5},
                    ],
                    "exclusions": [{"category": "identity", "text": "the keeper"}],
                }
            ],
        }
    )
    assert report["boundaries"][0]["safe_boundary"] == 5
    assert report["combined_note"].startswith("Spoiler-safe")
    with pytest.raises(ValueError, match="duplicate"):
        analyze({"works": [{"name": "A", "through": 1}, {"name": "a", "through": 2}]})
    with pytest.raises(ValueError, match="same type"):
        analyze(
            {
                "works": [
                    {
                        "name": "A",
                        "people": [
                            {"boundary_type": "chapter", "boundary": 1},
                            {"boundary_type": "episode", "boundary": 2},
                        ],
                    }
                ]
            }
        )
    with pytest.raises(TypeError, match="works"):
        analyze({"works": {}})
    with pytest.raises(TypeError, match="work 1"):
        analyze({"works": ["bad"]})
    with pytest.raises(ValueError, match="unsupported"):
        analyze({"works": [{"name": "A", "boundary_type": "page", "through": 2}]})
    with pytest.raises(ValueError, match="preset"):
        analyze({"preset": "secret", "works": [{"name": "A", "through": 1}]})


def test_cli_json_and_output_safety(tmp_path, capsys):
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    assert main([str(source), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["project"] == PROJECT
    output = tmp_path / "report.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2
