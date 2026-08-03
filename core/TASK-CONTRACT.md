# Task Contract

This document narrates every field a director must fill in before delegating work to an implementer,
matching [`../schemas/task-contract.schema.json`](../schemas/task-contract.schema.json) exactly.

A task contract is the only valid unit of delegation. If a field below cannot be filled in
concretely, the task is not ready to be delegated — return to [DELEGATION-PROTOCOL.md](DELEGATION-PROTOCOL.md).

## Required fields

- **`task_id`** — Unique identifier matching `^T-[0-9]{3,}$`, e.g. `T-001`. Lets every other
  document (reviews, failure loops, takeover records) reference this task unambiguously.
- **`title`** — Short human-readable name. Exists for humans scanning a task list, not for machine
  logic.
- **`objective`** — Why this task exists. Ties the task back to the requirement so an implementer
  understands intent, not just mechanics, and can make sane judgment calls on ambiguous edge cases
  within scope.
- **`current_state`** — The observed state of the code or behavior before this task starts. Prevents
  the implementer from working off an assumed baseline instead of the real one, and gives the
  reviewer a "before" to compare against.
- **`target_behavior`** — Precise description of behavior after the task is done. This is the
  specification the implementer builds to and the reviewer checks against; it must be precise enough
  that two different people would agree on whether it was met.
- **`must_read_files`** — Files the implementer must read before changing anything. Ensures the
  implementer has the necessary context (existing conventions, adjacent logic, related tests) before
  writing code.
- **`editable_files`** — Files or glob patterns the implementer is allowed to modify or create.
  Defines the positive boundary of the task's scope.
- **`forbidden_files`** — Files or glob patterns the implementer must not touch. Defines the
  negative boundary; often used to protect files another in-flight task owns, or files whose
  interfaces must not shift. See [CONCURRENCY-RULES.md](CONCURRENCY-RULES.md).
- **`interfaces_to_preserve`** — Public functions, endpoints, CLI flags, schemas, or contracts that
  must remain unchanged. Gives the reviewer a specific, checkable list for the
  `interfaces_preserved` gate in [REVIEW-GATES.md](REVIEW-GATES.md).
- **`input_format`** — Expected input shape for the changed behavior. Use `"n/a"` when the task has
  no meaningful input shape (e.g. a pure styling fix).
- **`output_format`** — Expected output shape for the changed behavior. Use `"n/a"` when not
  applicable.
- **`error_handling`** — Error situations that must be handled, and how. Prevents an implementation
  that only covers the happy path.
- **`preservation_conditions`** — Existing behavior that must not regress. Feeds directly into the
  reviewer's `no_regressions` check.
- **`completion_criteria`** — Array (at least one entry) of objective, checkable conditions that
  define done. These are what the implementer reports against in `completion_criteria_status` and
  what the reviewer checks in `completion_criteria_met`.
- **`test_commands`** — Array (at least one entry) of exact commands the implementer must run and
  report results for. Exact commands, not descriptions, so results are reproducible by the reviewer.
- **`manual_verification`** — Manual verification steps for cases automated tests cannot cover. May
  be an empty array when automated tests fully cover the behavior.
- **`report_format`** — The required report schema, normally the literal string
  `"implementation-report.schema.json"`.

## Optional fields

- **`depends_on`** — Array of `task_id`s that must be completed and reviewed before this task
  starts. Used for dependency ordering.
- **`conflict_domains`** — Object describing resources this task touches, used for the
  parallel-dispatch conflict check: `files`, `data_structures`, `interfaces`, `db_entities`,
  `shared_configs`, `state_stores`, `build_targets`, `user_flows`, each an array of strings. See [CONCURRENCY-RULES.md](CONCURRENCY-RULES.md)
  for how this is used before dispatching two tasks in parallel.

## Example

The following validates against the schema:

```json
{
  "task_id": "T-023",
  "title": "Add CSV export to reports page",
  "objective": "Analysts need to download report data for offline processing in spreadsheet tools.",
  "current_state": "The reports page renders a table with no export option.",
  "target_behavior": "An 'Export CSV' button downloads the currently filtered table as a CSV file matching the visible columns.",
  "must_read_files": ["src/pages/Reports.jsx", "src/lib/table.js"],
  "editable_files": ["src/pages/Reports.jsx", "src/lib/csvExport.js"],
  "forbidden_files": ["src/lib/table.js"],
  "interfaces_to_preserve": ["Reports.jsx default export signature"],
  "input_format": "The currently rendered table's row/column data",
  "output_format": "A downloaded .csv file with a header row matching visible column labels",
  "error_handling": ["Export button disabled when the table has zero rows"],
  "preservation_conditions": ["Existing filtering and sorting behavior unchanged"],
  "completion_criteria": ["Clicking Export CSV downloads a file", "File contents match visible filtered rows"],
  "test_commands": ["npm test -- Reports"],
  "manual_verification": ["Filter table, click Export CSV, open downloaded file and confirm rows match"],
  "report_format": "implementation-report.schema.json"
}
```
