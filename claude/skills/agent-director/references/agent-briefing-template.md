# Agent Briefing Templates

Three mandatory, never-silent notices to the user. Full rules:
[`DELEGATION-PROTOCOL.md`](../../../../core/DELEGATION-PROTOCOL.md) step 7,
[`RESCUE-PROTOCOL.md`](../../../../core/RESCUE-PROTOCOL.md) Step 2.

---

## Part 1 — Agent composition disclosure

Sent once per batch, **before** spawning any implementer. Work does not start until this has been
stated. Mirrors
[`agent-composition-disclosure.schema.json`](../../../../schemas/agent-composition-disclosure.schema.json)
field for field.

### director_model / director_effort

### subagent_count

### subagents

One entry per subagent about to be spawned:

- `role` — e.g. implementer, reviewer-second-pass.
- `task` — task_id or short description this subagent owns.
- `model`
- `effort` — `low` / `medium` / `high` / `xhigh` / `max`.
- `justification` — why this piece needs its own subagent rather than folding into another task in
  this batch. "Smaller diffs" or "tidier task IDs" alone is not sufficient — see
  `DELEGATION-PROTOCOL.md` step 4's minimality principle.

### parallel

Whether these subagents run concurrently (per `CONCURRENCY-RULES.md` conflict-domain check) or
sequentially.

### rescue_agent_available

Whether a Rescue Agent promotion is actually reachable in this session/environment if a task fails
twice — e.g. whether a stronger model tier exists to promote to.

### within_preapproved_range

`true` if `subagent_count` is within the active profile's `director.max_batch_agents` → notify and
proceed. `false` → this disclosure is also an approval request; do not spawn anything until
`approval_status` becomes `granted`.

### approval_status (required when within_preapproved_range is false)

`not_required` / `pending` / `granted` / `denied`.

---

## Part 2 — Promotion notice

Sent the moment a task is promoted to a Rescue Agent (or a mid-task escalation request is granted) —
never a silent decision. Mirrors
[`promotion-notice.schema.json`](../../../../schemas/promotion-notice.schema.json)
field for field.

### task

### prior_model / prior_effort

### failure_count

At least 2 — the number of counted failed loops on this task.

### failed_approaches

- What each failed attempt actually tried — not "it didn't work."

### promotion_reason

The specific reason, tied to the RESCUE-PROTOCOL.md Step 1 classification (`reasoning_gap` or
`model_capability_gap`).

### rescue_model / rescue_effort

### editable_scope / forbidden_scope

### task_scoped_only

Always `true` — this promotion applies to this failed task only, not the session's default
subagent tier.

### within_preapproved_range

`true` → notify and proceed. `false` → this notice is also an approval request; do not start the
Rescue Agent until `approval_status` becomes `granted`.

### approval_status (required when within_preapproved_range is false)

`not_required` / `pending` / `granted` / `denied`.

---

## Part 3 — Rescue outcome notice

Sent when the Rescue Agent's work ends, success or failure — either way. Mirrors
[`rescue-outcome-notice.schema.json`](../../../../schemas/rescue-outcome-notice.schema.json)
field for field.

### task

### result

`success` or `failure`.

### files_changed

### tests_run

- `command` → verbatim `result`, not a paraphrase.

### director_verification

What the director itself independently checked (diff, re-run tests) — not a restatement of the
Rescue Agent's own report.

### integrated

Only `true` if `result` is `success` and `director_verification` passed. A failed attempt is never
integrated.

### reverted_to_baseline

Whether the task's promotion has ended and subsequent, unrelated tasks are back on the normal
implementer tier. State this explicitly — never leave it for the user to infer.

### next_step_if_failed (required when result is failure)

One of: `director_direct_intervention` / `rollback` / `escalate_to_user` / `reduce_scope` /
`convert_to_investigation` — the RESCUE-PROTOCOL.md Step 3 choice the director is making next.
