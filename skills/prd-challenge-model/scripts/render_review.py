#!/usr/bin/env python3
"""Render a validated PRD Challenge Model JSON review as deterministic Markdown."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from validate_review import ContractError, load_and_validate


SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def clean(value: object) -> str:
    return " ".join(str(value).splitlines()).strip()


def render_finding(finding: dict) -> list[str]:
    lines = [
        f"### {finding['id']} · {finding['severity']} · {clean(finding['title'])}",
        "",
        f"- 类型：`{finding['defect_type']}` / `{finding['quality_dimension']}`",
        f"- 问题：{clean(finding['problem'])}",
        f"- 影响：{clean(finding['impact'])}",
        f"- 需要决策：{clean(finding['required_decision'])}",
        f"- 下游后果：{', '.join(f'`{item}`' for item in finding['consequence_types'])}",
        "- 证据：",
    ]
    for evidence in finding["evidence"]:
        location = f"{clean(evidence['source_path'])} · {clean(evidence['section'])}"
        lines.append(f"  - `{evidence['artifact_id']}` / `{evidence['requirement_id']}` / {location}: “{clean(evidence['quote'])}”")
    if finding["failure_witness"]:
        witness = finding["failure_witness"]
        lines += [
            "- Failure Witness：",
            f"  - Given：{clean(witness['given'])}",
            f"  - When：{clean(witness['when'])}",
            f"  - Then：{clean(witness['then'])}",
        ]
    if finding["contradiction_proof"]:
        proof = finding["contradiction_proof"]
        lines += [
            "- Contradiction Proof：",
            f"  - `{proof['statement_a']['requirement_id']}`：{clean(proof['statement_a']['meaning'])}",
            f"  - `{proof['statement_b']['requirement_id']}`：{clean(proof['statement_b']['meaning'])}",
        ]
    lines += [f"- 反证结论：{clean(finding['disproof']['summary'])}", ""]
    return lines


def render(review: dict) -> str:
    summary = review["summary"]
    lines = [
        "# PRD Challenge Review",
        "",
        "## Verdict",
        "",
        f"**{review['verdict']}**",
        "",
        "通过仅表示本次完整评审未发现已确认 P0/P1，不代表产品已整体达到开发就绪。",
        "",
    ]
    if review["verdict_reasons"]:
        lines += ["原因：", ""] + [f"- {clean(reason)}" for reason in review["verdict_reasons"]] + [""]

    lines += [
        "## Summary",
        "",
        "| Findings | P0 | P1 | P2 | P3 | Observations | Open Questions |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        f"| {summary['finding_count']} | {summary['severity_counts']['P0']} | {summary['severity_counts']['P1']} | {summary['severity_counts']['P2']} | {summary['severity_counts']['P3']} | {summary['observation_count']} | {summary['open_question_count']} |",
        "",
        "## Blocking Findings",
        "",
    ]
    blockers = sorted((item for item in review["findings"] if item["severity"] in {"P0", "P1"}), key=lambda item: (SEVERITY_ORDER[item["severity"]], item["id"]))
    if not blockers:
        lines += ["无。", ""]
    for finding in blockers:
        lines += render_finding(finding)

    lines += ["## Non-blocking Findings", ""]
    non_blockers = sorted((item for item in review["findings"] if item["severity"] in {"P2", "P3"}), key=lambda item: (SEVERITY_ORDER[item["severity"]], item["id"]))
    if not non_blockers:
        lines += ["无。", ""]
    for finding in non_blockers:
        lines += render_finding(finding)

    lines += ["## Open Questions", ""]
    if not review["open_questions"]:
        lines += ["无。", ""]
    for question in review["open_questions"]:
        marker = "阻断" if question["blocking"] else "非阻断"
        lines += [f"- **{question['id']} · {marker}**：{clean(question['question'])}（{clean(question['reason'])}）"]
    if review["open_questions"]:
        lines.append("")

    lines += ["## Observations", ""]
    if not review["observations"]:
        lines += ["无。", ""]
    for observation in review["observations"]:
        lines.append(f"- **{observation['id']} · {clean(observation['title'])}**：{clean(observation['description'])}")
    if review["observations"]:
        lines.append("")

    coverage = review["coverage"]
    lines += [
        "## Coverage",
        "",
        "| 范围 | 总数 | 已完成 | 失败/未分配 |",
        "|---|---:|---:|---:|",
        f"| Artifacts | {coverage['artifacts']['total']} | {coverage['artifacts']['parsed']} | {coverage['artifacts']['failed']} |",
        f"| Requirements | {coverage['requirements']['total']} | {coverage['requirements']['assigned'] + coverage['requirements']['standalone'] + coverage['requirements']['excluded']} | {coverage['requirements']['unassigned']} |",
        f"| Review Slices | {coverage['review_slices']['total']} | {coverage['review_slices']['fast_scan_done']} | {coverage['review_slices']['total'] - coverage['review_slices']['fast_scan_done']} |",
        "",
        f"Critical Decision Guard：`{str(coverage['critical_decision_guard_done']).lower()}`  ",
        f"Completion Guard：`{str(coverage['completion_guard_done']).lower()}`",
        "",
        "## Execution Issues",
        "",
    ]
    if not review["execution_issues"]:
        lines += ["无。", ""]
    for issue in review["execution_issues"]:
        marker = "阻断" if issue["blocking"] else "非阻断"
        lines.append(f"- **{issue['id']} · `{issue['code']}` · {marker}**：{clean(issue['message'])}")
    lines.append("")
    return "\n".join(lines)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
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
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        review = load_and_validate(args.review, check_verdict=True)
        atomic_write(args.output, render(review))
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"$: cannot render review: {exc}", file=sys.stderr)
        return 3
    print(f"rendered: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

