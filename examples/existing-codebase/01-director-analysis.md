# Director Analysis — T-301: Weekly Report Off-by-One / Timezone Bug

## Request

Fix a reported bug: weekly sales totals produced by
`src/reports/aggregator.py` are sometimes wrong by roughly one day's worth
of sales, and the error is intermittent depending on which timezone the
report server happens to be running in.

## Current state

`weekly_totals(events)` buckets `SaleEvent` records into ISO week starts by
calling `timestamp.astimezone()` with no explicit timezone (defaulting to
the server's local tz) and then compares against the week boundary with a
strict `<`, which excludes events landing exactly on the boundary
timestamp. Both defects push events across the boundary in different
directions depending on server locale and the exact second of the sale.

## Reproduction

Fixture in `tests/reports/test_aggregator.py` includes a sale at
`2026-08-02T23:30:00Z` (30 minutes before a Monday week boundary) and one at
exactly `2026-08-03T00:00:00Z`. On a server running in `America/New_York`,
both land in the wrong week's total. This reproduces on `main` today.

## Delegation plan and risk area

Single task, `src/reports/aggregator.py` and its test file only. The bug is
narrow in scope but subtle: previous experience with time-boundary bugs is
that a first fix often patches the exact reported test case (hardcoding
around the reproduction fixture) rather than fixing the underlying
UTC-vs-local defect. The task contract's completion criteria are therefore
written against two independent example timestamps, and manual verification
requires the fixture's hand-computed reference totals in
`docs/report-spec.md`, specifically so a fix that only satisfies the
committed test fixture — without generalizing — will be caught.

## What would trigger takeover

Per protocol, only after two full revision loops fail on objective grounds,
or if the implementer demonstrably cannot perform the task. "The bug looks
small" is explicitly not sufficient justification on its own.
