# Semantic evaluation protocol

Status: 12 provisional synthetic cases, not expert Gold Set. Expected roots are seed targets, not an exhaustive oracle. No model quality improvement has yet been measured.

From the Skill directory:
    python3 evaluations/evaluate.py evaluations/cases.json --prepare /tmp/rgq-blind
Run each input independently in a clean Codex session. Give the reviewer only the generated Markdown and the scope it contains; never expose cases.json, its labels, or another variant's outputs. Use the same model version, reasoning settings, allowed context, budget and input across three arms:
A: direct requirement review, no Skill; B: original prd-challenge-model2.0.0 at faa9ca1d189b59320d3a5b1b4b7ef573ed0ad6fa; C: enhanced Skill branch. For A require comparable finding ID, severity, root decision and evidence. Record model, revision, token usage if available, wall time, completion, tool failures and raw results for each run. Repeat with independent sessions; report variability.

A human reviewer, blind to the arm, matches each finding to at most one expected root based on the required product decision and impact, not title wording. Record unmatched/duplicate findings; if an additional valid root is found, adjudicate and update the reference across all arms before rescoring. Inspect original quote and scope separately. Confirm severity labels before treating this set as gold. Include completed and incomplete runs, not just successful runs. Report token/time and human verification effort separately.

Create a match file:
    {"runs":[{"case_id":"C01","completed":true,"findings":[{"id":"F-0001","root_id":"D1","severity":"P1"},{"id":"F-0002","root_id":null,"severity":"P2"}]}]}
Use null only for genuinely unmatched findings. Missing cases are counted as incomplete and expected roots missed.
    python3 evaluations/evaluate.py evaluations/cases.json --score matches.json

The scorer reports root recall, precision (duplicates penalized), missed blocking roots including downgraded severity, false blocking findings and incomplete count. Review false positives, quote accuracy, scope errors and duplicate mechanisms manually. Never optimize against test labels in the prompt. Expand with independently adjudicated real PRDs; keep development and frozen holdout datasets separate. Ablate M1 modeling, M5 challenge and M6 disproof separately on the development set before frozen comparison. Do not claim improved capability unless matched evaluations support it.

Engineering tests:
    cd scripts
    python3 -m unittest -v test_verify_sources
The eight source-verifier cases passed in an isolated Python environment; scoring logic was checked with synthetic match assertions. These tests do not substitute for real model evaluation.
