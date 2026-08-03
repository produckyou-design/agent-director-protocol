# Revision instruction template

Used inside a `review-result` whose `verdict` is `revision_required`, and as the `instruction` field of
the next [`failure-loop.schema.json`](../../../../schemas/failure-loop.schema.json) record. Every instruction
must be evidence-based — quote the actual failure, never "please fix it" or "try again."
See [FAILURE-LOOP.md](../../../../core/FAILURE-LOOP.md).

```json
{
  "instruction": "",
  "target_files": [],
  "evidence": ""
}
```

## Field notes

- `instruction` — minimum 10 characters. State precisely what must change and why, in terms the implementer can act on without re-reading the whole review.
- `target_files` — the specific files the revision should touch. Should be a subset of the original task's `editable_files`.
- `evidence` — the concrete artifact that motivates the instruction: a verbatim test-output excerpt, a code excerpt, or exact reproduction steps. This is what distinguishes a real revision loop from re-asking the same question.

## Loop record shape

Each full loop (instruction through re-review) is also logged as one entry against
[`schemas/failure-loop.schema.json`](../../../../schemas/failure-loop.schema.json):

```json
{
  "task_id": "T-001",
  "loop_number": 2,
  "instruction": "",
  "implementation_summary": "",
  "test_evidence": "",
  "review_verdict": "revision_required",
  "failure_reasons": [],
  "counted_as_failure": true,
  "notes": ""
}
```

Only a loop that actually ran instruction → implementation → tests → review counts toward the
two-failure threshold in [TAKEOVER-PROTOCOL.md](../../../../core/TAKEOVER-PROTOCOL.md). Regenerating an
answer without a real implementation-and-test cycle is not a loop and does not count.
