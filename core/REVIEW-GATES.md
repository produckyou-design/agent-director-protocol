# Review Gates

This document defines the ten mandatory checks the director performs on every implementation report,
matching [`../schemas/review-result.schema.json`](../schemas/review-result.schema.json).

## Principle

The director never trusts a completion report as-is. An implementer's `status: complete` in [`../schemas/implementation-report.schema.json`](../schemas/implementation-report.schema.json) is
an assertion, not evidence. Every review MUST record a `result` (`pass`, `fail`, or
`not_applicable`) and concrete `evidence` for each of the ten checks below before a `verdict` is
issued. "I read the summary and it sounded right" is not evidence.

**The gates assume a reviewer who did not write the change.** Reviewing an implementer's output
satisfies that by construction — different agent, different context — which is why the director
performs it directly. When the director itself authored the diff (a [takeover](TAKEOVER-PROTOCOL.md)), it does not
review its own work: the review goes to a separate reviewer agent at the director's own model and
effort, from a fresh context. See [ROLE-CONTRACT.md](ROLE-CONTRACT.md) → "The director MUST NOT review its own work."

## The ten checks

1. **`code_actually_changed`** — Inspect the actual diff or file contents, not the summary.
   Evidence: file paths and the specific lines changed. Common fake: a summary describing a change
   that was never applied, or a summary describing a bigger change than the diff shows.
2. **`feature_wired_into_flow`** — Trace the changed code from the real entry point (route, CLI
   command, UI action) to confirm it is reachable, not just present. Evidence: the call path or the
   reproduction that exercises it. Common fake: new function is written and even unit-tested but
   never called from anywhere real (`not_wired_into_flow`).
3. **`tests_actually_executed`** — Confirm the test commands in `test_commands` were actually run in
   this loop, not asserted. Evidence: the verbatim `output_excerpt` from `test_executions`,
   cross-checked for plausibility (timestamps, file paths, framework-specific formatting). Common
   fake: a hand-written "results" block that never came from a real run.
4. **`test_results_match_report`** — Confirm the `passed`/`failed`/`exit_code` numbers in the report
   match what the actual output shows. Common fake: output excerpt shows failures but `status` or
   `completion_criteria_status` claims success anyway.
5. **`no_fake_or_placeholder_success`** — Look for stubs, hardcoded return values, mocked-out core
   logic, or tests that assert trivialities (`expect(true).toBe(true)`) instead of real behavior.
   Evidence: the actual implementation code, read in full, not skimmed.
6. **`no_regressions`** — Re-run or inspect the `preservation_conditions` from the task contract.
   Evidence: test output or manual check showing prior behavior still holds. Common fake: only the
   new feature's tests were run; the existing suite was not.
7. **`interfaces_preserved`** — Diff the `interfaces_to_preserve` list against the actual current
   signatures/contracts. Common fake: a "minor" signature change described as compatible when
   callers would break.
8. **`no_out_of_scope_changes`** — Compare `files_changed` against `editable_files` and
   `forbidden_files`. Any touch to a forbidden file, or any file outside the granted scope, is a
   failure of this check regardless of whether the change itself was good.
9. **`error_handling_present`** — Confirm the `error_handling` conditions from the task contract are
   actually implemented, not just the happy path. Evidence: code inspection of the specific error
   branches, or a test that triggers them.
10. **`completion_criteria_met`** — Independently re-check every entry in `completion_criteria`, not
    just the implementer's self-reported `completion_criteria_status`. Evidence: the director's own
    verification of each criterion.

## Beyond implementer-written unit tests

Passing only the tests the implementer wrote is insufficient evidence on its own, because an
implementer under pressure can write tests that pass trivially against its own implementation. The
director MAY and, for user-facing or integration-sensitive tasks, SHOULD require additional
verification using the `additional_tests_required` field: integration tests, regression tests
against the wider suite, or a scripted user-flow check that exercises the feature the way a real
caller would. These are recorded as additional required tests, run before `completion_criteria_met`
and `no_regressions` can pass.

## Verdicts

- **`approved`** — all applicable checks pass; `not_applicable` is used only when a check genuinely
  does not apply (e.g. `error_handling_present` on a task with no error paths).
- **`revision_required`** — at least one check fails but the task is salvageable; requires
  `failure_reasons` (from [FAILURE-LOOP.md](FAILURE-LOOP.md)'s ten definitions) and `revision_instructions`, each with
  `instruction`, `target_files`, and the `evidence` that motivated it.
- **`rejected`** — the task as delegated cannot proceed; requires `failure_reasons`.

Every review that is not `approved` feeds into a failure loop record; see [FAILURE-LOOP.md](FAILURE-LOOP.md) for how failures
accumulate toward the takeover threshold in [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md).

\n