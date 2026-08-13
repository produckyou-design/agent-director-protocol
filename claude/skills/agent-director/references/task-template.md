# Task Contract Template

Fill every field before delegating. The shape mirrors
[`schemas/task-contract.schema.json`](../../../../schemas/task-contract.schema.json).

Before creation, the root/current parent session must assign
`delegation.role` as a non-Director worker role. A spawned subagent is never a
Director under any circumstance; `director` is invalid, and a missing or
ambiguous role is a pre-spawn failure. Replace the placeholders below with the
parent-assigned role and worker-specific contract values before spawning.

```json
{
  "task_id": "T-001",
  "title": "",
  "objective": "",
  "goal": "",
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
  "success_criteria": [],
  "failure_criteria": [],
  "termination_criteria": [],
  "required_evidence": [],
  "test_commands": [],
  "manual_verification": [],
  "report_format": "implementation-report.schema.json",
  "delegation": {
    "role": "implementer",
    "model": "<adapter-selected-worker-model>",
    "model_ceiling": "<adapter-worker-model-ceiling>",
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
- `goal` is the concrete goal for this worker; fill `success_criteria`,
  `failure_criteria`, `termination_criteria`, and `required_evidence` with
  worker-specific values before creation. Scope and non-goals must be explicit
  through `editable_files` and `forbidden_files`.
- `delegation.role` is assigned by the root/current parent before creation and
  must be a non-Director role (`investigator`, `implementer`, `reviewer`, or
  task-scoped `rescue`). `director` is invalid; a missing or ambiguous role is
  a pre-spawn failure.
- `editable_files` and `forbidden_files` are disjoint and must contain every expected write boundary.
- `delegation.justification` must identify a concrete independent result, conflict boundary,
  investigation need, blast-radius boundary, or independent reviewer context. A parallel batch must
  name at least two independently verifiable groups, disjoint domains, empty dependency edges, and
  the observed capacity used for `planned_workers`. Speed and efficiency may be outcomes or an
  explicit latency priority, but neither is a standalone justification.
- `delegation.model_ceiling` is the active adapter policy ceiling; a
  different model requires explicit user policy and disclosure.
- `conflict_domains` is not just a file list. Include interfaces, schemas, shared state, generated
  artifacts, and build/config targets whenever the task can affect them.
- `depends_on` is for real output dependencies. A conflict-only ordering decision should be stated
  in the disclosure without inventing a dependency. The batch-level work contract additionally
  discloses `independent_groups`, each group's `conflict_domains`, `dependency_edges`,
  `planned_workers`, `capacity_source`, `write_isolation`, and
  `why_fewer_workers_cannot_absorb`.
