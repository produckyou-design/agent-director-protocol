# Task Contract

This document narrates every field a director must fill in before delegating work, matching
[`../schemas/task-contract.schema.json`](../schemas/task-contract.schema.json). A Task Contract is
the only valid unit of delegation.

## Required fields

- **`task_id`** — Unique identifier matching `^T-[0-9]{3,}$`.
- **`title`** — Short human-readable task name.
- **`objective`** — Why the task exists, tied to the request.
- **`current_state`** — Observed behavior or code state before work starts.
- **`target_behavior`** — Precise after-state that a reviewer can check.
- **`must_read_files`** — Context files the worker must read first.
- **`editable_files`** — Positive write boundary; workers may not edit outside it.
- **`forbidden_files`** — Explicit negative boundary, including another task's files.
- **`interfaces_to_preserve`** — Public functions, endpoints, flags, schemas, and contracts that
  must not change unintentionally.
- **`input_format` / `output_format`** — Expected shapes, or `n/a` when not applicable.
- **`error_handling`** — Failure conditions and required behavior.
- **`preservation_conditions`** — Existing behavior that must not regress.
- **`completion_criteria`** — At least one objective, checkable condition.
- **`test_commands`** — At least one exact executable command whose output the worker must report.
- **`manual_verification`** — Manual checks when automation is insufficient; may be empty.
- **`report_format`** — Normally `implementation-report.schema.json`.
- **`delegation`** — The role, model, model ceiling, reasoning effort, execution mode, concrete
  justification, and `spawn_authority: director`. `execution: parallel` is valid only after the
  batch-level independent-group, disjoint-domain, empty-dependency, isolation, and capacity checks.
- **`goal`** — The concrete goal assigned to this worker; it is not inferred from `objective`.
- **`success_criteria`** — Objective conditions this worker must satisfy.
- **`failure_criteria`** — Conditions requiring the worker to report failure or stop.
- **`termination_criteria`** — Conditions that end the worker's assignment without further work.
- **`required_evidence`** — The evidence and deliverables the worker must return to the parent.
- **`conflict_domains`** — The complete resource set for conflict checking. Include files, code
  regions, data structures, interfaces, schemas, database entities/migrations, shared configs, state
  stores, generated artifacts, build targets, and user flows when applicable. Empty arrays are valid
  only for domains that genuinely do not apply.

## Delegation fields

`delegation.role` is one of `investigator`, `implementer`, `reviewer`, or task-scoped `rescue`,
assigned before the subagent is created. `director` is never a valid worker role: a spawned
subagent is never a Director under any circumstance, and only the root/current parent session is
Director. A missing or ambiguous role is a pre-spawn failure.
`delegation.model` records the actual worker model selected by the adapter or an explicit user
policy. `delegation.model_ceiling` records the active adapter policy ceiling.
`delegation.reasoning_effort` records the selected supported effort, not a promise
that every platform exposes the same labels. `delegation.execution` is `parallel` or `sequential`
after the deterministic batch check. `delegation.justification` must identify the independently
verifiable result, conflict boundary, dependency state, isolation/review need, and why an existing
worker cannot absorb it. Speed, parallelism, or efficiency claims alone do not qualify; an explicit
latency priority may be recorded only as an optional priority after the eligibility proof.

The per-worker contract must also make scope and non-goals explicit through the positive
`editable_files` boundary and negative `forbidden_files` boundary. The worker-specific `goal`,
`success_criteria`, `failure_criteria`, `termination_criteria`, and `required_evidence` fields are
mandatory. The overall `objective`, `completion_criteria`, and `error_handling` fields do not
substitute for them.

## Optional fields

- **`depends_on`** — Task IDs that must be reviewed and approved before this task starts.

## Batch work-contract disclosure

The visible batch work contract (the `work_contract` object in
[`agent-composition-disclosure.schema.json`](../schemas/agent-composition-disclosure.schema.json))
must add these dispatch fields for new task/state-changing disclosures:

- **`independent_groups`** — At least two groups for a parallel batch; each group needs its own
  independently verifiable completion/evidence path and complete `conflict_domains`.
- **`dependency_edges`** — The explicit cross-group edges, including `depends_on`, read/write
  consistency, generated-output, and integration dependencies. It must be empty for parallel work.
- **`planned_workers`** — `min(independent-group count, observed native runtime capacity)` when the
  parallel proof passes and capacity is known; `1` for a sequential/shared write domain or the
  conservative unknown-capacity fallback.
- **`capacity_source`** — The observed native runtime source, or `unknown`; a project cap must never
  be invented.
- **`write_isolation`** — `isolated` for parallel writes, `read_only` for parallel read-only work,
  or `sequential` when shared state must remain under one worker.
- **`why_fewer_workers_cannot_absorb`** — Why one worker cannot safely absorb the independently
  verifiable groups, or why one worker is the minimum safe owner of a sequential/shared domain.

These fields are optional in the JSON Schema for backward compatibility with previously recorded
disclosures, but the current protocol requires them in every new non-read-only work-contract
disclosure. They do not override native capacity or authorize automatic Director takeover.

## Example

The following is the minimum shape of a valid delegated contract; the complete example lives at
[`../examples/new-project/02a-task-contract.json`](../examples/new-project/02a-task-contract.json).

```json
{
  "task_id": "T-023",
  "title": "Add CSV export to reports",
  "objective": "Analysts need a reviewable export of the filtered report data.",
  "goal": "Implement the bounded CSV export behavior for the reports page and return the required test evidence.",
  "current_state": "The reports page renders filtered rows but has no export action.",
  "target_behavior": "The page downloads the visible filtered columns as a CSV file.",
  "must_read_files": ["src/pages/Reports.jsx"],
  "editable_files": ["src/pages/Reports.jsx", "src/lib/csvExport.js"],
  "forbidden_files": ["src/lib/table.js"],
  "interfaces_to_preserve": ["Reports.jsx default export"],
  "input_format": "The visible filtered table rows and column labels",
  "output_format": "A UTF-8 .csv download with a header row",
  "error_handling": ["Disable export when there are no rows"],
  "preservation_conditions": ["Existing filtering and sorting remain unchanged"],
  "completion_criteria": ["The download contains exactly the visible rows"],
  "success_criteria": [
    "The export uses the current filter state and produces a valid CSV download.",
    "The named test command passes and its output is reported verbatim."
  ],
  "failure_criteria": [
    "The worker cannot implement the goal within editable_files or a required test fails after scoped fixes."
  ],
  "termination_criteria": [
    "Stop without further edits when the goal is met and required evidence is captured.",
    "Stop and report when the parent contract is ambiguous or an out-of-scope dependency is required."
  ],
  "required_evidence": [
    "List of changed files, exact test commands, and verbatim test output.",
    "A note mapping each success criterion to concrete evidence and any out-of-scope issue."
  ],
  "test_commands": ["npm test -- Reports"],
  "manual_verification": ["Filter rows, export, and compare the downloaded file"],
  "report_format": "implementation-report.schema.json",
  "delegation": {
    "role": "implementer",
    "model": "<adapter-selected-worker-model>",
    "model_ceiling": "<adapter-worker-model-ceiling>",
    "reasoning_effort": "high",
    "execution": "sequential",
    "justification": "The export is an independently verifiable UI result with its own bounded write scope.",
    "spawn_authority": "director"
  },
  "conflict_domains": {
    "files": ["src/pages/Reports.jsx", "src/lib/csvExport.js"],
    "interfaces": ["Reports visible-table export"],
    "user_flows": ["reports-export"]
  }
}
```
