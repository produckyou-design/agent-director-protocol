#!/usr/bin/env python3
"""Verify that relative markdown links across the repository resolve.

Scans every *.md file (skipping caches and hidden directories other than
.github), extracts
markdown links (both inline `[text](target)` and reference-style
`[label]: target` definitions), and for every relative target (i.e. not
starting with http://, https://, mailto:, or a bare '#' anchor) checks that
the target file/directory exists relative to the directory containing the
linking file. A '#anchor' suffix is stripped before the filesystem check.

Exit codes: 0 = all relative links resolve, 1 = at least one broken link.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

def _skip_dir(name: str) -> bool:
    """Skip caches and hidden state/tooling directories, but keep .github."""
    return name == "__pycache__" or (name.startswith(".") and name != ".github")

INLINE_LINK_RE = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
REFERENCE_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")

SKIP_PREFIXES = ("http://", "https://", "mailto:")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def iter_markdown_files(root: Path):
    for path in root.rglob("*.md"):
        if any(_skip_dir(part) for part in path.relative_to(root).parts[:-1]):
            continue
        yield path


def extract_links(line: str) -> list[str]:
    targets = [m.group(1) for m in INLINE_LINK_RE.finditer(line)]
    ref_match = REFERENCE_DEF_RE.match(line)
    if ref_match:
        targets.append(ref_match.group(1))
    return targets


def is_external_or_anchor_only(target: str) -> bool:
    if target.startswith(SKIP_PREFIXES):
        return True
    if target.startswith("#"):
        return True
    return False


def resolve_target(md_file: Path, target: str) -> Path:
    # Strip a trailing #anchor (but not a '#' that's part of the path itself,
    # which practically never happens for real filesystem paths here).
    path_part = target.split("#", 1)[0]
    # Strip any query string, defensively.
    path_part = path_part.split("?", 1)[0]
    return (md_file.parent / path_part).resolve()


def run(root: Path) -> list[str]:
    broken: list[str] = []
    for md_file in sorted(iter_markdown_files(root)):
        try:
            lines = md_file.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as exc:
            broken.append(f"{md_file.relative_to(root)}: could not read as UTF-8 ({exc})")
            continue

        for lineno, line in enumerate(lines, start=1):
            for target in extract_links(line):
                if is_external_or_anchor_only(target):
                    continue
                path_part = target.split("#", 1)[0].split("?", 1)[0]
                if not path_part:
                    continue
                resolved = resolve_target(md_file, target)
                if not resolved.exists():
                    rel = md_file.relative_to(root)
                    broken.append(f"{rel}:{lineno}: broken link '{target}' -> {resolved} does not exist")
    return broken


def main() -> int:
    root = repo_root()
    broken = run(root)

    if not broken:
        checked = sum(1 for _ in iter_markdown_files(root))
        print(f"OK   all relative markdown links resolve ({checked} file(s) scanned)")
        return 0

    for item in broken:
        print(f"FAIL {item}")
    print(f"\n{len(broken)} broken link(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
