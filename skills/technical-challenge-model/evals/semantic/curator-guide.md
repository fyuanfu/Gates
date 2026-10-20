# Semantic Holdout Curator Guide

The production acceptance set must be created by an **independent curator** who did not tune the Skill wording and did not participate in the implementation review that produced the baseline.

## Objective

Create 10–15 genuinely unseen Technical Challenge cases that test whether the Skill generalizes beyond the development fixtures.

At least five cases must be **hard negative** designs: they should look risky at first glance but already contain the mechanism/evidence needed to satisfy the accepted obligation. These cases protect Finding Precision and clean-case false-positive rate.

## Required coverage

The final sealed set should jointly cover:

- `architecture`, `high_level`, and `detailed` design stages;
- `existing`, `planned`, `modified`, and `removed` mechanisms;
- Coverage Finding and Counterexample Finding paths;
- RequirementGap, EvidenceGap, OpenDecision, and clean PASS outputs;
- concurrency, ordering, idempotency, atomicity, dependency failure, compatibility/migration, lifecycle/persistence, and brownfield SystemConstraint cases.

## Sealing rule

Public inputs and hidden oracle are separate artifacts.

The public catalog contains only:

```text
case_id
metadata
input
context
```

The evaluator oracle contains only:

```text
case_id
expected
```

The **oracle must stay outside** the review agent sandbox and outside any workspace visible to the model executing the Skill. It may be stored in a curator-controlled location and supplied only to the evaluator after `report.json` exists.

Do not commit a new production oracle into the same repository path that the review agent can browse during acceptance.

## Oracle quality

For each case, record:

- required known Finding type(s), if any;
- forbidden Finding types only when clearly invalid;
- allowed Verdicts;
- expected counts of RequirementGap/EvidenceGap/OpenDecision;
- whether the case is intended to be a clean hard-negative case;
- a short human rationale kept with the curator, not mounted into the review sandbox.

Unexpected Findings are not automatically false positives. They go to expert adjudication.

## Contamination rule

If Skill wording is changed because of an acceptance case, that case is no longer unseen. Move it into Dev/regression and replace it with a new independently curated case before the next acceptance attempt.
