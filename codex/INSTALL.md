# Installing the Codex adapter

This adapter binds the platform-agnostic protocol in [`../core/`](../core/) to
OpenAI Codex CLI. It assumes a recent Codex CLI release; flag and config names
below were verified against current Codex documentation at the time of
writing — check your installed version's `--help` and `docs/` if something
doesn't match.

## What Codex supports natively (and what this repo adds)

Codex CLI natively supports:

- **`AGENTS.md`** project instructions, read from the repository root down to
  your working directory (concatenated root→cwd, with closer files appended
  later in the prompt; hard overrides use `AGENTS.override.md`) plus a global
  `~/.codex/AGENTS.md`.
- **A skills mechanism**: any directory containing a `SKILL.md` (YAML
  frontmatter + instructions) under `.agents/skills` (repo, scanned from CWD up
  to the repo root) or `$HOME/.agents/skills` (user level) is auto-discovered.
- **Named config profiles**, layered over `~/.codex/config.toml` and selected
  with `--profile <name>`.
- **`model_reasoning_effort`** as a config key (`minimal|low|medium|high|xhigh`,
  model-dependent).
- **`codex exec`**, a non-interactive mode for scripted/CI runs, plus in-session
  subagent threads for ad hoc delegation.

What Codex does **not** have is a first-class notion of "director/implementer/
reviewer roles" or a "task contract" object — those are this repo's
protocol, not a Codex feature. This adapter's job is entirely to describe how
to express that protocol using the native primitives above. Nothing here
claims Codex has built-in director/implementer orchestration; it doesn't.

This repo's own directory layout keeps the skill under
`codex/skills/agent-director/` (parallel to the same tree for other platform
adapters) rather than directly under `.agents/skills/`. Two install options
follow: point Codex at the file via `AGENTS.md` (works everywhere, no file
moves), or additionally place a copy where Codex's native scanner will find it.

## Project install (recommended for a single repo)

1. Copy this adapter's directory into the target repository, keeping the
   relative layout intact so links inside it keep resolving:
   - `codex/skills/agent-director/` (including `references/`)
   - `codex/profiles/sol-director.yaml`
   - The rest of the protocol: `core/`, `schemas/`.

   macOS/Linux:
   ```bash
   cp -r agent-director-protocol/core target-repo/core
   cp -r agent-director-protocol/schemas target-repo/schemas
   cp -r agent-director-protocol/codex target-repo/codex
   ```

   Windows (PowerShell):
   ```powershell
   Copy-Item -Recurse agent-director-protocol\core target-repo\core
   Copy-Item -Recurse agent-director-protocol\schemas target-repo\schemas
   Copy-Item -Recurse agent-director-protocol\codex target-repo\codex
   ```

2. Add the contents of [`AGENTS.md.example`](AGENTS.md.example) to the target
   repository's `AGENTS.md` (create one if it doesn't exist). This is what
   makes Codex read `codex/skills/agent-director/SKILL.md` at session start,
   since the file lives outside Codex's auto-scanned `.agents/skills` path.

3. *(Optional — gets native auto-discovery too.)* Symlink or copy the skill
   into a location Codex scans automatically:

   macOS/Linux:
   ```bash
   mkdir -p target-repo/.agents/skills
   ln -s ../../codex/skills/agent-director target-repo/.agents/skills/agent-director
   ```

   Windows (PowerShell, run as a user with symlink privilege, or copy instead):
   ```powershell
   # -Target must be absolute: NTFS resolves a relative target against the
   # link's own directory, which would produce a dangling link here.
   New-Item -ItemType SymbolicLink -Path target-repo\.agents\skills\agent-director -Target (Resolve-Path target-repo\codex\skills\agent-director)
   # or, without symlink privileges:
   Copy-Item -Recurse target-repo\codex\skills\agent-director target-repo\.agents\skills\agent-director
   ```
   If you copy instead of symlink, remember to re-copy after future updates —
   the copy will not stay in sync automatically.

4. Add a Codex profile so `--profile sol-director` picks up the intent
   described in `codex/profiles/sol-director.yaml`. Codex profiles are
   separate files next to your config, not the YAML shipped in this repo —
   create `~/.codex/sol-director.config.toml` with the settings that match
   your chosen model and effort level, e.g.:
   ```toml
   model = "<your director model>"
   model_reasoning_effort = "high"
   ```
   Alternative: a project-scoped `.codex/config.toml` (only loaded for
   trusted projects) applies these settings **always-on for that repo,
   without `--profile`** — project config cannot select named profiles, so
   if you use this route, skip the `--profile sol-director` flag entirely.

## User-global install (available to every project on the machine)

1. Copy the skill tree to your Codex home so it is available everywhere Codex
   runs, independent of any one repo's `AGENTS.md`:

   macOS/Linux:
   ```bash
   mkdir -p ~/.agents/skills
   cp -r agent-director-protocol/codex/skills/agent-director ~/.agents/skills/agent-director
   ```

   Windows (PowerShell):
   ```powershell
   New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
   Copy-Item -Recurse agent-director-protocol\codex\skills\agent-director "$HOME\.agents\skills\agent-director"
   ```
   This path (`$HOME/.agents/skills`) is Codex's native user-level skill scan
   location, so no `AGENTS.md` reference is required for discovery here — but
   the skill's internal links to `../../../core/...` and `../../../schemas/...`
   — and the `../../profiles/sol-director.yaml` link inside `SKILL.md`, which
   sits at a different depth — only resolve if you also keep a copy of
   `core/`, `schemas/`, and `profiles/` reachable at the same relative
   positions, or edit those links to absolute paths for your machine. For a global install it is usually simpler to keep the whole
   `agent-director-protocol` checkout on disk and use the project install
   method (`AGENTS.md` reference) in each repo instead.

2. Add the same instructions from `AGENTS.md.example` to
   `~/.codex/AGENTS.md` if you want the director-mode rules to apply to every
   project by default, not just ones with their own `AGENTS.md`.

## Verification

- Start Codex in the target repo and ask it to summarize its own operating
  rules; it should mention director mode, task contracts, and evidence-based
  review if `AGENTS.md` (or native skill discovery) is wired up correctly.
- Confirm the profile resolves without a config error, using the
  non-interactive form so it works in a script:
  `codex exec --profile sol-director "reply with the single word: ready"`.
- Give the director a trivial task and confirm it produces a task-contract
  JSON matching [`schemas/task-contract.schema.json`](../schemas/task-contract.schema.json)
  before any file is touched, rather than editing code directly.

## Differences from the Claude Code adapter (no forced parity)

- Claude Code's skill discovery, CLAUDE.md, and subagent dispatch are separate
  mechanisms from Codex's `.agents/skills`, `AGENTS.md`, and `codex exec` /
  in-session subagents — the two adapters describe the same protocol using
  each platform's real primitives, not a shared implementation.
- Codex has no equivalent of a persistent, named "subagent type" registry;
  every implementer run here is a fresh `codex exec` invocation carrying the
  full task contract as its prompt, not a pre-configured agent identity.
- Codex profile files are separate TOML files layered over `config.toml`, not
  an inline table — this repo's `profiles/sol-director.yaml` is a
  platform-neutral description of intent for you to translate into that
  format, not something Codex reads directly.

## Uninstall

- Project install: delete `codex/`, and remove the director-mode section you
  added to `AGENTS.md`. Remove `core/` and `schemas/` too if nothing else in
  the repo depends on them. If you created the optional `.agents/skills/agent-director`
  symlink or copy, delete it as well.
- User-global install: delete `~/.agents/skills/agent-director` (or the
  equivalent Windows path under `%USERPROFILE%\.agents\skills`) and remove the
  director-mode section from `~/.codex/AGENTS.md` if you added one. Delete any
  `~/.codex/sol-director.config.toml` (or similarly named) profile file you
  created for this adapter.
