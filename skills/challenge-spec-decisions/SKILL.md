---
name: challenge-spec-decisions
description: Discover missing requirement or design concerns, organize unresolved choices into a dependency-ordered decision tree, and challenge risky answers through assumptions, evidence, counterexamples, boundaries, and consequences. Use for deep questioning, Gate1/spec challenge, engineering-readiness assessment, requirement discovery, architecture/design review, decision clarification, or when a user asks to grill, drill into, stress-test, or expose gaps in a PRD, spec, technical proposal, feature idea, or implementation plan. Do not use for a simple summary or ordinary proofreading.
---

# Challenge Spec Decisions

Turn an incomplete requirement or design into an explicit set of facts, decisions, evidence, findings, and residual unknowns. Combine three mechanisms without conflating them:

- Discovery determines what may have been missed.
- Grilling determines which unresolved decision to address next.
- Socratic challenge determines whether an important answer is defensible.

## Non-negotiable constraints

- Do not modify source documents or code while running the challenge. Produce a separate assessment unless the user later requests edits.
- Do not silently fill requirement gaps or convert assumptions into facts.
- Retrieve facts from available code, documents, configuration, contracts, and tests before asking the user.
- Ask humans only for genuine decisions, inaccessible evidence, or ownership-dependent knowledge.
- Ask one frontier question per interaction; do not dump a pre-generated questionnaire.
- Recompute the tree after every material answer. Do not follow a stale list.
- Scale challenge depth to risk; do not endlessly challenge low-risk details.
- Record unresolved uncertainty rather than hiding it behind recommendations.

## Shared state

Maintain an internal challenge ledger. Each node contains:

```yaml
id: D-001
question: "What must be resolved?"
type: FACT | DECISION | UNKNOWN
domain: SCENARIO | STATE | RULE | DATA | DEPENDENCY | FAILURE | ENVIRONMENT | OTHER
depends_on: []
risk: LOW | MEDIUM | HIGH | CRITICAL
why_important: "Why this affects correctness or readiness"
status: OPEN | RESOLVED | ACCEPTED_RISK | NOT_APPLICABLE
answer: null
evidence: []
assumptions: []
new_branches: []
owner: null
```

Treat `UNKNOWN` as a current knowledge state. Reclassify it as `FACT` or `DECISION` when its nature becomes clear.

## Workflow

### 1. Establish the challenge target

Identify the goal, artifact, lifecycle stage, in-scope behavior, relevant system context, decision authority, and required output. State material scope assumptions. If no document exists, treat the user's description as the source artifact.

### 2. Discover the problem space

Read [references/discovery.md](references/discovery.md) completely. Build an Exploration Map before asking questions. Search beyond written content for missing scenarios, states, rules, data semantics, dependencies, failures, recovery, and environmental conditions.

Discovery generates candidate nodes; it does not decide product semantics.

### 3. Build and traverse the decision tree

Read [references/grilling.md](references/grilling.md) completely. Convert material candidates into the shared node schema, connect prerequisite relationships, resolve retrievable facts, and choose the highest-value open frontier node.

When interaction is required, ask exactly one question with:

1. the question;
2. why it must be answered now;
3. two or three materially distinct options when useful, including trade-offs;
4. an invitation to specify another choice.

Do not ask downstream questions whose prerequisites remain unresolved.

### 4. Challenge important answers

For a medium-, high-, or critical-risk answer, or any answer containing a consequential claim, read [references/socratic-challenge.md](references/socratic-challenge.md) completely and apply the risk-appropriate challenge depth.

Do not accept “the platform handles it,” “it should work,” or equivalent assertions as evidence. Separate the selected decision from factual claims used to justify it.

### 5. Update and repeat

After each answer:

1. extract facts, decisions, assumptions, claims, and evidence;
2. test contradictions against prior state and source artifacts;
3. resolve, invalidate, split, or reclassify nodes;
4. add newly exposed branches;
5. recompute dependencies and the frontier;
6. continue while a blocking frontier exists.

An answer may invalidate a subtree. Preserve the reason for invalidation instead of deleting the history silently.

### 6. Judge readiness

Return one verdict:

- `PASS`: no unresolved blocking decision or unsupported critical assumption remains.
- `CONDITIONAL PASS`: bounded non-blocking unknowns remain with owners and closure conditions.
- `BLOCK`: at least one unresolved item can materially alter scope, correctness, architecture, safety, data integrity, verification, or recovery.

Do not infer `PASS` merely because the conversation stopped.

## Finding format

Create a finding only when evidence and reasoning show a real defect, gap, or readiness risk.

```yaml
id: F-001
severity: BLOCKER | HIGH | MEDIUM | LOW
type: MISSING | AMBIGUOUS | INCONSISTENT | INCORRECT | UNSUPPORTED_ASSUMPTION | EVIDENCE_GAP | UNDEFINED_BEHAVIOR | UNRESOLVED_DECISION | NON_VERIFIABLE
object: "Affected requirement, scenario, state, rule, interface, or component"
attribute: "Completeness, clarity, consistency, correctness, robustness, verifiability, or traceability"
problem: "Specific defect or gap"
evidence: []
reasoning: "Why the evidence establishes the problem"
counterexample: "Concrete triggering situation, when applicable"
impact: "User or system consequence"
required_resolution: "Decision, evidence, or definition needed; do not decide for the owner"
owner: null
status: OPEN | RESOLVED | ACCEPTED_RISK
```

Distinguish findings from exploratory questions. An unanswered low-value question is not automatically a defect.

## Final output

Produce a concise report in this order:

1. **Verdict and rationale** — verdict, blocking reasons, assessed scope.
2. **Resolved decisions** — decision, rationale, owner, affected branches.
3. **Confirmed facts** — fact, direct evidence, confidence.
4. **Open decisions** — dependency, owner, impact, blocking status.
5. **Findings** — sorted by severity using the required schema.
6. **Residual unknowns** — why unknown, evidence needed, owner, closure condition.
7. **Coverage summary** — explored domains, intentionally deferred domains, and remaining blind spots.

Keep fact, decision, assumption, finding, and recommendation visibly distinct. Preserve traceability from every blocker to its source node and evidence.
