---
name: gap-discovery
description: >
  Discover important requirement gaps that are not explicitly written in a
  feature or story specification. Expand the candidate requirement space using
  bounded perspectives, search project evidence before escalating, compare
  candidates against the current requirement set, and return only material,
  evidence-backed candidate gaps or open questions. Use before implementation
  when the goal is to improve requirement recall without letting the agent
  invent product behavior.
---

# Gap Discovery

Systematically discover important requirement concerns that are absent or not
sufficiently defined in the current specification.

This skill is optimized for **recall-oriented exploration**. It does not prove
that a requirement set is complete, and it does not decide product truth.

Core flow:

```text
SCOPE -> COLLECT -> EXPAND -> COMPARE -> FILTER -> REPORT
```

When used together with `spec-challenge`, treat this skill as a specialized
explorer. `gap-discovery` finds and filters candidate gaps; `spec-challenge`
may later convert confirmed items into findings and make readiness decisions.

## Operating principle

Do not ask:

> What could possibly be missing?

Instead use:

```text
bounded perspective
    +
concrete requirement/model element
    +
project/domain evidence
    ↓
candidate concern
    ↓
compare against current requirement set
    ↓
material unanswered concern
    ↓
candidate gap / open question
```

The purpose is to expand the current problem model enough to expose important
missing decisions while controlling speculation and reviewer noise.

## Epistemic boundary

A model-generated concern is **not automatically a defect**.

Use these states precisely:

- `candidate`: a plausible concern produced by bounded exploration.
- `covered`: the current authoritative materials already answer it.
- `open_question`: the concern is material, but no authoritative answer was found.
- `confirmed_gap`: an authorized domain/product owner has confirmed that the requirement is missing or insufficient.
- `rejected`: the concern is not applicable, intentionally out of scope, or otherwise invalid.

This skill should normally output `open_question` rather than `confirmed_gap`
unless confirmation evidence already exists in the project materials.

Never invent product behavior in order to close a gap.

## Inputs

Required:

- target feature/story or requirement scope
- current requirement/specification set

Use when available:

- related requirements and domain documents
- acceptance criteria and scenarios
- product rules and decision records
- architecture/interface/data contracts
- existing implementation
- existing tests
- configuration and feature flags
- historical defects/incidents
- git history and related feature behavior

Do not require every source for every review.

## Phase 1 — SCOPE

Define the exploration boundary before generating questions.

Record:

- target feature/story
- in-scope actors and goals
- in-scope operations or capabilities
- explicit non-goals if known
- authoritative requirement sources

Do not expand into unrelated product areas merely because the model can imagine
them.

## Phase 2 — COLLECT

Build a compact evidence view before exploration.

Extract when applicable:

- actors and goals
- scenarios / acceptance conditions
- states and transitions
- rules and invariants
- operations
- data objects and relationships
- external dependencies/contracts
- observable outcomes
- explicit failure/recovery behavior
- constraints and assumptions

For every extracted element distinguish:

- `evidence_backed`
- `assumed`
- `not_defined`

Search the project before treating absence from the current file as a gap.

A fact present in another authoritative source is an **unknown-known retrieval
problem**, not a requirement gap.

## Phase 3 — EXPAND

Perform bounded exploration using only relevant perspectives.

Default perspectives are defined in `references/discovery-perspectives.md`:

- scenario
- state
- failure/recovery
- boundary
- rule/constraint
- dependency
- non-functional concern
- assumption
- cross-artifact coverage

Do not run every perspective mechanically.

Select a perspective only when the current model contains a structure that can
make that perspective meaningful.

Examples:

- state exploration requires meaningful mutable state
- concurrency/failure exploration requires shared or interruptible behavior
- dependency exploration requires an actual external contract
- boundary exploration requires a quantity, cardinality, lifecycle limit, time,
  capacity, or other meaningful boundary

For each exploration operation, record the trigger that caused the question.

Bad:

> What happens on network failure?

Good:

> Upload completion updates local metadata after a remote upload call. The
> remote contract allows timeout with unknown server outcome. What user-visible
> state is required when the client times out after the server may already have
> accepted the upload?

The second question is grounded in concrete structure and evidence.

## Phase 4 — COMPARE

For each candidate concern, search for an authoritative answer before reporting
it.

Recommended search order when applicable:

1. current requirement/spec
2. related requirement/domain docs
3. acceptance criteria/scenarios
4. decision records / product rules
5. interface/data contracts
6. existing implementation
7. existing tests
8. configuration / feature flags
9. git history / historical defects / related feature behavior

Classify the result:

### `covered`

An authoritative answer exists and is sufficiently explicit for downstream
implementation or verification.

Action:

- record the evidence
- do not report as a gap

### `partially_covered`

Some behavior is described but materially different interpretations remain.

Action:

- preserve the exact unresolved part
- continue to materiality filtering

### `unanswered`

No authoritative answer was found.

Action:

- continue to materiality filtering

Do not infer product intent from implementation behavior when requirements or
product decisions should be authoritative. Existing code can be evidence of
current behavior, not automatic proof of intended behavior.

## Phase 5 — FILTER

Gap discovery should favor recall, but output must remain reviewable.

Keep a candidate only when all are true:

1. **Derivation** — a concrete requirement/model element caused the question.
2. **Evidence search** — relevant authoritative sources were searched.
3. **Materiality** — different answers could materially change implementation,
   externally observable behavior, correctness, safety, compatibility,
   operability, or acceptance.
4. **Unresolvedness** — the current sources do not already answer the concern.
5. **Actionability** — a product/domain/architecture owner could answer the
   question or explicitly reject it.

Drop candidates that are:

- generic brainstorming
- unrelated to the current feature scope
- purely hypothetical with no credible trigger
- implementation-detail preferences with no externally relevant consequence
- duplicate semantic variants of a stronger candidate
- already answered elsewhere in authoritative project knowledge

## Materiality

Use materiality to prioritize candidate review. Do not assign final defect
severity unless the gap has already been confirmed.

### HIGH

Different answers could change one or more of:

- core user-visible behavior
- data integrity or irreversible state
- security/privacy behavior
- compatibility or contract behavior
- acceptance outcome
- recovery semantics for a core operation

### MEDIUM

Different answers could change meaningful secondary behavior, maintainability,
operability, or non-core acceptance, but implementation can be bounded without
risk to the primary contract.

### LOW

Useful clarification with limited downstream consequence.

Prefer reporting fewer high-value candidates over flooding the reviewer with
low-value possibilities.

## Phase 6 — REPORT

Produce a report using `templates/gap-discovery-report.md`.

Every reported candidate must include:

- `id`
- `perspective`
- `trigger`
- `question`
- `requirement_refs`
- `evidence_searched`
- `evidence_gap`
- `why_it_matters`
- `materiality`
- `confidence`
- `status`
- `suggested_owner`
- `recommended_action`

Optional when useful:

- related state/rule/dependency identifiers
- similar historical defect or requirement
- duplicate/merge relation to another candidate

## Confidence

Confidence describes confidence that the concern is genuinely unresolved and
relevant. It does not mean confidence about the missing product decision.

### HIGH

- trigger is concrete
- relevant authoritative sources were searched
- no answer was found
- implementation consequences are clear

### MEDIUM

- trigger and consequences are credible
- search coverage is reasonable
- some context or ownership remains uncertain

### LOW

- concern may be relevant but evidence/context is weak

Low-confidence items should normally be omitted from the main report or placed
in a clearly separated exploration appendix.

## Precision / Recall policy

This skill intentionally seeks higher recall than a traditional human-only
review, but must control false-positive burden.

Optimize for:

```text
important-gap recall
+
evidence-grounded candidates
+
manageable reviewer load
```

Do not optimize for:

```text
maximum number of questions
or
only 100%-certain questions
```

The first produces noise; the second suppresses discovery value.

## Search before human escalation

Never ask a human to resolve a fact that can reasonably be retrieved from the
project environment.

When a candidate remains after search:

- ask the appropriate decision owner
- request a decision, not a vague discussion
- include the evidence gap and implementation consequence

Example:

> The spec defines successful upload but does not define the state after a
> timeout with unknown remote outcome. Existing interface docs do not guarantee
> exactly-once execution. Should the client show failed, pending/reconciling, or
> another explicit state?

## Interaction with `spec-challenge`

When `spec-challenge` is available:

1. run `gap-discovery` during the challenge/exploration stage when hidden gaps
   are the primary concern
2. return candidate gaps and open questions
3. let `spec-challenge` decide whether confirmed unresolved items become
   findings
4. let `spec-challenge` own BLOCKER/WARNING/INFO severity and READY verdicts

Do not duplicate readiness decisions inside this skill.

## Non-goals

Do not:

- prove requirement completeness
- invent business rules
- silently repair the spec
- generate implementation tasks or code
- treat every possible edge case as mandatory
- convert model suggestions directly into defects
- assign final gate verdicts
- claim that all unknown-unknowns were discovered

## Completion criteria

Gap discovery is complete when:

1. the exploration scope is explicit
2. relevant project evidence was collected before speculation
3. relevant bounded perspectives were applied
4. every surviving candidate has a concrete derivation trigger
5. authoritative sources were searched for each surviving candidate
6. low-value and duplicate candidates were filtered
7. unresolved candidates clearly state why different answers matter
8. candidate status remains distinct from confirmed defect status
9. residual uncertainty is visible rather than hidden
