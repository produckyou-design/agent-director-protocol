# Review Result Template

Fill in after independently verifying an implementation report — reading the
actual diff and re-running the test commands yourself. Mirrors
[`review-result.schema.json`](../../../../schemas/review-result.schema.json)
field for field. Full gates:
[`REVIEW-GATES.md`](../../../../core/REVIEW-GATES.md).

## task_id

`T-###`

## loop_number

Integer, 1 or greater. 1 = the first implementation attempt for this task.

## verdict

One of: `approved` | `revision_required` | `rejected`

## checks

Ten checks are mandatory. For each: `result` is `pass` | `fail` |
`not_applicable`, and `evidence` states what you actually inspected (a diff
excerpt, a test command's real output, a specific file) — not what the
implementer claimed.

| Check | Result | Evidence |
|---|---|---|
| `code_actually_changed` | | |
| `feature_wired_into_flow` | | |
| `tests_actually_executed` | | |
| `test_results_match_report` | | |
| `no_fake_or_placeholder_success` | | |
| `no_regressions` | | |
| `interfaces_preserved` | | |
| `no_out_of_scope_changes` | | |
| `error_handling_present` | | |
| `completion_criteria_met` | | |

## failure_reasons

Required when `verdict` is not `approved`. Choose only from the canonical
enum — style or taste differences are never failure reasons.

`completion_criteria_unmet` | `test_failure` | `not_runnable` | `regression` |
`interface_violation` | `placeholder_implementation` | `fake_success` |
`not_wired_into_flow` | `instruction_not_applied` | `repeated_same_error`

- `...`

## revision_instructions

Required when `verdict` is `revision_required`. Each entry needs concrete,
evidence-based content — see also `revision-template.md` for a fuller
per-instruction template.

- **instruction**: (min 10 characters, specific and actionable)
  **target_files**: `path/to/file`
  **evidence**: (the test output, diff excerpt, or reproduction that
  motivates this instruction)

## additional_tests_required (optional)

Integration, regression, or user-flow tests the director adds beyond the
implementer's own tests.

- `...`

## notes (optional)

`...`
