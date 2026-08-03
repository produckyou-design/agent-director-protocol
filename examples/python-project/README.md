# Example: New Python Project (happy path)

## Scenario

A small CLI expense tracker (`add` / `list` / `total` commands) is built
from scratch. There is no existing code — this is the simplest full run of
the protocol: one task contract, one implementation, one review, approved
on the first loop.

## What this example demonstrates

- A complete, well-formed **task contract** for a greenfield task, including
  how `interfaces_to_preserve`, `preservation_conditions`, and
  `forbidden_files` are legitimately empty when there is nothing yet to
  protect.
- An **implementation report** with `status: "complete"` backed by real,
  independently-reproducible test output (the schema requires at least one
  `test_executions` entry whenever status is `complete`).
- A **review result** where all ten checks pass, including two
  `not_applicable` results (`no_regressions`, `interfaces_preserved`) — the
  correct verdict when there is genuinely nothing to regress or preserve,
  as opposed to marking them `pass` without basis.
- A one-loop **happy path**: no failure loop files exist in this example
  because none occurred.

## File-by-file walkthrough

| File | Purpose |
|---|---|
| `01-director-analysis.md` | Why this was delegated as one task, not decomposed further; risk areas the director identified before writing the contract. |
| `02-task-contract.json` | The full task contract delegated to the implementer. |
| `03-implementation-report.json` | The implementer's report: files changed, tests added, real test execution output, per-criterion evidence. |
| `04-review-result.json` | The director's review: all ten checks, each with the concrete evidence inspected. Verdict: `approved`, `loop_number: 1`. |
| `05-completion.md` | Final summary of what shipped and why it closed in a single loop. |

## What to notice

- The director did not trust the implementer's reported test counts — the
  review evidence for `tests_actually_executed` and
  `test_results_match_report` describes an **independent** re-run of
  `pytest tests/ -v`, not a re-statement of the report.
- `feature_wired_into_flow` evidence describes actually invoking the CLI
  subcommands in a shell, not just confirming the functions exist in
  `cli.py`. A implementation that defined `add()`/`list()`/`total()` but
  never registered them with argparse would fail this check even with
  passing unit tests.
