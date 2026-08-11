# Contributing

Thanks for considering a contribution to agent-director-protocol. This is a
documentation-and-tooling repository — a protocol specification, two platform
adapters, and the schemas/scripts that keep them consistent — so most
contributions are edits to Markdown, YAML, or JSON, checked by the validation
scripts described below.

## Proposing a change

1. **Open an issue first for anything nontrivial** — a new failure reason, a
   new adapter, a schema field change, or anything that touches the
   canonical terminology in more than one file. Small, self-contained fixes
   (typos, broken links, a clarifying sentence) can go straight to a pull
   request.
2. **Fork and branch**, make your change, and run validation locally (below)
   before opening the PR.
3. **Open a pull request** describing what changed and why. Reference the
   issue it resolves, if any. Keep the PR scoped to one change — do not mix
   an adapter update with an unrelated core-doc wording fix.
4. A maintainer reviews the PR the same way this protocol asks a director to
   review an implementer's work: against evidence (the actual diff, the
   actual validation output), not against the PR description alone.

## Running validation locally

The single entry point is:

```
python scripts/check_repository.py
```

This requires Python 3.10+ and the `jsonschema` package:

```
pip install jsonschema
```

`check_repository.py` runs schema validation for every example JSON document,
skill/template structure checks, cross-file link resolution, and a
sensitive-data scan. It exits 0 only if everything passes.

Also run the unit test suite directly when working on the scripts themselves:

```
python -m unittest discover -s tests
```

CI (`.github/workflows/`) runs `scripts/check_repository.py` on every push
and pull request; a merge should not be expected before it passes locally.

## Style rules

- **No model names in `core/`.** The core protocol documents (`core/*.md`)
  use role names (`director`, `implementer`, `reviewer`) only. Model names
  (and model aliases) belong exclusively in `*/profiles/*.yaml` files.
- **Use the canonical terminology exactly.** Task IDs match `^T-[0-9]{3,}$`;
  the ten objective failure reasons and the ten review-check keys are fixed
  enums (see `core/FAILURE-LOOP.md` and `core/REVIEW-GATES.md`) — do not
  introduce free-text synonyms for them.
- **No unverifiable claims.** Do not add performance, quality, or
  cost-improvement percentages anywhere in the repository. Describe
  mechanisms ("the reviewer independently re-runs the test commands"), not
  outcomes you cannot ground in evidence.
- **No real personal data.** No real emails, usernames, or absolute local
  filesystem paths in any file. Use placeholder domains (e.g. `example.com`)
  and generic paths (`<project>`, `target-repo`) instead.
- **Every relative Markdown link must resolve.** `scripts/check_repository.py`
  verifies this; broken links fail validation.
- **Adapters must stay honest about platform capabilities.** `claude/` and
  `codex/` must describe what each platform's real mechanisms do and do not
  provide (see the "Differences" sections in each `INSTALL.md` and
  `SKILL.md`) rather than implying feature parity that does not exist. If a
  platform lacks something the other has (a native subagent registry, a
  built-in "active profile" concept, etc.), say so explicitly instead of
  glossing over it.

## Schema-first changes

Any change to the shape of a task contract, implementation report, review
result, failure-loop record, or takeover record starts in `schemas/`, then
propagates outward in this order:

1. **Update the schema** in `schemas/*.schema.json` (draft-07, snake_case
   fields).
2. **Update every example** under `examples/**/` that uses the changed
   document type, so every example JSON file still validates against the new
   schema.
3. **Update the reference templates** in `claude/skills/agent-director/references/`
   and `codex/skills/agent-director/references/` (both adapters carry the
   same four templates — task, review, revision, takeover — and must stay in
   sync with each other and with the schema).
4. **Update the narrating core doc** (`core/TASK-CONTRACT.md`,
   `core/REVIEW-GATES.md`, `core/FAILURE-LOOP.md`, or
   `core/TAKEOVER-PROTOCOL.md`) so the prose description matches the schema
   field-for-field.
5. **Update `README.md` and `README.ko.md`** if the change affects anything
   quoted or summarized there (e.g. the ten review-check keys, the ten
   failure reasons, or the complete conflict-domain set).

A schema change that lands without matching example, template, and doc
updates will fail `scripts/check_repository.py` and should not be merged.
Every example JSON document must validate against its schema at all times —
there is no "the docs will catch up later" state.

## Cutting a release

The repository is distributed as a Claude Code plugin, and Claude Code only
delivers an update to installed users when `version` in
`.claude-plugin/plugin.json` changes. Pushing commits without bumping it ships
nothing — installed users stay on their old copy and `/plugin update` reports
they are already current.

So a release is three steps, in order:

1. Move the accumulated `[Unreleased]` entries in `CHANGELOG.md` under a new
   `## [x.y.z] - YYYY-MM-DD` heading, and re-open an empty `[Unreleased]`.
2. Set `version` in `.claude-plugin/plugin.json` to the same `x.y.z`.
   `tests/test_skill_structure.py` enforces this match, so a mismatch fails
   CI rather than silently shipping nothing.
3. Tag the release commit (`git tag -a vx.y.z`) and push the tag, then publish
   a GitHub Release with the changelog section as its notes.

Update `SECURITY.md`'s supported-versions table in the same commit when the
supported line moves.

## Adding a new platform adapter

If you propose a third adapter (beyond Claude Code and Codex), follow the
existing two as the pattern: a directory with `skills/agent-director/SKILL.md`
plus `references/`, an example project-instructions file (like
`CLAUDE.md.example` / `AGENTS.md.example`), at least one model profile under
`profiles/`, and an `INSTALL.md`. The adapter must link to `core/` for every
rule instead of restating it, and must be explicit about where the new
platform's native mechanisms end and this protocol's conventions begin.

## Code of conduct

Participation in this project is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
