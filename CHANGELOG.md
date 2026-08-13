# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Worker contracts now require explicit execution criteria.** Before a
  subagent is created, the root/current parent Director must assign a valid
  non-Director role and provide worker-specific `goal`, `success_criteria`,
  `failure_criteria`, `termination_criteria`, and `required_evidence` fields,
  in addition to scope and non-goals. A spawned subagent is never a Director
  under any circumstance; missing or ambiguous role/criteria is a pre-spawn
  failure.
- **Worker role boundaries are now explicit.** Each task tree has exactly one
  Director (the root/current parent session); spawned workers and reviewers
  treat the parent Director's Task Contract as authoritative and cannot
  reactivate Director mode, publish root-level disclosures, re-decompose or
  integrate the parent task, spawn/manage workers, or declare the overall task
  complete. Contracted deployments and other state-changing operations remain
  allowed when explicitly included in the parent contract.
- **ADP is now the default for Codex repository and code tasks.** The skill can
  still be invoked explicitly, but model/effort exceptions remain user-
  authorized and fail-closed.
- **Codex worker capacity is runtime-defined.** The adapter no longer invents a
  concurrent or cumulative numeric cap. Directors disclose the planned worker
  structure and evidence-based rationale before spawning; native slot-full
  responses require wait/close, re-scope, or return and never authorize
  Director takeover.
- **Every task now has an explicit disclosure phase.** `task_start` begins
  every task, `spawn` precedes a worker batch, and `addition` is required for
  later workers, contracts, revisions, rescues, reviewers, or material scope
  changes. Addition notices must explain the changed scope, assigned work,
  classified reason, and why an existing worker cannot absorb it.
- **Parallel dispatch is now deterministic.** A parallel batch requires at
  least two independently verifiable work groups, pairwise-disjoint conflict
  domains, no cross-group dependency edges, isolated write state, and observed
  native capacity. The work contract records `independent_groups`,
  `conflict_domains`, `dependency_edges`, `planned_workers`,
  `capacity_source`, `write_isolation`, and `why_fewer_workers_cannot_absorb`;
  known capacity of at least two uses `min(group count, observed capacity)`,
  while unknown or lower capacity falls back to one sequential worker without
  inventing a cap. The semantic dispatch validator checks domain/glob overlap
  and the capacity formula after schema validation. Speed or efficiency is an
  outcome/optional latency priority only and never overrides conflicts,
  dependencies, capacity, or the no-automatic-takeover rule.

## [0.8.6] - 2026-08-12

Parallel worker selection is now deterministic instead of treating parallelism
as categorically invalid or relying on vague speed justifications.

### Changed

- Parallel execution requires at least two independently verifiable groups,
  pairwise-disjoint conflict domains, empty dependency edges, isolated writes,
  and observed native capacity of at least two.
- `planned_workers` is the smaller of the eligible independent-group count and
  observed capacity; shared or sequential domains use one worker, and unknown
  capacity falls back conservatively to one sequential worker.
- Speed and efficiency are recorded as outcomes or explicit user latency
  priorities only; they never override conflict, dependency, isolation, or
  capacity checks.

## [0.8.5] - 2026-08-11

Worker recovery now treats wait timeouts as observations and requires explicit
progress or fatal-runtime evidence before interrupting or closing a native
worker.

### Fixed

- Native `RUNNING`, progressing, active-command, completed-but-unreported, and
  unknown states are preserved and distinguished instead of being inferred from
  file changes or a wait timeout.
- The first timeout records an observation and defaults to another bounded wait;
  interrupt is limited to explicit fatal evidence or a declared no-progress
  window, with one bounded post-interrupt close path.
- The one permitted interrupt now tells the worker to stop current work,
  summarize only secured evidence, start no new work/tests/edits, and exit.

## [0.8.4] - 2026-08-11

Worker recovery now distinguishes non-final work from a genuine native stall.

### Fixed

- A wait timeout no longer authorizes interrupt, close, splitting, or re-dispatch.
- Progress, active long-running commands, completed-but-unreported work, stalled
  workers, and unknown native telemetry now have separate states.
- Recovery acts only on a no-progress stall within the declared observation window.

## [0.8.3] - 2026-08-11

The Codex adapter now fails closed after worker and Rescue failures.

### Fixed

- Director takeover is no longer automatic after implementer or Rescue failure.
- Direct product-code takeover requires explicit current-session user authorization,
  a takeover disclosure and record, and independent review.
- Takeover records now carry explicit user-authorization evidence.

## [0.8.2] - 2026-08-11

The Codex adapter now handles native worker lifecycle failures explicitly.

### Fixed

- Worker timeout, interrupt, close/resume, and fork integration states are now fail-closed.
- Pre-spawn serialization failures are separated from implementation failures.
- Rescue is blocked when the active Luna/max baseline has no effort headroom.

## [0.8.1] - 2026-08-11

The Codex adapter now enforces the Director/implementer boundary for state-changing work.

### Fixed

- The Director cannot directly implement ordinary product-code or state-changing tasks.
- Shared-file conflicts now require a sequential implementer instead of silently using zero workers.

## [0.8.0] - 2026-08-09

The Codex adapter now treats explicit Director-mode activation as a fixed,
fail-closed worker dispatch policy.

### Changed

- **Every ADP native worker spawn is explicit.** After `$agent-director` or
  "Director mode on", the Director must pass
  `model="gpt-5.6-luna"` and
  `reasoning_effort="max"` on every spawn; the Director remains
  user-selected.
- **Named profiles and defaults are defense in depth.** The adapter prefers no
  named custom agent/type and verifies any selected profile is pinned to the
  same pair.
- **Worker acceptance is fail-closed.** Returned/runtime metadata is checked
  when exposed; mismatched workers are rejected/closed and unverifiable
  surfaces stop with a policy-violation/fallback report.
- **Rescue is unavailable at the max baseline.** Existing Core escalation and
  takeover gates remain the next path, with no silent model or effort change.
- **Codex role templates, project defaults, install guidance, plugin metadata,
  and regression guards are synchronized to Luna/max.**

## [0.7.0] - 2026-08-09

The Codex adapter now targets native multi-agent workflows instead of treating
`codex exec` and a project-local YAML alias as the primary runtime model.

### Changed

- **Native Codex delegation is the default.** The main user-selected Codex
  session is the director; native subagent threads are the normal worker path,
  while `codex exec` is reserved for non-interactive, CI, process-isolated, or
  native-unavailable work.
- **Real Codex project configuration is supplied.** The adapter now documents
  `.codex/config.toml` `[agents]` keys, four simultaneous threads, and
  `.codex/agents/*.toml` role files for investigator, implementer, reviewer,
  rescue, and release auditing.
- **Worker policy is explicit.** Normal delegated workers use the GPT-5.6 Luna
  ceiling; effort is selected by task kind and Rescue raises effort only on the
  same model. The director model is never silently inherited or changed.
- **Contracts and disclosures carry execution evidence.** Task Contracts now
  record delegation metadata and conflict domains; implementation reports
  record the assigned worker settings; reviews record their context; and the
  examples, templates, schemas, and Core rules are synchronized.
- **Installation documentation no longer implies a hidden mode switch.** It
  explains the actual `AGENTS.md`/skill/configuration setup and the need to
  start a new task or explicitly reread instructions after installation.

## [0.6.1] - 2026-08-07

Follow-through on 0.6.0. Removing the model axis from the Rescue Agent left three
things stale or newly load-bearing; this release fixes them.

### Fixed

- **The director must not review its own work.** `TAKEOVER-PROTOCOL.md` previously
  told the director to review its own takeover diff "with the same rigor as if an
  implementer had produced it" — an instruction, not a control. The context that
  produced a change also produced the reasoning for why it is correct, so it cannot
  supply the adversarial pressure the ten gates assume. Director-authored diffs now
  go to a **separate reviewer agent at the director's own model and reasoning
  effort, from a fresh context**. Ordinary implementer reviews are unchanged: a
  different agent with a different context is already independent, so the director
  performs those directly. New `ROLE-CONTRACT.md` section, referenced from
  `REVIEW-GATES.md` and `TAKEOVER-PROTOCOL.md`, with `reviewer.independent_for_director_authored_work`
  in the profile.
- **The no-direct-work rule now covers execution, not just authorship.**
  `ROLE-CONTRACT.md` said only that the director must not *write* product code, so
  running a deployment, applying a migration, or executing a release pipeline fell
  outside it — nothing contracted, nothing reviewed, and an evidence trail consisting
  of whatever the director reported about itself. State-changing operations are now
  delegated like any other work. Read-only inspection (reading logs, checking status,
  re-running tests to verify a report) is explicitly still part of reviewing.
- **README claim corrected.** Both READMEs said a secondary effect was that "the
  expensive model spends its turns on design and review instead of mechanical edits."
  With the implementer on the same tier as the director that is no longer true. The
  real, still-true benefit is stated instead: the director's context stays on design
  and review rather than filling with file contents and test output, and each
  implementer works from a clean context scoped to one task. The stale "a stronger
  model or higher reasoning effort" description of a Rescue Agent was corrected in the
  same pass.

### Changed

- `claude/profiles/default.yaml`: `implementer.preferred_models` is now a **single**
  entry, `[opus-5]`. Nothing in the protocol selects between list entries — a Rescue
  Agent only raises effort, and a model change is a user decision — so a two-entry
  list left a director guessing which to use with no rule to consult. To run cheaper,
  swap the alias wholesale. `codex/profiles/sol-director.yaml` is untouched.
- The `mechanical` effort tier gained a real definition rather than examples: the
  contract fully determines the change **and** a command verifies it; if the
  implementer has to decide anything, it is not mechanical. Also notes that `low`
  leaves the most room to climb, and that a "mechanical" task needing high effort is
  a misclassification signal rather than a reason to raise the default.

## [0.6.0] - 2026-08-07

Supersedes the escalation design shipped hours earlier in 0.5.0. That release made
reasoning effort the *first* axis but still let a Rescue Agent reach for a stronger
model on its second attempt; in review that left the model axis as an automatic
promotion path, which is the behavior this protocol is supposed to prevent. The model
axis is now removed from the Rescue Agent entirely.

### Changed

- **The Rescue Agent now raises reasoning effort only — it never swaps the
  implementer's model.** In 0.5.0 attempt 1 raised effort and attempt 2 added a
  stronger model. Both attempts now climb the effort ladder on the model already in use
  (e.g. `medium` → `high` → `xhigh`). Effort is a per-call parameter that reliably
  applies, it is the cheaper lever, and — decisively — auto-promoting to a
  higher-priced tier is the "throw the biggest model at everything" reflex this
  protocol exists to prevent. A model change is now always a user decision.
  The Step 1 classification survives, but it decides **how far to climb before
  handing off** rather than which axis to use: `reasoning_gap` uses both attempts,
  `model_capability_gap` uses one to confirm and then escalates.
- **When the effort ladder is exhausted, the protocol escalates the *director*, not
  the implementer.** Repeated implementation failure at high effort is evidence about
  the plan rather than the coder, so `RESCUE-PROTOCOL.md` Step 3's "escalate to the
  user" is now the *default* choice at that point, and the request asks to raise the
  director's own model and reasoning effort. New director self-escalation trigger in
  `ESCALATION-PROTOCOL.md` covers it.
- **A granted director escalation re-judges and re-contracts.** New
  `ESCALATION-PROTOCOL.md` section "An upgraded director re-judges, then
  re-contracts": the upgraded director does not hand the same task contract back to a
  new implementer — re-running an unchanged specification at a higher director tier
  changes nothing about the specification the implementer kept failing against, and
  that specification is the leading suspect. It re-examines the blocked task on its
  own judgment (not as an edit to its predecessor's), then issues a **revised task
  contract** delegated as a fresh task with its own failure-loop count.
  `current_state`, `target_behavior`, `completion_criteria`, and the file scope are
  all open to change; the rest of the task tree and `forbidden_scope` stay untouched.
- Correspondingly `EFFORT_ESCALATION_REQUEST` is the default request type and the
  only one a director can grant alone; `MODEL_ESCALATION_REQUEST` is forwarded to the
  user as a `DIRECTOR_ESCALATION_REQUEST`. Updated `core/RESCUE-PROTOCOL.md`,
  `core/ESCALATION-PROTOCOL.md`, both platform `SKILL.md` files (including the Codex
  `codex exec -c` command examples, which no longer pass `-c model=...`), both
  `escalation-template.md` references, and both READMEs.
- Profile effort tables gained a note that the default tier must leave **headroom**:
  effort is now the only ladder a stuck task can climb, so starting an implementer at
  its model's top tier means there is nothing left to escalate to.

## [0.5.0] - 2026-08-07

### Changed

- **Escalation raises reasoning effort before reaching for a stronger model.**
  Previously the first Rescue Agent attempt raised whichever axis matched the Step 1
  classification, so a `model_capability_gap` jumped straight to a bigger model.
  Effort became the first lever in both cases: attempt 1 keeps the failed
  implementer's model and raises effort, attempt 2 adds the stronger model.
  (Superseded by 0.6.0, which removes the model axis from the Rescue Agent
  altogether.) `EFFORT_ESCALATION_REQUEST` became the default request type.
- **Implementer profiles list a higher-capability tier first, with the reason stated
  as a principle rather than a benchmark.** `claude/profiles/default.yaml` now has
  `implementer.preferred_models: [opus-5, sonnet-5]`. The accompanying guidance —
  in the profiles and in both READMEs' "Configuration & model profiles" section —
  says to measure **cost per completed task, not per token**: a cheaper-per-token
  model that needs more steps, retries, and supervision can cost more to finish the
  same work, and a capable model at a modest effort tier is often the efficient
  point. Deliberately no benchmark numbers or prices: those depend on the workload
  and change over time, and this repository does not publish figures it cannot
  verify. Readers are told to sweep tiers and effort levels on their own tasks.

## [0.4.1] - 2026-08-06

### Changed

- **Merged `claude/profiles/opus-director.yaml` and `fable-director.yaml`
  into one `claude/profiles/default.yaml`.** The split implied you had to
  "pick a director model" by choosing a file, but the director was never
  determined by the profile — it is always whichever model is running the
  current session, and switching models with `/model` changes the director
  live, with no file to update. The two files differed only in
  `director.preferred_models`, a non-enforced hint; everything that actually
  matters operationally (`max_batch_agents`, `failure_threshold`,
  `effort_by_task_kind`) was identical between them. `default.yaml` now lists
  both tiers as recommendations and states explicitly what the profile is and
  is not for.
- `claude/INSTALL.md` ("Selecting a model profile" → "The default profile"),
  `claude/CLAUDE.md.example`, and both READMEs' "Configuration & model
  profiles" sections rewritten to match — the previous wording ("use
  `profiles/opus-director.yaml` for this project") asked users to designate a
  profile with no guidance on which one or why, which was the actual
  friction: a director with no profile reference in `CLAUDE.md` had no
  concrete source for `max_batch_agents` at all.
- `.claude-plugin/plugin.json` version 0.4.0 → 0.4.1.



- `.github/workflows/validate.yml`: `actions/checkout@v4` → `v5`,
  `actions/setup-python@v5` → `v6` — both were running on a Node.js 20 runtime
  GitHub Actions flagged as deprecated (forced onto Node 24 in the meantime,
  so this was cosmetic, not a functional break).

### Fixed

- Install docs gave `/plugin update agent-director`, which fails with
  `Plugin "agent-director" not found` even when installed — verified against a
  real install. The fully qualified `agent-director@agent-director-protocol`
  is required, and updating needs a restart to take effect. Also documented
  that a pre-existing manual copy under `~/.claude/skills/` is refused as a
  duplicate name once the plugin is installed, so it must be removed rather
  than left in place silently not loading.

## [0.4.0] - 2026-08-06

### Added

- **Installable as a Claude Code plugin, with updates.** New
  `.claude-plugin/marketplace.json` at the repository root makes the repo a
  plugin marketplace, so it can be installed with
  `/plugin marketplace add produckyou-design/agent-director-protocol` followed
  by `/plugin install agent-director@agent-director-protocol`. Installed users
  get updates via Claude Code's background marketplace refresh, or on demand
  with `/plugin update agent-director` — replacing the previous copy-the-files
  install, which had no update path at all.
- **Version guard test** (`tests/test_skill_structure.py`): `plugin.json`'s
  `version` must equal the newest released version in `CHANGELOG.md`. Claude
  Code only ships an update to installed users when that field changes, so a
  stale value silently delivers nothing; CI now fails instead.
- **"What this gets you"** section in `README.md` / `README.ko.md`: a table
  mapping concrete failure modes (a "done!" report for code never wired into
  the call path, invented test output, retry loops, unapproved subagent
  fan-out, parallel agents clobbering a file, a failed attempt discarded along
  with its evidence, vague delegation) to the specific rule that catches each
  one. Deliberately no percentage claims — the repository's existing stance
  against unverifiable metrics is unchanged; this states which failures the
  mechanism addresses, and adds an explicit "when it isn't worth it" note
  (one-file scripts, throwaway prototypes) so the overhead is stated honestly.

### Changed

- `README.md` / `README.ko.md` open with the value proposition and the
  failure-mode table rather than a structural description — the previous lede
  explained what the protocol *is* before saying why anyone would want it.
- `.claude-plugin/plugin.json` moved from `claude/skills/agent-director/` to
  the repository root and gained a `skills: "./claude/skills"` field. The
  plugin root is now the repo root, so the skill's relative links into `core/`
  and `schemas/` resolve inside an installed plugin; scoped to the old
  subdirectory they pointed outside it. Version bumped 0.1.0 → 0.4.0 (it had
  been left at 0.1.0 through two releases).

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
