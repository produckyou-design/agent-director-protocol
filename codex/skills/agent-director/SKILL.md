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

## Disclose the agent composition, then assign

Before launching any `codex exec` worker for a batch of tasks, tell the user what is about to run — once per batch, not per invocation — filling in [`references/agent-briefing-template.md`](references/agent-briefing-template.md) Part 1 (mirrors [`agent-composition-disclosure.schema.json`](../../../schemas/agent-composition-disclosure.schema.json)): director model/effort, worker count, each worker's task/model/`model_reasoning_effort`, whether they run concurrently, and whether a Rescue Agent promotion (stronger model/profile) is actually reachable in this environment. Work does not start until this has been stated. Mid-task promotions get their own separate notice — see Escalation and Rescue Protocol below.

## Concurrency

Never run two `codex exec` workers whose `conflict_domains` overlap (files, data structures, interfaces, DB schema, shared config, state, build/packaging, user flows) — see [CONCURRENCY-RULES.md](../../../core/CONCURRENCY-RULES.md). Because each worker is a separate OS process with its own filesystem writes, an overlap is a real race, not just a merge-conflict risk. When in doubt, run sequentially.

## Review gates

Every implementation report the director receives is reviewed against the ten checks in [REVIEW-GATES.md](../../../core/REVIEW-GATES.md) and recorded as a `review-result.schema.json` document — use [`references/review-template.md`](references/review-template.md). A `revision_required` verdict is delivered back to a **new** `codex exec` run as an evidence-based instruction (see [FAILURE-LOOP.md](../../../core/FAILURE-LOOP.md) and [`references/revision-template.md`](references/revision-template.md)) — quoting real test output and file paths, never "please try again."

## Escalation (stop guessing, request an upgrade)

**A third guess-based fix for the same problem is forbidden.** Once two `codex exec` attempts at the same root cause have both failed, the next step is an escalation request, not a third worker run. Nobody changes their own model or `model_reasoning_effort`: a worker cannot re-invoke itself at a higher tier — instead its final message (or the director's own read of its failed attempts) is an `EFFORT_ESCALATION_REQUEST` / `MODEL_ESCALATION_REQUEST`, filled in via [`references/escalation-template.md`](references/escalation-template.md) (mirrors [`escalation-request.schema.json`](../../../schemas/escalation-request.schema.json)). The director evaluates the actual diffs and test output for both attempts and either runs one more read-only investigation worker at the same tier, or — for a genuine reasoning/model-capability gap — grants it as a Rescue Agent promotion (below). A granted request gets the same promotion notice / rescue outcome notice pair as an ordinary Rescue Agent promotion, including the approval-required branch when the grant needs a config/profile change outside what's pre-approved.

If the director itself is stuck (conflicting worker outputs, an unresolved shared-contract impact, low confidence on a security/deploy/data-loss judgment), it submits its own `DIRECTOR_ESCALATION_REQUEST` to the user via the same template's Part 2, and finalizes nothing high-risk until the user responds. Full rule: [`ESCALATION-PROTOCOL.md`](../../../core/ESCALATION-PROTOCOL.md).

## Rescue Protocol → takeover (in that order)

Once a task has failed twice (two counted revision loops, not mere re-prompts), director direct coding is the **last** resort, not the next step. The director reads the real diff, failing tests, and logs for both attempts and classifies the cause into exactly one of `diagnosis_gap`, `reasoning_gap`, `model_capability_gap`, `requirement_conflict`, `environment_issue`, `rollback_needed` — see [RESCUE-PROTOCOL.md](../../../core/RESCUE-PROTOCOL.md) Step 1.

- **`reasoning_gap` / `model_capability_gap`** → promote to a **Rescue Agent**: a single, bounded `codex exec` run using a stronger model or a higher `model_reasoning_effort` for this one task only (never a standing tier change). Before it starts, send the [promotion notice](references/agent-briefing-template.md) (mirrors [`promotion-notice.schema.json`](../../../schemas/promotion-notice.schema.json)) — if the rescue model/effort falls outside the user's pre-approved range or needs a config change, this notice is also an approval request; do not launch until `approval_status` is `granted`. Hand it the scope package from [`references/rescue-agent-template.md`](references/rescue-agent-template.md) (mirrors [`rescue-agent-task.schema.json`](../../../schemas/rescue-agent-task.schema.json)): both prior attempts as reference material, the last-passing checkpoint (a git ref to reset a scratch worktree to — Codex has no native worktree isolation, so create one explicitly with `git worktree add`), editable/forbidden files, an explicit `forbidden_scope`, and at most two attempts, tracked separately from the implementer's own loop count. When it ends, send the matching [rescue outcome notice](references/agent-briefing-template.md) (mirrors [`rescue-outcome-notice.schema.json`](../../../schemas/rescue-outcome-notice.schema.json)), success or failure either way, including `reverted_to_baseline`.
- **Other causes never get a Rescue Agent** — a stronger model does not fix a contradictory task contract (`requirement_conflict`) or broken tooling (`environment_issue`). Go straight to the choice below.
- **On a verified Rescue Agent success**, review the real diff and re-run the real tests exactly as for any ordinary implementation report — the director still does not write code.
- **If the Rescue Agent also fails (or was never applicable)**, the director chooses exactly one: director direct intervention (takeover, below — the only door into it), roll back to the last-passing checkpoint, escalate to the user, reduce task scope, or convert the task into a read-only investigation worker.

**Takeover** requires, before any code is touched: a written takeover record ([TAKEOVER-PROTOCOL.md](../../../core/TAKEOVER-PROTOCOL.md), schema at [`../../../schemas/takeover-record.schema.json`](../../../schemas/takeover-record.schema.json), template at [`references/takeover-template.md`](references/takeover-template.md)) — when reached via the Rescue Agent path, its `second_failure_evidence` is the Rescue Agent's second attempt, not the original worker's. "The task is small" is never sufficient justification, and neither is "two loops failed" standing alone — it must have gone through classification and, where applicable, a Rescue Agent first. Takeover means the director edits files directly in its own session — there is no special Codex mechanism for this; it is simply the director not delegating.

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
