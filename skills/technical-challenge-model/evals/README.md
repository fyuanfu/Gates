# Technical Challenge Model evaluation

Status: **PILOT** until fresh-context semantic runs and holdout expert adjudication are completed.

## Dataset

- `dev/`: 20 development cases. Use these for RED/GREEN/REFACTOR.
- `holdout/`: 10 acceptance cases. Do not inspect or tune Skill wording against holdout expected answers before an acceptance attempt.
- `coverage-matrix.json`: coverage view across design stage, mechanism lifecycle, primary challenge lens, expected output class, and claim kind.

Each split stores a `cases.json` catalog. Every record contains input, optional context, metadata, and a hidden expected answer. The sandbox builder extracts only input/context for the review agent.

## Isolation

Prepare a semantic-run sandbox with:

```bash
python3 evals/scripts/prepare_case.py evals/dev/cases.json tc-dev-001 /tmp/tc-case
```

The sandbox contains only `SKILL.md`, Skill references, the selected `input.md`, and its explicit `context/`. It does **not** contain expected answers, prior outputs, other cases, or aggregate scores.

## Deterministic checks

```bash
python3 scripts/run_contract_tests.py
python3 evals/scripts/validate_dataset.py evals
```

Deterministic scoring may verify known required/forbidden finding types, allowed Verdict, and expected gap counts. It must not classify an unexpected semantic Finding as false.

## Expert adjudication

Unexpected Findings require an expert label:

```text
valid | invalid | duplicate | unverifiable
```

Because report-local Finding IDs such as `F-001` repeat across cases and repetitions, adjudication keys MUST be globally scoped as:

```text
<case_id>/<run_id>/<finding_id>
```

Example:

```text
tc-dev-001/run-01/F-002
```

Copy `adjudication-template.json` and use these namespaced keys. Real Finding Precision is undefined while required adjudications remain unresolved.

## Holdout sealing status

The current 10 `holdout/cases.json` fixtures are **candidate holdout cases, not an acceptance-sealed set for this authoring session**. Their expected answers were inspected while verifying the evaluation harness. They remain useful as regression fixtures, but production semantic acceptance requires an independent curator/runner to replace or re-seal an unseen holdout set before execution.

## Semantic acceptance

When a fresh-context runner is available:

1. Run each dev variant at least five times while developing wording.
2. Freeze Skill wording.
3. Run holdout cases without exposing answer keys.
4. Expert-adjudicate unexpected Findings using namespaced evaluation keys.
5. Report Recall, Precision, verdict accuracy, false positives on clean cases, and inter-run variance.

Any Skill change motivated by holdout failure invalidates that holdout attempt. Move the exposed case into dev and replace it with a new unseen holdout case.
