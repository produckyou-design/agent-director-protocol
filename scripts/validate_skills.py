#!/usr/bin/env python3
"""Validate the platform skill trees (claude/, codex/) for agent-director-protocol.

For each platform directory:
  - skills/agent-director/SKILL.md exists
  - SKILL.md has YAML frontmatter with a non-empty `name` and a non-empty,
    single-line `description`
  - name == "agent-director"
  - references/ contains exactly: task-template.md, review-template.md,
    revision-template.md, takeover-template.md
  - INSTALL.md exists
  - profiles/*.yaml exists (at least one .yaml file)

Exit codes: 0 = all checks passed, 1 = at least one check failed,
2 = a required dependency is missing (not used by this script, kept for
consistency with the other validators).

No third-party dependencies; frontmatter is parsed with a small hand-rolled
parser (no PyYAML) since only flat `key: value` pairs are needed here.
"""

from __future__ import annotations

import sys
from pathlib import Path

PLATFORMS = ["claude", "codex"]
REQUIRED_REFERENCE_FILES = {
    "task-template.md",
    "review-template.md",
    "revision-template.md",
    "takeover-template.md",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_frontmatter(text: str) -> tuple[dict, list[str]]:
    """Parse a minimal YAML frontmatter block of flat `key: value` pairs.

    Returns (fields, errors). `fields[key]` is a string. If a key's value
    continues onto following indented/blank lines (a YAML block scalar or
    multi-line value), the joined continuation is stored so callers can
    detect and reject non-single-line values.
    """
    errors: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        errors.append("file does not start with a '---' frontmatter fence")
        return {}, errors

    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
    if end_index is None:
        errors.append("frontmatter opening '---' has no closing '---'")
        return {}, errors

    block = lines[1:end_index]
    fields: dict[str, str] = {}
    current_key = None
    for raw_line in block:
        if not raw_line.strip():
            continue
        if raw_line[:1] not in (" ", "\t") and ":" in raw_line:
            key, _, value = raw_line.partition(":")
            key = key.strip()
            value = value.strip()
            # Strip a single layer of matching quotes, if present.
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            fields[key] = value
            current_key = key
        else:
            # Continuation / indented line: append to the current key so
            # multi-line values are detectable (and thus rejectable).
            if current_key is not None:
                fields[current_key] += "\n" + raw_line.strip()

    return fields, errors


def validate_platform(platform_dir: Path, platform: str) -> list[str]:
    failures: list[str] = []
    skill_dir = platform_dir / "skills" / "agent-director"
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        failures.append(f"[{platform}] missing {skill_md}")
    else:
        text = skill_md.read_text(encoding="utf-8")
        fields, fm_errors = parse_frontmatter(text)
        for err in fm_errors:
            failures.append(f"[{platform}] {skill_md}: {err}")

        name = fields.get("name")
        if not name:
            failures.append(f"[{platform}] {skill_md}: frontmatter missing non-empty 'name'")
        elif name != "agent-director":
            failures.append(
                f"[{platform}] {skill_md}: frontmatter name == {name!r}, expected 'agent-director'"
            )

        description = fields.get("description")
        if not description:
            failures.append(f"[{platform}] {skill_md}: frontmatter missing non-empty 'description'")
        elif "\n" in description:
            failures.append(f"[{platform}] {skill_md}: frontmatter 'description' must be single-line")

    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        failures.append(f"[{platform}] missing directory {references_dir}")
    else:
        actual = {p.name for p in references_dir.iterdir() if p.is_file()}
        if actual != REQUIRED_REFERENCE_FILES:
            missing = REQUIRED_REFERENCE_FILES - actual
            extra = actual - REQUIRED_REFERENCE_FILES
            detail = []
            if missing:
                detail.append(f"missing {sorted(missing)}")
            if extra:
                detail.append(f"unexpected {sorted(extra)}")
            failures.append(
                f"[{platform}] {references_dir} must contain exactly {sorted(REQUIRED_REFERENCE_FILES)}: "
                + "; ".join(detail)
            )

    install_md = platform_dir / "INSTALL.md"
    if not install_md.is_file():
        failures.append(f"[{platform}] missing {install_md}")

    profiles_dir = platform_dir / "profiles"
    if not profiles_dir.is_dir():
        failures.append(f"[{platform}] missing directory {profiles_dir}")
    else:
        yaml_files = list(profiles_dir.glob("*.yaml"))
        if not yaml_files:
            failures.append(f"[{platform}] {profiles_dir} must contain at least one *.yaml profile")

    return failures


def run(root: Path) -> list[str]:
    failures: list[str] = []
    for platform in PLATFORMS:
        platform_dir = root / platform
        if not platform_dir.is_dir():
            failures.append(f"[{platform}] missing platform directory {platform_dir}")
            continue
        failures.extend(validate_platform(platform_dir, platform))
    return failures


def main() -> int:
    root = repo_root()
    failures = run(root)

    if not failures:
        for platform in PLATFORMS:
            print(f"OK   [{platform}] skill tree valid")
        print(f"\n{len(PLATFORMS)} platform(s) checked, 0 failure(s).")
        return 0

    for failure in failures:
        print(f"FAIL {failure}")
    print(f"\n{len(failures)} failure(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
