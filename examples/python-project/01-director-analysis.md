# Director Analysis — T-101: CLI Expense Tracker (new project)

## Request

Build a small command-line expense tracker from scratch: users can add an
expense (amount, category, optional note), list recorded expenses, and print
a running total. No existing code exists — this is a greenfield task.

## Current state

Empty repository. No source files, no tests, no packaging metadata.

## Scope decision

This is small enough to delegate as a single task contract rather than
decomposing into sub-tasks: the three commands (`add`, `list`, `total`) share
one storage module and one CLI entry point, and splitting them would create
artificial interface coordination overhead for no benefit. One implementer,
one task contract, one review pass.

## Risk areas identified for the task contract

- **Data persistence**: must survive process restarts (a plain in-memory
  list is not acceptable) but must not require an external database for a
  single-user CLI tool. Decision: newline-delimited JSON file in the user's
  working directory.
- **Numeric correctness**: money must not be represented as `float` due to
  rounding error accumulation. The contract requires `Decimal`.
- **Error handling**: invalid amounts and a missing/corrupted data file are
  the two failure modes most likely to be skipped by a first-pass
  implementation, so both are called out explicitly as completion criteria
  and error-handling requirements.

## Interfaces to preserve

None — greenfield. `interfaces_to_preserve` in the task contract is
intentionally empty; nothing yet exists that a future task could break.

## Delegation

Single task contract T-101 issued to the implementer. Report format:
`implementation-report.schema.json`. Review will apply all ten standard
checks before acceptance; `feature_wired_into_flow` here means the three
subcommands are actually registered on the CLI entry point, not merely
defined as unused functions.
