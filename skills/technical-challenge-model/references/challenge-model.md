# Canonical challenge model

The challenge model is deliberately small. Every high-confidence conclusion must be traceable through these objects.

## RequirementObligation

An accepted behavior that the current feature must realize. It may come from PRD, AC, Scenario, Rule, State, Invariant, NFR, or an approved requirement decision.

Required semantics:

- `id`
- `source_ref`
- `statement`
- `invariants[]`

Do not create a RequirementObligation from architecture preference, industry convention, historical bug, or the technical design itself.

## SystemConstraint

A behavior or invariant the existing system must continue to preserve even when the current PRD does not restate it.

Authority:

- `verified`: directly supported by current code, contract, validated architecture rule, or authoritative system documentation.
- `curated`: intentionally maintained architecture/domain constraint with an identifiable source.
- `inferred`: discovered from history, Feature Tree relations, naming, code shape, or model inference and not yet independently verified.

An `inferred` SystemConstraint is a challenge candidate, not an independent Blocker anchor until verified.

## DesignDecision

An architecturally significant choice. Changing it materially changes behavior realization, state ownership, consistency, dependencies, quality attributes, compatibility, or failure modes.

Examples: scheduling, retry, persistence, state ownership, concurrency, idempotency, protocol, migration, compatibility, cache strategy, security boundary.

## Mechanism

The concrete technical construct that realizes a DesignDecision.

Lifecycle is mandatory:

- `existing`
- `planned`
- `modified`
- `removed`

Decision answers **what/why was chosen**. Mechanism answers **what technical construct makes it work**.

## Claim

A statement whose truth matters to the design.

Claim kinds:

- `precondition`
- `design-guarantee`
- `existing-system-fact`
- `platform`
- `api`
- `performance`
- `compatibility`

**Precondition is a Claim kind.** Do not maintain a duplicate or parallel precondition object. A precondition claim answers: **what must be true for this decision to correctly satisfy its anchor?**

Claim status:

- `VERIFIED`
- `SUPPORTED`
- `ASSUMED`
- `UNKNOWN`
- `CONTRADICTED`

## Counterexample

A plausible implementation-dependent failure path that challenges one Claim and can violate an obligation or system constraint.

Counterexamples are not required for obvious coverage failures. They are required for the Counterexample Finding path.

## Evidence

Evidence supports or refutes a Claim. Evidence adequacy depends on Claim type, source scope, mechanism lifecycle, and design stage. Evidence rules live in `evidence-and-findings.md`.

## Relations

```text
RequirementObligation SATISFIED_BY Mechanism
SystemConstraint PRESERVED_BY Mechanism
DesignDecision REALIZED_BY Mechanism
DesignDecision REQUIRES Claim(kind=precondition)
Counterexample CHALLENGES Claim
Evidence SUPPORTS|REFUTES Claim
Finding VIOLATES RequirementObligation|SystemConstraint
```
