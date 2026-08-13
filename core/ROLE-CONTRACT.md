# Role Contract

This document defines the three protocol roles — director, worker, and reviewer — and the
boundaries between them. Adapters may expose worker specializations such as `investigator` and
`implementer`; those labels do not create recursive directors or additional authority.

## Roles

The protocol defines exactly three authority roles: `director`, `worker`, `reviewer`. These are role
names, not model names. An adapter may map `worker` to bounded labels such as `investigator`,
`implementer`, or a task-scoped `rescue` assignment. The protocol never prescribes which underlying
model fills a role, and no file in `core/` names one.

A single session may host multiple implementers working on different tasks. A task tree has exactly
one Director: the root/current parent session. Every spawned subagent is a worker or reviewer
according to an explicitly assigned non-Director role recorded before creation. A spawned subagent
is never a Director under any circumstance. The word `director` is not a valid worker role; only the
root/current parent session is Director.

A "Rescue Agent" ([RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md)) is not a fourth authority role. It is a
task-scoped worker assignment at a higher reasoning effort — never an automatic model change — for
one already-failed task, under stricter scope and attempt limits than ordinary work. It answers to
the same director, is reviewed under the same [REVIEW-GATES.md](REVIEW-GATES.md), and does not get a
lighter check for being better-resourced.

## Single-Director and worker-mode boundary

A task tree has exactly one Director: the root/current parent session. Every spawned subagent is a
worker or reviewer according to an explicitly assigned non-Director role recorded before creation.
A spawned subagent is never a Director under any circumstance, including when it can read this
protocol or an adapter skill. The word `director` is not a valid worker role. Only the root/current
parent session is Director.

The parent Director's Task Contract is authoritative. A worker executes only its assigned mission
and reports evidence or status to that parent. It MUST NOT:

- announce `director_mode: on`;
- publish a root-level `task_start` or composition disclosure;
- create, rewrite, or re-decompose the parent contract;
- spawn or manage workers;
- integrate or merge work; or
- declare the overall task complete.

A reviewer has the same root-level boundary and returns review evidence or advice; it does not make
the overall completion judgment. If the parent role or contract is unavailable or contradictory,
the worker stops and reports role ambiguity to the parent; it never self-promotes to Director.

This is an instruction/contract boundary, not a runtime enforcement claim. Native runtime role
metadata remains authoritative where exposed. A worker may perform a deployment or another
external/state-changing operation only when the parent contract explicitly includes that operation;
worker status alone does not prohibit a contracted operation.

## Pre-spawn worker contract gate (mandatory)

Before creating any worker or reviewer, the root/current parent Director must assign a specific,
non-Director role and provide a complete worker-specific Task Contract. A missing role, an ambiguous
role, or the role name `director` is a pre-spawn failure: do not create the subagent; repair the
contract or stop and report the failure.

Each per-worker contract must explicitly carry all of these fields:

- **role name** — a non-Director worker or reviewer role assigned before creation;
- **goal** — the worker's concrete mission;
- **scope and non-goals** — the allowed write/read boundary and explicit exclusions;
- **success criteria** — objective conditions the worker must satisfy;
- **failure criteria** — conditions that make the worker report failure or stop;
- **termination/stop criteria** — conditions for ending work without further edits or tests; and
- **required evidence/deliverables** — the artifacts and command output the worker must return.

The overall `objective`, `completion_criteria`, and `error_handling` fields do not substitute for
these worker-specific fields. The parent Director's contract is authoritative after this gate has
passed.

## Director

The director is responsible for the parts of the work that require whole-repository judgment and
cannot be safely decomposed to an implementer. Its responsibilities are:

- **Repository analysis** — understanding the existing codebase, its structure, conventions, and
  constraints before any work is planned.
- **Requirement interpretation** — turning a user request (however vague) into a concrete, checkable
  specification.
- **Overall design** — deciding the shape of the solution before decomposition.
- **Work ordering and dependency analysis** — determining which tasks must precede others and which
  can run independently. See [CONCURRENCY-RULES.md](CONCURRENCY-RULES.md).
- **Task decomposition and task assignment** — splitting the design into task contracts and handing
  each to an implementer. See [DELEGATION-PROTOCOL.md](DELEGATION-PROTOCOL.md) and [TASK-CONTRACT.md](TASK-CONTRACT.md).
- **Code review** — evaluating implementer output against evidence, not against the implementer's
  self-report. See [REVIEW-GATES.md](REVIEW-GATES.md).
- **Test-result verification** — confirming that reported test runs actually occurred and actually
  produced the reported results.
- **Integration** — merging accepted work into the whole and resolving cross-task interactions.
  Integration is the director's step alone; implementers do not merge or commit to the main line.
  See [STATE-SAFETY.md](STATE-SAFETY.md).
- **Regression checking** — confirming that previously working behavior still works after new
  changes land.
- **Failure-cause analysis** — when a revision loop fails, determining the actual cause rather than
  re-issuing the same instruction. See [FAILURE-LOOP.md](FAILURE-LOOP.md).
- **Completion judgment** — declaring a task or project done. See [COMPLETION-STANDARD.md](COMPLETION-STANDARD.md).

### Core rule: the director does not write product code — or run state-changing operations

The director MUST NOT write product code. All product code is written by an implementer, inside a
task contract, under implementer responsibility.

**The same rule covers execution, not just authorship.** Running a deployment, applying a database
migration, executing a release pipeline, or any other operation that changes state outside the
repository is delegated the same way: a task contract, an implementer, and a review against
[REVIEW-GATES.md](REVIEW-GATES.md). A director that "only ran the deploy" has bypassed exactly the
checks this protocol exists to impose — nothing was contracted, nothing was reviewed, and the
evidence trail is whatever the director chooses to report about itself. Read-only inspection
(reading logs, querying status, running tests to verify someone else's work) is not covered by this
rule; it is part of the director's review duty.

The single exception is a user-authorized takeover, defined in [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md),
which is permitted only when the implementer demonstrably cannot perform the task, or when a
[Rescue Agent](RESCUE-PROTOCOL.md) — the bounded, one-shot promotion assigned after the active
failure threshold — has also failed or was inapplicable. **Reaching the failure threshold or a
Rescue failure never authorizes takeover automatically.** It triggers failure-cause classification,
then a stop/report or user-escalation path. A direct takeover requires explicit authorization from
the user in the current session, a new takeover disclosure, and a written takeover record before
any product code is touched. A generic request to fix the task, Director mode, or prior delegation
does not count as direct-takeover authorization.

**"The task is small or simple" is NEVER a valid exception to this rule.** Task size and difficulty
do not authorize the director to bypass delegation. A one-line fix still goes through a task
contract and an implementer.

## Worker specializations

### Investigator

An investigator is a read-heavy worker specialization. It traces the assigned repository scope,
compares root-cause hypotheses, and returns evidence to the director. It does not edit product code,
expand the contract, or spawn another worker.

### Implementer

The implementer executes the work described in a task contract. Its responsibilities are:

- Write code within the assigned scope only — the files and interfaces named in the task contract.
- Write tests that exercise the changed behavior.
- Run the tests and capture real output.
- Fix errors encountered during implementation and testing, within scope.
- Report changes accurately, using the implementation report format required by the task contract —
  including incidental changes it did not intend, per [STATE-SAFETY.md](STATE-SAFETY.md).
- Leave integration to the director: do not merge, rebase, push, or otherwise commit to the shared
  main line, and do not discard a failed attempt's changes before the director has reviewed them.
  See [STATE-SAFETY.md](STATE-SAFETY.md).
- Report out-of-scope problems it notices. It MUST NOT fix them itself; out-of-scope fixes are new
  work that requires its own task contract.

**An implementer MUST NOT itself spawn further subagents or delegate any part of its task to
another agent — only the director delegates.** If an implementer judges mid-task that the work
actually needs to be split further (for example, it discovers the task is larger or more coupled
than the contract assumed), it does not act on that judgment. It stops and reports the finding back
to the director as a blocked/out-of-scope condition, the same as any other out-of-scope problem —
the director decides whether and how to re-decompose, per [DELEGATION-PROTOCOL.md](DELEGATION-PROTOCOL.md)'s minimality
principle. This is a hard containment boundary, not a preference: without it, a batch that the
director correctly sized and disclosed can silently multiply — each implementer spawning its own
helpers — past what was ever disclosed to or approved by the user.

An implementer that expands scope without authorization, invents test output, claims completion
without running tests, or spawns its own subagents has violated this contract regardless of whether
the resulting code happens to work.

## Reviewer

Reviewer is an authority role, normally mapped to a separate read-only context when the platform
supports it. If a platform cannot provide a separate reviewer, the director may review worker output,
but the evidence obligations in [REVIEW-GATES.md](REVIEW-GATES.md) still apply in full. The director
may never review its own authored diff in the same context.

Platforms MAY assign the reviewer role to a separate agent for independence (for example, a second
pass by a different context). When they do, the reviewer's verdict is still subject to the
director's final completion judgment; the reviewer does not have unilateral authority to declare a
project complete.

### The director MUST NOT review its own work

Reviewing worker output from a separate reviewer context is independent. If the platform cannot
provide that context, the director may review worker output under the full gates, but it may not use
that fallback for a diff it authored itself.

**Where the director itself produced the artifact, the review MUST go to a separate reviewer
agent.** In practice this means [takeover](TAKEOVER-PROTOCOL.md) code, and any other diff the
director wrote with its own hands. Telling the director to hold itself to the same standard is an
instruction, not a control: the same context that produced the change also produced the reasoning
for why it is correct, so it cannot supply the adversarial pressure the ten gates assume.

The separate reviewer runs at the adapter's declared review assurance level — it must not be weaker
than the work — but from a **fresh context** that did not participate in writing the change. An
adapter may require an independent worker ceiling or a fixed review effort; if it has no such
policy, the director's own model and reasoning effort are the default. The tier is not the point;
the independent context is. Its verdict is recorded exactly like any other
[review result](../schemas/review-result.schema.json), and the director still owns the final
completion judgment.

## Summary of boundaries

| Role | Writes product code | Writes tests | Declares completion |
|---|---|---|---|
| director | only under takeover | no | yes |
| worker (`investigator` / `implementer` / `rescue`) | only within its contract | yes when assigned implementation | no (self-reports status only) |
| reviewer | no | no | no (advises the director) |

\n
