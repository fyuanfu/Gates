# Evidence Model

Use this contract to search, record, and evaluate evidence without overclaiming.

## Contents

- Evidence record
- Evidence strength
- Evidence modes
- Sufficiency by relationship
- Claim evaluation rules
- Search protocol
- Stopping rules
- Establishing absence

## Evidence record

```yaml
id: EVD-001
claim: CLM-001
polarity: positive | counter
category: design | code | configuration | schema | test_source | test_result | runtime | work
strength: direct | indirect
location:
  artifact: app/src/main/.../SyncWorker.kt
  ref: SyncWorker.resumePending
observation: the recovery entry point loads pending work and re-enqueues eligible items
condition_covered: connectivity restoration with persisted pending work
limitations:
  - process-death path was not executed in this run
```

Evidence is an inspected observation at a stable location. A conclusion without a location is reasoning, not evidence.

## Evidence strength

### Direct

Direct evidence establishes a required condition through an inspectable path, contract, assertion/oracle, executed result, or runtime observation.

Examples:

- a complete call/data/state path implements the claimed condition;
- an approved contract explicitly allocates the obligation;
- a test oracle directly asserts the claimed outcome;
- a passing result is linked to that exact test and revision;
- a runtime trace observes the required outcome under the claim's conditions.

### Indirect

Indirect evidence establishes plausibility or capability but not the claim itself.

Examples:

- a dependency is present;
- a similarly named class or method exists;
- a task is marked complete;
- a pending-state table exists without a recovery path;
- a test name resembles the claim but its setup or oracle does not cover it.

Multiple independent indirect observations may strengthen confidence but do not automatically become direct evidence.

### Counter evidence

Counter evidence is any reachable condition, alternate implementation, override, state transition, or observed result that conflicts with the claim or narrows its coverage.

Evaluate reachability and applicable conditions. Dead code or an impossible branch is not material counter evidence unless its status is uncertain.

## Evidence modes

- `STATIC`: design, code, configuration, schemas, and test source were inspected; no execution result is asserted.
- `EXECUTED`: revision-linked test results or runtime observations are available for the evaluated claims.
- `MIXED`: some claims have executed evidence and others have only static evidence.

Test source proves that a verification path and oracle exist. It does not prove that the test ran or passed. Test results without a link to revision, test identity, and outcome are indirect.

## Sufficiency by relationship

### Intent -> design allocation

Check this relationship for every material intent claim. Sufficient when an inspected design source identifies an owner, mechanism, state, interface, interaction, or decision that carries the claim. When no design artifact or allocation evidence exists, create a separate `UNTRACEABLE` finding unless an authoritative project policy explicitly says design allocation is not required for that claim. Do not use `not applicable` merely because no design artifact was supplied. Missing design allocation does not by itself prove behavior failure.

### Intent -> implementation/behavior

Sufficient static evidence requires a connected and reachable implementation path covering every material claim condition. A named symbol, isolated branch, or dependency is insufficient.

Executed evidence can directly establish behavior only for the exercised conditions. It does not prove unexercised branches.

### Approved design obligation -> implementation

Sufficient when the implementation realizes the mandated property. Equivalent mechanisms are allowed only if the authoritative design constrains the property rather than the exact mechanism.

### Intent -> verification

Sufficient coverage evidence requires setup/preconditions, stimulus, and an oracle tied to the claim outcome. A passing result is execution evidence only when linked to that verification asset and relevant revision.

### Work -> implementation

Work artifacts can locate intended changes. Confirm them against implementation evidence; never satisfy a claim with work evidence alone.

## Claim evaluation rules

Assign:

- `SATISFIED` when direct positive evidence covers all material conditions and no material counter evidence remains unresolved.
- `PARTIALLY_SATISFIED` when direct evidence covers some but not all material conditions, or a reachable counter path narrows coverage without defeating the entire claim.
- `CONTRADICTED` when direct counter evidence shows the required behavior/property fails or an approved obligation is violated.
- `UNVERIFIABLE` when available evidence cannot establish or refute the claim after the required search.

Do not use confidence to change the verdict. `SATISFIED` with static evidence may have medium confidence; state that execution was not observed. Use `UNVERIFIABLE`, not `SATISFIED` with low confidence, when no direct evidence exists.

## Search protocol

For each claim, keep a search ledger containing:

- concepts and native IDs searched;
- files/symbols inspected;
- dependencies expanded;
- positive paths followed;
- counter paths followed;
- verification assets and results inspected;
- inaccessible areas and other limitations.

For `critical` and `high` claims, inspect at minimum:

1. the primary positive implementation path;
2. relevant state/configuration ownership;
3. at least one applicable failure, alternate, recovery, or bypass path;
4. available verification source and results;
5. mandated design constraints.

For `medium` and `low` claims, scale expansion by risk, but still inspect obvious counter evidence.

## Stopping rules

Stop searching a claim when either condition holds:

### Evidence closure

- all expected material conditions have direct evidence;
- mandatory counter-search areas were inspected;
- apparent contradictions were resolved by reachability, precedence, or conditions;
- evidence locations are stable enough to cite.

### Practical exhaustion

- declared locations and intent-driven searches were inspected;
- relevant dependencies were expanded to a reasonable boundary;
- further search repeats prior paths or requires inaccessible artifacts/tools;
- the remaining uncertainty is recorded.

Practical exhaustion yields `UNVERIFIABLE` or a limited-confidence partial verdict; it never licenses an assumption.

## Establishing absence

Do not infer absence from a failed keyword search. `MISSING` requires bounded, affirmative evidence such as:

- an exhaustive registry/switch/table lacks the required case;
- a required interface has no implementation in the resolved scope;
- a reachable path ends in TODO, unsupported, no-op, or explicit omission;
- the only declared implementation location was inspected and the project structure establishes that it is exhaustive.

Otherwise use `UNVERIFIABLE` and document the search boundary.
