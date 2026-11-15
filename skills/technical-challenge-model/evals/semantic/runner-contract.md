# Semantic Acceptance Runner Contract

## Baseline

Semantic runs MUST name the frozen Skill baseline SHA. A run whose `baseline_sha` differs from the acceptance baseline belongs to another experiment.

## Phase A — Development semantic runs

1. Build isolated sandboxes with `build_semantic_batch.py` using five repetitions per Dev case.
2. Start every repetition in a fresh model context.
3. Mount only the sandbox contents.
4. The model executes the Skill and writes `report.json`.
5. After the model exits, evaluator-side tooling validates and scores the run with `record_semantic_run.py`.
6. Expert-adjudicate every unexpected Finding.
7. Aggregate with `aggregate_semantic_results.py`.

Use Dev failures to improve the Skill. Classify every semantic failure before changing wording:

- `A_ANCHOR`: wrong/missed RequirementObligation or SystemConstraint grounding.
- `B_DECISION_EXTRACTION`: significant DesignDecision/Mechanism not identified correctly.
- `C_PRECONDITION`: must-be-true Claim missing or wrong.
- `D_COUNTEREXAMPLE`: failure path missing, implausible, or not connected to an anchor violation.
- `E_EVIDENCE`: wrong evidence type, adequacy, absence reasoning, or lifecycle treatment.
- `F_ADJUDICATION`: Finding/RequirementGap/EvidenceGap/OpenDecision/Verdict/Severity routed incorrectly.
- `G_SCOPE`: invented product behavior, architecture preference, or other scope expansion.

## Phase B — Frozen sealed holdout

1. Freeze Skill wording and record the exact baseline SHA.
2. Obtain a public holdout catalog from the independent curator.
3. Keep the evaluator oracle outside the agent-visible workspace.
4. Build fresh sandboxes from the public catalog only.
5. Run each case in fresh contexts; 3–5 repetitions are recommended.
6. Validate every `report.json` before scoring.
7. Score with evaluator-only `--oracle` access.
8. Expert-adjudicate unexpected Findings using `<case_id>/<run_id>/<finding_id>` keys.
9. Aggregate metrics.

If a holdout result causes a Skill wording change, invalidate the attempt and replace the exposed holdout case before re-running acceptance.

## Acceptance metrics

Pilot targets:

```text
Critical Defect Recall >= 0.90
Expert-Adjudicated Finding Precision >= 0.80
Clean-case False Positive Rate <= 0.10
Inter-run Stability >= 0.80
Scope Expansion Finding Count = 0
Critical Finding Traceability = 1.00
High/Blocker Evidence Grounding = 1.00
```

These are engineering acceptance targets for this Skill, not industry benchmarks.

## Commands

Build a batch:

```bash
python3 evals/scripts/build_semantic_batch.py PUBLIC_CASES.json BATCH_DIR \
  --skill-root skills/technical-challenge-model \
  --repetitions 5 \
  --baseline-sha <frozen-sha>
```

Record one completed run using an external oracle:

```bash
python3 evals/scripts/record_semantic_run.py \
  report.json PUBLIC_CASES.json <case-id> <run-id> result.json \
  --baseline-sha <frozen-sha> \
  --oracle /evaluator-only/holdout-oracle.json
```

Aggregate semantic records:

```bash
python3 evals/scripts/aggregate_semantic_results.py runs.json \
  --adjudications adjudications.json
```
