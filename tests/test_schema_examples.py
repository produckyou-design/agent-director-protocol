"""Schema validity, example conformance, and negative validation tests.

Runnable via `python -m unittest discover -s tests` from the repo root.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCHEMAS_DIR = REPO_ROOT / "schemas"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from jsonschema import Draft7Validator
    from jsonschema.exceptions import ValidationError
except ImportError:  # pragma: no cover - exercised only when dependency missing
    print(
        "ERROR: the 'jsonschema' package is required but is not installed.\n"
        "Install it with:\n\n"
        "    pip install jsonschema\n"
    )
    raise

import validate_schemas  # noqa: E402


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


TEN_CHECK_KEYS = [
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


def minimal_check() -> dict:
    return {"result": "pass", "evidence": "inspected the diff"}


def minimal_review_result() -> dict:
    return {
        "task_id": "T-001",
        "loop_number": 1,
        "verdict": "approved",
        "review_context": "director_review_of_worker_output",
        "checks": {key: minimal_check() for key in TEN_CHECK_KEYS},
    }


def minimal_implementation_report(status: str = "complete") -> dict:
    return {
        "task_id": "T-001",
        "assigned_model": "configured-worker-model",
        "model_ceiling": "configured-worker-model-ceiling",
        "assigned_effort": "medium",
        "spawn_authority": "director",
        "status": status,
        "summary": "Implemented the requested change end to end.",
        "files_changed": [],
        "tests_added": [],
        "test_executions": [
            {
                "command": "pytest",
                "exit_code": 0,
                "passed": 1,
                "failed": 0,
                "output_excerpt": "1 passed in 0.01s",
            }
        ],
        "completion_criteria_status": [
            {"criterion": "does the thing", "met": True, "evidence": "verified manually"}
        ],
        "out_of_scope_issues": [],
    }


def minimal_agent_composition_disclosure() -> dict:
    return {
        "director_model": "configured-director-model",
        "director_effort": "high",
        "director_model_source": "user_selected_session",
        "user_visible": True,
        "work_contract": {
            "objective": "Validate the widget correction with independent evidence.",
            "scope": ["src/widget.py"],
            "planned_contracts": 1,
            "planned_workers": 1,
            "worker_model": "configured-worker-model",
            "worker_reasoning_effort": "medium",
            "minimum_safe_rationale": "The isolated widget boundary cannot be absorbed by fewer existing contracts without losing the independently verifiable result.",
            "tests": ["python -m unittest"],
            "stop_conditions": ["Stop on unverifiable worker metadata or native capacity refusal."],
        },
        "subagent_count": 1,
        "subagents": [
            {
                "role": "implementer",
                "task": "T-001",
                "model": "configured-worker-model",
                "model_ceiling": "configured-worker-model-ceiling",
                "effort": "medium",
                "justification": "Isolated, independently verifiable outcome per the task contract.",
                "model_source": "native_custom_agent",
                "conflict_domains": {"files": ["src/widget.py"]},
            }
        ],
        "execution_mode": "sequential",
        "rescue_agent_available": True,
        "within_preapproved_range": True,
        "approval_status": "not_required",
        "spawn_budget": {
            "already_spawned_count": 0,
            "this_batch_count": 1,
            "total_after_spawn": 1,
            "capacity_source": "observed_native_runtime",
            "capacity_known": False,
        },
    }


def minimal_takeover_record() -> dict:
    return {
        "task_id": "T-001",
        "original_requirement": "Implement the widget resize handler.",
        "first_failure_evidence": "Test run showed AttributeError on resize().",
        "first_revision_instruction": "Fix the AttributeError in resize() per traceback above.",
        "second_failure_evidence": "Second run still throws AttributeError, unchanged.",
        "second_revision_instruction": "Re-read resize() signature and fix the call site.",
        "repeated_failure_cause": "Implementer keeps calling a removed method name.",
        "takeover_justification": "Two full revision loops both failed on the same root cause.",
        "files_to_modify": ["src/widget.py"],
        "modification_scope": "Only the resize() method body in src/widget.py.",
    }


class TestSchemasAreValidDraft7(unittest.TestCase):
    def test_all_schemas_pass_check_schema(self):
        schema_files = sorted(SCHEMAS_DIR.glob("*.schema.json"))
        self.assertTrue(schema_files, f"no schema files found in {SCHEMAS_DIR}")
        for schema_path in schema_files:
            with self.subTest(schema=schema_path.name):
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                Draft7Validator.check_schema(schema)


class TestExamplesValidateAgainstSchemas(unittest.TestCase):
    def test_every_example_validates(self):
        oks, failures = validate_schemas.run(REPO_ROOT)
        self.assertEqual(failures, [], f"validate_schemas.run() reported failures: {failures}")
        self.assertTrue(oks, "expected at least one successful validation")


class TestNegativeValidation(unittest.TestCase):
    def test_review_result_missing_a_check_key_fails(self):
        schema = load_schema("review-result.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_review_result()
        # Sanity: the well-formed instance must validate first.
        validator.validate(instance)

        for missing_key in TEN_CHECK_KEYS:
            with self.subTest(missing_key=missing_key):
                broken = copy.deepcopy(instance)
                del broken["checks"][missing_key]
                with self.assertRaises(ValidationError):
                    validator.validate(broken)

    def test_implementation_report_complete_with_empty_test_executions_fails(self):
        schema = load_schema("implementation-report.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_implementation_report(status="complete")
        validator.validate(instance)  # sanity: valid as-is

        broken = copy.deepcopy(instance)
        broken["test_executions"] = []
        with self.assertRaises(ValidationError):
            validator.validate(broken)

    def test_agent_composition_disclosure_subagent_missing_justification_fails(self):
        schema = load_schema("agent-composition-disclosure.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_agent_composition_disclosure()
        validator.validate(instance)  # sanity: valid as-is

        broken = copy.deepcopy(instance)
        del broken["subagents"][0]["justification"]
        with self.assertRaises(ValidationError):
            validator.validate(broken)

    def test_agent_composition_disclosure_out_of_range_without_approval_status_fails(self):
        schema = load_schema("agent-composition-disclosure.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_agent_composition_disclosure()
        instance["within_preapproved_range"] = False
        instance["approval_status"] = "pending"
        validator.validate(instance)  # sanity: valid with approval_status present

        broken = copy.deepcopy(instance)
        del broken["approval_status"]
        with self.assertRaises(ValidationError):
            validator.validate(broken)

    def test_takeover_record_missing_second_failure_evidence_fails(self):
        schema = load_schema("takeover-record.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_takeover_record()
        validator.validate(instance)  # sanity: valid as-is

        broken = copy.deepcopy(instance)
        del broken["second_failure_evidence"]
        with self.assertRaises(ValidationError):
            validator.validate(broken)


if __name__ == "__main__":
    unittest.main()
