"""Structural tests: required directory layout and SKILL.md frontmatter.

Runnable via `python -m unittest discover -s tests` from the repo root. The
repo root is located relative to this file so the suite works regardless of
the caller's current working directory.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate_skills  # noqa: E402


def bounded_block(source: str, start_marker: str, end_marker: str) -> str:
    """Return a policy block bounded by two explicit markers."""
    start = source.index(start_marker)
    end = source.index(end_marker, start + len(start_marker))
    return source[start:end]

CORE_REQUIRED_FILES = {
    "ROLE-CONTRACT.md",
    "DELEGATION-PROTOCOL.md",
    "TASK-CONTRACT.md",
    "FAILURE-LOOP.md",
    "REVIEW-GATES.md",
    "CONCURRENCY-RULES.md",
    "ESCALATION-PROTOCOL.md",
    "RESCUE-PROTOCOL.md",
    "TAKEOVER-PROTOCOL.md",
    "COMPLETION-STANDARD.md",
    "STATE-SAFETY.md",
}

SCHEMA_REQUIRED_FILES = {
    "task-contract.schema.json",
    "implementation-report.schema.json",
    "review-result.schema.json",
    "failure-loop.schema.json",
    "takeover-record.schema.json",
    "escalation-request.schema.json",
    "director-escalation-request.schema.json",
    "rescue-agent-task.schema.json",
    "agent-composition-disclosure.schema.json",
    "promotion-notice.schema.json",
    "rescue-outcome-notice.schema.json",
}

EXAMPLE_REQUIRED_DIRS = {
    "new-project",
    "existing-codebase",
    "python-project",
    "web-project",
}


class TestDirectoryLayout(unittest.TestCase):
    def test_core_has_expected_docs(self):
        core_dir = REPO_ROOT / "core"
        self.assertTrue(core_dir.is_dir(), f"missing {core_dir}")
        actual = {p.name for p in core_dir.glob("*.md")}
        self.assertEqual(actual, CORE_REQUIRED_FILES)

    def test_schemas_has_eleven_files(self):
        schemas_dir = REPO_ROOT / "schemas"
        self.assertTrue(schemas_dir.is_dir(), f"missing {schemas_dir}")
        actual = {p.name for p in schemas_dir.glob("*.schema.json")}
        self.assertEqual(actual, SCHEMA_REQUIRED_FILES)

    def test_claude_skill_tree_exists(self):
        for platform in ("claude",):
            skill_md = REPO_ROOT / platform / "skills" / "agent-director" / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"missing {skill_md}")
            references_dir = REPO_ROOT / platform / "skills" / "agent-director" / "references"
            self.assertTrue(references_dir.is_dir(), f"missing {references_dir}")

    def test_four_example_dirs_exist(self):
        examples_dir = REPO_ROOT / "examples"
        self.assertTrue(examples_dir.is_dir(), f"missing {examples_dir}")
        actual = {p.name for p in examples_dir.iterdir() if p.is_dir()}
        self.assertEqual(actual, EXAMPLE_REQUIRED_DIRS)


class TestSkillFrontmatter(unittest.TestCase):
    def test_validate_skills_reports_no_failures(self):
        failures = validate_skills.run(REPO_ROOT)
        self.assertEqual(failures, [], f"validate_skills.run() reported failures: {failures}")

    def test_frontmatter_name_and_description(self):
        for platform in ("claude",):
            skill_md = REPO_ROOT / platform / "skills" / "agent-director" / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            fields, errors = validate_skills.parse_frontmatter(text)
            with self.subTest(platform=platform):
                self.assertEqual(errors, [])
                self.assertEqual(fields.get("name"), "agent-director")
                description = fields.get("description")
                self.assertTrue(description, "description must be non-empty")
                self.assertNotIn("\n", description, "description must be single-line")

    def test_references_directory_contains_exactly_seven_templates(self):
        for platform in ("claude",):
            references_dir = REPO_ROOT / platform / "skills" / "agent-director" / "references"
            actual = {p.name for p in references_dir.iterdir() if p.is_file()}
            with self.subTest(platform=platform):
                self.assertEqual(actual, validate_skills.REQUIRED_REFERENCE_FILES)

    def test_install_and_profiles_exist(self):
        for platform in ("claude",):
            install_md = REPO_ROOT / platform / "INSTALL.md"
            profiles_dir = REPO_ROOT / platform / "profiles"
            with self.subTest(platform=platform):
                self.assertTrue(install_md.is_file(), f"missing {install_md}")
                self.assertTrue(profiles_dir.is_dir(), f"missing {profiles_dir}")
                self.assertTrue(
                    list(profiles_dir.glob("*.yaml")),
                    f"{profiles_dir} must contain at least one *.yaml profile",
                )


class TestPluginManifests(unittest.TestCase):
    """Guards for the Claude Code plugin/marketplace manifests.

    The version guard matters operationally: Claude Code only delivers a plugin
    update to installed users when `version` in plugin.json changes. Pushing
    commits without bumping it is silently a no-op for everyone who installed
    the plugin, so a stale version here means shipping nothing.
    """

    def _load(self, name: str) -> dict:
        path = REPO_ROOT / ".claude-plugin" / name
        self.assertTrue(path.is_file(), f"missing {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_plugin_manifest_shape(self):
        plugin = self._load("plugin.json")
        self.assertEqual(plugin["name"], "agent-director")
        # `skills` must point at a real directory containing the skill.
        skills_rel = plugin["skills"].lstrip("./")
        skill_md = REPO_ROOT / skills_rel / "agent-director" / "SKILL.md"
        self.assertTrue(skill_md.is_file(), f"plugin `skills` path does not reach {skill_md}")

    def test_marketplace_manifest_shape(self):
        market = self._load("marketplace.json")
        self.assertIn("name", market)
        self.assertIn("name", market["owner"])
        entries = market["plugins"]
        self.assertTrue(entries, "marketplace.json lists no plugins")
        names = {e["name"] for e in entries}
        self.assertIn(self._load("plugin.json")["name"], names)

    def test_plugin_version_matches_latest_changelog_release(self):
        plugin_version = self._load("plugin.json")["version"]
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        released = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.M)
        self.assertTrue(released, "no released versions found in CHANGELOG.md")
        self.assertEqual(
            plugin_version,
            released[0],
            "plugin.json version must match the newest released CHANGELOG version — "
            "otherwise installed users receive no update for this release",
        )


class TestProtocolPolicy(unittest.TestCase):
    def test_worker_recovery_policy_preserves_progress_and_bounds_recovery(self):
        policy_files = [
            REPO_ROOT / "core" / "CONCURRENCY-RULES.md",
            REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md",
        ]
        required_patterns = [
            r"A native `RUNNING` worker is preserved by default",
            r"file changes or their absence are never stall evidence",
            r"absence of file changes alone never proves a stall",
            r"read-only architecture/design.*concrete scope.*evidence.*findings.*tests or inspection commands.*unresolved risks",
            r"first timeout.*another.*bounded wait",
            r"explicit fatal runtime evidence",
            r"crash.*repeated tool error.*explicit failure.*runtime disconnect.*repeated identical command",
            r"During the longer wait.*native status.*recent tool output.*active-command signals",
            r"no progress telemetry.*unknown.*not.*stalled",
            r"An interrupt is permitted only after",
            r"does not require an error message",
            r"Stop the\s+current work.*evidence already secured.*do not start new work,\s+tests,\s+or edits",
            r"queued request to\s+return progress is not an interrupt",
            r"For the non-final stalled recovery path, close is allowed only after.*stalled.*one interrupt.*one bounded wait",
            r"Preserve\s+`completed_work_unreported`\s+and\s+`unknown`",
        ]
        for path in policy_files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(policy_file=path.relative_to(REPO_ROOT)):
                for pattern in required_patterns:
                    self.assertRegex(source, re.compile(pattern, re.I | re.S), pattern)

    def test_terminal_cleanup_and_root_finalization_are_explicit(self):
        core_path = REPO_ROOT / "core" / "CONCURRENCY-RULES.md"
        core_source = core_path.read_text(encoding="utf-8")
        core_block = bounded_block(
            core_source,
            "### Successful terminal cleanup and root finalization",
            "On user interruption",
        )
        self.assertIn("An authoritative\nnative terminal result", core_block)
        self.assertIn("takes precedence over inferred", core_block)
        self.assertIn("one reconciliation record keyed by worker identity and\nlifecycle cycle", core_block)
        self.assertIn("`unclaimed`, `in_flight`, `succeeded`, `failed`, or `unknown`", core_block)
        self.assertIn("Every native cleanup invocation, initial or retry, requires a successful atomic", core_block)
        self.assertIn("only the claimant may invoke cleanup", core_block)
        self.assertIn("prior invocation is proven not accepted", core_block)
        self.assertRegex(core_block, re.compile(r"rather than\s+blindly invoking cleanup again"))
        self.assertRegex(core_block, re.compile(r"Resuming a closed\s+worker starts a new lifecycle\s+cycle"))
        self.assertIn("reconcile every lifecycle cycle it created", core_block)
        self.assertIn("Atomically claim and\ninvoke an `unclaimed` cycle", core_block)
        self.assertNotRegex(core_source, re.compile(r"\b(?:close_agent|resume_agent)\b"))

        claude_source = (REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("Close is allowed only after", claude_source)
        self.assertNotRegex(claude_source, re.compile(r"\b(?:close_agent|resume_agent)\b"))
        self.assertIn("An authoritative native terminal result", claude_source)
        self.assertIn("one reconciliation record per worker identity and lifecycle cycle", claude_source)
        self.assertIn("`unclaimed`, `in_flight`, `succeeded`, `failed`, or `unknown`", claude_source)
        self.assertIn("prior invocation was not accepted", claude_source)
        self.assertIn("Initial cleanup atomically claims `unclaimed`", claude_source)
        self.assertIn("atomically claim and invoke `unclaimed`", claude_source)
        self.assertIn("reconcile every lifecycle cycle it created", claude_source)

        for path in (REPO_ROOT / "core").glob("*.md"):
            with self.subTest(platform_neutral_file=path.relative_to(REPO_ROOT)):
                self.assertNotRegex(path.read_text(encoding="utf-8"), re.compile(r"\b(?:close_agent|resume_agent)\b"))

    def test_completion_standard_requires_root_worker_reconciliation(self):
        source = (REPO_ROOT / "core" / "COMPLETION-STANDARD.md").read_text(encoding="utf-8")
        block = bounded_block(source, "## Root finalization and worker reconciliation", "## Relationship to the failure loop")
        self.assertIn("MUST\nreconcile every lifecycle cycle it created", block)
        self.assertIn("takes\nprecedence over inferred non-final classifications", block)
        self.assertIn("captures and persists all available report/evidence", block)
        self.assertIn("atomic cleanup-claim state machine", block)
        self.assertIn("At most one native cleanup may\nbe accepted per lifecycle cycle", block)
        self.assertIn("reconciliation record", block)
        self.assertIn("atomically claims and invokes `unclaimed`", block)
        self.assertRegex(block, re.compile(r"does not treat a mere\s+claim as success"))
        self.assertIn("prior invocation is proven not accepted", block)
        self.assertIn("atomically consumes the retry and claims `in_flight`", block)
        self.assertRegex(block, re.compile(r"without a blind duplicate\s+invocation"))
        self.assertRegex(block, re.compile(r"resumed into a new lifecycle receives a new\s+reconciliation\s+cycle"))
        self.assertIn("Only when no authoritative terminal native result exists", block)
        self.assertNotRegex(block, re.compile(r"\b(?:close_agent|resume_agent)\b"))

    def test_cleanup_transition_table_serializes_initial_and_retry_claims(self):
        source = (REPO_ROOT / "core" / "CONCURRENCY-RULES.md").read_text(encoding="utf-8")
        table = bounded_block(
            source,
            "<!-- worker-cleanup-transition-table:start -->",
            "<!-- worker-cleanup-transition-table:end -->",
        )
        rows = []
        for line in table.splitlines():
            if not line.startswith("| `"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            rows.append(tuple(cells))

        self.assertIn(
            (
                "`unclaimed`",
                "terminal evidence captured; atomically claim attempt 1",
                "`in_flight`",
                "claimant invokes once",
            ),
            rows,
        )
        retry_row = next(row for row in rows if row[0] == "`failed` or `unknown`")
        self.assertIn("prior invocation is proven not accepted", retry_row[1])
        self.assertIn("atomically consume retry", retry_row[1])
        self.assertEqual("`in_flight`", retry_row[2])
        self.assertEqual("retry claimant invokes once", retry_row[3])
        self.assertIn(("`succeeded`", "any reconciliation", "`succeeded`", "do not invoke"), rows)

        def atomic_claim(record, snapshot, claimant, eligible_states, *, retry=False):
            if record["version"] != snapshot["version"]:
                return None
            if snapshot["state"] not in eligible_states:
                return None
            if retry and (not snapshot["prior_not_accepted"] or not snapshot["retry_available"]):
                return None
            next_attempt = snapshot["attempt_count"] + 1
            attempt_id = f"{record['cycle_id']}:{next_attempt}:{claimant}"
            record["state"] = "in_flight"
            record["attempt_count"] = next_attempt
            record["active_attempt_id"] = attempt_id
            record["version"] += 1
            if retry:
                record["retry_available"] = False
            record["invocations"].append(attempt_id)
            return attempt_id

        record = {
            "cycle_id": "worker-1/cycle-1",
            "version": 0,
            "state": "unclaimed",
            "attempt_count": 0,
            "retry_available": True,
            "prior_not_accepted": False,
            "active_attempt_id": None,
            "invocations": [],
        }
        initial_snapshot_a = dict(record)
        initial_snapshot_b = dict(record)
        initial_winner = atomic_claim(record, initial_snapshot_a, "director-a", {"unclaimed"})
        initial_loser = atomic_claim(record, initial_snapshot_b, "director-b", {"unclaimed"})
        self.assertIsNotNone(initial_winner)
        self.assertIsNone(initial_loser)
        self.assertEqual([initial_winner], record["invocations"])
        self.assertEqual(1, record["attempt_count"])

        record.update(state="failed", prior_not_accepted=True, active_attempt_id=None)
        record["version"] += 1
        retry_snapshot_a = dict(record)
        retry_snapshot_b = dict(record)
        retry_winner = atomic_claim(record, retry_snapshot_a, "director-a", {"failed", "unknown"}, retry=True)
        retry_loser = atomic_claim(record, retry_snapshot_b, "director-b", {"failed", "unknown"}, retry=True)
        self.assertIsNotNone(retry_winner)
        self.assertIsNone(retry_loser)
        self.assertFalse(record["retry_available"])
        self.assertEqual(2, record["attempt_count"])
        self.assertEqual(2, len(record["invocations"]))
        self.assertEqual(2, len(set(record["invocations"])))
        self.assertNotEqual(initial_winner, retry_winner)

        ambiguous = {
            "cycle_id": "worker-2/cycle-1",
            "version": 0,
            "state": "unknown",
            "attempt_count": 1,
            "retry_available": True,
            "prior_not_accepted": False,
            "active_attempt_id": None,
            "invocations": [],
        }
        ambiguous_snapshot_a = dict(ambiguous)
        ambiguous_snapshot_b = dict(ambiguous)
        self.assertIsNone(atomic_claim(ambiguous, ambiguous_snapshot_a, "director-a", {"failed", "unknown"}, retry=True))
        self.assertIsNone(atomic_claim(ambiguous, ambiguous_snapshot_b, "director-b", {"failed", "unknown"}, retry=True))
        self.assertEqual([], ambiguous["invocations"])
        self.assertEqual(1, ambiguous["attempt_count"])

    def test_korean_public_guidance_requires_terminal_cleanup_and_finalization(self):
        source = (REPO_ROOT / "README.ko.md").read_text(encoding="utf-8")
        required_patterns = [
            r"terminal result cleanup은 stalled recovery와 분리합니다",
            r"report/evidence를 캡처하고 저장한 다음",
            r"atomic cleanup claim",
            r"root 세션이 끝나기 전에 자신이\s+만든 모든 lifecycle을 reconcile",
            r"unreconciled child를 남겨 두고\s+조용히 종료해서는 안 됩니다",
            r"fork가 main working tree에 자동 merge되지는\s+않습니다",
        ]
        for pattern in required_patterns:
            with self.subTest(pattern=pattern):
                self.assertRegex(source, re.compile(pattern, re.S), pattern)

    def test_claude_guidance_has_no_stale_caps_or_direct_coding_exception(self):
        guidance_files = [
            REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "claude" / "profiles" / "default.yaml",
            REPO_ROOT / "claude" / "skills" / "agent-director" / "references" / "agent-briefing-template.md",
            REPO_ROOT / "claude" / "INSTALL.md",
            REPO_ROOT / "claude" / "CLAUDE.md.example",
            REPO_ROOT / "README.md",
            REPO_ROOT / "README.ko.md",
        ]
        stale_fixed_cap_terms = (
            "max_batch_agents",
            "max_total_spawned_agents_per_request",
            "within_limit",
        )
        stale_direct_coding_patterns = (
            r"single\s+small\s+fix",
            r"plain\s+direct\s+coding\s+is\s+fine",
            r"direct\s+coding\s+is\s+fine",
        )
        for path in guidance_files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(guidance_file=path.relative_to(REPO_ROOT)):
                for term in stale_fixed_cap_terms:
                    self.assertNotIn(term, source)
                for pattern in stale_direct_coding_patterns:
                    self.assertNotRegex(source, re.compile(pattern, re.I | re.S))

        claude_skill = (REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Native runtime capacity is the only authority for worker capacity", claude_skill)
        self.assertIn("keep it `unknown`", claude_skill)
        self.assertRegex(
            claude_skill,
            re.compile(r"slot-full.*wait.*inspect.*reconcil(?:e|ing) terminal.*(?:re-scop|return)", re.I | re.S),
        )

        briefing = (REPO_ROOT / "claude" / "skills" / "agent-director" / "references" / "agent-briefing-template.md").read_text(encoding="utf-8")
        self.assertNotRegex(briefing, re.compile(r"cumulative.{0,50}(?:limit|cap)", re.I | re.S))
        match = re.search(r"```json\s*(\{.*?\})\s*```", briefing, re.S)
        self.assertIsNotNone(match, "Claude briefing template has no JSON disclosure example")
        disclosure = json.loads(match.group(1))
        spawn_budget = disclosure["spawn_budget"]
        self.assertEqual(
            {
                "already_spawned_count",
                "this_batch_count",
                "total_after_spawn",
                "capacity_source",
                "capacity_known",
            },
            set(spawn_budget) - {"observed_capacity"},
        )
        self.assertTrue(spawn_budget["capacity_known"])
        self.assertEqual(spawn_budget["capacity_source"], "observed_native_runtime")
        self.assertIn("observed_capacity", spawn_budget)
        self.assertEqual(spawn_budget["observed_capacity"], 2)

        work_contract = disclosure["work_contract"]
        for field in (
            "independent_groups",
            "dependency_edges",
            "planned_workers",
            "capacity_source",
            "why_fewer_workers_cannot_absorb",
        ):
            self.assertIn(field, work_contract)
        self.assertEqual(len(work_contract["independent_groups"]), 2)
        self.assertEqual(work_contract["dependency_edges"], [])
        self.assertEqual(work_contract["planned_workers"], 2)

        example = (REPO_ROOT / "claude" / "CLAUDE.md.example").read_text(encoding="utf-8")
        self.assertRegex(example, re.compile(r"Every state-changing or code task.*small.*task contract.*implementer", re.I | re.S))
        self.assertIn("read_only: true", example)

        for readme_path in [REPO_ROOT / "README.md", REPO_ROOT / "README.ko.md"]:
            readme = readme_path.read_text(encoding="utf-8")
            with self.subTest(readme=readme_path.name):
                self.assertRegex(readme, re.compile(r"timeout.*(?:observation|관찰)", re.I | re.S))
                self.assertIn("evidence", readme)
                self.assertIn("unknown", readme)
                self.assertIn("bounded interrupt", readme)
                self.assertRegex(readme, re.compile(r"worker cap", re.I))

    def test_readme_recovery_summaries_have_full_parity(self):
        recovery_patterns = {
            "README.md": [
                r"A native `RUNNING` worker is preserved by\s+default",
                r"A wait timeout is an\s+observation only",
                r"On the first timeout, record the observation and perform\s+another\s+task-appropriate bounded wait by default",
                r"unless explicit fatal runtime\s+evidence already exists",
                r"a crash, repeated tool error, explicit failure,\s+runtime disconnect, or a demonstrably repeated identical command",
                r"(?:In\s+)?read-only tasks, file changes or\s+their\s+absence are never stall evidence",
                r"(?:In\s+)?write\s+tasks,\s+absence\s+of\s+file\s+changes\s+alone\s+never proves a stall",
                r"A read-only architecture/design final\s+report is a completed-work artifact only when it contains concrete scope,\s+evidence,\s+findings,\s+tests or inspection commands,\s+and unresolved risks",
                r"If progress telemetry is unavailable, classify the worker as `unknown`, not\s+`stalled`",
                r"A queued request to return progress is not an interrupt",
                r"Terminal-result cleanup is separate from stalled recovery",
                r"captures and persists the authoritative report/evidence",
                r"every lifecycle it created must be reconciled",
                r"does not merge its fork into the main working\s+tree",
            ],
            "README.ko.md": [
                r"네이티브 `RUNNING` worker는 기본적으로\s+보존합니다",
                r"wait timeout은 해당\s+대기 동안 final result가 도착하지 않았다는\s+관찰일 뿐",
                r"첫 timeout에서는 관찰을 기록하고 작업에 맞는 bounded wait를 한 번 더\s+수행합니다",
                r"fatal runtime evidence가 이미 있으면\s+예외입니다",
                r"crash, 반복된 tool error, 명시적 failure, runtime disconnect,\s+명백하게 반복되는 동일 command",
                r"파일 상태는 lifecycle evidence가 아닙니다\. read-only 작업에서 파일 변경\s+여부는 stall evidence가 아니며",
                r"write\s+작업에서도? 파일 변경이 없다는 사실만\s+으로 stall을 입증할 수 없습니다",
                r"read-only architecture/design 최종 report는\s+구체적 scope, evidence, findings, tests 또는 inspection commands와 unresolved\s+risks를 포함할 때만 completed-work artifact입니다",
                r"progress telemetry가 없으면 `stalled`가 아니라 `unknown`으로 분류합니다",
                r"queued progress 요청은 interrupt가 아닙니다",
                r"terminal result cleanup은 stalled recovery와 분리합니다",
                r"report/evidence를 캡처하고 저장한 다음",
                r"모든 lifecycle을 reconcile해야 하며",
                r"fork가 main working tree에 자동 merge되지는\s+않습니다",
            ],
        }
        for filename, patterns in recovery_patterns.items():
            readme = (REPO_ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(readme=filename):
                for pattern in patterns:
                    self.assertRegex(readme, re.compile(pattern), pattern)


class TestWorkerRoleBoundary(unittest.TestCase):
    """Guards against spawned workers reactivating root-level Director mode."""

    COMMON_BOUNDARY_CLAUSES = {
        "one_director": r"(?:task tree has exactly one Director|exactly one Director in a task tree)",
        "parent_contract_authority": r"parent Director(?:'s|’s)\s+Task Contract\s+is authoritative",
        "no_director_mode": r"(?:MUST NOT|must not|do not)\s*:?\s*(?:[-*]\s*)?announce\s+`director_mode:\s*on`",
        "no_root_disclosures": r"publish\s+(?:a\s+)?root-level\s+`?task_start`?\s+or\s+composition\s+disclosure",
        "no_overall_completion": r"declare\s+the\s+overall\s+task\s+complete",
        "role_ambiguity": r"stop(?:s)?\s+and\s+report(?:s)?\s+role\s+ambiguity\s+to\s+the\s+parent",
    }

    ADAPTER_BOUNDARY_CLAUSES = {
        "no_parent_rewrite": r"(?:create,\s*)?rewrite,?\s+or\s+re-decompose\s+the\s+parent\s+contract",
        "no_worker_management": r"spawn\s+or\s+manage\s+workers",
        "no_integration": r"integrate\s+or\s+merge(?:\s+work)?",
    }

    ASSIGNED_MISSION_CLAUSES = {
        "assigned_mission": r"worker (?:must )?execute(?:s)? only its assigned mission and report(?:s)? evidence or status",
    }

    COMMON_BOUNDARY_PROHIBITIONS = {
        name: pattern
        for name, pattern in {
            **COMMON_BOUNDARY_CLAUSES,
            **ADAPTER_BOUNDARY_CLAUSES,
        }.items()
        if name.startswith("no_")
    }

    CONTRACTED_OPERATION_CLAUSES = {
        "contracted_operation": r"worker may (?:perform|carry out) a deployment or another (?:external/)?state-changing operation.*parent contract explicitly includes",
        "native_runtime_metadata": r"native runtime role metadata remains authoritative",
    }

    ABSOLUTE_ROLE_CLAUSES = {
        "subagent_never_director": r"spawned subagent is never a Director under any circumstance",
        "role_before_creation": r"(?:assign|assigned|assigns).*role.*before (?:creation|spawn)",
        "director_invalid": r"(?:role name )?`?director`?.{0,40}(?:invalid|not a valid)",
    }

    WORKER_CONTRACT_CLAUSES = {
        "scope_and_non_goals": r"scope(?:\s+and\s+|/)non-goals",
        "goal": r"\bgoal\b",
        "success_criteria": r"success_criteria",
        "failure_criteria": r"failure_criteria",
        "termination_criteria": r"termination_criteria",
        "required_evidence": r"required_evidence",
        "pre_spawn_failure": r"pre-spawn failure",
    }

    WORKER_CONTRACT_FIELDS = (
        "goal",
        "success_criteria",
        "failure_criteria",
        "termination_criteria",
        "required_evidence",
    )

    YAML_PROMPT_CLAUSES = {
        "root_only_director": r"root/current parent session is the only Director",
        "assigned_worker_roles": r"spawned workers/reviewers remain in their assigned roles",
        "parent_contract_authority": r"parent Director(?:'s|’s)\s+Task Contract is authoritative",
        "assigned_mission": r"execute only the assigned mission and report evidence/status",
        "no_director_mode": r"do not announce\s+director_mode:\s*on",
        "no_root_disclosures": r"publish root-level\s+task_start/composition disclosures",
        "no_parent_rewrite": r"rewrite or re-decompose the parent contract",
        "no_worker_management": r"spawn/manage workers",
        "no_integration": r"integrate/merge",
        "no_overall_completion": r"declare overall completion",
        "role_ambiguity": r"stop and report role ambiguity to the parent",
        "contracted_operation": r"parent-contracted deployment or other external/state-changing operation remains allowed",
    }

    KOREAN_BOUNDARY_CLAUSES = {
        "one_director": r"Director가 정확히 하나뿐",
        "root_parent": r"`root/current parent session`",
        "parent_contract_authority": r"부모 Director의 Task Contract가 권위 있는 계약",
        "assigned_mission": r"worker는 배정된 임무만 실행하고 부모에게 evidence 또는 status를 보고",
        "no_director_mode": r"`director_mode: on`을 announce하거나",
        "no_root_disclosures": r"root-level `task_start` 또는 composition disclosure를 게시",
        "no_parent_rewrite": r"부모 contract를 다시 쓰거나 재분해",
        "no_worker_management": r"worker를 spawn하거나 관리",
        "no_integration": r"작업을 integrate하거나 merge",
        "no_overall_completion": r"`overall task complete`를 선언해서는 안 됩니다",
        "role_ambiguity": r"부모에게 `role ambiguity`\s*\(역할 모호성\)를 보고",
        "contracted_operation": r"부모 contract에 명시적으로 포함된 경우에 한해 worker가 배포나 다른 state-changing operation을 수행",
        "native_runtime_metadata": r"native runtime role metadata가 우선",
    }

    @staticmethod
    def _normalized(source: str) -> str:
        return re.sub(r"\s+", " ", source).strip()

    def _section(self, path: Path, heading_pattern: str) -> str:
        source = path.read_text(encoding="utf-8")
        match = re.search(rf"(?im)^(?P<level>##)\s+{heading_pattern}\s*$", source)
        if match is None:
            self.fail(f"{path.relative_to(REPO_ROOT)} has no matching boundary heading")
        level = len(match.group("level"))
        remainder = source[match.end() :]
        next_heading = re.search(rf"(?m)^#{{1,{level}}}\s+", remainder)
        end = match.end() + (next_heading.start() if next_heading else len(remainder))
        return self._normalized(source[match.start() : end])

    def _between(self, path: Path, start_pattern: str, end_pattern: str) -> str:
        source = path.read_text(encoding="utf-8")
        start = re.search(start_pattern, source, re.I | re.M)
        if start is None:
            self.fail(f"{path.relative_to(REPO_ROOT)} has no boundary start marker")
        remainder = source[start.end() :]
        end = re.search(end_pattern, remainder, re.I | re.M)
        end_offset = end.start() if end else len(remainder)
        return self._normalized(source[start.start() : start.end() + end_offset])

    def _assert_clauses(self, source: str, clauses: dict[str, str], surface: str) -> None:
        for name, pattern in clauses.items():
            with self.subTest(surface=surface, clause=name):
                self.assertRegex(source, re.compile(pattern, re.I | re.S), pattern)

    def _english_policy_boundaries(self) -> list[tuple[str, str]]:
        return [
            (
                "core/ROLE-CONTRACT.md",
                self._section(
                    REPO_ROOT / "core" / "ROLE-CONTRACT.md",
                    r"Single-Director and worker-mode boundary",
                ),
            ),
            (
                "core/DELEGATION-PROTOCOL.md",
                self._section(REPO_ROOT / "core" / "DELEGATION-PROTOCOL.md", r"Worker-mode boundary"),
            ),
            (
                "claude/skills/agent-director/SKILL.md",
                self._section(
                    REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md",
                    r"Worker-mode boundary \(mandatory\)",
                ),
            ),
        ]

    def test_core_and_adapter_boundaries_require_each_clause(self):
        clauses = {**self.COMMON_BOUNDARY_CLAUSES, **self.ADAPTER_BOUNDARY_CLAUSES}
        for surface, boundary in self._english_policy_boundaries():
            self._assert_clauses(boundary, clauses, surface)

    def test_assigned_mission_is_present_on_role_and_adapter_skills(self):
        surfaces = [
            (surface, boundary)
            for surface, boundary in self._english_policy_boundaries()
            if surface != "core/DELEGATION-PROTOCOL.md"
        ]
        for surface, boundary in surfaces:
            self._assert_clauses(boundary, self.ASSIGNED_MISSION_CLAUSES, surface)

    def test_contracted_operations_and_runtime_metadata_are_scoped_to_core_and_adapters(self):
        for surface, boundary in self._english_policy_boundaries():
            self._assert_clauses(boundary, self.CONTRACTED_OPERATION_CLAUSES, surface)

    def test_public_guidance_requires_each_english_boundary_prohibition(self):
        public_boundaries = [
            (
                "claude/CLAUDE.md.example",
                self._section(REPO_ROOT / "claude" / "CLAUDE.md.example", r"Director mode"),
            ),
        ]
        for surface, boundary in public_boundaries:
            self._assert_clauses(boundary, self.COMMON_BOUNDARY_CLAUSES, surface)

    def test_claude_activation_is_root_only_and_workers_skip_it(self):
        director_mode = self._section(REPO_ROOT / "claude" / "CLAUDE.md.example", r"Director mode")
        self.assertRegex(
            director_mode,
            re.compile(r"Only the root/current parent session operates as Director", re.I),
        )
        self.assertRegex(
            director_mode,
            re.compile(r"Spawned workers and reviewers do not activate Director mode", re.I),
        )
        self.assertNotRegex(
            director_mode,
            re.compile(r"load the `agent-director` skill and operate as director:", re.I),
        )

    def test_schema_requires_worker_execution_criteria_and_forbids_director_role(self):
        schema = json.loads(
            (REPO_ROOT / "schemas" / "task-contract.schema.json").read_text(encoding="utf-8")
        )
        for field in self.WORKER_CONTRACT_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, schema["required"])
                self.assertIn(field, schema["properties"])
        role_schema = schema["properties"]["delegation"]["properties"]["role"]
        self.assertNotIn("director", role_schema["enum"])
        self.assertRegex(role_schema["description"], re.compile(r"non-Director|director.*invalid", re.I))

    def test_claude_task_template_exposes_worker_contract_fields(self):
        path = REPO_ROOT / "claude" / "skills" / "agent-director" / "references" / "task-template.md"
        source = self._normalized(path.read_text(encoding="utf-8"))
        self._assert_clauses(source, self.ABSOLUTE_ROLE_CLAUSES, str(path.relative_to(REPO_ROOT)))
        for field in self.WORKER_CONTRACT_FIELDS:
            self.assertIn(f'"{field}"', source)

    def test_platform_and_plugin_surfaces_require_absolute_worker_boundary_and_contract(self):
        surfaces = [
            REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "claude" / "CLAUDE.md.example",
        ]
        for path in surfaces:
            source = self._normalized(path.read_text(encoding="utf-8"))
            surface = str(path.relative_to(REPO_ROOT))
            with self.subTest(surface=surface):
                self._assert_clauses(source, self.ABSOLUTE_ROLE_CLAUSES, surface)
                self._assert_clauses(source, self.WORKER_CONTRACT_CLAUSES, surface)

    def test_korean_public_guidance_exposes_worker_contract_fields(self):
        source = self._normalized((REPO_ROOT / "README.ko.md").read_text(encoding="utf-8"))
        self.assertIn("비(非)Director 역할", source)
        self.assertIn("worker는", source)
        for field in self.WORKER_CONTRACT_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, source)

    def test_absolute_role_and_contract_mutants_are_rejected(self):
        path = REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md"
        source = self._normalized(path.read_text(encoding="utf-8"))
        clauses = {**self.ABSOLUTE_ROLE_CLAUSES, **self.WORKER_CONTRACT_CLAUSES}
        for name, pattern in clauses.items():
            mutant = re.sub(pattern, "", source, count=1, flags=re.I | re.S)
            with self.subTest(clause=name):
                self.assertNotRegex(mutant, re.compile(pattern, re.I | re.S), pattern)

    def test_individual_prohibition_mutants_are_rejected(self):
        boundary = self._section(
            REPO_ROOT / "core" / "ROLE-CONTRACT.md",
            r"Single-Director and worker-mode boundary",
        )
        for name, pattern in self.COMMON_BOUNDARY_PROHIBITIONS.items():
            mutant = re.sub(pattern, "", boundary, count=1, flags=re.I | re.S)
            with self.subTest(clause=name):
                self.assertNotRegex(mutant, re.compile(pattern, re.I | re.S), pattern)

if __name__ == "__main__":
    unittest.main()
