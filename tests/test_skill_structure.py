"""Structural tests: required directory layout and SKILL.md frontmatter.

Runnable via `python -m unittest discover -s tests` from the repo root. The
repo root is located relative to this file so the suite works regardless of
the caller's current working directory.
"""

from __future__ import annotations

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
    def test_core_has_ten_docs(self):
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


if __name__ == "__main__":
    unittest.main()
