"""Schema validity, example conformance, and negative validation tests.

Runnable via `python -m unittest discover -s tests` from the repo root.
@author Son Nguyen <hoangson091104@gmail.com>
"""

from __future__ import annotations

import copy
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
from validate_dispatch_plan import (  # noqa: E402
    validate_dispatch_plan,
    validate_work_contract,
)


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
        "phase": "spawn",
        "user_visible": True,
        "work_contract": {
            "objective": "Validate the widget correction with independent evidence.",
            "scope": ["src/widget.py"],
            "planned_contracts": 1,
            "planned_workers": 1,
            "worker_model": "configured-worker-model",
            "worker_reasoning_effort": "medium",
            "minimum_safe_rationale": "The isolated widget boundary cannot be absorbed by fewer existing contracts without losing the independently verifiable result.",
            "independent_groups": [
                {
                    "group_id": "G-001",
                    "scope": ["src/widget.py"],
                    "independently_verifiable": True,
                    "conflict_domains": {
                        "files": ["src/widget.py"],
                        "code_regions": ["Widget.resize"],
                        "interfaces": [],
                        "schemas": [],
                        "generated_artifacts": [],
                        "shared_configs": [],
                        "state_stores": [],
                        "data_structures": [],
                        "db_entities": [],
                        "build_targets": [],
                        "user_flows": ["widget-resize"],
                    },
                }
            ],
            "dependency_edges": [],
            "capacity_source": "observed_native_runtime",
            "observed_capacity": 1,
            "write_isolation": "sequential",
            "why_fewer_workers_cannot_absorb": "One worker is the minimum safe owner of this isolated write domain and its independent evidence.",
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
        "user_authorization_evidence": "User explicitly authorized direct implementation after the takeover disclosure.",
        "files_to_modify": ["src/widget.py"],
        "modification_scope": "Only the resize() method body in src/widget.py.",
    }


def validate_parallel_work_contract(contract: dict, justification: str) -> list[str]:
    """Use the production semantic validator, not a test-only approximation."""

    return validate_work_contract(
        contract,
        execution_mode="parallel",
        justification=justification,
    )


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

    def test_legacy_agent_composition_without_dispatch_plan_fields_remains_compatible(self):
        schema = load_schema("agent-composition-disclosure.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_agent_composition_disclosure()
        for field in (
            "independent_groups",
            "dependency_edges",
            "capacity_source",
            "observed_capacity",
            "why_fewer_workers_cannot_absorb",
        ):
            del instance["work_contract"][field]
        validator.validate(instance)

    def test_task_start_zero_workers_requires_explicit_read_only_marker(self):
        schema = load_schema("agent-composition-disclosure.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_agent_composition_disclosure()
        instance["phase"] = "task_start"
        instance["work_contract"]["planned_workers"] = 0
        instance["work_contract"]["read_only"] = True
        instance["subagent_count"] = 0
        instance["subagents"] = []
        instance["spawn_budget"]["this_batch_count"] = 0
        validator.validate(instance)

        broken = copy.deepcopy(instance)
        del broken["work_contract"]["read_only"]
        with self.assertRaises(ValidationError):
            validator.validate(broken)

    def test_addition_requires_scope_task_basis_absorption_reason_and_new_marker(self):
        schema = load_schema("agent-composition-disclosure.schema.json")
        validator = Draft7Validator(schema)

        instance = minimal_agent_composition_disclosure()
        instance["phase"] = "addition"
        instance["addition"] = {
            "changed_scope": ["tests/test_schema_examples.py"],
            "change_summary": "Add an independent schema regression case.",
            "added_worker_task": "Review the new disclosure phase contract.",
            "addition_basis": "mandatory_independent_review",
            "why_existing_workers_cannot_absorb": "The existing implementer cannot absorb the independent review without reviewing its own diff.",
            "new_disclosure": True,
        }
        validator.validate(instance)

        broken = copy.deepcopy(instance)
        del broken["addition"]["why_existing_workers_cannot_absorb"]
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


class TestDeterministicParallelDispatch(unittest.TestCase):
    def _parallel_contract(self) -> dict:
        return {
            "independent_groups": [
                {
                    "group_id": "G-001",
                    "scope": ["src/auth/*"],
                    "independently_verifiable": True,
                    "conflict_domains": {
                        "files": ["src/auth/*"],
                        "interfaces": ["POST /login"],
                    },
                },
                {
                    "group_id": "G-002",
                    "scope": ["src/session/*"],
                    "independently_verifiable": True,
                    "conflict_domains": {
                        "files": ["src/session/*"],
                        "interfaces": ["SessionService"],
                    },
                },
            ],
            "dependency_edges": [],
            "planned_workers": 2,
            "capacity_source": "observed_native_runtime",
            "observed_capacity": 3,
            "write_isolation": "isolated",
            "why_fewer_workers_cannot_absorb": "Independent completion and evidence paths require separate workers.",
        }

    def test_parallel_plan_uses_independent_groups_and_capacity_minimum(self):
        contract = self._parallel_contract()
        self.assertEqual(
            validate_parallel_work_contract(
                contract,
                "Two independent groups have disjoint conflict domains, empty dependency edges, and observed capacity supports separate evidence.",
            ),
            [],
        )

    def test_speed_only_or_vague_parallelism_justification_is_rejected(self):
        contract = self._parallel_contract()
        for justification in ("for speed", "parallel", "for efficiency"):
            with self.subTest(justification=justification):
                self.assertTrue(validate_parallel_work_contract(contract, justification))

    def test_parallel_plan_requires_dispatch_disclosure_fields(self):
        contract = self._parallel_contract()
        del contract["capacity_source"]
        del contract["why_fewer_workers_cannot_absorb"]
        errors = validate_parallel_work_contract(
            contract,
            "Two independent groups have disjoint conflict domains, empty dependency edges, and observed capacity supports separate evidence.",
        )
        self.assertTrue(any("work contract must disclose capacity_source" in error for error in errors))
        self.assertTrue(any("work contract must disclose why_fewer_workers_cannot_absorb" in error for error in errors))

    def test_unknown_capacity_uses_one_worker_without_inventing_a_cap(self):
        contract = self._parallel_contract()
        contract["observed_capacity"] = None
        contract["capacity_source"] = "unknown"
        contract["planned_workers"] = 1
        parallel_errors = validate_parallel_work_contract(
            contract,
            "Two independent groups have disjoint conflict domains, empty dependency edges, and unknown capacity requires a conservative sequential fallback.",
        )
        self.assertTrue(parallel_errors)
        self.assertIn("parallel dispatch requires known native capacity", " ".join(parallel_errors))

        self.assertEqual(
            validate_work_contract(
                contract,
                execution_mode="sequential",
                justification="Unknown capacity requires a conservative sequential fallback.",
            ),
            [],
        )

        contract["planned_workers"] = 2
        self.assertTrue(
            validate_work_contract(
                contract,
                execution_mode="sequential",
                justification="Unknown capacity requires a conservative sequential fallback.",
            ),
        )

    def test_parallel_plan_rejects_one_group_conflicts_dependencies_and_wrong_capacity(self):
        cases = {
            "one group": {
                "independent_groups": [self._parallel_contract()["independent_groups"][0]],
                "dependency_edges": [],
                "planned_workers": 1,
                "observed_capacity": 4,
            },
            "overlap": {
                **copy.deepcopy(self._parallel_contract()),
                "planned_workers": 2,
            },
            "dependency": {
                **copy.deepcopy(self._parallel_contract()),
                "dependency_edges": [{"from": "G-001", "to": "G-002"}],
            },
            "capacity": {
                **copy.deepcopy(self._parallel_contract()),
                "planned_workers": 3,
            },
        }
        cases["overlap"]["independent_groups"][1]["conflict_domains"]["files"] = ["src/auth/session.py"]

        for name, contract in cases.items():
            with self.subTest(case=name):
                self.assertTrue(
                    validate_parallel_work_contract(
                        contract,
                        "Two independent groups have disjoint conflict domains, empty dependency edges, and observed capacity supports separate evidence.",
                    ),
                )

    def test_parallel_plan_rejects_intersecting_globs_not_contained_in_each_other(self):
        contract = self._parallel_contract()
        contract["independent_groups"][0]["conflict_domains"]["files"] = ["src/*/test.py"]
        contract["independent_groups"][1]["conflict_domains"]["files"] = ["src/auth/*"]
        errors = validate_parallel_work_contract(
            contract,
            "Two independent groups have disjoint conflict domains, empty dependency edges, and observed capacity supports separate evidence.",
        )
        self.assertIn("groups conflict in files", " ".join(errors))

    def test_real_composition_example_uses_schema_and_semantic_validation(self):
        instance = json.loads(
            (REPO_ROOT / "examples" / "new-project" / "00-agent-composition-disclosure.json").read_text(
                encoding="utf-8"
            )
        )
        schema = load_schema("agent-composition-disclosure.schema.json")
        Draft7Validator(schema).validate(instance)
        self.assertEqual(validate_dispatch_plan(instance), [])

    def test_schema_shape_valid_capacity_and_overlap_fail_semantic_validation(self):
        instance = json.loads(
            (REPO_ROOT / "examples" / "new-project" / "00-agent-composition-disclosure.json").read_text(
                encoding="utf-8"
            )
        )
        schema = load_schema("agent-composition-disclosure.schema.json")
        validator = Draft7Validator(schema)

        wrong_capacity = copy.deepcopy(instance)
        wrong_capacity["work_contract"]["planned_workers"] = 3
        validator.validate(wrong_capacity)
        self.assertTrue(validate_dispatch_plan(wrong_capacity))

        overlap = copy.deepcopy(instance)
        overlap["work_contract"]["independent_groups"][1]["conflict_domains"]["files"] = [
            "internal/health/handler.go"
        ]
        validator.validate(overlap)
        self.assertTrue(validate_dispatch_plan(overlap))

    def test_parallel_plan_rejects_subagent_array_cardinality_mismatch(self):
        instance = json.loads(
            (REPO_ROOT / "examples" / "new-project" / "00-agent-composition-disclosure.json").read_text(
                encoding="utf-8"
            )
        )
        instance["subagents"] = []
        errors = validate_dispatch_plan(instance)
        self.assertIn("subagents length must equal subagent_count", " ".join(errors))

    def test_policy_documents_state_the_rule_and_not_the_old_blanket_reason(self):
        policy_files = [
            REPO_ROOT / "core" / "CONCURRENCY-RULES.md",
            REPO_ROOT / "core" / "DELEGATION-PROTOCOL.md",
            REPO_ROOT / "claude" / "skills" / "agent-director" / "SKILL.md",
            REPO_ROOT / "README.md",
            REPO_ROOT / "README.ko.md",
        ]
        for path in policy_files:
            source = path.read_text(encoding="utf-8")
            with self.subTest(policy_file=path.relative_to(REPO_ROOT)):
                self.assertIn("independent_groups", source)
                self.assertIn("dependency_edges", source)
                self.assertIn("planned_workers", source)
                self.assertIn("capacity_source", source)
                self.assertIn("write_isolation", source)
                self.assertIn("why_fewer_workers_cannot_absorb", source)
                self.assertRegex(source, re.compile(r"two or more|two or more independently|두 개 이상의|독립적으로", re.I))
                self.assertRegex(source, r"disjoint|pairwise|쌍별|분리")
                self.assertRegex(source, r"min\(")
                self.assertRegex(source, r"unknown|capacity.*알 수 없|unknown이면")

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
