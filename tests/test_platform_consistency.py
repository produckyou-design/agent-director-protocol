"""Cross-platform / cross-schema consistency tests.

Runnable via `python -m unittest discover -s tests` from the repo root.
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
SCHEMAS_DIR = REPO_ROOT / "schemas"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import check_repository  # noqa: E402

CANONICAL_TEN_CHECK_KEYS = [
    "code_actually_changed",
    "feature_wired_into_flow",
    "tests_actually_executed",
    "test_results_match_report",
    "no_fake_or_placeholder_success",
    "no_regressions",
    "interfaces_preserved",
    "no_out_of_scope_changes",
    "error_handling_present",
    "completion_criteria_met",
]

MODEL_NAME_PATTERN = re.compile(
    r"\b(claude|opus|sonnet|haiku|codex|openai|anthropic|gpt)\b", re.IGNORECASE
)


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


class TestReferenceFilenameSets(unittest.TestCase):
    def test_claude_and_codex_reference_filenames_are_identical(self):
        claude_refs = REPO_ROOT / "claude" / "skills" / "agent-director" / "references"
        codex_refs = REPO_ROOT / "codex" / "skills" / "agent-director" / "references"
        claude_files = {p.name for p in claude_refs.iterdir() if p.is_file()}
        codex_files = {p.name for p in codex_refs.iterdir() if p.is_file()}
        self.assertEqual(claude_files, codex_files)


class TestTenCheckKeys(unittest.TestCase):
    def test_review_result_check_keys_match_canonical_list(self):
        schema = load_schema("review-result.schema.json")
        required_keys = schema["properties"]["checks"]["required"]
        self.assertEqual(sorted(required_keys), sorted(CANONICAL_TEN_CHECK_KEYS))
        self.assertEqual(len(required_keys), 10)


class TestFailureReasonEnumsMatch(unittest.TestCase):
    def test_failure_reason_enums_identical_across_schemas(self):
        review_schema = load_schema("review-result.schema.json")
        loop_schema = load_schema("failure-loop.schema.json")

        review_enum = review_schema["definitions"]["failure_reason"]["enum"]
        loop_enum = loop_schema["properties"]["failure_reasons"]["items"]["enum"]

        self.assertEqual(sorted(review_enum), sorted(loop_enum))


class TestCoreDocsHaveNoModelNames(unittest.TestCase):
    def test_core_markdown_has_no_model_name_strings(self):
        core_dir = REPO_ROOT / "core"
        offenders = []
        for md_file in sorted(core_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if MODEL_NAME_PATTERN.search(line):
                    offenders.append(f"{md_file.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")
        self.assertEqual(offenders, [], f"model-name strings found in core/: {offenders}")


class TestSkillsLinkToSameCoreDocSet(unittest.TestCase):
    def test_both_skill_mds_link_to_same_core_doc_filenames(self):
        claude_skill = REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md"
        codex_skill = REPO_ROOT / "codex" / "skills" / "agent-director" / "SKILL.md"
        claude_links = check_repository.extract_core_doc_filenames(claude_skill)
        codex_links = check_repository.extract_core_doc_filenames(codex_skill)
        self.assertTrue(claude_links, "claude/SKILL.md has no links into core/")
        self.assertEqual(claude_links, codex_links)


if __name__ == "__main__":
    unittest.main()
