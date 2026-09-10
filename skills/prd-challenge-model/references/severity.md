# Severity and confirmation

## Principle

Assign severity from the worst credible downstream consequence of a reasonable implementation interpretation if the requirement enters development unchanged. Do not grade wording quality and do not lower severity because confidence is low.

| Severity | Required consequence |
|---|---|
| `P0` | Severe data loss, major privacy/security incident, unrecoverable critical business incident, or complete loss of a core capability supported by supplied requirement evidence |
| `P1` | Primary user goal failure, false success, critical state corruption, missing critical path, severe behavioral ambiguity, or conflict in a core business rule |
| `P2` | Non-core failure omission, local boundary gap, secondary behavior uncertainty, or bounded UX behavior ambiguity |
| `P3` | Low-impact requirement defect that still has an explicit downstream implementation or verification consequence |

Harmless terminology, style, formatting, and spelling issues are Observations, never P3.

## P0 burden of proof

Use P0 only when supplied evidence establishes both extraordinary impact and a credible path to it. At least one of these must be explicit or directly derivable from authoritative requirements:

- systemic or bulk loss affecting many records/users;
- loss of irreplaceable critical assets;
- major privacy, security, financial, or regulated-data exposure;
- unrecoverable failure of a business-critical capability at broad scope.

Irreversibility alone does not make an issue P0. Accidental deletion of one ordinary user item, without evidence of broader scale or exceptional criticality, is normally P1 because it is a serious user-goal failure but not yet a catastrophic incident. If scale or criticality is unknown, retain the supported severity and ask a separate non-blocking question; do not speculate upward.

## Confirmation evidence

Every Finding requires source Evidence and completed disproof. Every P0/P1 requires at least one of:

### Failure Witness

```json
{
  "given": "relevant precondition",
  "when": "trigger, interruption, or failure",
  "then": "wrong result still permitted by the current requirement"
}
```

### Contradiction Proof

```json
{
  "statement_a": {"requirement_id": "R-001-0001", "meaning": "first behavior"},
  "statement_b": {"requirement_id": "R-002-0004", "meaning": "mutually exclusive behavior"}
}
```

`CONTRADICTORY` always requires a Contradiction Proof and at least two source Evidence entries.

## Disproof budget

| Potential severity | Required search |
|---|---|
| P0 | Global authorized evidence plus witness/proof |
| P1 | Targeted evidence, global fallback when needed, plus witness/proof |
| P2 | Local and linked-Slice evidence |
| P3 | Basic source-evidence check |

Classify a disproved candidate as REJECTED. Classify genuinely inaccessible owner knowledge as NEEDS_CONTEXT. If the absence itself makes a critical behavior indeterminate, confirm a MISSING Finding instead.
