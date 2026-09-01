# Socratic Challenge Module

Use this module to test whether an important answer or claim is defensible. Challenge the reasoning, not the person. The goal is explicit assumptions, bounded evidence, and concrete failure consequences.

## 1. Set challenge depth

| Risk | Required checks |
| --- | --- |
| Low | definition, basic consistency |
| Medium | definition, conditions, assumptions, evidence, boundary |
| High/Critical | all eight checks below plus counter-evidence search |

Treat deletion, payment, authorization, privacy, security, migration, multi-device consistency, core state machines, concurrency, background execution, irreversible side effects, and recovery as high risk unless evidence justifies lower severity.

## 2. Run the eight checks

1. **Definition — What exactly?** Define terms, success, failure, and observable outcome.
2. **Conditions — Under what conditions?** State prerequisites and environmental scope.
3. **Assumptions — What must be true?** Expose platform, ordering, availability, identity, and behavioral assumptions.
4. **Evidence — How do we know?** Identify direct evidence and its applicability.
5. **Reasoning — Why does it follow?** Check the inference from evidence to conclusion for missing premises or overreach.
6. **Counterexample — When does it fail?** Construct a plausible falsifying case, not a fantastical edge case.
7. **Boundary — Where does it stop?** Test empty, maximum, duplicate, expired, old/new version, cross-account/device/region, and concurrency boundaries as relevant.
8. **Consequence — So what?** Trace user effect, data effect, propagation, detectability, and recoverability.

Ask only the minimum follow-up needed to resolve the highest-risk weakness. Many checks can be performed against available evidence without questioning the user.

## 3. Evaluate evidence

Prefer evidence in this order, while considering relevance and scope:

1. executable test or reproducible observation;
2. current code and configuration;
3. authoritative contract, protocol, or official platform guarantee;
4. current project documentation;
5. applicable historical production evidence;
6. expert judgment;
7. unsupported assumption.

An official document may prove platform behavior but not an OEM-specific guarantee. A test may prove one configuration but not all declared environments. Record the evidence boundary.

Search for both support and contradiction. Look for code paths, contracts, tests, logs, or platform clauses that would falsify the claim. Absence of contradiction is not proof.

## 4. Test the inference

Reject or qualify reasoning that:

- treats correlation as causation;
- generalizes from one environment beyond its evidence;
- substitutes mechanism presence for outcome guarantee;
- ignores timing, retries, duplication, reordering, or partial completion;
- assumes a dependency's best-effort behavior is a contract;
- proves the happy path while claiming recovery correctness;
- uses the proposed design itself as evidence that the requirement is satisfied.

Express the gap as `evidence → missing premise → conclusion`.

## 5. Build a useful counterexample

Construct the smallest realistic sequence that violates the claim:

```yaml
preconditions: []
events: []
failed_assumption: ""
observable_effect: ""
recovery_possible: true
```

Prioritize interruptions at side effects, duplicated execution, reordered remote events, identity changes, process death, dependency degradation, and stale data. Tie the counterexample to an explicit requirement, invariant, or user expectation.

## 6. Resolve the challenge

Classify the challenged answer as:

- `SUPPORTED`: evidence directly supports the bounded claim.
- `QUALIFIED`: valid only under explicit conditions or narrower scope.
- `REFUTED`: contradictory evidence or a valid counterexample defeats it.
- `UNSUPPORTED`: plausible but lacks adequate evidence.
- `DECISION_NEEDED`: no factual proof can select among legitimate policies.

For `QUALIFIED`, feed the conditions back into requirements and the decision tree. For `REFUTED` or `UNSUPPORTED`, create a finding when the claim is necessary for readiness. For `DECISION_NEEDED`, return ownership to Grilling.

Stop challenging when additional questioning will not change the decision, evidence requirement, risk classification, or downstream design. Record residual uncertainty instead of seeking philosophical certainty.

