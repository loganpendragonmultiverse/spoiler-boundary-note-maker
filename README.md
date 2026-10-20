# Spoiler Boundary Note Maker

[![CI](https://github.com/loganpendragonmultiverse/spoiler-boundary-note-maker/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/spoiler-boundary-note-maker/actions/workflows/ci.yml)

Record precise safe-discussion boundaries across books, comics, shows, and games. The command uses explicit UTF-8 JSON input and produces reviewable JSON or Markdown output.

## Three-minute start

```bash
python -m pip install .
spoiler-boundary examples/sample.json
spoiler-boundary examples/sample.json --format json --output report.json
```

The example documents the v1 input shape. Existing report files are never overwritten. Source inputs are read-only except where the documented purpose explicitly creates a new output artifact.

Version 1.1 also accepts a `people` list on each work. Give every person a `name`, matching `boundary_type`, and numeric `boundary`; the report selects the earliest mutually safe point. Supported types are chapter, issue, episode, season, quest, and timestamp. Categorized `exclusions` and `friends`, `public`, or `private` sharing presets make the generated note fit its audience. The original `through` and `exclude` shape remains supported.

## Privacy and platforms

The tool runs locally and does not upload input or include telemetry. Python 3.10 or newer is supported on Windows, macOS, and Linux.

## Interpretation boundary

The note is only as safe as the supplied boundaries. It cannot inspect conversations or know which details count as spoilers.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

Release metadata must stay aligned across the package, changelog, GitHub release, and Logan Pendragon Forge catalog.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## 1.2.0 - 2026-10-16

For named boundaries, declare an explicit earlier-to-later `milestones` list on the work, for example `"milestones":["Opening","Arrival","Finale"]`, and set each person's `boundary` to one of those exact strings. All participants must use the same supported boundary type. Selection is independent of participant order. Empty, duplicate or unknown labels and mixed numeric/named boundaries fail closed; without a milestone list, multiple-person boundaries must be finite numbers. Booleans, NaN and infinity are rejected. Valid numeric comparison and the original single `through` text note remain supported. Unused future milestone labels are not copied into reports.

The `public` preset changes note wording only. JSON retains participant names and supplied boundaries, including participants who are further ahead; it does not anonymize them or redact their submitted details. Review reports before sharing.

## 1.2.1 validation and output safety

Work names, supplied participant names, and exclusion text/categories must be
non-empty strings; malformed JSON structures produce an actionable error. Output files are created exclusively:
existing files and symbolic links are rejected, including dangling links. This
checks an existing output leaf and creates files exclusively; it is not an
atomic defense against hostile leaf or parent-path replacement during the command. Inputs remain read-only.

`examples/shared-milestones.json` demonstrates ordered named boundaries,
participants at different points, and categorized exclusions.
