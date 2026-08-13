# Concurrency Rules

This document defines when delegated tasks may run in parallel and when they must run sequentially.
The adapter observes native runtime capacity; the protocol supplies correctness
and disclosure checks without inventing a concurrent or cumulative numeric cap.

## Deterministic parallel-dispatch rule

The director must describe the batch as `independent_groups`, `conflict_domains`, and
`dependency_edges` before choosing an execution mode. A batch is eligible for `parallel` execution
only when all of these conditions hold:

1. It contains **two or more independently verifiable work groups**. Each group has its own bounded
   scope, completion criteria, and evidence path; a list of filenames is not enough.
2. Every pair of groups has disjoint conflict domains. Compare files, code regions, interfaces,
   schemas, generated output (`generated_artifacts` / build targets), shared state
   (`shared_configs` / `state_stores`), data (`data_structures` / database entities), and user
   flows. A shared file or shared interface forces sequencing even when the intended lines differ.
3. There are no cross-group dependency edges, including `depends_on`, read/write consistency, a
   required generated artifact, or an integration result that one group must receive from another.

If any condition fails, the batch is sequential. A shared, conflicting, or sequential write domain
has **one worker owner** (`planned_workers: 1` for that domain); do not use parallel workers to hide
the conflict. Read/read work can be parallel only after the same group, domain, and dependency
checks pass. Parallel writes also require isolated working copies; without isolation, they are
sequential even when the intended domains appear disjoint.

Parallelism is a consequence of this proof, not a justification by itself. Speed or efficiency may
be recorded as an outcome, and an explicit latency priority may be recorded as an optional user
priority, but neither can create independent groups or override a conflict, dependency, missing
isolation, or native capacity.

## The conflict check

Before a parallel dispatch, compare the `conflict_domains` object in every Task Contract. For each
domain key, normalize exact names and declared glob patterns, then check for intersection. A shared
file is sufficient to force sequencing even when the intended code regions differ. A shared
interface or schema is sufficient even when the files differ.

If a conflict is found, record the actual conflict or dependency edge and choose a deterministic
sequential order. Do not create a false dependency merely to hide a conflict; the disclosure should
state that the order is a conflict-safety decision. A vague claim such as "parallel for speed" or
"parallel for efficiency" is not a valid eligibility or scale decision.

## Native capacity and disclosed batches

The active adapter may expose `agents.max_concurrent_threads_per_session` or another runtime
capacity value. That observed value is runtime capacity only; ADP does not add a concurrent or
cumulative numeric cap. For `N = len(independent_groups)`:

- when `N >= 2`, the domains are disjoint, dependency edges are empty, and observed capacity is a
  known integer of at least two, set `planned_workers = min(N, observed_capacity)`;
- when the batch is a single group or fails the parallel eligibility proof, set
  `planned_workers: 1` for the sequential/shared write domain;
- when capacity is unknown or less than two, do not claim a parallel slot count. Use the
  conservative one-worker sequential fallback (`planned_workers: 1`) and retain
  `capacity_source: "unknown"`; when the runtime reports zero available capacity, stop or wait
  rather than issuing a zero-worker write dispatch.

The work-contract disclosure must include `independent_groups`, each group's complete
`conflict_domains`, `dependency_edges`, `planned_workers`, `capacity_source`, `write_isolation`, and
`why_fewer_workers_cannot_absorb`. The capacity source must identify the native runtime observation
or explicitly say `unknown`; it is never replaced by a project default.

Draft-07 schema validation checks the field shapes and the basic parallel
requirements. The repository's semantic validator
(`scripts/validate_dispatch_plan.py`, invoked by `scripts/validate_schemas.py`)
also checks pairwise domain/glob overlap, dependency endpoints, write isolation,
and the `planned_workers = min(N, observed_capacity)` formula. A schema-valid
disclosure is not dispatch-ready until both checks pass.

Before every task, every state-changing operation, and every native-spawn attempt, the director
must visibly disclose a checkable work contract to the user. It must state objective/scope,
planned total contracts/workers, the minimum-safe rationale based only on
conflict boundaries, dependencies, independent evidence/review, or blast-radius
isolation (and why fewer existing contracts/workers cannot absorb it), the model
and effort, the complete batch plan, exact test commands, and stop conditions.

Every task starts with `phase: task_start`. A zero-worker task start is valid only for a
work contract marked `read_only: true`; `phase: spawn` and `phase: addition` require positive
worker totals. The native-spawn attempt gets its own visible spawn disclosure even when the
task-start notice already described the intended work.

Before each later batch, send a continuation disclosure stating the previous
batch's result and closure state, why the next batch remains necessary, the next
batch size, and the updated plan. A preplanned later batch is not an
unapproved addition, but it still requires this disclosure.

Any later addition or material scope change requires a new `phase: addition` disclosure before
dispatch. It must state `changed_scope`, `change_summary`, `added_worker_task`, one classified
`addition_basis` (`newly_discovered_evidence`, `new_conflict_domain`, `new_dependency`,
`mandatory_independent_review`, or `classified_failure`),
`why_existing_workers_cannot_absorb`, and `new_disclosure: true`. The new worker must still satisfy
the deterministic group/domain/dependency rule and the observed-capacity formula; a stated speed,
parallelism, or efficiency benefit cannot substitute for that evidence. The repository documents
and validates this contract, but the native platform-owned `multi_agent_v1__spawn_agent` call
remains outside repository interception.

When active slots are full, wait for workers to finish, independently inspect
the required evidence, capture terminal reports/evidence, and reconcile
terminal workers through the serialized cleanup state machine below. At most
one cleanup invocation may be accepted per lifecycle cycle. Preserve and
report non-final workers according to the lifecycle rules below, then re-scope
or return to the user. Do not claim native unavailability or perform the
delegated investigation/implementation directly. Capacity saturation alone is
never a takeover or escalation gate.

## Spawn accounting

The disclosure records request accounting and whether native capacity was
observed, without a protocol numeric limit:

```text
already_spawned_count
this_batch_count
total_after_spawn
capacity_source
capacity_known
```

Counts do not reset merely because a batch finishes. Revisions, new
investigators, and rescue assignments require a new disclosure. A native
slot-full response requires wait/close/re-scope/return and never authorizes
Director takeover.

## Shared working state

Native subagents inherit the parent session's permissions and normally operate in the same project
context. Parallel write tasks therefore require an explicitly isolated worktree or equivalent. If
the adapter cannot guarantee isolation, any parallel batch containing writes is invalid and must run
sequentially. A read-only investigator and read-only reviewer may be parallel when their evidence
does not depend on each other.

## Worked example

```json
{
  "task_id": "T-041",
  "conflict_domains": {
    "files": ["src/api/orders.js"],
    "interfaces": ["POST /orders"],
    "user_flows": ["checkout"]
  }
}
```

```json
{
  "task_id": "T-042",
  "conflict_domains": {
    "files": ["src/api/inventory.js"],
    "interfaces": ["GET /inventory/:id"],
    "user_flows": ["inventory-lookup"]
  }
}
```

These are two independently verifiable groups with disjoint domains and no dependency edge, so they
may be disclosed as `parallel` only when the native runtime reports usable capacity. With
`observed_capacity: 2`, the work contract records `planned_workers: 2` (`min(2, 2)`). If capacity is
unknown, it records `capacity_source: "unknown"` and uses one sequential worker without inventing a
cap. If a third task changes `POST /orders`, the interface intersection forces it to run
sequentially with T-041 regardless of its filename; a speed or efficiency claim cannot change that
decision.

## Failure and interruption

Tasks in one batch do not share failure counts. Review and integrate each passing task independently,
but hold a task whose dependency failed. Each failed task follows its own failure/rescue protocol.
If a failure invalidates the batch's design, stop integration and return to design rather than
integrating half of a plan known to be wrong.

## Progress-aware worker waiting

A native `RUNNING` worker is preserved by default. A wait timeout records an observation event only:
no final result arrived during that wait. It is not completion evidence, an interrupt signal, or stall
evidence by itself. The director must inspect the native state before taking recovery action:

- **`progressing`** — progress evidence includes recent worker/tool output, a status transition, an active-command signal, or another progress artifact declared in the contract. Preserve the worker and continue a
  task-appropriate bounded wait. A progressing worker or active command is never interrupted or
  closed merely because a wait expired.
- **`completed_work_unreported`** — only while native status is non-terminal or unknown,
  acceptance evidence, a checkpoint, a diff, or test output shows that work may be complete but no
  final report arrived. Inspect the available evidence without claiming completion; do not rerun the
  work merely to obtain a final message. An authoritative native terminal result always takes
  precedence over this inferred classification.
- **`stalled`** — native status remains `RUNNING` and no active command or other progress signal
  exists for the declared no-progress observation window.
- **`unknown`** — the native surface exposes no progress telemetry. Do not convert lack of telemetry
  into a stall; report the monitoring limitation and preserve the worker state.

File state is never a standalone lifecycle signal. In read-only tasks, file changes or their absence are never stall evidence. A read-only architecture/design final report may be treated as a completed-work artifact only when it contains concrete scope, evidence, findings, tests or inspection commands, and unresolved risks. In write tasks, absence of file changes alone never proves a stall.

On the first timeout, record the observation and perform another task-appropriate bounded wait by
default. Skip that additional wait only when explicit fatal runtime evidence already exists: a crash,
repeated tool error, explicit failure, runtime disconnect, or a demonstrably repeated identical
command. During the longer wait, inspect native status, recent tool output, active-command signals,
or other declared progress when exposed. If the surface exposes no progress telemetry, classify the
state as `unknown`, not `stalled`.

An interrupt is permitted only after either explicit fatal runtime evidence (crash, repeated tool
error, explicit failure, runtime disconnect, or demonstrably repeated identical command), or the
declared no-progress observation window has elapsed with native status still `RUNNING` and no active
command or progress signal. The no-progress path does not require an error message; it is a bounded
recovery path and must not silently loop forever.

After the one permitted `interrupt=true`, direct the worker: "Stop the current work, summarize only evidence already secured, do not start new work, tests, or edits, then exit." A queued request to return progress is not an interrupt. Do not close a normal `RUNNING` or `progressing` worker. For the non-final stalled recovery path, close is allowed only after `stalled` classification, one interrupt, and one bounded wait if it remains non-final. Preserve `completed_work_unreported` and `unknown`; do not close either merely to obtain a final report. A fresh implementer or scope split requires a new addition disclosure and revised contract; repeated native stalls must stop/report native unavailability rather than becoming a timeout/re-dispatch loop.

### Successful terminal cleanup and root finalization

Terminal-result cleanup is separate from stalled recovery. An authoritative
native terminal result such as `completed`, `errored`, `interrupted`, or
`shutdown` takes precedence over inferred `completed_work_unreported` or
`unknown` classifications. Once that terminal result arrives, the Director
first captures and persists all available report and evidence, then enters the
serialized cleanup state machine for that worker's current lifecycle cycle. A
successful native cleanup may be accepted at most once per lifecycle cycle; a
bounded retry is an additional invocation attempt only when the prior attempt
is proven not accepted. A `task_complete`/final
native lifecycle event with an open native edge is completed terminal work
awaiting cleanup, not `RUNNING`. Without an authoritative terminal result,
`completed_work_unreported` and `unknown` remain non-final and are never closed
merely to force a report.

The Director maintains one reconciliation record keyed by worker identity and
lifecycle cycle. It records the terminal result, evidence-capture state,
cleanup state (`unclaimed`, `in_flight`, `succeeded`, `failed`, or `unknown`),
attempt count, retry availability, a unique attempt identifier, and outcome.
Every native cleanup invocation, initial or retry, requires a successful atomic
claim transition to `in_flight`; only the claimant may invoke cleanup. Competing
reconcilers re-read the record and never invoke from a stale state.

<!-- worker-cleanup-transition-table:start -->
| Current state | Required evidence and atomic transition | Next state | Native cleanup action |
|---|---|---|---|
| `unclaimed` | terminal evidence captured; atomically claim attempt 1 | `in_flight` | claimant invokes once |
| `failed` or `unknown` | native state is still terminal/open, prior invocation is proven not accepted, retry remains; atomically consume retry and claim the next attempt | `in_flight` | retry claimant invokes once |
| `in_flight` | authoritative native state says closed | `succeeded` | do not invoke |
| `in_flight` | acceptance remains unknown | `unknown` | do not invoke |
| `succeeded` | any reconciliation | `succeeded` | do not invoke |
<!-- worker-cleanup-transition-table:end -->

After an invocation, record `succeeded` when authoritative native state says
closed, `failed` only for an explicit rejected/not-accepted outcome, and
`unknown` when acceptance cannot be established. `succeeded` is never invoked
again. A failed or unknown attempt receives at most one bounded retry, and only
through the atomic retry claim in the table; otherwise preserve and report the
unresolved state rather than blindly invoking cleanup again. Resuming a closed
worker starts a new lifecycle cycle with a new record.

Before the root Director emits its final response or ends the task, it must
reconcile every lifecycle cycle it created. For each terminal cycle, consult
the reconciliation record and capture missing evidence. Atomically claim and
invoke an `unclaimed` cycle under the transition table; skip `succeeded`; and
resolve `in_flight`, `failed`, or `unknown` from authoritative native state
before any bounded retry claim. Preserve and
report non-final cycles according to this policy. The Director must not
silently finish while owned children remain unreconciled. A platform-native
close or resume operation does not merge a worker fork into the main working
tree; inspect the fork diff or report and explicitly integrate it after review.

On user interruption, report what completed, what remains active, and where each state is preserved.
Never abandon an in-flight write or discard its evidence silently.
