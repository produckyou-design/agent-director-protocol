# agent-director-protocol (ADP)

*[한국어](README.ko.md)*

**Stop taking "Done!" at face value from an agent that graded its own homework.**

ADP turns one coding agent into a **director** that plans, delegates, and then
*verifies* — against the actual diff and the actual test output — before
anything counts as finished. Implementation goes to **implementer** subagents
working from written, checkable contracts. A stuck implementer escalates with
evidence instead of guessing a third time; a promotion to a stronger model is
bounded and disclosed, never silent; and nothing spawns a swarm of subagents
behind your back.

It is a protocol, not a framework — Markdown rules, JSON Schemas, and thin
adapters for **Claude Code** and **OpenAI Codex**. No runtime, no dependency
to install into your project.

## Install

**Claude Code** — two commands in any session, and it updates itself from then
on:

```
/plugin marketplace add produckyou-design/agent-director-protocol
/plugin install agent-director@agent-director-protocol
```

Then ask Claude to act as director on something small: *"delegate this instead
of coding it yourself."* You should see a task contract before any file is
touched.

**OpenAI Codex** — for an explicit per-task switch, install the Codex plugin
and invoke `$agent-director`; for persistent project defaults, merge the
director section into `AGENTS.md` and copy the native `.codex/config.toml` and
`.codex/agents/*.toml` templates into your repo. Native subagent threads are
the default; see [`codex/INSTALL.md`](codex/INSTALL.md).

Full options — user-global vs. per-project, manual copy without the plugin,
model profiles, updating, and uninstall — are in the platform-specific
installation guides ([`claude/INSTALL.md`](claude/INSTALL.md) and
[`codex/INSTALL.md`](codex/INSTALL.md)) and the quick install sections below.

## What this gets you

No percentages — here are the specific failure modes the protocol is built to
catch, and the rule that catches each one. If you have not hit these, you
probably do not need this repository.

| Failure mode you've probably seen | What stops it |
|---|---|
| "Done!" — but the code was never wired into the real call path, or the test never ran | Ten mandatory [review gates](core/REVIEW-GATES.md) scored against the actual diff and actual test output; an implementer's `status` field starts a review, it never ends one |
| A stub, hardcoded return, or invented test output presented as a working feature | `placeholder_implementation` / `fake_success` are named, objective [failure reasons](core/FAILURE-LOOP.md) — not judgment calls |
| The agent burns turns retrying the same broken fix on a loop | A third guess-based fix at the same root cause is forbidden; it must [escalate with evidence](core/ESCALATION-PROTOCOL.md) instead |
| Escalation means "throw the biggest model at everything" | A [Rescue Agent](core/RESCUE-PROTOCOL.md) raises **reasoning effort only, never the model** — one task, ≤2 attempts, and only for a genuine reasoning/capability gap. A model change needs the user's say-so; when effort runs out the protocol escalates the *director* (the plan is the likely suspect), not the implementer |
| A model quietly upgrades itself, or spawns workers you never approved | Every promotion and worker plan is disclosed *before* it runs, with a per-subagent `justification`; native capacity is observed at runtime, and implementers cannot spawn subagents at all |
| Two parallel agents clobber the same file | An eight-domain [conflict check](core/CONCURRENCY-RULES.md) before dispatch; a shared file always forces sequencing |
| A failed attempt gets `git checkout .`-ed away, taking the evidence with it | [State safety](core/STATE-SAFETY.md): failed work is preserved until reviewed, and the checkpoint is a real commit SHA |
| Vague work ("fix the UI") gets handed off and comes back as something else | A [task contract](core/TASK-CONTRACT.md) with `current_state`, `target_behavior`, and objective `completion_criteria` is required before delegation |

Two secondary effects, stated as expectations rather than measurements: the
director's context stays on design and review instead of filling up with file
contents and test output — each implementer works from a clean context scoped
to one task — and every decision leaves a written artifact (task contract,
review result, failure loop, takeover record), so you can audit *why*
something was done, not just what changed.

**When it isn't worth it:** a one-file script, a throwaway prototype, or any
task where you'd rather read the diff yourself than read a review of it. The
protocol adds real overhead — contracts, disclosures, evidence — and that
overhead only pays for itself on work that is large enough, or risky enough,
that a silent failure would cost more than the ceremony.

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

A **Rescue Agent** is not a fourth role — it's the implementer role run at a
higher reasoning effort (never a different model) for one already-failed task,
under tighter scope and a hard attempt limit. It is reviewed exactly like any
other implementer output.

**Reviewer** is a role, not necessarily a separate participant: reviewing an
implementer's output is already independent, so the director does it directly.
The exception is work the director wrote itself — a recorded takeover — which
goes to a **separate reviewer agent at the director's own model and effort,
from a fresh context.** The director never reviews its own diff; "hold yourself
to the same standard" is an instruction, not a control.

The "director never writes product code" rule also covers *running*
state-changing operations — deploys, migrations, release pipelines are
delegated like any other work. Full definitions and boundaries:
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
   the implementer's own loop count), that raises **reasoning effort only —
   never the model** (e.g. `medium` → `high` → `xhigh`). A model change is a
   cost decision reserved for the user, reached through step 4; auto-promoting
   to a pricier tier is the reflex this protocol exists to prevent. It works from an isolated last-passing checkpoint with an
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
4. **Only once the effort ladder is exhausted** (or the cause was never a
   reasoning/capability gap) does the director choose: escalate to the user,
   direct intervention (takeover — still gated by a written record, still the
   last resort, never the automatic next step), roll back, reduce scope, or
   convert the task into a read-only investigation. See
   [`core/TAKEOVER-PROTOCOL.md`](core/TAKEOVER-PROTOCOL.md).

   **Escalating after an exhausted effort ladder means raising the *director*,
   not the implementer.** An implementer failing at high effort is evidence
   about the plan rather than the coder — the design, the decomposition, or
   the task contract is the leading suspect. So the request asks the user to
   raise the director's own model and effort; if granted, the upgraded
   director **re-judges the task on its own standard and issues a revised task
   contract** rather than re-delegating the one that kept failing. The revised
   contract is a fresh task with its own loop count. A stronger implementer
   model is something the user may grant here — never an automatic promotion.

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
│  ├─ CLAUDE.md.example          profiles/default.yaml
│  └─ INSTALL.md
├─ codex/                        OpenAI Codex adapter
│  ├─ skills/agent-director/SKILL.md + references/*.md (7 templates)
│  ├─ AGENTS.md.example          profiles/default.yaml
│  ├─ config.toml.example        agents/*.toml.example
│  └─ INSTALL.md
├─ plugins/agent-director/       explicit Codex plugin ($agent-director)
├─ .agents/plugins/              repository marketplace manifest
├─ schemas/                      11 JSON Schema (draft-07) documents
├─ examples/                     4 worked, schema-valid scenarios
│  ├─ python-project/  web-project/  existing-codebase/  new-project/
├─ scripts/                      validation scripts (check_repository.py, ...)
├─ tests/                        unittest suite
└─ .github/workflows/            CI: runs the validation scripts
```

## Quick install — Claude Code

**Recommended — install as a plugin.** This is the only install that updates
itself: Claude Code refreshes marketplaces in the background, and
`/plugin update agent-director@agent-director-protocol` pulls a new release on
demand (use the fully qualified name — the bare one is not found).

```
/plugin marketplace add produckyou-design/agent-director-protocol
/plugin install agent-director@agent-director-protocol
```

The plugin ships `core/` and `schemas/` alongside the skill, so nothing else
needs copying. Full details, shell equivalents, and uninstall:
[`claude/INSTALL.md`](claude/INSTALL.md).

**Or copy the files manually** — vendored into one project, with no update
path (you re-copy on each release). Copy the skill into a project (or your
user-global skills directory), then merge the director-mode snippet from
[`claude/CLAUDE.md.example`](claude/CLAUDE.md.example) into your `CLAUDE.md`.
Commands below are copied from [`claude/INSTALL.md`](claude/INSTALL.md).

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

Copy `core/` and `schemas/`, install the canonical skill under the target's
`.agents/skills/`, and copy the native config/role templates under `.codex/`.
Then merge the director-mode section from
[`codex/AGENTS.md.example`](codex/AGENTS.md.example) into the repo's
`AGENTS.md`. The complete commands are in [`codex/INSTALL.md`](codex/INSTALL.md).

```bash
cp -r agent-director-protocol/core target-repo/core
cp -r agent-director-protocol/schemas target-repo/schemas
mkdir -p target-repo/.agents/skills target-repo/.codex/agents
cp -r agent-director-protocol/codex/skills/agent-director target-repo/.agents/skills/agent-director
cp agent-director-protocol/codex/config.toml.example target-repo/.codex/config.toml
for file in agent-director-protocol/codex/agents/*.toml.example; do
  cp "$file" "target-repo/.codex/agents/$(basename "${file%.example}")"
done
```

```powershell
Copy-Item -Recurse agent-director-protocol\core target-repo\core
Copy-Item -Recurse agent-director-protocol\schemas target-repo\schemas
New-Item -ItemType Directory -Force target-repo\.agents\skills | Out-Null
New-Item -ItemType Directory -Force target-repo\.codex\agents | Out-Null
Copy-Item -Recurse agent-director-protocol\codex\skills\agent-director target-repo\.agents\skills\agent-director
Copy-Item agent-director-protocol\codex\config.toml.example target-repo\.codex\config.toml
Get-ChildItem agent-director-protocol\codex\agents\*.toml.example | ForEach-Object {
  Copy-Item $_.FullName target-repo\.codex\agents\$($_.BaseName)
}
```

Codex's main session is the Director and native subagent threads are the normal
delegation path. `.codex/config.toml` and `.codex/agents/*.toml` are the actual
project-scoped settings; `codex exec` is only the documented fallback for
non-interactive or process-isolated work. `codex/profiles/default.yaml` is
policy metadata, not a profile Codex loads. After explicit `$agent-director`
or "Director mode on" activation, every ADP-created native worker spawn must
explicitly include `model="gpt-5.6-luna"` and
`reasoning_effort="max"`. The Director's selected model is never
inherited, and task kind never selects effort.

The project defaults and role files are defense in depth. Prefer no named
custom agent/type; if one is selected, verify its loaded profile is pinned to
the same pair before dispatch. Verify returned/runtime metadata when exposed:
a mismatch rejects and closes the worker and discards its output; a surface
that cannot accept or verify the pair stops with a policy-violation/fallback
report. Non-Luna/non-max exceptions require explicit user authorization and
disclosure. The normal baseline is already max, so Codex Rescue is unavailable;
preserve evidence and use the Core escalation/takeover gates.

The Codex adapter does not impose a concurrent or cumulative numeric worker
limit. It records native runtime capacity when exposed and records `unknown`
when the surface provides no capacity metadata; a native slot-full response
requires waiting, inspecting evidence, closing completed workers, re-scoping,
or returning to the user. Before every task, every state-changing operation,
and every native-spawn attempt, the Director must visibly disclose
`user_visible: true` plus the `work_contract` objective, scope, planned
contract/worker totals, minimum-safe rationale, exact tests, and stop
conditions. `task_start` begins every task; zero workers are valid only for an
explicit `read_only: true` task. `spawn` and `addition` require positive worker
totals.

Every later worker, contract, revision, rescue, reviewer, or material scope
change requires a new `addition` disclosure with `changed_scope`,
`change_summary`, `added_worker_task`, a classified basis, and
`why_existing_workers_cannot_absorb`. The repository documents and validates
the boundary but cannot hard-intercept the platform-owned native
`multi_agent_v1__spawn_agent` tool.

Initial decomposition must justify why its contract size and total
contract/worker count are the minimum safe structure, based on conflict
boundaries, dependencies, independent evidence/review, or blast-radius
isolation, and why fewer existing contracts cannot absorb it. Mid-task
additions require a new disclosure grounded in newly discovered evidence, a
new conflict/dependency, a mandatory independent-review boundary, or a
classified failure, plus why an existing contract/worker cannot absorb it.

**Explicit Codex plugin switch** — install the repository marketplace plugin
when you want to turn the protocol on for a particular task:

```text
codex plugin marketplace add produckyou-design/agent-director-protocol
codex plugin add agent-director@agent-director-protocol-plugins
```

In a new task/thread, invoke `$agent-director` or say “Director mode on”. The
plugin is an instruction switch: it announces the current session as Director
and uses native subagents, but it cannot change the current session's selected
model, install project files, or retroactively reload an already-running task.
Use [`plugins/agent-director/README.md`](plugins/agent-director/README.md) for
the exact boundary and [`codex/INSTALL.md`](codex/INSTALL.md) for persistent
project installation.

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

Each platform ships policy metadata (`claude/profiles/default.yaml`,
`codex/profiles/default.yaml`) — a **convention read by the skill's own
instructions**, not a native profile automatically loaded by Claude Code or
Codex. Codex's actual project settings are the `[agents]` keys in
`.codex/config.toml` and the standalone files in `.codex/agents/`.

**The profile does not determine who the director is.** The director is
always whichever model is running the current session — switch models
mid-project with `/model` and the director switches with you, live, no file
to touch. What the profile actually holds is operational policy that should
stay stable regardless of which model happens to be in the director seat
today: adapter model/effort rules and how many failed loops on one task trigger
Rescue Protocol classification (`failure_threshold`). Concurrency is
platform-native; the Codex adapter observes runtime capacity and does not add
a project numeric worker limit:

```yaml
# Model names are environment aliases the user may freely change; the protocol never depends on a specific model name.
director:
  preferred_models: [opus-5, fable-5]  # recommended tiers for this role, not a selection you must make
  effort: high        # optional hint; adapters map to platform mechanism or omit
implementer:
  preferred_models: [opus-5]   # one tier — nothing in the protocol picks between entries
  effort_by_task_kind:
    investigation: high   # root-cause hunts, competing hypotheses, design judgement
    audit: high            # pre-release compliance / security review
    implementation: medium
    pipeline: medium       # release/deploy execution — procedure fidelity, not creativity
    mechanical: low        # version bumps, doc sync, single-line edits
  effort_default: medium
  failure_threshold: 2   # counted failed loops before Rescue Protocol classification
reviewer:
  inherit: director   # default: reviewer == director
```

Model names are environment aliases — swap them for whatever your platform
resolves them to. `core/` never mentions a model name; adapter policy metadata
and native configuration are where model settings belong.

**Choosing an implementer tier: measure cost per completed task, not per
token.** A model with a lower per-token price that needs more steps, more
retries, and more supervision to finish the same work can cost more in total —
and the per-token gap is often narrower than the sticker suggests once an
introductory rate expires. The same logic runs the other way on reasoning
effort: spending more up front sometimes *lowers* total cost by cutting the
number of turns, while a capable model at a modest effort tier is frequently
the efficient point. Effort defaults carried over from an older model rarely
transfer unchanged. This repository states no benchmark numbers because the
right answer depends on your workload and on prices that change — sweep tiers
and effort levels on your own tasks and compare the cost to *done*.

**Only override the profile if a project wants different policy** — for
example, a project may change its adapter-specific failure threshold. Do not
add a project concurrency cap to the Codex adapter: native runtime capacity is
the only capacity authority. To override other policy, copy the policy file and
edit your copy, or follow the platform-specific `INSTALL.md` instructions.

### Codex explicit dispatch and verification

The Codex-specific adapter is stricter than the platform-neutral profile
example above: explicit Director-mode activation fixes every ADP native worker
spawn to `model="gpt-5.6-luna"` and
`reasoning_effort="max"`. The Director remains user-selected.
Defaults and named profiles are only defense in depth. Omit a named custom
agent/type unless its loaded profile is verified against the pair. If returned
metadata is mismatched, reject/close the worker and discard its output; if the
surface cannot accept or verify the pair, stop and report a fallback
requirement. A non-Luna/non-max exception needs explicit user authorization and
disclosure. Rescue has no headroom at max, so use the Core escalation/takeover
gates.

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

1. **A distinct conflict boundary or dependency** that an existing
   contract/worker cannot safely absorb.
2. **Isolating blast radius** — a risky change should be reviewable
   independently of a safe one.
3. **Genuinely independent verifiable outcomes** that would otherwise force
   unrelated work into a single contract, making it harder to review or
   revert in isolation.
4. **An independent reviewer context** that cannot be supplied by the
   implementer without self-review.

"Smaller diffs" or "tidier task IDs" alone is never sufficient. The Codex
adapter has no ADP batch or cumulative numeric cap: the native runtime is the
only capacity authority. If the runtime reports full capacity, wait/close,
re-scope, or return; user rationale cannot override the native refusal and
capacity saturation never authorizes takeover. See
[`core/DELEGATION-PROTOCOL.md`](core/DELEGATION-PROTOCOL.md).

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
- **Spawning without explicit worker settings or accepting unverified metadata.**
  Every ADP native spawn must carry `model="gpt-5.6-luna"` and
  `reasoning_effort="max"`. A mismatch is rejected/closed and an
  unverifiable surface stops with a fallback report.
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
  must fit the observed native runtime capacity — passing the conflict-domain
  check makes a batch *safe* to execute, not *sized appropriately*. See
  `core/DELEGATION-PROTOCOL.md` and `core/CONCURRENCY-RULES.md`.
- **Using generic contract-scale or addition reasons.** Speed, parallelism,
  efficiency, task size/complexity, many files, context reduction, empty slots,
  and tidy/smaller task IDs do not justify another contract or worker. Initial
  decomposition must explain the minimum structure and why fewer contracts
  cannot absorb it; every mid-task addition needs a new evidence-based
  disclosure and the same absorption explanation.
- **An implementer spawning its own subagents.** Only the director delegates.
  An implementer that decides mid-task it needs more help reports that as a
  blocked/out-of-scope finding — it does not act on it. See
  `core/ROLE-CONTRACT.md`.

## Limitations

- **Platform mechanics differ, and this repo does not force parity between
  them.** Claude Code has native subagents (the Task/Agent tool); Codex has no
  equivalent persistent subagent identity — its implementer role here is a
  explicit native subagent spawn with a per-request model/effort pair (or a
  documented `codex exec` fallback) per task. The two adapters describe the same
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
