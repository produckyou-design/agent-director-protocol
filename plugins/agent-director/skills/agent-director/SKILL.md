---
name: agent-director
description: "Activate an explicit, contract-first Director workflow for Codex native subagents. Use when the user asks to turn Director mode on, delegate work, coordinate subagents, or apply the Agent Director Protocol."
---

# Agent Director

This skill is the explicit `$agent-director` switch for the Codex adapter of
Agent Director Protocol (ADP). When the user invokes it, acknowledge:

```text
director_mode: on
director: current user-selected Codex session
workers: native Codex subagent threads by default
worker_model_ceiling: gpt-5.6-luna
```

The switch changes the operating instructions for this task. It is not a
hidden platform setting: it cannot change the model selected for the current
session, raise a worker above the configured ceiling, or retroactively alter
an already-running task. If the project adapter was installed or updated
during a task, start a new task/thread or explicitly reread the project
instructions before relying on the update.

## Operating contract

- The main session is the Director. The user-selected model remains the
  Director model; do not silently replace it.
- Use native Codex subagent threads for delegation by default. Use `codex exec`
  only as the documented fallback when native delegation is unavailable or
  the task explicitly requires a separate process.
- Normal implementer, investigator, reviewer, and rescue work is capped at
  `gpt-5.6-luna` in this adapter. Do not self-escalate the model.
- Map task kind to effort: mechanical `low`, pipeline `medium`, implementation
  `high`, and investigation/audit/review `max`. Rescue raises effort only on
  the same model and is limited to two attempts.
- Do not let implementers spawn children. Only the Director delegates.
- Default to at most four simultaneous native subagents and twelve cumulative
  spawns per request. Disclose the composition before spawning.
- Shared files or interfaces force sequential execution. Record the conflict
  domains and the reason for every delegated task.
- Require a task contract before delegation, including current state, target
  behavior, editable and forbidden files, completion criteria, tests, effort,
  model ceiling, execution mode, conflict domains, and spawn authority.
- Treat `status: complete` as a request for review, never as proof of
  completion. Independently inspect the diff and rerun the relevant checks.
- After two failures with the same root cause, stop guess-based retries and
  classify the cause. Use bounded same-model rescue only for a genuine
  reasoning/capability gap; otherwise revise scope, escalate to the user,
  investigate, roll back, or use a recorded takeover.
- Preserve failed work and checkpoints until the Director has reviewed the
  evidence. Never hide a failed attempt with an unapproved destructive reset.

## Required disclosure

Before any spawn, show or record the worker count, role, model source, assigned
model, model ceiling, effort, execution mode, conflict domains, spawn budget,
and justification. If native threads are unavailable and `codex exec` is used,
state that fallback and its exact model/effort settings.

## Project adapter boundary

This plugin supplies the explicit skill switch. A project that needs persistent
defaults must also install or merge:

- `AGENTS.md` from `codex/AGENTS.md.example`;
- `.codex/config.toml` from `codex/config.toml.example`;
- named `.codex/agents/*.toml` profiles;
- `core/` and `schemas/` if the project keeps the audit artifacts locally.

The YAML at `codex/profiles/default.yaml` is policy metadata for the adapter,
not a native Codex auto-loaded profile. Follow `codex/INSTALL.md` for the
complete project install and validation procedure.

## Completion gate

Before declaring the user request complete, the Director must verify the
actual changed files, relevant tests, secrets safety, and integration path.
If this repository is the subject of the change, run:

```text
python scripts/check_repository.py
```

Report skipped checks and unresolved blockers explicitly.
