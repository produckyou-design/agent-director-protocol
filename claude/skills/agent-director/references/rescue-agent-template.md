# Rescue Agent Scope Package Template

The bounded package the director hands to a one-shot Rescue Agent, after classifying a twice-failed
task as `reasoning_gap` or `model_capability_gap`. Mirrors
[`rescue-agent-task.schema.json`](../../../../schemas/rescue-agent-task.schema.json)
field for field. Full rule: [`RESCUE-PROTOCOL.md`](../../../../core/RESCUE-PROTOCOL.md).

Before filling this in, send the user a
[promotion notice](agent-briefing-template.md#part-2--promotion-notice) — and wait for approval if it
falls outside the user's pre-approved model/effort range or needs extra cost.

## failed_task_id

`T-###` — unmodified by hindsight.

## failure_classification

`reasoning_gap` or `model_capability_gap` only. If the real cause is `requirement_conflict` or
`environment_issue`, do not fill in this template — go straight to
[RESCUE-PROTOCOL.md](../../../../core/RESCUE-PROTOCOL.md) Step 3.

## attempt_1 / attempt_1_result

What the first failed attempt changed, and the verbatim evidence of its outcome.

## attempt_2 / attempt_2_result

What the second failed attempt changed — a genuinely different approach — and its verbatim outcome.

## confirmed_facts

- What is actually established, with evidence, across both attempts.

## unresolved_points

- What remains uncertain after both attempts.

## last_passing_checkpoint

The commit, tag, or green-test state immediately before the first failed attempt. Preserve this
before the Rescue Agent starts. Prefer an isolated branch/worktree from this checkpoint over
continuing the failed implementer's working state — the failed attempts are reference material, not
a forced starting point.

## editable_files

- `path/to/file`

## forbidden_files

- `path/to/file`

## forbidden_scope

What the Rescue Agent may NOT do — e.g. redesign unrelated modules, change shared contracts not
implicated by this failure. The Rescue Agent does not redesign the project.

## completion_criteria

- Objective, checkable criteria.

## test_commands (optional)

- `command`

## assigned_model / assigned_effort

The director's explicit choice — never automatic. Effort: `low` / `medium` / `high` / `xhigh` /
`max`.

## max_attempts

Fixed at `2`. Tracked separately from the implementer's own failure-loop count.

## attempt_number

`1` or `2` — which Rescue Agent attempt this is.

---

When the Rescue Agent's work ends, send the matching
[outcome notice](agent-briefing-template.md#part-3--rescue-outcome-notice) — success or failure,
either way.
