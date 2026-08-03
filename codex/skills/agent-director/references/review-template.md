# Review result template

Fill in after inspecting an implementation report's actual evidence — never from the implementer's
self-reported `status` alone. Fields mirror [`schemas/review-result.schema.json`](../../../../schemas/review-result.schema.json)
exactly; the ten `checks` keys are mandatory and fixed. See [REVIEW-GATES.md](../../../../core/REVIEW-GATES.md).

```json
{
  "task_id": "T-001",
  "loop_number": 1,
  "verdict": "approved",
  "checks": {
    "code_actually_changed": { "result": "pass", "evidence": "" },
    "feature_wired_into_flow": { "result": "pass", "evidence": "" },
    "tests_actually_executed": { "result": "pass", "evidence": "" },
    "test_results_match_report": { "result": "pass", "evidence": "" },
    "no_fake_or_placeholder_success": { "result": "pass", "evidence": "" },
    "no_regressions": { "result": "pass", "evidence": "" },
    "interfaces_preserved": { "result": "pass", "evidence": "" },
    "no_out_of_scope_changes": { "result": "pass", "evidence": "" },
    "error_handling_present": { "result": "pass", "evidence": "" },
    "completion_criteria_met": { "result": "pass", "evidence": "" }
  },
  "failure_reasons": [],
  "revision_instructions": [],
  "additional_tests_required": [],
  "notes": ""
}
```

## Field notes

- `loop_number` — 1 for the first implementation, 2 for the first revision cycle, and so on. Matches the loop's [`failure-loop.schema.json`](../../../../schemas/failure-loop.schema.json) record.
- Each check's `result` is `pass`, `fail`, or `not_applicable`; `evidence` must say what was actually inspected (a diff, a test-output line, a reproduction step) — not "looks fine."
- `failure_reasons` — required (min 1) when `verdict` is `revision_required` or `rejected`. Use only the canonical enum: `completion_criteria_unmet`, `test_failure`, `not_runnable`, `regression`, `interface_violation`, `placeholder_implementation`, `fake_success`, `not_wired_into_flow`, `instruction_not_applied`, `repeated_same_error`. Style or taste preferences are never a failure reason.
- `revision_instructions` — required when `verdict` is `revision_required`. See [`revision-template.md`](revision-template.md) for the shape of each entry.
- `additional_tests_required` — integration/regression/user-flow tests the director is adding beyond what the implementer wrote, if any.
