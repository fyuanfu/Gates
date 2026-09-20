#!/usr/bin/env python3
"""Deterministic validation for technical-challenge-model reports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """Raised when a report violates the canonical contract."""


VALID_VERDICTS = {"PASS", "PASS_WITH_ACTIONS", "NEEDS_DECISION", "BLOCKED"}
VALID_ASSURANCE = {"DOCUMENT_ONLY", "CONTEXT_GROUNDED", "REPOSITORY_GROUNDED", "EVIDENCE_VERIFIED"}
VALID_STAGES = {"architecture", "high_level", "detailed"}
VALID_CONSTRAINT_AUTHORITY = {"verified", "curated", "inferred"}
VALID_MECHANISM_LIFECYCLE = {"existing", "planned", "modified", "removed"}
VALID_CLAIM_STATUS = {"VERIFIED", "SUPPORTED", "ASSUMED", "UNKNOWN", "CONTRADICTED"}
VALID_COVERAGE_STATUS = {"COVERED", "PARTIAL", "MISSING", "CONTRADICTED", "UNCLEAR"}
VALID_SEVERITY = {"BLOCKER", "HIGH", "MEDIUM", "LOW"}


def _json_type_matches(value: Any, expected: str) -> bool:
    mapping = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return mapping[expected](value)


def _resolve_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ContractError(f"unsupported schema ref: {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def validate_schema(value: Any, schema: dict[str, Any], root: dict[str, Any], path: str = "$") -> None:
    if "$ref" in schema:
        validate_schema(value, _resolve_ref(root, schema["$ref"]), root, path)
        return
    expected = schema.get("type")
    if expected is not None:
        expected_types = expected if isinstance(expected, list) else [expected]
        if not any(_json_type_matches(value, item) for item in expected_types):
            raise ContractError(f"{path}: expected {' or '.join(expected_types)}")
    if "const" in schema and value != schema["const"]:
        raise ContractError(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractError(f"{path}: invalid enum value {value!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ContractError(f"{path}: string is empty")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            raise ContractError(f"{path}: does not match {schema['pattern']}")
    if isinstance(value, list):
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                raise ContractError(f"{path}: duplicate array items")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], root, f"{path}[{index}]")
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = sorted(required - set(value))
        if missing:
            raise ContractError(f"{path}: missing required fields: {', '.join(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise ContractError(f"{path}: unknown fields: {', '.join(unknown)}")
        for key, item in value.items():
            if key in properties:
                validate_schema(item, properties[key], root, f"{path}.{key}")


def _ids(items: list[dict[str, Any]], collection: str, errors: list[str]) -> set[str]:
    values: list[str] = []
    for item in items:
        value = item.get("id")
        if not isinstance(value, str) or not value:
            errors.append(f"{collection}: item missing id")
            continue
        values.append(value)
    if len(values) != len(set(values)):
        errors.append(f"{collection}: duplicate ids")
    return set(values)


def validate_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if report.get("schema_version") != "1.0.0":
        errors.append("invalid schema_version")
    if report.get("design_stage") not in VALID_STAGES:
        errors.append("invalid design_stage")
    if report.get("verdict") not in VALID_VERDICTS:
        errors.append("invalid verdict")
    if report.get("assurance_level") not in VALID_ASSURANCE:
        errors.append("invalid assurance_level")

    required_collections = [
        "obligations", "system_constraints", "decisions", "mechanisms", "claims",
        "coverage", "counterexamples", "evidence", "findings", "requirement_gaps",
        "evidence_gaps", "open_decisions",
    ]
    for name in required_collections:
        if not isinstance(report.get(name), list):
            errors.append(f"{name}: expected array")
            report[name] = []

    obligation_ids = _ids(report["obligations"], "obligations", errors)
    constraint_ids = _ids(report["system_constraints"], "system_constraints", errors)
    decision_ids = _ids(report["decisions"], "decisions", errors)
    mechanism_ids = _ids(report["mechanisms"], "mechanisms", errors)
    claim_ids = _ids(report["claims"], "claims", errors)
    counterexample_ids = _ids(report["counterexamples"], "counterexamples", errors)
    evidence_ids = _ids(report["evidence"], "evidence", errors)
    _ids(report["findings"], "findings", errors)
    _ids(report["requirement_gaps"], "requirement_gaps", errors)
    _ids(report["evidence_gaps"], "evidence_gaps", errors)
    _ids(report["open_decisions"], "open_decisions", errors)

    constraints = {item.get("id"): item for item in report["system_constraints"]}
    mechanisms = {item.get("id"): item for item in report["mechanisms"]}

    for item in report["system_constraints"]:
        if item.get("authority") not in VALID_CONSTRAINT_AUTHORITY:
            errors.append(f"{item.get('id','<unknown>')}: invalid constraint authority")

    for item in report["decisions"]:
        did = item.get("id", "<unknown>")
        for oid in item.get("supports", []):
            if oid not in obligation_ids:
                errors.append(f"{did}: unknown obligation id {oid}")
        for cid in item.get("preserves", []):
            if cid not in constraint_ids:
                errors.append(f"{did}: unknown constraint id {cid}")

    for item in report["mechanisms"]:
        mid = item.get("id", "<unknown>")
        did = item.get("decision_id")
        if did not in decision_ids:
            errors.append(f"{mid}: unknown decision id {did}")
        if item.get("lifecycle") not in VALID_MECHANISM_LIFECYCLE:
            errors.append(f"{mid}: invalid mechanism lifecycle")

    for item in report["claims"]:
        cid = item.get("id", "<unknown>")
        did = item.get("decision_id")
        if did is not None and did not in decision_ids:
            errors.append(f"{cid}: unknown decision id {did}")
        for mid in item.get("mechanism_ids", []):
            if mid not in mechanism_ids:
                errors.append(f"{cid}: unknown mechanism id {mid}")
        if item.get("status") not in VALID_CLAIM_STATUS:
            errors.append(f"{cid}: invalid claim status")

    for item in report["coverage"]:
        anchor_type = item.get("anchor_type")
        anchor_id = item.get("anchor_id")
        if anchor_type == "obligation" and anchor_id not in obligation_ids:
            errors.append(f"coverage: unknown obligation id {anchor_id}")
        elif anchor_type == "constraint" and anchor_id not in constraint_ids:
            errors.append(f"coverage: unknown constraint id {anchor_id}")
        elif anchor_type not in {"obligation", "constraint"}:
            errors.append("coverage: invalid anchor_type")
        for did in item.get("decision_ids", []):
            if did not in decision_ids:
                errors.append(f"coverage: unknown decision id {did}")
        for mid in item.get("mechanism_ids", []):
            if mid not in mechanism_ids:
                errors.append(f"coverage: unknown mechanism id {mid}")
        if item.get("status") not in VALID_COVERAGE_STATUS:
            errors.append("coverage: invalid status")

    for item in report["evidence"]:
        eid = item.get("id", "<unknown>")
        claim_id = item.get("claim_id")
        if claim_id is not None and claim_id not in claim_ids:
            errors.append(f"{eid}: unknown claim id {claim_id}")
        if item.get("type") == "CODE_SEARCH_ABSENCE" and claim_id in claim_ids:
            claim = next((c for c in report["claims"] if c.get("id") == claim_id), None)
            if claim:
                planned = any(mechanisms.get(mid, {}).get("lifecycle") == "planned" for mid in claim.get("mechanism_ids", []))
                if planned and item.get("adequacy") not in {"INAPPROPRIATE_FOR_PLANNED_MECHANISM", "WEAK"}:
                    errors.append(f"{eid}: code absence cannot strongly refute a planned mechanism")

    for item in report["counterexamples"]:
        ceid = item.get("id", "<unknown>")
        claim_id = item.get("claim_id")
        if claim_id not in claim_ids:
            errors.append(f"{ceid}: unknown claim id {claim_id}")

    for item in report["evidence_gaps"]:
        egid = item.get("id", "<unknown>")
        claim_id = item.get("claim_id")
        if claim_id not in claim_ids:
            errors.append(f"{egid}: unknown claim id {claim_id}")

    for item in report["findings"]:
        fid = item.get("id", "<unknown>")
        linked_obligations = item.get("linked_obligations", [])
        linked_constraints = item.get("linked_constraints", [])
        if not linked_obligations and not linked_constraints:
            errors.append(f"{fid}: missing requirement/system anchor")
        for oid in linked_obligations:
            if oid not in obligation_ids:
                errors.append(f"{fid}: unknown obligation id {oid}")
        for cid in linked_constraints:
            if cid not in constraint_ids:
                errors.append(f"{fid}: unknown constraint id {cid}")
        did = item.get("decision_id")
        if did is not None and did not in decision_ids:
            errors.append(f"{fid}: unknown decision id {did}")
        for mid in item.get("mechanism_ids", []):
            if mid not in mechanism_ids:
                errors.append(f"{fid}: unknown mechanism id {mid}")
        claim_id = item.get("claim_id")
        if claim_id is not None and claim_id not in claim_ids:
            errors.append(f"{fid}: unknown claim id {claim_id}")
        ceid = item.get("counterexample_id")
        if ceid is not None and ceid not in counterexample_ids:
            errors.append(f"{fid}: unknown counterexample id {ceid}")
        for eid in item.get("evidence_ids", []):
            if eid not in evidence_ids:
                errors.append(f"{fid}: unknown evidence id {eid}")
        finding_path = item.get("path")
        if finding_path is None:
            finding_path = "coverage" if item.get("type") in {"DESIGN_COVERAGE_GAP", "DESIGN_CONTRADICTION"} else "counterexample"
        if finding_path == "counterexample":
            if item.get("claim_id") is None:
                errors.append(f"{fid}: counterexample finding requires claim_id")
            if item.get("counterexample_id") is None:
                errors.append(f"{fid}: counterexample finding requires counterexample_id")
        if item.get("severity") not in VALID_SEVERITY:
            errors.append(f"{fid}: invalid severity")
        if item.get("severity") == "BLOCKER":
            if not item.get("evidence_ids"):
                errors.append(f"{fid}: blocker missing evidence")
            if linked_constraints and not linked_obligations:
                authorities = [constraints.get(cid, {}).get("authority") for cid in linked_constraints]
                if authorities and all(value == "inferred" for value in authorities):
                    errors.append(f"{fid}: blocker cannot rely only on inferred constraints")

    return errors


def load_report(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read report: {exc}") from exc
    schema_path = Path(__file__).resolve().parents[1] / "references" / "report.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read bundled schema: {exc}") from exc
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ContractError("bundled schema must declare Draft 2020-12")
    validate_schema(value, schema, schema)
    errors = validate_report(value)
    if errors:
        raise ContractError("\n".join(errors))
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        load_report(args.report)
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"valid: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
