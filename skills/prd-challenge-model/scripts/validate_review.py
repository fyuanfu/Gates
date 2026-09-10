#!/usr/bin/env python3
"""Validate PRD Challenge Model reviews with Python's standard library only."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """A deterministic review-contract violation."""


def _fail(path: str, message: str) -> None:
    raise ContractError(f"{path}: {message}")


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

    if "anyOf" in schema:
        errors = []
        for choice in schema["anyOf"]:
            try:
                validate_schema(value, choice, root, path)
                return
            except ContractError as exc:
                errors.append(str(exc))
        _fail(path, "does not match any allowed schema")

    expected = schema.get("type")
    if expected is not None:
        expected_types = expected if isinstance(expected, list) else [expected]
        if not any(_json_type_matches(value, item) for item in expected_types):
            _fail(path, f"expected {' or '.join(expected_types)}")

    if "const" in schema and value != schema["const"]:
        _fail(path, f"must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        _fail(path, f"invalid enum value {value!r}")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            _fail(path, "string is empty")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            _fail(path, f"does not match {schema['pattern']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            _fail(path, f"must be >= {schema['minimum']}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            _fail(path, f"requires at least {schema['minItems']} item(s)")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
            if len(encoded) != len(set(encoded)):
                _fail(path, "contains duplicate items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                validate_schema(item, item_schema, root, f"{path}[{index}]")

    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = sorted(required - set(value))
        if missing:
            _fail(path, f"missing required fields: {', '.join(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                _fail(path, f"unknown fields: {', '.join(unknown)}")
        for key, item in value.items():
            if key in properties:
                validate_schema(item, properties[key], root, f"{path}.{key}")


def _unique_ids(items: list[dict[str, Any]], collection: str) -> set[str]:
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        _fail(f"$.{collection}", "duplicate IDs")
    return set(ids)


def _require_refs(refs: list[str], allowed: set[str], path: str) -> None:
    missing = sorted(set(refs) - allowed)
    if missing:
        _fail(path, f"unknown IDs: {', '.join(missing)}")


def _validate_evidence(evidence: dict[str, Any], artifacts: dict[str, dict[str, Any]], requirements: dict[str, dict[str, Any]], path: str) -> None:
    artifact_id = evidence["artifact_id"]
    if artifact_id not in artifacts:
        _fail(f"{path}.artifact_id", f"unknown ID {artifact_id}")
    if evidence["source_path"] != artifacts[artifact_id]["path"]:
        _fail(f"{path}.source_path", "does not match artifact path")
    requirement_id = evidence["requirement_id"]
    if requirement_id is not None:
        if requirement_id not in requirements:
            _fail(f"{path}.requirement_id", f"unknown ID {requirement_id}")
        if requirements[requirement_id]["artifact_id"] != artifact_id:
            _fail(f"{path}.requirement_id", "belongs to a different artifact")


def expected_verdict(review: dict[str, Any]) -> str:
    if review["review_status"] == "INCOMPLETE":
        return "review_incomplete"
    if any(item["severity"] in {"P0", "P1"} for item in review["findings"]):
        return "review_failed"
    return "review_passed"


def validate_cross_fields(review: dict[str, Any], *, check_verdict: bool = True) -> None:
    artifact_ids = _unique_ids(review["artifacts"], "artifacts")
    requirement_ids = _unique_ids(review["requirements"], "requirements")
    slice_ids = _unique_ids(review["review_slices"], "review_slices")
    _unique_ids(review["critical_decisions"], "critical_decisions")
    finding_ids = _unique_ids(review["findings"], "findings")
    _unique_ids(review["observations"], "observations")
    question_ids = _unique_ids(review["open_questions"], "open_questions")
    issue_ids = _unique_ids(review["execution_issues"], "execution_issues")

    artifacts = {item["id"]: item for item in review["artifacts"]}
    requirements = {item["id"]: item for item in review["requirements"]}

    for index, artifact in enumerate(review["artifacts"]):
        if artifact["parse_status"] == "PARSED" and artifact["parse_error"] is not None:
            _fail(f"$.artifacts[{index}].parse_error", "must be null when parsed")
        if artifact["parse_status"] == "FAILED" and not artifact["parse_error"]:
            _fail(f"$.artifacts[{index}].parse_error", "is required when parsing failed")

    slice_membership = Counter(
        requirement_id
        for review_slice in review["review_slices"]
        for requirement_id in review_slice["requirement_ids"]
    )
    for index, requirement in enumerate(review["requirements"]):
        if requirement["artifact_id"] not in artifact_ids:
            _fail(f"$.requirements[{index}].artifact_id", "unknown artifact")
        excluded = requirement["coverage_status"] == "EXCLUDED_WITH_REASON"
        if excluded != (requirement["exclusion_reason"] is not None):
            _fail(f"$.requirements[{index}].exclusion_reason", "does not match coverage_status")
        count = slice_membership[requirement["id"]]
        if requirement["coverage_status"] == "ASSIGNED_TO_SLICE" and count != 1:
            _fail(f"$.requirements[{index}].coverage_status", "assigned requirement must appear in exactly one Slice")
        if requirement["coverage_status"] != "ASSIGNED_TO_SLICE" and count != 0:
            _fail(f"$.requirements[{index}].coverage_status", "standalone or excluded requirement must not appear in a Slice")

    prefix = {"BEHAVIOR": "S-BEH-", "BUSINESS_RULE": "S-RULE-", "CONSTRAINT": "S-CON-", "NFR": "S-NFR-"}
    for index, review_slice in enumerate(review["review_slices"]):
        _require_refs(review_slice["requirement_ids"], requirement_ids, f"$.review_slices[{index}].requirement_ids")
        _require_refs(review_slice["cross_slice_ids"], slice_ids, f"$.review_slices[{index}].cross_slice_ids")
        if not review_slice["id"].startswith(prefix[review_slice["type"]]):
            _fail(f"$.review_slices[{index}].id", "prefix does not match Slice type")
        testability = review_slice["testability"]
        if review_slice["fast_scan_done"] and testability is None:
            _fail(f"$.review_slices[{index}].testability", "required after Fast Scan")
        if not review_slice["fast_scan_done"] and testability is not None:
            _fail(f"$.review_slices[{index}].testability", "must be null before Fast Scan")
        measurement = testability["measurement"] if testability is not None else None
        if testability is not None and review_slice["type"] in {"NFR", "CONSTRAINT"} and measurement is None:
            _fail(f"$.review_slices[{index}].testability.measurement", "required for NFR/Constraint")
        if testability is not None and review_slice["type"] not in {"NFR", "CONSTRAINT"} and measurement is not None:
            _fail(f"$.review_slices[{index}].testability.measurement", "must be null for Behavior/Rule")
        if review_slice["deep_challenge_status"] == "NOT_REQUIRED" and (review_slice["minimal_challenge"] == "SUSPICIOUS" or review_slice["risk_signals"]):
            _fail(f"$.review_slices[{index}].deep_challenge_status", "Deep Challenge required by suspicion or risk signal")

    for index, decision in enumerate(review["critical_decisions"]):
        _require_refs(decision["requirement_ids"], requirement_ids, f"$.critical_decisions[{index}].requirement_ids")

    required_disproof_scopes = {
        "P0": {"GLOBAL"},
        "P1": {"TARGETED", "GLOBAL"},
        "P2": {"LOCAL", "TARGETED", "GLOBAL"},
        "P3": {"BASIC", "LOCAL", "TARGETED", "GLOBAL"},
    }
    for index, finding in enumerate(review["findings"]):
        _require_refs(finding["requirement_ids"], requirement_ids, f"$.findings[{index}].requirement_ids")
        _require_refs(finding["review_slice_ids"], slice_ids, f"$.findings[{index}].review_slice_ids")
        _require_refs(finding["disproof"]["checked_requirement_ids"], requirement_ids, f"$.findings[{index}].disproof.checked_requirement_ids")
        if finding["disproof"]["scope"] not in required_disproof_scopes[finding["severity"]]:
            _fail(f"$.findings[{index}].disproof.scope", "insufficient for severity")
        if finding["severity"] in {"P0", "P1"} and finding["failure_witness"] is None and finding["contradiction_proof"] is None:
            _fail(f"$.findings[{index}]", "P0/P1 requires failure_witness or contradiction_proof")
        if finding["defect_type"] == "CONTRADICTORY":
            if finding["contradiction_proof"] is None or len(finding["evidence"]) < 2:
                _fail(f"$.findings[{index}]", "contradiction requires proof and two Evidence entries")
        for evidence_index, evidence in enumerate(finding["evidence"]):
            _validate_evidence(evidence, artifacts, requirements, f"$.findings[{index}].evidence[{evidence_index}]")
        proof = finding["contradiction_proof"]
        if proof:
            for side in ("statement_a", "statement_b"):
                if proof[side]["requirement_id"] not in requirement_ids:
                    _fail(f"$.findings[{index}].contradiction_proof.{side}.requirement_id", "unknown requirement")

    for index, observation in enumerate(review["observations"]):
        _require_refs(observation["requirement_ids"], requirement_ids, f"$.observations[{index}].requirement_ids")
        for evidence_index, evidence in enumerate(observation["evidence"]):
            _validate_evidence(evidence, artifacts, requirements, f"$.observations[{index}].evidence[{evidence_index}]")
    for index, question in enumerate(review["open_questions"]):
        _require_refs(question["requirement_ids"], requirement_ids, f"$.open_questions[{index}].requirement_ids")
    for index, issue in enumerate(review["execution_issues"]):
        _require_refs(issue["artifact_ids"], artifact_ids, f"$.execution_issues[{index}].artifact_ids")
        _require_refs(issue["requirement_ids"], requirement_ids, f"$.execution_issues[{index}].requirement_ids")

    coverage = review["coverage"]
    artifact_counts = coverage["artifacts"]
    actual_parsed = sum(item["parse_status"] == "PARSED" for item in review["artifacts"])
    actual_failed = len(review["artifacts"]) - actual_parsed
    if (artifact_counts["total"], artifact_counts["parsed"], artifact_counts["failed"]) != (len(review["artifacts"]), actual_parsed, actual_failed):
        _fail("$.coverage.artifacts", "counts do not match artifacts")

    requirement_counts = coverage["requirements"]
    status_counts = Counter(item["coverage_status"] for item in review["requirements"])
    expected_requirement_counts = {
        "total": len(review["requirements"]),
        "assigned": status_counts["ASSIGNED_TO_SLICE"],
        "standalone": status_counts["STANDALONE_REVIEW"],
        "excluded": status_counts["EXCLUDED_WITH_REASON"],
        "unassigned": status_counts["UNASSIGNED"],
    }
    if requirement_counts != expected_requirement_counts:
        _fail("$.coverage.requirements", "counts do not match requirements")

    slice_counts = coverage["review_slices"]
    expected_slice_counts = {
        "total": len(review["review_slices"]),
        "integrity_valid": sum(item["integrity_status"] == "VALID" for item in review["review_slices"]),
        "fast_scan_done": sum(item["fast_scan_done"] for item in review["review_slices"]),
        "minimal_challenge_done": sum(item["minimal_challenge"] != "NOT_RUN" for item in review["review_slices"]),
        "deep_challenge_done": sum(item["deep_challenge_status"] == "DONE" for item in review["review_slices"]),
        "deep_challenge_not_required": sum(item["deep_challenge_status"] == "NOT_REQUIRED" for item in review["review_slices"]),
    }
    if slice_counts != expected_slice_counts:
        _fail("$.coverage.review_slices", "counts do not match review_slices")

    severity_counts = Counter(item["severity"] for item in review["findings"])
    summary = review["summary"]
    expected_summary = {
        "finding_count": len(review["findings"]),
        "blocking_finding_count": severity_counts["P0"] + severity_counts["P1"],
        "observation_count": len(review["observations"]),
        "open_question_count": len(review["open_questions"]),
        "severity_counts": {level: severity_counts[level] for level in ("P0", "P1", "P2", "P3")},
    }
    if summary != expected_summary:
        _fail("$.summary", "counts do not match result collections")

    metrics = review["metrics"]
    if metrics["confirmed_candidate_count"] != len(review["findings"]):
        _fail("$.metrics.confirmed_candidate_count", "must equal findings length")
    if metrics["review_slice_count"] != len(review["review_slices"]):
        _fail("$.metrics.review_slice_count", "must equal review_slices length")
    if metrics["qualified_candidate_count"] < metrics["confirmed_candidate_count"] + metrics["rejected_candidate_count"]:
        _fail("$.metrics.qualified_candidate_count", "cannot be smaller than confirmed plus rejected")
    if metrics["raw_candidate_count"] < metrics["qualified_candidate_count"]:
        _fail("$.metrics.raw_candidate_count", "cannot be smaller than qualified candidates")

    blocking_ids = {
        item["id"] for item in review["execution_issues"] if item["blocking"]
    } | {
        item["id"] for item in review["open_questions"] if item["blocking"]
    }
    incomplete_conditions = [
        not review["artifacts"],
        not review["requirements"],
        any(item["required"] and item["parse_status"] == "FAILED" for item in review["artifacts"]),
        requirement_counts["unassigned"] > 0,
        any(item["integrity_status"] != "VALID" for item in review["review_slices"]),
        any(not item["fast_scan_done"] for item in review["review_slices"]),
        any(item["minimal_challenge"] == "NOT_RUN" for item in review["review_slices"]),
        any(item["deep_challenge_status"] == "NOT_RUN" for item in review["review_slices"]),
        not coverage["critical_decision_guard_done"],
        not coverage["completion_guard_done"],
        bool(blocking_ids),
    ]
    should_be_incomplete = any(incomplete_conditions)
    if should_be_incomplete != (review["review_status"] == "INCOMPLETE"):
        _fail("$.review_status", "does not match Completion Guard evidence")
    if review["review_status"] == "INCOMPLETE" and not blocking_ids:
        _fail("$.review_status", "INCOMPLETE requires a blocking issue or question")
    if review["review_status"] == "COMPLETED" and blocking_ids:
        _fail("$.review_status", "COMPLETED cannot contain blocking issues/questions")

    if check_verdict:
        expected = expected_verdict(review)
        if review["verdict"] != expected:
            _fail("$.verdict", f"must be {expected}")
        reasons = review["verdict_reasons"]
        if expected == "review_passed" and reasons:
            _fail("$.verdict_reasons", "PASS requires no reasons")
        if expected != "review_passed" and not reasons:
            _fail("$.verdict_reasons", "non-PASS requires reasons")
        required_reason_ids = blocking_ids if expected == "review_incomplete" else {item["id"] for item in review["findings"] if item["severity"] in {"P0", "P1"}}
        for item_id in required_reason_ids:
            if not any(item_id in reason for reason in reasons):
                _fail("$.verdict_reasons", f"must reference {item_id}")


def load_and_validate(path: Path, *, check_verdict: bool = True) -> dict[str, Any]:
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"$: cannot read review JSON: {exc}") from exc
    schema_path = Path(__file__).resolve().parents[1] / "references" / "review.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"$: cannot read bundled schema: {exc}") from exc
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ContractError("$: bundled schema must use Draft 2020-12")
    validate_schema(review, schema, schema)
    validate_cross_fields(review, check_verdict=check_verdict)
    return review


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review", type=Path)
    parser.add_argument("--pre-adjudication", action="store_true", help="skip only final Verdict/reason consistency")
    args = parser.parse_args(argv)
    try:
        load_and_validate(args.review, check_verdict=not args.pre_adjudication)
    except ContractError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"valid: {args.review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
