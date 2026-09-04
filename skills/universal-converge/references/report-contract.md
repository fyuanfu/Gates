# Report Contract

Return Markdown with exactly four H2 sections in this order. Do not add an executive summary, methodology section, appendix, or repair plan outside them.

## Contents

- 1. Convergence Verdict
- 2. Claim Coverage
- 3. Findings
- 4. Traceability Evidence
- Language and evidence hygiene

## 1. Convergence Verdict

Use this fixed field order:

```text
Verdict: PASS | PASS_WITH_WARNINGS | BLOCK
Confidence: high | medium | low
Target: <feature/change/component/release slice>
Scope: <included repository/modules/artifacts>
Evidence mode: STATIC | EXECUTED | MIXED
Primary reason: <one evidence-based sentence>
Blocking findings: <IDs or none>
Evidence limitations: <none or concise list>
```

The primary reason must explain the highest-precedence verdict rule. Do not call `BLOCK` a test failure unless an executed result failed.

## 2. Claim Coverage

First return the summary table:

| Claim status | Count |
| --- | ---: |
| Satisfied | 0 |
| Partial | 0 |
| Contradicted | 0 |
| Unverifiable | 0 |

Then return one row per claim:

| Claim | Source | Criticality | Verdict | Confidence | Evidence basis |
| --- | --- | --- | --- | --- | --- |

Rules:

- `Source` contains all native intent/obligation references.
- `Evidence basis` contains short stable locations, not raw code.
- Counts must equal the detailed rows.
- Include zero counts and include every material claim.

## 3. Findings

Return the compact index:

| ID | Source | Claim | Layer | Type | Severity | Blocking | Finding |
| --- | --- | --- | --- | --- | --- | --- | --- |

If there are no findings, write `No findings.` after the header and do not invent rows.

For every finding, immediately follow the index with a detail block in ID order:

```text
### F-001 — <short title>

- Source references: <refs>
- Claim: <claim ID and statement>
- Layer / type / severity: <layer> / <type> / <severity>
- Description: <what is wrong and under which condition>
- Positive evidence: <stable locations or none>
- Counter evidence: <stable locations or none>
- Searched scope: <concepts, paths, symbols, branches, and inaccessible boundaries inspected for this finding>
- Impact: <delivery/user/engineering consequence>
- Recommendation: <what must be resolved or evidenced; no invented architecture>
- Confidence: high | medium | low
- Blocking: yes | no
```

Do not duplicate the same evidence excerpt across multiple findings; reuse locations.

## 4. Traceability Evidence

Return a compact chain for:

- every blocking finding;
- every HIGH or CRITICAL finding;
- every critical/high claim that is `UNVERIFIABLE`.

Use this fixed form:

```text
Source <native ref>
  -> Claim <claim ID>: <statement>
     -> Design: <locations, none, or not applicable>
     -> Implementation: <locations, none, or not inspected>
     -> Verification source: <locations, none, or not inspected>
     -> Executed result/runtime: <locations, none, or not available>
     -> Counter evidence: <locations or none found within stated scope>
  -> Claim verdict: <verdict>
  -> Finding: <finding IDs or none>
```

End the section with:

```text
Search boundary: <what was inspected and what was inaccessible>
Counter-search status: <complete/partial by critical or high claim>
```

## Language and evidence hygiene

- Match the user's language unless asked otherwise; keep canonical enum values in English.
- Distinguish `not found within scope`, `not inspected`, `not available`, and `not applicable`.
- Cite `path::symbol`, `path#line`, document section, native artifact ID, test ID, or result ID.
- Keep code excerpts under the minimum needed to explain the finding.
- Never report a tool action, inferred assumption, or task checkbox as evidence of behavior.
- Do not claim full repository coverage unless the inspected boundary establishes it.
