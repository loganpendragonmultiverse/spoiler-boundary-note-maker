from __future__ import annotations

import json
from typing import Any

PROJECT = "spoiler-boundary-note-maker"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _spoiler_boundary(data: dict[str, Any]) -> dict[str, Any]:
    boundaries: list[dict[str, Any]] = []
    for item in _require(data, "works"):
        name = str(_require(item, "name"))
        through = str(_require(item, "through"))
        exclusions = [str(value) for value in item.get("exclude", [])]
        note = f"Safe through {name}: {through}."
        if exclusions:
            note += " Do not discuss " + ", ".join(exclusions) + "."
        boundaries.append({"name": name, "through": through, "exclude": exclusions, "note": note})
    return {
        "boundaries": boundaries,
        "combined_note": " ".join(item["note"] for item in boundaries),
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_spoiler_boundary(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.extend(
                [
                    f"## {key.replace('_', ' ').title()}",
                    "",
                    f"```json\n{json.dumps(value, indent=2, ensure_ascii=False, default=str)}\n```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
