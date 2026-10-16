import json

import pytest

from spoiler_boundary_note_maker.cli import main
from spoiler_boundary_note_maker.core import analyze, render_markdown


def payload(values, milestones=None):
    work = {
        "name": "Harbor",
        "people": [
            {"name": str(i), "boundary_type": "quest", "boundary": v} for i, v in enumerate(values)
        ],
    }
    if milestones is not None:
        work["milestones"] = milestones
    return {"works": [work]}


def test_named_order_and_future_labels(tmp_path, capsys):
    for values in [["Opening", "Arrival"], ["Arrival", "Opening"]]:
        result = analyze(payload(values, ["Opening", "Arrival", "FUTURE_CANARY"]))
        assert result["boundaries"][0]["safe_boundary"] == "Opening"
        assert "FUTURE_CANARY" not in json.dumps(result) + render_markdown(result)
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload(["Arrival", "Opening"], ["Opening", "Arrival"])))
    assert main([str(path), "--format", "json"]) == 0
    assert "Opening" in capsys.readouterr().out


@pytest.mark.parametrize(
    "values,milestones",
    [
        (["A", "B"], None),
        (["A", "B"], ["B", "B"]),
        (["A", "B"], ["A", ""]),
        (["A", "C"], ["A", "B"]),
        (["A", 2], ["A", "B"]),
        ([True, 2], None),
        ([float("nan"), 2], None),
        ([float("inf"), 2], None),
        (["A", "B"], {}),
        (["A", "B"], ["A", 1]),
        (["A", "B"], []),
    ],
)
def test_fail_closed(values, milestones, tmp_path, capsys):
    data = payload(values, milestones)
    with pytest.raises((TypeError, ValueError)):
        analyze(data)
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data))
    assert main([str(path)]) == 2
    assert "error:" in capsys.readouterr().err


def test_numeric_compatibility():
    assert analyze(payload([8, 3.5]))["boundaries"][0]["safe_boundary"] == 3.5


def test_large_finite_integer_compatibility():
    assert analyze(payload([10**400, 3.5]))["boundaries"][0]["safe_boundary"] == 3.5
