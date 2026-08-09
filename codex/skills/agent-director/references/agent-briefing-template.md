# Agent Briefing Templates

These are mandatory, never-silent notices. Full rules are in
[`DELEGATION-PROTOCOL.md`](../../../../core/DELEGATION-PROTOCOL.md) and
[`RESCUE-PROTOCOL.md`](../../../../core/RESCUE-PROTOCOL.md). The JSON shapes
mirror the schemas under `schemas/`.

## Part 1 — Agent composition disclosure

Send once per batch, **before** spawning any native subagent. Work does not
start until it has been stated.

Before the schema-shaped JSON, state
`contract_scale_justification: <minimum structure and why fewer existing
contracts/workers cannot absorb it>`. Base it on conflict boundaries,
dependencies, independent evidence/review, or blast-radius isolation. Reject
speed, parallelism, efficiency, task size/complexity, file count, context
reduction, empty slots, and tidy/smaller IDs.

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
      "model": "gpt-5.6-luna",
      "model_ceiling": "gpt-5.6-luna",
      "effort": "max",
      "justification": "An independent read-only root-cause result is required before implementation can be safely contracted.",
      "model_source": "explicit_native_spawn",
      "conflict_domains": {
        "files": ["src/auth/*"],
        "interfaces": ["POST /api/login"]
      }
    },
    {
      "role": "implementer",
      "task": "T-002 session validation correction",
      "model": "gpt-5.6-luna",
      "model_ceiling": "gpt-5.6-luna",
      "effort": "max",
      "justification": "The correction is an independently verifiable bounded implementation after the investigation result.",
      "model_source": "explicit_native_spawn",
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
    "max_total_spawned_agents_per_request": 12,
    "within_limit": true
  }
}
```

`execution_mode` is `parallel` only after the conflict check proves the
workers independent. `within_preapproved_range` concerns the batch limit;
`spawn_budget.within_limit` concerns the cumulative request limit. These are
separate controls. Every native spawn in this disclosure must also carry
`model="gpt-5.6-luna"` and
`reasoning_effort="max"` explicitly. If a named profile is used,
record that it was verified against those fields. If runtime metadata is
missing or mismatched, stop accepting the worker result; mismatch requires
reject/close and missing verification requires a fallback report.

## Part 2 — Promotion notice

Send when a failed task is promoted to a Rescue Agent or a granted mid-task
escalation begins. Rescue keeps the same model and raises effort only. At the
normal `max` baseline there is no same-model headroom, so ordinary Codex ADP
runs record Rescue as unavailable and use the Core escalation/takeover gates.

Before any mid-task contract/agent/investigator/reviewer/revision/rescue
addition, send a new disclosure and state `addition_justification`. Classify
it as newly discovered evidence, a new conflict domain/dependency, a mandatory
independent-review boundary, or a classified failure, and explain why an
existing contract/worker cannot absorb it.

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
