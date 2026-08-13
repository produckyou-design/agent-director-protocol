# Completion Standard

This document defines what "done" means under this protocol, and who is allowed to say so.

## Completion is a director judgment, not an implementer status

An implementer's `status` field in [`../schemas/implementation-report.schema.json`](../schemas/implementation-report.schema.json) — `complete`, `partial`, `blocked`, or `failed` — is the
implementer's own assessment. **It is never the basis for declaring a task done.** The director
declares completion, and only on the basis of evidence independently reviewed, per [REVIEW-GATES.md](REVIEW-GATES.md). An
implementer reporting `status: complete` starts a review; it does not end one.

## What "done" requires

A task is complete only when all of the following hold, each grounded in evidence gathered by the
director:

1. **All `completion_criteria` are met, with evidence.** Every entry in the task contract's
   `completion_criteria` array has been independently checked by the director, not merely accepted
   from the implementer's `completion_criteria_status`.
2. **All ten review checks pass** (or are legitimately `not_applicable`), per [`../schemas/review-result.schema.json`](../schemas/review-result.schema.json) and [REVIEW-GATES.md](REVIEW-GATES.md):
   `code_actually_changed`, `feature_wired_into_flow`, `tests_actually_executed`,
   `test_results_match_report`, `no_fake_or_placeholder_success`, `no_regressions`,
   `interfaces_preserved`, `no_out_of_scope_changes`, `error_handling_present`,
   `completion_criteria_met`.
3. **Tests were actually executed and match the report.** The verbatim `output_excerpt` in
   `test_executions` was inspected, not the implementer's summary of it. A described test run is not
   an executed test run.
4. **No regressions.** The `preservation_conditions` from the task contract still hold, verified by
   the director, not assumed because "nothing looked related."
5. **Interfaces are preserved.** Every entry in `interfaces_to_preserve` remains unchanged, or any
   change was explicitly authorized and re-delegated as its own task.
6. **Manual verification is done when the task contract specifies it.** If `manual_verification` is
   non-empty, those steps were actually carried out — not skipped because the automated tests
   passed.

A task missing any one of these is not done, regardless of how much work went into it or how
confident the implementer's report sounds.

## Root finalization and worker reconciliation

Before the root Director emits its final response or ends the task, it MUST
reconcile every lifecycle cycle it created. An authoritative terminal native
result such as `completed`, `errored`, `interrupted`, or `shutdown` takes
precedence over inferred non-final classifications. For each terminal cycle, the
Director first captures and persists all available report/evidence and then
enters the atomic cleanup-claim state machine in
[`CONCURRENCY-RULES.md`](CONCURRENCY-RULES.md). At most one native cleanup may
be accepted per lifecycle cycle. A `task_complete`/final native lifecycle event with an open
native edge is completed terminal work awaiting cleanup, not `RUNNING`.

The per-worker reconciliation record required by
[`CONCURRENCY-RULES.md`](CONCURRENCY-RULES.md) is authoritative for cleanup
accounting. Root finalization atomically claims and invokes `unclaimed`, skips
`succeeded`, and does not treat a mere claim as success. For `in_flight`,
`failed`, or `unknown`, it inspects authoritative native state: already closed
becomes `succeeded`; a recorded bounded retry is allowed only when the cycle
remains terminal/open, the prior invocation is proven not accepted, and one
reconciler atomically consumes the retry and claims `in_flight`; otherwise the
unresolved state is preserved and reported without a blind duplicate
invocation. A worker resumed into a new lifecycle receives a new reconciliation
cycle and record; accepted-cleanup accounting is evaluated separately for that
new cycle.

Only when no authoritative terminal native result exists,
`completed_work_unreported` and `unknown` remain non-final classifications;
they are preserved and reported under
[`CONCURRENCY-RULES.md`](CONCURRENCY-RULES.md), not closed merely to force a
report. The Director MUST NOT silently finish while owned children remain
unreconciled.

## Relationship to the failure loop

If evidence review surfaces one or more of the ten objective failures defined in [FAILURE-LOOP.md](FAILURE-LOOP.md)
(`completion_criteria_unmet`, `test_failure`, `not_runnable`, `regression`, `interface_violation`,
`placeholder_implementation`, `fake_success`, `not_wired_into_flow`, `instruction_not_applied`,
`repeated_same_error`), the task is not complete. The director issues a `revision_required` or
`rejected` verdict with evidence-based `revision_instructions`, and a new revision loop begins.
Style or taste preferences are never grounds to withhold completion — only the objective failures
above are.

## Completion for a whole project

A project (or a batch of parallel/sequential tasks) is complete only when every constituent task is
complete under the standard above, integration has been performed, and a final regression pass
confirms the tasks work together — not just individually. Two individually-approved tasks that
conflict when integrated are not a completed project; integration and regression checking (see [ROLE-CONTRACT.md](ROLE-CONTRACT.md))
are director responsibilities that happen after individual task approval, not a substitute for it.

## No unverifiable claims

Completion statements MUST be grounded in what was actually run and observed in this review — actual
test output, actual file contents, actual reproduction steps. Claims like "this should work" or
"this is fine, it's a minor change" are not completion evidence and do not satisfy this standard.

\n
