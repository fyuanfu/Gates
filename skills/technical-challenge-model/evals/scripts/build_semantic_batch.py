#!/usr/bin/env python3
"""Build isolated semantic-evaluation sandboxes without exposing answer keys."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def _load_cases(catalog: Path) -> list[dict]:
    try:
        payload = json.loads(Path(catalog).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read catalog: {exc}") from exc
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("catalog.cases must be an array")
    return cases


def _copy_skill(skill_root: Path, target: Path) -> None:
    if not (skill_root / "SKILL.md").is_file():
        raise ValueError(f"missing skill: {skill_root / 'SKILL.md'}")
    (target / "skill" / "references").mkdir(parents=True)
    shutil.copy2(skill_root / "SKILL.md", target / "skill" / "SKILL.md")
    refs = skill_root / "references"
    if refs.is_dir():
        for path in refs.iterdir():
            if path.is_file():
                shutil.copy2(path, target / "skill" / "references" / path.name)


def build_batch(
    catalog: Path,
    skill_root: Path,
    output_dir: Path,
    repetitions: int,
    baseline_sha: str,
) -> dict:
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")
    if not baseline_sha:
        raise ValueError("baseline_sha is required")

    cases = _load_cases(Path(catalog))
    output_dir = Path(output_dir)
    skill_root = Path(skill_root)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    runs = []
    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("case missing case_id")
        for index in range(1, repetitions + 1):
            run_id = f"run-{index:02d}"
            relative = Path("runs") / case_id / run_id
            sandbox = output_dir / relative
            (sandbox / "case").mkdir(parents=True)
            _copy_skill(skill_root, sandbox)
            (sandbox / "case" / "input.md").write_text(str(case.get("input", "")), encoding="utf-8")
            context = case.get("context") or {}
            if not isinstance(context, dict):
                raise ValueError(f"{case_id}: context must be an object")
            if context:
                context_dir = sandbox / "case" / "context"
                context_dir.mkdir()
                for name, content in context.items():
                    target = context_dir / name
                    if target.name != name or name in {"expected.json", "cases.json"}:
                        raise ValueError(f"{case_id}: unsafe context name: {name}")
                    target.write_text(str(content), encoding="utf-8")
            runs.append({
                "case_id": case_id,
                "run_id": run_id,
                "sandbox": relative.as_posix(),
            })

    manifest = {
        "baseline_sha": baseline_sha,
        "repetitions": repetitions,
        "runs": runs,
    }
    (output_dir / "run-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "
",
        encoding="utf-8",
    )
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--skill-root", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--baseline-sha", required=True)
    args = parser.parse_args(argv)
    try:
        build_batch(args.catalog, args.skill_root, args.output_dir, args.repetitions, args.baseline_sha)
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 2
    print(args.output_dir / "run-manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
