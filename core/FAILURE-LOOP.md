# Failure Loop

This document defines what counts as one revision loop and lists the ten objective failure
definitions used across the protocol.

## What counts as a loop

A **revision loop** is the full cycle:

instruction → implementation → tests → director review → evidence-based revision instruction →
re-implementation → re-test → re-review

All eight stages must occur for the cycle to count as one loop. In particular:

- The instruction that starts a re-implementation MUST be evidence-based — grounded in specific test
  output, a specific code excerpt, or a specific reproduction, not a restated version of the
  original request.
- **Re-asking the same question or regenerating an answer without new evidence does NOT count as a
  loop.** If the director simply repeats "make it work" after a failed attempt, no loop has
  occurred, regardless of how much wall-clock time passed or how many messages were exchanged.
- Loops are numbered per task, starting at 1 for the initial implementation cycle. `loop_number: 2`
  is the first revision cycle, and so on.

Loop records are written using [`../schemas/failure-loop.schema.json`](../schemas/failure-loop.schema.json): `task_id`, `loop_number`, `instruction`,
`implementation_summary`, `test_evidence` (a verbatim excerpt, never paraphrased), `review_verdict`,
`failure_reasons`, `counted_as_failure`, and optional `notes`.

Only loops where `counted_as_failure` is `true` count toward the failure threshold that triggers
[RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) classification and, ultimately, permits takeover under
[TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md). That threshold is the active profile's
`implementer.failure_threshold` — **default two** — not a value hardcoded in this document; a
profile may raise or lower it (never below one), and every other document in this protocol that
says "two failures" means "that configured count." A loop that ends in `review_verdict: approved`
is not a failure. A loop that ends in `revision_required` or `rejected` for an objective reason (see
below) is counted.

## The ten objective failure definitions

These are the only classifications used in `failure_reasons` across [`../schemas/failure-loop.schema.json`](../schemas/failure-loop.schema.json) and [`../schemas/review-result.schema.json`](../schemas/review-result.schema.json). Style or taste
differences are NEVER a failure reason under this protocol.

1. **`completion_criteria_unmet`** — One or more of the task contract's `completion_criteria` were
   not satisfied, whether or not the implementer reported them as met.
2. **`test_failure`** — A reported or required test command actually failed (nonzero exit code,
   failing assertions), regardless of what the implementer's summary claims.
3. **`not_runnable`** — The code does not build, start, or execute in the environment the task
   targets — a more basic defect than a failing test.
4. **`regression`** — Previously working behavior, covered by `preservation_conditions` or
   otherwise, now behaves differently or breaks.
5. **`interface_violation`** — A function signature, endpoint, CLI flag, schema, or other item
   listed in `interfaces_to_preserve` was changed without authorization.
6. **`placeholder_implementation`** — The change is a stub, `TODO`, hardcoded return value, or
   otherwise does not implement the real target behavior, even if it superficially compiles or
   passes a shallow test.
7. **`fake_success`** — Reported test output, results, or evidence do not match what actually
   happened — invented, paraphrased, or edited output presented as real.
8. **`not_wired_into_flow`** — The new code exists but is not actually reachable from the real user
   flow, entry point, or caller it was meant to serve.
9. **`instruction_not_applied`** — The prior revision instruction was not acted on, in whole or in
   part.
10. **`repeated_same_error`** — The same defect recurs after a revision instruction meant to fix it,
    indicating the root cause was not addressed.

## Using these definitions

Both loop records and review results MUST use these exact enum values — no free-text failure
categories. When a loop fails for an objective reason, the director's next instruction must name the
specific failure reason(s) and cite evidence, so the next loop is grounded rather than a repeat of
the same guess. Review mechanics that surface this evidence are defined in [REVIEW-GATES.md](REVIEW-GATES.md).
