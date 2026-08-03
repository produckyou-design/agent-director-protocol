# Installing the agent-director skill in Claude Code

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

## Selecting a model profile

Profiles (`profiles/opus-director.yaml`, `profiles/fable-director.yaml`) are
a **convention read by the skill's own instructions** — they are not a
native Claude Code mechanism. There is no built-in "active profile" concept
in Claude Code itself; you make one active by either:

- copying the chosen profile YAML to
  `<install-location>/skills/agent-director/profile.yaml` next to `SKILL.md`
  so the skill's own guidance can point to a single, predictable file, or
- referencing the chosen profile file's path directly from your project's
  `CLAUDE.md` (e.g. "use `profiles/opus-director.yaml` for this project").

Either way, the profile only records *preferred model names* per role
(director / implementer / reviewer). Actually steering a subagent to a
specific model uses the Task/Agent tool's own `model` parameter when the
harness exposes one; when it does not, the director simply notes the
intended model in its own delegation prompt as a hint. Nothing in this
protocol depends on any specific model name existing — profiles list
aliases you are free to rename or replace.

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
