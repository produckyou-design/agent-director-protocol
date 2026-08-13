# Agent Director Codex plugin

This is the Codex Agent Director workflow for the Agent Director Protocol. It
is applied by default to repository and code tasks; explicit invocation is
also supported when the user wants to make the policy visible.

Install it from the repository marketplace:

```text
codex plugin marketplace add produckyou-design/agent-director-protocol
codex plugin add agent-director@agent-director-protocol-plugins
```

In a new Codex task/thread, the skill is applied automatically when the task
is repository or code work. `$agent-director` or "Director mode on" remains an
optional explicit invocation. The skill announces the current session as
Director and requires every ADP-created native worker spawn to include
`model="gpt-5.6-luna"` and
`reasoning_effort="max"`. The user-selected model continues to own
the Director session; it is never inherited by a worker.

That Director announcement is root-only. A task tree has exactly one Director:
the root/current parent session. Every spawned subagent is a worker or reviewer
according to its assigned role, and the parent Director's Task Contract is
authoritative. A worker must execute only its assigned mission and report
evidence or status; a spawned subagent is never a Director under any
circumstance. Only the root/current parent session is Director, and the parent
must assign a valid non-Director role before creation; `director` is invalid.
It must not announce `director_mode: on`, publish a
root-level `task_start` or composition disclosure, rewrite or re-decompose the
parent contract, spawn or manage workers, integrate or merge work, or declare
the overall task complete. If the parent role or contract is unavailable or
contradictory, stop and report role ambiguity to the parent rather than
self-promoting to Director. This is an instruction/contract boundary; native
runtime role metadata remains authoritative where exposed. A worker may perform
a deployment or another state-changing operation when the parent contract
explicitly includes it.

Before every worker spawn, the root/current parent Director must assign the
non-Director role before creation and provide a complete per-worker Task
Contract containing scope and non-goals plus the exact fields `goal`,
`success_criteria`, `failure_criteria`, `termination_criteria`, and
`required_evidence` (evidence/deliverables). Overall `objective`,
`completion_criteria`, and generic `error_handling` do not substitute for
worker-specific fields. Missing, ambiguous, or `director` role assignment, or
any required field, is a pre-spawn failure; the worker must not be created.

The plugin is a behavior/instruction switch, not a hidden model or runtime
toggle. It does not retroactively reload an existing task, install project
files, or change a running session's model. Defaults and named profiles are
defense in depth. Prefer no named custom agent/type; if one is used, verify
its profile is pinned to the same pair before dispatch.

Every task begins with a visible `task_start` work-contract notice. A
read-only task may plan zero workers only when it marks
`work_contract.read_only: true`; worker batches use `spawn` and require
positive totals. Any later worker, contract, revision, rescue, reviewer, or
scope addition requires a new `addition` notice stating the changed scope,
what the new worker will do, a classified reason, and why an existing worker
cannot absorb it. The repository can validate this contract but cannot
intercept the platform-owned `multi_agent_v1__spawn_agent` call.

The Director is the coordinator and reviewer, not the ordinary implementer.
Implementation and other state changes require a positive worker total. When
files overlap, use one sequential implementer; do not convert the conflict to
zero workers and direct Director edits. Luna/max on the Director session does
not remove this boundary. Direct takeover is never automatic: the failure,
escalation, rescue, and takeover gates are evidence gates only. It requires
explicit current-session user authorization after a takeover disclosure,
followed by the required record and independent review. “Fix it” and “Director
mode” do not authorize direct product-code implementation.

Returned/runtime metadata must be checked when exposed. A mismatched worker is
rejected and closed and its output is discarded. If the surface cannot accept
or verify the pair, stop and report a policy violation/fallback requirement.
Any non-Luna/non-max exception needs explicit user authorization and disclosure.
At the max baseline, Codex Rescue is unavailable because no higher same-model
effort exists; preserve evidence and stop/report or ask the user. Do not turn
Rescue failure into automatic Director takeover.

Native worker recovery is progress-aware and fail-closed. A native `RUNNING` worker is preserved by default. A wait timeout is an observation only: no final
result arrived during that wait; timeout alone is never completion, interrupt,
close, splitting, or re-dispatch evidence. On the first timeout, record the
observation and perform another task-appropriate bounded wait by default,
unless explicit fatal runtime evidence already exists: a crash, repeated tool error, explicit failure, runtime disconnect, or a demonstrably repeated identical command. During the longer wait, inspect exposed native status, recent tool output, active-command signals, or other declared progress evidence.
A progressing worker or active command is never interrupted or closed merely
because a wait expired.

File state is not lifecycle evidence: in read-only tasks, file changes or their absence are never stall evidence; in write tasks, absence of file changes alone never proves a stall. A read-only architecture/design final report counts as a
completed-work artifact only when it includes concrete scope, evidence,
findings, tests or inspection commands, and unresolved risks. If the native
surface exposes no progress telemetry, classify the state as `unknown`, not
`stalled`. Work that appears complete without a final report is recorded as
`completed_work_unreported` only while native status is non-terminal or unknown.

Only explicit fatal evidence or a declared bounded no-progress window with
native status still `RUNNING` and no active command or progress signal permits
one bounded interrupt (`interrupt=true`). An interrupt is permitted only after
that same explicit fatal evidence or declared bounded no-progress window. The
no-progress path does not require an error message and must not silently loop
forever. The interrupt tells the worker: "Stop the current work, summarize only evidence already secured, do not start new work, tests, or edits, then exit." A queued request to return progress is not an interrupt.
Normal `RUNNING` or progressing workers are not closed.
For the non-final stalled recovery path, close is allowed only after `stalled` classification, one interrupt, and one bounded wait if it remains non-final. Preserve `completed_work_unreported` and `unknown`; do not close either merely to obtain a final report. Do not
repeatedly resume or re-dispatch the same unresponsive worker. A fresh
implementer or scope split requires both a new `addition` disclosure and a
revised contract.

Terminal-result cleanup is separate from stalled recovery. An authoritative
native terminal result such as `completed`, `errored`, `interrupted`, or
`shutdown` takes precedence over inferred non-final classifications. The
Director first captures and persists all available report/evidence, then enters
the atomic cleanup-claim state machine for the current lifecycle cycle. At most
one `close_agent` call may be accepted per lifecycle cycle. A
`task_complete`/final native lifecycle event with an open native edge is
completed terminal work awaiting cleanup, not `RUNNING`. Without an
authoritative terminal result, `completed_work_unreported` and `unknown` remain
non-final and are never closed merely to force a report.

Maintain one reconciliation record per worker identity and lifecycle cycle with
cleanup state `unclaimed`, `in_flight`, `succeeded`, `failed`, or `unknown`,
attempt count, retry availability, unique attempt identifier, and outcome.
Every initial or retry `close_agent` invocation requires an atomic transition
from an eligible state to `in_flight`; only the winning claimant invokes.
Initial cleanup atomically claims `unclaimed`. A retry atomically consumes the
one retry and claims `failed` or `unknown` only when authoritative native state
proves the worker is still terminal/open and the prior invocation was not
accepted. Already closed becomes `succeeded`; never invoke `succeeded` again.
Otherwise preserve/report unresolved acceptance without a blind duplicate
call. `resume_agent` begins a new lifecycle cycle and record.

Before the root Director emits its final response or ends the task, it must
reconcile every lifecycle cycle it created. It consults the reconciliation
record, captures missing terminal evidence, atomically claims and invokes
`unclaimed`, skips `succeeded`, and resolves `in_flight`, `failed`, or `unknown`
from authoritative native state before an atomic bounded-retry claim. It
preserves/reports non-final and unresolved cycles. The
Director must not silently finish while owned children
remain unreconciled.

Closing or resuming (`close_agent` or `resume_agent`) does not merge fork changes into the main tree, so inspect
and review the fork diff or implementation report before integration. A named
implementer uses `fork_context=false` or omission; `fork_context=true` is
compatible only when `agent_type` is omitted. Serialization failure is a
pre-spawn dispatch failure, not an implementation failure. Rescue is
unavailable at the active Luna/max baseline.

Initial decomposition must justify why its contract size and total
contract/worker count are minimal, using conflict boundaries, dependencies,
independent evidence/review, or blast-radius isolation and explaining why fewer
existing contracts cannot absorb the work. Mid-task additions require a new
disclosure grounded in newly discovered evidence, a new conflict/dependency,
a mandatory independent-review boundary, or a classified failure, plus why an
existing worker cannot absorb it. Speed and efficiency may be recorded as
outcomes, and an explicit latency priority may be recorded, but neither is a
standalone reason to add a worker or mark a batch parallel.

Parallel dispatch is deterministic: the visible `work_contract` must disclose
`independent_groups`, each group's `conflict_domains`, `dependency_edges`,
`planned_workers`, `capacity_source`, `write_isolation`, and
`why_fewer_workers_cannot_absorb`. Parallel is allowed only for two or more
independently verifiable groups with pairwise-disjoint domains across files,
code regions, interfaces, schemas, generated output, build targets, shared
state, data, and user flows, with no
cross-group dependency edges and with isolated write state. A
shared/conflicting or sequential write domain uses one worker. With known
native capacity of at least two, `planned_workers = min(group count,
observed_capacity)`; with unknown capacity, use one sequential worker and
record `unknown` without inventing a cap. Capacity saturation never authorizes
Director takeover.

For persistent project defaults, follow
[codex/INSTALL.md](../../codex/INSTALL.md) and install the project's
`AGENTS.md`, `.codex/config.toml`, and role profiles. Personal custom
agents may be placed under `$CODEX_HOME/agents/`, but they still require
explicit per-spawn model/effort fields and the same metadata verification.

Never place API keys, access tokens, or private transcripts in this plugin.
