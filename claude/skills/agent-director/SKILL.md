---
name: agent-director
description: Use when the user wants director-mode operation — planning, delegating, and reviewing work instead of coding directly — e.g. "act as director", "delegate implementation", "don't code this yourself", or multi-task feature builds that benefit from parallel implementers.
---

# Agent Director (Claude Code adapter)

This skill binds the platform-neutral agent-director-protocol to Claude Code's
mechanics. It does not restate the full protocol — the authoritative rules
live in [`core/`](../../../core/). Read the relevant core doc before acting
on any section below.

## Roles, mapped to Claude Code

- **Director** — the main conversation model (this session). Plans,
  decomposes, delegates, and reviews. Never writes product code itself except
  after a recorded takeover (see below).
- **Implementer** — a subagent spawned with the Task/Agent tool. Default
  model is Sonnet-class, per `implementer.preferred_models` in the active
  profile under [`../../profiles/`](../../profiles/) (see also
  [`CLAUDE.md.example`](../../CLAUDE.md.example) for how a project points at
  one).
- **Reviewer** — the director itself, unless a profile sets
  `reviewer.inherit` to something else. Full rule:
  [`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md).

## Delegating a task

1. Write a complete task contract before spawning any implementer. Fill in
   every field from [`references/task-template.md`](references/task-template.md);
   the JSON shape it mirrors is
   [`task-contract.schema.json`](../../../schemas/task-contract.schema.json).
   A vague scope ("improve the feature") is not a valid contract — see
   [`TASK-CONTRACT.md`](../../../core/TASK-CONTRACT.md).
2. Pass the **full contract**, not a summary, in the subagent prompt when
   invoking the Task/Agent tool. The implementer should never have to guess
   at `editable_files`, `forbidden_files`, `interfaces_to_preserve`,
   `completion_criteria`, or `test_commands`.
3. Require the implementer to return an implementation report shaped like
   [`implementation-report.schema.json`](../../../schemas/implementation-report.schema.json)
   (status, files changed, tests actually executed with verbatim output,
   completion criteria status, out-of-scope issues).
   [`references/review-template.md`](references/review-template.md) is for
   the director's own review output, not the implementer's report — do not
   hand it to the subagent.
4. Full delegation mechanics:
   [`DELEGATION-PROTOCOL.md`](../../../core/DELEGATION-PROTOCOL.md).

## Reviewing (never trust the report)

The director independently verifies before accepting any implementation:

- Read the actual diff yourself (do not rely on the implementer's summary).
- Re-run the `test_commands` from the task contract yourself — or, when
  re-running is impractical, inspect the raw output evidence — and compare
  against what the report claims (per
  [`REVIEW-GATES.md`](../../../core/REVIEW-GATES.md)).
- Score all ten checks in
  [`references/review-template.md`](references/review-template.md)
  (`code_actually_changed`, `feature_wired_into_flow`,
  `tests_actually_executed`, `test_results_match_report`,
  `no_fake_or_placeholder_success`, `no_regressions`,
  `interfaces_preserved`, `no_out_of_scope_changes`,
  `error_handling_present`, `completion_criteria_met`), each with concrete
  evidence, per
  [`review-result.schema.json`](../../../schemas/review-result.schema.json).
- On `revision_required`, write an evidence-based revision instruction using
  [`references/revision-template.md`](references/revision-template.md) and
  re-delegate — do not just re-ask the same subagent to "try again" without
  new, specific guidance.
- Full gates: [`REVIEW-GATES.md`](../../../core/REVIEW-GATES.md).

## Concurrency

Spawn parallel subagents only when their `conflict_domains` (files,
data_structures, interfaces, db_entities, shared_configs, state_stores,
build_targets, user_flows) do not overlap. Any overlap forces sequential
execution. Never let two subagents edit the same file concurrently. When the
environment supports isolated working copies (e.g. the Agent tool's
`worktree` isolation), prefer that for anything running in parallel as an
extra safety margin, not as a substitute for the conflict-domain check. Full
rule: [`CONCURRENCY-RULES.md`](../../../core/CONCURRENCY-RULES.md).

## Failure loop and takeover

Count only full revision loops (instruction → implementation → tests →
director review → evidence-based revision instruction → re-implementation →
re-test → re-review) as failures — merely re-asking or regenerating an
answer does not count. Takeover becomes permissible only when **two**
counted failures have occurred on the same task, or the implementer
demonstrably cannot perform the task at all (per
[`TAKEOVER-PROTOCOL.md`](../../../core/TAKEOVER-PROTOCOL.md)). Then:

1. Fill in
   [`references/takeover-template.md`](references/takeover-template.md)
   (mirrors
   [`takeover-record.schema.json`](../../../schemas/takeover-record.schema.json))
   with concrete evidence from both failed loops.
2. Record it (e.g. in the task's example/audit trail).
3. Only then may the director write product code directly, bounded to
   `modification_scope`.

"The task is small or simple" is never a valid takeover reason. Full rules:
[`FAILURE-LOOP.md`](../../../core/FAILURE-LOOP.md) and
[`TAKEOVER-PROTOCOL.md`](../../../core/TAKEOVER-PROTOCOL.md). Completion is
only claimed per
[`COMPLETION-STANDARD.md`](../../../core/COMPLETION-STANDARD.md).

## Reference templates in this skill

- [`references/task-template.md`](references/task-template.md) — task
  contract fill-in.
- [`references/review-template.md`](references/review-template.md) —
  ten-check review result fill-in.
- [`references/revision-template.md`](references/revision-template.md) —
  evidence-based revision instruction.
- [`references/takeover-template.md`](references/takeover-template.md) —
  takeover record fill-in.

## Full protocol (core, platform-neutral)

[`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md) ·
[`DELEGATION-PROTOCOL.md`](../../../core/DELEGATION-PROTOCOL.md) ·
[`TASK-CONTRACT.md`](../../../core/TASK-CONTRACT.md) ·
[`FAILURE-LOOP.md`](../../../core/FAILURE-LOOP.md) ·
[`REVIEW-GATES.md`](../../../core/REVIEW-GATES.md) ·
[`CONCURRENCY-RULES.md`](../../../core/CONCURRENCY-RULES.md) ·
[`TAKEOVER-PROTOCOL.md`](../../../core/TAKEOVER-PROTOCOL.md) ·
[`COMPLETION-STANDARD.md`](../../../core/COMPLETION-STANDARD.md)
