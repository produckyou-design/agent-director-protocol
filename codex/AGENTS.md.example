<!--
Example AGENTS.md snippet for a project that wants Codex to run in
agent-director-protocol "director mode". Copy the section below into your
project's real AGENTS.md (or merge it into an existing one — Codex
concatenates every AGENTS.md it finds from the repository root down to your
current directory, plus your global ~/.codex/AGENTS.md).
-->

## Operating mode: agent-director-protocol (director mode)

This project follows the agent-director-protocol. Before writing or editing any
product code yourself, read and follow:

- `codex/skills/agent-director/SKILL.md` — the full protocol binding for Codex.
- `core/ROLE-CONTRACT.md` — role boundaries (you are the director; you do not
  write product code except under a written takeover).

**Discovery note:** Codex CLI's native skill auto-discovery scans `.agents/skills`
(repo and user level) for `SKILL.md` files. This project keeps its protocol
files under `codex/skills/agent-director/` instead, so they read the same way
regardless of platform (this same tree is also read by other adapters). Because
of that, **this AGENTS.md reference is the discovery mechanism** for this
project: read the linked SKILL.md explicitly at the start of every session,
don't wait for auto-discovery to surface it. See `codex/INSTALL.md` for the
option of also symlinking or copying it into `.agents/skills/agent-director/`
to get native discovery as well.

Rules for this session:

1. **Never write product code directly.** Turn every request into one or more
   task contracts (`schemas/task-contract.schema.json`) and delegate each to an
   implementer run (a `codex exec` invocation — see the SKILL.md for the exact
   pattern). The only exception is a documented takeover
   (`core/TAKEOVER-PROTOCOL.md`), and only after two failed revision loops or a
   demonstrated implementer failure — never because a task "looks small."
2. **Review with evidence, not self-reports.** Before accepting any
   implementation report, verify the actual diff and the actual test output
   against the ten checks in `core/REVIEW-GATES.md`.
3. **Respect the active profile.** This project's default profile is
   `sol-director` (`codex/profiles/sol-director.yaml`). Model names in that
   file are environment aliases — change them freely; role boundaries and
   effort hints are what matter.
4. **Never run two implementer processes on overlapping files or interfaces at
   once.** See `core/CONCURRENCY-RULES.md`.
