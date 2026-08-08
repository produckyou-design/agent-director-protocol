---
name: agent-director
description: Enact the agent-director protocol on Codex native subagents with a user-selected director, Luna worker ceiling, contract-first delegation, conflict-safe execution, and evidence-based review.
---

# Agent Director — Codex adapter

This is the Codex binding for the platform-neutral protocol in [`core/`](../../../core/).
Read [`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md) first, then read only the
core documents and schemas relevant to the current task. The protocol is an
operating policy layered on Codex; it is not a Codex runtime, daemon, or hidden
dispatcher.

## What Codex actually provides

Use the current native surfaces in this order:

1. **Project guidance:** Codex reads `AGENTS.md` before work. The repository
   root `AGENTS.md` points to this canonical skill. The `.agents/skills/` bridge
   makes the skill discoverable through the native project skill surface; the
   `.codex/skills/` copy is a compatibility bridge and must not diverge.
2. **Native subagent workflow:** the director session can spawn subagent
   threads, wait for them, inspect them, and collect their summaries. Native
   delegation is the default for interactive Codex app, CLI, and IDE sessions.
3. **Custom agents:** project-scoped agents live in `.codex/agents/*.toml`.
   Each standalone file must define `name`, `description`, and
   `developer_instructions`; supported session keys such as `model`,
   `model_reasoning_effort`, and `sandbox_mode` may be added. The `name` field
   is authoritative.
4. **Native multi-agent settings:** `.codex/config.toml` may use the real
   `[agents]` keys `enabled`, `max_concurrent_threads_per_session`,
   `default_subagent_model`, `default_subagent_reasoning_effort`, and
   `interrupt_message`. Do not invent undocumented depth/runtime controls or a
   project-local pseudo-profile key.
5. **`codex exec` fallback:** use `codex exec` only for non-interactive/CI
   work, process isolation, or an environment without native subagent tools.
   A real user profile is a `$CODEX_HOME/<name>.config.toml` file; this
   repository's `codex/profiles/default.yaml` is policy metadata and is never
   loaded by Codex. Use `--profile <name>` only for a real native profile, or
   use `-c model=...` / `-c model_reasoning_effort=...` when the installed CLI
   supports those overrides.

Official references: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), and
[advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

## Director model

The director is the main Codex session the user is speaking to. **The user
chooses the director model and effort.** The protocol never selects Sol, Terra,
Luna, or any other director tier and never treats `default.yaml` as a native
Codex profile. Every disclosure records the actual current session values and
`director_model_source: user_selected_session`.

The director must:

- inspect the repository and relevant tests before designing work;
- interpret the requirement and write the fewest verifiable Task Contracts;
- check dependencies and all conflict domains before considering parallelism;
- disclose the complete batch before spawning anything;
- integrate only reviewed work and make the final completion judgment.

The director does not write product code or run state-changing operations. The
only exception is a recorded takeover under [`TAKEOVER-PROTOCOL.md`](../../../core/TAKEOVER-PROTOCOL.md).
If the director authored a diff under takeover, it must use an independent
reviewer context and must not self-review.

## Worker model policy: Luna ceiling

The normal Codex delegated worker is **GPT-5.6 Luna**. The native project
defaults and the investigator, implementer, reviewer, and rescue custom-agent
files pin the worker model to `gpt-5.6-luna`.

| Assignment | Native agent | Default effort | Write access |
| --- | --- | --- | --- |
| Root-cause investigation | `investigator` | `max` | read-only |
| Contract execution | `implementer` | `high` | workspace-write |
| Evidence review | `reviewer` | `max` | read-only |
| Task-scoped rescue | `rescue` | director-selected higher step | workspace-write |

`release_auditor` is also a read-only Luna custom agent at `medium` effort for
repository release checks. It is not a reason to create another worker when an
existing contract can include the check.

The director model is not inherited by a worker merely because it is stronger.
An explicit user policy may choose another worker model, but the disclosure
must record that exception and the protocol must not silently apply it. The
adapter never performs automatic `Luna → Terra` or `Luna → Sol` escalation.

## Reasoning effort policy

Codex's native key is `model_reasoning_effort`. For GPT-5.6, use only the
documented values `low`, `medium`, `high`, `xhigh`, and `max` in this adapter.
Select effort by task kind; do not run every task at `max`:

| Task kind | Effort |
| --- | --- |
| mechanical | `low` |
| pipeline | `medium` |
| implementation | `high` |
| investigation | `max` |
| audit/review | `max` |

The native custom-agent files supply safe role defaults. If the native spawn
surface permits an explicit effort for a particular contract, the director may
set the contract's selected effort within the table and the Luna ceiling.

## Contract-first delegation

For every non-trivial change, follow this exact order:

1. Repository analysis.
2. Requirement interpretation.
3. Design.
4. Fewest-first task decomposition.
5. Complete [`task-contract.schema.json`](../../../schemas/task-contract.schema.json),
   including `delegation.role`, `delegation.model`, `delegation.model_ceiling`,
   `delegation.reasoning_effort`, `delegation.execution`, and a concrete
   `delegation.justification`.
6. Conflict-domain check across files, code regions, interfaces, schemas,
   migrations, shared state, generated artifacts, build/config files, and
   user flows.
7. Agent composition disclosure, including spawn budget.
8. Native subagent spawn by the director only.
9. Worker execution and actual evidence collection.
10. Independent evidence-based review.

Never spawn an agent to discover what the Task Contract should have said. A
worker that finds a new conflict, missing requirement, or need for further
decomposition reports it to the director and stops; it never spawns a child.

### Justification gate

Every new subagent needs a specific reason why the work cannot be folded into
an existing contract or worker. Acceptable reasons include independent
parallelism, a distinct conflict domain, an independently verifiable result,
an isolated blast radius, a separate root-cause investigation, or an
independent reviewer context. “The task is large”, “there are many files”,
“smaller diffs”, “there is an empty slot”, and “retry after failure” are not
justifications.

## Conflict-safe execution

Use the Task Contract `conflict_domains` object and compare every pair before
dispatch. Read/read work may run in parallel when there is no dependency. Any
write/write overlap, shared interface/schema/config/state, or read/write
consistency dependency is sequential. Different filenames do not prove that
two API or schema changes are independent.

Native subagents inherit the parent session's sandbox and approval context. In
the normal local workflow they should be treated as sharing the working tree;
parallel write tasks therefore require disjoint domains and an explicitly
isolated worktree, otherwise they run sequentially.

The native concurrency ceiling is configured by the actual Codex key
`agents.max_concurrent_threads_per_session = 4`. This is only the simultaneous
thread limit. The protocol also enforces a per-request cumulative budget of
12 spawned agents, independent of how many batches finish.

## Agent composition disclosure

Before the first spawn in every batch, send one disclosure matching
[`agent-composition-disclosure.schema.json`](../../../schemas/agent-composition-disclosure.schema.json):

- current director model and effort, with source `user_selected_session`;
- each worker's role, Task Contract, model, model ceiling, effort, and concrete
  justification;
- each worker's conflict domains and whether the batch is `parallel` or
  `sequential`;
- `already_spawned_count`, `this_batch_count`, `total_after_spawn`, and the
  request limit of 12;
- whether the batch is within both the concurrency and cumulative budgets;
- whether Rescue has effort headroom on the same Luna model;
- approval status if a batch exceeds the configured batch budget.

Do not silently add an investigator, reviewer, revision worker, or rescue
worker later. Any new agent, new conflict domain, budget exception, or material
execution-mode change requires a new disclosure and approval when applicable.

## Rescue and escalation

Rescue is a bounded implementer assignment, not a stronger model tier:

```text
same GPT-5.6 Luna
  → inspect failure evidence
  → raise effort one supported step
  → retry the same bounded contract
  → at Luna max, return the problem to the director
```

The director must classify the failure before promotion. Do not create a new
agent for every failed attempt. A Rescue notice and outcome notice are required
and the rescue remains task-scoped. If the worker is already at `max`, Rescue
is unavailable: preserve the evidence, revise the contract or escalate to the
director/user/takeover path according to the Core protocol. Never lower effort
to pretend a rescue ladder exists, and never change the model automatically.

## Review and completion

The reviewer is read-only by default. It checks the actual diff, actual test
output, completion criteria, preservation conditions, interfaces, error paths,
regressions, scope, and evidence. It returns a
`review-result.schema.json`-shaped result; it does not directly fix findings.

The director never accepts an implementer's `status` by itself. Completion
requires real test excerpts, one evidence entry per completion criterion, and
a passing review. Keep contracts, reports, and command excerpts free of
secrets, tokens, and private transcript content; local evidence belongs under
the ignored `.codex/agent-director/runs/` directory.

## State safety

Before the first native spawn, establish a real last-passing commit, tag, or
branch tip and resolve or explicitly record a dirty tree. Preserve user changes
and failed-worker diffs for review. Do not run destructive Git cleanup to make a
diff look clean. Workers do not merge or push; integration happens only after
the director's review gates pass.

The full platform-neutral rules live in `core/`; update schemas and examples
when a protocol field changes. Run `python scripts/check_repository.py` after
changing this adapter.

## Core reference map

The platform-neutral rules are authoritative. The adapter-specific mapping above
does not replace them:

- [`COMPLETION-STANDARD.md`](../../../core/COMPLETION-STANDARD.md)
- [`CONCURRENCY-RULES.md`](../../../core/CONCURRENCY-RULES.md)
- [`DELEGATION-PROTOCOL.md`](../../../core/DELEGATION-PROTOCOL.md)
- [`ESCALATION-PROTOCOL.md`](../../../core/ESCALATION-PROTOCOL.md)
- [`FAILURE-LOOP.md`](../../../core/FAILURE-LOOP.md)
- [`RESCUE-PROTOCOL.md`](../../../core/RESCUE-PROTOCOL.md)
- [`REVIEW-GATES.md`](../../../core/REVIEW-GATES.md)
- [`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md)
- [`STATE-SAFETY.md`](../../../core/STATE-SAFETY.md)
- [`TAKEOVER-PROTOCOL.md`](../../../core/TAKEOVER-PROTOCOL.md)
- [`TASK-CONTRACT.md`](../../../core/TASK-CONTRACT.md)
