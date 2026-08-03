# Takeover record template

Write this **before** touching any product code directly. Fields mirror
[`schemas/takeover-record.schema.json`](../../../../schemas/takeover-record.schema.json) exactly.
See [TAKEOVER-PROTOCOL.md](../../../../core/TAKEOVER-PROTOCOL.md) — takeover is allowed only after two
full failed revision loops, or when the implementer demonstrably cannot perform the task.
**"The task is small or simple" is never a valid justification.**

```json
{
  "task_id": "T-001",
  "original_requirement": "",
  "first_failure_evidence": "",
  "first_revision_instruction": "",
  "second_failure_evidence": "",
  "second_revision_instruction": "",
  "repeated_failure_cause": "",
  "takeover_justification": "",
  "files_to_modify": [],
  "modification_scope": "",
  "notes": ""
}
```

## Field notes

- `original_requirement` — the requirement exactly as first delegated, not a revised version.
- `first_failure_evidence` / `second_failure_evidence` — concrete evidence from each of the two failed loops (test output, error message, or reviewed diff), each at least 10 characters and drawn from the corresponding [`failure-loop.schema.json`](../../../../schemas/failure-loop.schema.json) records.
- `first_revision_instruction` / `second_revision_instruction` — the evidence-based instructions actually given after each failure.
- `repeated_failure_cause` — the director's own analysis of *why* both loops failed the same way, not a restatement of the symptoms.
- `takeover_justification` — why direct intervention is required now. Reject any draft that reduces to "it's a small fix."
- `files_to_modify` — at least one file; the exact, bounded set the director will touch directly.
- `modification_scope` — the bounded scope of the direct change. Anything discovered beyond this scope during takeover goes back through a new task contract and delegation — it is not absorbed into the takeover.
