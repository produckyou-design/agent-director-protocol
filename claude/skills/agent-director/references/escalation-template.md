# Escalation Request Template

Two forms in this file: the **implementer's** request to the director, and the **director's own**
request to the user. Neither role changes its own model or effort — both stop and ask. Full rule:
[`ESCALATION-PROTOCOL.md`](../../../../core/ESCALATION-PROTOCOL.md).

A third guess-based fix for the same problem is forbidden. Once two attempts at the same root cause
have failed, fill in the matching section below instead of trying again.

---

## Part 1 — Implementer → Director

Mirrors
[`escalation-request.schema.json`](../../../../schemas/escalation-request.schema.json)
field for field.

### request_type

`EFFORT_ESCALATION_REQUEST` (same model, higher reasoning tier) or `MODEL_ESCALATION_REQUEST`
(stronger model needed). You may argue for both, but name the primary one.

**`EFFORT_ESCALATION_REQUEST` is the default** — more reasoning room on the same model is the
cheaper move and is often sufficient on its own. Ask for `MODEL_ESCALATION_REQUEST` only when the
implementer is already at its highest available reasoning effort (no headroom left to test), or
when the evidence points at a capability the current model tier lacks at any effort setting — and
say which of the two applies. A model request made while effort headroom remains, with no stated
reason, is routed back as an effort escalation.

### task

`T-###` or a short task description.

### root_cause_key

A short stable label for the suspected root cause — used to check that attempt_1 and attempt_2
actually targeted the same thing.

### failed_test (optional)

The specific test that keeps failing.

### attempt_1 / attempt_1_result

What the first fix changed, and what actually happened (evidence, not a summary judgment).

### attempt_2 / attempt_2_result

What the second fix changed — a genuinely different approach, not a restatement of attempt_1 — and
what actually happened.

### confirmed_facts

- What is actually known, backed by evidence.

### unresolved_points

- What is still uncertain after both attempts.

### current_model / current_effort

### recommended_model / recommended_effort (optional)

A recommendation, not a directive — the director decides.

### regression_risk

`low` / `medium` / `high` — risk that a third blind attempt widens breakage or touches shared
contracts.

### protected_files (optional)

- Files a next attempt must not touch without explicit director authorization.

### last_passing_test (optional)

The last known-good checkpoint to fall back to.

### exact_next_prompt

The precise instruction to run next once escalation is granted — not "try again."

---

## Part 2 — Director → User (self-escalation)

Mirrors
[`director-escalation-request.schema.json`](../../../../schemas/director-escalation-request.schema.json)
field for field. Use when the director itself — not an implementer — is the one stuck. No high-risk
decision is finalized and no speculative implementation proceeds before the user responds.

### current_model / current_effort

### blocked_decision

The specific design, integration, or risk decision the director cannot confidently make right now.

### confirmed_facts

- What is actually established, with evidence.

### unresolved_conflicts

- The specific conflicting results, designs, or subagent reports that could not be reconciled.

### attempts

- What was already tried at the current model/effort to resolve `blocked_decision`.

### risk_if_continued

What could go wrong if the director proceeds on a guess instead of escalating (data loss, security,
broken shared contract, botched deploy, etc.).

### recommended_model / recommended_effort (optional)

### review_scope

What the upgraded model/effort should actually review or decide — bounded, not "the whole project."

### protected_files (optional)

- Files that must stay untouched.

### last_passing_checkpoint (optional)

The last known-good state to fall back to if escalation does not resolve the block.

### exact_next_prompt

The precise question or task for the upgraded model — or the user — to resolve.

---

## Director's evaluation checklist (before granting either request)

Do not auto-approve. Check, with evidence:

- [ ] Read the actual git diff for both attempts.
- [ ] Read the actual failing test output / logs.
- [ ] Confirmed the two attempts were genuinely different approaches, not restatements.
- [ ] Confirmed both attempts targeted the same `root_cause_key`.
- [ ] Confirmed the problem is narrowed enough to act on.

Then choose exactly one:

- **One more read-only investigation round**, same model/effort — when the block is really
  `diagnosis_gap` (root cause not yet pinned down), not a reasoning/capability gap.
- **Grant as a Rescue Agent promotion** — when the block is a genuine `reasoning_gap` or
  `model_capability_gap`. This merges what used to be separate "raise effort" and "reassign to a
  stronger model" options: fill in
  [`agent-briefing-template.md`](agent-briefing-template.md) Part 2 (promotion notice) before
  anything runs, then hand off via
  [`rescue-agent-template.md`](rescue-agent-template.md). Full flow:
  [`RESCUE-PROTOCOL.md`](../../../../core/RESCUE-PROTOCOL.md).
- **Escalate to the user** — an unresolved design/architecture/security/data-loss judgment call.
- **Suspend the task or roll back** to the last known-passing checkpoint.

**Director direct intervention is never chosen at this point.** It is reachable only after a Rescue
Agent has also failed (or the classification is `requirement_conflict` / `environment_issue`, which
never get a Rescue Agent) — see
[`RESCUE-PROTOCOL.md`](../../../../core/RESCUE-PROTOCOL.md) Step 3, and
still requires a [takeover record](takeover-template.md) per
[`TAKEOVER-PROTOCOL.md`](../../../../core/TAKEOVER-PROTOCOL.md) before any code is touched.

If a granted Rescue Agent promotion also fails, do not escalate or promote a second time on the same
block — the Rescue Agent's own two-attempt limit is exhausted; move to RESCUE-PROTOCOL.md Step 3
(director direct intervention, rollback, user judgment, scope reduction, or investigation pivot).
