---
name: agent-director
description: Enact the agent-director-protocol on OpenAI Codex CLI — one Codex session directs, decomposes, delegates task contracts to implementer runs, and reviews evidence before declaring anything done.
---

# Agent Director — Codex adapter

This file binds the platform-agnostic protocol in [`core/`](../../../core/) to OpenAI Codex CLI mechanics. It does not restate the rules — it says which Codex feature enacts which rule. Read [ROLE-CONTRACT.md](../../../core/ROLE-CONTRACT.md) first.

## Director

The director is the main, interactive Codex session the user talks to. It runs under a profile named `sol-director` (see [`../../profiles/sol-director.yaml`](../../profiles/sol-director.yaml)) with model alias `sol`.

**The model alias is a user-configurable convenience name, not a real model ID.** Point `sol` at whatever Codex model your `config.toml` resolves it to; the protocol does not care which model that is, only that the director role gets a capable, high-context model. Nothing in `core/` or in this file names a real model.

Per [ROLE-CONTRACT.md](../../../core/ROLE-CONTRACT.md), the director analyzes the repo, turns the request into task contracts (see [TASK-CONTRACT.md](../../../core/TASK-CONTRACT.md) and [`references/task-template.md`](references/task-template.md)), delegates, reviews, and judges completion. **The director does not write product code**, except under a written takeover (below).

## Implementer

Codex has no separate "subagent" object distinct from Codex itself — an implementer here is another Codex run. Two native mechanisms are available; this protocol uses the first as its default delegation path and treats the second as an option:

1. **`codex exec` worker runs (default).** `codex exec` is Codex's documented non-interactive mode: `codex exec "<prompt>"` runs a task to completion outside the TUI, and accepts `--profile <name>`, `-c key=value` overrides, `--json` for a structured event stream, and `--output-schema <path> -o <path>` to force a schema-conformant final message. The director spawns one `codex exec` run per task, passing the **complete task-contract JSON as the prompt** (see [DELEGATION-PROTOCOL.md](../../../core/DELEGATION-PROTOCOL.md)) and requiring the run's final message to be an `implementation-report.schema.json`-conformant JSON document (enforce this with `--output-schema schemas/implementation-report.schema.json` — the path is resolved from the directory where you run `codex exec`, normally the repo root; note `--output-schema` support is model-dependent, so fall back to requesting the JSON in the prompt if your model rejects the flag). This gives each implementer an isolated process and a clean context per task.
2. **In-session subagent threads.** Current Codex CLI releases also support asking the director's own interactive session to spawn subagent threads for focused sub-investigations (inspected/switched with `/agent`), with results folded back as a summary. This is convenient for read-only exploration but is session-bound and less suited to enforcing the isolation and reporting contract this protocol requires, so it is not the default implementer path here.

Whichever mechanism is used, the implementer's obligations from [ROLE-CONTRACT.md](../../../core/ROLE-CONTRACT.md) are unchanged: work only inside `editable_files`, run the `test_commands` for real, and return an implementation report — never a hand-summary.

## Effort mapping

Codex's reasoning-effort knob is the config key `model_reasoning_effort` (values: `minimal | low | medium | high | xhigh`; support and range are model-dependent). The director sets this per task, not globally:

- One-off override on a worker invocation: `codex exec -c model_reasoning_effort=low "<task-contract JSON>"`.
- Standing default for a role: set `model_reasoning_effort` inside the relevant profile file (Codex loads named profiles from `$CODEX_HOME/<profile-name>.config.toml`, selected with `--profile <name>`).

**Set it explicitly on every worker spawn**, per `implementer.effort_by_task_kind` in [`../../profiles/sol-director.yaml`](../../profiles/sol-director.yaml): `investigation`/`audit` → `high`, `implementation`/`pipeline` → `medium`, `mechanical` → `low`. Omitting `-c model_reasoning_effort=...` silently falls back to the profile default, which under-powers investigation and over-powers mechanical work. When a first attempt returns thin evidence, raise effort one step on re-delegation — see [FAILURE-LOOP.md](../../../core/FAILURE-LOOP.md).

## Decompose to the fewest workers that qualify

Before disclosing anything, check whether this really needs N `codex exec` workers or whether some pieces belong in one broader task contract. Splitting further than the minimum needs a concrete reason — genuine parallelism benefit, a distinct `model_reasoning_effort` tier for one part, blast-radius isolation, or genuinely independent verifiable outcomes — not "smaller diffs." See [`DELEGATION-PROTOCOL.md`](../../../core/DELEGATION-PROTOCOL.md) step 4.

## Disclose the agent composition, then assign

Before launching any `codex exec` worker for a batch of tasks, tell the user what is about to run — once per batch, not per invocation — filling in [`references/agent-briefing-template.md`](references/agent-briefing-template.md) Part 1 (mirrors [`agent-composition-disclosure.schema.json`](../../../schemas/agent-composition-disclosure.schema.json)): director model/effort, worker count, each worker's task/model/`model_reasoning_effort` **and `justification`** (why this piece needs its own `codex exec` run rather than folding into another task in the batch), whether they run concurrently, and whether a Rescue Agent promotion (stronger model/profile) is actually reachable in this environment. Work does not start until this has been stated. **If the worker count exceeds the active profile's `director.max_batch_agents`, this disclosure is also an approval request** — `within_preapproved_range: false`, `approval_status: pending` — dispatch waits for `approval_status: granted`, the same pattern an out-of-range Rescue Agent promotion uses. A conflict-free batch (per [CONCURRENCY-RULES.md](../../../core/CONCURRENCY-RULES.md)) is still subject to this cap — conflict-freedom means the batch is *safe*, not that its size needs no sign-off. Mid-task promotions get their own separate notice — see Escalation and Rescue Protocol below — and do not count against `max_batch_agents`.

**A worker must never launch its own `codex exec` workers.** If one reports mid-task that the work needs splitting further, that comes back to the director as an out-of-scope/blocked finding — the director decides whether to re-decompose. This is the containment boundary that keeps a disclosed, approved batch from silently multiplying past what the user saw. See [`ROLE-CONTRACT.md`](../../../core/ROLE-CONTRACT.md).

## Concurrency

Never run two `codex exec` workers whose `conflict_domains` overlap (files, data structures, interfaces, DB schema, shared config, state, build/packaging, user flows) — see [CONCURRENCY-RULES.md](../../../core/CONCURRENCY-RULES.md). Because each worker is a separate OS process with its own filesystem writes, an overlap is a real race, not just a merge-conflict risk. Codex has no native worktree isolation, so give concurrent workers their own `git worktree add` copies explicitly — the conflict-domain check covers *intended* changes, not a stray write or regenerated artifact from one process landing in another's diff. Without isolation, run sequentially.

**When part of a batch fails**, resolve each task on its own evidence: integrate the passing ones (unless they `depends_on` a failed task — then hold and re-review after), and let each failed task run its own failure loop with its own count. Failures do not pool across tasks. If the failure shows the *design* was wrong rather than one worker struggling, stop integrating and return to design. On user interruption, report what completed, what was in flight, and where each state is preserved — never abandon in-flight work silently.

## State safety (git discipline)

- **Establish a last-passing checkpoint** (a real commit SHA/tag, not "the state before we started") before the first `codex exec` dispatch, and resolve a dirty working tree first — otherwise every later diff is ambiguous. This is the same ref a Rescue Agent's scratch worktree resets to.
- **Never destroy a failed worker's changes before reviewing them.** No `git checkout .` / `reset --hard` / `clean -fd` on unreviewed work — the failed diff is the evidence the revision instruction, Rescue Agent package, and takeover record all depend on. Preserve it (scratch branch, named stash, patch) first.
- **Workers don't commit to the main line.** Integration is the director's step, after the review gates pass. A worker may commit freely inside its own worktree/branch.
- **Destructive operations are deliberate decisions**, never incidental steps: force-push or history rewrite of a pushed branch, deleting the only copy of work, or discarding the checkpoint itself. State what will be lost first.
- Verify `files_changed` against the real diff — an omitted incidental change (reformatted file, regenerated lockfile) hides scope creep.

Full rule: [`STATE-SAFETY.md`](../../../core/STATE-SAFETY.md).

## Review gates

Every implementation report the director receives is reviewed against the ten checks in [REVIEW-GATES.md](../../../core/REVIEW-GATES.md) and recorded as a `review-result.schema.json` document — use [`references/review-template.md`](references/review-template.md). A `revision_required` verdict is delivered back to a **new** `codex exec` run as an evidence-based instruction (see [FAILURE-LOOP.md](../../../core/FAILURE-LOOP.md) and [`references/revision-template.md`](references/revision-template.md)) — quoting real test output and file paths, never "please try again."

## Escalation (stop guessing, request an upgrade)

**A third guess-based fix for the same problem is forbidden.** Once `codex exec` attempts at the same root cause have failed the active profile's `implementer.failure_threshold` times (default two — see [`../../profiles/sol-director.yaml`](../../profiles/sol-director.yaml)), the next step is an escalation request, not another worker run. Nobody changes their own model or `model_reasoning_effort`: a worker cannot re-invoke itself at a higher tier — instead its final message (or the director's own read of its failed attempts) is an `EFFORT_ESCALATION_REQUEST` — the default, since more reasoning room on the same model is cheaper and usually sufficient — or a `MODEL_ESCALATION_REQUEST` only when `model_reasoning_effort` is already maxed out or the gap is a capability the tier lacks at any setting, filled in via [`references/escalation-template.md`](references/escalation-template.md) (mirrors [`escalation-request.schema.json`](../../../schemas/escalation-request.schema.json)). The director evaluates the actual diffs and test output for both attempts and either runs one more read-only investigation worker at the same tier, or — for a genuine reasoning/model-capability gap — grants it as a Rescue Agent promotion (below). A granted request gets the same promotion notice / rescue outcome notice pair as an ordinary Rescue Agent promotion, including the approval-required branch when the grant needs a config/profile change outside what's pre-approved.

If the director itself is stuck (conflicting worker outputs, an unresolved shared-contract impact, low confidence on a security/deploy/data-loss judgment), it submits its own `DIRECTOR_ESCALATION_REQUEST` to the user via the same template's Part 2, and finalizes nothing high-risk until the user responds. Full rule: [`ESCALATION-PROTOCOL.md`](../../../core/ESCALATION-PROTOCOL.md).

## Rescue Protocol → takeover (in that order)

Once a task has failed the active profile's `implementer.failure_threshold` times (default **two**
counted revision loops, not mere re-prompts — see [`../../profiles/sol-director.yaml`](../../profiles/sol-director.yaml), which raises
this to 3 by default since a `codex exec` worker run is cheap enough that one extra evidence-based
attempt costs little before promoting), director direct coding is the **last** resort, not the next
step. The director reads the real diff, failing tests, and logs for both attempts and classifies the
cause into exactly one of `diagnosis_gap`, `reasoning_gap`, `model_capability_gap`,
`requirement_conflict`, `environment_issue`, `rollback_needed` — see [RESCUE-PROTOCOL.md](../../../core/RESCUE-PROTOCOL.md) Step 1.

- **`reasoning_gap` / `model_capability_gap`** → promote to a **Rescue Agent**, raising *one axis at a
  time* across its (at most two) `codex exec` attempts — **reasoning effort first**, since more
  reasoning room on the same model is the cheaper move and is often enough on its own:
  ```bash
  # attempt 1 — keep the failed worker's model, raise effort only
  codex exec --profile sol-director -c model_reasoning_effort=high "<rescue task>"

  # attempt 2 (only if attempt 1 also fails) — keep the raised effort, now
  # also move to a stronger model
  codex exec --profile sol-director -c model=<stronger-model> -c model_reasoning_effort=high "<rescue task>"
  ```
  Lead with `-c model=...` on attempt 1 only when the failed worker was **already at its highest
  available `model_reasoning_effort`** — no effort headroom is left to test, and `promotion_reason`
  must say so. Assigning both axes on attempt 1 is likewise allowed when the evidence already makes
  a single-axis attempt clearly futile — state why in `promotion_reason` when you do.
  Before attempt 1 launches, send the [promotion notice](references/agent-briefing-template.md)
  (mirrors [`promotion-notice.schema.json`](../../../schemas/promotion-notice.schema.json)) — if the rescue model/effort falls
  outside the user's pre-approved range or needs a config change, this notice is also an approval
  request; do not launch until `approval_status` is `granted`. Hand it the scope package from
  [`references/rescue-agent-template.md`](references/rescue-agent-template.md) (mirrors [`rescue-agent-task.schema.json`](../../../schemas/rescue-agent-task.schema.json)):
  both prior attempts as reference material, the last-passing checkpoint (a git ref to reset a
  scratch worktree to — Codex has no native worktree isolation, so create one explicitly with
  `git worktree add`), editable/forbidden files, an explicit `forbidden_scope`, and this run's
  `attempt_number` (1 or 2) with its own `assigned_model` / `assigned_effort` — tracked separately
  from the implementer's own loop count. When each attempt ends, send the matching
  [rescue outcome notice](references/agent-briefing-template.md) (mirrors [`rescue-outcome-notice.schema.json`](../../../schemas/rescue-outcome-notice.schema.json)), success or
  failure either way, including `reverted_to_baseline`.
- **`requirement_conflict`** → not a Rescue Agent. Revise the task contract to resolve the
  contradiction and re-delegate as an ordinary new `codex exec` run per [DELEGATION-PROTOCOL.md](../../../core/DELEGATION-PROTOCOL.md) — submit your
  own `DIRECTOR_ESCALATION_REQUEST` first if confidence in the revision is low or it touches
  architecture/security/deployment/data-loss risk. Only if the *revised* contract's run also fails
  does this go to the choice below.
- **`environment_issue` / `diagnosis_gap` / `rollback_needed`** never get a Rescue Agent or a
  revision attempt — a stronger model does not fix broken tooling or a task contract that was never
  the problem. Go straight to the choice below.
- **On a verified Rescue Agent success**, review the real diff and re-run the real tests exactly as for any ordinary implementation report — the director still does not write code.
- **If the Rescue Agent also fails, the revised contract also fails, or a cause never routed to
  either**, the director chooses exactly one: director direct intervention (takeover, below — the only door into it), roll back to the last-passing checkpoint, escalate to the user, reduce task scope, or convert the task into a read-only investigation worker.

**Takeover** requires, before any code is touched: a written takeover record ([TAKEOVER-PROTOCOL.md](../../../core/TAKEOVER-PROTOCOL.md), schema at [`../../../schemas/takeover-record.schema.json`](../../../schemas/takeover-record.schema.json), template at [`references/takeover-template.md`](references/takeover-template.md)) — its `second_failure_evidence` is whichever step actually ran its course: the Rescue Agent's second attempt (`reasoning_gap`/`model_capability_gap`), or the revised task contract's failed re-delegation (`requirement_conflict`) — never the original worker's second loop. "The task is small" is never sufficient justification, and neither is "hit the failure threshold" standing alone — it must have gone through classification and, where applicable, a Rescue Agent or a revised contract first. Takeover means the director edits files directly in its own session — there is no special Codex mechanism for this; it is simply the director not delegating.

## Completion judgment

The director never declares a task done from an implementer's self-reported `status` field. Per [COMPLETION-STANDARD.md](../../../core/COMPLETION-STANDARD.md), completion requires verbatim `output_excerpt` test evidence in the implementation report, one entry per `completion_criteria` item with concrete evidence, and a passing review verdict. Paraphrased or invented test output is a `fake_success` failure, not a completion.

## Reference templates

- [`references/task-template.md`](references/task-template.md) — task-contract fields to fill in before delegating.
- [`references/review-template.md`](references/review-template.md) — the ten checks plus verdict.
- [`references/revision-template.md`](references/revision-template.md) — evidence-based revision instructions.
- [`references/escalation-template.md`](references/escalation-template.md) — implementer→director and director→user escalation request fill-in.
- [`references/rescue-agent-template.md`](references/rescue-agent-template.md) — Rescue Agent scope package fill-in.
- [`references/agent-briefing-template.md`](references/agent-briefing-template.md) — agent composition disclosure, promotion notice, and rescue outcome notice fill-in.
- [`references/takeover-template.md`](references/takeover-template.md) — the takeover record required before direct edits.
