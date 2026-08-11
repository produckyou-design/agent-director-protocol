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

    def test_both_platform_skill_trees_exist(self):
        for platform in ("claude", "codex"):
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
        for platform in ("claude", "codex"):
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
        for platform in ("claude", "codex"):
            references_dir = REPO_ROOT / platform / "skills" / "agent-director" / "references"
            actual = {p.name for p in references_dir.iterdir() if p.is_file()}
            with self.subTest(platform=platform):
                self.assertEqual(actual, validate_skills.REQUIRED_REFERENCE_FILES)

    def test_install_and_profiles_exist(self):
        for platform in ("claude", "codex"):
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


class TestCodexAdapterWorkerPolicy(unittest.TestCase):
    def test_changelog_080_uses_native_spawn_effort_field(self):
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        match = re.search(
            r"^## \[0\.8\.0\].*?(?=^## \[|\Z)",
            changelog,
            re.M | re.S,
        )
        self.assertIsNotNone(match, "CHANGELOG.md has no 0.8.0 release section")
        release = match.group(0)
        self.assertIn('model="gpt-5.6-luna"', release)
        self.assertIn('reasoning_effort="max"', release)
        self.assertNotRegex(
            release,
            re.compile(
                r"native worker spawn[\s\S]{0,200}model_reasoning_effort",
                re.I,
            ),
        )

    def test_all_codex_custom_agent_examples_pin_luna_max(self):
        agent_dir = REPO_ROOT / "codex" / "agents"
        files = sorted(agent_dir.glob("*.toml.example"))
        self.assertEqual(
            {path.stem for path in files},
            {"investigator.toml", "implementer.toml", "reviewer.toml", "rescue.toml", "release-auditor.toml"},
        )
        for path in files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(profile=path.name):
                self.assertRegex(source, re.compile(r'^model\s*=\s*"gpt-5\.6-luna"$', re.M), path.name)
                self.assertRegex(source, re.compile(r'^model_reasoning_effort\s*=\s*"max"$', re.M), path.name)

    def test_codex_defaults_and_policy_docs_are_fixed_and_fail_closed(self):
        config = (REPO_ROOT / "codex" / "config.toml.example").read_text(encoding="utf-8")
        profile = (REPO_ROOT / "codex" / "profiles" / "default.yaml").read_text(encoding="utf-8")
        self.assertIn('default_subagent_reasoning_effort = "max"', config)
        self.assertNotIn("effort_by_task_kind", profile)
        self.assertIn("explicit_per_spawn", profile)
        self.assertIn("runtime_capacity", profile)
        self.assertNotIn("max_total_spawned_agents_per_request", profile)
        self.assertIn("runtime_metadata_verification: required", profile)
        self.assertIn("available: false", profile)

        policy_files = [
            REPO_ROOT / "codex" / "AGENTS.md.example",
            REPO_ROOT / "codex" / "INSTALL.md",
            REPO_ROOT / "codex" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "codex" / "skills" / "agent-director" / "references" / "task-template.md",
            REPO_ROOT / "codex" / "skills" / "agent-director" / "references" / "agent-briefing-template.md",
            REPO_ROOT / "plugins" / "agent-director" / "README.md",
            REPO_ROOT / "plugins" / "agent-director" / "skills" / "agent-director" / "SKILL.md",
        ]
        for path in policy_files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(policy_file=path.relative_to(REPO_ROOT)):
                self.assertNotIn("effort_by_task_kind", source)
                self.assertIn("gpt-5.6-luna", source)
                self.assertIn("max", source)
                self.assertNotIn("max_concurrent_threads_per_session = 4", source)
                self.assertNotIn("max_total_spawned_agents_per_request", source)
                self.assertRegex(source, r'(?<!model_)reasoning_effort[\"\`]*\s*[:=]\s*[\"\`]?max')
                self.assertRegex(source, re.compile(r"metadata|runtime", re.I))
                self.assertRegex(source, re.compile(r"reject|close|unverifiable|fallback", re.I))
                self.assertRegex(source, re.compile(r"conflict boundar|conflict domain", re.I))
                self.assertRegex(source, re.compile(r"cannot (?:safely )?(?:absorb|be folded)|cannot absorb", re.I))
                self.assertRegex(source, re.compile(r"new\s+(?:composition\s+)?disclosure", re.I))
                self.assertRegex(source, re.compile(r"classified\s+failure", re.I))

        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn('reasoning_effort="max"', readme)
        self.assertIn("minimum safe structure", readme)
        self.assertRegex(readme, re.compile(r"new\s+disclosure", re.I))
        korean_readme = (REPO_ROOT / "README.ko.md").read_text(encoding="utf-8")
        self.assertIn('reasoning_effort="max"', korean_readme)
        self.assertNotIn('native worker spawn must carry model_reasoning_effort', korean_readme)
        self.assertIn("기존 contract/worker가 흡수할 수", korean_readme)

    def test_codex_plugin_manifest_matches_release(self):
        manifest = json.loads(
            (
                REPO_ROOT / "plugins" / "agent-director" / ".codex-plugin" / "plugin.json"
            ).read_text(encoding="utf-8")
        )
        changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        released = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.M)
        self.assertTrue(released)
        self.assertEqual(manifest["version"], released[0])
        self.assertIn("gpt-5.6-luna", manifest["description"])
        self.assertIn("fail-closed", manifest["description"])

    def test_codex_skill_allows_default_implicit_invocation(self):
        skill_metadata = (
            REPO_ROOT
            / "plugins"
            / "agent-director"
            / "skills"
            / "agent-director"
            / "agents"
            / "openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: true", skill_metadata)
        self.assertIn("by default", skill_metadata)

    def test_codex_disclosure_phases_are_explicit_and_platform_boundary_is_honest(self):
        policy_files = [
            REPO_ROOT / "core" / "DELEGATION-PROTOCOL.md",
            REPO_ROOT / "core" / "CONCURRENCY-RULES.md",
            REPO_ROOT / "codex" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "plugins" / "agent-director" / "skills" / "agent-director" / "SKILL.md",
        ]
        for path in policy_files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(policy_file=path.relative_to(REPO_ROOT)):
                self.assertIn("task_start", source)
                self.assertIn("addition_basis", source)
                self.assertRegex(source, re.compile(r"before every task", re.I))

        codex_skill = (REPO_ROOT / "codex" / "skills" / "agent-director" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("multi_agent_v1__spawn_agent", codex_skill)

    def test_plugin_skill_blocks_unapproved_director_implementation(self):
        skill = (
            REPO_ROOT
            / "plugins"
            / "agent-director"
            / "skills"
            / "agent-director"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertRegex(skill, re.compile(r"Director .*does not\s+directly edit product code", re.I | re.S))
        self.assertIn("planned_workers > 0", skill)
        self.assertIn("work_contract.read_only: true", skill)
        self.assertRegex(skill, re.compile(r"shared .*conflict domain", re.I | re.S))
        self.assertRegex(skill, re.compile(r"Luna/max .*does not remove", re.I | re.S))


    def test_native_worker_lifecycle_recovery_is_fail_closed(self):
        policy_files = [
            REPO_ROOT / "codex" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "plugins" / "agent-director" / "skills" / "agent-director" / "SKILL.md",
        ]
        for path in policy_files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(policy_file=path.relative_to(REPO_ROOT)):
                self.assertIn("wait_agent", source)
                self.assertIn("interrupt=true", source)
                self.assertIn("Do not repeatedly resume", source)
                self.assertRegex(source, re.compile(r"(?:does|do) not merge", re.I))
                self.assertIn("fork_context=false", source)
                self.assertRegex(source, re.compile(r"serialization failure", re.I))
                self.assertIn("Rescue is unavailable", source)
                self.assertRegex(
                    source,
                    re.compile(r"never take over.*automatically|never.*takeover automatically", re.I | re.S),
                )
                self.assertIn("current-session user authorization", source)
                self.assertRegex(source, re.compile(r"progress evidence", re.I))
                self.assertIn("completed_work_unreported", source)
                self.assertIn("stalled", source)
                self.assertIn("active command", source)
                self.assertIn("unknown", source)
                self.assertRegex(source, re.compile(r"timeout.*never", re.I | re.S))

    def test_worker_recovery_policy_preserves_progress_and_bounds_recovery(self):
        policy_files = [
            REPO_ROOT / "core" / "CONCURRENCY-RULES.md",
            REPO_ROOT / "codex" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "plugins" / "agent-director" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "plugins" / "agent-director" / "README.md",
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
            r"Close is allowed only after.*stalled.*one interrupt.*one bounded wait",
            r"Preserve `completed_work_unreported` and `unknown`",
        ]
        for path in policy_files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(policy_file=path.relative_to(REPO_ROOT)):
                for pattern in required_patterns:
                    self.assertRegex(source, re.compile(pattern, re.I | re.S), pattern)

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
            re.compile(r"slot-full.*wait.*inspect.*clos(?:e|ing) completed.*(?:re-scop|return)", re.I | re.S),
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
                self.assertRegex(readme, re.compile(r"timeout.*observation", re.I | re.S))
                self.assertIn("progress evidence", readme)
                self.assertIn("unknown", readme)
                self.assertIn("bounded interrupt", readme)
                self.assertRegex(readme, re.compile(r"numeric worker cap", re.I))

    def test_readme_recovery_summaries_have_full_parity(self):
        recovery_patterns = {
            "README.md": [
                r"normal baseline is already\s+max, so Codex Rescue is unavailable",
                r"Rescue failure does not grant\s+automatic Director takeover",
                r"A native `RUNNING` worker is preserved by\s+default",
                r"A wait timeout is an observation only",
                r"On the first timeout, record the observation and perform\s+another task-appropriate bounded wait by default",
                r"unless explicit fatal runtime\s+evidence already exists",
                r"a crash, repeated tool error, explicit failure,\s+runtime disconnect, or a demonstrably repeated identical command",
                r"During the\s+longer wait, inspect exposed native status, recent tool output, active-command\s+signals, or other declared progress evidence",
                r"read-only tasks, file changes or their\s+absence are never stall evidence",
                r"write tasks, absence of file changes alone\s+never proves a stall",
                r"read-only architecture/design final report counts as a\s+completed-work artifact only when it includes concrete scope, evidence,\s+findings, tests or inspection commands, and unresolved risks",
                r"no progress telemetry, classify the state as `unknown`, not\s+`stalled`",
                r"Only explicit fatal evidence or a declared bounded no-progress window with\s+native status still `RUNNING` and no active command or progress signal permits\s+one bounded interrupt \(`interrupt=true`\)",
                r"Stop the current work,\s+summarize only evidence already secured, do not start new work, tests, or edits,\s+then exit",
                r"A queued message/request to return progress is not an interrupt",
                r"Normal `RUNNING` or progressing workers are not closed",
                r"Preserve `completed_work_unreported` and `unknown`",
                r"Repeated resume/re-dispatch is forbidden as a timeout-recovery loop",
                r"Any fresh implementer or\s+scope split requires a new `addition` disclosure and revised contract",
                r"A named implementer uses\s+`fork_context=false` or omits it",
                r"`fork_context=true`\s+is compatible only when\s+`agent_type` is omitted",
                r"Serialization failure is a\s+pre-spawn dispatch failure, not an implementation failure",
            ],
            "README.ko.md": [
                r"기본값이 이미\s+max이므로 Codex Rescue는 일반 ADP 실행에서\s+사용할 수 없으며",
                r"Rescue 실패는\s+automatic Director takeover를\s+허용하지 않습니다",
                r"네이티브 `RUNNING` worker는 기본적으로\s+보존합니다",
                r"wait timeout은 해당 대기 동안 final result가 도착하지 않았다는\s+관찰일 뿐",
                r"첫 timeout이 발생하면 관찰을 기록하고,\s+명시적인 fatal runtime evidence",
                r"기본적으로 작업에 맞는 두 번째 bounded wait를 수행합니다",
                r"충돌, 반복된 tool error, 명시적 failure,\s+runtime disconnect 또는 동일 command의 반복 실행이 입증된 경우",
                r"더 긴 대기 동안 노출된 네이티브 status, 최근 tool output, active-command 신호\s+또는 선언된 progress를 확인합니다",
                r"read-only 작업에서 파일이\s+변경되거나 변경되지 않은 것은 어떤 경우에도 stall evidence가 아니며",
                r"write\s+작업에서 파일 변경이 없다는 사실만으로는 stall을 입증할 수 없습니다",
                r"read-only architecture/design 최종 report는 concrete scope, evidence, findings,\s+tests 또는 inspection commands, unresolved risks를 포함할 때만\s+completed-work artifact로 인정합니다",
                r"progress telemetry가 노출되지 않으면\s+stalled가 아니라 `unknown`으로 분류합니다",
                r"명시적 fatal evidence 또는 네이티브 status가 여전히 `RUNNING`이고 active\s+command나 progress signal이 없는, 선언된 bounded no-progress observation\s+window가 끝난 경우에만\s+하나의 bounded interrupt\(`interrupt=true`\)를 허용합니다",
                r"현재 작업을 중단하고, 이미 확보한\s+evidence만 요약하며, 새 work, tests 또는 edits를 시작하지 말고 종료하세요",
                r"queued message/request to return progress는 interrupt가 아닙니다",
                r"정상\s+`RUNNING` 또는 progressing worker는 close하지 않습니다",
                r"`completed_work_unreported`와 `unknown`은 보존하며",
                r"반복 resume/re-dispatch를 timeout 복구 루프로 사용하는 것은 금지하며",
                r"새 implementer 또는 scope split에는 새 `addition` disclosure와\s+수정된 contract가 필요합니다",
                r"이름이 지정된 implementer는\s+`fork_context=false`를 사용하거나 이를 생략합니다",
                r"`fork_context=true`는\s+`agent_type`을 생략한 경우에만 호환됩니다",
                r"serialization\s+failure는 구현 실패가 아니라\s+pre-spawn dispatch failure입니다",
                r"모든 task, 모든 state-changing operation, 모든 native-spawn attempt 전에 Director는\s+`user_visible: true`인 work-contract disclosure를 먼저",
            ],
        }
        for filename, patterns in recovery_patterns.items():
            readme = (REPO_ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(readme=filename):
                for pattern in patterns:
                    self.assertRegex(readme, re.compile(pattern), pattern)

if __name__ == "__main__":
    unittest.main()
