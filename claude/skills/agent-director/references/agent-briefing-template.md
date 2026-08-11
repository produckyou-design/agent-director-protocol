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
  "subagent_count": 2,
  "subagents": [
    {
      "role": "investigator",
      "task": "T-001 root-cause investigation",
      "model": "<adapter-selected-worker-model>",
      "model_ceiling": "<adapter-worker-model-ceiling>",
      "effort": "max",
      "justification": "An independent read-only root-cause result is required before implementation can be safely contracted.",
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
      "justification": "The correction is an independently verifiable bounded implementation after the investigation result.",
      "model_source": "native_subagent",
      "conflict_domains": {
        "files": ["src/session/*"],
        "interfaces": ["SessionService"]
      }
    }
  ],
  "execution_mode": "sequential",
  "rescue_agent_available": true,
  "within_preapproved_range": true,
  "approval_status": "not_required",
  "spawn_budget": {
    "already_spawned_count": 0,
    "this_batch_count": 2,
    "total_after_spawn": 2,
    "capacity_source": "observed_native_runtime",
    "capacity_known": false,
    "observed_capacity": null
  }
}
```

`execution_mode` is `parallel` only after the conflict check proves the
workers independent. `spawn_budget` records request accounting and the
capacity observation supplied by the native runtime. If that observation is
unavailable, keep `capacity_known` false and `observed_capacity` null; the
disclosure must not invent a project worker cap. `within_preapproved_range`
and `approval_status` describe any separately authorized policy exception and
do not create worker-capacity authority.

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
