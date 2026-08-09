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
  justification, and `spawn_authority: director`.
- **`conflict_domains`** — The complete resource set for conflict checking. Include files, code
  regions, data structures, interfaces, schemas, database entities/migrations, shared configs, state
  stores, generated artifacts, build targets, and user flows when applicable. Empty arrays are valid
  only for domains that genuinely do not apply.

## Delegation fields

`delegation.role` is one of `investigator`, `implementer`, `reviewer`, or task-scoped `rescue`.
`delegation.model` records the actual worker model selected by the adapter or an explicit user
policy. `delegation.model_ceiling` records the active adapter policy ceiling.
`delegation.reasoning_effort` records the selected supported effort, not a promise
that every platform exposes the same labels. `delegation.execution` is `parallel` or `sequential`
after the conflict check. `delegation.justification` must explain why this work cannot be folded into
an existing contract or worker; “large task”, “many files”, and “efficiency” are not enough.

## Optional fields

- **`depends_on`** — Task IDs that must be reviewed and approved before this task starts.

## Example

The following is the minimum shape of a valid delegated contract; the complete example lives at
[`../examples/new-project/02a-task-contract.json`](../examples/new-project/02a-task-contract.json).

```json
{
  "task_id": "T-023",
  "title": "Add CSV export to reports",
  "objective": "Analysts need a reviewable export of the filtered report data.",
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
