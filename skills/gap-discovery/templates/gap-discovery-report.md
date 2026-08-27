# Gap Discovery Report

## 1. Scope

- **Target:**
- **Requirement sources:**
- **In scope:**
- **Explicit non-goals:**
- **Project evidence searched:**

## 2. Exploration Summary

| Perspective | Applied | Trigger / rationale | Candidate count | Surviving count |
|---|---:|---|---:|---:|
| Scenario |  |  |  |  |
| State |  |  |  |  |
| Failure / recovery |  |  |  |  |
| Boundary |  |  |  |  |
| Rule / constraint |  |  |  |  |
| Dependency |  |  |  |  |
| Non-functional |  |  |  |  |
| Assumption |  |  |  |  |
| Cross-artifact coverage |  |  |  |  |

> Do not treat this table as a mandatory checklist. Mark a perspective `N/A`
> when no concrete model structure makes it relevant.

## 3. Candidate Gaps / Open Questions

### GAP-001 — <short title>

- **Perspective:** `<scenario|state|failure|boundary|rule|dependency|nfr|assumption|cross-artifact>`
- **Status:** `<open_question|confirmed_gap>`
- **Materiality:** `<HIGH|MEDIUM|LOW>`
- **Confidence:** `<HIGH|MEDIUM|LOW>`
- **Requirement refs:**
- **Trigger:**
  - What concrete requirement/model element caused this question?
- **Question:**
  - What decision is required?
- **Evidence searched:**
  - `<source/path/section>`
- **Evidence gap:**
  - What authoritative answer is missing or only partially defined?
- **Why it matters:**
  - How could different answers change implementation, observable behavior,
    correctness, safety, compatibility, operability, or acceptance?
- **Suggested owner:**
- **Recommended action:**

Repeat for each surviving candidate.

## 4. Covered Candidates

List only useful examples where exploration found an apparent gap but repository
search resolved it. This section demonstrates that search was performed before
human escalation.

| Candidate concern | Resolution | Authoritative evidence |
|---|---|---|
|  |  |  |

## 5. Rejected / Filtered Noise

Summarize categories rather than dumping every generated question.

Examples:

- out of feature scope
- already answered by authoritative sources
- no material implementation consequence
- generic hypothetical edge case
- semantic duplicate
- weak derivation / insufficient context

## 6. Decision Queue

| ID | Decision owner | Question | Why decision is needed | Materiality |
|---|---|---|---|---|
|  |  |  |  |  |

## 7. Residual Uncertainty

State what this exploration did **not** establish.

Examples:

- domain documents unavailable
- dependency contract incomplete
- historical defect data not searched
- only selected perspectives were applicable
- no claim of exhaustive completeness

## 8. Machine-Readable Candidate Shape

```yaml
candidate_gaps:
  - id: GAP-001
    perspective: failure
    status: open_question
    materiality: HIGH
    confidence: HIGH
    requirement_refs:
      - REQ-12
    trigger: >-
      Upload completion updates local metadata after the remote upload call,
      while the remote contract allows timeout with unknown server outcome.
    question: >-
      What user-visible state is required after a timeout when the server may
      already have accepted the upload?
    evidence_searched:
      - spec.md#upload
      - api/upload-contract.md#timeouts
    evidence_gap: >-
      No authoritative source defines the post-timeout state or reconciliation
      behavior.
    why_it_matters: >-
      Different answers lead to failed, pending, or reconciled states and can
      change retry/idempotency behavior.
    suggested_owner: product/domain owner
    recommended_action: >-
      Define the required post-timeout state and retry/reconciliation semantics.
```

## 9. Handoff to Spec Review

If a parent `spec-challenge` review exists:

- send only surviving candidate gaps/open questions
- preserve evidence and materiality
- do not convert them into BLOCKER/WARNING automatically
- let the parent review confirm findings and own the readiness verdict
