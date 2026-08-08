# Concurrency Rules

This document defines when delegated tasks may run in parallel and when they must run sequentially.
The adapter supplies the native simultaneous-thread setting; the protocol supplies the correctness
check and cumulative spawn limit.

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

## Cumulative spawn budget

The protocol policy separately limits one user request to a cumulative budget. The active adapter
profile supplies the limit, and the disclosure records:

```text
already_spawned_count
this_batch_count
total_after_spawn
max_total_spawned_agents_per_request
within_limit
```

This count does not reset merely because a batch finishes. Revisions, new investigators, and rescue
assignments count unless the active adapter explicitly documents that a replacement reuses an existing
slot. At the limit, the director must merge/revise/re-scope/return the work rather than spawn another
agent. Exceeding it requires a new disclosure and explicit user approval.

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
the budgets permit it. If a third task changes `POST /orders`, the interface intersection forces it
to run sequentially with T-041 regardless of its filename.

## Failure and interruption

Tasks in one batch do not share failure counts. Review and integrate each passing task independently,
but hold a task whose dependency failed. Each failed task follows its own failure/rescue protocol.
If a failure invalidates the batch's design, stop integration and return to design rather than
integrating half of a plan known to be wrong.

On user interruption, report what completed, what remains active, and where each state is preserved.
Never abandon an in-flight write or discard its evidence silently.
