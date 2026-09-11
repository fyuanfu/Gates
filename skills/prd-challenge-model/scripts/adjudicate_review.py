#!/usr/bin/env python3
"""Compute and atomically persist the deterministic PRD Gate verdict."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from validate_review import ContractError, expected_verdict, load_and_validate, validate_cross_fields


def adjudicate(review: dict) -> dict:
    verdict = expected_verdict(review)
    review["verdict"] = verdict
    if verdict == "review_incomplete":
        ids = [item["id"] for item in review["execution_issues"] if item["blocking"]]
        review["verdict_reasons"] = [f"Review incomplete: {item_id}" for item_id in sorted(set(ids))]
    elif verdict == "review_failed":
        ids = [item["id"] for item in review["findings"] if item["severity"] in {"P0", "P1"}]
        review["verdict_reasons"] = [f"Confirmed blocking finding: {item_id}" for item_id in ids]
    else:
        review["verdict_reasons"] = []
    validate_cross_fields(review, check_verdict=True)
    return review


def atomic_write(path: Path, value: dict) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    args = parser.parse_args(argv)
    try:
        review = load_and_validate(args.review, check_verdict=False)
        adjudicate(review)
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        atomic_write(args.review, review)
    except OSError as exc:
        print(f"$: cannot write adjudicated review: {exc}", file=sys.stderr)
        return 3
    print(json.dumps({"verdict": review["verdict"], "review": str(args.review)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
