# Deep challenge and disproof — executable methods

Run M5 only when Minimal Challenge is suspicious or source-backed risk signals fire. Run M6 for every candidate before confirmation, including candidates discovered by Traceability Guard. This file supplements, not replaces, contracts.md and severity.md. No new product scope, implementation prescriptions or ungrounded obligations.

## M5 — Goal-driven counterexample search (P12–P13)

### 1. Select and justify exploration
Read the Slice's explicit business promise and applicable linked rules. State the smallest observable outcome whose failure would violate that promise. Derive necessary conditions and invariants without assuming an implementation. Write a short working set of hypotheses: promise + necessary condition + source IDs + feasible event that might violate it + potential impact. Select families based on evidence, not a universal checklist.

| Signal/semantic feature | Explore | Minimum concrete analysis |
|---|---|---|
| ASYNC_OPERATION, RETRY, REPEATED_ACTION | uncertain completion, duplicate effect | compare first success/lost response, first failure, retry and repeated trigger outcomes where feasible |
| PERSISTENT_STATE, DATA_MUTATION, DESTRUCTIVE_ACTION | state/data invariants | track before/after state and ownership for each explicitly in-scope representation; compare failure and success |
| LIFECYCLE_CHANGE, EXTERNAL_DEPENDENCY | interruption/recovery | change event at relevant observable boundary; compare before, during and after recovery |
| MULTI_STEP_OPERATION | partial success | identify independently committed sub-results; consider one failed step after earlier success |
| CONCURRENCY, IDENTITY_CONTEXT_CHANGE, PERMISSION_BOUNDARY | interleaving, authorization | two feasible actions/events on same relevant object or account, compare ordering and rules |
| TIME_BOUND, CAPACITY_BOUND, LOAD_SENSITIVE, ENVIRONMENT_SENSITIVE, AVAILABILITY_BOUND | partitions and measurement | compare representative below/at/above declared boundary or differing in-scope measurement setups |
| USER_VISIBLE_SUCCESS_FAILURE | false success | compare underlying promised result with reported outcome |
| semantic gap without mapped signal | open challenge | derive a failure from goal, state, rules, data or dependency without inventing a signal |

Use only source-supported context; a signal is not evidence of a defect. For Android use only the existing Android activation rules and relevant matched subset. Do not infer platform or permission dependence from Android alone.

### 2. Construct and test hypotheses
For each selected family:
- Build the normal path with source-supported starting state, trigger, committed outcome, effects and linked rules.
- Choose one counterfactual change: negate a guard, change an event/order, cross a specified boundary, alter dependency availability, or invalidate an explicitly necessary outcome. Keep unrelated facts fixed.
- For state-heavy behavior make a small table of reachable state + event + guard -> required next state/effect. Inspect feasible unhandled or incompatible transitions; do not require explicit behavior for impossible events.
- For rule-heavy behavior use a decision table of distinct feasible condition classes and matching rules. Examine overlap, gaps, boundary inclusivity and exceptions.
- For data-heavy behavior compare data before/after with promised invariants (ownership, preservation, uniqueness, visibility, deletion). Only consider copies or representations evidenced by scope.
- For timing-heavy behavior compare two feasible event orders, especially interrupted or uncertain completion. Do not assume asynchronous implementation where source does not support it.
- Explore combinations only when conditions interact: e.g. event A changes the guard, ownership or state observed by event B. Reduce to one or two interacting factors first; deepen only for a distinct material consequence. Do not enumerate Cartesian products.
- Instantiate matching patterns as hypotheses, not evidence; search at least one open challenge independently of the library.

### 3. Minimize and qualify the witness
For a plausible failure, record Given (reachable context), When (event), Wrong Result (allowed by the current source), Violated Promise (source ID), Missing Decision (not an implementation prescription), and candidate consequence. Remove unnecessary assumptions/events; if removing a condition does not affect the failure, omit it. Verify that the wrong result is not already prohibited by the authoritative source. A hypothetical wrong implementation violating an explicit requirement is a downstream bug, not a requirement defect.

Example: scope explicitly includes saving an edited note and reporting save success. Source only says "When save is pressed, return to the list and display Saved", with no authoritative success condition. Given edits not accepted by the persistence operation, when save is pressed, the requirement still permits a Saved label. This is a candidate false-success decision gap. If a global rule already says all success messages require durable commit, reject it. Do not prescribe databases, draft storage or retry queues.

Example: "On save failure stay on the editor with all user edits intact and indicate failure." A suggested defect that edits might disappear is rejected; the implementation might violate the requirement, but the requirement defines the needed behavior. If recovery after process death is outside scope, do not invent it as a requirement.

### 4. Stop and record
For each selected family record source IDs, technique, concrete condition explored, candidate or reason no material issue, and any necessary but unexecuted work. Prioritize potentially blocking impact and unexplored mechanisms. Stop when selected families and one independent open challenge have been executed, remaining variants are infeasible, resolved or same-root duplicates, and no material unresolved branch remains unexplored within scope. Budget exhaustion before necessary analysis is an execution issue, not NO_SUSPICION or DONE. Retain short working notes; emit canonical candidate packets using existing fields only.

## M6 — Adversarial disproof (P14–P17, and late P18 candidates)

For each candidate:
1. Restate the exact decision allegedly missing, ambiguous or contradictory, the affected promise and minimal witness. Identify what would falsify it. For ambiguity require two plausible interpretations with different material outcomes; for contradiction require feasible overlapping conditions and incompatible effects.
2. Verify quoted text in the original artifact and that the anchor IDs actually support the premise. Check authority and scope. Derived/industry assumptions alone cannot establish a finding.
3. Search for counterevidence by decision, entity aliases, action/result synonyms, exceptions and negation, not merely the original title. Inspect the anchor section, linked rules/ACs, definitions, global rules, and explicit precedence. Use BASIC for P3, LOCAL for P2, TARGETED for P1 (expand globally if needed), GLOBAL for P0; record actual checked IDs and sections, including contrary evidence. For a missing requirement search for an equivalent rule rather than expecting the same wording.
4. Attempt to invalidate the witness: prove a precondition unreachable, a rule not applicable, an outcome already forbidden, two cases disjoint, an authoritative exception decisive, or an apparent gap only implementation freedom. If a resolution narrows the problem, reframe the candidate and repeat checks on the revised witness.
5. Scope guard: if a reasonable implementation satisfying the existing requirements can fulfill the approved promise deterministically without the proposed additional product decision, and the only difference is acceptable implementation freedom, preference or a new capability, drop it. Conversely, do not dismiss a materially wrong permitted outcome solely because engineers could choose the safe implementation.
6. Resolve as CONFIRMED (source-supported decision defect and allowed consequence survive), REJECTED (specific counterevidence defeats it), DROPPED (scope/style/implementation-only or no consequence), OBSERVATION (harmless wording), or NEEDS_CONTEXT (owner knowledge not available and defect cannot yet be established). An established missing product decision is a finding, not incomplete review; inability to perform required evidence checks is a blocking execution issue. P0/P1 need the existing proof/witness and severity-specific budget. Recheck budget if potential severity increases. Independent subagent review is useful for disputed blocking candidates when available; otherwise do a separate adversarial pass over source, not just the prior summary.
7. Record checked IDs and decisive evidence, disposition, surviving witness and severity basis as auditable summaries. A statement "checked all, confirmed" without explaining what was checked and why it did not resolve the issue is insufficient.

### Calibration examples
- Confirm: a shared-note owner is allowed to delete by one rule and prohibited by another, both apply and no precedence exists. Reject if authoritative owner exception resolves the overlap.
- Confirm: two reasonable units for a limit change pass/fail and no authoritative definition resolves them. Reject if a global unit definition applies.
- Drop: requesting offline sync when scope only commits online editing and no offline continuity is promised.
- Reject: proposing duplicate-effect risk when the authoritative rule explicitly ensures one effect for a repeated operation; implementation violations are not requirement gaps.
- NEEDS_CONTEXT: an external regulation is suspected but its applicability and content are unavailable and source does not independently prove an issue. Do not invent it.
