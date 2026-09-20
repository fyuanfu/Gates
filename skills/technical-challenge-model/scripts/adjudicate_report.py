#!/usr/bin/env python3
"""Apply deterministic verdict rules to a technical challenge report."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from validate_report import ContractError, validate_report


def adjudicate(report: dict) -> dict:
    if (
        any(item.get("severity") == "BLOCKER" for item in report.get("findings", []))
        or any(item.get("critical") for item in report.get("evidence_gaps", []))
    ):
        report["verdict"] = "BLOCKED"
    elif any(item.get("blocking") for item in report.get("requirement_gaps", [])) or any(item.get("blocking") for item in report.get("open_decisions", [])):
        report["verdict"] = "NEEDS_DECISION"
    elif report.get("findings") or report.get("evidence_gaps") or report.get("open_decisions"):
        report["verdict"] = "PASS_WITH_ACTIONS"
    else:
        report["verdict"] = "PASS"
    return report


def atomic_write(path: Path, report: dict) -> None:
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        adjudicate(report)
        errors = validate_report(report)
        if errors:
            raise ContractError("\n".join(errors))
        atomic_write(args.report, report)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({"verdict": report["verdict"], "report": str(args.report)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
