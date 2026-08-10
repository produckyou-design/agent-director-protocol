---
name: agent-director
description: Enact the agent-director protocol on Codex native subagents with a user-selected director, explicit Luna/max worker dispatch, contract-first delegation, conflict-safe execution, and fail-closed evidence-based review.
---

# Agent Director -- Codex adapter

This is the Codex binding for the platform-neutral protocol in [`core/`](../../../core/).
Read [`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md) first, then read only the
core documents and schemas relevant to the current task. The protocol is an
operating policy layered on Codex; it is not a Codex runtime, daemon, or hidden
dispatcher.

## What Codex actually provides

Use the current native surfaces in this order:

1. **Project guidance:** Codex reads `AGENTS.md` before work. The repository
   root `AGENTS.md` points to this canonical skill. The `.agents/skills/`
   bridge makes the skill discoverable through the native project skill
   surface; the `.codex/skills/` copy is a compatibility bridge and must not
   diverge.
2. **Native subagent workflow:** the director session can spawn subagent
   threads, wait for them, inspect them, and collect their summaries. Native
   delegation is the default for interactive Codex app, CLI, and IDE sessions.
3. **Custom agents:** project-scoped agents live in `.codex/agents/*.toml`.
   Each standalone file must define `name`, `description`, and
   `developer_instructions`; supported session keys such as `model`,
   `model_reasoning_effort`, and `sandbox_mode` may be added. The `name` field
   is authoritative, but a named profile is never a substitute for explicit
   model and effort fields in the spawn request.
4. **Native multi-agent settings:** `.codex/config.toml` may use the real
   `[agents]` keys `enabled`, `max_concurrent_threads_per_session`,
   `default_subagent_model`, `default_subagent_reasoning_effort`, and
   `interrupt_message`. These defaults are defense in depth; they do not
   replace explicit per-spawn dispatch or runtime verification. Do not invent
   undocumented depth/runtime controls or a project-local pseudo-profile key.
5. **`codex exec` fallback:** use `codex exec` only for non-interactive/CI
   work, process isolation, or an environment without native subagent tools.
   A real user profile is a `$CODEX_HOME/<name>.config.toml` file; this
   repository's `codex/profiles/default.yaml` is policy metadata and is never
   loaded by Codex. Use `--profile <name>` only for a real native profile, or
   use explicit `-c model=...` and `-c model_reasoning_effort=...` overrides
   when the installed CLI supports them. The same acceptance and verification
   gates apply to the fallback.

Official references: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference), and
[advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

## Activation and Director model

Apply this policy by default to every repository and code task. Announce
`director_mode: on` at the start of the task. Explicit `$agent-director` or
`Director mode on` remains a supported way to request the same policy, but it
is not required for normal activation. This is an instruction policy, not a
hidden product or system setting.

The Director is the main Codex session the user is speaking to. **The user
chooses the Director model and effort.** The protocol never selects Sol, Terra,
Luna, or any other Director tier and never treats `default.yaml` as a native
Codex profile. Every disclosure records the actual current session values and
`director_model_source: user_selected_session`.

The Director must:

- inspect the repository and relevant tests before designing work;
- interpret the requirement and write the fewest verifiable Task Contracts;
- check dependencies and all conflict domains before considering parallelism;
- disclose the complete batch before spawning anything;
- integrate only reviewed work and make the final completion judgment.

The Director does not write product code or run state-changing operations. The
only exception is a recorded takeover under
[`TAKEOVER-PROTOCOL.md`](../../../core/TAKEOVER-PROTOCOL.md). If the Director
authored a diff under takeover, it must use an independent reviewer context and
must not self-review.

## Worker dispatch policy: explicit Luna/max baseline

When ADP is active, every ADP-created native Codex subagent must be dispatched
with both fields present in the spawn request:

```text
model = "gpt-5.6-luna"
reasoning_effort = "max"
```

The Director is never inherited by a worker merely because it is stronger. The
worker baseline is fixed for every role:

| Assignment | Native role/profile | Explicit model | Explicit effort | Write access |
| --- | --- | --- | --- | --- |
| Root-cause investigation | `investigator` | `gpt-5.6-luna` | `max` | read-only |
| Contract execution | `implementer` | `gpt-5.6-luna` | `max` | workspace-write |
| Evidence review | `reviewer` | `gpt-5.6-luna` | `max` | read-only |
| Release audit | `release_auditor` | `gpt-5.6-luna` | `max` | read-only |
| Task-scoped rescue | `rescue` | `gpt-5.6-luna` | `max` | workspace-write |

The adapter does not select effort by task kind. Native defaults and custom
agent files pin the same pair as defense in depth, but configuration is not
the enforcement claim. Every request must express
`model="gpt-5.6-luna"` and `reasoning_effort="max"`. The role may be carried in the Task Contract and
prompt without selecting a named custom agent.

## Native spawn acceptance and fail-closed verification

Before every native spawn, the Director must:

1. Put `model="gpt-5.6-luna"` and
   `reasoning_effort="max"` directly in the spawn request. Do not rely
   on session inheritance, `[agents]` defaults, a YAML policy file, or an
   omitted field.
2. Prefer no named custom agent/type. If a named custom agent is used, load
   its exact profile first and verify that both pinned fields equal the pair
   above; otherwise do not dispatch it.
3. When the native surface returns worker/runtime metadata, verify the returned
   model and effort before using any result. A mismatch is a policy violation:
   reject and close the worker and discard its output.
4. If the surface cannot accept the explicit pair or cannot expose metadata
   needed for verification, stop and report a policy violation/fallback
   requirement. Do not claim that execution was forced or accept unverified
   output.

Any non-Luna or non-`max` exception requires explicit user authorization and a
disclosure naming the exception. There is no silent inheritance, downgrade, or
promotion. A user-authorized exception is a disclosed policy change for that
spawn, not the adapter default.

## Mandatory work-contract notice boundary

Before every task, every state-changing operation, and every native-spawn
attempt, visibly publish `user_visible: true` with a checkable work contract.
The notice must state the objective, scope, planned contract/worker totals,
minimum-safe rationale, model/effort, complete batch plan, exact tests, and
stop conditions. This applies even to a read-only task that will spawn no
worker.

Use these phases:

- `task_start` starts every task and every state-changing operation. A zero-
  worker task start is valid only when `work_contract.read_only: true`.
- `spawn` is the disclosure immediately before a worker batch or native-spawn
  attempt and requires positive worker totals.
- `addition` is a new disclosure before any later contract, worker,
  investigator, reviewer, revision, rescue, or material scope change. It must
  state `changed_scope`, `change_summary`, `added_worker_task`, one of
  `addition_basis` must be one of `newly_discovered_evidence`, `new_conflict_domain`, `new_dependency`,
  `mandatory_independent_review`, or `classified_failure`,
  `why_existing_workers_cannot_absorb`, and `new_disclosure: true`.

Speed, parallelism, efficiency, task size/complexity, file count, empty slots,
and tidy IDs are never valid addition or scale reasons.

The Codex repository can validate and document this boundary, but it cannot
hard-intercept or add parameters to the platform-owned native
`multi_agent_v1__spawn_agent` tool. Do not claim a runtime gate that the
platform does not expose.

## Contract-first delegation

For every task, every state-changing operation, and every native-spawn attempt,
follow this exact order:

1. Repository analysis.
2. Requirement interpretation.
3. Design.
4. Fewest-first task decomposition.
   Before any spawn, record a concrete contract-scale justification for why
   this contract size and the total contract/worker count are the minimum safe
   structure and why the work cannot be folded into fewer existing contracts.
5. Complete [`task-contract.schema.json`](../../../schemas/task-contract.schema.json),
   including `delegation.role`, `delegation.model`, `delegation.model_ceiling`,
   `delegation.reasoning_effort`, `delegation.execution`, and a concrete
   `delegation.justification`.
6. Conflict-domain check across files, code regions, interfaces, schemas,
   migrations, shared state, generated artifacts, build/config files, and user
   flows.
7. Agent composition disclosure, including the explicit worker pair and spawn
   budget.
8. Native subagent spawn by the Director only.
9. Worker execution and actual evidence collection, including metadata checks.
10. Independent evidence-based review.

Never spawn an agent to discover what the Task Contract should have said. A
worker that finds a new conflict, missing requirement, or need for further
decomposition reports it to the Director and stops; it never spawns a child.

### Justification gate

The initial `delegation.justification` set must explain conflict boundaries,
dependencies, independent evidence/review needs, or blast-radius isolation and
why fewer existing contracts/workers cannot safely absorb the work. Speed,
parallelism, efficiency, task size/complexity, many files, context reduction,
empty slots, and tidy/smaller task IDs are rejected.

Every mid-task addition of a contract, worker, investigator, reviewer,
revision, or rescue requires a new disclosure first. Its concrete addition
justification must cite newly discovered evidence, a new conflict
domain/dependency, a mandatory independent-review boundary, or a classified
failure and explain why an existing contract/worker cannot absorb it.

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

Native capacity comes from the active Codex runtime through
`agents.max_concurrent_threads_per_session` or returned metadata, when exposed.
The adapter does not add a concurrent or cumulative numeric cap. If capacity is
unknown, record it as unknown and do not invent a project limit.

## Agent composition disclosure

Before the first spawn in every batch, send one disclosure matching
[`agent-composition-disclosure.schema.json`](../../../schemas/agent-composition-disclosure.schema.json):

- `user_visible: true` and a `work_contract` containing the objective, scope,
  planned contract/worker totals, worker model/effort, minimum-safe rationale,
  exact tests, and stop conditions;
- the disclosure `phase` (`task_start`, `spawn`, or `addition`), with the
  addition fields present whenever `phase: addition`;
- current Director model and effort, with source `user_selected_session`;
- each worker's role, Task Contract, explicit model `gpt-5.6-luna`, explicit
  effort `max`, model ceiling, and concrete justification;
- each worker's conflict domains and whether the batch is `parallel` or
  `sequential`;
- `already_spawned_count`, `this_batch_count`, and `total_after_spawn`;
- whether native runtime capacity was observed or remains unknown;
- whether Rescue has effort headroom on the same Luna model. With the normal
  `max` baseline, Rescue is unavailable for ordinary Codex ADP runs;
- the observed runtime-capacity result, or an explicit `unknown` value when the
  native surface exposes no capacity metadata.

Do not silently add an investigator, reviewer, revision worker, or rescue
worker later. Any addition requires the new disclosure and concrete addition
justification above; a material execution-mode or scope change requires a new
disclosure before it is dispatched.

## Rescue and escalation

Rescue is a bounded implementer assignment, not a stronger model tier:

```text
same GPT-5.6 Luna at max
  -> inspect failure evidence
  -> no higher same-model effort exists
  -> preserve evidence and use Core escalation/takeover gates
```

The Director must classify the failure before promotion. Do not create a new
agent for every failed attempt. A Rescue notice and outcome notice are required
when a supported Rescue promotion exists, and the rescue remains task-scoped.
At the `max` baseline there is no Rescue headroom for ordinary Codex ADP runs:
preserve the evidence, revise the contract, or use the Core escalation/takeover
path. Never lower effort to pretend a rescue ladder exists, and never change
the model automatically.

## Review and completion

The reviewer is read-only by default. It checks the actual diff, actual test
output, completion criteria, preservation conditions, interfaces, error paths,
scope, metadata verification, and evidence. It returns a
`review-result.schema.json`-shaped result; it does not directly fix findings.

The Director never accepts an implementer's `status` by itself. Completion
requires real test excerpts, one evidence entry per completion criterion, a
passing review, and an accepted worker metadata check. Keep contracts, reports,
and command excerpts free of secrets, tokens, and private transcript content;
local evidence belongs under the ignored `.codex/agent-director/runs/`
directory.

## State safety

Before the first native spawn, establish a real last-passing commit, tag, or
branch tip and resolve or explicitly record a dirty tree. Preserve user changes
and failed-worker diffs for review. Do not run destructive Git cleanup to make
a diff look clean. Workers do not merge or push; integration happens only
after the Director's review gates pass.

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
