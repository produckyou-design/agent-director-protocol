# Completion — T-201: CSV Export for Orders Dashboard

## Outcome

Approved on loop 2, after one revision loop. The loop counted as a full
failure because it went all the way through implementation, tests, and
director review before revision instructions were issued.

## What was delivered

- `server/routes/orders.js` — `GET /api/orders/export`, filter-compatible
  with the existing endpoint.
- `server/services/csvExport.js` — CSV formatting.
- `client/src/components/ExportButton.jsx` — the export button.
- `client/src/pages/OrdersPage.jsx` — now actually renders the button in
  its toolbar, wired to the page's live filter state (the loop 1 gap).
- Test suites: 9 passing server tests, 7 passing client tests.

## Why loop 1 counted as a failure

The implementer's loop 1 report claimed `status: "complete"` and every
completion criterion `met: true`, backed by passing tests. But the director
did not stop at re-running the reported tests — it loaded the actual
dashboard page. There was no Export CSV button on screen: `ExportButton.jsx`
existed and worked in isolation, but `OrdersPage.jsx` never imported or
rendered it. The client test also only mounted `ExportButton` directly,
so it passed without ever exercising the real user flow. That combination —
a component that works standalone plus a test that never renders the page
that's supposed to host it — is exactly the `not_wired_into_flow` /
`no_fake_or_placeholder_success` failure pattern the review checks exist to
catch.

## Why loop 2 was approved

The revision instructions were concrete and file-scoped: import and render
`ExportButton` in `OrdersPage.jsx`'s toolbar, and replace the isolated test
with one that renders the full page. Loop 2's diff did exactly that, and
the director verified it by loading the dashboard directly rather than
re-reading the report.
