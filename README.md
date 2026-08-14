# agent-director-protocol (ADP)

*[한국어](README.ko.md)*

**Stop taking "Done!" at face value from an agent that graded its own homework.**

ADP turns one Claude Code session into a **Director** that plans, delegates,
and verifies against the actual diff and actual test output before anything
counts as finished. Implementation goes to workers working from written,
checkable contracts. A stuck worker escalates with evidence instead of
guessing a third time, and every promotion or addition is disclosed.

This distribution supports **Claude Code only**. ADP is a protocol, not a
runtime: it is Markdown rules, JSON Schemas, templates, and a thin Claude Code
adapter. There is no daemon or dependency to install into the target project.

## Install

The recommended install is the Claude Code plugin:

```
/plugin marketplace add produckyou-design/agent-director-protocol
/plugin install agent-director@agent-director-protocol
```

Then ask Claude to act as director on a small feature, for example:
“delegate this instead of coding it yourself.” You should see a composition
notice and task contract before any file is touched.

Full install, update, manual-copy, and uninstall instructions are in
[`claude/INSTALL.md`](claude/INSTALL.md).

## What this gets you

| Failure mode | What stops it |
|---|---|
| “Done!” without a real integration or test | Ten mandatory [review gates](core/REVIEW-GATES.md) checked against the actual diff and test output |
| A stub or invented success presented as working | Objective [failure reasons](core/FAILURE-LOOP.md) such as `placeholder_implementation` and `fake_success` |
| Repeating the same broken fix | A third guess-based attempt at the same root cause is forbidden; the task escalates with evidence |
| Silent model promotion or worker additions | Composition, promotion, and addition disclosures are required before they happen |
| Parallel workers clobbering shared files | [Conflict-domain checks](core/CONCURRENCY-RULES.md) force sequencing for shared state |
| Failed work disappearing | [State safety](core/STATE-SAFETY.md) preserves the evidence and requires a real checkpoint |
| Vague work being delegated vaguely | [Task contracts](core/TASK-CONTRACT.md) define current state, target behavior, scope, and completion criteria |

## Roles

| Role | Writes product code | Declares overall completion |
|---|---:|---:|
| Director | Only under a recorded, user-authorized takeover | Yes |
| Implementer | Yes, within the contract scope | No; it reports evidence |
| Reviewer | No | No; it advises the Director |

There is exactly one Director: the root/current parent Claude Code session.
Every spawned worker receives a non-Director role before creation. A worker
must not announce `director_mode: on`, publish root-level disclosures,
re-decompose the parent contract, spawn or manage workers, integrate work, or
declare the overall task complete.

Every worker contract includes:

- `goal`
- scope and non-goals
- `success_criteria`
- `failure_criteria`
- `termination_criteria`
- `required_evidence`

Missing or ambiguous role/criteria is a pre-spawn failure.

## How it works

```
analyze → design → disclose composition → write contract → delegate
   → implement and test → inspect diff and evidence → review → integrate
```

The core rules define each boundary:

- [Role contract](core/ROLE-CONTRACT.md)
- [Delegation protocol](core/DELEGATION-PROTOCOL.md)
- [Task contract](core/TASK-CONTRACT.md)
- [Concurrency rules](core/CONCURRENCY-RULES.md)
- [Review gates](core/REVIEW-GATES.md)
- [Failure loop](core/FAILURE-LOOP.md)
- [Escalation protocol](core/ESCALATION-PROTOCOL.md)
- [Rescue protocol](core/RESCUE-PROTOCOL.md)
- [Takeover protocol](core/TAKEOVER-PROTOCOL.md)
- [Completion standard](core/COMPLETION-STANDARD.md)
- [State safety](core/STATE-SAFETY.md)

## Worker recovery and cleanup

A native `RUNNING` worker is preserved by default. A wait timeout is an
observation only: no final result arrived during that wait. Timeout alone is
never completion, interrupt, close, splitting, or re-dispatch evidence.

On the first timeout, record the observation and perform another
task-appropriate bounded wait by default, unless explicit fatal runtime
evidence already exists: a crash, repeated tool error, explicit failure,
runtime disconnect, or a demonstrably repeated identical command.

File state is not lifecycle evidence. In read-only tasks, file changes or
their absence are never stall evidence. In write tasks, absence of file
changes alone never proves a stall. A read-only architecture/design final
report is a completed-work artifact only when it contains concrete scope,
evidence, findings, tests or inspection commands, and unresolved risks.

If progress telemetry is unavailable, classify the worker as `unknown`, not
`stalled`. Only explicit fatal evidence or a declared bounded no-progress
window permits one bounded interrupt. The interrupt tells the worker to stop,
summarize only evidence already secured, start no new work, tests, or edits,
and exit. A queued request to return progress is not an interrupt.

Terminal-result cleanup is separate from stalled recovery. The Director first
captures and persists the authoritative report/evidence, then reconciles the
worker lifecycle through one atomic cleanup claim. Before the root session
finishes, every lifecycle it created must be reconciled; it must not silently
finish while owned children remain unreconciled.

Closing or resuming a worker does not merge its fork into the main working
tree. The Director must inspect the fork diff or report and explicitly
integrate it after review.

## Quick start

1. Install the Claude Code plugin or copy the Claude adapter manually.
2. Pick a feature with at least two meaningful moving parts.
3. Ask Claude to “act as director for this feature.”
4. Confirm that it publishes the composition notice, task contract, worker
   report, independent review, and completion evidence in that order.

If the Director edits product code without a contract and takeover record, or
silently adds/promotes a worker, the protocol is not being followed.

## Configuration and profiles

The Claude profile at [`claude/profiles/default.yaml`](claude/profiles/default.yaml)
is policy metadata read by the skill. It does not select the Director model or
provide hard runtime enforcement. The Director is the model running the root
Claude Code session; the adapter records the intended policy and native
capabilities honestly.

The protocol does not impose a project-wide numeric worker cap. The native
runtime is the capacity authority. If capacity is unknown, use one sequential
worker and record `capacity_source: "unknown"`. Parallel work requires
independent verifiable groups, disjoint conflict domains, no dependency edges,
isolated writes, and observed capacity. Parallel dispatch requires two or more
independently verifiable groups. The work contract records
`independent_groups`, `conflict_domains`, `dependency_edges`, `planned_workers`,
`capacity_source`, `write_isolation`, and `why_fewer_workers_cannot_absorb`.
With observed capacity, `planned_workers = min(independent-group count,
observed capacity)`; with unknown capacity, use one worker. Speed or efficiency
alone is never a reason to add a worker.

## Applying ADP to a project

For a project install, copy the Claude skill and the platform-neutral files:

```powershell
New-Item -ItemType Directory -Force -Path "<project>\.claude\skills" | Out-Null
Copy-Item -Recurse "claude\skills\agent-director" "<project>\.claude\skills\agent-director"
Copy-Item -Recurse "core" "<project>\core"
Copy-Item -Recurse "schemas" "<project>\schemas"
```

Then merge [`claude/CLAUDE.md.example`](claude/CLAUDE.md.example) into the
project's `CLAUDE.md` if persistent project guidance is wanted.

## Examples

| Example | Demonstrates |
|---|---|
| [`examples/python-project/`](examples/python-project/) | A simple greenfield task approved on the first loop |
| [`examples/web-project/`](examples/web-project/) | An additive feature with one evidence-based revision |
| [`examples/existing-codebase/`](examples/existing-codebase/) | A bug fix that reaches takeover after recorded failures |
| [`examples/new-project/`](examples/new-project/) | Independent work groups and a conflict-domain check |

## Limitations

- The Claude adapter is instructions and templates, not a hard enforcement
  runtime. A model that ignores `SKILL.md` or `CLAUDE.md` is not mechanically
  stopped by this repository.
- Profiles are conventions. Native Claude Code behavior and capacity remain
  authoritative where they differ from a document.
- A worker's self-reported `complete` status starts review; it never ends it.

## Security notes

Do not put secrets, credentials, or tokens in task contracts, reports,
escalation records, or takeover records. Review every `test_commands` and
`manual_verification` instruction before execution. Scrub secrets from any
captured command output.

## Validation

Run the full repository check before relying on a change:

```
python scripts/check_repository.py
```

This validates schemas, examples, the Claude skill tree, links, templates,
and sensitive-data rules. CI runs the same check on every push and pull
request.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the schema-first workflow,
release process, and local validation commands.

## License

[MIT](LICENSE).

## Korean translation

[`README.ko.md`](README.ko.md) is the Korean translation of this document.
