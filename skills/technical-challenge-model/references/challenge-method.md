# Challenge method

## 1. Calibrate by design stage

Do not review every document at detailed-design depth.

| design_stage | Required challenge depth | Do not demand yet |
|---|---|---|
| `architecture` | boundaries, major decisions, dependencies, high-level state ownership, quality/failure strategy | method names, DB fields, transaction ordering details |
| `high_level` | component responsibilities, state ownership, protocol, recovery, persistence strategy, compatibility and major concurrency semantics | line-level implementation details |
| `detailed` | explicit state transitions, ordering, transaction boundaries, retry semantics, key lifecycle, migration sequence, concurrency guards | nothing needed solely for implementation syntax |

A missing detail is a Finding only if it is required at the declared stage to establish design correctness.

## 2. Build coverage first

Map each accepted RequirementObligation and relevant SystemConstraint to DesignDecisions and Mechanisms.

Coverage states:

```text
COVERED | PARTIAL | MISSING | CONTRADICTED | UNCLEAR
```

### Coverage Finding

Use this path when an accepted anchor is explicitly missing or contradicted by the design:

```text
Obligation / verified-or-curated Constraint
→ coverage MISSING or CONTRADICTED
→ appropriate source/design evidence
→ DESIGN_COVERAGE_GAP or DESIGN_CONTRADICTION
```

Do not manufacture a Counterexample merely to justify an obvious missing mechanism.

## 3. Derive critical precondition claims

For each significant decision ask:

> What must be true for this decision to correctly satisfy the linked obligation and preserve the linked constraint?

Typical kinds include state validity, ordering, atomicity, idempotency, uniqueness, availability, persistence, and compatibility.

## 4. Select only relevant challenge lenses

Prefer typed Mechanism semantics over keyword matching.

Examples:

- retry scheduler → idempotency, concurrency, ordering, persistence, lifecycle
- persistent store → atomicity, crash consistency, migration, compatibility
- callback/event source → duplicate, reorder, delay, stale state
- remote dependency → timeout, ambiguous success, degradation, retry

Keywords are fallback extraction hints, never the primary routing model.

## 5. Search counterexamples

Mutation library:

```text
Duplicate | Delay | Drop | Reorder | Restart | Partial Success |
Stale State | Concurrent Execution | Dependency Degradation
```

For each critical precondition claim:

1. negate the claim;
2. select one plausible mutation;
3. propagate it through the relevant mechanisms;
4. observe the resulting state;
5. identify the violated obligation/constraint;
6. resolve the claim with evidence.

### Counterexample Finding

Use this path for implementation-dependent failure:

```text
Decision → Mechanism → Claim(kind=precondition or guarantee)
→ plausible Counterexample → anchor violation → adequate Evidence → Finding
```

Counterexample Findings require both `claim_id` and `counterexample_id`.

## 6. Brownfield retrieval

Retrieve only what a current Claim requires:

```text
Level 1: design-referenced symbols/modules
Level 2: direct dependencies of challenged decisions
Level 3: targeted evidence needed to support/refute a Claim
```

Do not scan the whole repository before forming a review hypothesis.

Feature Tree, historical requirements, historical bugs, and RiskPatterns can expose hidden existing constraints or choose lenses. They are challenge seeds, not present-defect proof.

## 7. Stop condition

Stop when all critical anchors have coverage, relevant system constraints are considered, significant decisions are analyzed at stage-appropriate depth, critical precondition claims are challenged, high-risk candidates are evidence-resolved, and no selected risk lens remains uncovered.
