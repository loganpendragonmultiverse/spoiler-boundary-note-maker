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

The project is feature-complete for its documented v1 scope. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).
