# Delegation Protocol

This document defines how the director turns work into delegated, verifiable tasks.

## The delegation sequence

The director MUST follow this sequence for any nontrivial change:

1. **Analyze the repository.** Read the relevant code, its structure, its existing conventions, and
   its tests before forming an opinion about the solution.
2. **Interpret the requirement.** Convert the user's request — which may be vague — into a concrete
   statement of current behavior and target behavior.
3. **Design.** Decide the overall shape of the solution: what changes, in what order, and why.
   Design happens before decomposition; tasks are not invented ad hoc as work proceeds.
4. **Decompose into tasks.** Split the design into units of work, each of which is either a
   verifiable user flow (something a user or caller can observe working end to end) or an
   independent technical outcome (something checkable in isolation, such as "this module compiles
   and its unit tests pass"). A task that cannot be phrased as one of these two things is not yet
   ready for delegation — return to design.
5. **Order by dependency.** Determine which tasks require another task's output first, and which are
   independent. Independent tasks are candidates for parallel dispatch; see [CONCURRENCY-RULES.md](CONCURRENCY-RULES.md).
6. **Write a task contract per task.** Every delegated unit of work gets its own task contract,
   matching every required field of the schema. See [TASK-CONTRACT.md](TASK-CONTRACT.md) and `../schemas/task-contract.schema.json`.
7. **Disclose the agent composition, then assign.** Before spawning any implementer, tell the user
   what is about to run, matching [`../schemas/agent-composition-disclosure.schema.json`](../schemas/agent-composition-disclosure.schema.json)
   field for field: `director_model`, `director_effort`, `subagent_count`, `subagents` (each one's
   role, task, model, and effort), `parallel`, and `rescue_agent_available`. This happens once, for
   the whole batch of tasks about to be dispatched, not per individual spawn. Only then does the
   director hand each task contract to an implementer. Do not assign a task before its `depends_on`
   tasks have been reviewed and approved. (Mid-task promotions — [Rescue Agent](RESCUE-PROTOCOL.md) promotion or
   a granted [escalation](ESCALATION-PROTOCOL.md) — get their own notice when they happen; see RESCUE-PROTOCOL.md.
   They are not folded into this upfront disclosure.)
8. **Review.** Every implementation report is reviewed against evidence before being accepted. See
   [REVIEW-GATES.md](REVIEW-GATES.md).

Skipping a step (for example, decomposing directly from a vague request without an explicit design
step) is a protocol violation even if the resulting tasks look reasonable.

## Vague scopes must never be delegated as-is

Requests such as "improve the feature," "fix the UI," or "resolve the bug" are not task contracts
and MUST NOT be handed to an implementer in that form. A vague request lacks `current_state`,
`target_behavior`, and `completion_criteria` that an implementer or reviewer could check
objectively. Delegating it as-is pushes the interpretation problem onto the implementer, who is not
positioned to make repository-wide judgment calls.

The director MUST convert the vague request into one or more concrete task contracts before
delegating. Converting a vague request means:

- Reproducing or locating the actual problem (not assuming what "the bug" is).
- Stating the current, observed behavior precisely.
- Stating the target behavior precisely enough that a third party could verify it without asking the
  requester follow-up questions.
- Identifying which files are in scope and which are explicitly out of scope.
- Writing completion criteria that are objective — checkable by running something, not by taste.

### Worked example

Vague request: *"Fix the UI — the login form looks broken."*

This is not delegable. The director first reproduces the issue, finds that the password field does
not mask input on the mobile layout, and converts it into a concrete task contract:

```json
{
  "task_id": "T-014",
  "title": "Mask password input on mobile login form",
  "objective": "Users on mobile viewports can currently read the password as plain text while typing, which is a security and UX defect on the login screen.",
  "current_state": "On viewport widths below 480px, the password <input> renders with type=\"text\" due to a CSS override in mobile.css that unintentionally strips the input type behavior.",
  "target_behavior": "On all viewport widths, the password field renders as a masked input (type=\"password\") with the existing show/hide toggle still functional.",
  "must_read_files": ["src/components/LoginForm.jsx", "src/styles/mobile.css"],
  "editable_files": ["src/components/LoginForm.jsx", "src/styles/mobile.css"],
  "forbidden_files": ["src/components/LoginForm.test.jsx"],
  "interfaces_to_preserve": ["LoginForm onSubmit(props) contract"],
  "input_format": "n/a",
  "output_format": "n/a",
  "error_handling": ["Toggle button still works when field is masked"],
  "preservation_conditions": ["Desktop login form behavior unchanged"],
  "completion_criteria": ["Password input has type=password at all viewport widths", "Show/hide toggle still switches type correctly"],
  "test_commands": ["npm test -- LoginForm"],
  "manual_verification": ["Load login page at 375px width and confirm password is masked while typing"],
  "report_format": "implementation-report.schema.json"
}
```

This is delegable: an implementer can read it, act on it, and a reviewer can check it against
evidence, without ever having to guess what "broken" meant.
