#!/usr/bin/env python3
"""Run deterministic Technical Challenge Model contract tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]


def run(command: list[str]) -> int:
    print("+", " ".join(command))
    completed = subprocess.run(command, cwd=REPO_ROOT, text=True)
    return completed.returncode


def main() -> int:
    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", str(SKILL_ROOT / "evals" / "tests"), "-v"],
        [sys.executable, str(SKILL_ROOT / "evals" / "scripts" / "validate_dataset.py"), str(SKILL_ROOT / "evals")],
    ]
    for command in commands:
        code = run(command)
        if code:
            return code

    word_count = len((SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").split())
    if word_count > 500:
        print(f"SKILL.md too large: {word_count} words > 500", file=sys.stderr)
        return 1
    print(f"SKILL.md words: {word_count}")
    print("contract tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
