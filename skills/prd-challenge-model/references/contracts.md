# Canonical contracts

## Contents

1. Invocation
2. Stable IDs
3. Enumerations
4. Canonical model
5. Object contracts
6. Cross-field invariants
7. Verdict

## Invocation

Normalize the user request to:

```json
{
  "artifacts": [
    {
      "path": "requirements/gallery-prd.md",
      "type": "PRD",
      "authority": "PRIMARY",
      "required": true
    }
  ],
  "review_scope": {
    "iteration_goal": "",
    "included_sections": [],
    "excluded_sections": []
  },
  "options": {
    "risk_patterns_path": null,
    "output_dir": "prd-challenge-model-output",
    "execution_mode": "AUTO"
  }
}
```

Required direct-read formats are `.md`, `.txt`, `.json`, `.yaml`, `.yml`, and `.html`. Support PDF, DOCX, or images only when the runtime can extract them reliably. A required parse failure is blocking. Do not silently ignore any artifact.

Artifact type:

```text
PRD | USER_STORY | AC | UX | BUSINESS_RULE | STATE | CONSTRAINT | NFR |
EXISTING_BEHAVIOR | RISK_PATTERN | OTHER_REQUIREMENT
```

Authority:

```text
PRIMARY | SUPPORTING | CONTEXT
```

Use explicit user precedence first. Treat unspecified authority as PRIMARY. A PRIMARY/PRIMARY conflict is a candidate. A PRIMARY/SUPPORTING conflict is still reportable but the PRIMARY describes the expected behavior. CONTEXT can discover or disprove a candidate but cannot independently override PRIMARY. Never hard-code PRD above UX.

Execution mode:

```text
AUTO | SINGLE_AGENT | DELEGATED
```

No requirement artifact, only technical-design input, or an owner-dependent review boundary that cannot be determined produces `review_incomplete`. The Canonical Model therefore permits empty Artifact and Requirement arrays only when a blocking Issue/Question explains the incomplete run.

## Stable IDs

- Sort normalized absolute artifact paths lexically and assign `A-001...`.
- Preserve an existing business ID as `source_requirement_id`; assign internal Requirement IDs as `R-{artifact_sequence}-{source_order}`, for example `R-001-0007`.
- Assign Slice IDs as `S-BEH-001`, `S-RULE-001`, `S-CON-001`, or `S-NFR-001`.
- Assign `D-0001`, `F-0001`, `O-0001`, `Q-0001`, and `E-0001` to decisions, findings, observations, questions, and issues.
- Sort candidates before assigning final IDs by lowest Requirement ID, then defect type, then normalized title.

## Enumerations

Consequence:

```text
IMPLEMENTATION_UNCERTAINTY | VERIFICATION_UNCERTAINTY |
BEHAVIORAL_CONTRADICTION | USER_VISIBLE_FAILURE
```

Quality dimension:

```text
COMPLETENESS | CLARITY | CONSISTENCY
```

Defect type:

```text
MISSING | AMBIGUOUS | CONTRADICTORY
```

Severity and Verdict:

```text
P0 | P1 | P2 | P3
review_passed | review_failed | review_incomplete
```

Execution issue code:

```text
NO_REQUIREMENT_INPUT | UNSUPPORTED_FORMAT | ARTIFACT_PARSE_FAILED |
REQUIREMENT_UNASSIGNED | SLICE_INTEGRITY_UNRESOLVED |
REQUIRED_STEP_MISSING | CRITICAL_EVIDENCE_UNAVAILABLE |
CONTRACT_VALIDATION_FAILED | RENDER_FAILED | CONTEXT_CAPACITY_EXCEEDED |
PROMPT_INJECTION_IGNORED | INTERNAL_EXECUTION_ERROR
```

Detected by:

```text
QUALITY_SCAN | TESTABILITY_PROBE | MINIMAL_CHALLENGE | LOCAL_CONSISTENCY |
GLOBAL_DECISION_GUARD | DEEP_CHALLENGE | RISK_PATTERN
```

## Canonical model

`review.json` is the only source of truth. It must conform to `review.schema.json` and contain:

```json
{
  "schema_version": "1.0.0",
  "review_id": "REV-20260910-120000",
  "review_status": "COMPLETED",
  "verdict": "review_passed",
  "verdict_reasons": [],
  "summary": {},
  "artifacts": [],
  "requirements": [],
  "review_slices": [],
  "critical_decisions": [],
  "findings": [],
  "observations": [],
  "open_questions": [],
  "coverage": {},
  "execution_issues": [],
  "metrics": {}
}
```

Use source-language prose and fixed English keys/enums. Do not expose hidden reasoning.

## Object contracts

### Summary

`finding_count`, `blocking_finding_count`, `observation_count`, and `open_question_count` are non-negative integers. `severity_counts` contains exactly `P0`, `P1`, `P2`, and `P3` non-negative counts.

### Artifact

Required fields: `id`, `path`, `type`, `authority`, `required`, `parse_status`, `parse_error`. Parse status is `PARSED` or `FAILED`; parse error is a string or null.

### Requirement

Required fields: `id`, `artifact_id`, `source_requirement_id`, `section`, `source_order`, `type`, `title`, `text`, `coverage_status`, `exclusion_reason`.

Coverage status is `ASSIGNED_TO_SLICE`, `STANDALONE_REVIEW`, `EXCLUDED_WITH_REASON`, or `UNASSIGNED`. `UNASSIGNED` is representable only so an incomplete run remains machine-readable; it always blocks release. Exclusion reason is null unless excluded, then exactly one of `OUT_OF_SCOPE_TECHNICAL`, `DUPLICATE_SOURCE`, `SUPERSEDED`, `NON_REQUIREMENT_CONTENT`, or `USER_EXCLUDED`.

### Review Slice

Required fields: `id`, `type`, `title`, `goal_or_rule`, `requirement_ids`, `cross_slice_ids`, `integrity_status`, `fast_scan_done`, `minimal_challenge`, `deep_challenge_status`, `risk_signals`, `testability`.

Type is `BEHAVIOR`, `BUSINESS_RULE`, `CONSTRAINT`, or `NFR`. Integrity status is `VALID`, `MERGE_REQUIRED`, `SPLIT_REQUIRED`, or `CROSS_SLICE_RELATION_REQUIRED`. Any non-VALID value is representable for an incomplete run but blocks release. Minimal challenge is `NO_SUSPICION`, `SUSPICIOUS`, or `NOT_RUN`; Deep Challenge is `DONE`, `NOT_REQUIRED`, or `NOT_RUN`. `fast_scan_done=false` or any `NOT_RUN` blocks release.

Testability is null until Fast Scan completes. A completed Testability object contains four booleans: `trigger_determinable`, `precondition_constructible`, `outcome_observable`, and `oracle_deterministic`. `measurement` is null except for NFR/Constraint, where it contains five booleans: `condition_defined`, `start_point_defined`, `end_point_defined`, `threshold_defined`, and `environment_defined`.

### Critical Decision

Required fields: `id`, `subject`, `action`, `property`, `scope`, `value`, and non-empty `requirement_ids`. Property is one of `STATE`, `SUCCESS_DEFINITION`, `FAILURE_DEFINITION`, `PERMISSION`, `OWNERSHIP`, `DELETION_EFFECT`, `PERSISTENCE`, `RETRY`, `DEFAULT`, `DATA_EFFECT`, `RECOVERY`, or `IDENTITY_SCOPE`.

### Evidence

Required fields: `artifact_id`, nullable `requirement_id`, `source_path`, `section`, and `quote`. Quote the shortest sufficient original excerpt. Contradictions require two mutually exclusive source excerpts. Missing Findings may cite an anchor that proves the behavior is in scope but leaves the outcome undefined.

### Disproof

Required fields: `executed`, `scope`, `outcome`, `checked_requirement_ids`, and `summary`. Scope is `BASIC`, `LOCAL`, `TARGETED`, or `GLOBAL`. A Finding always has `executed=true` and `outcome=CONFIRMED`.

### Finding

Required fields:

```text
id | status | severity | quality_dimension | defect_type |
consequence_types | review_slice_ids | requirement_ids | title | problem |
impact | required_decision | evidence | testability | detected_by | disproof |
failure_witness | contradiction_proof
```

Status is always `CONFIRMED`. `review_slice_ids` may be empty for Standalone Review; `requirement_ids`, `consequence_types`, `evidence`, and `detected_by` must be non-empty.

### Observation

Required fields: `id`, `title`, `description`, `requirement_ids`, and `evidence`. It has no severity, defect type, or consequence.

### Open Question

Required fields: `id`, `question`, `reason`, `requirement_ids`, `blocking`, and `requested_from`. Requested from is `PRODUCT`, `UX`, `BUSINESS`, `REQUIREMENT_OWNER`, or `UNKNOWN`.

### Execution Issue

Required fields: `id`, `code`, `message`, `blocking`, `artifact_ids`, and `requirement_ids`.

### Coverage

```json
{
  "artifacts": {"total": 1, "parsed": 1, "failed": 0},
  "requirements": {"total": 1, "assigned": 1, "standalone": 0, "excluded": 0, "unassigned": 0},
  "review_slices": {
    "total": 1,
    "integrity_valid": 1,
    "fast_scan_done": 1,
    "minimal_challenge_done": 1,
    "deep_challenge_done": 0,
    "deep_challenge_not_required": 1
  },
  "critical_decision_guard_done": true,
  "completion_guard_done": true
}
```

### Metrics

Required non-negative integers: `raw_candidate_count`, `qualified_candidate_count`, `confirmed_candidate_count`, `rejected_candidate_count`, `dropped_candidate_count`, `deep_challenge_trigger_count`, and `review_slice_count`.

## Cross-field invariants

1. All object IDs are unique in their collection and match the schema pattern.
2. Every referenced Artifact, Requirement, and Slice ID exists.
3. `artifacts.total = parsed + failed = len(artifacts)`.
4. `requirements.total = assigned + standalone + excluded + unassigned = len(requirements)`.
5. Slice Coverage counts equal actual Slice states; completed reviews require all integrity valid, Fast Scan done, and Minimal Challenge done.
6. Completed reviews require every Slice's Deep Challenge to be done or explicitly not required.
7. Coverage counts equal actual object fields.
8. Every Finding has at least one consequence, Requirement, Evidence item, and detection method.
9. Every Finding's disproof executed is true and outcome is CONFIRMED.
10. P0/P1 has a Failure Witness or Contradiction Proof.
11. CONTRADICTORY has a Contradiction Proof and at least two Evidence entries.
12. Observation contains none of the Finding-only fields.
13. Summary and Metrics counts equal their source arrays.
14. `INCOMPLETE` has a blocking Issue/Question and a reason referencing its ID.
15. `COMPLETED` has no blocking Issue/Question.
16. PASS has empty reasons; non-PASS has at least one reason.

## Verdict

The script applies only:

```python
if review_status == "INCOMPLETE":
    verdict = "review_incomplete"
elif any(f["severity"] in {"P0", "P1"} for f in findings):
    verdict = "review_failed"
else:
    verdict = "review_passed"
```

Precedence is incomplete, failed, then passed. A review can be incomplete and still display confirmed blockers. PASS means this completed review found no confirmed P0/P1; it does not establish global development readiness.
