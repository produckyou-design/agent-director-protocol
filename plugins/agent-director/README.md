# Agent Director Codex plugin

This is the explicit Codex skill switch for the Agent Director Protocol.

Install it from the repository marketplace:

```text
codex plugin marketplace add produckyou-design/agent-director-protocol
codex plugin add agent-director@agent-director-protocol-plugins
```

In a new Codex task/thread, invoke `$agent-director` or say “Director mode on”.
The skill then announces the current session as Director and uses native Codex
subagent threads as the default worker mechanism. The user-selected model
continues to own the Director session; normal workers are capped at
`gpt-5.6-luna`.

The plugin is a behavior/instruction switch, not a hidden model or runtime
toggle. It does not retroactively reload an existing task, install project
files, or change a running session's model. For persistent project defaults,
follow [`codex/INSTALL.md`](../../codex/INSTALL.md) and install the project's
`AGENTS.md`, `.codex/config.toml`, and named agent profiles.
