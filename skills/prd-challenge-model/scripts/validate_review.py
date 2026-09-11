#!/usr/bin/env python3
"""Validate PRD Challenge Model RGQ 2.0 reviews using only the standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BEHAVIOR_DIMENSIONS = {
    "ACTOR", "TRIGGER", "PRECONDITION", "SUCCESS",
    "FAILURE", "RECOVERY", "STATE", "FEEDBACK",
}
ROLE_BY_SLICE_TYPE = {
    "BEHAVIOR": {"DEFINES_BEHAVIOR", "VERIFIES_BEHAVIOR", "DEFINES_STATE"},
    "BUSINESS_RULE": {"DEFINES_RULE"},
    "CONSTRAINT": {"DEFINES_CONSTRAINT"},
    "NFR": {"DEFINES_NFR"},
}
RELATION_TARGET_TYPE = {
    "USES_RULE": "BUSINESS_RULE",
    "SUBJECT_TO_CONSTRAINT": "CONSTRAINT",
    "SUBJECT_TO_NFR": "NFR",
    "RELATED_BEHAVIOR": "BEHAVIOR",
}


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
        for choice in schema["anyOf"]:
            try:
                validate_schema(value, choice, root, path)
                return
            except ContractError:
                pass
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
        if schema.get("items"):
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], root, f"{path}[{index}]")
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


def expected_input_fingerprint(review: dict[str, Any]) -> str:
    artifacts = [
        {
            "content_sha256": item["content_sha256"],
            "id": item["id"],
            "path": item["path"],
            "source_version": item["source_version"],
        }
        for item in sorted(review["artifacts"], key=lambda item: item["id"])
    ]
    payload = {
        "artifacts": artifacts,
        "scope_snapshot": review["review_context"]["scope_snapshot"],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def derive_traceability_gaps(review: dict[str, Any]) -> list[dict[str, str]]:
    """Derive reportable gaps; do not persist these duplicate summaries in review.json."""
    gaps: list[dict[str, str]] = []
    verified_requirements: set[str] = set()
    incoming_links: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    for review_slice in review["review_slices"]:
        for link in review_slice["cross_slice_links"]:
            incoming_links[link["slice_id"]].append((review_slice["id"], link["relation"]))
        roles = {role for binding in review_slice["requirement_bindings"] for role in binding["roles"]}
        for binding in review_slice["requirement_bindings"]:
            if "VERIFIES_BEHAVIOR" in binding["roles"]:
                verified_requirements.add(binding["requirement_id"])
        if review_slice["type"] == "BEHAVIOR" and "DEFINES_BEHAVIOR" not in roles:
            gaps.append({"kind": "BEHAVIOR_WITHOUT_SOURCE", "id": review_slice["id"]})
        if review_slice["type"] == "BEHAVIOR" and review_slice["verification"] is not None and review_slice["verification"]["status"] in {"PARTIAL", "MISSING"}:
            gaps.append({"kind": "BEHAVIOR_WITHOUT_COMPLETE_VERIFICATION", "id": review_slice["id"]})

    for requirement in review["requirements"]:
        if requirement["type"] == "AC" and requirement["coverage_status"] == "ASSIGNED_TO_SLICE" and requirement["id"] not in verified_requirements:
            gaps.append({"kind": "ORPHAN_ACCEPTANCE_CRITERION", "id": requirement["id"]})
    for review_slice in review["review_slices"]:
        if review_slice["type"] in {"BUSINESS_RULE", "CONSTRAINT", "NFR"} and review_slice["id"] not in incoming_links and review_slice["traceability_exemption"] is None:
            gaps.append({"kind": "UNLINKED_SUPPORTING_SLICE", "id": review_slice["id"]})
    return gaps


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


def _validate_behavior_coverage(review_slice: dict[str, Any], requirement_ids: set[str], path: str) -> None:
    items = review_slice["behavior_coverage"]
    if not review_slice["fast_scan_done"]:
        if items is not None:
            _fail(f"{path}.behavior_coverage", "must be null before Fast Scan")
        return
    if review_slice["type"] != "BEHAVIOR":
        if items is not None:
            _fail(f"{path}.behavior_coverage", "must be null for non-BEHAVIOR Slice")
        return
    if items is None:
        _fail(f"{path}.behavior_coverage", "is required for BEHAVIOR Slice")
    dimensions = [item["dimension"] for item in items]
    if len(dimensions) != len(set(dimensions)) or set(dimensions) != BEHAVIOR_DIMENSIONS:
        _fail(f"{path}.behavior_coverage", "must contain each RGQ behavior dimension exactly once")
    for index, item in enumerate(items):
        item_path = f"{path}.behavior_coverage[{index}]"
        _require_refs(item["requirement_ids"], requirement_ids, f"{item_path}.requirement_ids")
        if item["status"] != "NOT_APPLICABLE" and not item["requirement_ids"]:
            _fail(f"{item_path}.requirement_ids", "requires source or in-scope anchor evidence")


def _validate_verification(verification: dict[str, Any], requirement_ids: set[str], path: str) -> None:
    _require_refs(verification["requirement_ids"], requirement_ids, f"{path}.requirement_ids")
    status = verification["status"]
    basis = verification["basis"]
    fields = (verification["condition"], verification["expected_observable_result"], verification["decision_rule"])
    if status == "COMPLETE":
        if basis not in {"EXPLICIT_SOURCE", "NORMALIZED_FROM_SOURCE"} or not verification["requirement_ids"] or not all(fields) or verification["missing_elements"]:
            _fail(path, "COMPLETE requires sourced condition, observable result, decision rule, and no missing elements")
    elif status == "PARTIAL":
        if basis not in {"EXPLICIT_SOURCE", "NORMALIZED_FROM_SOURCE"} or not verification["requirement_ids"] or not verification["missing_elements"]:
            _fail(path, "PARTIAL requires source requirements and missing elements")
    elif status == "MISSING":
        if basis != "ABSENT" or not verification["requirement_ids"] or not verification["missing_elements"]:
            _fail(path, "MISSING requires ABSENT basis, an in-scope anchor, and missing elements")
    else:
        if basis != "NOT_APPLICABLE" or verification["requirement_ids"] or any(value is not None for value in fields) or verification["missing_elements"]:
            _fail(path, "NOT_APPLICABLE requires empty evidence, fields, and missing elements")


def validate_cross_fields(review: dict[str, Any], *, check_verdict: bool = True) -> None:
    artifact_ids = _unique_ids(review["artifacts"], "artifacts")
    requirement_ids = _unique_ids(review["requirements"], "requirements")
    slice_ids = _unique_ids(review["review_slices"], "review_slices")
    _unique_ids(review["critical_decisions"], "critical_decisions")
    finding_ids = _unique_ids(review["findings"], "findings")
    _unique_ids(review["observations"], "observations")
    _unique_ids(review["open_questions"], "open_questions")
    _unique_ids(review["execution_issues"], "execution_issues")

    if review["review_context"]["input_fingerprint"] != expected_input_fingerprint(review):
        _fail("$.review_context.input_fingerprint", "does not match scope snapshot and Artifact hashes")

    artifacts = {item["id"]: item for item in review["artifacts"]}
    requirements = {item["id"]: item for item in review["requirements"]}
    slices = {item["id"]: item for item in review["review_slices"]}
    for index, artifact in enumerate(review["artifacts"]):
        if artifact["parse_status"] == "PARSED" and artifact["parse_error"] is not None:
            _fail(f"$.artifacts[{index}].parse_error", "must be null when parsed")
        if artifact["parse_status"] == "FAILED" and not artifact["parse_error"]:
            _fail(f"$.artifacts[{index}].parse_error", "is required when parsing failed")

    slice_membership: Counter[str] = Counter()
    prefix = {"BEHAVIOR": "S-BEH-", "BUSINESS_RULE": "S-RULE-", "CONSTRAINT": "S-CON-", "NFR": "S-NFR-"}
    for index, review_slice in enumerate(review["review_slices"]):
        path = f"$.review_slices[{index}]"
        if not review_slice["id"].startswith(prefix[review_slice["type"]]):
            _fail(f"{path}.id", "prefix does not match Slice type")
        bound_in_slice: set[str] = set()
        for binding_index, binding in enumerate(review_slice["requirement_bindings"]):
            binding_path = f"{path}.requirement_bindings[{binding_index}]"
            _require_refs([binding["requirement_id"]], requirement_ids, f"{binding_path}.requirement_id")
            if binding["requirement_id"] in bound_in_slice:
                _fail(f"{path}.requirement_bindings", "a Requirement must have one binding with one or more roles per Slice")
            bound_in_slice.add(binding["requirement_id"])
            invalid_roles = set(binding["roles"]) - ROLE_BY_SLICE_TYPE[review_slice["type"]]
            if invalid_roles:
                _fail(f"{binding_path}.roles", f"roles do not match Slice type: {', '.join(sorted(invalid_roles))}")
        slice_membership.update(bound_in_slice)
        for link_index, link in enumerate(review_slice["cross_slice_links"]):
            link_path = f"{path}.cross_slice_links[{link_index}]"
            _require_refs([link["slice_id"]], slice_ids, f"{link_path}.slice_id")
            if link["slice_id"] == review_slice["id"]:
                _fail(f"{link_path}.slice_id", "cannot link a Slice to itself")
            if slices[link["slice_id"]]["type"] != RELATION_TARGET_TYPE[link["relation"]]:
                _fail(link_path, "relation does not match target Slice type")
        exemption = review_slice["traceability_exemption"]
        if exemption is not None:
            if review_slice["type"] == "BEHAVIOR":
                _fail(f"{path}.traceability_exemption", "BEHAVIOR Slice cannot bypass traceability")
            _require_refs(exemption["requirement_ids"], requirement_ids, f"{path}.traceability_exemption.requirement_ids")
        testability = review_slice["testability"]
        if review_slice["fast_scan_done"] and testability is None:
            _fail(f"{path}.testability", "required after Fast Scan")
        if not review_slice["fast_scan_done"] and testability is not None:
            _fail(f"{path}.testability", "must be null before Fast Scan")
        _validate_behavior_coverage(review_slice, requirement_ids, path)
        verification = review_slice["verification"]
        if review_slice["fast_scan_done"] and verification is None:
            _fail(f"{path}.verification", "required after Fast Scan")
        if not review_slice["fast_scan_done"] and verification is not None:
            _fail(f"{path}.verification", "must be null before Fast Scan")
        if verification is not None:
            _validate_verification(verification, requirement_ids, f"{path}.verification")
        measurement = testability["measurement"] if testability is not None else None
        if testability is not None and review_slice["type"] in {"NFR", "CONSTRAINT"} and measurement is None:
            _fail(f"{path}.testability.measurement", "required for NFR/Constraint")
        if testability is not None and review_slice["type"] not in {"NFR", "CONSTRAINT"} and measurement is not None:
            _fail(f"{path}.testability.measurement", "must be null for Behavior/Rule")
        if review_slice["deep_challenge_status"] == "NOT_REQUIRED" and (review_slice["minimal_challenge"] == "SUSPICIOUS" or review_slice["risk_signals"]):
            _fail(f"{path}.deep_challenge_status", "Deep Challenge required by suspicion or risk signal")

    for index, requirement in enumerate(review["requirements"]):
        path = f"$.requirements[{index}]"
        if requirement["artifact_id"] not in artifact_ids:
            _fail(f"{path}.artifact_id", "unknown artifact")
        excluded = requirement["coverage_status"] == "EXCLUDED_WITH_REASON"
        if excluded != (requirement["exclusion_reason"] is not None):
            _fail(f"{path}.exclusion_reason", "does not match coverage_status")
        count = slice_membership[requirement["id"]]
        if requirement["coverage_status"] == "ASSIGNED_TO_SLICE" and count != 1:
            _fail(f"{path}.coverage_status", "assigned requirement must appear in exactly one Slice")
        if requirement["coverage_status"] != "ASSIGNED_TO_SLICE" and count != 0:
            _fail(f"{path}.coverage_status", "standalone or excluded requirement must not appear in a Slice")

    for index, decision in enumerate(review["critical_decisions"]):
        _require_refs(decision["requirement_ids"], requirement_ids, f"$.critical_decisions[{index}].requirement_ids")

    required_disproof_scopes = {"P0": {"GLOBAL"}, "P1": {"TARGETED", "GLOBAL"}, "P2": {"LOCAL", "TARGETED", "GLOBAL"}, "P3": {"BASIC", "LOCAL", "TARGETED", "GLOBAL"}}
    for index, finding in enumerate(review["findings"]):
        path = f"$.findings[{index}]"
        _require_refs(finding["requirement_ids"], requirement_ids, f"{path}.requirement_ids")
        _require_refs(finding["review_slice_ids"], slice_ids, f"{path}.review_slice_ids")
        _require_refs(finding["disproof"]["checked_requirement_ids"], requirement_ids, f"{path}.disproof.checked_requirement_ids")
        if finding["disproof"]["scope"] not in required_disproof_scopes[finding["severity"]]:
            _fail(f"{path}.disproof.scope", "insufficient for severity")
        if finding["severity"] in {"P0", "P1"} and finding["failure_witness"] is None and finding["contradiction_proof"] is None:
            _fail(path, "P0/P1 requires failure_witness or contradiction_proof")
        if finding["defect_type"] == "CONTRADICTORY" and (finding["contradiction_proof"] is None or len(finding["evidence"]) < 2):
            _fail(path, "contradiction requires proof and two Evidence entries")
        for evidence_index, evidence in enumerate(finding["evidence"]):
            _validate_evidence(evidence, artifacts, requirements, f"{path}.evidence[{evidence_index}]")
        if finding["contradiction_proof"]:
            for side in ("statement_a", "statement_b"):
                _require_refs([finding["contradiction_proof"][side]["requirement_id"]], requirement_ids, f"{path}.contradiction_proof.{side}.requirement_id")

    for index, observation in enumerate(review["observations"]):
        _require_refs(observation["requirement_ids"], requirement_ids, f"$.observations[{index}].requirement_ids")
        for evidence_index, evidence in enumerate(observation["evidence"]):
            _validate_evidence(evidence, artifacts, requirements, f"$.observations[{index}].evidence[{evidence_index}]")
    for index, question in enumerate(review["open_questions"]):
        path = f"$.open_questions[{index}]"
        _require_refs(question["requirement_ids"], requirement_ids, f"{path}.requirement_ids")
        _require_refs(question["finding_ids"], finding_ids, f"{path}.finding_ids")
        if question["answer_required"] and not question["finding_ids"]:
            _fail(f"{path}.finding_ids", "answer_required question must link to a confirmed Finding")
    for index, issue in enumerate(review["execution_issues"]):
        _require_refs(issue["artifact_ids"], artifact_ids, f"$.execution_issues[{index}].artifact_ids")
        _require_refs(issue["requirement_ids"], requirement_ids, f"$.execution_issues[{index}].requirement_ids")

    coverage = review["coverage"]
    actual_parsed = sum(item["parse_status"] == "PARSED" for item in review["artifacts"])
    expected_artifacts = {"total": len(review["artifacts"]), "parsed": actual_parsed, "failed": len(review["artifacts"]) - actual_parsed}
    if coverage["artifacts"] != expected_artifacts:
        _fail("$.coverage.artifacts", "counts do not match artifacts")
    status_counts = Counter(item["coverage_status"] for item in review["requirements"])
    expected_requirements = {"total": len(review["requirements"]), "assigned": status_counts["ASSIGNED_TO_SLICE"], "standalone": status_counts["STANDALONE_REVIEW"], "excluded": status_counts["EXCLUDED_WITH_REASON"], "unassigned": status_counts["UNASSIGNED"]}
    if coverage["requirements"] != expected_requirements:
        _fail("$.coverage.requirements", "counts do not match requirements")
    expected_slices = {
        "total": len(review["review_slices"]),
        "integrity_valid": sum(item["integrity_status"] == "VALID" for item in review["review_slices"]),
        "fast_scan_done": sum(item["fast_scan_done"] for item in review["review_slices"]),
        "minimal_challenge_done": sum(item["minimal_challenge"] != "NOT_RUN" for item in review["review_slices"]),
        "deep_challenge_done": sum(item["deep_challenge_status"] == "DONE" for item in review["review_slices"]),
        "deep_challenge_not_required": sum(item["deep_challenge_status"] == "NOT_REQUIRED" for item in review["review_slices"]),
    }
    if coverage["review_slices"] != expected_slices:
        _fail("$.coverage.review_slices", "counts do not match review_slices")
    behavior_counts = Counter(item["status"] for review_slice in review["review_slices"] for item in (review_slice["behavior_coverage"] or []))
    expected_behavior = {"total": sum(behavior_counts.values()), "defined": behavior_counts["DEFINED"], "partial": behavior_counts["PARTIAL"], "missing": behavior_counts["MISSING"], "not_applicable": behavior_counts["NOT_APPLICABLE"]}
    if coverage["behavior_dimensions"] != expected_behavior:
        _fail("$.coverage.behavior_dimensions", "counts do not match behavior coverage")
    verification_profiles = [item["verification"] for item in review["review_slices"] if item["verification"] is not None]
    verification_counts = Counter(item["status"] for item in verification_profiles)
    expected_verification = {"total": len(verification_profiles), "complete": verification_counts["COMPLETE"], "partial": verification_counts["PARTIAL"], "missing": verification_counts["MISSING"], "not_applicable": verification_counts["NOT_APPLICABLE"]}
    if coverage["verification"] != expected_verification:
        _fail("$.coverage.verification", "counts do not match Verification Profiles")

    severity_counts = Counter(item["severity"] for item in review["findings"])
    expected_summary = {
        "finding_count": len(review["findings"]), "blocking_finding_count": severity_counts["P0"] + severity_counts["P1"],
        "observation_count": len(review["observations"]), "open_question_count": len(review["open_questions"]),
        "severity_counts": {level: severity_counts[level] for level in ("P0", "P1", "P2", "P3")},
    }
    if review["summary"] != expected_summary:
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

    blocking_issue_ids = {item["id"] for item in review["execution_issues"] if item["blocking"]}
    incomplete_conditions = [
        not review["artifacts"], not review["requirements"],
        any(item["required"] and item["parse_status"] == "FAILED" for item in review["artifacts"]),
        expected_requirements["unassigned"] > 0,
        any(item["integrity_status"] != "VALID" for item in review["review_slices"]),
        any(not item["fast_scan_done"] for item in review["review_slices"]),
        any(item["minimal_challenge"] == "NOT_RUN" for item in review["review_slices"]),
        any(item["deep_challenge_status"] == "NOT_RUN" for item in review["review_slices"]),
        not coverage["critical_decision_guard_done"], not review["traceability"]["guard_done"], not coverage["completion_guard_done"],
        bool(blocking_issue_ids),
    ]
    should_be_incomplete = any(incomplete_conditions)
    if should_be_incomplete != (review["review_status"] == "INCOMPLETE"):
        _fail("$.review_status", "does not match Completion Guard evidence")
    if review["review_status"] == "INCOMPLETE" and not blocking_issue_ids:
        _fail("$.review_status", "INCOMPLETE requires a blocking execution issue")
    if review["review_status"] == "COMPLETED" and blocking_issue_ids:
        _fail("$.review_status", "COMPLETED cannot contain blocking execution issues")

    if check_verdict:
        expected = expected_verdict(review)
        if review["verdict"] != expected:
            _fail("$.verdict", f"must be {expected}")
        reasons = review["verdict_reasons"]
        if expected == "review_passed" and reasons:
            _fail("$.verdict_reasons", "PASS requires no reasons")
        if expected != "review_passed" and not reasons:
            _fail("$.verdict_reasons", "non-PASS requires reasons")
        required_ids = blocking_issue_ids if expected == "review_incomplete" else {item["id"] for item in review["findings"] if item["severity"] in {"P0", "P1"}}
        for item_id in required_ids:
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
