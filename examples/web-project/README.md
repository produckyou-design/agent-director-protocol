# Example: Feature Added to an Existing Web App (one revision loop)

## Scenario

CSV export is added to an existing Express + React order dashboard. The
first implementation attempt builds a working export endpoint and a working
button component — but never connects the button to the actual dashboard
page. The director catches this, issues an evidence-based revision, and the
second attempt is approved.

## What this example demonstrates

- A task contract for an **additive feature on an existing system**, where
  `interfaces_to_preserve` and `preservation_conditions` are non-empty and
  meaningful (the existing `GET /api/orders` endpoint and `OrdersPage`
  rendering must not change).
- A **revision loop**: implementation → tests → director review → an
  evidence-based `revision_instructions` array → re-implementation →
  re-review, with a `failure-loop` record capturing the full cycle.
- The `not_wired_into_flow` failure reason: code that works in isolation
  but is never reached from the real user flow.
- Why `counted_as_failure: true` applies even though most of the work
  (the server endpoint) was correct — one broken completion criterion in a
  fully-executed loop is enough to count.

## File-by-file walkthrough

| File | Purpose |
|---|---|
| `01-director-analysis.md` | Scope decision and why `feature_wired_into_flow` was flagged as a specific risk before delegation. |
| `02-task-contract.json` | The task contract, including preservation conditions for the existing endpoint and page. |
| `03-implementation-report.json` | Loop 1: implementer reports `status: "complete"`, all criteria `met: true`. |
| `04-review-result.json` | Loop 1 review: `revision_required`, `failure_reasons: ["not_wired_into_flow"]`, with evidence from actually loading the dashboard. |
| `05-failure-loop-1.json` | The recorded loop: instruction, what was actually implemented, test evidence, verdict, `counted_as_failure: true`. |
| `06-implementation-report.json` | Loop 2: the button is wired into `OrdersPage`, and the test now renders the real page. |
| `07-review-result.json` | Loop 2 review: `approved`, `loop_number: 2`. |
| `08-completion.md` | Final summary: what shipped, why loop 1 failed, why loop 2 passed. |

## What to notice

- The implementer's loop 1 tests all passed — the failure was invisible to
  the implementer's own test suite because that suite never rendered the
  page the feature was supposed to appear on. The director's review caught
  it only by independently loading the dashboard, which is why
  `feature_wired_into_flow` and `no_fake_or_placeholder_success` exist as
  separate checks from `tests_actually_executed`.
- The revision instructions in `04-review-result.json` name exact target
  files and cite the exact evidence (no button in the rendered page, no
  `ExportButton` reference in `OrdersPage.jsx`) rather than giving vague
  feedback like "make sure it's hooked up".
