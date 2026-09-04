# Artifact and Claim Model

Use this contract to determine what is binding and to build stable, atomic claims.

## Contents

- Artifact roles
- Authority states
- Authority admission
- Conflicts and precedence
- Intent inventory schema
- Materiality
- Declared obligation versus derived concern
- Claim construction
- Criticality
- Stable ordering

## Artifact roles

| Role | Purpose | Typical material | Evidentiary use |
| --- | --- | --- | --- |
| `intent` | Defines what must hold | Requirement, story, AC, scenario, rule, invariant, accepted constraint | Source of product obligations |
| `design` | Defines an approved allocation or technical obligation | Architecture, ADR, contract, state/data model, sequence, interface decision | Source of engineering obligations and allocation evidence |
| `work` | Describes planned or claimed work | Task, issue, plan, commit note | Navigation and corroboration only |
| `implementation` | Describes current system reality | Code, configuration, schema, resources, runtime wiring | Evidence of implemented behavior/property |
| `verification` | Defines or records checks | Test code, oracle, test result, runtime trace, validation report | Coverage or execution evidence |
| `unknown` | Cannot be classified confidently | Ambiguous or inaccessible artifact | Limitation; never silently authoritative |

An artifact may contain sections with different roles. Classify the relevant section, not only the whole file.

## Authority states

Assign one state to every candidate obligation:

- `REQUIRED`: explicitly accepted or mandatory.
- `APPROVED`: approved engineering decision or contract.
- `ADVISORY`: guidance that is non-binding.
- `DRAFT`: proposed but not accepted.
- `REJECTED`: explicitly superseded or rejected.
- `UNKNOWN`: acceptance cannot be established.

Only `REQUIRED` product intent and `APPROVED` engineering obligations can directly create blocking claims. `ADVISORY`, `DRAFT`, `REJECTED`, and `UNKNOWN` text may guide discovery but must not be treated as binding.

## Authority admission

Admit an obligation as `REQUIRED` or `APPROVED` only when acceptance is established by at least one of:

- the user explicitly supplies the statement or artifact as the accepted baseline for this review;
- the artifact carries an explicit status, approval, mandatory marker, or acceptance record;
- an authoritative repository policy defines that artifact class, location, or version as binding;
- an unambiguous cross-reference from an already authoritative artifact incorporates it.

A conventional filename, directory, template, issue state, task checkbox, implementation behavior, or recency alone does not establish authority. If the source appears requirement-like but acceptance cannot be established, assign `UNKNOWN` and identify the missing authority evidence.

If no in-scope obligation can be admitted as `REQUIRED` or `APPROVED`, create an intent-layer `UNVERIFIABLE` extraction finding and return `BLOCK`. A review with zero authoritative claims is not evidence of convergence.

## Conflicts and precedence

Use explicit project precedence, status, and version markers when present. Prefer a later artifact only when it explicitly supersedes the earlier one or the project's policy establishes ordering.

When two authoritative sources conflict and precedence cannot be established:

1. preserve both source references;
2. create no synthesized obligation;
3. mark affected claims `UNVERIFIABLE`;
4. create one `CONTRADICTS` finding at layer `intent` or `design`;
5. set severity from the impact of choosing the wrong interpretation.

Implementation reality never overrides accepted intent; it may contradict it. A task never overrides either.

## Intent inventory schema

```yaml
id: INT-001
source:
  artifact: requirements.md
  ref: AC-003
  location: requirements.md#network-recovery
type: requirement | scenario | rule | invariant | product_constraint | engineering_obligation
statement: unfinished sync work continues after connectivity returns
authority: REQUIRED | APPROVED | ADVISORY | DRAFT | REJECTED | UNKNOWN
priority: P0 | P1 | P2 | P3 | UNKNOWN
conditions:
  - connectivity was temporarily unavailable
notes: null
```

Use the project's native ID as `id` when unique. Otherwise create `INT-###` IDs in deterministic source order.

## Materiality

Create claims for an intent when failure could change at least one of:

- user-visible behavior or acceptance;
- a business rule, invariant, or state transition;
- data integrity, security, privacy, safety, compatibility, or external side effect;
- an approved public/internal contract;
- an approved engineering constraint required for delivery;
- a declared recovery, lifecycle, performance, or reliability property.

Do not create separate gate claims for prose context, rationale, examples, headings, duplicate statements, or advisory implementation suggestions.

## Declared obligation versus derived concern

A `declared obligation` has a source with `REQUIRED` or `APPROVED` authority. A `derived concern` is an inferred risk such as a possible race, retry duplication, or lifecycle loss.

Use derived concerns only to:

- expand search;
- identify counter-evidence candidates;
- find a source that may establish a declared obligation.

Never assign a blocking claim to a derived concern without an authoritative source.

## Claim construction

A claim must be:

- source-grounded;
- atomic and independently decidable;
- conditional where the source is conditional;
- implementation-neutral unless the source mandates an implementation property;
- testable through design, implementation, verification, or runtime evidence;
- scoped to the evaluated target.

Split a statement when one part can be true while another is false. Merge duplicate meanings and retain all `source_intents`.

### Claim schema

```yaml
id: CLM-001
source_intents:
  - INT-001
statement: unfinished sync work remains recoverable and can resume after connectivity returns
kind: behavior | state | rule | invariant | contract | engineering_property
conditions:
  - a sync operation was unfinished when connectivity was lost
expected_evidence:
  design:
    - ownership and recovery mechanism are allocated
  implementation:
    - unfinished work remains discoverable
    - a connectivity-restoration path can resume it
  verification:
    - an oracle distinguishes resumed work from permanent termination
criticality: critical | high | medium | low
authority: REQUIRED | APPROVED
```

## Criticality

Use explicit priority and impact when available. Otherwise assign:

- `critical`: failure can cause severe safety/security/privacy breach, unrecoverable corruption/loss, or total failure of a non-negotiable capability.
- `high`: failure breaks a core AC, rule, invariant, P0/P1 scenario, public contract, or approved mandatory engineering constraint.
- `medium`: failure affects a secondary path, bounded recovery/compatibility case, or meaningful but non-core behavior.
- `low`: failure affects minor behavior or low-risk traceability without changing core acceptance.

Do not raise criticality merely because evidence is weak.

## Stable ordering

Order artifacts by canonical path, then source location. Order intents by artifact order and native source reference. Order claims by first source intent and normalized statement. Generate IDs only after sorting. Preserve IDs throughout the run.
