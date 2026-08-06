# State Safety

This document defines how working state is protected across delegation: who commits, when, what
happens to an implementer's uncommitted work, and which operations are never performed without an
explicit, recorded decision.

Every other document in this protocol assumes a recoverable working state. [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) hands a
Rescue Agent a "last-passing checkpoint"; [FAILURE-LOOP.md](FAILURE-LOOP.md) assumes a failed loop can be examined and
retried; [TAKEOVER-PROTOCOL.md](TAKEOVER-PROTOCOL.md) assumes the director can inspect what two failed attempts actually
changed. None of that holds if failed work is silently discarded or if two agents overwrite each
other's history. This document states those assumptions as rules.

The rules below are written in Git terms because that is the common case. A project using a different
version-control system applies the same obligations to its equivalent operations; a project with no
version control at all cannot satisfy this document, and the director MUST say so plainly rather than
pretending the protections exist.

## Checkpoint before delegating

Before dispatching any implementer, the director MUST establish a **last-passing checkpoint**: a
committed, identifiable state (commit SHA, tag, or branch tip) where the project's tests were last
observed to pass, or where it was last known to build and run if there are no tests.

- The checkpoint is recorded as an identifier, not a description. "The state before we started" is
  not a checkpoint; `a1b2c3d` is.
- If the working tree is dirty when a task is about to be delegated, the director resolves that
  first — commit it, stash it, or explicitly record that the uncommitted changes are part of the
  starting state. Delegating on top of unexplained uncommitted work makes every later diff
  ambiguous, and the ambiguity surfaces exactly when something has already gone wrong.
- The checkpoint identifier is what a Rescue Agent receives as `last_passing_checkpoint`
  ([`../schemas/rescue-agent-task.schema.json`](../schemas/rescue-agent-task.schema.json)) and what option **B** ("roll back") in
  [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) Step 3 rolls back to.

## Failed work is preserved, not discarded

**A failed attempt's changes MUST NOT be destroyed before the director has reviewed them.** The
diff of a failed attempt is primary evidence: [REVIEW-GATES.md](REVIEW-GATES.md) requires the director to read the actual
diff rather than the implementer's summary, [FAILURE-LOOP.md](FAILURE-LOOP.md) requires evidence-based revision
instructions, and [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) hands both prior attempts to a Rescue Agent as reference
material. Destroying the work destroys the evidence that the next step depends on.

Specifically, after a failed attempt and before the director's review, no one runs `git checkout .`,
`git restore .`, `git reset --hard`, `git clean -fd`, or any equivalent that discards uncommitted
work. Preserve it first — a commit on a scratch branch, a stash with a named message, or a patch
file — and only then return the working tree to the checkpoint.

Once the director has reviewed a failed attempt and recorded its evidence (in a
[failure-loop record](../schemas/failure-loop.schema.json), review result, or Rescue Agent package),
the preserved copy may be discarded.

## Who commits, and when

- **Implementers do not commit to the main line.** An implementer works in its assigned scope and
  reports; it does not merge, rebase onto, or push the branch that other tasks and the director are
  reading. Platforms where a subagent shares the director's working tree make this a hard rule, not
  a preference: an implementer committing mid-task rewrites the state the director is about to
  review.
- **Integration is the director's step**, per [ROLE-CONTRACT.md](ROLE-CONTRACT.md). Work becomes part of the main line
  only after the review gates pass. This is the same rule [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) states for Rescue Agent
  output ("no failed change is merged automatically"), generalized to every implementation.
- **An implementer MAY commit within its own isolated working copy** — a worktree or branch created
  for that task alone — where doing so does not affect anyone else's view. This is encouraged for
  parallel work; see [CONCURRENCY-RULES.md](CONCURRENCY-RULES.md).

## Destructive operations require an explicit decision

The following are never performed as an incidental step inside another task. Each requires the
director to decide it deliberately, state what will be lost, and — where the loss extends beyond
this project's own working state — obtain the user's approval first:

- Force-pushing, or any history rewrite of a branch others may have (`rebase`, `commit --amend`,
  `filter-branch`) once it has been pushed.
- Deleting a branch, tag, worktree, or stash that holds the only copy of some work.
- `git reset --hard`, `git clean`, or equivalent, on a tree with uncommitted work — see the
  preservation rule above.
- Any operation that discards the last-passing checkpoint itself.

A rollback under [RESCUE-PROTOCOL.md](RESCUE-PROTOCOL.md) Step 3 option **B** is a deliberate decision of exactly this kind:
it is announced, not performed silently, and it states which attempts are being abandoned.

## Isolation for parallel work

When two or more implementers run concurrently, each MUST work in an isolated copy (a worktree,
branch, or equivalent) rather than sharing one working tree — even after the conflict-domain check in
[CONCURRENCY-RULES.md](CONCURRENCY-RULES.md) has passed. The conflict check establishes that their *intended* changes do not
overlap; it does not prevent an unrelated stray write, a build artifact, or a tool run from one agent
appearing in another's diff. Where the platform provides no isolation mechanism, run the tasks
sequentially instead.

## Reporting state accurately

An implementation report describes what the implementer actually changed on disk. Claiming a file was
modified when it was not, or omitting an incidental change (a reformatted file, a regenerated lockfile,
a stray artifact), is a reporting failure under [FAILURE-LOOP.md](FAILURE-LOOP.md) — `fake_success` when the claim is
invented, `no_out_of_scope_changes` (a [REVIEW-GATES.md](REVIEW-GATES.md) check) when the omission hides scope creep. The
director verifies `files_changed` against the real diff, not against the summary.
