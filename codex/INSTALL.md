# Installing the Codex adapter

This adapter applies the platform-neutral protocol in [`../core/`](../core/)
to Codex's current native multi-agent surfaces. It is a set of project files
and instructions, not a runtime, daemon, hidden dispatcher, or native Codex
profile.

## What Codex actually reads

Use these surfaces in this order:

- `AGENTS.md` for project instructions;
- `.agents/skills/*/SKILL.md` for native project skill discovery;
- `.codex/config.toml` `[agents]` keys for multi-agent defaults and the
  simultaneous-thread ceiling;
- `.codex/agents/*.toml` for standalone custom agents;
- native subagent threads in the Codex app, CLI, or IDE;
- `codex exec` only for non-interactive, CI, process-isolated, or
  native-unavailable work.

The custom-agent files must contain `name`, `description`, and
`developer_instructions`. `model`, `model_reasoning_effort`, and `sandbox_mode`
are role settings. The adapter does not invent depth, runtime, or model-list
configuration keys.

The user-selected current Codex session is the director. The protocol does not
choose the director model. Native delegated workers use a **GPT-5.6 Luna
ceiling** by default; the director's model is not silently inherited by a
worker and Luna is never automatically promoted to Terra or Sol.

## Files supplied by this repository

- `core/` — platform-neutral contracts, roles, concurrency, review, failure,
  rescue, escalation, takeover, and completion rules;
- `schemas/` — task contracts, reports, disclosures, reviews, and escalation
  JSON Schemas;
- `codex/skills/agent-director/` — the canonical Codex binding and reference
  templates;
- `codex/config.toml.example` — the actual native `[agents]` configuration
  template;
- `codex/agents/*.toml.example` — native custom-agent templates for
  investigator, implementer, reviewer, rescue, and release auditing;
- `plugins/agent-director/` — an explicit Codex plugin skill that can be
  invoked as `$agent-director` for a task-level switch;
- `.agents/plugins/marketplace.json` — the repository marketplace entry for
  that plugin;
- `codex/profiles/default.yaml` — policy metadata only; Codex never loads it as
  a native profile;
- `codex/AGENTS.md.example` — a section to merge into the target project's
  `AGENTS.md`.

## Explicit per-task plugin switch

If the plugin marketplace is available in your Codex installation, add this
repository marketplace and install the explicit skill:

```text
codex plugin marketplace add produckyou-design/agent-director-protocol
codex plugin add agent-director@agent-director-protocol-plugins
```

In a new task/thread, invoke `$agent-director` or say “Director mode on”. The
plugin announces the current user-selected session as Director and activates
the contract-first instructions with native subagents as the default worker
path. It does not change the selected session model, install project files, or
retroactively reload an already-running task. Use the project install below
for persistent `.agents/`, `AGENTS.md`, and `.codex/` defaults.

## Project install

Merge the example files into the target repository. Do not overwrite an
existing `AGENTS.md`, `.codex/config.toml`, or unrelated custom-agent files.
Preserve any project-specific settings while adding the `[agents]` keys and
role files deliberately.

### macOS/Linux

```bash
cp -r agent-director-protocol/core target-repo/core
cp -r agent-director-protocol/schemas target-repo/schemas
cp -r agent-director-protocol/codex/skills/agent-director target-repo/.agents/skills/agent-director
mkdir -p target-repo/.codex/agents
cp agent-director-protocol/codex/config.toml.example target-repo/.codex/config.toml
for file in agent-director-protocol/codex/agents/*.toml.example; do
  cp "$file" "target-repo/.codex/agents/$(basename "${file%.example}")"
done
```

### Windows PowerShell

```powershell
Copy-Item -Recurse "agent-director-protocol\core" "target-repo\core"
Copy-Item -Recurse "agent-director-protocol\schemas" "target-repo\schemas"
New-Item -ItemType Directory -Force "target-repo\.agents\skills" | Out-Null
Copy-Item -Recurse "agent-director-protocol\codex\skills\agent-director" `
  "target-repo\.agents\skills\agent-director"
New-Item -ItemType Directory -Force "target-repo\.codex\agents" | Out-Null
Copy-Item "agent-director-protocol\codex\config.toml.example" `
  "target-repo\.codex\config.toml"
Get-ChildItem "agent-director-protocol\codex\agents\*.toml.example" | ForEach-Object {
  Copy-Item $_.FullName "target-repo\.codex\agents\$($_.BaseName)"
}
```

Then merge [`AGENTS.md.example`](AGENTS.md.example) into the target's
`AGENTS.md`. If the target already has `.codex/skills/`, a compatibility copy
of the same canonical skill may be placed there, but `.agents/skills/` is the
native discovery path.

The copied `codex/profiles/default.yaml` is optional policy documentation. It
must not be passed to `codex --profile`; a real Codex profile is a
`$CODEX_HOME/<name>.config.toml` file.

## Native configuration supplied by this adapter

The example project configuration uses only the native keys:

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 4
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "high"
interrupt_message = true
```

The role templates pin the same Luna model and set their policy boundaries:

- `investigator.toml`: read-only, `max`;
- `implementer.toml`: workspace-write, `high`;
- `reviewer.toml`: read-only, `max`;
- `rescue.toml`: same Luna model; the director supplies a higher supported
  effort for a task-scoped rescue;
- `release-auditor.toml`: read-only, `medium`.

The four-thread setting is a simultaneous limit, not the protocol's cumulative
per-request budget of twelve spawned agents. Overlapping write or read/write
conflict domains still run sequentially.

## How to use it

Start Codex in the trusted target repository after installation. The current
session is the director. Before the first spawn it must:

1. read the skill and relevant Core/schema documents;
2. analyze the repository and write the fewest complete Task Contracts;
3. check all conflict domains and dependencies;
4. disclose the complete composition and spawn budget;
5. spawn native subagent threads only after that disclosure;
6. review actual diffs and actual test output before declaring completion.

There is no hidden platform-level "director mode" switch in Codex. The
effective persistent setup is the project instruction plus the discovered skill
and native agent settings; the explicit `$agent-director` plugin is the
task-level instruction switch. For a session that started before these files
were installed, explicitly ask it to reread `AGENTS.md` and the canonical
skill, or start a new task so the project instructions are loaded from the
beginning.

## `codex exec` fallback

Use `codex exec` for non-interactive/CI work, process isolation, or a client
without native subagent tools. A real native profile is a file at
`$CODEX_HOME/<name>.config.toml`, selected with `--profile <name>`. The
repository's `codex/profiles/default.yaml` is not that file.

For a one-off explicit worker override, use supported CLI syntax such as:

```bash
codex exec \
  -c model='"gpt-5.6-luna"' \
  -c model_reasoning_effort='"high"' \
  "<complete task-contract JSON>"
```

The fallback still requires the same contract, disclosure, conflict check,
budget, implementation report, and review gates. It is not a second protocol.

## Verification and secrets

Run this repository's offline validation from its root:

```bash
python scripts/check_repository.py
```

In an installed project, run that project's normal tests as well. Keep
contracts, reports, and command excerpts free of API keys, tokens, credentials,
private transcripts, and other sensitive output. Store local evidence under an
ignored `.codex/agent-director/runs/` directory.

## Uninstall

Remove only the copied `core/`, `schemas/`, Codex skill bridge, and agent role
files after checking that no other workflow depends on them. Remove the
director section from `AGENTS.md` manually. Do not delete user-global Codex
settings or credentials.
