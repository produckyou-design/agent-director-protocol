# Concurrency Rules

This document defines when tasks may run in parallel and when they must run sequentially.

## Default: sequential

Only genuinely independent tasks run in parallel. Independence is not assumed; it is checked. If any
of the following overlap between two tasks, the director MUST default to running them sequentially
rather than in parallel:

- the same file
- the same data structure
- the same interface
- the same database schema
- the same shared configuration
- the same state management
- the same build or packaging configuration
- the same user flow

This list is deliberately conservative. When in doubt about overlap, treat it as overlapping.

## The conflict check

Before dispatching two or more tasks in parallel, the director MUST perform a conflict check using
the `conflict_domains` object on each task's [task contract](TASK-CONTRACT.md), matching [`../schemas/task-contract.schema.json`](../schemas/task-contract.schema.json): `files`, `data_structures`,
`interfaces`, `db_entities`, `shared_configs`, `state_stores`, `build_targets`, `user_flows`.

The check is a set intersection per key: for each key, take task A's array and task B's array and
check for any shared entry. If any key has a nonempty intersection, the pair is blocked from
parallel dispatch — the tasks are ordered sequentially instead, respecting whatever `depends_on`
relationship makes sense, or run one after the other even without a formal dependency.

**Two implementers must never modify the same file concurrently**, even if every other domain is
independent. A shared file is always sufficient to force sequencing, regardless of whether the two
tasks' changes seem "obviously" non-overlapping in intent — merge conflicts and silent overwrites
are exactly the failure mode this rule exists to prevent.

## Worked example

Two candidate tasks, both ready to dispatch:

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

Checking T-041 against T-042: `files` = `{orders.js}` vs `{inventory.js}` — no overlap. `interfaces`
— no overlap. `user_flows` = `{checkout}` vs `{inventory-lookup}` — no overlap. **Allowed pair**:
dispatch T-041 and T-042 in parallel.

Now consider a third task:

```json
{
  "task_id": "T-043",
  "conflict_domains": {
    "files": ["src/api/orders.js", "src/api/orderValidation.js"],
    "interfaces": ["POST /orders"],
    "user_flows": ["checkout"]
  }
}
```

Checking T-041 against T-043: `files` intersect at `orders.js`, `interfaces` intersect at `POST
/orders`, `user_flows` intersect at `checkout`. **Blocked pair**: T-041 and T-043 MUST run
sequentially, in dependency order or in the order the director chooses, never concurrently.

## Interaction with dependency ordering

A conflict-check failure is not the same as a `depends_on` relationship — the tasks may have no
logical dependency on each other's output, only a resource collision. In that case the director
sequences them (either order is valid) rather than declaring a false dependency. `depends_on` is
reserved for genuine "B needs A's output" relationships from [DELEGATION-PROTOCOL.md](DELEGATION-PROTOCOL.md)'s ordering step.
