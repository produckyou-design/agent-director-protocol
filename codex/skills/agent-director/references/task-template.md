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
    "reasoning_effort": "max",
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
- The initial set of `delegation.justification` values must explain why each
  contract's size and the total contract/worker count are the minimum safe
  structure. Identify conflict boundaries, dependencies, independent
  evidence/review needs, or blast-radius isolation and why fewer existing
  contracts/workers cannot absorb the work. A parallel batch must name at least
  two independently verifiable groups, prove pairwise-disjoint domains and
  empty dependency edges, and show the observed capacity used for
  `planned_workers`.
- Speed and efficiency may be recorded as outcomes, and an explicit latency
  priority may be recorded, but neither is a standalone reason for a worker or
  parallel mode. A mid-task addition still needs a new disclosure based on
  newly discovered evidence, a new conflict domain/dependency, a mandatory
  independent-review boundary, or a classified failure, including why an
  existing contract/worker cannot absorb it.
- `delegation.model` and `delegation.reasoning_effort` must match the
  explicit native spawn fields: `gpt-5.6-luna` and `max`. Defaults and
  named profiles are defense in depth, not a substitute for those fields.
- A named custom agent/type is omitted unless its loaded profile has been
  verified to pin the same model and effort. Runtime metadata must be checked
  before accepting output; a mismatch is rejected/closed and an unverifiable
  surface stops with a policy-violation/fallback report.
- A non-Luna/non-max exception requires explicit user authorization and a
  disclosure naming it.
- `conflict_domains` is not just a file list. Include interfaces, schemas, shared state, generated
  artifacts, and build/config targets whenever the task can affect them.
- `depends_on` is for real output dependencies. A conflict-only ordering decision should be stated
  in the disclosure without inventing a dependency. The batch-level work contract additionally
  discloses `independent_groups`, each group's `conflict_domains`, `dependency_edges`,
  `planned_workers`, `capacity_source`, `write_isolation`, and
  `why_fewer_workers_cannot_absorb`.
