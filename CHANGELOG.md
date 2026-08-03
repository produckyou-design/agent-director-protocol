# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-03

Initial release.

### Added

- **Core protocol** (`core/`): platform-neutral specification of the
  director / implementer / reviewer roles and the full delegation lifecycle —
  `ROLE-CONTRACT.md`, `DELEGATION-PROTOCOL.md`, `TASK-CONTRACT.md`,
  `FAILURE-LOOP.md`, `REVIEW-GATES.md`, `CONCURRENCY-RULES.md`,
  `TAKEOVER-PROTOCOL.md`, `COMPLETION-STANDARD.md`.
- **JSON Schemas** (`schemas/`, draft-07): `task-contract.schema.json`,
  `implementation-report.schema.json`, `review-result.schema.json`,
  `failure-loop.schema.json`, `takeover-record.schema.json`.
- **Claude Code adapter** (`claude/`): `skills/agent-director/SKILL.md` and
  its four reference templates (task, review, revision, takeover),
  `CLAUDE.md.example`, model profiles (`opus-director.yaml`,
  `fable-director.yaml`), and `INSTALL.md`.
- **OpenAI Codex adapter** (`codex/`): `skills/agent-director/SKILL.md` and
  its four reference templates, `AGENTS.md.example`, model profile
  (`sol-director.yaml`), and `INSTALL.md`.
- **Worked examples** (`examples/`): four schema-valid, end-to-end scenarios —
  `python-project` (greenfield happy path), `web-project` (one revision
  loop), `existing-codebase` (two failed loops leading to takeover), and
  `new-project` (parallel task dispatch with a conflict-domain check).
- **Validation tooling** (`scripts/`, `tests/`): schema validation, skill and
  template structure checks, cross-file link resolution, a sensitive-data
  scan, and a Python `unittest` suite, all runnable through the single entry
  point `scripts/check_repository.py`.
- **CI** (`.github/workflows/`): runs `scripts/check_repository.py` on every
  change.
- Root documentation: this changelog, `LICENSE` (MIT), `CONTRIBUTING.md`,
  `SECURITY.md`, `CODE_OF_CONDUCT.md`, `README.md`, and the Korean
  translation `README.ko.md`.
