# Skill evaluation guide

## Principle

The Skill is developed RED → GREEN → REFACTOR. Semantic evaluation must use fresh contexts. Never tune on holdout answers.

## Dataset split

- `evals/dev/`: visible development cases used for RED/GREEN/REFACTOR.
- `evals/holdout/`: acceptance cases not used to change Skill wording.
- Expected answers are never mounted into the review agent's execution sandbox.

A case runner must expose only:

```text
SKILL.md
required references
case input
explicitly supplied mock repository/context
```

It must hide expected answers, prior outputs, aggregate scores, and other cases.

## Repetitions

For wording/behavior tests use at least five fresh runs per dev variant when a fresh-agent runner exists. Track both mean quality and variance. A single good sample is not evidence of stable behavior.

## Deterministic oracle

Machine checks may score:

- required known finding type detected;
- forbidden finding type absent;
- allowed Verdict;
- RequirementGap/EvidenceGap count;
- JSON/schema/cross-reference integrity;
- critical Finding traceability and evidence presence.

Machine checks must not label an unexpected semantic Finding as false merely because it was absent from the answer key.

## Expert adjudication

Every unexpected Finding enters expert adjudication:

```text
valid | invalid | duplicate | unverifiable
```

Confirmed Finding Precision is undefined until all findings needed by that metric are adjudicated. Do not report a proxy as real Precision.

## Holdout gate

Use dev cases to tune the Skill. Run holdout only after wording is frozen for an acceptance attempt. Any change made because of a holdout failure invalidates that holdout score; move the case into dev and introduce a new unseen holdout case.

## Current harness limitation

If the runtime has no fresh-context/subagent/model runner, prepare the semantic cases and deterministic harness but do not claim semantic RED/GREEN or production quality thresholds were executed. Mark the Skill `PILOT` until fresh-context evaluation is performed.
