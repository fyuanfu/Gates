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


## Semantic failure taxonomy

Before changing Skill wording, classify the observed failure:

```text
A_ANCHOR              wrong/missed requirement or system-constraint grounding
B_DECISION_EXTRACTION significant decision/mechanism not identified correctly
C_PRECONDITION        must-be-true Claim missing or incorrect
D_COUNTEREXAMPLE      failure path missing, implausible, or not connected to an anchor
E_EVIDENCE            wrong evidence type/adequacy/lifecycle/absence reasoning
F_ADJUDICATION        Finding/Gap/Verdict/Severity routed incorrectly
G_SCOPE               invented product behavior, preference, or scope expansion
```

## Fresh-context semantic protocol

1. Freeze a baseline SHA.
2. Use `build_semantic_batch.py` to create isolated case × repetition sandboxes.
3. Start every sandbox in a fresh model context.
4. The review model sees only Skill/references/input/context and writes `report.json`.
5. Evaluator-side tooling validates the report and runs `record_semantic_run.py`.
6. Unexpected Findings receive independent expert adjudication.
7. Aggregate with `aggregate_semantic_results.py`.

For production holdout, public cases and evaluator oracle MUST be separate. Supply the hidden oracle only to `record_semantic_run.py --oracle` after the model has completed the run.

Pilot semantic targets:

```text
Critical Defect Recall >= 0.90
Expert-Adjudicated Finding Precision >= 0.80
Clean-case False Positive Rate <= 0.10
Inter-run Stability >= 0.80
Scope Expansion Finding Count = 0
```

These are project acceptance targets, not general industry benchmarks.
