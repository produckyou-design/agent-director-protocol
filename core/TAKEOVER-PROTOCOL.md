# Takeover Protocol

This document defines the only conditions under which the director may write product code directly,
and the record it must produce before doing so.

**Sequencing note:** reaching the failure threshold (the active profile's `implementer.failure_threshold`,
two by default) does NOT by itself authorize takeover, and takeover is never the automatic next step
once it's reached. [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) governs what happens at that point: the director classifies
the failure cause and, for a reasoning or model capability gap, promotes the task to a bounded,
one-shot Rescue Agent (at most two attempts, one axis raised at a time); for a requirement conflict,
it revises the task contract and re-delegates instead — before takeover is even considered.
Condition (b) below is satisfied only once that Rescue Agent step or revised contract has been tried
and failed, or was inapplicable per Rescue Protocol's classification. [ESCALATION-PROTOCOL.md](ESCALATION-PROTOCOL.md) covers
the separate case of a mid-task request for more power (before the failure threshold is reached).

## When takeover is allowed

Per [ROLE-CONTRACT.md](ROLE-CONTRACT.md), the director does not write product code. Takeover is the sole, narrow exception, permitted
ONLY when:

- **(a)** the implementer demonstrably cannot perform the task — for example, the task requires
  access, tooling, or a capability the implementer role genuinely lacks, and this has been
  established with concrete evidence, not assumed in advance. This condition is independent of
  [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) — a missing capability or access right is not fixed by a stronger model, so it
  does not require a Rescue Agent attempt first; or
- **(b)** at least the active profile's `implementer.failure_threshold` (two by default) full revision
  loops, as defined in [FAILURE-LOOP.md](FAILURE-LOOP.md), have ended in `counted_as_failure: true`, **and** the
  Rescue Protocol step that count triggers has run its course: either a Rescue Agent was assigned
  and also failed after its allotted attempts, a revised task contract for a `requirement_conflict`
  was tried and also failed, or Rescue Agent promotion was inapplicable because the failure was
  classified as `environment_issue` (see [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) Step 1). **Reaching the failure
  threshold alone, without having gone through that classification (and, where applicable, a Rescue
  Agent or a revised contract), does NOT satisfy condition (b).**

Both conditions require evidence gathered through the normal delegation and review cycle. Takeover
is never a shortcut chosen instead of delegation, and it is never a shortcut chosen instead of a
Rescue Agent; it is a fallback reached only after delegation — and, for condition (b), Rescue Agent
promotion — has been tried and has objectively failed, or shown to be inapplicable.

**"The task is small or simple" is explicitly NOT a valid exception.** Task size, perceived
triviality, or time pressure never justify skipping delegation. If a task is genuinely trivial,
delegating it costs little; taking it over anyway erodes the review boundary that makes the rest of
the protocol trustworthy.

## The takeover record

Before writing any code under takeover, the director MUST write a takeover record matching [`../schemas/takeover-record.schema.json`](../schemas/takeover-record.schema.json) in
full. When reached via condition (b), `second_failure_evidence` and `second_revision_instruction`
describe whichever step condition (b) actually required to run its course before takeover became
reachable: the **Rescue Agent's** second attempt for `reasoning_gap` / `model_capability_gap`, or the
**revised task contract's** failed re-delegation for `requirement_conflict` — not the original
implementer's second loop in either case.

- **`task_id`** — the task being taken over.
- **`original_requirement`** — the requirement as originally delegated, unmodified by hindsight.
- **`first_failure_evidence`** — concrete evidence of the first failure: test output, error message,
  or reviewed diff.
- **`first_revision_instruction`** — the evidence-based instruction given after the first failure.
- **`second_failure_evidence`** — concrete evidence of the second failure, after the first revision
  loop was fully executed.
- **`second_revision_instruction`** — the evidence-based instruction given after the second failure.
- **`repeated_failure_cause`** — the director's analysis of why the loops kept failing. This must be
  a real causal analysis, not a restatement of "it still didn't work."
- **`takeover_justification`** — why direct intervention is required now. MUST NOT be, or reduce to,
  "the task is small or simple."
- **`files_to_modify`** — the exact files the director will change directly (at least one entry).
- **`modification_scope`** — the bounded scope of the direct changes.

For condition (a) — implementer demonstrably cannot perform the task — `first_failure_evidence` and
`second_failure_evidence` document the concrete demonstration of incapability (e.g. the implementer
reporting `blocked` with a specific missing capability), and `repeated_failure_cause` documents why
that incapability is structural rather than a one-off.

## Scope discipline after takeover

Once takeover begins, the director's changes MUST stay within `modification_scope`. If, while making
the change, the director finds that more files or a wider change than `files_to_modify` /
`modification_scope` is actually needed, that additional work is NOT covered by the existing
takeover record. It goes back through normal delegation ([DELEGATION-PROTOCOL.md](DELEGATION-PROTOCOL.md)) as a new or revised task contract —
the director does not simply expand the takeover in place.

## After takeover

Takeover changes are still subject to the same review gates as any other change (see [REVIEW-GATES.md](REVIEW-GATES.md)), performed
with the same rigor as if an implementer had produced the diff.

**The director does not review its own takeover code.** Per [ROLE-CONTRACT.md](ROLE-CONTRACT.md) → "The director MUST
NOT review its own work," the review goes to a separate reviewer agent running at the director's own
model and reasoning effort, from a fresh context that did not participate in writing the change.
Earlier versions of this document asked the director to hold itself to the same standard here; that
was an instruction, not a control — the context that produced the change also produced the reasoning
for why it is correct, and so cannot supply the adversarial pressure the ten gates assume. The
absence of an independent implementer is precisely why an independent reviewer is required.

A takeover record and its resulting change do not themselves reset the failure-loop counter for the
task — they close out the specific failure loops that triggered the takeover. Any further work on the
same task, if it resumes normal delegation afterward, starts its own loop count.

\n
