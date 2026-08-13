# Agent Briefing Templates

These are mandatory, never-silent notices. Full rules are in
[`DELEGATION-PROTOCOL.md`](../../../../core/DELEGATION-PROTOCOL.md) and
[`RESCUE-PROTOCOL.md`](../../../../core/RESCUE-PROTOCOL.md). The JSON shapes
mirror the schemas under `schemas/`.

## Part 1 — Agent composition disclosure

Send once per batch, **before** spawning any native subagent. Work does not
start until it has been stated.

```json
{
  "director_model": "<actual user-selected model>",
  "director_effort": "<low|medium|high|xhigh|max>",
  "director_model_source": "user_selected_session",
  "phase": "spawn",
  "user_visible": true,
  "work_contract": {
    "objective": "<checkable objective>",
    "scope": ["<files, interfaces, or state boundaries>"],
    "planned_contracts": 2,
    "planned_workers": 2,
    "worker_model": "<adapter-selected-worker-model>",
    "worker_reasoning_effort": "high",
    "minimum_safe_rationale": "Two independently verifiable work groups have disjoint domains and require separate evidence; one worker cannot preserve those independent review boundaries.",
    "independent_groups": [
      {
        "group_id": "G-001",
        "scope": ["src/auth/*"],
        "independently_verifiable": true,
        "conflict_domains": {
          "files": ["src/auth/*"],
          "code_regions": [],
          "interfaces": ["POST /api/login"],
          "schemas": [],
          "generated_artifacts": [],
          "shared_configs": [],
          "state_stores": [],
          "data_structures": [],
          "db_entities": [],
          "build_targets": [],
          "user_flows": ["login"]
        }
      },
      {
        "group_id": "G-002",
        "scope": ["src/session/*"],
        "independently_verifiable": true,
        "conflict_domains": {
          "files": ["src/session/*"],
          "code_regions": [],
          "interfaces": ["SessionService"],
          "schemas": [],
          "generated_artifacts": [],
          "shared_configs": [],
          "state_stores": [],
          "data_structures": [],
          "db_entities": [],
          "build_targets": [],
          "user_flows": ["session-validation"]
        }
      }
    ],
    "dependency_edges": [],
    "capacity_source": "observed_native_runtime",
    "observed_capacity": 2,
    "write_isolation": "isolated",
    "why_fewer_workers_cannot_absorb": "Each group has its own verification path and disjoint write domain; folding them into one worker would remove the required independent evidence boundary.",
    "tests": ["<exact test command>"],
    "stop_conditions": ["<failure, capacity, or verification stop condition>"]
  },
  "subagent_count": 2,
  "subagents": [
    {
      "role": "implementer",
      "task": "T-001 authentication correction",
      "model": "<adapter-selected-worker-model>",
      "model_ceiling": "<adapter-worker-model-ceiling>",
      "effort": "max",
      "justification": "This group has an independently verifiable result and a disjoint authentication domain; it cannot be folded into the session group without losing isolation.",
      "model_source": "native_subagent",
      "conflict_domains": {
        "files": ["src/auth/*"],
        "interfaces": ["POST /api/login"]
      }
    },
    {
      "role": "implementer",
      "task": "T-002 session validation correction",
      "model": "<adapter-selected-worker-model>",
      "model_ceiling": "<adapter-worker-model-ceiling>",
      "effort": "high",
      "justification": "This group has an independently verifiable result and a disjoint session domain with no dependency edge to T-001.",
      "model_source": "native_subagent",
      "conflict_domains": {
        "files": ["src/session/*"],
        "interfaces": ["SessionService"]
      }
    }
  ],
  "execution_mode": "parallel",
  "rescue_agent_available": false,
  "within_preapproved_range": true,
  "approval_status": "not_required",
  "spawn_budget": {
    "already_spawned_count": 0,
    "this_batch_count": 2,
    "total_after_spawn": 2,
    "capacity_source": "observed_native_runtime",
    "capacity_known": true,
    "observed_capacity": 2
  }
}
```

`execution_mode` is `parallel` only when there are at least two independently
verifiable groups, their complete conflict domains are pairwise disjoint, and
`dependency_edges` is empty. A shared/conflicting or sequential write domain
uses one worker. With known native capacity of at least two,
`planned_workers = min(independent-group count, observed_capacity)`; with
unknown capacity, use one sequential worker and record `capacity_source` as
`unknown` without inventing a cap. The work contract must disclose
`independent_groups`, `conflict_domains`, `dependency_edges`,
`planned_workers`, `capacity_source`, `write_isolation`, and
`why_fewer_workers_cannot_absorb`. `spawn_budget` records request accounting
and the capacity observation supplied by the native runtime.
`within_preapproved_range` and `approval_status` describe any separately
authorized policy exception and do not create worker-capacity authority.

## Part 2 — Promotion notice

Send when a failed task is promoted to a Rescue Agent or a granted mid-task
escalation begins. Rescue keeps the same model and raises effort only.

Required fields:

- `task`
- `prior_model` / `prior_effort`
- `failure_count` — at least the active policy threshold
- `failed_approaches`
- `promotion_reason` — `reasoning_gap` or `model_capability_gap`
- `rescue_model` — equal to `prior_model`
- `model_ceiling`
- `rescue_effort`
- `editable_scope` / `forbidden_scope`
- `task_scoped_only: true`
- `within_preapproved_range` and conditional `approval_status`

If the worker is already at its model's maximum supported effort, do not emit a
fake promotion; record that Rescue is unavailable and use the Core escalation
path.

## Part 3 — Rescue outcome notice

Send when the Rescue Agent ends, whether it succeeds or fails. Include:

- `task` and `result` (`success` or `failure`);
- actual `files_changed`;
- `tests_run` with verbatim `result` for each command;
- the director's independent diff/test verification;
- `integrated` only after verification passes;
- `reverted_to_baseline` explicitly;
- `next_step_if_failed` when the result is failure.
