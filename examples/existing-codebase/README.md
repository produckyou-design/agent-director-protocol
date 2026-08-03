# Example: Bug Fix in an Existing Codebase (two failures, director takeover)

## Scenario

A timezone/off-by-one bug in a weekly sales report aggregator. Two full
revision loops fail because the implementer keeps patching around the
specific reproduction date the director supplies instead of fixing the
general UTC week-boundary computation. The director then takes over with
a single, narrowly-scoped direct fix.

## What this example demonstrates

- A **bug-fix task contract** on an existing codebase, with
  `preservation_conditions` protecting unrelated call sites and unaffected
  weeks.
- Two consecutive **failure loops**, each `counted_as_failure: true`,
  showing how a fix can pass its own tests while still being a
  `placeholder_implementation` (loop 1) or a `repeated_same_error` /
  `instruction_not_applied` (loop 2).
- A **takeover record** with all ten required fields, where
  `takeover_justification` explicitly cites the two failed loops' evidence
  — never "the task is simple."
- The director's own bounded direct fix in `10-completion.md`, scoped
  exactly to what the takeover record declared in `modification_scope`.

## File-by-file walkthrough

| File | Purpose |
|---|---|
| `01-director-analysis.md` | Bug reproduction and the specific risk (fixes that target the fixture instead of the rule) called out before delegation. |
| `02-task-contract.json` | The bug-fix task contract. |
| `03-implementation-report.json` | Loop 1: a literal date-match special case, reported as complete. |
| `04-review-result.json` | Loop 1 review: `revision_required`, `failure_reasons: ["test_failure", "placeholder_implementation"]`, with a director-run regression date exposing the hardcoding. |
| `05-failure-loop-1.json` | Loop 1 record, `counted_as_failure: true`. |
| `06-implementation-report.json` | Loop 2: naive-datetime handling fixed, but the boundary logic gets a second hardcoded date instead of a general rule. |
| `07-review-result.json` | Loop 2 review: `rejected`, `failure_reasons: ["repeated_same_error", "instruction_not_applied"]`, with a third regression date exposing the same pattern. |
| `08-failure-loop-2.json` | Loop 2 record, `counted_as_failure: true` — two counted failures now on record. |
| `09-takeover-record.json` | All ten required fields: both failures' evidence and instructions, the director's analysis of *why* both loops failed the same way, and a bounded `files_to_modify` / `modification_scope`. |
| `10-completion.md` | The director's direct fix and the verification run across all regression dates surfaced during review. |

## What to notice

- Each loop's own test suite passed. The failures were only visible
  because the director added an independent regression case with a
  *different* date each time — this is why `test_results_match_report`
  and `no_fake_or_placeholder_success` are separate checks from
  `tests_actually_executed`.
- `repeated_failure_cause` in the takeover record names the actual pattern
  (enumerating literal dates instead of generalizing), not a vague
  restatement of "it didn't work twice."
- The takeover's `modification_scope` is deliberately narrow — one
  function body — and explicitly preserves the one thing loop 2 got
  right (the `ValueError` guard), rather than rewriting the file wholesale.
