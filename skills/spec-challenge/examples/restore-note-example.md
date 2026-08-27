# Example — Restore Deleted Note

This example demonstrates the intended distinction between:

- repository search
- structural challenge
- finding
- known unknown

It intentionally does **not** record `unknown_unknown` as a finding state.

---

## Input spec

```text
Story:
As a user, I can restore a deleted note from Trash.

Scenario:
Given a note is in Trash
When I restore it
Then the note is restored to its original folder
```

---

## Step 1 — SEARCH

Apparent gap:

> How long can a deleted note remain restorable?

Repository search finds:

```text
RetentionPolicy: deleted notes are retained for 30 days.
```

Result:

```yaml
id: RK-001
status: resolved_from_repository
resolution: Deleted notes are restorable for 30 days.
evidence: RetentionPolicy
```

This is **not** a Finding.

It was an apparent gap whose answer already existed in project knowledge.

---

## Step 2 — MODEL

Evidence-backed model:

```text
State:
ACTIVE -> TRASHED -> ACTIVE

Operation:
restore(note)

Relationship:
Note -> Folder

Rule:
TRASHED notes may be restored within 30 days.

Expected outcome:
Restored note returns to original folder.
```

Missing from the current model:

- behavior if original folder no longer exists
- behavior of partial restore if restore has multiple persistent effects

These are not findings yet. They are model gaps/candidates requiring derivation and search.

---

## Step 3 — STRUCTURAL CHALLENGE

### Challenge A — data relationship mutation

Model elements:

```text
Operation: restore(note)
Relationship: Note -> Folder
Folder has an independent lifecycle from Note.
```

Transformation:

```text
Referenced target changes independently -> target can be missing at restore time
```

Derived question:

> What is the required restore destination when the original folder no longer exists?

Search is repeated. No authoritative answer is found.

Materiality:

Different answers produce different user-visible behavior:

- restore to root
- recreate folder
- reject restore

Without a decision, a coding agent must invent behavior.

Result: create Finding F-001.

```yaml
id: F-001
summary: Restore destination is undefined when the original folder is missing
classification: missing-decision
severity: blocker
status: open

epistemic_state: known_unknown

discovered_by:
  operation: data-relationship-mutation
  model_elements:
    - "Operation: restore(note)"
    - "Relationship: Note -> Folder"
    - "Folder lifecycle is independent"

evidence:
  - "Spec requires restore to original folder"
  - "No fallback rule found in spec, domain docs, ADRs, code, or tests"

question: >
  What is the required restore destination when the original folder no longer exists?

impact:
  - user-visible behavior
  - data consistency

owner: product
recommended_action: define fallback behavior
```

Important:

The Finding is **currently a known unknown** because the question can now be stated explicitly.

The report does not claim:

```text
previous_state = unknown_unknown
```

That historical epistemic state is not provable from the record.

---

### Challenge B — multi-step partial success

Suppose repository exploration shows restore currently requires these persistent effects:

```text
1. move attachment files
2. update note metadata
3. remove trash entry
4. mark sync state dirty
```

The challenge does not ask a canned question such as:

> What happens on process death?

Instead it applies the model operation:

```text
multiple persistent effects
+
execution can stop between effects
=
possible persistent intermediate state
```

Derived question:

> Which state is valid if attachment files are moved but note metadata has not yet been updated?

Search finds an existing transaction/recovery policy that guarantees replay until metadata and trash state converge.

Result:

```yaml
id: RK-002
status: resolved_from_repository
resolution: Restore is replayable and recovery converges to a single ACTIVE state.
evidence: RestoreRecoveryPolicy + existing recovery tests
```

No Finding is created.

This demonstrates why **SEARCH must run both before and after challenge derivation**.

---

## Step 4 — VERDICT

Because F-001 remains unresolved:

```text
Verdict: NOT_READY
```

Reason:

```text
The coding agent cannot implement the missing-folder restore path without inventing externally observable product behavior.
```

After the product owner decides:

```text
If original folder is missing, restore to the root folder.
```

The source of truth is updated and affected challenge operations are rerun.

If no blocker remains:

```text
Verdict: READY or READY_WITH_WARNINGS
```

---

## Key lesson

The intended flow is:

```text
behavior model
    -> structural challenge
    -> newly discovered concrete question
    -> repository search
    -> finding only if still unresolved and material
    -> known unknown
    -> decision
    -> known known
```

`Unknown unknown` is the motivation for challenge, not a reportable Finding type.
