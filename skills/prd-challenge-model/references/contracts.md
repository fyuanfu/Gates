# Canonical contracts · RGQ 2.0

## Contents

1. Boundary and migration
2. Invocation and input identity
3. Stable IDs and enums
4. Canonical model
5. Slice assessments
6. Findings, questions, and issues
7. Cross-field invariants
8. Verdict

## Boundary and migration

Review product requirement behavior within the supplied and approved scope. Use scope to bound analysis; do not judge whether the product goal is valuable or whether the scope should be larger. Do not review architecture, APIs, databases, code, framework choices, or technical feasibility.

Schema `2.0.0` is intentionally incompatible with `1.0.0`. It adds input identity, typed trace bindings, Behavior Coverage, Verification Profiles, and a Traceability Guard. Never silently upgrade a stored `1.0.0` result or reuse its Verdict for changed inputs.

## Invocation and input identity

Normalize the request to:

```json
{
  "artifacts": [
    {"path": "requirements/gallery-prd.md", "type": "PRD", "authority": "PRIMARY", "required": true, "source_version": null}
  ],
  "review_scope": {"iteration_goal": "", "included_sections": [], "excluded_sections": []},
  "options": {"risk_patterns_path": null, "android_mode": "AUTO", "output_dir": "prd-challenge-model-output", "execution_mode": "AUTO"}
}
```

Required direct-read formats are `.md`, `.txt`, `.json`, `.yaml`, `.yml`, and `.html`. Support PDF, DOCX, or images only when the runtime can extract them reliably. A required parse failure is blocking.

Artifact type:

```text
PRD | USER_STORY | AC | UX | BUSINESS_RULE | STATE | CONSTRAINT | NFR |
EXISTING_BEHAVIOR | RISK_PATTERN | OTHER_REQUIREMENT
```

Authority is `PRIMARY | SUPPORTING | CONTEXT`. Use explicit user precedence first. Never hard-code PRD above UX. Context may discover or disprove a candidate but cannot independently override Primary requirements.

For every Artifact calculate SHA-256 from the exact reviewed bytes and record optional source version. Calculate `review_context.input_fingerprint` as SHA-256 of canonical compact JSON containing:

```json
{
  "artifacts": [{"content_sha256": "...", "id": "A-001", "path": "...", "source_version": null}],
  "scope_snapshot": {"iteration_goal": "", "included_sections": [], "excluded_sections": []}
}
```

Sort Artifacts by ID and JSON object keys lexically; preserve scope-array order. A Verdict is reusable only for the same fingerprint and Skill version.

If the supplied boundary is insufficient to determine which sections or behavior belong to the review, record blocking `REVIEW_SCOPE_UNRESOLVED`. Requiring a boundary is not a review of product value or scope correctness.

## Stable IDs and enums

- Sort normalized absolute Artifact paths lexically; assign `A-001...`.
- Preserve business IDs in `source_requirement_id`; assign `R-{artifact_sequence}-{source_order}`.
- Assign Slice IDs as `S-BEH-001`, `S-RULE-001`, `S-CON-001`, or `S-NFR-001`.
- Assign `D-0001`, `F-0001`, `O-0001`, `Q-0001`, and `E-0001`.
- Sort confirmed candidates by lowest Requirement ID, defect type, and normalized title before assigning Finding IDs.

Quality dimension remains deliberately small:

```text
COMPLETENESS | CLARITY | CONSISTENCY
```

Coverage, Verification, Robustness, and Traceability are detection activities, not additional Finding dimensions.

Other key enums:

```text
Consequence:
IMPLEMENTATION_UNCERTAINTY | VERIFICATION_UNCERTAINTY |
BEHAVIORAL_CONTRADICTION | USER_VISIBLE_FAILURE

Defect type:
MISSING | AMBIGUOUS | CONTRADICTORY

Severity:
P0 | P1 | P2 | P3

Verdict:
review_passed | review_failed | review_incomplete
```

## Canonical model

`review.json` is the only source of truth and conforms to `review.schema.json`:

```json
{
  "schema_version": "2.0.0",
  "review_context": {"skill_version": "2.0.0", "scope_snapshot": {}, "input_fingerprint": "..."},
  "review_id": "REV-20260911-120000",
  "review_status": "COMPLETED",
  "verdict": "review_passed",
  "verdict_reasons": [],
  "summary": {},
  "artifacts": [],
  "requirements": [],
  "review_slices": [],
  "traceability": {"guard_done": true},
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

### Requirement and typed Slice binding

Requirement Coverage status is `ASSIGNED_TO_SLICE`, `STANDALONE_REVIEW`, `EXCLUDED_WITH_REASON`, or `UNASSIGNED`. An assigned Requirement appears in exactly one Slice, but one binding may hold several semantic roles:

```json
{"requirement_id": "R-001-0001", "roles": ["DEFINES_BEHAVIOR", "VERIFIES_BEHAVIOR"]}
```

Roles:

```text
BEHAVIOR: DEFINES_BEHAVIOR | VERIFIES_BEHAVIOR | DEFINES_STATE
BUSINESS_RULE: DEFINES_RULE
CONSTRAINT: DEFINES_CONSTRAINT
NFR: DEFINES_NFR
```

Cross-Slice links originate from the consuming Slice:

```json
{"slice_id": "S-RULE-001", "relation": "USES_RULE"}
```

Relations are `USES_RULE`, `SUBJECT_TO_CONSTRAINT`, `SUBJECT_TO_NFR`, and `RELATED_BEHAVIOR` and must point to the matching Slice type.

An unlinked global Rule/Constraint/NFR may use `traceability_exemption` only when an authoritative Requirement explicitly defines its global scope. Cite those Requirement IDs and explain the exemption. A BEHAVIOR Slice cannot use an exemption.

## Slice assessments

### Behavior Coverage

After Fast Scan, every BEHAVIOR Slice contains each of these exactly once:

```text
ACTOR | TRIGGER | PRECONDITION | SUCCESS | FAILURE | RECOVERY | STATE | FEEDBACK
```

Each item records `DEFINED | PARTIAL | MISSING | NOT_APPLICABLE`, Requirement evidence, and rationale. `DEFINED`, `PARTIAL`, and `MISSING` require source or in-scope anchor Requirements. `NOT_APPLICABLE` requires a reason and may have no Requirement IDs.

Coverage gaps create candidates, never automatic Findings. Qualify impact and run disproof before confirmation.

### Verification Profile

After Fast Scan, every Slice contains one Verification Profile:

```json
{
  "status": "PARTIAL",
  "basis": "EXPLICIT_SOURCE",
  "requirement_ids": ["R-001-0001"],
  "condition": "The upload is described as complete.",
  "expected_observable_result": "The UI displays success.",
  "decision_rule": null,
  "missing_elements": ["authoritative_success_definition"],
  "rationale": "The authoritative completion event is absent."
}
```

Rules:

- `COMPLETE`: use `EXPLICIT_SOURCE` or `NORMALIZED_FROM_SOURCE`; require condition, observable result, deterministic decision rule, source Requirements, and no missing elements.
- `PARTIAL`: require source Requirements and missing elements.
- `MISSING`: use `ABSENT`; cite an in-scope anchor and name missing elements.
- `NOT_APPLICABLE`: use `NOT_APPLICABLE`; leave evidence, fields, and missing elements empty; explain why.
- `NORMALIZED_FROM_SOURCE` may reorganize uniquely determined source meaning but cannot invent behavior.
- NFR/Constraint also retain the existing Measurement booleans.

Before Fast Scan, Testability, Behavior Coverage, and Verification remain null.

### Traceability Guard

Set `traceability.guard_done=true` only after checking:

1. every Behavior has a `DEFINES_BEHAVIOR` source;
2. every applicable Behavior has a Verification Profile;
3. every AC assigned to a Slice participates as `VERIFIES_BEHAVIOR`;
4. every Rule/Constraint/NFR links to an applicable Behavior or has an evidence-backed exemption;
5. every referenced ID exists.

Persist only typed bindings and links. Derive orphan ACs, unverified Behaviors, unlinked supporting Slices, and report counts; do not store duplicate gap lists.

Semantic gaps create candidates. Failure to execute the Guard creates blocking `TRACEABILITY_GUARD_NOT_RUN` and `review_incomplete`.

## Findings, questions, and issues

Put only CONFIRMED defects in `findings`. Every Finding needs source evidence, Requirement IDs, a downstream consequence, a detection method, and executed disproof. P0/P1 additionally needs a Failure Witness or Contradiction Proof.

Put harmless wording or formatting issues in `observations` without severity. Put questions needed to resolve a Finding in `open_questions` and link them through `finding_ids`. `answer_required=true` requires at least one confirmed Finding. Questions never directly change `review_status` or Verdict.

Use `execution_issues` only for review execution limitations. Blocking Issue codes include missing input, unresolved boundary, parse failure, unassigned Requirement, unresolved Slice Integrity, missing required stage, Traceability Guard not run, unavailable evidence, context exhaustion, or internal validation/render failure. `PROMPT_INJECTION_IGNORED` remains non-blocking evidence.

## Cross-field invariants

The deterministic Validator enforces at least:

1. schema and Skill versions equal `2.0.0`;
2. input fingerprint matches scope snapshot and Artifact identities;
3. all IDs are unique and references exist;
4. each assigned Requirement occurs in exactly one Slice;
5. Binding roles and link targets match Slice types;
6. Fast Scan completion matches Testability, Coverage, and Verification presence;
7. BEHAVIOR Coverage contains all eight dimensions exactly once;
8. Verification status matches evidence and required fields;
9. Coverage, Summary, and Metrics equal derived collections;
10. P0/P1 evidence and disproof budgets are satisfied;
11. `INCOMPLETE` has a blocking Execution Issue; completed reviews have none;
12. answer-required Questions link to confirmed Findings;
13. PASS has no reasons; non-PASS reasons reference every blocker.

## Verdict

Apply only:

```python
if review_status == "INCOMPLETE":
    verdict = "review_incomplete"
elif any(finding["severity"] in {"P0", "P1"} for finding in findings):
    verdict = "review_failed"
else:
    verdict = "review_passed"
```

Missing product decisions discovered by a completed review are Findings, not execution failures. A completed review with P2/P3 may pass this specific blocking policy; the report must still display those Findings.
