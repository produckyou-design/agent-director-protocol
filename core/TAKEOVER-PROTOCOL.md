# Takeover Protocol

This document defines the only conditions under which the director may write product code directly,
and the record it must produce before doing so.

## When takeover is allowed

Per [ROLE-CONTRACT.md](ROLE-CONTRACT.md), the director does not write product code. Takeover is the sole, narrow exception, permitted
ONLY when:

- **(a)** the implementer demonstrably cannot perform the task — for example, the task requires
  access, tooling, or a capability the implementer role genuinely lacks, and this has been
  established with concrete evidence, not assumed in advance; or
- **(b)** at least two full revision loops, as defined in [FAILURE-LOOP.md](FAILURE-LOOP.md), have ended in `counted_as_failure:
  true`.

Both conditions require evidence gathered through the normal delegation and review cycle. Takeover
is never a shortcut chosen instead of delegation; it is a fallback reached only after delegation has
been tried and has objectively failed, or shown to be inapplicable.

**"The task is small or simple" is explicitly NOT a valid exception.** Task size, perceived
triviality, or time pressure never justify skipping delegation. If a task is genuinely trivial,
delegating it costs little; taking it over anyway erodes the review boundary that makes the rest of
the protocol trustworthy.

## The takeover record

Before writing any code under takeover, the director MUST write a takeover record matching [`../schemas/takeover-record.schema.json`](../schemas/takeover-record.schema.json) in
full:

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
with the same rigor as if an implementer had produced the diff. The director reviewing its own
takeover code does not get a lighter check; if anything, the absence of an independent implementer
makes independent evidence more important, not less.

A takeover record and its resulting change do not themselves reset the failure-loop counter for the
task — they close out the specific two loops that triggered the takeover. Any further work on the
same task, if it resumes normal delegation afterward, starts its own loop count.
