#!/usr/bin/env python3
"""Semantically validate the cross-field rules for an ADP dispatch plan.

JSON Schema draft-07 validates individual field shapes, but it cannot prove
pairwise glob disjointness or the capacity formula.  This module is the
repository's deterministic semantic validator for those runtime-facing rules.
@author Son Nguyen <hoangson091104@gmail.com>
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from typing import Any


CONFLICT_DOMAIN_KEYS = (
    "files",
    "code_regions",
    "interfaces",
    "schemas",
    "generated_artifacts",
    "build_targets",
    "shared_configs",
    "state_stores",
    "data_structures",
    "db_entities",
    "user_flows",
)

DISPATCH_FIELDS = (
    "independent_groups",
    "dependency_edges",
    "capacity_source",
    "observed_capacity",
    "why_fewer_workers_cannot_absorb",
    "write_isolation",
)


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


_GLOB_UNIVERSE = frozenset(chr(code) for code in range(32, 127)) | frozenset({"/", "\\"})


def _glob_tokens(pattern: str) -> list[tuple[str, frozenset[str] | None]]:
    """Tokenize the shell-style glob subset used in conflict-domain paths."""

    tokens: list[tuple[str, frozenset[str] | None]] = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            while index + 1 < len(pattern) and pattern[index + 1] == "*":
                index += 1
            tokens.append(("star", None))
            index += 1
            continue
        if char == "?":
            tokens.append(("set", _GLOB_UNIVERSE))
            index += 1
            continue
        if char == "[":
            closing = pattern.find("]", index + 1)
            if closing != -1:
                body = pattern[index + 1 : closing]
                negate = body[:1] in {"!", "^"}
                if negate:
                    body = body[1:]
                chars: set[str] = set()
                cursor = 0
                while cursor < len(body):
                    if cursor + 2 < len(body) and body[cursor + 1] == "-":
                        chars.update(chr(code) for code in range(ord(body[cursor]), ord(body[cursor + 2]) + 1))
                        cursor += 3
                    else:
                        chars.add(body[cursor])
                        cursor += 1
                if chars:
                    values = _GLOB_UNIVERSE - chars if negate else frozenset(chars)
                    tokens.append(("set", frozenset(values)))
                    index = closing + 1
                    continue
        tokens.append(("set", frozenset({char})))
        index += 1
    return tokens


def _tokens_can_consume(left: tuple[str, frozenset[str] | None], right: tuple[str, frozenset[str] | None]) -> bool:
    if left[0] == "star" or right[0] == "star":
        return True
    return bool((left[1] or frozenset()) & (right[1] or frozenset()))


def _globs_intersect(left: str, right: str) -> bool:
    """Return whether two shell-style globs have at least one common string."""

    left_tokens = _glob_tokens(left)
    right_tokens = _glob_tokens(right)
    pending = deque([(0, 0)])
    seen: set[tuple[int, int]] = set()
    while pending:
        left_index, right_index = pending.popleft()
        state = (left_index, right_index)
        if state in seen:
            continue
        seen.add(state)
        if left_index == len(left_tokens) and right_index == len(right_tokens):
            return True

        if left_index < len(left_tokens) and left_tokens[left_index][0] == "star":
            pending.append((left_index + 1, right_index))
        if right_index < len(right_tokens) and right_tokens[right_index][0] == "star":
            pending.append((left_index, right_index + 1))

        if left_index >= len(left_tokens) or right_index >= len(right_tokens):
            continue
        left_token = left_tokens[left_index]
        right_token = right_tokens[right_index]
        if left_token[0] == "star" and right_token[0] == "star":
            pending.append((left_index, right_index))
        elif left_token[0] == "star":
            pending.append((left_index, right_index + 1))
        elif right_token[0] == "star":
            pending.append((left_index + 1, right_index))
        elif _tokens_can_consume(left_token, right_token):
            pending.append((left_index + 1, right_index + 1))
    return False


def _domains_overlap(left: list[str], right: list[str]) -> bool:
    """Return whether exact names or arbitrary declared glob patterns intersect."""

    return any(_globs_intersect(a, b) for a in left for b in right)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _required_dispatch_errors(contract: Mapping[str, Any]) -> list[str]:
    return [
        f"work contract must disclose {field}"
        for field in DISPATCH_FIELDS
        if field not in contract
    ]


def validate_work_contract(
    contract: Mapping[str, Any],
    *,
    execution_mode: str,
    justification: str = "",
    source: str = "<work_contract>",
) -> list[str]:
    """Return semantic dispatch errors for one visible ``work_contract``.

    Historical sequential disclosures may omit the newer dispatch fields.  A
    current parallel disclosure, or any disclosure that starts supplying the
    dispatch plan, must provide the complete set and passes the cross-field
    checks below.
    """

    errors: list[str] = []
    planned_workers = contract.get("planned_workers")
    has_plan = any(field in contract for field in DISPATCH_FIELDS)
    active = execution_mode == "parallel" or has_plan or (
        _is_int(planned_workers) and planned_workers > 1
    )
    if not active:
        return errors

    errors.extend(_required_dispatch_errors(contract))

    groups = contract.get("independent_groups", [])
    if not isinstance(groups, list):
        errors.append("independent_groups must be an array")
        groups = []

    if execution_mode == "parallel" and len(groups) < 2:
        errors.append("parallel dispatch requires at least two independent groups")
    if execution_mode == "sequential" and not groups:
        errors.append("a current dispatch plan requires at least one independent group")

    group_ids: list[str] = []
    for group in groups:
        if not isinstance(group, Mapping):
            errors.append("every independent group must be an object")
            continue
        group_id = group.get("group_id")
        if not isinstance(group_id, str) or not group_id:
            errors.append("every independent group must disclose a non-empty group_id")
        elif group_id in group_ids:
            errors.append(f"duplicate independent group id: {group_id}")
        else:
            group_ids.append(group_id)
        if not group.get("scope"):
            errors.append("every group must disclose a bounded scope")
        if group.get("independently_verifiable") is not True:
            errors.append("every group must be independently verifiable")
        if not isinstance(group.get("conflict_domains"), Mapping):
            errors.append("every group must disclose conflict_domains")

    dependency_edges = contract.get("dependency_edges", [])
    if not isinstance(dependency_edges, list):
        errors.append("dependency_edges must be an array")
        dependency_edges = []
    for edge in dependency_edges:
        if not isinstance(edge, Mapping):
            errors.append("every dependency edge must be an object")
            continue
        for endpoint in ("from", "to"):
            if edge.get(endpoint) not in group_ids:
                errors.append(f"dependency edge {endpoint} must name a known group")
    if execution_mode == "parallel" and dependency_edges:
        errors.append("parallel dispatch requires empty dependency_edges")

    if execution_mode == "parallel":
        for index, left in enumerate(groups):
            if not isinstance(left, Mapping):
                continue
            left_domains = left.get("conflict_domains")
            if not isinstance(left_domains, Mapping):
                continue
            for right in groups[index + 1 :]:
                if not isinstance(right, Mapping):
                    continue
                right_domains = right.get("conflict_domains")
                if not isinstance(right_domains, Mapping):
                    continue
                for key in CONFLICT_DOMAIN_KEYS:
                    if _domains_overlap(
                        _strings(left_domains.get(key)),
                        _strings(right_domains.get(key)),
                    ):
                        errors.append(f"groups conflict in {key}")

    capacity_source = contract.get("capacity_source")
    observed_capacity = contract.get("observed_capacity")
    if capacity_source == "unknown":
        if observed_capacity is not None:
            errors.append("unknown capacity must use observed_capacity=null")
        if planned_workers != 1:
            errors.append("unknown capacity requires one sequential worker")
        if execution_mode == "parallel":
            errors.append("parallel dispatch requires known native capacity")
    elif not _is_int(observed_capacity) or observed_capacity <= 0:
        errors.append("known capacity must be a positive integer")
    elif execution_mode == "parallel":
        if observed_capacity < 2:
            errors.append("parallel dispatch requires native capacity of at least two")
        expected = min(len(groups), observed_capacity)
        if planned_workers != expected:
            errors.append(
                f"planned_workers must equal min({len(groups)}, {observed_capacity})"
            )
    elif execution_mode == "sequential" and planned_workers != 1:
        errors.append("sequential dispatch requires one worker")

    if execution_mode == "parallel" and contract.get("write_isolation") not in {
        "isolated",
        "read_only",
    }:
        errors.append(
            "parallel dispatch requires write_isolation=isolated or write_isolation=read_only"
        )

    rationale = (justification or str(contract.get("minimum_safe_rationale", ""))).casefold().strip()
    if execution_mode == "parallel":
        if rationale in {"for speed", "for parallelism", "for efficiency", "faster", "parallel"}:
            errors.append("speed-only or vague parallelism justification is not accepted")
        required_evidence = ("independent", "conflict", "dependency", "capacity")
        if rationale and not all(term in rationale for term in required_evidence):
            errors.append(
                "justification must identify independent groups, domains, dependencies, and capacity"
            )

    if errors:
        return [f"{source}: {error}" for error in errors]
    return []


def validate_dispatch_plan(instance: Mapping[str, Any], source: str = "<instance>") -> list[str]:
    """Validate a complete agent-composition disclosure's dispatch semantics."""

    if not isinstance(instance, Mapping):
        return [f"{source}: disclosure must be an object"]
    contract = instance.get("work_contract")
    if not isinstance(contract, Mapping):
        return [f"{source}: work_contract must be an object"]

    execution_mode = instance.get("execution_mode")
    if execution_mode not in {"parallel", "sequential"}:
        return []

    planned_workers = contract.get("planned_workers")
    if planned_workers == 0 and contract.get("read_only") is True:
        return []

    errors = validate_work_contract(
        contract,
        execution_mode=execution_mode,
        source=source,
    )

    if execution_mode == "parallel":
        subagent_count = instance.get("subagent_count")
        subagents = instance.get("subagents")
        if not isinstance(subagents, list) or len(subagents) != subagent_count:
            errors.append(
                f"{source}: subagents length must equal subagent_count for a parallel batch"
            )
        if subagent_count != planned_workers:
            errors.append(
                f"{source}: subagent_count must equal planned_workers for a parallel batch"
            )
    return errors
