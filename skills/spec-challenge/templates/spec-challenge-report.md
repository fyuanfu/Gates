# Spec Challenge Report

## 1. Verdict

**Verdict:** `READY | READY_WITH_WARNINGS | NOT_READY`

**Reason:**

- <short evidence-based reason>

---

## 2. Scope

**Target:** <feature/story>

**Specification:** <path or identifier>

**Sources inspected:**

- <source 1>
- <source 2>

**Source precedence / authority notes:**

- <note when sources overlap or conflict>

---

## 3. Behavior Model Understood

### Actors / Goals

- <actor -> goal>

### Scenarios

- <scenario id/name -> observable outcome>

### Rules / Invariants

- <rule or invariant>

### States / Transitions

- <source --event--> target>

### Data / Relationships

- <A -> B>

### Dependencies / Contracts

- <dependency -> relevant contract assumption>

### Observable Acceptance Outcomes

- <observable oracle>

---

## 4. Resolved Knowledge

Items that initially appeared unclear but were resolved from authoritative project knowledge.

| ID | Apparent gap | Resolution | Evidence |
|---|---|---|---|
| RK-001 | <what looked missing> | <authoritative answer> | <source/path/ref> |

Do not turn these into findings.

---

## 5. Blocking Findings

Use one section per finding.

### F-001 — <summary>

```yaml
id: F-001
classification: missing-decision | ambiguity | contradiction | unverifiable | dependency-gap | unsafe-assumption
severity: blocker
status: open

epistemic_state: known_unknown

discovered_by:
  operation: <e.g. state-transition-closure>
  model_elements:
    - <element 1>
    - <element 2>

evidence:
  - <evidence that creates the question>
  - <evidence that no authoritative answer was found>

question: >
  <single concrete unresolved question>

impact:
  - <behavior/correctness/compatibility/acceptance impact>

owner: <product | domain | architecture | dependency-owner | other>
recommended_action: <decision or evidence needed>
```

**Why this blocks implementation:** <why coding would otherwise require guessing>

---

## 6. Warnings

### W-001 — <summary>

```yaml
id: W-001
classification: <classification>
severity: warning
status: open
question: <question if any>
impact:
  - <impact>
owner: <owner>
recommended_action: <action>
```

**Why this can be deferred safely:** <reason>

---

## 7. Decisions Required

| Finding | Decision owner | Decision needed | Recommended default | Blocking? |
|---|---|---|---|---|
| F-001 | <owner> | <decision> | <recommendation or N/A> | Yes |

Only include decisions that cannot reasonably be retrieved from project knowledge.

---

## 8. Challenge Coverage

Record structural challenge operations that were applied.

| Challenge operation | Applied | Evidence / result |
|---|---:|---|
| Scenario branch expansion | Yes/No/N/A | <what was examined> |
| State-transition closure | Yes/No/N/A | <what was examined> |
| Rule overlap / precedence | Yes/No/N/A | <what was examined> |
| Invariant stress | Yes/No/N/A | <what was examined> |
| Multi-step partial success | Yes/No/N/A | <what was examined> |
| Data relationship mutation | Yes/No/N/A | <what was examined> |
| Shared-state concurrency | Yes/No/N/A | <what was examined> |
| Dependency contract projection | Yes/No/N/A | <what was examined> |
| Acceptance oracle derivation | Yes/No/N/A | <what was examined> |
| Cross-model interaction | Yes/No/N/A | <what was examined> |

`N/A` is valid when the model genuinely has no relevant structure. Do not force all operations onto every feature.

---

## 9. Residual Risk

List important uncertainty that remains after the challenge but is not a concrete unresolved finding.

- <residual uncertainty>

Never state that all unknown-unknowns have been eliminated.

---

## 10. Recheck Status

After decisions are resolved, record only affected rechecks.

| Finding | Resolution | Source-of-truth updated | Rechecked operations | Status |
|---|---|---|---|---|
| F-001 | <decision> | <path/ref> | <operations> | closed |

---

## 11. Handoff

**Implementation handoff allowed:** `YES | NO`

**Reason:** <short reason>

**Next workflow:**

- `grill-with-docs` / `grilling` when decisions remain
- `to-questionnaire` when another stakeholder owns the missing knowledge
- `to-spec` when decisions are resolved but a normalized buildable spec is still needed
- implementation workflow only when the verdict permits it
