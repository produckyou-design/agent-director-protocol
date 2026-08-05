# Rescue Protocol (one-shot promotion for a failed task)

This document defines what happens after an implementer fails the same task twice: a bounded,
one-shot promotion to a **Rescue Agent** — not immediate director takeover. Director direct coding
remains the last resort, not the default next step.

This document supersedes the previous default of "two failed loops → director takes over" described
in earlier drafts of [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md) and [ROLE-CONTRACT.md](ROLE-CONTRACT.md). Those files now point here.
[ESCALATION-PROTOCOL.md](ESCALATION-PROTOCOL.md) covers a different trigger — an implementer or the director proactively
asking for more power mid-task; this document covers what the director does by default once an
implementer has already failed the same task twice.

## The default flow

The failure count that triggers this flow is the active profile's `implementer.failure_threshold`
— **default two**, the number used throughout this document and its examples (see
[FAILURE-LOOP.md](FAILURE-LOOP.md)). A profile MAY raise it (e.g. when the implementer tier is
cheap enough that an extra guess costs little before promoting) or lower it (never below
one); whatever value is configured, "twice" below means "that many times."

```
implementer fails task the configured number of times (failure_threshold, default 2 counted loops, FAILURE-LOOP.md)
        │
        ▼
director reviews the actual diff, failing tests, and logs
        │
        ▼
director classifies the failure cause (exactly one, below)
        │
        ├─ reasoning gap / model capability gap ──► promote to Rescue Agent (one-shot, ≤2 attempts,
        │                                            one axis raised per attempt — Step 2)
        │                                                   │
        │                                    succeeds ◄─────┤──────► fails again (≤2 attempts used)
        │                                        │                          │
        │                              review + integrate            director chooses:
        │                              (no director coding)          A/B/C/D/E below
        │
        ├─ requirement conflict ──► director revises the task contract & re-delegates
        │                            (ordinary planning, not a Step 3 choice — self-escalate
        │                             first if confidence is low or risk is high)
        │                                        │
        │                          succeeds ◄────┤────► the revised contract also fails
        │                                                        │
        │                                              director chooses: A/B/C/D/E below
        │
        └─ diagnosis gap / environment issue / rollback needed
                    │
                    ▼
           do NOT promote to a Rescue Agent — route straight to director choice A/B/C/D/E
```

Director direct coding (**A** below) is never the automatic next step after two failures. It is one
option among five, chosen only after a Rescue Agent has also failed, after a revised task contract
for a `requirement_conflict` has also failed, or immediately for `environment_issue`.

## Step 1 — classify the failure cause

After reading the real diff, the real failing tests, and the real logs for both failed attempts, the
director assigns exactly one cause:

- **`diagnosis_gap`** — the root cause itself was never correctly identified; both attempts guessed
  at symptoms.
- **`reasoning_gap`** — the root cause is understood, but the fix requires reasoning depth the
  implementer's current effort tier did not apply.
- **`model_capability_gap`** — the root cause is understood, but the fix requires capability (e.g.
  architectural judgment, cross-file reasoning) beyond what the current model tier reliably
  produces.
- **`requirement_conflict`** — the two failures stem from the task contract itself containing
  contradictory or ambiguous requirements, not from implementer weakness.
- **`environment_issue`** — the failures stem from tooling, environment, or infrastructure problems
  unrelated to reasoning or model choice.
- **`rollback_needed`** — the attempts have damaged working state badly enough that recovery, not
  a further fix, is the priority.

**Only `reasoning_gap` and `model_capability_gap` route to a Rescue Agent.** `requirement_conflict`
and `environment_issue` are explicitly NOT treated as reasoning problems — promoting to a stronger
model does not fix a contradictory spec or a broken CI runner. `diagnosis_gap` may earn one
read-only investigation round (not a fix attempt) before re-classification; it does not by itself
justify a Rescue Agent. `rollback_needed` routes directly to option **B** in Step 3.

**`requirement_conflict` does not default to Step 3's five options.** Its default resolution is
the director revising the task contract to resolve the contradiction and re-delegating per
[DELEGATION-PROTOCOL.md](DELEGATION-PROTOCOL.md) — ordinary planning, done again with better information, not an
escalation choice. If confidence in that redesign is low, or it touches architecture, security,
deployment, or data-loss risk, the director uses its own self-escalation path
([ESCALATION-PROTOCOL.md](ESCALATION-PROTOCOL.md) → "Director self-escalation") to request a higher effort tier for
itself *before* finalizing the new contract — it does not silently redesign at the same tier that
already produced two failures downstream. Step 3 is for `requirement_conflict` only if a revised
contract, once tried, also fails; `environment_issue` routes straight to Step 3.

## Step 2 — Rescue Agent (reasoning_gap / model_capability_gap only)

A Rescue Agent is a **single task's** one-shot promotion, not a standing tier. It uses a higher
reasoning effort or a stronger model than the implementer that failed — the director assigns this
explicitly (from the active profile's model/effort options); it is never automatic.

### Escalate one axis at a time

The Rescue Agent's first attempt raises only the axis that matches Step 1's classification, holding
the other fixed — a combined jump on attempt 1 tells the director nothing about which axis actually
mattered:

- **`model_capability_gap`** → attempt 1 uses a stronger model at the failed implementer's own
  effort tier. Only if attempt 1 also fails does attempt 2 add a higher effort tier on top of that
  same stronger model.
- **`reasoning_gap`** → attempt 1 keeps the failed implementer's model and raises only the effort
  tier. Only if attempt 1 also fails does attempt 2 add a stronger model on top of that higher
  effort tier.

Each attempt is its own [`rescue-agent-task.schema.json`](../schemas/rescue-agent-task.schema.json) document
(`attempt_number: 1` or `2`) with its own `assigned_model` / `assigned_effort`, and its own
[promotion notice](../schemas/promotion-notice.schema.json) — attempt 2's notice states plainly what
changed from attempt 1's. A director MAY assign both axes on attempt 1 instead, when the evidence
already makes a single-axis attempt clearly futile — but then `promotion_reason` must say why
staging was skipped, not leave it unstated.

**Every promotion is announced to the user at the time it happens — never a silent internal
decision.** The director sends a promotion notice matching
[`../schemas/promotion-notice.schema.json`](../schemas/promotion-notice.schema.json) field for field:
`task`, `prior_model`, `prior_effort`, `failure_count`, `failed_approaches`, `promotion_reason`,
`rescue_model`, `rescue_effort`, `editable_scope`, `forbidden_scope`, `task_scoped_only` (always
`true` — this promotion applies to this task only), and `within_preapproved_range`.

- If `within_preapproved_range` is `true` (the assigned model/effort is already something the user
  has pre-approved), the director notifies and proceeds.
- If it is `false` — the promotion would require the user to change model settings, exceeds a
  pre-approved model/effort range, or needs extra cost — **the notice is also an approval request.**
  The director does not start the Rescue Agent until `approval_status` becomes `granted`.

The same notice-then-proceed-or-wait rule applies when an
[`EFFORT_ESCALATION_REQUEST` / `MODEL_ESCALATION_REQUEST`](ESCALATION-PROTOCOL.md) is granted mid-task.

### Scope package (what the Rescue Agent receives)

The director hands the Rescue Agent a bounded package, matching
[`../schemas/rescue-agent-task.schema.json`](../schemas/rescue-agent-task.schema.json):

- The failed task, unmodified by hindsight.
- Both prior attempts and their actual results (diffs, test output, logs — verbatim, not
  paraphrased).
- Confirmed facts and unresolved points, separated.
- The last known-passing checkpoint.
- Editable files, forbidden files, completion criteria — same discipline as any
  [task contract](TASK-CONTRACT.md).
- An explicit `forbidden_scope`: what the Rescue Agent may NOT do (e.g. redesign unrelated modules,
  change shared contracts not implicated by the failure).

**The Rescue Agent does not redesign the project.** It receives only the failed task, its own
history, and the scope above — nothing wider.

### Isolation

Before assigning, the director preserves the last-passing checkpoint (the commit, tag, or
green-test state immediately before the first failed attempt). Where the platform supports isolated
working copies (see [CONCURRENCY-RULES.md](CONCURRENCY-RULES.md) on worktree isolation), the Rescue Agent works from that
checkpoint in a separate branch or worktree — not by continuing from the failed implementer's
possibly-contaminated working state. The failed attempts are provided as **reference material**, not
as a starting point the Rescue Agent is forced to build on.

### Attempt limit

The Rescue Agent gets **at most two implementation attempts**, counted separately from the
implementer's own failure-loop count in [FAILURE-LOOP.md](FAILURE-LOOP.md) — a Rescue Agent's `attempt_number` is its own
counter, not a continuation of `loop_number`. After a second Rescue Agent failure, no further
guess-based attempt is made by anyone; proceed to Step 3.

### On success — and on final failure

However the Rescue Agent's work ends, the director sends a matching outcome notice —
[`../schemas/rescue-outcome-notice.schema.json`](../schemas/rescue-outcome-notice.schema.json): `task`,
`result`, `files_changed`, `tests_run` (verbatim, per command), `director_verification`,
`integrated`, `reverted_to_baseline`, and — when `result` is `failure` — `next_step_if_failed` (one of
the five Step 3 choices below).

If the Rescue Agent succeeds, the director reviews the actual diff and re-runs the actual tests —
the same [REVIEW-GATES.md](REVIEW-GATES.md) discipline as any other implementation, no lighter check because a
stronger model produced it — and records that in `director_verification`. **On a verified success,
the director does not write code.** The change is integrated exactly as an ordinary approved
implementation would be (`integrated: true`). Promotion applies only to the one failed task; once it
is resolved, subsequent unrelated tasks return to the normal implementer tier — state
`reverted_to_baseline: true` in the notice, do not let the user infer it from a later report.

Failed Rescue Agent attempts are never merged to the main line automatically — only a
director-reviewed, evidence-checked result is integrated (same rule as takeover's scope discipline).
`integrated` is `false` whenever `result` is `failure`.

## Step 3 — if the Rescue Agent also fails (or was never applicable)

The director chooses exactly one:

- **A. Director direct intervention.** Allowed ONLY when all four hold: the root cause is
  sufficiently identified, the fix is local in scope, a verifying test exists, and direct
  intervention is safer than reassigning to yet another agent. This is [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md) — a
  takeover record is still required before any code is touched. The director does not write
  speculative code when the root cause is still unclear.
- **B. Roll back to the last known-passing checkpoint.**
- **C. Escalate to the user for judgment** — per [ESCALATION-PROTOCOL.md](ESCALATION-PROTOCOL.md)'s director self-escalation path when
  the block is a design/architecture/security/data-loss judgment call.
- **D. Reduce task scope** — split off the part that is achievable and re-delegate it normally;
  park the rest.
- **E. Convert to an investigation task** — when the real problem is that too little is known to
  specify a fix at all; delegate a read-only investigation task instead of another fix attempt.

## What this replaces

- [ROLE-CONTRACT.md](ROLE-CONTRACT.md)'s "single exception is takeover... permitted only when the implementer demonstrably
  cannot perform the task, or when at least two full revision loops have failed" no longer means
  *immediate* takeover at two failures. The two-failure count now triggers classification and,
  for `reasoning_gap` / `model_capability_gap`, Rescue Agent promotion first.
- [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md) condition (b) is now read as "a Rescue Agent was tried and also failed, or
  was inapplicable per Step 1's classification" — not "two loops failed" standing alone. Condition
  (a) (implementer genuinely cannot perform the task — missing access/tooling) is unaffected; it
  does not route through a Rescue Agent, since more reasoning power does not grant missing access.

## Rules that must not be violated

1. Environment issues and requirement conflicts are never treated as reasoning/model problems — they
   do not get a Rescue Agent.
2. A Rescue Agent's attempt count is tracked separately from the implementer's failure-loop count.
3. A verified Rescue Agent success ends the sequence — the director does not then write code anyway.
4. The last-passing checkpoint is preserved before a Rescue Agent starts.
5. No failed change — implementer's or Rescue Agent's — is merged automatically. Integration happens
   only after the director verifies the real diff and real tests.
6. Nothing about roles, review gates, or git safety rules elsewhere in this protocol changes. This
   document adds one bounded step between "two failures" and "takeover"; it does not relax review,
   concurrency, or completion standards.
7. Model/effort assignment for a Rescue Agent is the director's explicit choice (or a
   [`DIRECTOR_ESCALATION_REQUEST`](ESCALATION-PROTOCOL.md) to the user if the director itself is unsure which tier to
   assign) — never an automatic switch.
8. Every promotion gets a [promotion notice](../schemas/promotion-notice.schema.json) when it starts and a
   [rescue outcome notice](../schemas/rescue-outcome-notice.schema.json) when it ends — including
   `reverted_to_baseline`, so the return to the normal tier is stated, not left for the user to infer
   from a later report. Neither direction is a silent internal decision. This applies to a granted
   mid-task escalation request the same as to a Rescue Agent promotion.
9. A Rescue Agent's first attempt raises exactly one axis (model or effort, matching Step 1's
   classification) unless the director states in `promotion_reason` why a combined jump was
   necessary — see Step 2, "Escalate one axis at a time."
10. The failure count that triggers this document is the active profile's
    `implementer.failure_threshold`, not a hardcoded constant — a profile may set it above or below
    two, but never below one, and the count still requires objective `counted_as_failure: true`
    loops per [FAILURE-LOOP.md](FAILURE-LOOP.md), not a raw retry tally.
9. A promotion notice outside the user's pre-approved model/effort range, or requiring extra cost, is
   also an approval request — the Rescue Agent does not start until approval is granted.
