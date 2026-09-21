#!/usr/bin/env python3
"""Validate dev/holdout semantic-eval catalogs and coverage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPECTED_COUNTS = {"dev": 20, "holdout": 10}
REQUIRED_STAGES = {"architecture", "high_level", "detailed"}
REQUIRED_LIFECYCLES = {"existing", "planned", "modified", "removed"}
REQUIRED_OUTPUTS = {"finding", "requirement_gap", "evidence_gap", "open_decision", "pass"}
REQUIRED_LENSES = {
    "coverage", "idempotency", "concurrency", "ordering", "lifecycle",
    "atomicity", "persistence", "dependency", "compatibility", "migration",
    "architecture-conformance",
}
REQUIRED_CLAIM_KINDS = {
    "precondition", "design-guarantee", "existing-system-fact", "platform",
    "api", "performance", "compatibility",
}


def _load_catalog(path: Path, errors: list[str]) -> list[dict]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: cannot read catalog: {exc}")
        return []
    cases = value.get("cases")
    if not isinstance(cases, list):
        errors.append(f"{path}: cases must be an array")
        return []
    return cases


def validate_dataset(root: Path) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    seen_ids: set[str] = set()
    metadata_rows: list[dict] = []

    for split, expected_count in EXPECTED_COUNTS.items():
        catalog = root / split / "cases.json"
        cases = _load_catalog(catalog, errors)
        if len(cases) != expected_count:
            errors.append(f"{split}: expected {expected_count} {split} cases, found {len(cases)}")
        for index, case in enumerate(cases):
            where = f"{catalog}#{index}"
            case_id = case.get("case_id")
            if not isinstance(case_id, str) or not case_id:
                errors.append(f"{where}: missing case_id")
            elif case_id in seen_ids:
                errors.append(f"{where}: duplicate case_id {case_id}")
            else:
                seen_ids.add(case_id)
            if not isinstance(case.get("input"), str) or not case.get("input", "").strip():
                errors.append(f"{where}: input must be non-empty text")
            if not isinstance(case.get("context", {}), dict):
                errors.append(f"{where}: context must be an object")
            metadata = case.get("metadata")
            if not isinstance(metadata, dict):
                errors.append(f"{where}: missing metadata")
                continue
            required_metadata = {"design_stage", "mechanism_lifecycle", "primary_lens", "expected_output", "claim_kind"}
            missing = sorted(required_metadata - set(metadata))
            if missing:
                errors.append(f"{where}: metadata missing {', '.join(missing)}")
            metadata_rows.append(metadata)
            expected = case.get("expected")
            if not isinstance(expected, dict):
                errors.append(f"{where}: expected must be an object")
                continue
            for field in ("must_detect", "must_not_detect", "allowed_verdicts"):
                if not isinstance(expected.get(field), list):
                    errors.append(f"{where}: expected.{field} must be an array")
            for field in ("expected_requirement_gap_count", "expected_evidence_gap_count", "expected_open_decision_count"):
                if not isinstance(expected.get(field), int):
                    errors.append(f"{where}: expected.{field} must be an integer")

    def require_axis(field: str, required: set[str]) -> None:
        actual = {row.get(field) for row in metadata_rows}
        missing = sorted(required - actual)
        if missing:
            errors.append(f"missing {field} coverage: {', '.join(missing)}")

    require_axis("design_stage", REQUIRED_STAGES)
    require_axis("mechanism_lifecycle", REQUIRED_LIFECYCLES)
    require_axis("expected_output", REQUIRED_OUTPUTS)
    require_axis("primary_lens", REQUIRED_LENSES)
    require_axis("claim_kind", REQUIRED_CLAIM_KINDS)
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = validate_dataset(args.root)
    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        return 1
    print("dataset valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
