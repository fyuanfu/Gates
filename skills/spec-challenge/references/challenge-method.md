# Structural Challenge Method

This reference defines how `spec-challenge` derives new questions from a behavior model without degrading into a generic edge-case checklist.

## Principle

A challenge should be generated from a concrete model structure or interaction.

Use:

```text
model element(s) -> transformation / interaction -> unsupported outcome -> question
```

Do not use:

```text
generic edge-case list -> ask everything
```

The goal is to expand the current problem model enough to discover relevant questions that were not previously explicit.

---

## 1. Scenario branch expansion

Given a scenario:

```text
Given P
When A
Then O
```

Derive questions by varying only material prerequisites and outcomes.

Operations:

- negate a prerequisite that can realistically be absent
- repeat the action when it may not be one-shot
- substitute a materially different actor/state
- identify a branch already implied by a rule or dependency

Example:

```text
Scenario: restore note to original folder
Relationship: note -> original folder
```

Derived branch:

```text
original folder missing
```

Question:

> What is the required restore destination when the original folder no longer exists?

Do not enumerate arbitrary permutations with no behavioral consequence.

---

## 2. State-transition closure

For each operation that changes state, model:

```text
source_state --event--> target_state
```

Check:

- source state is defined
- target state is defined
- transition guard is defined when needed
- invalid transition behavior is known
- intermediate state exists when the operation is not atomic
- failure outcome is known
- retry/re-entry behavior is known when the operation can be repeated

Derivation rule:

```text
non-atomic transition + interruptible execution -> intermediate-state question
```

Example:

```text
TRASHED -> RESTORED
implementation-relevant operation sequence:
1. move attachments
2. update metadata
3. remove trash record
```

Derived question:

> Which externally valid state must hold if execution stops between steps 1 and 2?

The question is derived from transition structure, not from a preset `process death` item.

---

## 3. Rule overlap and precedence

Represent a rule minimally as:

```text
scope + condition -> required/prohibited outcome
```

Compare rules whose scopes overlap.

Look for:

- same condition, different outcomes
- broad rule vs exception with no precedence
- two valid rules that can apply simultaneously
- rule that conflicts with a state invariant

Example:

```text
R1: deleted notes can be restored within 30 days
R2: notes under legal hold cannot change location
```

If a legally held deleted note exists, both scopes overlap.

Derived question:

> Which rule has precedence when a note is both restorable and under legal hold?

---

## 4. Invariant stress

For every invariant:

```text
I must always be true
```

Identify operations that can change any variable participating in `I`.

Then ask whether the invariant can be violated:

- during a partial operation
- under retry
- under concurrent actions
- after dependency failure
- after migration/restart

Example:

```text
Invariant: every active note references an existing folder
Operation: restore note
Relationship: note.folderId -> folder
```

Derived question:

> What behavior preserves the invariant when `folderId` references a deleted folder?

---

## 5. Multi-step atomicity and partial success

For operations with multiple state-changing effects, enumerate the effects, not generic failures.

Example:

```text
restore =
- move file
- update DB record
- restore attachments
- update sync state
```

For each adjacent pair, consider:

```text
previous effect succeeded + next effect did not complete
```

Ask only when partial completion can become externally observable or persist.

Possible derived questions:

- What state is valid after partial completion?
- Is rollback required?
- Is retry idempotent?
- Which effect defines commit success?

---

## 6. Data relationship mutation

Build a small relation graph:

```text
A -> B
A -> C
```

For each operation changing `A`, determine whether referenced/owned objects may independently change.

Challenge:

- target missing
- target stale
- child partially available
- ownership changed
- schema/contract version differs

Only create a question when the relationship matters to observable behavior or correctness.

Example:

```text
Note -> Folder
Note -> Attachments
```

Restore changes Note state, but Folder and Attachments have independent lifecycles.

Derived questions can therefore emerge from those relationships rather than from an edge-case catalog.

---

## 7. Shared-state concurrency

Apply only when two or more actions can affect the same state.

Represent:

```text
A changes X
B changes X
```

Then examine:

- A before B
- B before A
- overlapping A/B
- duplicate A

Ask whether the final state differs materially.

Example:

```text
restore(note) changes note.lifecycle
permanentDelete(note) changes note.lifecycle
```

Derived question:

> What result is authoritative when restore and permanent delete race on the same note?

Do not ask concurrency questions for local immutable transformations with no shared state.

---

## 8. Dependency contract projection

For each external dependency, identify the assumptions the feature makes about its contract:

- success semantics
- error semantics
- ordering
- idempotency
- latency/timeout behavior
- version compatibility
- consistency guarantees

Search for the contract first.

Then project contract uncertainty onto user-visible behavior.

Example:

```text
Feature assumes cloud restore returns exactly-once success.
Contract does not guarantee exactly-once execution.
```

Derived question:

> What behavior is required when the cloud restore request is retried after an unknown outcome?

---

## 9. Acceptance oracle derivation

For each acceptance statement, rewrite it as:

```text
input / precondition
observable action
observable expected result
```

If the expected result cannot be observed or distinguished from alternatives, derive a verification question.

Bad acceptance statement:

> Restore should be reliable.

Derived question:

> Which observable outcomes define successful restore, including metadata, attachments, location, and sync state?

This does not require every implementation detail to be asserted; it requires an externally meaningful oracle.

---

## 10. Cross-model interaction

The highest-value discoveries often come from interactions between different model dimensions.

Prioritize these combinations:

```text
state x failure
state x concurrency
rule x rule
rule x state
operation x invariant
operation x data relationship
scenario x dependency
acceptance x observable outcome
```

A candidate question is stronger when it can cite both sides of the interaction.

Example:

```text
Operation: restore
Invariant: active note must reference an existing folder
Relationship: note -> folder
```

The combined model produces a concrete missing decision about restore destination when the folder is absent.

---

## Candidate quality filter

Before creating a finding, require all of the following:

1. **Derivation** — identify the model elements that caused the question.
2. **Materiality** — explain how different answers could change behavior/correctness/acceptance.
3. **Evidence gap** — repository search did not find an authoritative answer.
4. **Implementation consequence** — without an answer, the coding agent would need to guess or leave an unsafe gap.

If one is missing, keep it as analysis noise or drop it.

---

## What this method does not claim

This method does not prove that all unknown-unknowns are found.

It creates a repeatable exploration process that:

- expands the current problem model
- discovers structurally implied questions
- converts discovered questions into explicit known-unknowns
- makes residual uncertainty visible
