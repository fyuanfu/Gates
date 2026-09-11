# Review workflow

## Contents

1. Mission and scope
2. Fixed pipeline
3. Review Slice rules
4. Fast scan
5. Global decisions
6. Challenge and scope guard
7. Consequence and qualification
8. Disproof and candidate lifecycle
9. Completion and delegation

## Mission and scope

Find requirement defects that can propagate into implementation uncertainty, verification uncertainty, contradictory behavior, or user-visible failure. Do not score writing quality. Do not assess technical design or product strategy.

Treat the supplied product goal and iteration scope as fixed review axioms. The review does not ask whether the product should pursue another goal, serve another actor, add another capability, or expand to another platform/channel. It asks whether the already-committed behavior is sufficiently complete, clear, and consistent to remain correct and verifiable under realistic in-scope conditions.

The only Finding dimensions are `COMPLETENESS`, `CLARITY`, and `CONSISTENCY`. Testability is a probe that must resolve to one of those dimensions.

## Fixed pipeline

Execute all stages in this order:

| Stage | Action | Required evidence of completion |
|---|---|---|
| P0 | Initialize run | Fresh output directory and normalized input |
| P1 | Parse artifacts | Artifact parse status and errors |
| P2 | Artifact Index | Stable IDs for every artifact |
| P3 | Requirement Index | Atomic requirements with source order and quotes |
| P4 | Review Slices | All reviewable requirements assigned or standalone |
| P5 | Slice Integrity | Every Slice resolves to `VALID` |
| P6 | Coverage Guard | No unassigned Requirement |
| P7 | Unified Fast Scan | Four scans complete per Slice |
| P8 | Global Critical Decision Guard | One global index complete |
| P9 | Deep selection | Suspicion and deterministic signals recorded |
| P10 | Deep Challenge | `DONE` or `NOT_REQUIRED` per Slice |
| P11 | Consequence mapping | At least one consequence per retained candidate |
| P12 | Scope Guard | Every retained candidate proves relation to the current promise and is not scope expansion |
| P13 | Evidence qualification | Source/effect checks complete |
| P14 | Targeted disproof | Budget selected and executed |
| P15 | Resolve candidate | Final candidate state |
| P16 | Dedup and severity | One Finding per root cause |
| P17 | Completion Guard | `COMPLETED` or `INCOMPLETE` |
| P18 | Validate model | Pre-adjudication validation succeeds |
| P19 | Adjudicate | Deterministic Verdict written |
| P20 | Render Markdown | Human view generated from JSON |
| P21 | Contract verification | Final JSON validation succeeds |

Add a blocking Execution Issue when a required stage cannot complete. Do not continue with a false success.

## Review Slice rules

Use four Slice types:

### BEHAVIOR

Model Actor, Object, Trigger, Precondition, State, Success, Failure, Recovery, Dependency, and Feedback.

Minimal Challenge: "If implemented exactly as written, what is the smallest in-scope situation in which the user can still observe a wrong result?"

### BUSINESS_RULE

Model Condition, Scope, Exception, Conflict, and Observable Effect.

Minimal Challenge: "Is there a valid business situation in which this rule becomes contradictory, ambiguous, or impossible to apply?"

### CONSTRAINT

Model Applicability, Boundary, Exception, and Enforcement expectation.

Minimal Challenge: "Is there a boundary, exception, or scope interpretation that prevents unique enforcement?"

### NFR

Model Measurement Condition, Environment, Dataset scale, Start point, End point, Threshold, and Observable Result.

Minimal Challenge: "Is there a reasonable test condition under which satisfaction cannot be judged objectively?"

### Slice Integrity

Before review, detect requirements outside a Slice that share Actor, Object, State, Rule, Goal, Dependency, Outcome, or Constraint. Merge, split, or add a cross-Slice relation. The final `integrity_status` must be `VALID`.

Every Requirement must be exactly one of:

- `ASSIGNED_TO_SLICE`
- `STANDALONE_REVIEW`
- `EXCLUDED_WITH_REASON`

Never leave `UNASSIGNED`. Exclusion requires one reason allowed by the contract.

## Unified Fast Scan

Run exactly once for every Slice:

1. **Quality Scan:** look for missing, ambiguous, or contradictory Trigger, Precondition, Behavior, Result, Rule, State, Boundary, Exception, Dependency, Feedback, Constraint, and measurement condition.
2. **Testability Probe:** decide the fixed boolean fields from the contract. For NFR/Constraint, also complete Measurement.
3. **Minimal Challenge:** set `NO_SUSPICION` or `SUSPICIOUS` using the Slice-specific question.
4. **Local Consistency:** compare only related requirements clustered by Actor, Object, Action, State, Rule, Result, Term, Dependency, Goal, Constraint, or Metric.

For any missing-behavior candidate, identify the existing requirement or promised outcome that makes the missing behavior relevant. Do not create a candidate merely because a similar product could support it.

Do not confirm Findings or assign final severity during Fast Scan.

## Global Critical Decision Guard

Build a lightweight index keyed by `subject + action + property + scope`. Index at least state, success/failure definition, permission, ownership, deletion effect, persistence, retry, default, data effect, recovery, and identity scope. Generate a Consistency Candidate when the same key has mutually exclusive values.

Do not build a full knowledge graph or compare every Requirement pair.

## Deep Challenge

Run only when Minimal Challenge is `SUSPICIOUS` or a deterministic risk signal fires. Select only relevant families: State, Timing, Failure, Recovery, Dependency, Context, Boundary, Partial Success, Repeated Action, and Risk Pattern.

Construct challenges around the current promise, not adjacent product possibilities. Prefer the question: **"Under what realistic in-scope condition could the promised result become wrong, undefined, misleading, contradictory, unrecoverable, or unverifiable?"**

Risk patterns and industry knowledge may suggest realistic failure mechanisms, but they do not authorize new product scope. A pattern is useful only when it exposes a failure of behavior already promised by the supplied requirements.

## Scope Guard

Apply the Scope Guard to every candidate before evidence qualification.

A candidate may continue only when all of the following are true:

1. **Scope anchor:** at least one supplied requirement, rule, scenario, interaction, constraint, NFR, or explicitly stated outcome proves that the affected behavior is already in scope.
2. **Promise relation:** the candidate protects the correctness, determinism, recoverability, consistency, or verifiability of that existing behavior.
3. **Failure witness:** there is a realistic condition under which omitting or leaving the candidate unresolved can make the current promise fail, become ambiguous, produce a wrong/false result, or prevent unique verification.
4. **No new product objective:** resolving the candidate does not require introducing a materially new product goal, actor, standalone capability, supported platform/channel, external integration, monetization model, or unrelated future use case.

Use this decisive test:

> **If this candidate is rejected, can the current in-scope promise still be implemented and verified correctly under the identified realistic condition?**

- If **yes**, classify it as enhancement, preference, future idea, or unrelated scope and drop it from Findings.
- If **no**, retain it for completeness/clarity/consistency qualification.

Do not confuse failure handling with feature expansion. For example, specifying what happens when an in-scope upload is interrupted may be required to prevent false success or inconsistent state; proposing support for a new cloud provider is a new capability and must be dropped unless that provider is already in scope.

Typical **in-scope completeness** candidates include missing behavior for an already-relevant state transition, natural interruption, partial success, retry/recovery semantics, dependency failure, duplicate action, boundary condition, or user feedback where omission can break the current promised result.

Typical **scope expansion** candidates include new target users, new business goals, optional convenience features, unrelated channels/platforms, additional third-party services, new monetization, new sharing/collaboration modes, or speculative future scenarios whose absence does not break the current promise.

## Consequence and qualification

Map every Scope-Guard-retained candidate to at least one contract consequence. Then require all of:

- a Source Anchor;
- current scope relevance;
- an effect on defined behavior;
- a real downstream consequence;
- not a product enhancement;
- not a technical preference;
- not an unsupported guess.

Candidates failing these checks become Observation or DROPPED.

## Disproof and lifecycle

Search in order: related requirements, same Slice, cross-Slice relations, Critical Decision Index, local evidence, then global authorized evidence when necessary. Actively try to show the candidate is false.

Disproof must also test scope: search for text that narrows the affected condition out of the current iteration or proves that the allegedly required behavior is intentionally excluded. If so, reject the candidate rather than silently expanding scope.

Use this state machine:

```text
DISCOVERED
  -> SCOPE_GUARDED -> QUALIFIED -> CONFIRMED
                                 -> REJECTED
                                 -> NEEDS_CONTEXT
  -> OBSERVATION
  -> DROPPED
```

Only CONFIRMED candidates become Findings. If disproof succeeds, use REJECTED rather than lowering severity. NEEDS_CONTEXT becomes an Open Question unless the missing decision itself proves a MISSING defect.

## Completion and delegation

Set `INCOMPLETE` when a required artifact fails parsing, a Requirement is unassigned, integrity remains unresolved, a required stage is missing, critical evidence is unavailable, coverage arithmetic is inconsistent, the Global Guard is absent, a blocking issue/question exists, validation fails, or context capacity prevents full protection.

When delegating, the coordinator owns parsing, indexing, slicing, integrity, coverage, the Global Guard, Scope Guard, deduplication, severity, completion, and Verdict. Delegate only Slice packets; never duplicate full-document review.

The non-removable protections are Coverage Guard, Slice Integrity, Minimal Challenge for every Slice, Global Critical Decision Guard, Scope Guard, P0/P1 disproof, P0/P1 witness/proof, source evidence for every Finding, Completion Guard, open challenge beyond patterns, and deterministic final validation/adjudication.
