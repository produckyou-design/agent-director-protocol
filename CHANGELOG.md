# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-08-06

### Added

- **State Safety** (`core/STATE-SAFETY.md`, new — `core/` grows from 10 to 11
  documents): the working-state discipline every other document already assumed
  but none stated. A last-passing checkpoint must be established (as a real
  commit SHA or tag) before the first dispatch; **a failed attempt's changes may
  not be destroyed before the director has reviewed them**, since that diff is
  the evidence the revision instruction, Rescue Agent package, and takeover
  record all depend on; implementers do not commit to the main line (integration
  is the director's step); destructive operations — force-push or history
  rewrite of a pushed branch, deleting the only copy of work, discarding the
  checkpoint — are deliberate, stated decisions rather than incidental steps;
  and concurrent implementers get isolated working copies because the
  conflict-domain check covers intended changes only.
- **Partial batch failure handling** (`core/CONCURRENCY-RULES.md`): what happens
  when some tasks in a parallel batch pass and others fail. Passing tasks
  integrate on their own evidence (unless they `depends_on` a failed task, in
  which case they are held and re-reviewed); each failed task runs its own
  failure loop with its own count — **failures do not pool across tasks**;
  integration follows dependency order, not completion order. If the failure
  reveals the batch's underlying *design* was wrong, the director stops
  integrating and returns to design. User interruption mid-batch requires
  reporting what completed, what was in flight, and where each state is
  preserved.

### Fixed

- **Dangling reference**: `core/RESCUE-PROTOCOL.md` rule 6 cited "git safety
  rules elsewhere in this protocol" that did not exist anywhere in `core/`. It
  now points at the new `STATE-SAFETY.md`, and the checkpoint-preservation step
  in Step 2 links there as well.

### Changed

- `core/ROLE-CONTRACT.md` (director integration duty, implementer reporting and
  no-commit-to-main-line duties) and `core/DELEGATION-PROTOCOL.md` step 7
  (establish the checkpoint before the first dispatch) now reference
  `STATE-SAFETY.md`.
- Both platform adapters' `SKILL.md` gain a "State safety (git discipline)"
  section and batch-failure handling; the Codex adapter states explicitly that
  concurrent workers need explicit `git worktree add` isolation, since Codex has
  no native worktree mechanism.
- `README.md` / `README.ko.md`: new "State safety" section, batch-failure
  paragraph under parallel work rules, and updated repository-layout tree.

## [0.2.0] - 2026-08-06

### Added

- **Escalation Protocol** (`core/ESCALATION-PROTOCOL.md`, new): a mid-task
  request mechanism for a stuck implementer or director to ask for more
  reasoning power *before* guessing a third time — `EFFORT_ESCALATION_REQUEST`
  / `MODEL_ESCALATION_REQUEST` (implementer → director) and
  `DIRECTOR_ESCALATION_REQUEST` (director → user). Neither role ever changes
  its own model or effort; a request is granted only after the requester's
  evidence is independently checked.
- **Rescue Protocol** (`core/RESCUE-PROTOCOL.md`, new): replaces the previous
  "two failed loops → director takes over" default. After two counted
  failures, the director now classifies the cause
  (`diagnosis_gap` / `reasoning_gap` / `model_capability_gap` /
  `requirement_conflict` / `environment_issue` / `rollback_needed`); only a
  genuine reasoning or model-capability gap earns a bounded, one-shot
  **Rescue Agent** promotion (≤2 attempts, isolated checkpoint, explicit
  `forbidden_scope`) before director takeover becomes reachable at all.
  Director direct coding remains the last resort, gated by the same
  takeover-record requirement as before.
- **Mandatory disclosure/notification schemas**: three new JSON Schemas make
  the "never silent" requirement checkable —
  `agent-composition-disclosure.schema.json` (who's about to run, stated
  before any spawn), `promotion-notice.schema.json` (why a task is being
  promoted, doubling as an approval request outside the pre-approved
  model/effort range), and `rescue-outcome-notice.schema.json` (what
  happened, including whether the team reverted to its normal tier).
- **Escalation request schemas**: `escalation-request.schema.json` and
  `director-escalation-request.schema.json`.
- **`rescue-agent-task.schema.json`**: the bounded scope package (prior
  attempts, last-passing checkpoint, editable/forbidden scope, attempt limit)
  handed to a Rescue Agent.
- **Per-task-kind reasoning effort**: `implementer.effort_by_task_kind` added
  to all three model profiles (`opus-director.yaml`, `fable-director.yaml`,
  `sol-director.yaml`) — investigation/audit default to `high`,
  implementation/pipeline to `medium`, mechanical work to `low`. The director
  must set this explicitly on every spawn rather than inheriting a session
  default.
- **Agent-composition disclosure step**: `DELEGATION-PROTOCOL.md` step 7 now
  requires disclosing the full spawn plan (director model/effort, each
  subagent's role/task/model/effort, parallel or sequential, Rescue Agent
  availability) before any implementer is spawned for a batch.
- Three new reference templates per platform adapter (`claude/`, `codex/`):
  `escalation-template.md`, `rescue-agent-template.md`,
  `agent-briefing-template.md` — bringing each adapter's reference set from
  four templates to seven.
- `core/` grows from 8 to 10 documents; `schemas/` from 5 to 11.
- **Configurable failure threshold**: `implementer.failure_threshold` (new profile field,
  default 2) replaces the hardcoded "two failed loops" count referenced across
  `FAILURE-LOOP.md`, `ESCALATION-PROTOCOL.md`, `RESCUE-PROTOCOL.md`, and
  `TAKEOVER-PROTOCOL.md`. `codex/profiles/sol-director.yaml` raises it to 3, since a
  `codex exec` worker run is cheap enough that one extra evidence-based attempt costs
  little before promoting.
- **Escalate one axis at a time**: a Rescue Agent's first attempt now raises only the
  axis matching the Step 1 classification — `model_capability_gap` bumps the model and
  holds effort fixed; `reasoning_gap` bumps effort and holds the model fixed. Only a
  failed first attempt adds the other axis on attempt 2. A director may still assign
  both axes on attempt 1 when the evidence makes staging clearly unnecessary, but must
  say so in `promotion_reason`.
- **`requirement_conflict` gets its own default path**: instead of falling into
  `RESCUE-PROTOCOL.md` Step 3's generic five options, the director now revises the task
  contract and re-delegates (ordinary re-planning, self-escalating first if confidence
  is low or the risk is architectural/security/deployment/data-loss). Step 3 applies
  only if that revised contract also fails.
- **Agent-spawn volume controls**, addressing a real over-delegation pattern (too many
  subagents dispatched for the actual scope of work):
  - **Decomposition minimality** (`DELEGATION-PROTOCOL.md` step 4): the director now
    defaults to the fewest tasks that satisfy the verifiable-unit rule. Splitting
    further requires a stated reason — parallelism benefit, a distinct effort/model
    tier, blast-radius isolation, or genuinely independent outcomes — not "smaller
    diffs" or "tidier task IDs."
  - **Per-subagent `justification`** (new required field on
    `agent-composition-disclosure.schema.json`'s `subagents[]` items): every disclosed
    subagent must state why it needs its own slot rather than folding into another task
    in the same batch.
  - **`director.max_batch_agents`** (new profile field, default 4): above this many
    subagents in one disclosed batch, the agent-composition disclosure also becomes an
    approval request (`within_preapproved_range` / `approval_status`, mirroring the
    Rescue Agent promotion pattern) — dispatch waits for the user to grant it. A
    conflict-free batch is still subject to this cap; `CONCURRENCY-RULES.md` gates
    safety, not size.
  - **Implementers cannot spawn subagents** (`ROLE-CONTRACT.md`): an explicit
    containment boundary — an implementer that judges a task needs further splitting
    reports that back to the director as an out-of-scope finding instead of acting on
    it. This closes the main path by which a correctly-sized, disclosed batch could
    silently multiply past what the user approved.

### Changed

- `core/TAKEOVER-PROTOCOL.md` condition (b) now requires the Rescue Protocol
  to have run its course (promotion tried and failed, or classified as
  inapplicable) — "two failed loops" alone no longer authorizes takeover.
- `core/ROLE-CONTRACT.md` and `core/DELEGATION-PROTOCOL.md` updated to
  reference the Rescue Agent and disclosure requirements; a Rescue Agent is
  explicitly clarified as filling the implementer role, not a fourth role.
- Both platform adapters' `SKILL.md` rewritten: "Failure loop and takeover"
  replaced by "Failure loop → Rescue Agent → takeover (in that order)"; new
  "Escalation" section; new agent-composition-disclosure step in the
  delegation sequence.
- `README.md` / `README.ko.md`'s "Parallel work rules" section now spells out
  the four concrete reasons for splitting into more than one subagent, and
  the "Bad usage" list gains two entries: over-decomposition and an
  implementer spawning its own subagents.
- `SECURITY.md` supported-versions table updated to `0.2.x`.

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
