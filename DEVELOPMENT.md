# Development contract

Record precise safe-discussion boundaries across books, comics, shows, and games.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, changelog, README claims, repository metadata, release assets, and the Forge catalog together.

## 1.2.0 - 2026-10-16

Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. Keep regression fixtures synthetic and source inputs unchanged. `tests/test_feature_wave.py` covers the new behavior, malformed inputs and compatibility defaults. Verify README and CHANGELOG in wheel metadata/documentation and in the source archive before release. Protected cross-platform CI and CodeQL remain required; draft PR preparation does not authorize a merge or release.

## 1.2.1 acceptance

Run the full formatting, lint, strict typing, coverage and build checks above.
`tests/test_gold_validation.py` covers malformed input, successful fresh outputs,
existing files, dangling links where supported, and unchanged input bytes.
Install both built distributions outside the source tree and rerun the complete
suite against the installed package. Confirm all four handoff documents and the
license are present in the wheel/source distribution; exercise the installed CLI.
