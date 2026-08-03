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

Guidance (a hint, not a schema field): `low` for mechanical, well-specified edits (renames, boilerplate, config plumbing); `high` (or `xhigh` for the director's own planning/decomposition pass) for design-heavy or ambiguous tasks. This mirrors the `effort` hint in [`../../profiles/sol-director.yaml`](../../profiles/sol-director.yaml) — adapters map it to the real mechanism or omit it.

## Concurrency

Never run two `codex exec` workers whose `conflict_domains` overlap (files, data structures, interfaces, DB schema, shared config, state, build/packaging, user flows) — see [CONCURRENCY-RULES.md](../../../core/CONCURRENCY-RULES.md). Because each worker is a separate OS process with its own filesystem writes, an overlap is a real race, not just a merge-conflict risk. When in doubt, run sequentially.

## Review gates

Every implementation report the director receives is reviewed against the ten checks in [REVIEW-GATES.md](../../../core/REVIEW-GATES.md) and recorded as a `review-result.schema.json` document — use [`references/review-template.md`](references/review-template.md). A `revision_required` verdict is delivered back to a **new** `codex exec` run as an evidence-based instruction (see [FAILURE-LOOP.md](../../../core/FAILURE-LOOP.md) and [`references/revision-template.md`](references/revision-template.md)) — quoting real test output and file paths, never "please try again."

## Takeover

If two full revision loops on the same task both end in a counted failure, or the implementer demonstrably cannot perform the task, the director may take over — but only after writing a takeover record ([TAKEOVER-PROTOCOL.md](../../../core/TAKEOVER-PROTOCOL.md), schema at [`schemas/takeover-record.schema.json`](../../../schemas/takeover-record.schema.json), template at [`references/takeover-template.md`](references/takeover-template.md)). "The task is small" is never sufficient justification. Takeover means the director edits files directly in its own session — there is no special Codex mechanism for this; it is simply the director not delegating.

## Completion judgment

The director never declares a task done from an implementer's self-reported `status` field. Per [COMPLETION-STANDARD.md](../../../core/COMPLETION-STANDARD.md), completion requires verbatim `output_excerpt` test evidence in the implementation report, one entry per `completion_criteria` item with concrete evidence, and a passing review verdict. Paraphrased or invented test output is a `fake_success` failure, not a completion.

## Reference templates

- [`references/task-template.md`](references/task-template.md) — task-contract fields to fill in before delegating.
- [`references/review-template.md`](references/review-template.md) — the ten checks plus verdict.
- [`references/revision-template.md`](references/revision-template.md) — evidence-based revision instructions.
- [`references/takeover-template.md`](references/takeover-template.md) — the takeover record required before direct edits.
