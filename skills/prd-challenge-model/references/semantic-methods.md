# Semantic methods — executable review procedures

These are review-time instructions, not additional requirements. Use the common guard in prompts.md. Keep only auditable summaries, not private reasoning. Use canonical IDs in all results; temporary working tables may be plain text/JSON and must not add keys to review.json. The coordinator retains them until Completion Guard.

## M1 — Source-first modeling (P3–P6)

1. Enumerate source blocks in order: headings, paragraphs, list items, table rows (include inherited headers), acceptance criteria, captions and applicable definitions. Use a contiguous line/page range, not only selected quotations. Mark each block reviewed, excluded with reason, or unreadable. Reconcile this inventory against the original file, not only the generated Requirement Index.
2. Extract one requirement per independently decidable commitment. Split when actor, condition, action, result or obligation can change independently; keep conjunctions that specify one indivisible business decision. Preserve qualifiers, negations, units, exception scope, and exact original excerpts. Do not transform examples into universal rules. If splitting loses necessary context, retain the source context via reference.
3. For each candidate behavior record a lightweight working tuple: goal/commitment, actor, object and ownership, trigger, guard, pre-state, intended action, observable result, post-state, data effects, dependencies, failure/recovery. Each populated fact is EXPLICIT (source says it), DERIVED (entailed or candidate inference, with premise IDs and rationale), or UNKNOWN. A DERIVED hypothesis never becomes an authoritative rule merely because it is plausible.
4. Build Slice boundaries around one independently verifiable business commitment. Link shared rules, constraints and NFRs to consumers, not by keyword but by applicable actor/object/condition. Preserve cross-behavior dependencies and conflicting statements. Do not merge separate goals because they share a screen; do not split success and failure of one goal into unrelated behaviors. Use canonical Slice roles and links.
5. Re-read source blocks in reverse direction: for each unrepresented normative phrase ask whether it defines an independent decision, modifies an existing decision, or is out of scope. For each extracted item locate its verbatim source. Correct missing items and dangling links before review; record unresolved coverage/parse as an execution issue. Do not claim semantic extraction completeness from assigned-ID counts.

Worked example: "An owner may delete an unshared note. Shared notes cannot be deleted." Extract two rules with guards owner+unshared, shared. The second rule applies regardless of ownership; no contradiction. Do not invent a trash bin, database schema or a separate feature.

## M2 — Baseline review (P7–P10)

### Completeness: forward and backward
For each applicable behavior:
- Start with explicit trigger and admissible preconditions. Walk the shortest normal path through observable outcomes and changed data/state; compare each promised result with source coverage.
- Work backward from the promised outcome: identify necessary business conditions and invariants (e.g. a reported successful save corresponds to a saved revision). Distinguish logical necessity from desirable UX and implementation freedom.
- Negate one necessary condition while preserving scope. Ask whether the event can occur and whether an implementation consistent with all source clauses could violate a promise. If yes, create a candidate with a concrete witness; if a gap only allows harmless design choices, drop it.
- Fill all eight coverage dimensions according to source; a missing dimension alone is not a finding. For non-behavior slices, review the rule's domain, guard, effect, exception, measurable constraint and links instead of fabricating behavior dimensions.

### Clarity: competing interpretations
Extract the exact decision that is uncertain. Construct two reasonable interpretations that respect the same text and conditions. For each specify a concrete observation, state/data effect or pass/fail result. If no materially different downstream consequence exists, record at most an observation. Resolve ambiguity using definitions, nearby conditions, examples that are normative, and authorized precedence. If neither interpretation survives, revise the candidate. Never demand technical mechanism when product behavior is uniquely determined.

Example: "Keep recent notes" with an explicit retention obligation but no age/quantity permits different deletion results; ambiguity can matter. "Use a convenient implementation" in non-requirement rationale is not a defect. An unspecified animation technique with a unique observable outcome is implementation freedom.

### Verification: derive the oracle, not a new requirement
For each Slice extract the input/precondition, event, externally observable outcome and rule deciding pass/fail. Trace each to source. If the result can be uniquely normalized from source, use NORMALIZED_FROM_SOURCE; no separate AC is required. For a numeric NFR identify metric/unit, start/end, data scale, environment, aggregation/percentile if material, and threshold; if two realistic measurement setups yield incompatible compliance, identify the missing decision. A UI success label is not proof of durable business success if durability is promised. Record unknown elements without inventing thresholds or technology.

### Local consistency and minimal challenge
Normalize rules as subject + action + property + scope + guard + value/effect. Compare applicable pairs using M3. Then find the smallest perturbation of the normal path that could violate a promise (one condition, event or order change). Check observable effects; select applicable risk signals using source facts, not imagined architecture. A risk signal or a material unresolved gap triggers deep challenge; if none, give an auditable no-suspicion rationale. Do not label unknown as safe merely because it is absent from the pattern library.

## M3 — Rule and cross-behavior consistency (P8, P11)

Build the existing Critical Decision Index across all authorized sources; use scope/guard in working comparisons even when they are serialized as scope text in the canonical schema. Canonicalize aliases only with evidence of same entity and meaning; distinguish different accounts, objects, versions and lifecycle states.
1. Retrieve pairs with same object/operation or a shared invariant/data effect, including different actions that interact (delete versus restore, permissions versus sharing). Inspect primary/supporting authority and explicit exceptions first.
2. For each potentially conflicting pair construct a common reachable context. If guards are disjoint, reject. If overlap is unknown, mark it as uncertainty and do not assert contradiction.
3. For overlapping guards, compare required outcomes. Contradiction means the same context cannot satisfy both, not merely different wording. For multiple predicates, build a small decision table: feasible condition classes, matching rules, allowed outcome, exception/priority, source IDs. Include uncovered feasible cells only when a committed behavior requires a decision.
4. For interacting behaviors check postcondition of one versus precondition/invariant of the next, ownership, deletion/retention, state and timing. Compare ordering only when source or reachable interaction warrants it.
5. If a conflict survives, produce two exact quotes, common context, mutually exclusive outcomes, and precedence search results; use CONTRADICTORY only with two source evidence entries and proof. If neither rule determines a needed outcome, use MISSING/AMBIGUOUS instead.

Example: "All owners may permanently delete shared notes" and "No shared note may be deleted" overlap for an owner of a shared note. If a later explicit exception says owners may delete shared notes, the precedence may resolve the conflict. Do not report both the rule overlap and the same underlying missing precedence as duplicate findings.

## M4 — Traceability and adjudication (P18–P20)

For each behavior verify the defining source and that ACs genuinely exercise its guard and result, not just share terms. For each applicable rule/constraint/NFR identify actual consumer(s) using the applicability guard; an explicit global rule can use the existing exemption. Verify each link semantically and structurally. A missing explicit AC is not a finding when source already yields a deterministic oracle. Feed every traceability candidate back through consequence mapping, qualification and M6 before deduplication; no candidate may bypass disproof because it was detected late.

Merge findings by the product decision that would resolve them, affected behavior and consequence. Preserve all independent evidence and materially different impacts; do not merge merely similar titles across distinct required decisions. Assign severity from supported impact, not the number of scenarios or confidence. Maintain candidate outcomes, including rejection reasons, in working notes. Distinguish absent product decisions from inaccessible evidence/failed execution. A completed review may still have unresolved product decisions as confirmed findings.

## Method basis

- IREB CPRE Requirements Modeling: https://cpre.ireb.org/en/concept/requirements-modeling — scenario, state and relationship modeling; adapted here as lightweight review-time tuples.
- ISTQB black-box techniques: https://astqb.org/4-2-black-box-test-techniques/ — decision tables, state transitions, partitions and boundaries; adapted to requirements rather than executed test cases.
- NASA requirements validation and verification matrix: https://www.nasa.gov/reference/system-engineering-handbook-appendix/ and https://www.nasa.gov/reference/appendix-d-requirements-verification-matrix/ — evidence, requirements and verification alignment.
- Goal-backward inference, smallest failure witness and counterfactual selection are RGQ-specific operational adaptations; their incremental benefit is a hypothesis to be evaluated, not a claim of validated effectiveness.
