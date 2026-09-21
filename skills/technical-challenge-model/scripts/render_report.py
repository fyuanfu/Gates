#!/usr/bin/env python3
"""Render a validated technical challenge JSON report as deterministic Markdown."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from validate_report import ContractError, load_report


SEVERITY_ORDER = {"BLOCKER": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _clean(value: object) -> str:
    return " ".join(str(value).splitlines()).strip()


def render(report: dict) -> str:
    lines = [
        "# Technical Challenge Report",
        "",
        "## Verdict & Assurance",
        "",
        f"- Verdict: **{report['verdict']}**",
        f"- Assurance: **{report['assurance_level']}**",
        f"- Design stage: `{report['design_stage']}`",
        "",
        "## Technical Findings",
        "",
    ]

    findings = sorted(report.get("findings", []), key=lambda item: (SEVERITY_ORDER.get(item.get("severity"), 99), item.get("id", "")))
    if not findings:
        lines += ["无。", ""]
    for item in findings:
        lines += [
            f"### {item['id']} · {item['severity']} · {_clean(item['title'])}",
            "",
            f"- Type: `{item['type']}`",
            f"- Impact: {_clean(item['impact'])}",
            f"- Requirement anchors: {', '.join(item.get('linked_obligations', [])) or '-'}",
            f"- System constraints: {', '.join(item.get('linked_constraints', [])) or '-'}",
            f"- Evidence: {', '.join(item.get('evidence_ids', [])) or '-'}",
            f"- Required action: {_clean(item['required_action'])}",
            "",
        ]

    lines += ["## Requirement Gaps", ""]
    if not report.get("requirement_gaps"):
        lines += ["无。", ""]
    else:
        for item in report["requirement_gaps"]:
            lines.append(f"- **{item['id']}**: {_clean(item['question'])} (`blocking={str(item['blocking']).lower()}`)")
        lines.append("")

    lines += ["## Evidence Gaps", ""]
    if not report.get("evidence_gaps"):
        lines += ["无。", ""]
    else:
        for item in report["evidence_gaps"]:
            lines.append(f"- **{item['id']}** / `{item['claim_id']}`: {_clean(item['required_evidence'])}")
        lines.append("")

    lines += ["## Open Decisions", ""]
    if not report.get("open_decisions"):
        lines += ["无。", ""]
    else:
        for item in report["open_decisions"]:
            lines.append(f"- **{item['id']}**: {_clean(item['decision'])} (owner: {_clean(item['owner'])})")
        lines.append("")

    lines += ["## Requirement / Constraint Coverage", ""]
    if not report.get("coverage"):
        lines += ["无。", ""]
    else:
        lines += ["| Anchor | Status | Decisions | Mechanisms |", "|---|---|---|---|"]
        for item in report["coverage"]:
            lines.append(
                f"| `{item['anchor_id']}` | `{item['status']}` | {', '.join(item['decision_ids']) or '-'} | {', '.join(item['mechanism_ids']) or '-'} |"
            )
        lines.append("")

    lines += ["## Critical Claims & Counterexamples", ""]
    for claim in report.get("claims", []):
        lines.append(f"- **{claim['id']}** `{claim['kind']}` / `{claim['status']}`: {_clean(claim['statement'])}")
    if not report.get("claims"):
        lines.append("无。")
    lines.append("")
    for ce in report.get("counterexamples", []):
        lines.append(f"- **{ce['id']}** against `{ce['claim_id']}`: {_clean(' -> '.join(ce['failure_path']))}")
    if not report.get("counterexamples"):
        lines.append("无反例。")
    lines.append("")

    return "\n".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
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
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = load_report(args.report)
        _atomic_write(args.output, render(report))
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    print(f"rendered: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
