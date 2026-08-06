# Role Contract

This document defines the three roles in the agent-director protocol and the boundaries between
them.

## Roles

The protocol defines exactly three roles: `director`, `implementer`, `reviewer`. These are role
names, not model names. Any capable agent may be assigned to any role; the protocol never prescribes
which underlying model fills a role, and no file in `core/` names one.

A single session may host multiple implementers working on different tasks. A project has exactly
one director acting at a time for a given task tree.

A "Rescue Agent" ([RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md)) is not a fourth role. It is the `implementer` role, filled
with a stronger model or higher reasoning effort for one already-failed task, under stricter scope
and attempt limits than an ordinary implementer assignment. It answers to the same director, is
reviewed under the same [REVIEW-GATES.md](REVIEW-GATES.md), and does not get a lighter check for being better-resourced.

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
- **Regression checking** — confirming that previously working behavior still works after new
  changes land.
- **Failure-cause analysis** — when a revision loop fails, determining the actual cause rather than
  re-issuing the same instruction. See [FAILURE-LOOP.md](FAILURE-LOOP.md).
- **Completion judgment** — declaring a task or project done. See [COMPLETION-STANDARD.md](COMPLETION-STANDARD.md).

### Core rule: the director does not write product code

The director MUST NOT write product code. All product code is written by an implementer, inside a
task contract, under implementer responsibility.

The single exception is takeover, defined in [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md), which is permitted only when the implementer
demonstrably cannot perform the task, or when a [Rescue Agent](RESCUE-PROTOCOL.md) — the bounded, one-shot promotion
assigned after two failed revision loops — has also failed or was inapplicable. **Two failed
revision loops alone do not authorize takeover;** they trigger failure-cause classification and, for
a reasoning or model capability gap, a Rescue Agent attempt first. Takeover requires a written
takeover record before any code is touched.

**"The task is small or simple" is NEVER a valid exception to this rule.** Task size and difficulty
do not authorize the director to bypass delegation. A one-line fix still goes through a task
contract and an implementer.

## Implementer

The implementer executes the work described in a task contract. Its responsibilities are:

- Write code within the assigned scope only — the files and interfaces named in the task contract.
- Write tests that exercise the changed behavior.
- Run the tests and capture real output.
- Fix errors encountered during implementation and testing, within scope.
- Report changes accurately, using the implementation report format required by the task contract.
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

Reviewer is a role, not a separate participant by default. The reviewer role is performed by the
director unless a platform explicitly maps it to a distinct agent. When reviewer and director are
the same actor, the review obligations in [REVIEW-GATES.md](REVIEW-GATES.md) still apply in full — being the same actor does not
relax the evidence requirements.

Platforms MAY assign the reviewer role to a separate agent for independence (for example, a second
pass by a different context). When they do, the reviewer's verdict is still subject to the
director's final completion judgment; the reviewer does not have unilateral authority to declare a
project complete.

## Summary of boundaries

| Role | Writes product code | Writes tests | Declares completion |
|---|---|---|---|
| director | only under takeover | no | yes |
| implementer | yes, in scope | yes | no (self-reports status only) |
| reviewer | no | no | no (advises the director) |
