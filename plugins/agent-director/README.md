# Agent Director Codex plugin

This is the Codex Agent Director workflow for the Agent Director Protocol. It
is applied by default to repository and code tasks; explicit invocation is
also supported when the user wants to make the policy visible.

Install it from the repository marketplace:

```text
codex plugin marketplace add produckyou-design/agent-director-protocol
codex plugin add agent-director@agent-director-protocol-plugins
```

In a new Codex task/thread, the skill is applied automatically when the task
is repository or code work. `$agent-director` or "Director mode on" remains an
optional explicit invocation. The skill announces the current session as
Director and requires every ADP-created native worker spawn to include
`model="gpt-5.6-luna"` and
`reasoning_effort="max"`. The user-selected model continues to own
the Director session; it is never inherited by a worker.

The plugin is a behavior/instruction switch, not a hidden model or runtime
toggle. It does not retroactively reload an existing task, install project
files, or change a running session's model. Defaults and named profiles are
defense in depth. Prefer no named custom agent/type; if one is used, verify
its profile is pinned to the same pair before dispatch.

Every task begins with a visible `task_start` work-contract notice. A
read-only task may plan zero workers only when it marks
`work_contract.read_only: true`; worker batches use `spawn` and require
positive totals. Any later worker, contract, revision, rescue, reviewer, or
scope addition requires a new `addition` notice stating the changed scope,
what the new worker will do, a classified reason, and why an existing worker
cannot absorb it. The repository can validate this contract but cannot
intercept the platform-owned `multi_agent_v1__spawn_agent` call.

The Director is the coordinator and reviewer, not the ordinary implementer.
Implementation and other state changes require a positive worker total. When
files overlap, use one sequential implementer; do not convert the conflict to
zero workers and direct Director edits. Luna/max on the Director session does
not remove this boundary. Direct takeover is never automatic: the failure,
escalation, rescue, and takeover gates are evidence gates only. It requires
explicit current-session user authorization after a takeover disclosure,
followed by the required record and independent review. “Fix it” and “Director
mode” do not authorize direct product-code implementation.

Returned/runtime metadata must be checked when exposed. A mismatched worker is
rejected and closed and its output is discarded. If the surface cannot accept
or verify the pair, stop and report a policy violation/fallback requirement.
Any non-Luna/non-max exception needs explicit user authorization and disclosure.
At the max baseline, Codex Rescue is unavailable because no higher same-model
effort exists; preserve evidence and stop/report or ask the user. Do not turn
Rescue failure into automatic Director takeover.

Native worker recovery is bounded and fail-closed. A wait timeout is not a
result. For a stuck worker, send one interrupting input with `interrupt=true`,
bounded-wait, then close once if it remains non-final; do not repeatedly
resume it. Use a fresh implementer under a new addition disclosure. Closing
or resuming does not merge fork changes into the main tree, so inspect and
review the fork diff or implementation report before integration. A named
implementer uses `fork_context=false` or omission; `fork_context=true` is
compatible only when `agent_type` is omitted. Serialization failure is a
pre-spawn dispatch failure, not an implementation failure. Rescue is
unavailable at the active Luna/max baseline.

The timeout path is progress-aware. A timeout only means that no final result
arrived. Recent worker/tool output, a status transition, an active command, or
other declared progress keeps the worker alive; an expired wait window alone
never authorizes interrupt, close, splitting, or re-dispatch. Acceptance
evidence without a final message is recorded as `completed_work_unreported`.
Only a no-progress running state over the declared observation window is
`stalled` and permits one interrupt, one bounded wait, and one close. If the
native surface exposes no progress signal, report `unknown` rather than
inventing a stall.

Initial decomposition must justify why its contract size and total
contract/worker count are minimal, using conflict boundaries, dependencies,
independent evidence/review, or blast-radius isolation and explaining why fewer
existing contracts cannot absorb the work. Mid-task additions require a new
disclosure grounded in newly discovered evidence, a new conflict/dependency,
a mandatory independent-review boundary, or a classified failure, plus why an
existing worker cannot absorb it. Speed, parallelism, efficiency, task
size/complexity, file count, context reduction, empty slots, and tidy/smaller
IDs are rejected.

For persistent project defaults, follow
[codex/INSTALL.md](../../codex/INSTALL.md) and install the project's
`AGENTS.md`, `.codex/config.toml`, and role profiles. Personal custom
agents may be placed under `$CODEX_HOME/agents/`, but they still require
explicit per-spawn model/effort fields and the same metadata verification.

Never place API keys, access tokens, or private transcripts in this plugin.
