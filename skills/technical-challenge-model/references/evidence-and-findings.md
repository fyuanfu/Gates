# Evidence, findings, gaps, and verdicts

## Claim-appropriate evidence

Do not rank evidence globally. Ask what kind of evidence can actually support or refute this Claim.

| Claim type | Appropriate evidence |
|---|---|
| platform | official platform contract plus focused test when needed |
| existing-system-fact | current code, runtime behavior, static analysis |
| api | API contract and/or server implementation |
| performance | benchmark or load measurement under stated conditions |
| failure recovery | fault-injection or recovery test; contract where authoritative |
| compatibility | schemas, version contract, migration logic/tests |
| planned design guarantee | Technical Design plus compatible external contracts |

Evidence status on the Claim remains `VERIFIED`, `SUPPORTED`, `ASSUMED`, `UNKNOWN`, or `CONTRADICTED`.

## Mechanism lifecycle evidence matrix

- `existing`: current code/runtime is primary evidence.
- `planned`: current-code absence is not negative evidence; inspect design completeness and external compatibility.
- `modified`: inspect both existing behavior and the proposed delta; neither side alone is sufficient.
- `removed`: inspect current dependents and removal impact; absence after the change is intended only when all required dependencies are closed.

A targeted search that finds nothing means **no supporting evidence found in the searched scope**. It does not prove non-existence unless the scope is authoritative/exhaustive.

## SystemConstraint authority gate

A `verified` or `curated` SystemConstraint may directly anchor a Finding.

An **inferred SystemConstraint** must first be independently verified. Until then, route uncertainty to `EvidenceGap` or `OpenDecision`; it cannot independently anchor a Technical Finding at any severity.

Historical bugs, RiskPatterns, and Feature Tree relations are Challenge Seeds. Verify the current design before creating a Finding.

## Two Finding paths

### Coverage Finding

Required when explicit accepted behavior/system constraint is missing or contradicted. Counterexample is optional.

Typical types:

- `DESIGN_COVERAGE_GAP`
- `DESIGN_CONTRADICTION`

### Counterexample Finding

Required for an implementation-dependent failure mode. Must include a critical Claim, a plausible Counterexample, anchor impact, and appropriate evidence.

Typical types include state, timing, concurrency, idempotency, atomicity, dependency, compatibility, migration, and architecture-conformance gaps.

## Finding vs gaps

`Technical Finding`: adequate evidence shows the design is defective.

`RequirementGap`: expected product behavior is undefined. Do not decide it inside Technical Challenge.

`EvidenceGap`: an important factual/design Claim remains unverified. For example, a quantitative latency claim without a benchmark. Set `critical=true` only when the declared design stage requires that Claim to approve the design; a critical EvidenceGap blocks the Gate but remains an uncertainty, not a Technical Finding.

`OpenDecision`: known architecture alternatives exist and an architecture owner must intentionally choose among them. It is not a missing product requirement and not merely missing factual evidence.

## Severity

- `BLOCKER`: a core obligation/constraint can be violated and no acceptable mitigation exists; at least one referenced Evidence item with `adequacy=APPROPRIATE` is mandatory.
- `HIGH`: serious violation is plausible and supported, but uncertainty or partial mitigation remains.
- `MEDIUM`: real weakness with bounded impact or easy implementation-stage closure.
- `LOW`: non-blocking robustness or technical debt.

`UNKNOWN` is not a severity. Unresolved truth belongs in EvidenceGap/OpenDecision.

## Verdict and assurance

Verdict:

```text
BLOCKED | NEEDS_DECISION | PASS_WITH_ACTIONS | PASS
```

Assurance:

```text
DOCUMENT_ONLY | CONTEXT_GROUNDED | REPOSITORY_GROUNDED | EVIDENCE_VERIFIED
```

Verdict answers what the review found. Assurance answers how strongly the result is grounded. A document-only PASS is not equivalent to an evidence-verified PASS.
