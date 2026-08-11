# Installing the agent-director skill in Claude Code

There are two ways to install. **Plugin install is recommended** — it is the
only one that can update itself later.

| | Plugin install | Manual copy |
|---|---|---|
| Setup | two commands | copy 3 directories per project |
| Updates | background refresh + `/plugin update` | none — you re-copy by hand |
| Scope | user-wide (or per project with `--scope project`) | wherever you copied it |
| Requires | Claude Code with plugin support | any Claude Code |

## Plugin install (recommended)

From inside a Claude Code session:

```
/plugin marketplace add produckyou-design/agent-director-protocol
```

```
/plugin install agent-director@agent-director-protocol
```

Or from a shell:

```bash
claude plugin marketplace add produckyou-design/agent-director-protocol
claude plugin install agent-director@agent-director-protocol
```

The plugin ships the skill together with `core/` and `schemas/`, so its
internal links resolve without any extra copying. Verify by asking Claude to
act as director on a small feature — it should produce a task contract before
touching code.

### Updating

Claude Code refreshes marketplaces in the background, so an installed plugin
picks up new releases on its own. To update immediately:

```
/plugin marketplace update agent-director-protocol
/plugin update agent-director@agent-director-protocol
```

**Use the fully qualified `agent-director@agent-director-protocol`, not the
bare plugin name** — the bare name fails with `Plugin "agent-director" not
found` even when it is installed. Updating requires a restart to take effect.

Updates are delivered when this repository's `version` field changes (see
`.claude-plugin/plugin.json`), which happens on every tagged release. Note
that background refresh can fail for private repositories, where Git
credential helpers are disabled during pulls; this repository is public, so
that limitation does not apply here.

If you previously installed by copying files into `~/.claude/skills/`, remove
that copy — Claude Code reports the name as already taken and refuses to load
it, since the installed plugin takes precedence. Keeping both means the copy
silently never runs.

### Uninstalling a plugin install

```
/plugin uninstall agent-director@agent-director-protocol
/plugin marketplace remove agent-director-protocol
```

---

## Manual copy install

Use this if you want the files vendored into a specific project, or your
Claude Code build has no plugin support. **There is no update mechanism for a
manual copy — you re-copy when a new release lands.**

This adapter is a normal Claude Code skill directory
(`skills/agent-director/`, containing `SKILL.md` and `references/`). Claude
Code discovers skills under `.claude/skills/` in a project, or under
`~/.claude/skills/` (Windows: `%USERPROFILE%\.claude\skills\`) for a
user-global install. Install to whichever scope you want the skill
available in.

## Project install

`SKILL.md` links to the platform-neutral rules with relative paths
(`../../../core/...`, `../../../schemas/...`), so a working install needs
`core/` and `schemas/` copied into the project alongside the skill, not just
the skill directory by itself:

```bash
# macOS / Linux
mkdir -p <project>/.claude/skills
cp -r claude/skills/agent-director <project>/.claude/skills/agent-director
cp -r core <project>/core
cp -r schemas <project>/schemas
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path "<project>\.claude\skills" | Out-Null
Copy-Item -Recurse "claude\skills\agent-director" "<project>\.claude\skills\agent-director"
Copy-Item -Recurse "core" "<project>\core"
Copy-Item -Recurse "schemas" "<project>\schemas"
```

## User-global install

Copy the skill directory into your user-global skills directory instead:

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
cp -r claude/skills/agent-director ~/.claude/skills/agent-director
```

```powershell
# Windows PowerShell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse "claude\skills\agent-director" "$env:USERPROFILE\.claude\skills\agent-director"
```

A user-global install makes the skill available in every project; a project
install keeps it scoped to that one repository. Both can coexist; the
project-local copy takes precedence for that project.

Because a user-global skill has no single project root to place `core/` and
`schemas/` next to, `SKILL.md`'s `../../../core/...` and
`../../../schemas/...` links only resolve per-project if you also copy
`core/` and `schemas/` into each project that uses the global skill (same
commands as the project install, minus the skill copy step), or edit those
links to an absolute path for your machine. For most users the project
install above is simpler for exactly this reason.

## Verify the install

- Ask Claude Code to list its available skills, or start a new turn and
  check that `agent-director` appears in the skills list shown to you.
- Or simply invoke it by intent: ask Claude to "act as director for this
  feature" or "delegate this implementation instead of coding it directly."
  If installed correctly, Claude Code loads `SKILL.md` and follows the
  delegate/review workflow described there.

## Activate director mode in a project

Merge the snippet from `CLAUDE.md.example` (in this same `claude/` directory)
into the project's `CLAUDE.md` (or your user-global `~/.claude/CLAUDE.md`).
That snippet tells Claude to load the `agent-director` skill for multi-task
work and to avoid coding directly before delegation has been attempted.

## The default profile (and why you usually don't need to touch it)

`profiles/default.yaml` applies automatically — it is a **convention read by
the skill's own instructions**, not a native Claude Code mechanism, and there
is only one file, so there is nothing to select. It does **not** determine who
the director is: the director is always whoever is running the current
session, and that changes live if you switch models with `/model` — no file
update needed for that. What the profile actually holds is operational
policy that should stay stable regardless of which model happens to be
director today:

- `implementer.preferred_models` / `effort_by_task_kind` — which model and
  reasoning tier a spawned subagent gets, per kind of task.
- `implementer.failure_threshold` — how many failed loops on one task trigger
  Rescue Protocol classification (see [RESCUE-PROTOCOL.md](../core/RESCUE-PROTOCOL.md)).
- Native runtime capacity — the active runtime is the only worker-capacity
  authority. If capacity telemetry is unavailable, keep it `unknown`; do not
  invent a numeric project cap. A slot-full response requires waiting,
  inspecting evidence, closing completed workers, then re-scoping or returning.

**Only override it if a project wants different policy** — e.g. a stricter
project changes `failure_threshold`. To override:

- copy `default.yaml` to `<install-location>/skills/agent-director/profile.yaml`
  next to `SKILL.md` and edit your copy, or
- reference a differently-named profile file's path directly from your
  project's `CLAUDE.md` (e.g. "use `profiles/strict.yaml` for this project").

Actually steering a subagent to a specific model uses the Task/Agent tool's
own `model` parameter when the harness exposes one; when it does not, the
director simply notes the intended model in its own delegation prompt as a
hint. Nothing in this protocol depends on any specific model name existing —
`preferred_models` lists aliases you are free to rename or replace.

## Uninstall

1. Delete the skill directory you copied:
   - project: `<project>/.claude/skills/agent-director/`
   - user-global: `~/.claude/skills/agent-director/`
     (Windows: `%USERPROFILE%\.claude\skills\agent-director\`)
2. Remove the director-mode snippet you had merged from `CLAUDE.md.example`
   out of the project's (or your user-global) `CLAUDE.md`.
3. If you copied a profile YAML to `profile.yaml` next to `SKILL.md`, it is
   removed along with the skill directory in step 1; no separate cleanup is
   needed.
4. Delete the `core/` and `schemas/` copies from the project if nothing else
   in that repository depends on them.
