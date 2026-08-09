# Concurrency Rules

This document defines when delegated tasks may run in parallel and when they must run sequentially.
The adapter observes native runtime capacity; the protocol supplies correctness
and disclosure checks without inventing a concurrent or cumulative numeric cap.

## Default: sequential unless proven independent

Only genuinely independent tasks run in parallel. Independence is not inferred from different
filenames. If any of these domains overlap, the director MUST default to sequential execution:

- files or glob patterns;
- code regions or data structures;
- public interfaces, API contracts, or event names;
- schemas or database entities/migrations;
- shared configuration or state stores;
- generated artifacts or build/package targets;
- user flows or data dependencies.

Read/read work may run in parallel when it has no dependency. Write/write overlap is forbidden.
Read/write work is sequential whenever the read must see the writer's result or the writer could
invalidate the reader's evidence.

## The conflict check

Before a parallel dispatch, compare the `conflict_domains` object in every Task Contract. For each
domain key, normalize exact names and declared glob patterns, then check for intersection. A shared
file is sufficient to force sequencing even when the intended code regions differ. A shared
interface or schema is sufficient even when the files differ.

If a conflict is found, add a real dependency where one task needs the other's output or otherwise
choose a deterministic sequential order. Do not create a false dependency merely to hide a conflict;
the disclosure should state that the order is a conflict-safety decision.

## Native capacity and disclosed batches

The active adapter may expose `agents.max_concurrent_threads_per_session` or
another runtime capacity value. That observed value is runtime capacity only;
ADP does not add a concurrent or cumulative numeric cap. If capacity metadata
is absent, record it as unknown and do not invent a project default.

Before the first spawn or any state-changing work, the director must visibly
disclose a checkable work contract to the user. It must state objective/scope,
planned total contracts/workers, the minimum-safe rationale based only on
conflict boundaries, dependencies, independent evidence/review, or blast-radius
isolation (and why fewer existing contracts/workers cannot absorb it), the model
and effort, the complete batch plan, exact test commands, and stop conditions.

Before each later batch, send a continuation disclosure stating the previous
batch's result and closure state, why the next batch remains necessary, the next
batch size, and the updated plan. A preplanned later batch is not an
unapproved addition, but it still requires this disclosure.

When active slots are full, wait for workers to finish, independently inspect
the required evidence, close completed workers to release slots, and then
re-scope or return to the user. Do not claim native unavailability or perform
the delegated investigation/implementation directly. Capacity saturation alone
is never a takeover or escalation gate.

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

These tasks have no intersection and may be disclosed as `parallel` if they have no dependency and
the observed native runtime capacity permits it. If a third task changes `POST /orders`, the
interface intersection forces it to run sequentially with T-041 regardless of its filename.

## Failure and interruption

Tasks in one batch do not share failure counts. Review and integrate each passing task independently,
but hold a task whose dependency failed. Each failed task follows its own failure/rescue protocol.
If a failure invalidates the batch's design, stop integration and return to design rather than
integrating half of a plan known to be wrong.

On user interruption, report what completed, what remains active, and where each state is preserved.
Never abandon an in-flight write or discard its evidence silently.
