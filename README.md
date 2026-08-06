# agent-director-protocol (ADP)

*[한국어](README.ko.md)*

A platform-neutral operating protocol for AI coding agents: one high-capability
**director** plans, decomposes, delegates, and reviews; **implementer**
subagents write the actual code. When an implementer gets stuck, the protocol
has a defined escalation path — a bounded **Rescue Agent** promotion, then
takeover — instead of leaving "the model just tries harder" to chance. The
core protocol is platform-agnostic; thin adapters bind it to Claude Code and
OpenAI Codex.

## The problem

A single top-tier model working alone tends to do everything itself: read the
code, design the change, write it, test it, and grade its own homework, all in
one uninterrupted pass. That burns the most capable (and most expensive)
model's attention on mechanical edits, and it removes the one thing that
catches silent failures — an independent check between "I wrote the code" and
"the task is done." A model that both implements and reviews its own work has
no adversarial pressure forcing it to look for what it got wrong. And when it
does get stuck, "try again" and "just use a bigger model for everything" are
both bad defaults — one burns turns on a repeated mistake, the other burns
budget on tasks that never needed it.

This repository does not claim a magic percentage improvement in quality or
cost. It describes a mechanism instead: split the work into a role that
**plans, delegates, and reviews** and a role that **implements**, force every
delegated unit of work through a written, checkable contract, require the
reviewing role to verify evidence — actual diffs, actual test output — rather
than trust a self-reported "done," and give a stuck implementer a structured,
disclosed way to ask for more power instead of guessing a third time. The
result is a workflow, not a benchmark claim: read the docs, decide whether the
mechanism fits your project, and judge the outcome yourself.

## Roles

| Role | Writes product code | Writes tests | Declares completion |
|---|---|---|---|
| director | only under a recorded takeover | no | yes |
| implementer | yes, within contract scope | yes | no (self-reports status only) |
| reviewer | no | no | no (advises the director) |

A **Rescue Agent** is not a fourth role — it's the implementer role, filled by
a stronger model or higher reasoning effort for one already-failed task, under
tighter scope and a hard attempt limit. It is reviewed exactly like any other
implementer output. Reviewer is a role, not necessarily a separate participant
— by default the director performs it. Full definitions, boundaries, and the
"director never writes product code" rule:
[`core/ROLE-CONTRACT.md`](core/ROLE-CONTRACT.md).

## How it works

```
 analyze repo ──▶ interpret requirement ──▶ design ──▶ decompose into tasks
      │                                                       │
      │  core/DELEGATION-PROTOCOL.md                          ▼
      │  ▲ disclose agent composition                write a task contract per task
      │  │ before spawning anything                  core/TASK-CONTRACT.md
      │                                                       │
      │                                                       ▼
      │                                    order by dependency / conflict check
      │                                    core/CONCURRENCY-RULES.md
      │                                                       │
      │                                                       ▼
      │                                       delegate ──▶ implement + test
      │                                                (implementer role)
      │                                                       │
      │              stuck? (2 failed attempts,                ▼
      │               same root cause) ◀────────  director review (10 gates)
      │                    │                       core/REVIEW-GATES.md
      │                    ▼                                  │
      │        escalation request                ┌────────────┴────────────┐
      │        core/ESCALATION-PROTOCOL.md        ▼                         ▼
      │                    │                 approved             revision_required
      │                    ▼                      │                         │
      │        director classifies cause          ▼                         ▼
      │        core/RESCUE-PROTOCOL.md    completion standard   evidence-based revision
      │             │             │       core/COMPLETION-STANDARD.md   instruction, loop again
      │   reasoning/model    other cause          ▲                core/FAILURE-LOOP.md
      │      gap only        (spec/env/                                    │
      │             │         rollback)                                    │
      │             ▼             │                                        │
      │   Rescue Agent            │                                        │
      │   (1-shot, ≤2 tries)      │                                        │
      │       │       │           │                                        │
      │  succeeds   fails ────────┤                                        │
      │       │       │           │                                        │
      │       └──▶ review ◀───────┘                                        │
      │            + integrate         director picks ONE:                 │
      │                            direct intervention (takeover, last resort)
      │                            roll back / escalate to user /
      │                            reduce scope / convert to investigation
      │                            core/TAKEOVER-PROTOCOL.md
      ▼
 integration + regression pass across all tasks (core/COMPLETION-STANDARD.md)
```

Each stage is a link above to the core document that defines it in full. The
short version: nothing is delegated vaguely, nothing is accepted on a
self-report, a stuck implementer requests more power rather than guessing a
third time, only a genuine reasoning/model-capability gap earns a bounded
Rescue Agent promotion, director direct coding is the last resort — reachable
only after that promotion has also failed or didn't apply — and "done" is a
director judgment backed by evidence, never an implementer's `status` field.

## Escalation → Rescue Agent → takeover

The part of the protocol most likely to differ from what you'd expect a
solo agent to do: **a third guess-based fix for the same problem is
forbidden.**

1. **Failed attempts at the same root cause, up to the active profile's
   `implementer.failure_threshold`** (default two — different diffs, different
   results, same underlying cause, not re-prompts) trigger an escalation
   request, not another try. An implementer stops and submits
   `EFFORT_ESCALATION_REQUEST` / `MODEL_ESCALATION_REQUEST`; the director can
   submit its own `DIRECTOR_ESCALATION_REQUEST` to the user when it is the one
   stuck. Neither role ever changes its own model or effort — the request is
   only granted after the requester's evidence (actual diffs, actual test
   output) is independently checked. See
   [`core/ESCALATION-PROTOCOL.md`](core/ESCALATION-PROTOCOL.md).
2. **The director classifies the failure** into exactly one cause:
   `diagnosis_gap`, `reasoning_gap`, `model_capability_gap`,
   `requirement_conflict`, `environment_issue`, `rollback_needed`. Only
   `reasoning_gap` and `model_capability_gap` justify more model power — a
   stronger model doesn't fix a contradictory task contract or broken CI.
3. **A genuine reasoning/capability gap → Rescue Agent**: a one-shot promotion,
   scoped to this one task, capped at two attempts (tracked separately from
   the implementer's own loop count), that raises **one axis at a time** —
   `model_capability_gap` bumps the model first and only adds effort on a
   second attempt; `reasoning_gap` bumps effort first and only adds model on a
   second attempt. It works from an isolated last-passing checkpoint with an
   explicit `forbidden_scope` and does not redesign the project. A
   `requirement_conflict`, by contrast, never gets a Rescue Agent — the
   director revises the task contract and re-delegates instead, as ordinary
   planning with better information. Every promotion is
   disclosed to the user *before* it starts — with the prior attempts, the
   reason, the assigned model/effort, and (when it falls outside a
   pre-approved range or adds cost) as an explicit approval request — and
   every outcome, success or failure, gets a matching notice when it ends.
   Nothing here is silent. See
   [`core/RESCUE-PROTOCOL.md`](core/RESCUE-PROTOCOL.md).
4. **Only if the Rescue Agent also fails** (or the cause was never a
   reasoning/capability gap) does the director choose: direct intervention
   (takeover — still gated by a written record, still the last resort, never
   the automatic next step), roll back, escalate to the user, reduce scope, or
   convert the task into a read-only investigation. See
   [`core/TAKEOVER-PROTOCOL.md`](core/TAKEOVER-PROTOCOL.md).

Three schemas make the disclosure requirement checkable rather than aspirational:
[`agent-composition-disclosure.schema.json`](schemas/agent-composition-disclosure.schema.json)
(who's about to run, stated before any spawn),
[`promotion-notice.schema.json`](schemas/promotion-notice.schema.json) (why this
task is being promoted, and the approval gate when needed), and
[`rescue-outcome-notice.schema.json`](schemas/rescue-outcome-notice.schema.json)
(what happened, and whether the team reverted to its normal tier).

## Repository layout

```
agent-director-protocol/
├─ README.md  README.ko.md  LICENSE  CHANGELOG.md
├─ CONTRIBUTING.md  SECURITY.md  CODE_OF_CONDUCT.md  .gitignore
├─ core/                         platform-neutral protocol (11 docs)
│  ├─ ROLE-CONTRACT.md           DELEGATION-PROTOCOL.md
│  ├─ TASK-CONTRACT.md           FAILURE-LOOP.md
│  ├─ REVIEW-GATES.md            CONCURRENCY-RULES.md
│  ├─ ESCALATION-PROTOCOL.md     RESCUE-PROTOCOL.md
│  ├─ TAKEOVER-PROTOCOL.md       STATE-SAFETY.md
│  ├─ COMPLETION-STANDARD.md
├─ claude/                       Claude Code adapter
│  ├─ skills/agent-director/SKILL.md + references/*.md (7 templates)
│  ├─ CLAUDE.md.example          profiles/{opus-director,fable-director}.yaml
│  └─ INSTALL.md
├─ codex/                        OpenAI Codex adapter
│  ├─ skills/agent-director/SKILL.md + references/*.md (7 templates)
│  ├─ AGENTS.md.example          profiles/sol-director.yaml
│  └─ INSTALL.md
├─ schemas/                      11 JSON Schema (draft-07) documents
├─ examples/                     4 worked, schema-valid scenarios
│  ├─ python-project/  web-project/  existing-codebase/  new-project/
├─ scripts/                      validation scripts (check_repository.py, ...)
├─ tests/                        unittest suite
└─ .github/workflows/            CI: runs the validation scripts
```

## Quick install — Claude Code

Copy the skill into a project (or your user-global skills directory), then
merge the director-mode snippet from [`claude/CLAUDE.md.example`](claude/CLAUDE.md.example)
into your `CLAUDE.md`. Commands below are copied from [`claude/INSTALL.md`](claude/INSTALL.md).

```bash
# Project install (macOS/Linux)
mkdir -p <project>/.claude/skills
cp -r claude/skills/agent-director <project>/.claude/skills/agent-director
cp -r core <project>/core
cp -r schemas <project>/schemas
```

```powershell
# Project install (Windows PowerShell)
New-Item -ItemType Directory -Force -Path "<project>\.claude\skills" | Out-Null
Copy-Item -Recurse "claude\skills\agent-director" "<project>\.claude\skills\agent-director"
Copy-Item -Recurse "core" "<project>\core"
Copy-Item -Recurse "schemas" "<project>\schemas"
```

For a user-global install (available in every project), copy to
`~/.claude/skills/agent-director` instead — see the full steps, verification,
profile selection, and uninstall instructions in
[`claude/INSTALL.md`](claude/INSTALL.md).

## Quick install — Codex

Copy `core/`, `schemas/`, and `codex/` into the target repo, then add the
director-mode section from [`codex/AGENTS.md.example`](codex/AGENTS.md.example)
to the repo's `AGENTS.md`. Commands below are copied from [`codex/INSTALL.md`](codex/INSTALL.md).

```bash
cp -r agent-director-protocol/core target-repo/core
cp -r agent-director-protocol/schemas target-repo/schemas
cp -r agent-director-protocol/codex target-repo/codex
```

```powershell
Copy-Item -Recurse agent-director-protocol\core target-repo\core
Copy-Item -Recurse agent-director-protocol\schemas target-repo\schemas
Copy-Item -Recurse agent-director-protocol\codex target-repo\codex
```

Codex has no native "director/implementer" concept — this adapter maps the
protocol onto `AGENTS.md`, `codex exec` worker runs, and named profiles. Full
steps (including the optional native `.agents/skills` discovery path and the
profile-to-`config.toml` mapping) are in [`codex/INSTALL.md`](codex/INSTALL.md).

## 3-minute quick start

1. Install the skill for your platform (above).
2. In a small feature branch, ask the agent to **"act as director for this
   feature"** — pick something with 2+ moving pieces, not a one-line fix.
3. Watch for the sequence described in "How it works": the director should
   first disclose the agent composition (models, effort, whether a Rescue
   Agent is even available this session), then read the relevant code, then
   produce a **task contract** (not start editing files), then delegate that
   contract to a subagent, then require an **implementation report** back
   with real test output, then produce a **review result** scoring the ten
   checks with evidence, and finally a short **completion report** that cites
   what it actually verified.
4. If you see the director editing product code directly, without a task
   contract and without a takeover record — or silently upgrading a subagent
   to a stronger model without telling you — the protocol is not being
   followed. See "Bad usage" below.

## Configuration & model profiles

Profiles (`claude/profiles/*.yaml`, `codex/profiles/sol-director.yaml`) are a
**convention read by the skill's own instructions**, not a mechanism enforced
by Claude Code or Codex. Each profile names preferred models per role, and —
new in this version — a per-task-kind reasoning-effort table the director
must apply on every spawn:

```yaml
# Model names are environment aliases the user may freely change; the protocol never depends on a specific model name.
director:
  preferred_models: [opus-5]
  effort: high        # optional hint; adapters map to platform mechanism or omit
implementer:
  preferred_models: [sonnet-5]
  effort_by_task_kind:
    investigation: high   # root-cause hunts, competing hypotheses, design judgement
    audit: high            # pre-release compliance / security review
    implementation: medium
    pipeline: medium       # release/deploy execution — procedure fidelity, not creativity
    mechanical: low        # version bumps, doc sync, single-line edits
  effort_default: medium
reviewer:
  inherit: director   # default: reviewer == director
```

Model names are environment aliases — swap them for whatever your platform
resolves them to. `core/` never mentions a model name; only `*/profiles/*.yaml`
do. To switch profiles, edit the YAML directly, or (Claude Code) copy the
chosen file to `profile.yaml` next to `SKILL.md`, or (Codex) translate the
`preferred_models`/`effort`/`effort_by_task_kind` fields into your own
`config.toml` / named profile, as described in each platform's `INSTALL.md`.

## Applying this to a new project

Starting from nothing, the director's first job is still analysis and design
before decomposition — there is no existing codebase to read, but there is
still a requirement to interpret and a set of tasks to identify and order
(including which ones are safe to run in parallel). See the worked walkthrough
in [`examples/new-project/`](examples/new-project/) and, for a single-task
greenfield build, [`examples/python-project/`](examples/python-project/).

## Applying this to an existing project

The delegation sequence starts with repository analysis: read the actual
code, its conventions, and its tests before forming an opinion. Bug fixes and
additive features both go through the same task-contract → implement → review
cycle; the difference is that `must_read_files`, `interfaces_to_preserve`, and
`preservation_conditions` usually carry real weight instead of being empty.
See [`examples/web-project/`](examples/web-project/) for an additive feature
with one revision loop, and [`examples/existing-codebase/`](examples/existing-codebase/)
for a bug fix that reaches director takeover after two failed loops.

## Worked examples

| Example | What it shows |
|---|---|
| [`examples/python-project/`](examples/python-project/) | Greenfield CLI tool, one task, approved on the first loop — the simplest full run of the protocol. |
| [`examples/web-project/`](examples/web-project/) | Additive feature on an existing web app; loop 1 fails `not_wired_into_flow`, loop 2 is approved. |
| [`examples/existing-codebase/`](examples/existing-codebase/) | Bug fix; two counted failure loops on the same root cause, followed by a director takeover. |
| [`examples/new-project/`](examples/new-project/) | Two independent tasks on a new service dispatched in parallel, with a full conflict-domain check. |

These four examples predate the Rescue Agent / escalation layer and still
illustrate the takeover path directly (a `requirement_conflict`-style case
where a stronger model wouldn't have helped either). Read them alongside
[`core/RESCUE-PROTOCOL.md`](core/RESCUE-PROTOCOL.md) to see where a Rescue
Agent promotion would now sit before that takeover in a `reasoning_gap` case.

## A real excerpt: task contract

Trimmed from [`examples/existing-codebase/02-task-contract.json`](examples/existing-codebase/02-task-contract.json):

```json
{
  "task_id": "T-301",
  "title": "Fix timezone and off-by-one bug in weekly report aggregator",
  "objective": "Weekly sales totals must be computed consistently in UTC and must include every event from the full 7-day week, so reports do not silently under- or over-count sales depending on server locale or the exact second of a sale.",
  "current_state": "src/reports/aggregator.py's weekly_totals() calls timestamp.astimezone() with no explicit timezone, defaulting to the server's local time, and compares event timestamps to the week boundary using a strict '<', which excludes events landing exactly on the boundary.",
  "target_behavior": "weekly_totals(events) buckets every event by its UTC calendar week, inclusive of the full week, regardless of the server's local timezone setting.",
  "editable_files": ["src/reports/aggregator.py", "tests/reports/test_aggregator.py"],
  "forbidden_files": ["src/reports/exporter.py", "src/billing/invoice_totals.py"],
  "completion_criteria": [
    "A sale event timestamped 2026-08-02T23:30:00Z is counted in the week starting 2026-07-27, not the following week, regardless of server timezone."
  ],
  "test_commands": ["pytest tests/reports/test_aggregator.py -v"],
  "report_format": "implementation-report.schema.json"
}
```

## A real excerpt: review-result verdict

Trimmed from [`examples/python-project/04-review-result.json`](examples/python-project/04-review-result.json)
(an `approved` verdict — see [`examples/existing-codebase/04-review-result.json`](examples/existing-codebase/04-review-result.json)
for a `revision_required` one with `failure_reasons`):

```json
{
  "task_id": "T-101",
  "loop_number": 1,
  "verdict": "approved",
  "checks": {
    "feature_wired_into_flow": {
      "result": "pass",
      "evidence": "Ran `python -m expense_tracker add 12.50 food --note lunch` ... directly in a shell; all three subcommands are registered in cli.py's argparse subparsers and produce the expected output, not just defined in isolation."
    },
    "tests_actually_executed": {
      "result": "pass",
      "evidence": "Re-ran `pytest tests/ -v` independently of the implementer's report: 8 passed in 0.39s, matching the reported test names and count."
    }
  },
  "notes": "Clean first-pass implementation. No revision loop required."
}
```

## Takeover example

[`examples/existing-codebase/`](examples/existing-codebase/) walks through a
timezone/off-by-one bug where two full revision loops fail for the *same*
underlying reason: each attempt patches the exact reproduction date the
director supplied instead of fixing the general UTC week-boundary rule (loop
1 is `placeholder_implementation`, loop 2 is `repeated_same_error` +
`instruction_not_applied`). Only after both loops are recorded as
`counted_as_failure: true` does the director write
[`09-takeover-record.json`](examples/existing-codebase/09-takeover-record.json) —
citing both failures' concrete evidence and a real causal analysis
(`repeated_failure_cause`), not "the task is simple" — and then make a single
bounded direct edit, scoped to one function body, per
[`10-completion.md`](examples/existing-codebase/10-completion.md).

## Parallel work rules

Two tasks may be dispatched to implementers at the same time only if none of
eight conflict domains overlap: `files`, `data_structures`, `interfaces`,
`db_entities`, `shared_configs`, `state_stores`, `build_targets`, `user_flows`.
Any nonempty intersection on any single domain forces sequential execution,
even if the tasks seem unrelated in intent — a shared file alone is always
enough to force sequencing. Full rule and worked examples:
[`core/CONCURRENCY-RULES.md`](core/CONCURRENCY-RULES.md).

Passing that check makes a split *safe*, not *warranted*. The default is the
fewest task contracts that satisfy the verifiable-unit rule — one implementer
working through several steps in sequence is the common case, not the
exception. Splitting into more than one subagent needs one of these reasons, stated as
that subagent's `justification` in the agent-composition disclosure (see
[`schemas/agent-composition-disclosure.schema.json`](schemas/agent-composition-disclosure.schema.json)):

1. **Genuine parallelism benefit** — the pieces have disjoint
   `conflict_domains` and finishing sooner materially matters.
2. **A distinct effort or model tier is actually warranted** for one part
   (e.g. one piece is `investigation`-kind work, the rest is `mechanical`).
3. **Isolating blast radius** — a risky change should be reviewable
   independently of a safe one.
4. **Genuinely independent verifiable outcomes** that would otherwise force
   unrelated work into a single contract, making it harder to review or
   revert in isolation.

"Smaller diffs" or "tidier task IDs" alone is never sufficient. A batch above
the active profile's `director.max_batch_agents` (default 4) requires the
user's explicit approval before anything spawns, regardless of how cleanly it
passes the conflict-domain check. See
[`core/DELEGATION-PROTOCOL.md`](core/DELEGATION-PROTOCOL.md) step 4.

When part of a batch fails, each task is resolved on its own evidence:
passing tasks integrate normally (unless they depend on a failed one), and
each failed task runs its own failure loop with its own count — failures do
not pool across tasks. If a failure reveals the *design* was wrong rather
than one implementer struggling, the director stops integrating and returns
to design.

## State safety

Every other rule here assumes a recoverable working state, so
[`core/STATE-SAFETY.md`](core/STATE-SAFETY.md) states that assumption
explicitly:

- A **last-passing checkpoint** (a real commit SHA or tag, not "the state
  before we started") is established before the first dispatch, and a dirty
  working tree is resolved first — otherwise every later diff is ambiguous.
- **A failed attempt's changes are never destroyed before the director has
  reviewed them.** That diff is the evidence the revision instruction, Rescue
  Agent package, and takeover record all depend on. No `git checkout .`,
  `reset --hard`, or `clean -fd` on unreviewed work.
- **Implementers do not commit to the main line.** Integration is the
  director's step, after review gates pass; an implementer may commit freely
  inside its own worktree or branch.
- **Destructive operations are deliberate decisions**, never incidental
  steps — force-pushing or rewriting a pushed branch, deleting the only copy
  of some work, or discarding the checkpoint itself.
- **Concurrent implementers get isolated working copies.** The
  conflict-domain check covers *intended* changes; it does not stop a stray
  write or a regenerated artifact from one agent landing in another's diff.
  Where no isolation mechanism exists, run sequentially.

## Bad usage (anti-patterns)

- **Delegating "fix the UI" with no contract.** A vague request is not a task
  contract; the director must reproduce the actual problem and write concrete
  `current_state` / `target_behavior` / `completion_criteria` first.
- **The director coding because "it's a small task."** Task size is never a
  valid reason to skip delegation or takeover requirements — see
  `core/ROLE-CONTRACT.md` and `core/TAKEOVER-PROTOCOL.md`.
- **Jumping straight to takeover after two failures.** Two failed loops
  trigger classification and, for a reasoning/capability gap, a Rescue Agent
  attempt *first* — takeover is what happens if that also fails, not the
  automatic next step. See `core/RESCUE-PROTOCOL.md`.
- **Promoting a subagent to a stronger model without telling anyone.** Every
  Rescue Agent promotion — and every return to the normal tier once it's
  resolved — gets a notice at the time it happens. A silent upgrade (or
  silent downgrade back) is a protocol violation even if the resulting code
  is fine.
- **Trusting an implementer's `status: complete` as-is.** It starts a review;
  it never ends one. The director must independently verify evidence.
- **Counting a re-prompt as a revision loop.** Re-asking "make it work" after
  a failure, without a new evidence-based instruction, is not a loop and does
  not count toward the two-failure escalation threshold.
- **Running parallel tasks that share a file.** Even if every other conflict
  domain is independent, two implementers touching the same file concurrently
  is always blocked — sequence them instead.
- **Over-decomposing into many narrow subagents "just to be safe."** The
  default is the fewest tasks that satisfy the verifiable-unit rule, not the
  most. Every disclosed subagent needs a stated `justification`, and a batch
  above `director.max_batch_agents` requires the user's approval before
  anything spawns — passing the conflict-domain check makes a batch *safe* to
  parallelize, not *sized appropriately*. See `core/DELEGATION-PROTOCOL.md`
  step 4 and `core/CONCURRENCY-RULES.md`.
- **An implementer spawning its own subagents.** Only the director delegates.
  An implementer that decides mid-task it needs more help reports that as a
  blocked/out-of-scope finding — it does not act on it. See
  `core/ROLE-CONTRACT.md`.

## Limitations

- **Platform mechanics differ, and this repo does not force parity between
  them.** Claude Code has native subagents (the Task/Agent tool); Codex has no
  equivalent persistent subagent identity — its implementer role here is a
  fresh `codex exec` invocation (or, less preferred, an in-session subagent
  thread) per task. The two adapters describe the same protocol using each
  platform's real primitives, not a shared implementation.
- **Profiles are conventions, not enforcement.** Neither platform has a
  built-in "active profile" concept that this repo hooks into; a profile YAML
  only works if the director's own instructions (the skill) actually read and
  apply it.
- **This is instructions, not a runtime.** Nothing here is code that enforces
  the rules mechanically. Compliance depends entirely on the model actually
  following the protocol — a model that ignores `SKILL.md` or `AGENTS.md`
  will not be stopped from writing product code directly, or from silently
  promoting itself, by anything in this repository.

## Security notes

- Task contracts can legitimately instruct running commands (`test_commands`,
  `manual_verification`). Review `test_commands` before running them in a
  sensitive environment — they run with whatever privileges the implementer
  session has.
- Never put secrets, credentials, or tokens in task contracts, implementation
  reports, review results, escalation requests, or takeover records — these
  are meant to be readable audit artifacts.
- Reports may embed real command output (`test_executions.output_excerpt`).
  Scrub secrets from that output before recording or sharing it.

## Validation

Run the full repository check before relying on any change:

```
python scripts/check_repository.py
```

Requires Python 3.10+ and `pip install jsonschema`. This runs schema
validation for every example JSON document, skill/template structure checks,
cross-file link resolution, and a sensitive-data scan; exit code 0 means
everything passed. CI runs the same command on every change (plain text
status in `.github/workflows/`, no badges).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose changes, the
schema-first workflow, and how to run validation locally.

## License

[MIT](LICENSE) — chosen as the default license for maximum reuse, by
individuals and organizations, on any platform.

## Korean translation

[README.ko.md](README.ko.md) is a full Korean translation of this document.
