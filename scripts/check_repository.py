#!/usr/bin/env python3
"""Single entry point for validating the agent-director-protocol repository.

Runs, in order:
  1. validate_skills   - platform skill tree structure
  2. validate_schemas   - schema validity + example conformance
  3. verify_links       - markdown relative link resolution
  4. sensitive-data scan
  5. residue scan (build-environment leakage)
  6. install-doc path check
  7. platform consistency check
  8. `python -m unittest discover -s tests`

Prints a PASS/FAIL summary table and exits non-zero if any section failed.

Usage:
    python scripts/check_repository.py [--skip-tests]

@author Son Nguyen <hoangson091104@gmail.com>

Exit codes: 0 = all sections passed, 1 = at least one section failed,
2 = the jsonschema dependency is missing (propagated from validate_schemas).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Make sibling scripts importable regardless of cwd.
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_schemas  # noqa: E402
import validate_skills  # noqa: E402
import verify_links  # noqa: E402

def _skip_dir(name: str) -> bool:
    """Skip caches and hidden state/tooling directories, but keep .github."""
    return name == "__pycache__" or (name.startswith(".") and name != ".github")


# This script's own filename is allowlisted out of the sensitive-data and
# residue scans below: it necessarily contains the pattern *definitions*
# (forbidden-string entries and token-pattern fragments) that the scan looks
# for, without those definitions being actual leaked secrets or
# build-environment residue.
SELF_FILENAME = Path(__file__).name

# ---------------------------------------------------------------------------
# Sensitive-data scan
# ---------------------------------------------------------------------------
# Token patterns are built by string concatenation so this file's own source
# never contains the literal regex text a naive text-search might flag.
_TOKEN_PATTERNS = [
    ("GitHub personal token (ghp_)", "gh" + "p_" + "[A-Za-z0-9]{20,}"),
    ("GitHub OAuth token (gho_)", "gh" + "o_" + "[A-Za-z0-9]{20,}"),
    ("GitHub fine-grained PAT", "github_" + "pat_" + "[A-Za-z0-9_]{20,}"),
    ("AWS access key", "AKIA" + "[0-9A-Z]{16}"),
    ("OpenAI-style secret key", "sk-" + "[A-Za-z0-9_-]{20,}"),
    ("Slack token", "xox" + "[baprs]-" + "[A-Za-z0-9-]{10,}"),
    (
        "Private key block",
        "-----BEGIN " + "(RSA |EC |OPENSSH )?" + "PRIVATE KEY" + "-----",
    ),
]

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
EMAIL_ALLOWLIST_SUFFIXES = ("@example.com", "@users.noreply.github.com")
AUTHOR_HEADER = "@author Son Nguyen <hoangson091104@gmail.com>"

ABS_PATH_PATTERNS = [
    ("Windows user path", r"C:\\Users\\[^\\\s\"']+"),
    ("Linux home path", r"/home/[^/\s\"']+/"),
    ("macOS user path", r"/Users/[^/\s\"']+/"),
]

# ---------------------------------------------------------------------------
# Residue scan (build-environment leakage)
# ---------------------------------------------------------------------------
# Default forbidden strings: generic indicators that content leaked from a
# development scratch area into the repository. Machine- or project-specific
# names (a private tool name, a local directory name) belong in a local,
# git-ignored denylist instead of being committed here:
# scripts/residue-denylist.local.txt — one case-insensitive string per line,
# '#' comments and blank lines ignored.
RESIDUE_FORBIDDEN_STRINGS = ["scratchpad", "appdata\\local\\temp"]
RESIDUE_LOCAL_DENYLIST = Path(__file__).with_name("residue-denylist.local.txt")


def load_residue_strings() -> list[str]:
    strings = list(RESIDUE_FORBIDDEN_STRINGS)
    if RESIDUE_LOCAL_DENYLIST.is_file():
        for raw in RESIDUE_LOCAL_DENYLIST.read_text(encoding="utf-8").splitlines():
            entry = raw.strip()
            if entry and not entry.startswith("#"):
                strings.append(entry)
    return strings


# A drive-letter absolute path such as C:\Users\example\... or D:\build\...
# The negative lookbehind avoids matching a stray "<word-char>:\" that is
# actually part of an escape sequence inside a string literal (e.g. the text
# "with:\n" in a Python source string is not a path).
RESIDUE_DRIVE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:\\[^\s\"'<>|]+")


def iter_all_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(_skip_dir(part) for part in path.relative_to(root).parts[:-1]):
            continue
        yield path


def read_text_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8", errors="strict").splitlines()
    except (UnicodeDecodeError, OSError):
        return None


def scan_sensitive_data(root: Path) -> list[str]:
    findings: list[str] = []
    for path in iter_all_files(root):
        if path.name == SELF_FILENAME:
            continue
        lines = read_text_lines(path)
        if lines is None:
            continue
        rel = path.relative_to(root)
        for lineno, line in enumerate(lines, start=1):
            # The repository requires this exact non-secret authorship marker
            # on edited source files; do not treat that metadata as a leak.
            if line.strip() == AUTHOR_HEADER:
                continue
            for label, pattern in _TOKEN_PATTERNS:
                if re.search(pattern, line):
                    findings.append(f"{rel}:{lineno}: possible {label}")

            for match in re.finditer(EMAIL_PATTERN, line):
                email = match.group(0)
                if email.lower().endswith(EMAIL_ALLOWLIST_SUFFIXES):
                    continue
                findings.append(f"{rel}:{lineno}: email address found ({email})")

            for label, pattern in ABS_PATH_PATTERNS:
                if re.search(pattern, line):
                    findings.append(f"{rel}:{lineno}: absolute user path found ({label})")
    return findings


def scan_residue(root: Path) -> list[str]:
    findings: list[str] = []
    forbidden_strings = load_residue_strings()
    for path in iter_all_files(root):
        if path.name in (SELF_FILENAME, RESIDUE_LOCAL_DENYLIST.name):
            continue
        lines = read_text_lines(path)
        if lines is None:
            continue
        rel = path.relative_to(root)
        for lineno, line in enumerate(lines, start=1):
            lowered = line.lower()
            for forbidden in forbidden_strings:
                if forbidden.lower() in lowered:
                    findings.append(f"{rel}:{lineno}: forbidden string '{forbidden}' found")

            if RESIDUE_DRIVE_PATH_RE.search(line):
                findings.append(f"{rel}:{lineno}: possible build-environment path residue")
    return findings


def check_install_docs(root: Path) -> list[str]:
    failures: list[str] = []
    claude_install = root / "claude" / "INSTALL.md"

    if not claude_install.is_file():
        failures.append(f"missing {claude_install}")
    else:
        text = claude_install.read_text(encoding="utf-8")
        if ".claude/skills" not in text:
            failures.append(f"{claude_install} must mention '.claude/skills'")

    return failures


CORE_DOC_LINK_RE = re.compile(r"\[[^\]]*\]\(((?:\.\./)*core/([A-Za-z0-9_-]+\.md))[^)]*\)")


def extract_core_doc_filenames(skill_md: Path) -> set[str]:
    if not skill_md.is_file():
        return set()
    text = skill_md.read_text(encoding="utf-8")
    return {m.group(2) for m in CORE_DOC_LINK_RE.finditer(text)}


def check_platform_consistency(root: Path) -> list[str]:
    failures: list[str] = []

    claude_refs = root / "claude" / "skills" / "agent-director" / "references"
    claude_ref_files = {p.name for p in claude_refs.iterdir() if p.is_file()} if claude_refs.is_dir() else set()

    claude_skill = root / "claude" / "skills" / "agent-director" / "SKILL.md"
    claude_core_links = extract_core_doc_filenames(claude_skill)

    if not claude_core_links:
        failures.append(f"{claude_skill} has no links into core/ (expected the core doc set)")

    return failures


def run_unittests(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output


def print_section(title: str, failures: list[str]) -> bool:
    passed = not failures
    status = "PASS" if passed else "FAIL"
    print(f"\n--- {title}: {status} ---")
    for failure in failures:
        print(f"  FAIL {failure}")
    if passed:
        print("  OK   no issues found")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the `python -m unittest discover -s tests` step (used by the test suite itself).",
    )
    args = parser.parse_args()

    root = REPO_ROOT
    results: list[tuple[str, bool]] = []

    # 1. validate_skills
    skills_failures = validate_skills.run(root)
    results.append(("validate_skills", print_section("validate_skills", skills_failures)))

    # 2. validate_schemas (may exit(2) internally via ImportError at module
    # import time above; if we got this far, jsonschema is present).
    _, schema_failures = validate_schemas.run(root)
    results.append(("validate_schemas", print_section("validate_schemas", schema_failures)))

    # 3. verify_links
    link_failures = verify_links.run(root)
    results.append(("verify_links", print_section("verify_links", link_failures)))

    # 4. sensitive-data scan
    sensitive_findings = scan_sensitive_data(root)
    results.append(("sensitive-data scan", print_section("sensitive-data scan", sensitive_findings)))

    # 5. residue scan
    residue_findings = scan_residue(root)
    results.append(("residue scan", print_section("residue scan", residue_findings)))

    # 6. install-doc path check
    install_failures = check_install_docs(root)
    results.append(("install-doc path check", print_section("install-doc path check", install_failures)))

    # 7. platform consistency
    consistency_failures = check_platform_consistency(root)
    results.append(("platform consistency", print_section("platform consistency", consistency_failures)))

    # 8. unittest discovery
    if args.skip_tests:
        print("\n--- unittest discover -s tests: SKIPPED (--skip-tests) ---")
        results.append(("unittest discover -s tests", True))
    else:
        tests_ok, tests_output = run_unittests(root)
        print(f"\n--- unittest discover -s tests: {'PASS' if tests_ok else 'FAIL'} ---")
        print(tests_output)
        results.append(("unittest discover -s tests", tests_ok))

    print("\n=================== SUMMARY ===================")
    all_passed = True
    for name, passed in results:
        print(f"  {'PASS' if passed else 'FAIL':4s}  {name}")
        all_passed = all_passed and passed
    print("================================================")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
