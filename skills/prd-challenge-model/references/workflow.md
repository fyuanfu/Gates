# Review workflow · RGQ 2.0

## Contents

1. Mission and boundaries
2. Fixed pipeline
3. Indexing and Slice Integrity
4. RGQ Fast Scan
5. Global and Deep Challenge
6. Qualification and disproof
7. Traceability and completion
8. Delegation and cost controls

## Mission and boundaries

Find requirement defects that can cause divergent implementation, non-deterministic verification, conflict with authoritative product behavior, or user-visible failure. Work only inside the approved product scope. Treat scope as an input boundary, not an object for value or priority review.

Review only product behavior. Ignore technical implementation text except to classify it as non-requirement input. Never recommend architecture, APIs, storage, frameworks, jobs, or additional features.

The only Finding dimensions are `COMPLETENESS`, `CLARITY`, and `CONSISTENCY`. Coverage, Verification, Robustness Challenge, and Traceability are detection activities whose candidates must resolve to one of those three dimensions.

## Fixed pipeline

Execute in order:

| Stage | Output | Stop condition |
|---|---|---|
| P1 | Invocation and scope snapshot | Boundary cannot be established |
| P2 | Artifact hashes and input fingerprint | Required input inaccessible |
| P3 | Artifact Index and parse results | Required parse failure |
| P4 | Requirement Index | No product requirement input |
| P5 | Typed Review Slices | Requirement cannot be assigned |
| P6 | Slice Integrity | Merge/split/relation unresolved |
| P7 | Behavior Coverage | Fast Scan cannot complete |
| P8 | Clarity and local consistency | Fast Scan cannot complete |
| P9 | Testability and Verification Profile | Fast Scan cannot complete |
| P10 | Minimal Challenge | Any Slice not challenged |
| P11 | Global Critical Decision Guard | Global guard cannot run |
| P12 | Risk selection | Record only fired signals |
| P13 | Conditional Deep Challenge | Required challenge not run |
| P14 | Consequence mapping | Drop candidates without a permitted consequence |
| P15 | Finding qualification | Drop enhancements, preferences, and guesses |
| P16 | Disproof | Do not confirm unresolved candidates |
| P17 | Candidate lifecycle | CONFIRMED / REJECTED / NEEDS_CONTEXT / OBSERVATION / DROPPED |
| P18 | Traceability Guard | Guard cannot complete |
| P19 | Deduplication and severity | Preserve strongest evidence and consequence |
| P20 | Completion Guard | Any execution protection missing |
| P21 | Canonical `review.json` | Schema or invariant failure |
| P22 | Adjudicate, revalidate, render | Script failure |

An empty Findings array never proves that the pipeline completed.

## Indexing and Slice Integrity

Parse every supplied Artifact and calculate SHA-256 from exact bytes. Extract atomic product Requirements in source order without repairing missing behavior. Bind each assigned Requirement to exactly one primary Slice with one or more roles.

Build:

- `BEHAVIOR`: actor, object, trigger, precondition, state, success, failure, recovery, dependency, and feedback belonging to one user/business behavior;
- `BUSINESS_RULE`: authoritative permission, prohibition, calculation, ownership, default, retention, retry, or data-effect rule;
- `CONSTRAINT`: product boundary or externally imposed product constraint;
- `NFR`: measurable performance, stability, availability, security, privacy, capacity, or compatibility commitment.

Keep related Requirements together. Split independent behaviors. Use typed Cross-Slice links for Rules, Constraints, and NFRs consumed by a Behavior. Use a traceability exemption only when source text explicitly defines a global applicability scope.

## RGQ Fast Scan

Run the following exactly once per valid Slice.

### 1. Behavior Coverage

For each BEHAVIOR assess `ACTOR`, `TRIGGER`, `PRECONDITION`, `SUCCESS`, `FAILURE`, `RECOVERY`, `STATE`, and `FEEDBACK` as `DEFINED`, `PARTIAL`, `MISSING`, or `NOT_APPLICABLE`. Cite source or in-scope anchor Requirement IDs and give an auditable rationale.

Do not assume every gap is a defect. Ask whether the missing or partial behavior permits materially different implementations, prevents deterministic verification, contradicts authoritative behavior, or exposes a wrong user result.

### 2. Clarity and consistency

Check ambiguous terms, conditions, quantities, ownership, state, ordering, exceptions, feedback, and metrics. Confirm AMBIGUOUS only when at least two reasonable product behaviors remain possible. Compare local actor/object/action/state/rule/result/term meanings within the Slice.

### 3. Testability and Verification

Complete Testability booleans and the Verification Profile. Extract or normalize only source-determined condition, observable result, and decision rule. Mark missing elements rather than inventing an Oracle.

For NFR/Constraint also assess Measurement Condition, Environment, Dataset scale, Start point, End point, Threshold, and Observable Result.

### 4. Minimal Challenge

Ask one bounded question per Slice:

> If this requirement were implemented literally, what is the smallest in-scope condition that could still produce a materially wrong user or business result?

Set `NO_SUSPICION` only when no deterministic risk signal, semantic gap, or counterexample is found.

## Global and Deep Challenge

Build a Critical Decision Index using `subject + action + property + scope`. Compare state, success, failure, permission, ownership, deletion effect, persistence, retry, default, data effect, recovery, and identity scope across all authoritative inputs.

Run Deep Challenge only when Minimal Challenge is suspicious or a deterministic signal fires. Select only applicable families: state, timing, failure, recovery, dependency, boundary, partial success, repeated action, data effect, permission, identity, concurrency, or NFR measurement.

Read `risk-patterns.json` only after a matching signal fires. Read `risk-patterns-android.json` only when all are true:

1. the supplied product scope explicitly identifies Android;
2. the reviewed behavior includes the relevant platform dependency;
3. a matching risk signal fires.

Use Android patterns to challenge product behavior after denial, interruption, or platform variation already in scope. Never convert them into implementation prescriptions or requests to support additional devices, OS versions, or OEMs.

Preserve one open challenge beyond historical patterns so the library does not limit exploration.

## Qualification and disproof

Keep a candidate only if it maps to one or more:

```text
IMPLEMENTATION_UNCERTAINTY
VERIFICATION_UNCERTAINTY
BEHAVIORAL_CONTRADICTION
USER_VISIBLE_FAILURE
```

Drop style comments, optional improvements, preferences, technical suggestions, new-feature proposals, or risks unsupported by the supplied scope.

Before confirming every candidate, search for conditions, precedence, definitions, exclusions, later sections, global rules, or contextual evidence that resolves it. Use at least BASIC disproof for P3, LOCAL for P2, TARGETED for P1, and GLOBAL for P0. P0/P1 also requires a concrete Failure Witness or mutually exclusive Contradiction Proof.

When missing product information itself already makes implementation or verification indeterminate, confirm a MISSING Finding and optionally attach an answer-required Open Question. Do not change the run to `INCOMPLETE`.

## Traceability and completion

After candidate resolution, run the Traceability Guard over typed relations. Derive, but do not persist, missing Behavior sources, orphan ACs, incomplete Behavior Verification, and unlinked supporting Slices. A derived gap is a candidate, not automatic proof of a defect.

Set `INCOMPLETE` only for execution failure: missing/unreadable required input, unresolved boundary, unassigned Requirement, unresolved Slice Integrity, missing required scan/challenge/global/traceability stage, invalid evidence or fingerprint, context exhaustion, or failed validation/rendering. Every incomplete result needs a blocking Execution Issue.

Questions discovered during a completed review never make the run incomplete. They must link to confirmed Findings when an answer is required.

## Delegation and cost controls

- At most 40 Requirements: use one agent.
- 41–150: delegate only independent canonical Slice packets when subagents are available.
- More than 150: batch by Slice while keeping one coordinator for indexing, global decisions, traceability, deduplication, completion, and Verdict.
- Fall back to one agent without reducing baseline coverage.
- Never ask multiple agents to reread the complete document.
- Do not load Android patterns or Deep Challenge without matching signals.
- Render only gaps and critical evidence in Markdown; keep the full matrix in JSON.

The non-removable protections are Artifact fingerprinting, Requirement Coverage, Slice Integrity, eight-dimension Behavior Coverage, Verification Profile, Minimal Challenge, Global Critical Decision Guard, conditional open challenge, evidence, disproof, P0/P1 proof, Traceability Guard, Completion Guard, and deterministic final scripts.
