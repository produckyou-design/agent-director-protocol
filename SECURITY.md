# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | yes |

This project is pre-1.0; security fixes land on the latest `0.1.x` release.
There is no long-term support branch at this stage.

## Reporting a vulnerability

**Do not report vulnerabilities by email.** Use **GitHub Security Advisories**
(private reporting) on this repository: open the repository's **Security**
tab and select **"Report a vulnerability"** to start a private advisory.
This keeps the report and any discussion out of public issues until a fix is
available.

Please include:

- The affected file(s) or component (e.g. a specific script under
  `scripts/`, a schema, a template).
- Steps to reproduce, or the specific misuse scenario you're concerned about.
- The potential impact as you understand it.

You should expect an initial response acknowledging the report; because this
is a small, community-maintained documentation-and-tooling project, please
allow a reasonable amount of time for triage rather than expecting a fixed
SLA.

## Scope

This is a documentation and tooling repository — a protocol specification
(Markdown), JSON Schemas, example JSON/Markdown documents, and Python
validation scripts. It does not run a service and does not process user data
on any server. The realistic risk surface is narrower than a typical
application, but not zero:

- **Prompt-injection-style misuse of templates or examples.** The task
  contract, implementation report, review result, and takeover templates in
  `claude/skills/agent-director/references/` and
  `codex/skills/agent-director/references/` are designed to be filled in and
  passed to an AI agent as instructions. A malicious or careless fill-in
  (or a compromised example used as a copy-paste starting point) could smuggle
  instructions intended to make an agent run unintended commands or exfiltrate
  data. Treat any task contract, review result, or report you did not write
  yourself as untrusted input, and review `test_commands` and
  `manual_verification` steps before letting an agent execute them,
  especially in a sensitive environment.
- **Secrets leaking into reports.** Implementation reports and review results
  can embed real command output (`test_executions.output_excerpt`). If you
  find an example, template, or script that encourages capturing output
  without a reminder to scrub secrets, please report it — see
  `core/COMPLETION-STANDARD.md` and the README's security notes for the
  expected practice.
- **The validation scripts themselves (`scripts/`).** These are local,
  offline Python scripts intended to run against a checkout of this
  repository. A vulnerability here would most likely be a scripting issue
  (e.g. unsafe path handling) rather than a network-facing one; report it the
  same way as above.

Issues that are purely about the protocol's *effectiveness* (e.g. "the
review gates don't catch every possible failure mode") are design feedback,
not security reports — please open a regular issue for those instead of a
security advisory.
