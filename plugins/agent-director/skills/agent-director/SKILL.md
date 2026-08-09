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
worker_dispatch: explicit model=gpt-5.6-luna, reasoning_effort=max
```

The switch changes the operating instructions for this task. It is not a
hidden platform setting: it cannot change the model selected for the current
session or retroactively alter an already-running task.

## Activation and dispatch contract

- The main session is the Director. The user-selected model and effort remain
  the Director settings; do not force a named Director model.
- Every ADP-created native Codex subagent spawn must explicitly supply
  `model="gpt-5.6-luna"` and
  `reasoning_effort="max"`. Never inherit the Director or select
  effort by task kind.
- Prefer no named custom agent/type. A role can be carried in the Task
  Contract and prompt. If a named profile is used, load the exact profile and
  verify that it pins the same model and effort before dispatch.
- The `[agents]` defaults and custom-agent files are defense in depth, not
  proof that a spawn was forced. A missing explicit field is a policy failure.
- Any non-Luna/non-max exception requires explicit user authorization and a
  disclosure naming the exception. There is no silent inheritance or
  escalation.

## Fail-closed worker verification

- When returned/runtime metadata exposes model and effort, verify both before
  using any worker result.
- A mismatch is a policy violation: reject and close the worker and discard its
  output.
- If the native surface cannot accept the explicit pair or cannot expose the
  metadata needed to verify it, stop and report a policy violation/fallback
  requirement. Do not claim forced execution or accept unverified output.

## Required order before spawning

1. Restate the mission, acceptance criteria, constraints, and dependencies.
2. Inspect the repository and identify the actual files, symbols, interfaces,
   schemas, data, and tests involved.
3. Write the smallest sufficient Task Contract set and justify why its contract
   size and total contract/worker count are the minimum safe structure. Cite
   conflict boundaries, dependencies, independent evidence/review, or
   blast-radius isolation and why fewer existing contracts cannot absorb it.
4. Declare conflict domains, including files, code regions, generated output,
   shared state, schemas, database records, and user flows.
5. Choose the narrowest suitable role: investigator, implementer, reviewer, or
   rescue.
6. Reject speed, parallelism, efficiency, task size/complexity, many files,
   context reduction, empty slots, and tidy/smaller task IDs as scale reasons.
7. Publish the full composition disclosure: Director model/effort/source,
   every worker's role, task, explicit model, explicit max effort, model
   ceiling, justification, conflict domains, execution mode, rescue policy,
   and budget.
8. Check the batch and cumulative spawn budgets before each spawn.
9. Spawn native Codex subagent threads by default. Use `codex exec` only
   for CI, non-interactive process isolation, or unavailable native subagents,
   with the same explicit model/effort and verification gates.
10. Require each worker to return actual evidence, changed files, tests, and
    unresolved risks. Do not treat intent or a clean exit as proof.
11. Run an independent read-only review when the task changes behavior,
    schemas, security, shared state, or release-critical files.
12. Reconcile worker results in the Director and make the final completion
    judgment. Workers cannot declare the overall task complete.

Any mid-task contract, worker, investigator, reviewer, revision, or rescue
addition requires a new disclosure first. Its justification must cite newly
discovered evidence, a new conflict domain/dependency, a mandatory independent
review boundary, or a classified failure and explain why an existing
contract/worker cannot absorb it.

## Conflict, concurrency, and budget

- Run independent read-only work in parallel only when evidence sources are
  independent.
- Run overlapping writes sequentially. Shared working-tree writes are
  conflicts even when the agents believe their files are different.
- Respect the native concurrent-thread ceiling from
  `agents.max_concurrent_threads_per_session` (the project adapter default
  is four spawned workers, excluding the Director).
- The protocol budget is four workers per batch and twelve cumulative spawned
  workers per user request. Do not silently exceed either limit.
- Workers may not spawn subagents. The Director owns the topology.

## Rescue and Core escalation

Rescue only raises reasoning effort on the same model. The ordinary Codex ADP
baseline is already `gpt-5.6-luna` at `max`, so Rescue is unavailable for
ordinary runs because no higher same-model effort exists. Preserve failure
evidence and use the Core failure-classification, escalation, and takeover
gates. Never lower effort to pretend a rescue ladder exists.

## State safety and reporting

Preserve user changes. Never reset, overwrite, delete, or publish unrelated
work without explicit authorization. Keep secrets, tokens, credentials, and
private transcripts out of plugin files, reports, commits, and public output.
Before reporting success, verify the real changed files, relevant tests,
metadata acceptance, secrets safety, and integration path. If the surface was
unverifiable, report the blocker rather than completion.

If this plugin is installed without the project adapter, use the same contract,
disclosure, explicit dispatch, and fail-closed policy but do not claim that
project-scoped native config or custom agents were installed.
