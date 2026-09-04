---
name: universal-converge
description: Verify whether a software implementation converges with accepted product and engineering intent. Use for delivery-readiness gates, requirement-to-code or design-to-code consistency checks, acceptance-criteria coverage, architecture allocation reviews, and implementation traceability audits. Do not use for general code-quality review, redesign, or remediation work.
---

# Universal Converge

## Mission

Determine whether the current implementation has converged with accepted product and engineering intent. Prove accepted commitments; do not expand or reinterpret them.

Operate read-only against the reviewed system. Do not edit input requirements, designs, work items, code, configuration, tests, or existing reports. You may create a new Converge report artifact when requested. Remediation belongs to a separate skill or later task.

Match the user's language in the report.

## Non-negotiable rules

1. Treat artifact meaning, not filenames or process conventions, as authoritative.
2. Treat accepted requirements, acceptance criteria, scenarios, rules, invariants, contracts, and approved technical constraints as intent. Do not treat tasks, issues, plans, or commit notes as intent or proof.
3. Derive claims as implementation-neutral facts that must hold. Do not invent mandatory components, frameworks, storage, schedulers, classes, or other implementation choices.
4. Require evidence for every material claim. Search for both supporting and counter-evidence before assigning a verdict.
5. Use design and work artifacts as navigation hints, never as the boundary of code discovery.
6. Use risk patterns only to expand exploration or counter-evidence searches. Never promote a risk pattern or model-derived concern into a blocking requirement without authoritative support.
7. Separate missing implementation, insufficient evidence, and missing traceability. Do not collapse them into one generic gap.
8. Base severity on impact to accepted intent, not on the artifact layer where the problem appears.
9. Do not return `PASS` from task completion markers, symbol-name matches, framework presence, test existence, or an isolated happy path.
10. Distinguish test source from executed results. Never state that a test ran or passed when only test code is available.
11. Expose conflicting authoritative artifacts and unavailable evidence. Never resolve either with an unstated assumption.
12. Restrict review to the requested target and the dependencies required to evaluate its claims; do not drift into a repository-wide quality review.
13. Fail closed when accepted intent cannot be established. Zero authoritative claims can never produce `PASS` or `PASS_WITH_WARNINGS`.

## Load the operating references

- Before classifying inputs or extracting intent, read [references/artifact-and-claim-model.md](references/artifact-and-claim-model.md).
- Before searching or weighing evidence, read [references/evidence-model.md](references/evidence-model.md).
- Before generating findings and the final gate, read [references/findings-and-verdict.md](references/findings-and-verdict.md).
- Before producing the final response or a report file, read [references/report-contract.md](references/report-contract.md).

Read every applicable reference completely. The references contain normative schemas and thresholds, not optional background.

## Scale execution

Use one agent for a small feature or tightly bounded change. When the scope is large and delegated agents are available and permitted, keep one orchestrator and separate three responsibilities: intent and claim analysis, evidence exploration, and final verdict review. The verdict reviewer must independently challenge evidence sufficiency, over-inference, finding duplication, severity, and gate computation. The orchestrator retains the canonical IDs and produces the single final report.

## Workflow

### 1. Establish review scope

Identify the requested feature, change, release, or repository scope. Record user-supplied artifact paths, explicit exclusions, inaccessible areas, and one evidence mode: `STATIC`, `EXECUTED`, or `MIXED`.

If no scope is stated, infer the narrowest defensible scope from the current change and related artifacts. State the inference. Ask only when materially different scope choices would change the gate result.

### 2. Discover and classify artifacts

Inspect the project structure, change metadata when available, headings, content semantics, and cross-references. Classify each relevant artifact as `intent`, `design`, `work`, `implementation`, `verification`, or `unknown` when confidence is too low.

Do not require `spec.md`, `plan.md`, `tasks.md`, or any fixed workflow. Record authority and classification confidence. Apply the authority-admission rules before extracting any blocking claim. Resolve conflicting sources using the artifact authority rules; expose unresolved authoritative conflicts instead of choosing silently.

### 3. Build the Intent Inventory

Extract only accepted, material commitments within scope. Preserve source location, statement, type, priority or criticality when declared, and authority.

Distinguish:

- **Declared obligation:** directly supported by an authoritative artifact and eligible to affect the gate.
- **Derived concern:** inferred from experience, architecture knowledge, or risk patterns; use only to guide discovery until authoritative support is found.

Do not silently strengthen, weaken, merge, or complete ambiguous intent. If ambiguity prevents a reliable claim, preserve the ambiguity as an unverifiable condition. If no `REQUIRED` or `APPROVED` intent can be admitted, record an intent-layer extraction gap and stop any path to a passing gate.

### 4. Build Verification Claims

Create one or more independently decidable claims for each material intent. Phrase each claim as a required observable behavior or engineering property, not as an implementation prescription.

For every claim, record a stable claim ID, source intent and exact source reference, normalized statement, expected evidence categories, criticality and its source, applicable conditions, and unavoidable assumptions.

Split compound intent when its parts can fail independently. Do not create claims from work artifacts alone.

When native IDs are unavailable, sort by canonical source path, source location, and normalized claim text before assigning generated IDs. Merge semantic duplicates while retaining every source reference.

### 5. Discover evidence per claim

Use progressive disclosure:

1. Start with intent artifacts, design/work indexes, project structure, and declared scope.
2. Search design, implementation, configuration/schema, and verification artifacts for one claim at a time.
3. Expand only as needed through domain concepts, states, rules, interfaces, call paths, data flow, state ownership, dependencies, runtime wiring, and configuration.

Compute search scope as:

`declared scope + intent-driven discovery + dependency expansion`

Trace behavior end to end. A type, dependency, API, or test name is only indirect evidence unless its path and assertions establish the claim.

Always evaluate intent → design allocation for every material intent claim. Use `not applicable` only when an authoritative project policy explicitly exempts that claim from design allocation; absence of a design artifact is not an exemption. Evaluate the other relationships when applicable:

1. intent → implementation/behavior;
2. approved design obligation → implementation;
3. intent → verification/oracle;
4. work declaration → implementation.

Keep a per-claim search ledger. Apply the evidence-closure and practical-exhaustion stopping rules in `references/evidence-model.md`.

### 6. Search for counter-evidence

Actively try to falsify each material claim. Inspect alternative branches, error handling, lifecycle transitions, persistence boundaries, competing state updates, feature flags, configuration variants, and test exclusions relevant to that claim.

Use domain risk patterns as optional search prompts without limiting open exploration. Record meaningful counter-evidence and the scope searched even when none is found.

Positive and counter-evidence search is mandatory for every `critical` and `high` claim. Inspect applicable alternate, error, lifecycle, recovery, configuration, or bypass paths; do not satisfy this rule with a generic statement that no counter-evidence was seen.

### 7. Evaluate each claim

Assign exactly one claim verdict: `SATISFIED`, `PARTIALLY_SATISFIED`, `CONTRADICTED`, or `UNVERIFIABLE`.

Explain why the evidence reaches that threshold and assign confidence. Keep behavior satisfaction separate from design traceability; implemented behavior may be satisfied while design allocation remains a warning. Confidence never upgrades insufficient evidence into satisfaction.

### 8. Generate findings

Create findings only for material gaps or intent-expanding behavior. Use only `MISSING`, `PARTIAL`, `CONTRADICTS`, `UNVERIFIABLE`, `UNTRACEABLE`, or `UNREQUESTED`.

Attach one primary layer: `intent`, `design`, `implementation`, `behavior`, or `traceability`. Classify missing or unlinked verification evidence as `traceability`; use `behavior` only when an executed result directly contradicts the required outcome.

Every finding must identify source intent, claim, positive evidence, counter-evidence where applicable, searched scope, impact, severity, confidence, and a non-prescriptive recommended action.

Report `UNREQUESTED` only for implementation that expands system intent, such as new user-visible behavior, business rules, public interfaces, permissions, data collection, persistence, or external side effects. Do not flag ordinary utilities, framework glue, logging, defensive handling, or refactoring merely because they lack a direct requirement reference.

### 9. Issue the gate verdict

Derive one result from all in-scope claim verdicts and findings: `PASS`, `PASS_WITH_WARNINGS`, or `BLOCK`.

Apply the exact precedence policy in `references/findings-and-verdict.md`. Do not average findings or let many weak signals manufacture a block. List blocking finding IDs explicitly.

## Completion conditions

Return a final verdict only after:

- material intent within scope has been inventoried;
- at least one authoritative `REQUIRED` or `APPROVED` claim exists; otherwise the verdict is `BLOCK` with an intent-layer extraction finding;
- each material intent maps to at least one claim or an explicit extraction gap;
- each claim records positive-evidence and counter-evidence search results;
- each claim has a verdict and confidence;
- every finding is traceable to evidence and accepted intent, except constrained `UNREQUESTED` findings;
- the aggregate gate verdict follows the documented policy.
- test source and executed results are labeled separately;
- every critical/high claim records counter-search status;
- scope, evidence mode, inaccessible areas, and search limitations are explicit.

If artifacts, repository access, build outputs, or runtime evidence are unavailable, identify the exact limitation. Use `UNVERIFIABLE` where the limitation prevents proof; never fabricate evidence or infer `PASS` from absence of findings.

## Output contract

Produce exactly these four literal H2 headings, including their numeric prefixes and order:

1. `## 1. Convergence Verdict` — gate, scope, top reason, blocking IDs, limitations.
2. `## 2. Claim Coverage` — counts and a per-claim verdict table.
3. `## 3. Findings` — prioritized summary plus full evidence records.
4. `## 4. Traceability Evidence` — source intent → claim → design/code/test/counter-evidence → claim verdict.

Do not add, rename, renumber, or reorder top-level sections. Follow every field and table rule in `references/report-contract.md`.

Use stable IDs such as `INT-001`, `CLM-001`, `EVD-001`, and `F-001`. Cite repository evidence with file paths and symbols or line references whenever available. Clearly label facts, inferences, missing evidence, and unknowns. Include every required field even when its value is `none`, `unknown`, `not inspected`, `not available`, or `not applicable`.
