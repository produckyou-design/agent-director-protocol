# Escalation Protocol

This document defines when an implementer or the director must stop making guess-based changes and
request a reasoning-effort or model upgrade instead. **The point is not automatic model switching.**
It is to convert "the same problem keeps failing" into a deliberate, evidence-based request that a
human or the director explicitly grants — never a silent auto-upgrade, and never a third guess.

## No third guess

A third guess-based fix for the same problem is forbidden. A "guess-based fix" is any change made
without the root cause narrowed to evidence that distinguishes it from the two prior attempts. Once
two attempts at the same root cause have failed, the next action is an escalation request (below),
not another attempt.

This is not a new failure-counting system. Where a trigger below corresponds to an existing
[FAILURE-LOOP.md](FAILURE-LOOP.md) failure reason, use that vocabulary — do not invent a parallel one.

## Trigger conditions

Stop and evaluate escalation when any of the following is true:

- Two different fixes for the same root cause have both failed (`repeated_same_error` /
  `completion_criteria_unmet` per [FAILURE-LOOP.md](FAILURE-LOOP.md)).
- The same test fails twice in a row after a fix meant to address it (`test_failure` +
  `repeated_same_error`).
- The failure surface widens with each attempted fix (`regression`, worsening).
- A previously working feature breaks (`regression`).
- A third attempt is about to be made without the root cause narrowed to evidence.
- The change touches a shared contract, architecture, security, deployment, or data-loss risk and
  the judgment is not confident.
- Current confidence in the judgment is below 70%.

**These triggers are deliberately more sensitive than the full-loop threshold in
[FAILURE-LOOP.md](FAILURE-LOOP.md) / [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md)** — the active profile's
`implementer.failure_threshold` (two by default). A confidence or risk signal can fire mid-attempt,
before that many full revision loops have completed — requesting more reasoning power is cheap, so
the bar to ask for it is deliberately lower than the bar for director takeover, regardless of what
the configured threshold is.

### Exclusions

Simple typos, command-input mistakes, and transient environment failures may be excluded from the
failure count. The exclusion reason MUST be logged in the task record or review notes — silently
discounting a failure without a logged reason is not permitted.

## Implementer duty: request, don't switch

An implementer MUST NOT change its own model or reasoning effort. On hitting a trigger, it stops
further speculative changes and submits exactly one of `EFFORT_ESCALATION_REQUEST` or
`MODEL_ESCALATION_REQUEST`, matching
[`../schemas/escalation-request.schema.json`](../schemas/escalation-request.schema.json) field for field:

`task`, `root_cause_key`, `failed_test`, `attempt_1`, `attempt_1_result`, `attempt_2`,
`attempt_2_result`, `confirmed_facts`, `unresolved_points`, `current_model`, `current_effort`,
`recommended_model`, `recommended_effort`, `regression_risk`, `protected_files`, `last_passing_test`,
`exact_next_prompt`.

`EFFORT_ESCALATION_REQUEST` asks for a higher reasoning tier on the same model. `MODEL_ESCALATION_REQUEST`
asks for a stronger model. An implementer may believe both are warranted and say so in the request,
but the final decision belongs to the director.

**Ask for effort first.** `EFFORT_ESCALATION_REQUEST` is the default request type: more reasoning
room on the same model is the cheaper move and is often sufficient on its own. It is also the only
one the director can grant on its own — a [Rescue Agent](RESCUE-PROTOCOL.md) raises effort, never the
model.

`MODEL_ESCALATION_REQUEST` is for when effort is genuinely not the missing ingredient: the
implementer is already at its model's highest available effort, or the evidence points at a
capability the tier does not have at any setting. **Granting it is not something the director does
by itself** — a model change is a cost and policy decision, so the director forwards it to the user
as a `DIRECTOR_ESCALATION_REQUEST` (below). A model request submitted while effort headroom remains,
with no stated reason, is routed back as an effort escalation.

**No third guess-based fix proceeds without a director instruction issued after this request.**

## Director duty: verify before granting

The director does not auto-approve an escalation request. It independently checks:

- The actual git diff for both attempts.
- The actual failing test output and logs.
- Whether the two attempts were genuinely different approaches, not restatements of each other.
- Whether both attempts targeted the same `root_cause_key`.
- Whether the problem is narrowed enough to act on, or is still unbounded.

Then the director chooses exactly one of:

- **Read-only investigation or reproduction, one more round, same model.** The problem isn't narrowed
  enough yet to know whether promotion is even the right move.
- **Promote to a Rescue Agent (one-shot, ≤2 attempts).** Applies when the request's underlying cause
  is `reasoning_gap` or `model_capability_gap` — the same classification used after repeated
  implementer failures. See [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) for the scope package, isolation, and attempt
  limit. **A Rescue Agent raises reasoning effort only**, so this option grants an
  `EFFORT_ESCALATION_REQUEST`; a `MODEL_ESCALATION_REQUEST` cannot be satisfied here and is
  forwarded to the user instead (below).
- **Do not promote.** If the request's underlying cause is actually `requirement_conflict` or
  `environment_issue`, a stronger model will not fix it — route to escalate-to-user or suspend/
  rollback instead (below), per [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) Step 1.
- **Escalate to the user for judgment.** The decision exceeds what the director should decide
  unilaterally (see director self-escalation, below, if the director itself is the one stuck).
- **Suspend the task or roll back.** Continuing is riskier than stopping.

Director direct intervention is never chosen at this point. It is reachable only after a Rescue Agent
has also failed (or was never applicable), through [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) Step 3 — it is the last resort,
not a peer option here, and still requires a takeover record per [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md) even then.

## Relationship to takeover

Escalation is the default first response to a stuck loop, and it is never a shortcut straight to
takeover. [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md)'s threshold and this protocol's "no third guess"
threshold land on the same count by design — both read the same profile's `implementer.failure_threshold`
(two by default) — the difference is the action taken, not the count. At that count, [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) governs what happens next: the director classifies the
failure cause, and for `reasoning_gap` / `model_capability_gap` promotes a bounded, one-shot Rescue
Agent (≤2 attempts) — never the director writing product code directly. Takeover remains reserved
for TAKEOVER-PROTOCOL.md's two narrow conditions: the implementer demonstrably cannot perform the
task at all (unrelated to reasoning power), or a Rescue Agent was tried and also failed, or Rescue
Agent promotion was inapplicable per Rescue Protocol's classification (`requirement_conflict`,
`environment_issue`) and the loop still fails.

## Director self-escalation

The director stops speculative judgment or implementation and requests promotion from the user when
any one of the following holds:

- The same design or integration judgment has been attempted two different ways and remains
  unresolved.
- Conflicting results from multiple subagents cannot be reconciled with evidence.
- The impact on a shared contract, architecture, security, deployment, or data-loss risk cannot be
  confirmed.
- Context loss or misjudgment at the current model is recurring.
- Current judgment confidence is below 70%.
- The current reasoning effort cannot determine a verifiable next action.
- The current model's highest available reasoning effort has already been tried and did not resolve
  the block.
- **An implementer has exhausted its own effort ladder on one task** — a Rescue Agent climbed to the
  model's high effort tiers and the task still fails. Repeated implementation failure at high effort
  is evidence about the *plan*, not the implementer: the design, the decomposition, or the task
  contract is likely wrong. Ask the user to raise **the director's** model and effort so the design
  can be re-examined by a better-resourced director, rather than asking for a bigger implementer.
  See [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) Step 3, option **C**.

The director does not change its own model or reasoning effort automatically. It stops and submits a
`DIRECTOR_ESCALATION_REQUEST` to the user, matching
[`../schemas/director-escalation-request.schema.json`](../schemas/director-escalation-request.schema.json)
field for field: `current_model`, `current_effort`, `blocked_decision`, `attempts`,
`confirmed_facts`, `unresolved_conflicts`, `risk_if_continued`, `recommended_model`,
`recommended_effort`, `review_scope`, `forbidden_scope`, `protected_files`,
`last_passing_checkpoint`, `exact_next_prompt`.

**Before the user decides whether to grant the escalation, the director finalizes no high-risk
decision and attempts no third guess.** After a granted escalation, the director does not restart
the whole project — it re-examines only `review_scope`, the block directly related to it, and
nothing in `forbidden_scope`.

## After escalation

An upgraded model or effort tier does not get a wider mandate. It is bounded to:

- The blocked decision.
- The relevant files.
- The relevant tests.
- The explicitly stated decision scope.

It does not redesign the project or touch unrelated code. Its output is still subject to the same
review gates as any other change — see [REVIEW-GATES.md](REVIEW-GATES.md). An upgraded model's result is not approved without
real evidence any more than a base-tier implementer's would be.

### An upgraded director re-judges, then re-contracts

When the escalation was granted because an implementer exhausted its effort ladder, the upgraded
director does **not** hand the same task contract back to a new implementer. Re-running an
unchanged contract at a higher director tier changes nothing about the specification that the
implementer kept failing against — and that specification is the leading suspect.

Instead, within `review_scope`, the upgraded director re-examines the blocked task **on its own
judgment, not as an edit to its predecessor's** — re-reading the code and the failed attempts,
re-deciding what the task actually requires, and then issuing a **revised task contract** per
[DELEGATION-PROTOCOL.md](DELEGATION-PROTOCOL.md). Treat the earlier contract as evidence about what was tried, not as a
baseline to preserve: `current_state`, `target_behavior`, `completion_criteria`, and the file scope
are all open to change, and the task may be split, narrowed, or re-ordered if that is what the
re-judgment concludes.

This is scoped re-planning, not a project redesign — the rest of the task tree and anything in
`forbidden_scope` stays untouched. The revised contract is delegated as a **fresh task with its own
failure-loop count**: it is a different specification, so the prior loops do not carry over. If the
revised contract also fails, the director does not escalate again on the same block — it moves to
[RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) Step 3's remaining choices (rollback, reduced scope, investigation task, or a
recorded takeover).

If the upgraded attempt also fails, escalation is not repeated a second time on the same block. The
director moves to user judgment, task suspension, or rollback — not a further escalation loop.

\n
