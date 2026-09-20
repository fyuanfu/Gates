#!/usr/bin/env python3
"""Prepare an isolated semantic-eval sandbox from a case catalog."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def load_case(catalog: Path, case_id: str) -> dict:
    try:
        value = json.loads(Path(catalog).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read catalog: {exc}") from exc
    for case in value.get("cases", []):
        if case.get("case_id") == case_id:
            return case
    raise ValueError(f"unknown case_id: {case_id}")


def prepare_case(catalog: Path, case_id: str, output_dir: Path, skill_root: Path) -> None:
    case = load_case(catalog, case_id)
    output_dir = Path(output_dir)
    skill_root = Path(skill_root)
    if not (skill_root / "SKILL.md").is_file():
        raise ValueError(f"missing skill: {skill_root / 'SKILL.md'}")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / "skill" / "references").mkdir(parents=True)
    (output_dir / "case").mkdir(parents=True)

    shutil.copy2(skill_root / "SKILL.md", output_dir / "skill" / "SKILL.md")
    refs = skill_root / "references"
    if refs.is_dir():
        for path in refs.iterdir():
            if path.is_file():
                shutil.copy2(path, output_dir / "skill" / "references" / path.name)

    (output_dir / "case" / "input.md").write_text(str(case.get("input", "")), encoding="utf-8")
    context = case.get("context") or {}
    if context:
        context_dir = output_dir / "case" / "context"
        context_dir.mkdir()
        for name, content in context.items():
            target = context_dir / name
            if target.name != name or name in {"expected.json", "cases.json"}:
                raise ValueError(f"unsafe context name: {name}")
            target.write_text(str(content), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("case_id")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    try:
        prepare_case(args.catalog, args.case_id, args.output_dir, args.skill_root)
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 2
    print(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
