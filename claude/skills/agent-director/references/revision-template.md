# Revision Instruction Template

Use this after a review verdict of `revision_required` (or `rejected`, when
re-delegating instead of taking over). Every field must be grounded in
concrete evidence you gathered yourself — not a paraphrase of what the
implementer said. This is what makes a revision loop count as a real loop
rather than a bare re-ask; see
[`FAILURE-LOOP.md`](../../../../core/FAILURE-LOOP.md).

## task_id

`T-###`

## loop_number

The loop this revision instruction starts. `1` is the initial
implementation; a revision instruction issued after loop 1's review starts
loop 2, and so on.

## prior_verdict

`revision_required` | `rejected`

## failure_reasons

From the canonical enum only
([`review-result.schema.json`](../../../../schemas/review-result.schema.json)):

`completion_criteria_unmet` | `test_failure` | `not_runnable` | `regression` |
`interface_violation` | `placeholder_implementation` | `fake_success` |
`not_wired_into_flow` | `instruction_not_applied` | `repeated_same_error`

- `...`

## failure_evidence

Verbatim excerpt(s) of what actually happened: real test output, a
reproduction transcript, or the exact code excerpt that violates the
contract. No paraphrasing.

```
<verbatim test output / diff / reproduction>
```

## exact_instructions

Specific, actionable instructions — not "fix the bug" but what to change and
why, tied directly to `failure_evidence` above.

1. `...`

## target_files

Files the revision must touch (should be a subset of the original task
contract's `editable_files`).

- `path/to/file`

## retest_commands

Exact commands to re-run after the revision, to be executed by the
implementer and then independently re-run by the director.

- `...`

## notes (optional)

`...`
