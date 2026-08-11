# Delegation Protocol

This document defines how a director turns work into delegated, verifiable task contracts. The
platform adapter supplies the actual spawn mechanism and model policy; this Core document supplies
the order, authority, minimality, and evidence rules.

## The delegation sequence

For every task, every state-changing operation, and every native-spawn attempt, the director MUST
first publish a visible work-contract notice and then follow this sequence. A task may be read-only,
but it still starts with the notice:

1. **Analyze the repository.** Read the relevant code, structure, conventions, current instructions,
   and tests before forming an opinion.
2. **Interpret the requirement.** State the observed current behavior and the precise target behavior.
3. **Design.** Decide the overall shape and order before inventing task IDs.
4. **Decompose fewest-first.** Use the smallest number of independently verifiable Task Contracts
   that satisfies the design. A contract may cover multiple related files and steps.
5. **Write each Task Contract.** Every contract must validate against
   [`task-contract.schema.json`](../schemas/task-contract.schema.json), including its worker role,
   model ceiling, reasoning effort, execution mode, concrete subagent justification, and complete
   conflict domains.
6. **Order by dependency.** A task may start only after its `depends_on` tasks have been reviewed
   and approved. Independent read-heavy tasks are candidates for parallel execution.
7. **Run the conflict check.** Compare every pair across files, code regions, data structures,
   interfaces, schemas, database entities, shared configs, state stores, generated artifacts, build
   targets, and user flows. Any overlap or read/write consistency dependency becomes sequential.
8. **Check runtime capacity.** Record native capacity when exposed. If it is unknown, do not invent
   a protocol limit; let the native surface return its actual result and handle slot-full with
   wait/close, re-scope, or return.
9. **Disclose the work contract and agent composition.** Before every task, state-changing
   operation, and native-spawn attempt, send the appropriate visible disclosure matching
   [`agent-composition-disclosure.schema.json`](../schemas/agent-composition-disclosure.schema.json)
   for the complete batch. It must contain `phase`, `user_visible: true`, objective, scope,
   planned contract/worker totals, minimum-safe rationale, worker model/effort, exact tests,
   stop conditions, and the composition fields for any worker batch.
10. **Spawn through the adapter.** Only the director may create the disclosed workers. A worker may
    not create a child worker or silently split its own contract.
11. **Collect actual evidence.** Workers run the stated tests and return the implementation report;
    they do not declare completion. The contract must state any expected long-running command and
    the progress evidence that distinguishes an active task from a stall; a wait timeout alone is
    not a failure signal.
12. **Review and integrate.** The director or an independent reviewer checks the real diff, real
    output, scope, interfaces, preservation conditions, and completion criteria before integration.

Skipping a step is a protocol violation even if the resulting code happens to work.

## Mandatory disclosure phases

Every task begins with `phase: task_start`. A zero-worker task start is valid only when the
work contract explicitly sets `read_only: true` and no worker will be spawned. A worker batch uses
`phase: spawn` and requires positive worker totals. A native-spawn attempt must never be silently
introduced after a task-start notice; it needs its own visible spawn disclosure first.

Any later addition or material change that introduces a contract, worker, investigator, reviewer,
revision, rescue, or scope change requires a new `phase: addition` disclosure before dispatch. The
addition must include all of these fields:

- `changed_scope` — what scope changed;
- `change_summary` — what changed;
- `added_worker_task` — what the added worker will do;
- `addition_basis` — exactly one of `newly_discovered_evidence`, `new_conflict_domain`,
  `new_dependency`, `mandatory_independent_review`, or `classified_failure`;
- `why_existing_workers_cannot_absorb` — why an existing contract or worker cannot absorb it; and
- `new_disclosure: true` — the explicit new-notice marker.

Speed, parallelism, efficiency, task size, empty slots, and tidy IDs are not valid addition bases.
An adapter can validate and document this boundary, but a repository cannot assume that it can
hard-intercept a platform-owned native spawn tool or add a required parameter to it.

## Fewest tasks first

Splitting beyond the minimum requires a concrete reason recorded in the contract and disclosure:

- a distinct conflict boundary or dependency that an existing contract/worker
  cannot safely absorb;
- blast-radius isolation for a risky or independently reversible outcome;
- a separate root-cause investigation or independently verifiable result;
- an independent reviewer context.

These are not valid reasons by themselves: many files, a large-looking diff, tidy task IDs, an empty
agent slot, or a previous worker failure. A failed task normally enters its own evidence-based
revision/rescue path; it does not automatically create a replacement worker.

## Justification gate

Every subagent entry must answer:

> Why can this work not be included in an existing Task Contract or performed by an existing worker?

The answer must name the actual independent result, conflict boundary, investigation need, or review
independence. Abstract wording such as “for efficiency” is insufficient. Missing or formalistic
justification blocks the spawn.

## Approval and runtime-capacity rules

The disclosure records the planned worker count and whether native capacity was observed. The
adapter does not add a concurrent or cumulative numeric cap. A native slot-full response is
external backpressure: wait for workers to finish, close completed workers, re-scope, or return.
A rationale or approval cannot override a native refusal, and capacity saturation never authorizes
direct takeover.

## No recursive delegation

The allowed topology is a star:

```text
                 Director
              /      |      \
          Worker A  Worker B  Reviewer
```

Workers report decomposition needs, newly discovered conflicts, or out-of-scope requirements back
to the director. They do not spawn, reassign, or approve another worker.

## Vague scopes are not delegable

“Improve the feature”, “fix the UI”, and “look into the bug” are not contracts. The director must
locate the problem, record current state, define target behavior, bound editable and forbidden files,
list preservation conditions, and provide objective completion criteria and executable test commands.

## Native versus fallback execution

The Core protocol does not require a particular platform mechanism. Each adapter documents its
native delegation surface and any fallback for non-interactive or process-isolated work. In every
case, the contract, disclosure, conflict check, runtime-capacity observation, worker boundary, and
review gates remain mandatory.
