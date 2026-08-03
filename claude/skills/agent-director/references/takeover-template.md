# Takeover Record Template

Mandatory record the director must complete **before** writing any product
code directly. Mirrors
[`takeover-record.schema.json`](../../../../schemas/takeover-record.schema.json)
field for field. Takeover is allowed only after two failed revision loops,
or when the implementer demonstrably cannot perform the task — "the task is
small or simple" is never a valid justification. Full rule:
[`TAKEOVER-PROTOCOL.md`](../../../../core/TAKEOVER-PROTOCOL.md).

## task_id

`T-###`

## original_requirement

The requirement as originally delegated (min 10 characters).

## first_failure_evidence

Concrete evidence of the first failure: test output, error message, or
reviewed diff (min 10 characters).

```
<verbatim evidence>
```

## first_revision_instruction

The evidence-based revision instruction given after the first failure (min
10 characters).

## second_failure_evidence

Concrete evidence of the second failure, after the revision loop was fully
executed (min 10 characters).

```
<verbatim evidence>
```

## second_revision_instruction

The evidence-based revision instruction given after the second failure (min
10 characters).

## repeated_failure_cause

The director's analysis of why the loops kept failing (min 10 characters).

## takeover_justification

Why direct intervention is required now. Must NOT be "the task is small or
simple" (min 10 characters).

## files_to_modify

The exact files the director will change directly (at least one required).

- `path/to/file`

## modification_scope

The bounded scope of the direct changes (min 10 characters). Anything
beyond this scope goes back through delegation to an implementer.

## notes (optional)

`...`
