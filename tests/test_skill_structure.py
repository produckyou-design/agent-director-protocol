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


if __name__ == "__main__":
    unittest.main()
