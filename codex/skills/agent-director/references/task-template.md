# Task Contract Template

Fill every field before delegating. The shape mirrors
[`schemas/task-contract.schema.json`](../../../../schemas/task-contract.schema.json).

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
  "delegation": {
    "role": "implementer",
    "model": "gpt-5.6-luna",
    "model_ceiling": "gpt-5.6-luna",
    "reasoning_effort": "high",
    "execution": "sequential",
    "justification": "",
    "spawn_authority": "director"
  },
  "depends_on": [],
  "conflict_domains": {
    "files": [],
    "code_regions": [],
    "data_structures": [],
    "interfaces": [],
    "schemas": [],
    "db_entities": [],
    "shared_configs": [],
    "state_stores": [],
    "generated_artifacts": [],
    "build_targets": [],
    "user_flows": []
  }
}
```

## Field notes

- `objective` and `target_behavior` must explain the why and the precise after-state.
- `editable_files` and `forbidden_files` are disjoint and must contain every expected write boundary.
- `delegation.justification` must identify a concrete independent result, conflict boundary,
  investigation need, blast-radius boundary, or independent reviewer context. “For efficiency” or
  “many files” is not sufficient.
- `delegation.model_ceiling` is the adapter policy ceiling; a
  different model requires explicit user policy and disclosure.
- `conflict_domains` is not just a file list. Include interfaces, schemas, shared state, generated
  artifacts, and build/config targets whenever the task can affect them.
- `depends_on` is for real output dependencies. A conflict-only ordering decision should be stated
  in the disclosure without inventing a dependency.
