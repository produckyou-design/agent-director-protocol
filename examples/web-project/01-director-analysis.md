# Director Analysis — T-201: CSV Export for Orders Dashboard

## Request

Add a "Export CSV" capability to the existing order management dashboard
(Express API + React client). Users should be able to download the
currently filtered order list as a CSV file.

## Current state

- `server/routes/orders.js` exposes `GET /api/orders` with `status`,
  `dateFrom`, `dateTo` query filters, returning paginated JSON.
- `client/src/pages/OrdersPage.jsx` renders a table of orders fetched via
  `client/src/api/ordersClient.js`, with a toolbar above the table
  containing existing filter controls.
- No export functionality exists anywhere in the codebase.

## Scope decision

Single task, delegated as one contract, because the server endpoint and the
client button are tightly coupled (the button's query params must match the
endpoint's filter contract) and splitting them would require a dependency
edge for no real parallelism benefit.

## Interfaces to preserve

- `GET /api/orders` response shape and pagination — export must be an
  additive endpoint, not a modification of the existing one.
- `OrdersPage` component's existing rendering and default export signature,
  since other pages import it.

## Why `feature_wired_into_flow` is called out explicitly

Dashboard features are a common place for "technically built but not
reachable" failures: a new component or endpoint can exist, pass its own
unit tests, and still never be rendered or invoked from the actual page a
user interacts with. The task contract's `target_behavior` and
`completion_criteria` are written to require an end-to-end, clickable
outcome, not just the existence of a button component or endpoint.

## Delegation

Task contract T-201 issued. Report format:
`implementation-report.schema.json`. Review will independently open the
dashboard and click the button rather than trusting the implementer's
description of it.
