# Semantic evaluation

The `evals/cases` corpus forward-tests RGQ behavior without exposing expected answers to the reviewer. Each case contains a raw `input.md` and a separate `expected.json` for the evaluator.

Run the Skill on `input.md`, save the canonical result as `review.json`, then evaluate it:

```bash
python3 scripts/evaluate_semantics.py <review.json> evals/cases/<case>/expected.json
```

Expectations may require a Verdict, one or more findings, forbidden findings, and a maximum Finding count. Finding matching supports `source_requirement_id`, `defect_type`, `consequence_type`, `minimum_severity`, and a case-insensitive `text_pattern` applied to the Finding title, problem, impact, and required decision.

Use source requirement IDs from the raw input when present. `minimum_severity` means the observed Finding may be equally or more severe. Forward-test agents receive only `input.md`; evaluators receive only the resulting `review.json` and `expected.json`.
