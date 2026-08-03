# Task contract template

Fill in every field before delegating a task to an implementer run. Fields mirror
[`schemas/task-contract.schema.json`](../../../../schemas/task-contract.schema.json) exactly — see
[TASK-CONTRACT.md](../../../../core/TASK-CONTRACT.md) for the rules behind each field. This template is
platform-neutral: paste the filled-in JSON as the prompt to whatever mechanism runs the implementer.

```json
{
  "task_id": "T-001",
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

## Field notes

- `task_id` — `^T-[0-9]{3,}$`, e.g. `T-001`. Unique within the project.
- `objective` / `target_behavior` — minimum 10 characters; state the *why* and the precise *after* behavior. "Improve X" is not valid.
- `must_read_files` vs `editable_files` vs `forbidden_files` — read-only context, allowed write scope, and explicitly off-limits files. Keep these three disjoint and exhaustive of what the implementer needs to know.
- `completion_criteria` and `test_commands` — each requires at least one entry. Every criterion must be objectively checkable; every command must be one the implementer can actually run and paste output from.
- `manual_verification` — may be an empty array when automated tests fully cover the behavior.
- `depends_on` — omit, or list task IDs that must already be reviewed-approved.
- `conflict_domains` — omit entirely for a task with no shared-resource risk. When present, any overlap with another in-flight task's `conflict_domains` forces sequential execution (see [CONCURRENCY-RULES.md](../../../../core/CONCURRENCY-RULES.md)).
