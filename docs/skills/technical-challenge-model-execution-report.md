# Technical Challenge Model — Execution Report

> Date: 2026-09-21  
> Branch: `technical-challenge-model-v1`  
> Base: `main@af678286c9d7024e0d3b1660e3d0d9e988df880e`  
> Release status: **PILOT**

## Execution mode

The Superpowers flow selected `subagent-driven-development`, but this harness has no independent subagent/model runner. Per Superpowers routing, execution continued with `executing-plans` while retaining TDD, verification-before-completion, and final self-review.

The runtime cannot clone GitHub directly, so branch files were read through the GitHub connector and materialized into a local verification workspace. Files changed during review were re-read from the remote branch after writeback.

## Deterministic verification

Fresh local verification after the final fixes:

```text
33/33 unittest cases PASS
dataset contract PASS
end-to-end validate -> adjudicate -> validate -> render PASS
Python py_compile PASS
```

Remote dataset inspection:

```text
20 development cases
10 candidate holdout cases
30 unique case IDs
design stages: architecture / high_level / detailed
mechanism lifecycle: existing / planned / modified / removed
output classes: finding / requirement_gap / evidence_gap / open_decision / pass
claim kinds: precondition / design-guarantee / existing-system-fact / platform / api / performance / compatibility
```

Remote `SKILL.md` word count: **382**, within the <=500-word compact-skill target.

## TDD fixes made during final review

### 1. Expert-adjudication key collision

RED exposed that report-local Finding IDs such as `F-002` can repeat across cases/runs. Aggregation previously keyed expert labels only by local Finding ID.

Fixed contract:

```text
<case_id>/<run_id>/<finding_id>
```

Regression coverage now verifies two runs containing the same local Finding ID can receive independent expert labels.

### 2. Inferred SystemConstraint scope gate

RED exposed that a HIGH/MEDIUM Finding could be anchored only to an `inferred` constraint.

Validator now rejects any formal Finding whose only anchors are inferred constraints. Such uncertainty must stay in EvidenceGap/OpenDecision until independently verified.

### 3. Counterexample claim-chain integrity

RED exposed that a Counterexample Finding could reference one Claim while its Counterexample referenced another.

Validator now requires the Finding and Counterexample to reference the same Claim.

### 4. Blocker evidence adequacy

RED exposed that a Blocker could pass with only weak evidence.

Validator now requires at least one referenced Evidence item with:

```text
adequacy = APPROPRIATE
```

## Semantic acceptance status

Production semantic acceptance is **not complete**.

This harness has no fresh-context/subagent/model runner, so it cannot validly execute:

- 5x fresh Dev RED/GREEN repetitions;
- frozen-wording semantic holdout runs;
- independent expert adjudication of semantic outputs;
- measured Recall / true Finding Precision / clean-case FP / inter-run stability.

Additionally, the current 10 holdout answer keys were inspected during harness verification. They are therefore candidate regression fixtures, not an unseen acceptance set for this authoring session. A future independent curator/runner must replace or re-seal an unseen holdout set.

No semantic quality threshold is claimed in this report.

## Final review status

Structural implementation is complete against the current Spec/Plan and deterministic gates are green.

Remaining production gate:

```text
fresh-context semantic evaluation
+ unseen holdout
+ independent expert adjudication
```

The branch has not been merged into `main`.
