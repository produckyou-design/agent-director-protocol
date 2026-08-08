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
  after a recorded takeover (see below) — and the same rule covers *running*
  state-changing operations (deploys, migrations, release pipelines), which
  are delegated like any other work. Read-only inspection is fine; it is part
  of reviewing.
- **Implementer** — a subagent spawned with the Task/Agent tool. Its model is
  selected by the active adapter profile and recorded explicitly in the Task
  Contract; the profile under [`../../profiles/`](../../profiles/) provides the
  current default (see also
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
   `delegation`, `conflict_domains`,
   `completion_criteria`, or `test_commands`.
3. Require the implementer to return an implementation report shaped like
   [`implementation-report.schema.json`](../../../schemas/implementation-report.schema.json)
   (status, files changed, tests actually executed with verbatim output,
   completion criteria status, out-of-scope issues).
   [`references/review-template.md`](references/review-template.md) is for
   the director's own review output, not the implementer's report — do not
   hand it to the subagent.
4. **Set reasoning effort explicitly on every spawn.** Classify the task, then
   pass the `effort` matching `implementer.effort_by_task_kind` in the active
   profile. Omitting `effort` silently inherits the session default — that
   under-powers investigation and over-powers mechanical work, and the failure
   is invisible in the returned report.

   | task kind | effort | typical work |
   |---|---|---|
   | `investigation` | `high` | root-cause hunts, competing hypotheses, design judgement |
   | `audit` | `high` | pre-release compliance / security review |
   | `implementation` | `medium` | building to a complete contract |
   | `pipeline` | `medium` | release/deploy execution (procedure fidelity) |
   | `mechanical` | `low` | version bumps, doc sync, single-line edits |

   Record the chosen kind and effort in the contract so a revision loop can
   raise it deliberately. When a first attempt returns thin evidence or misses
   a hypothesis the director expected, **raise effort one step on
   re-delegation** instead of merely restating the same instruction — see
   [`FAILURE-LOOP.md`](../../../core/FAILURE-LOOP.md).
5. **Decompose to the fewest tasks that qualify, not the most.** Before disclosing anything, check
   whether this really needs N subagents or whether some pieces belong in one broader task contract.
   Splitting further than the minimum needs a concrete reason — genuine parallelism benefit, a
   distinct effort/model tier for one part, blast-radius isolation, or genuinely independent
   verifiable outcomes — not "smaller diffs." See
   [`DELEGATION-PROTOCOL.md`](../../../core/DELEGATION-PROTOCOL.md) step 4.
6. **Disclose the agent composition before spawning anything.** Once per batch — not per individual
   spawn — tell the user what is about to run, filling in
   [`references/agent-briefing-template.md`](references/agent-briefing-template.md) Part 1 (mirrors
   [`agent-composition-disclosure.schema.json`](../../../schemas/agent-composition-disclosure.schema.json)):
   director model/effort and source, subagent count, each subagent's role/task/model/model ceiling,
   effort, model source, conflict domains, and **`justification`** (why this piece needs its own
   subagent, not folded into another task in the batch), execution mode, spawn budget, and whether a
   Rescue Agent promotion is even reachable this session. Work does not start until this has been
   stated. **If `subagent_count` exceeds the active
   profile's `director.max_batch_agents`, this disclosure is also an approval request** —
   `within_preapproved_range: false`, `approval_status: pending` — and dispatch waits for
   `approval_status: granted`, the same pattern a Rescue Agent promotion outside the pre-approved
   range uses. A conflict-free batch is still subject to this cap; passing the conflict-domain check
   means the batch is *safe* to run in parallel, not that its size needs no sign-off — see
   [`CONCURRENCY-RULES.md`](../../../core/CONCURRENCY-RULES.md). Mid-task promotions (Rescue Agent, or a granted
   escalation) get their own separate notice later — see Escalation and Failure loop below — not
   folded into this upfront disclosure, and do not count against `max_batch_agents`.
7. **A subagent must never spawn its own subagents.** If one reports mid-task that it thinks the work
   needs splitting further, that comes back to you as an out-of-scope/blocked finding — you decide
   whether to re-decompose, per step 5. This is the containment boundary that keeps a disclosed,
   approved batch from silently multiplying past what the user saw. See
   [`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md).
8. Full delegation mechanics:
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

## Escalation (stop guessing, request an upgrade)

**A third guess-based fix for the same problem is forbidden.** Once two attempts at the same root
cause have failed — two different diffs, two different results, same underlying cause — the next
step is an escalation request, not a third try. This applies to implementers and to the director
itself. It is not automatic model switching: nobody changes their own model or effort; the
implementer requests it from the director, the director requests it from the user, and the request
is only granted after the requester's evidence is independently checked.

- **Implementer stuck** → it stops and submits `EFFORT_ESCALATION_REQUEST` (the default — more
  reasoning room on the same model is cheaper and usually enough) or, only when effort is already
  maxed out or the gap is a capability the tier lacks at any setting,
  `MODEL_ESCALATION_REQUEST` — using
  [`references/escalation-template.md`](references/escalation-template.md) (mirrors
  [`escalation-request.schema.json`](../../../schemas/escalation-request.schema.json)).
  It does not attempt a third fix while waiting.
- **Director evaluates** — reads the actual diffs and test evidence for both attempts, confirms they
  were genuinely different approaches at the same root cause, then either runs one more read-only
  investigation round at the same tier, or — for a genuine reasoning/model-capability gap — grants
  the request as a Rescue Agent promotion (see Failure loop below). A granted escalation gets the
  same [promotion notice / rescue outcome notice](references/agent-briefing-template.md) pair as an
  ordinary Rescue Agent promotion — including the approval-required branch when the grant falls
  outside the user's pre-approved model/effort range. It is never silently applied.
- **Director stuck** (conflicting subagent results, an unresolved shared-contract impact, insufficient
  confidence in a security/deployment/data-loss judgment, or confidence below 70%) → it submits its
  own `DIRECTOR_ESCALATION_REQUEST` to the user via the same template, and finalizes nothing
  high-risk until the user responds.
- Trigger conditions other than "two failed attempts" (widening failure surface, a previously
  passing feature breaking, low confidence) can fire this earlier than the failure-loop count below —
  asking for more reasoning power is cheap, so the bar to ask is lower than the bar for takeover,
  regardless of what the active profile's `failure_threshold` is set to.
- Typos, command mistakes, and transient environment failures may be excluded from the count, but
  the exclusion reason must be logged.

Full rule: [`ESCALATION-PROTOCOL.md`](../../../core/ESCALATION-PROTOCOL.md).

## Concurrency

Spawn parallel subagents only when their `conflict_domains` (files,
data_structures, interfaces, db_entities, shared_configs, state_stores,
build_targets, user_flows) do not overlap. Any overlap forces sequential
execution. Never let two subagents edit the same file concurrently. When the
environment supports isolated working copies (e.g. the Agent tool's
`worktree` isolation), use it for anything running in parallel — the
conflict-domain check covers *intended* changes, not a stray write or
regenerated artifact from one subagent landing in another's diff. Where no
isolation is available, run sequentially. Full rule:
[`CONCURRENCY-RULES.md`](../../../core/CONCURRENCY-RULES.md).

**When part of a batch fails**, resolve each task on its own evidence: integrate
the passing ones (unless they `depends_on` a failed task — then hold and
re-review after), and let each failed task run its own failure loop with its own
count. Failures do not pool across tasks. If the failure shows the *design* was
wrong rather than one implementer struggling, stop integrating and return to
design. On user interruption, report what completed, what was in flight, and
where each state is preserved — never abandon in-flight work silently.

## State safety (git discipline)

- **Establish a last-passing checkpoint** (a real commit SHA/tag, not "the state
  before we started") before the first dispatch, and resolve a dirty working tree
  first — otherwise every later diff is ambiguous.
- **Never destroy a failed attempt's changes before reviewing them.** No
  `git checkout .` / `reset --hard` / `clean -fd` on unreviewed work — the failed
  diff is the evidence the revision instruction, Rescue Agent package, and
  takeover record all depend on. Preserve it (scratch branch, named stash, patch)
  first.
- **Subagents don't commit to the main line.** Integration is yours, after the
  review gates pass. A subagent may commit freely inside its own worktree/branch.
- **Destructive operations are deliberate decisions**, never incidental steps:
  force-push or history rewrite of a pushed branch, deleting the only copy of
  work, or discarding the checkpoint itself. State what will be lost first.
- Verify `files_changed` against the real diff — an omitted incidental change
  (reformatted file, regenerated lockfile) hides scope creep.

Full rule: [`STATE-SAFETY.md`](../../../core/STATE-SAFETY.md).

## Failure loop → Rescue Agent → takeover (in that order)

Escalation (above) is a mid-task request for more power. This section is the *default* path once an
implementer has already failed the same task the active profile's `implementer.failure_threshold`
times (default **two** — see [`../../profiles/`](../../profiles/)) — **director direct coding is the
last resort here, not the next step.** Count only full revision loops (instruction → implementation
→ tests → director review → evidence-based revision instruction → re-implementation → re-test →
re-review) as failures — merely re-asking or regenerating an answer does not count.

```
implementer fails the configured number of times (failure_threshold, default 2 counted loops)
  → director reads the real diff/tests/logs and classifies the cause
      reasoning_gap / model_capability_gap → Rescue Agent: raise EFFORT only, same model
                                              (e.g. medium → high → xhigh; never a model swap)
                                                  succeeds → review + integrate, done, no director coding
                                                  effort ladder exhausted → default: escalate to the
                                                    user to raise THE DIRECTOR's model/effort.
                                                    Granted → upgraded director re-judges and issues
                                                    a REVISED task contract (fresh loop count).
      requirement_conflict → director revises the task              other step-4 choices:
      contract & re-delegates (ordinary planning,                     direct intervention (takeover, last resort)
      not a step-4 choice — self-escalate first if                    roll back
      confidence is low). Fails too → picks ONE ↴                     reduce scope
                                                                      convert to an investigation task
      diagnosis_gap / environment_issue / rollback_needed
      → skip the Rescue Agent, go straight to the
        same director-picks-ONE choice
```

1. **Classify** the failure into exactly one cause (`diagnosis_gap`, `reasoning_gap`,
   `model_capability_gap`, `requirement_conflict`, `environment_issue`, `rollback_needed`) using the
   actual diffs, failing tests, and logs from both attempts — not the implementer's summary.
2. **`reasoning_gap` / `model_capability_gap` → Rescue Agent, which raises reasoning effort only.**
   It **never swaps the implementer's model** — both attempts climb the effort ladder on the model
   already in use (e.g. `medium` → `high` → `xhigh`). A model change is a cost decision that
   belongs to the user, reached through step 4, not an automatic promotion. The classification
   decides how far to climb before handing off: `reasoning_gap` uses both attempts;
   `model_capability_gap` uses one to confirm, then goes to step 4 (say so in `promotion_reason`).
   If the implementer was already at its model's top effort, skip the Rescue Agent entirely and go
   to step 4. Before attempt 1 runs, send the
   [promotion notice](references/agent-briefing-template.md) (mirrors
   [`promotion-notice.schema.json`](../../../schemas/promotion-notice.schema.json)):
   task, prior model/effort, failure count, what each failed attempt tried, the promotion reason, the
   assigned rescue model/effort for *this attempt*, editable/forbidden scope, and whether it's within
   the user's pre-approved range. If not, this notice is also an approval request — do not start
   until `approval_status` is `granted`. Hand the scope package via
   [`references/rescue-agent-template.md`](references/rescue-agent-template.md) (mirrors
   [`rescue-agent-task.schema.json`](../../../schemas/rescue-agent-task.schema.json)):
   both prior attempts as reference (not a forced starting point), the last-passing checkpoint,
   editable/forbidden files, an explicit `forbidden_scope`, and this attempt's `attempt_number` (1 or
   2) with its own `assigned_model` / `assigned_effort` — tracked separately from the implementer's
   own loop count. Prefer an isolated branch/worktree from the last-passing checkpoint (see
   Concurrency, above) rather than continuing the failed implementer's working state. When each
   attempt ends — success or failure — send the matching
   [rescue outcome notice](references/agent-briefing-template.md) (mirrors
   [`rescue-outcome-notice.schema.json`](../../../schemas/rescue-outcome-notice.schema.json)),
   including `reverted_to_baseline` so the return to the normal tier is stated, not inferred.
3. **`requirement_conflict` → revise the contract, not a Rescue Agent.** The default response is
   ordinary re-planning: fix the contradiction in the task contract and re-delegate per
   [`DELEGATION-PROTOCOL.md`](../../../core/DELEGATION-PROTOCOL.md) — not a Rescue Agent, and not yet a
   step-4 choice. If confidence in the revision is low, or it touches architecture, security,
   deployment, or data-loss risk, submit your own `DIRECTOR_ESCALATION_REQUEST` (Escalation, above)
   before finalizing it. Only if the *revised* contract also fails does this go to step 4.
   `environment_issue` and `diagnosis_gap`/`rollback_needed` never get a Rescue Agent or a revision
   attempt — go straight to step 4 (rollback_needed defaults to "roll back").
4. **If the Rescue Agent's effort ladder is exhausted, the revised contract also fails, or a cause
   never routed to either,** choose exactly one: **escalate to the user** (the default when the
   effort ladder ran out), director direct intervention (still requires the takeover record below —
   the ONLY door into takeover), roll back to the last-passing checkpoint, reduce task scope, or
   convert the task into a read-only investigation.

   **When you escalate because effort ran out, ask to raise *your own* model and effort — not the
   implementer's.** An implementer failing at high effort is evidence about the plan, not the coder:
   the design, the decomposition, or the contract you wrote is the leading suspect. If the user
   grants it, the upgraded director **re-judges the task on its own standard and issues a revised
   task contract** — do not re-delegate the contract that kept failing. Treat the old contract as
   evidence about what was tried; `current_state`, `target_behavior`, `completion_criteria`, and the
   file scope are all open to change, and the task may be split or narrowed. The revised contract is
   a fresh task with its own failure-loop count. A stronger *implementer* model is something the
   user may grant in response — never something you promote to on your own.
5. **On a verified Rescue Agent success, the director does not write code anyway.** Review the real
   diff and re-run the real tests exactly as for any other implementation, then integrate.

**Takeover itself** (director direct intervention) requires, before any code is touched:

1. Fill in
   [`references/takeover-template.md`](references/takeover-template.md)
   (mirrors
   [`takeover-record.schema.json`](../../../schemas/takeover-record.schema.json))
   with concrete evidence — `second_failure_evidence` is whichever step actually ran its course: the
   Rescue Agent's second attempt (`reasoning_gap`/`model_capability_gap`) or the revised task
   contract's failed re-delegation (`requirement_conflict`) — never the original implementer's second
   loop.
2. Record it (e.g. in the task's example/audit trail).
3. Only then may the director write product code directly, bounded to `modification_scope`.
4. **Send the resulting diff to a separate reviewer — do not review your own code.** Spawn a
   reviewer subagent at *your own* model and effort, with a fresh context that did not participate
   in writing the change, and have it score the ten gates. Same rigor, no inherited blind spots.
   See [`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md) → "The director MUST NOT review its own
   work."

"The task is small or simple" is never a valid takeover reason, and "the implementer hit the failure
threshold" is never a valid takeover reason **by itself** — it must have gone through classification
and, where applicable, a Rescue Agent or a revised task contract first. Full rules:
[`FAILURE-LOOP.md`](../../../core/FAILURE-LOOP.md),
[`RESCUE-PROTOCOL.md`](../../../core/RESCUE-PROTOCOL.md), and
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
- [`references/escalation-template.md`](references/escalation-template.md) —
  implementer→director and director→user escalation request fill-in.
- [`references/rescue-agent-template.md`](references/rescue-agent-template.md) —
  Rescue Agent scope package fill-in.
- [`references/agent-briefing-template.md`](references/agent-briefing-template.md) —
  agent composition disclosure, promotion notice, and rescue outcome notice
  fill-in.

## Full protocol (core, platform-neutral)

[`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md) ·
[`DELEGATION-PROTOCOL.md`](../../../core/DELEGATION-PROTOCOL.md) ·
[`TASK-CONTRACT.md`](../../../core/TASK-CONTRACT.md) ·
[`FAILURE-LOOP.md`](../../../core/FAILURE-LOOP.md) ·
[`REVIEW-GATES.md`](../../../core/REVIEW-GATES.md) ·
[`CONCURRENCY-RULES.md`](../../../core/CONCURRENCY-RULES.md) ·
[`ESCALATION-PROTOCOL.md`](../../../core/ESCALATION-PROTOCOL.md) ·
[`RESCUE-PROTOCOL.md`](../../../core/RESCUE-PROTOCOL.md) ·
[`TAKEOVER-PROTOCOL.md`](../../../core/TAKEOVER-PROTOCOL.md) ·
[`STATE-SAFETY.md`](../../../core/STATE-SAFETY.md) ·
[`COMPLETION-STANDARD.md`](../../../core/COMPLETION-STANDARD.md)
