---
name: spec-challenge
description: >
  Challenge a feature or story specification before implementation. Build an
  evidence-backed behavior model, search the repository before asking humans,
  structurally derive new questions from model gaps and interactions, and turn
  only material unresolved questions into findings. Use when a spec must be
  proven safe for a coding agent without letting the agent invent product
  behavior.
---

# Spec Challenge

Determine whether a specification is sufficiently bounded for implementation by a coding agent.

The goal is not to prove that no unknown-unknowns exist. That is impossible.
The goal is to reduce hidden risk by systematically exploring the behavior model and converting newly discovered important questions into explicit known-unknowns.

Core flow:

```text
COLLECT -> SEARCH -> MODEL -> CHALLENGE -> FINDINGS -> DECIDE -> RECHECK -> VERDICT
```

## Epistemic model

Use these terms precisely:

- **Known known**: an answer is known and supported by evidence.
- **Known unknown**: a concrete question is known, but its authoritative answer is not.
- **Unknown known**: an answer exists in project knowledge, but the current agent has not retrieved it yet.
- **Unknown unknown**: a relevant question is not yet present in the agent's current problem model.

Never record `unknown_unknown` as a finding classification or state. Once a question has been discovered and can be written down, it is no longer an unknown-unknown.

## Inputs

Required:

- target feature/story
- current specification

Use available project context when relevant:

- related specs and domain docs
- ADRs and architecture docs
- interfaces/contracts
- existing implementation
- existing tests
- configuration
- git history
- related feature behavior

Do not require every source for every feature.

## Phase 1 — COLLECT

Identify the authoritative materials that define the target behavior.

Record:

- sources inspected
- source precedence when multiple sources overlap
- obvious missing inputs

Do not infer product behavior from absence.

## Phase 2 — SEARCH

Before raising a spec gap, search for an existing answer.

For every apparent missing fact, search in this order when applicable:

1. current spec
2. related requirement/domain docs
3. ADRs/architecture docs
4. interface or data contracts
5. existing implementation
6. existing tests
7. configuration
8. git history / related feature behavior

If an authoritative answer is found:

- add it to `Resolved Knowledge`
- record the evidence
- do not create a finding

This phase primarily reduces **unknown knowns**.

Never ask a human for a fact that can reasonably be retrieved from the project environment.

## Phase 3 — MODEL

Build a compact behavior model from evidence only.

Extract, when applicable:

- actors and goals
- scenarios
- rules
- invariants
- states
- state transitions
- operations
- data objects and relationships
- external dependencies/contracts
- observable outcomes
- failure behavior
- recovery behavior
- explicit constraints

For every model element, distinguish:

- `evidence-backed`
- `assumed`
- `missing`

Do not silently promote assumptions into facts.

## Phase 4 — CHALLENGE

Do not run a flat edge-case checklist.

Derive new questions by operating on the behavior model. Use `references/challenge-method.md`.

The challenger should look for structural incompleteness and interactions such as:

- scenario branches with undefined outcomes
- state transitions with missing entry/exit/failure semantics
- rules whose scopes overlap or conflict
- multi-step operations with interruption points
- data relationships that can become partially updated
- repeated or concurrent operations against shared state
- dependency contracts whose failure modes affect observable behavior
- acceptance claims without a usable oracle

A challenge candidate becomes a discovered question only when the model gives a concrete reason to ask it.

Bad:

> Check process death.

Good:

> Restore consists of file move + metadata update + trash removal. These are separate state-changing steps. What state is valid if execution stops after the first step?

The second question is derived from the model rather than copied from a generic checklist.

## Phase 5 — VALIDATE CANDIDATES

For each newly derived question:

1. Search again for an authoritative answer.
2. Determine whether the answer can materially change behavior, correctness, compatibility, safety, or acceptance.
3. Drop speculative or immaterial questions.
4. Keep only questions that would otherwise require the implementation agent to guess.

Do not report brainstorming noise as findings.

## Phase 6 — CREATE FINDINGS

A **Finding** is an evidence-backed review discovery that requires disposition.

Allowed classifications:

- `missing-decision`
- `ambiguity`
- `contradiction`
- `unverifiable`
- `dependency-gap`
- `unsafe-assumption`

A finding is not a bug, not a question type, and not an epistemic origin label.

Every finding must include:

- `id`
- `summary`
- `classification`
- `discovered_by`
- `evidence`
- `question`
- `impact`
- `severity`
- `owner`
- `recommended_action`
- `status`

Use this epistemic state only when useful:

```yaml
epistemic_state: known_unknown
```

Never claim that a finding was previously an `unknown_unknown`; that previous state cannot be proven from the record.

## Severity

### BLOCKER

Use when implementation cannot proceed safely without inventing externally observable behavior or violating an unresolved rule/contract.

Typical cases:

- contradictory authoritative rules
- undefined user-visible outcome
- unresolved state transition with correctness impact
- unknown required dependency contract
- acceptance criterion without an observable oracle
- unsafe assumption required to implement

### WARNING

Use when the unresolved item is real but can be explicitly deferred without forcing implementation behavior to be guessed.

### INFO

Use for useful observations that require no decision.

Do not inflate severity.

## Phase 7 — DECIDE

Separate unresolved items by owner.

### Repository-answerable fact

Search again. Do not ask the user.

### Product/domain/architecture decision

Ask the decision owner.

When Matt Skills Curated is available:

- use `grill-with-docs` / `grilling` for synchronous decision exploration
- use `to-questionnaire` when the answer belongs to another stakeholder
- use `to-spec` only after the relevant decisions are resolved and a normalized buildable spec is needed

Questions should request decisions, not rediscoverable repository facts.

Recommendations are allowed; silently choosing for the owner is not.

## Phase 8 — RECHECK

After a decision is made:

1. update the source of truth or decision record
2. rerun search for newly referenced facts/contracts
3. rerun only affected challenge operations
4. check whether the decision introduced contradictions
5. update finding status

Do not mechanically rerun unrelated checks.

## Output

Produce a report using `templates/spec-challenge-report.md`.

The report must contain:

- verdict
- inspected scope and evidence
- behavior model summary
- resolved knowledge
- blocking findings
- warnings
- decisions required
- residual risk
- challenge coverage

## Verdict rules

### NOT_READY

Return when any of these remain:

- unresolved blocker
- contradictory authoritative requirements
- implementation must invent user-visible behavior
- essential contract is unknown
- core acceptance behavior is not verifiable

### READY_WITH_WARNINGS

Return when:

- no blockers remain
- warnings are explicitly safe to defer
- coding does not require guessing

### READY

Return when:

- no blockers remain
- no material unresolved decisions remain
- core behavior is verifiable
- required contracts and invariants are known

`READY` never means that all future unknown-unknowns have been eliminated.
It means the current specification is sufficiently bounded for implementation.

## Non-goals

Do not:

- implement code
- generate engineering tasks
- silently repair the spec by inventing product behavior
- turn every challenge dimension into mandatory spec fields
- claim exhaustive discovery of unknown-unknowns
- produce findings without evidence
- block on hypothetical edge cases that do not affect the implementation contract

## Completion criteria

The challenge is complete when:

1. project knowledge was searched before humans were asked
2. a behavior model was built from evidence
3. structural challenge operations were applied to relevant model elements
4. each finding is concrete, material, and evidence-backed
5. every blocker has a decision owner or authoritative resolution path
6. the coding agent does not need to invent externally observable behavior
7. residual uncertainty is stated rather than hidden
