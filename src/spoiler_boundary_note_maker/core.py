from __future__ import annotations

import json
import math
from typing import Any

PROJECT = "spoiler-boundary-note-maker"
BOUNDARY_TYPES = {"chapter", "issue", "episode", "season", "quest", "timestamp"}


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TypeError("input must be a JSON object")
    works = _require(data, "works")
    if not isinstance(works, list):
        raise TypeError("works must be a list")
    boundaries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(works, 1):
        if not isinstance(item, dict):
            raise TypeError(f"work {index} must be an object")
        raw_name = _require(item, "name")
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ValueError(f"work {index} name must be non-empty text")
        name = raw_name.strip()
        key = name.casefold()
        if key in seen:
            raise ValueError(f"duplicate work: {name}")
        seen.add(key)
        people = item.get("people")
        legacy = people is None
        if people is None:
            boundary_type = str(item.get("boundary_type", "chapter"))
            value = item.get("boundary", item.get("through"))
            people = [{"name": "shared", "boundary_type": boundary_type, "boundary": value}]
        if not isinstance(people, list) or not people:
            raise ValueError(f"work {name} requires people boundaries")
        normalized = []
        for person in people:
            if not isinstance(person, dict):
                raise TypeError("people boundaries must be objects")
            kind = str(person.get("boundary_type", item.get("boundary_type", "chapter")))
            if kind not in BOUNDARY_TYPES:
                raise ValueError(f"unsupported boundary type: {kind}")
            value = person.get("boundary", person.get("through"))
            if value is None or value == "":
                raise ValueError(f"{name} has a missing boundary")
            person_name = person.get("name", "reader")
            if not isinstance(person_name, str) or not person_name.strip():
                raise ValueError("participant name must be non-empty text")
            normalized.append(
                {
                    "name": person_name.strip(),
                    "boundary_type": kind,
                    "boundary": value,
                }
            )
        kinds = {person["boundary_type"] for person in normalized}
        if len(kinds) != 1:
            raise ValueError(f"{name} boundaries must use the same type")
        values = [person["boundary"] for person in normalized]
        milestones = item.get("milestones")
        if milestones is not None:
            if (
                not isinstance(milestones, list)
                or not milestones
                or any(not isinstance(label, str) or not label.strip() for label in milestones)
                or len(set(milestones)) != len(milestones)
            ):
                raise ValueError("milestones must be an ordered unique non-empty string list")
            if any(not isinstance(value, str) or value not in milestones for value in values):
                raise ValueError("boundaries must name declared milestones")
            safe = min(values, key=milestones.index)
        elif legacy and isinstance(values[0], str) and values[0].strip():
            safe = values[0]
        else:
            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or isinstance(value, float)
                and not math.isfinite(value)
                for value in values
            ):
                raise ValueError("boundaries require finite numbers or ordered named milestones")
            safe = min(values)
        exclusions = item.get("exclusions", item.get("exclude", []))
        if not isinstance(exclusions, list):
            raise TypeError("exclusions must be a list")
        categorized = []
        for exclusion in exclusions:
            category: Any
            text: Any
            if isinstance(exclusion, str):
                category, text = "general", exclusion
            elif isinstance(exclusion, dict):
                category = exclusion.get("category", "general")
                text = exclusion.get("text")
            else:
                raise TypeError("exclusions must contain text or category/text objects")
            if (
                not isinstance(category, str)
                or not category.strip()
                or not isinstance(text, str)
                or not text.strip()
            ):
                raise ValueError("exclusion category and text must be non-empty text")
            categorized.append({"category": category, "text": text})
        note = (
            f"Safe through {name}: {safe}."
            if legacy
            else f"Safe through {name}: {next(iter(kinds))} {safe}."
        )
        if categorized:
            if legacy:
                note += (
                    " Do not discuss "
                    + ", ".join(str(x.get("text", "")) for x in categorized)
                    + "."
                )
            else:
                note += (
                    " Avoid "
                    + "; ".join(
                        f"{x.get('category', 'general')}: {x.get('text', '')}" for x in categorized
                    )
                    + "."
                )
        boundaries.append(
            {
                "name": name,
                "boundary_type": next(iter(kinds)),
                "safe_boundary": safe,
                "people": normalized,
                "exclusions": categorized,
                "note": note,
            }
        )
    preset = str(data.get("preset", "friends"))
    combined = " ".join(item["note"] for item in boundaries)
    if preset == "public":
        combined = "Spoiler-safe discussion boundary: " + combined
    elif preset == "private":
        combined = "Private boundary details: " + combined
    elif preset != "friends":
        raise ValueError("preset must be friends, public, or private")
    return {
        "version": 2,
        "project": PROJECT,
        "preset": preset,
        "boundaries": boundaries,
        "combined_note": combined,
    }


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Spoiler Boundary Note Maker", "", report["combined_note"], "", "## Boundaries", ""]
    for item in report["boundaries"]:
        lines.append(f"- **{item['name']}**: {item['boundary_type']} {item['safe_boundary']}")
        for exclusion in item["exclusions"]:
            lines.append(
                f"  - Avoid ({exclusion.get('category', 'general')}): {exclusion.get('text', '')}"
            )
    return "\n".join(lines).rstrip() + "\n"
