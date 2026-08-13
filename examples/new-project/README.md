# Example: Parallel Distribution of Two Independent Tasks (new project)

## Scenario

A new Go API service needs two starting pieces: a `GET /health` endpoint
(T-401) and a YAML config file loader (T-402). The two are unrelated in
files, data structures, and interfaces, so the director delegates them to
two implementers at the same time instead of running them one after another.

## What this example demonstrates

- The deterministic **`independent_groups` / `conflict_domains` /
  `dependency_edges` check** the director runs before approving parallel
  execution: a table across files, code regions, interfaces, schemas,
  generated output, shared state, data, build targets, and user flows showing
  zero overlap and an empty dependency edge list.
- A **counter-example** in `01-director-analysis.md`: a hypothetical third
  task that *would* force sequential execution, because it would share the
  `interfaces` and `data_structures` domains with T-402.
- Two independent **task contracts** (`02a`/`02b`) with `conflict_domains`
  filled in and genuinely disjoint; the batch plan also records
  `planned_workers = min(independent-group count, observed native capacity)`
  and why one worker cannot absorb both groups.
- Two independent **implementation reports** and **review results**
  (`03a`/`03b`, `04a`/`04b`), each approved without referencing the other
  task's status.
- Why a shared integration point is not included in either parallel task's
  read set: a resource read by both groups is still a shared conflict domain,
  so integration context is supplied after the independent package work lands.

## File-by-file walkthrough

| File | Purpose |
|---|---|
| `00-agent-composition-disclosure.json` | The schema-valid batch disclosure consumed by the semantic dispatch validator. |
| `01-director-analysis.md` | The conflict-domain table proving no overlap, plus the sequential counter-example. |
| `02a-task-contract.json` | T-401: the health endpoint task contract, with `conflict_domains` filled in. |
| `02b-task-contract.json` | T-402: the config loader task contract, with `conflict_domains` filled in. |
| `03a-implementation-report.json` | T-401 implementation report. |
| `03b-implementation-report.json` | T-402 implementation report. |
| `04a-review-result.json` | T-401 review: `approved`, `loop_number: 1`. |
| `04b-review-result.json` | T-402 review: `approved`, `loop_number: 1`. |
| `05-completion.md` | Combined outcome, including the `go build ./...` check that only succeeds once both land. |

## What to notice

- Neither review result references the other task. Parallel-eligibility
  means each side's approval is self-contained — T-401's
  `completion_criteria_met` check does not require T-402 to exist, and
  vice versa, even though the full binary only builds once both are done.
- The conflict-domain table is evidence, not a claim: it lists the actual
  file paths, interface names, and data structures each task touches, so
  the "no overlap" conclusion can be checked column by column rather than
  taken on trust.
- A speed or efficiency claim would not be enough to authorize this batch. The
  two groups are parallel only because their verification paths and domains
  are independent, their dependency edges are empty, and capacity is observed.
