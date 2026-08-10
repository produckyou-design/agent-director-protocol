# Agent Director Codex plugin

This is the explicit Codex skill switch for the Agent Director Protocol.

Install it from the repository marketplace:

```text
codex plugin marketplace add produckyou-design/agent-director-protocol
codex plugin add agent-director@agent-director-protocol-plugins
```

In a new Codex task/thread, invoke `$agent-director` or say "Director mode
on". The skill announces the current session as Director and requires every
ADP-created native worker spawn to include
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

Returned/runtime metadata must be checked when exposed. A mismatched worker is
rejected and closed and its output is discarded. If the surface cannot accept
or verify the pair, stop and report a policy violation/fallback requirement.
Any non-Luna/non-max exception needs explicit user authorization and disclosure.
At the max baseline, Codex Rescue is unavailable because no higher same-model
effort exists; preserve evidence and use the Core escalation/takeover gates.

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
