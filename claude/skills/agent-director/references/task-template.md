# Task Contract Template

Fill in every field before delegating to an implementer. This mirrors
[`task-contract.schema.json`](../../../../schemas/task-contract.schema.json)
field for field. A vague scope ("improve the feature", "fix the UI") is not
a valid contract — see
[`TASK-CONTRACT.md`](../../../../core/TASK-CONTRACT.md).

## task_id

`T-###` (3+ digits), e.g. `T-001`.

## title

Short human-readable task name.

## objective

Why this task exists — the purpose of the work (min 10 characters).

## current_state

Observed state of the code/behavior before this task.

## target_behavior

Precise description of the behavior after the task is done (min 10
characters).

## must_read_files

Files the implementer must read before changing anything.

- `path/to/file`

## editable_files

Files (or glob patterns) the implementer is allowed to modify or create.

- `path/to/file`

## forbidden_files

Files (or glob patterns) the implementer must not touch.

- `path/to/file`

## interfaces_to_preserve

Public functions, endpoints, CLI flags, schemas, or contracts that must
remain unchanged.

- `...`

## input_format

Expected input shape for the changed behavior. Use `n/a` when not
applicable.

## output_format

Expected output shape for the changed behavior. Use `n/a` when not
applicable.

## error_handling

Error situations that must be handled, and how.

- `...`

## preservation_conditions

Existing behavior that must not regress.

- `...`

## completion_criteria

Objective, checkable conditions that define done (at least one required).

1. `...`

## test_commands

Exact commands the implementer must run and report results for (at least one
required).

- `...`

## manual_verification

Manual verification steps, when automated tests are insufficient. May be
empty.

- `...`

## report_format

Normally: `implementation-report.schema.json`.

## depends_on (optional)

Task IDs that must be completed and reviewed before this task starts.

- `T-###`

## conflict_domains (optional)

Resources this task touches, used for the parallel-execution conflict check.
Any overlap with another in-flight task forces sequential execution. Leave a
sub-key out (or empty) if not applicable.

- `files`: `...`
- `data_structures`: `...`
- `interfaces`: `...`
- `db_entities`: `...`
- `shared_configs`: `...`
- `state_stores`: `...`
- `build_targets`: `...`
- `user_flows`: `...`

---

## JSON skeleton

```json
{
  "task_id": "T-###",
  "title": "",
  "objective": "",
  "current_state": "",
  "target_behavior": "",
  "must_read_files": [],
  "editable_files": [],
  "forbidden_files": [],
  "interfaces_to_preserve": [],
  "input_format": "",
  "output_format": "",
  "error_handling": [],
  "preservation_conditions": [],
  "completion_criteria": [],
  "test_commands": [],
  "manual_verification": [],
  "report_format": "implementation-report.schema.json",
  "depends_on": [],
  "conflict_domains": {
    "files": [],
    "data_structures": [],
    "interfaces": [],
    "db_entities": [],
    "shared_configs": [],
    "state_stores": [],
    "build_targets": [],
    "user_flows": []
  }
}
```
