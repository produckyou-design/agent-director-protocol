#!/usr/bin/env python3
"""Validate schemas/*.schema.json and every examples/**/*.json against them.

Steps:
  1. Every schemas/*.schema.json must parse as JSON and pass
     jsonschema.Draft7Validator.check_schema.
  2. Every examples/**/*.json is mapped to a schema by a filename substring:
       task-contract         -> task-contract.schema.json
       implementation-report -> implementation-report.schema.json
       review-result         -> review-result.schema.json
       failure-loop          -> failure-loop.schema.json
       takeover-record       -> takeover-record.schema.json
     An example JSON file whose name matches none of these substrings is a
     failure (unmapped example).

Exit codes: 0 = pass, 1 = failure, 2 = jsonschema is not installed.
@author Son Nguyen <hoangson091104@gmail.com>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from validate_dispatch_plan import validate_dispatch_plan

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    print(
        "ERROR: the 'jsonschema' package is required but is not installed.\n"
        "Install it with:\n\n"
        "    pip install jsonschema\n",
        file=sys.stderr,
    )
    sys.exit(2)


FILENAME_TO_SCHEMA = [
    ("agent-composition", "agent-composition-disclosure.schema.json"),
    ("task-contract", "task-contract.schema.json"),
    ("implementation-report", "implementation-report.schema.json"),
    ("review-result", "review-result.schema.json"),
    ("failure-loop", "failure-loop.schema.json"),
    ("takeover-record", "takeover-record.schema.json"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def schema_for_filename(name: str) -> str | None:
    for substring, schema_name in FILENAME_TO_SCHEMA:
        if substring in name:
            return schema_name
    return None


def run(root: Path) -> tuple[list[str], list[str]]:
    """Returns (oks, failures) as lists of human-readable messages."""
    oks: list[str] = []
    failures: list[str] = []

    schemas_dir = root / "schemas"
    schema_files = sorted(schemas_dir.glob("*.schema.json"))
    if not schema_files:
        failures.append(f"no *.schema.json files found under {schemas_dir}")
        return oks, failures

    loaded_schemas: dict[str, dict] = {}
    for schema_path in schema_files:
        rel = schema_path.relative_to(root)
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{rel}: invalid JSON ({exc})")
            continue
        try:
            Draft7Validator.check_schema(schema)
        except jsonschema.exceptions.SchemaError as exc:
            failures.append(f"{rel}: not a valid draft-07 schema ({exc.message})")
            continue
        loaded_schemas[schema_path.name] = schema
        oks.append(f"{rel}: valid JSON, valid draft-07 schema")

    examples_dir = root / "examples"
    example_files = sorted(examples_dir.glob("**/*.json")) if examples_dir.is_dir() else []
    if not example_files:
        failures.append(f"no example JSON files found under {examples_dir}")

    for example_path in example_files:
        rel = example_path.relative_to(root)
        schema_name = schema_for_filename(example_path.name)
        if schema_name is None:
            failures.append(
                f"{rel}: filename does not match any known schema substring "
                f"({[s for s, _ in FILENAME_TO_SCHEMA]})"
            )
            continue
        if schema_name not in loaded_schemas:
            failures.append(f"{rel}: mapped schema {schema_name} was not successfully loaded")
            continue

        try:
            instance = json.loads(example_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{rel}: invalid JSON ({exc})")
            continue

        validator = Draft7Validator(loaded_schemas[schema_name])
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        if errors:
            first = errors[0]
            path = "/".join(str(p) for p in first.path) or "<root>"
            failures.append(
                f"{rel}: fails {schema_name} at '{path}': {first.message}"
                + (f" ({len(errors) - 1} more error(s))" if len(errors) > 1 else "")
            )
        else:
            if schema_name == "agent-composition-disclosure.schema.json":
                semantic_errors = validate_dispatch_plan(instance, str(rel))
                if semantic_errors:
                    failures.extend(semantic_errors)
                    continue
            oks.append(f"{rel}: valid against {schema_name}")

    return oks, failures


def main() -> int:
    root = repo_root()
    oks, failures = run(root)

    for ok in oks:
        print(f"OK   {ok}")
    for failure in failures:
        print(f"FAIL {failure}")

    print(f"\n{len(oks)} passed, {len(failures)} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
