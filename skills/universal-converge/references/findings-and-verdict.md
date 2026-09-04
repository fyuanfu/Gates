# Findings and Verdict Policy

Use this contract to convert claim results and cross-artifact gaps into deterministic findings and a gate verdict.

## Contents

- Canonical finding schema
- Finding types
- Layers
- Claim-to-finding mapping
- Restrict UNREQUESTED
- Severity
- Finding normalization
- Gate computation
- Verdict confidence

## Canonical finding schema

```yaml
id: F-001
source_refs:
  - AC-003
claim: CLM-003
layer: intent | design | implementation | behavior | traceability
type: MISSING | PARTIAL | CONTRADICTS | UNVERIFIABLE | UNTRACEABLE | UNREQUESTED
severity: CRITICAL | HIGH | MEDIUM | LOW
description: a reachable failure path permanently completes unfinished work
positive_evidence:
  - app/.../SyncWorker.kt::resumePending
counter_evidence:
  - app/.../SyncRepository.kt::markFailedAsCompleted
searched_scope:
  - app/.../SyncWorker.kt::resumePending
  - app/.../SyncRepository.kt state transitions
impact: some interrupted sync operations cannot resume
recommendation: resolve the terminal-state/recovery inconsistency and provide claim-linked verification evidence
confidence: high | medium | low
blocking: true
```

Use `none` for an empty evidence list. Never omit required fields.

## Finding types

- `MISSING`: affirmative bounded evidence establishes that a required element, condition, case, or implementation is absent.
- `PARTIAL`: a required claim is implemented or verified for only some material conditions.
- `CONTRADICTS`: direct evidence conflicts with accepted intent, an approved obligation, or another authoritative source.
- `UNVERIFIABLE`: reasonable search cannot establish or refute a required claim.
- `UNTRACEABLE`: an expected mapping or allocation cannot be connected across artifacts, without proving that runtime behavior fails.
- `UNREQUESTED`: inspected implementation expands system intent without an accepted source.

Do not use `MISSING` merely because evidence was not found. Do not use `UNTRACEABLE` as a synonym for missing implementation.

For every material intent claim, require design allocation evidence. If no design source or allocation can be found, emit `UNTRACEABLE` unless an authoritative project policy explicitly exempts that claim from design. Keep this independent from the behavior verdict: a claim may be `SATISFIED` while its design allocation finding remains non-blocking.

## Layers

- `intent`: ambiguity or contradiction within authoritative product intent.
- `design`: missing or contradictory approved allocation/decision.
- `implementation`: code, configuration, schema, resource, or wiring gap.
- `behavior`: observable required outcome is partial or contradicted.
- `traceability`: mapping between accepted source, claim, work, implementation, or verification cannot be established.

Choose the layer containing the problem, not the artifact where it was first noticed.
Use `traceability` for missing, partial, or unlinked verification/oracle evidence. Use `behavior` when an executed test result or runtime observation directly contradicts the required outcome.

## Claim-to-finding mapping

| Claim verdict | Default finding | Notes |
| --- | --- | --- |
| `SATISFIED` | none | A separate design/verification/traceability finding may still exist. |
| `PARTIALLY_SATISFIED` | `PARTIAL` | Cite uncovered conditions or narrowing counter paths. |
| `CONTRADICTED` | `CONTRADICTS` | Cite direct counter evidence. |
| `UNVERIFIABLE` | `UNVERIFIABLE` | State the searches and missing/inaccessible evidence. |

Use `MISSING` instead of the default only when the evidence model's absence rule is met. Use `UNTRACEABLE` for an independent allocation/mapping gap.

## Restrict UNREQUESTED

Report `UNREQUESTED` only when evidence discovered while tracing in-scope claims shows intent-expanding behavior such as:

- new user-visible behavior or business rule;
- new public interface or compatibility surface;
- new permission, data collection, or persistence behavior;
- new external side effect;
- widened product policy or scope.

Do not scan broadly for unrequested behavior. Do not report utilities, logs, framework glue, refactors, defensive checks, or ordinary error handling solely because they lack a requirement link.

## Severity

Assign severity from impact and claim criticality. Layer alone never determines severity.

### CRITICAL

Use when the issue can cause severe safety/security/privacy harm, unrecoverable corruption or loss, total failure of a non-negotiable capability, or direct violation of a critical approved constraint.

### HIGH

Use when the issue breaks or makes unverifiable a required critical/high claim, core AC/rule/invariant, P0/P1 scenario, public contract, or mandatory approved engineering obligation.

### MEDIUM

Use for a secondary required scenario, bounded recovery/compatibility weakness, material verification gap, or significant design/traceability gap that does not defeat core acceptance.

### LOW

Use for minor non-core mismatch, low-risk unrequested behavior, or low-risk traceability/documentation weakness.

Do not lower severity because confidence is low. If the impact itself is uncertain, state the uncertainty and choose the highest level directly supported by evidence.

## Finding normalization

Merge findings only when all are the same:

- claim or obligation;
- failing condition;
- cause location;
- impact;
- remediation owner/decision.

Keep separate findings if product, design, implementation, or verification owners must make different decisions. A claim verdict and a traceability gap can therefore produce separate findings.

## Gate computation

Apply rules from top to bottom.

### BLOCK

Return `BLOCK` when any condition is true:

1. at least one `CRITICAL` finding exists;
2. a `REQUIRED` critical/high claim is `CONTRADICTED` or `PARTIALLY_SATISFIED`;
3. a `REQUIRED` critical/high claim is `UNVERIFIABLE` after required search;
4. an `APPROVED` critical/high engineering obligation is contradicted or missing;
5. unresolved counter evidence materially undermines a required core claim;
6. authoritative intent is internally contradictory for a core behavior, so safe delivery acceptance cannot be determined;
7. implementation artifacts for the declared delivery target are unavailable, so core convergence cannot be evaluated.
8. no in-scope obligation can be admitted as `REQUIRED` or `APPROVED`, so convergence has no authoritative baseline.

### PASS_WITH_WARNINGS

Return `PASS_WITH_WARNINGS` when no BLOCK rule applies and at least one condition is true:

- a medium/low required claim is partial or unverifiable;
- a non-blocking design, verification, or traceability gap exists;
- low-risk intent-expanding behavior exists;
- search or access limitations remain but do not affect core claims;
- all required claims are statically satisfied but material execution evidence requested by project policy is unavailable.

### PASS

Return `PASS` only when:

- at least one in-scope `REQUIRED` or `APPROVED` claim exists;
- every `REQUIRED` and `APPROVED` claim is `SATISFIED`;
- mandatory counter-evidence searches are complete;
- no material unresolved counter evidence exists;
- no findings remain;
- scope and evidence limitations do not affect the conclusion.

Do not use percentages, averages, or majority voting. One blocking claim is sufficient to BLOCK.

## Verdict confidence

Report confidence separately:

- `high`: authoritative scope is clear and direct evidence covers material paths, including executed evidence where required.
- `medium`: conclusion is supported, but some evidence is static or a non-core boundary was not exercised.
- `low`: material access, authority, or execution limitations remain.

Confidence does not soften a BLOCK or upgrade a report to PASS.
