# Technical Challenge Model Implementation Plan

> **Execution:** Use `superpowers:subagent-driven-development` when a subagent runner exists; otherwise use `superpowers:executing-plans`.  
> **Spec:** `docs/skills/technical-challenge-model.md`

**Goal:** Deliver a tested `technical-challenge-model` Skill that challenges existing technical designs against accepted requirements and Brownfield constraints without inventing product behavior.

**Architecture:** Compact `SKILL.md` orchestrates five references. Canonical JSON is validated and deterministically adjudicated/rendered. Semantic quality is evaluated with isolated Dev/Holdout cases and expert adjudication of unexpected Findings.

**Tech Stack:** Markdown, JSON, Python 3 standard library, GitHub branch `technical-challenge-model-v1`.

## Global Constraints

- Requirement Anchored.
- System-Constraint Aware.
- Decision Centered.
- Preconditions First.
- Counterexample + Evidence Driven.
- Precondition is `Claim.kind=precondition`; no duplicate entity.
- Current-code absence cannot refute a `planned` mechanism.
- Historical knowledge is a challenge seed, not current-defect proof.
- No semantic quality claims without fresh-context execution evidence.

## Revised task sequence

### Task 0 — Repository convention inspection

- Inspect existing `prd-challenge-model` package, scripts, agent metadata and canonical JSON pattern.
- Preserve compatible repository conventions without copying PRD-specific semantics.

### Task 1 — RED deterministic baseline

- Write validator/adjudicator tests before scripts.
- Verify imports/behavior fail for missing implementation.

### Task 2 — Minimal Skill contract

- Add trigger-only frontmatter.
- Keep SKILL.md around 350–500 words.
- Route model/method/evidence/Android/evaluation references.

### Task 3 — Canonical semantic model

- Implement RequirementObligation, SystemConstraint, DesignDecision, Mechanism and Claim.
- Model Precondition only as a Claim kind.
- Gate inferred SystemConstraint.

### Task 4 — Coverage Finding path

- Implement `COVERED/PARTIAL/MISSING/CONTRADICTED/UNCLEAR`.
- Allow Coverage Finding without artificial Counterexample.

### Task 5 — Design-stage-aware challenge depth

- Freeze `architecture/high_level/detailed` semantics.
- Add semantic dataset cases proving stage-specific depth.

### Task 6 — Counterexample Finding path

- Add typed lens routing and mutation library.
- Require claim + counterexample for implementation-dependent Findings.

### Task 7 — Evidence adequacy and lifecycle matrix

- Match evidence to Claim type.
- Implement existing/planned/modified/removed evidence rules.
- Treat search absence conservatively.

### Task 8 — Finding/Gap/OpenDecision and Gate semantics

- Keep Finding/RequirementGap/EvidenceGap/OpenDecision separate.
- Define severity, deterministic Verdict and independent Assurance.
- Critical EvidenceGap may block Gate without becoming a Technical Finding.

### Task 9 — JSON Schema + semantic validator

- Draft 2020-12 closed-root schema.
- Cross-reference integrity validation.
- Two Finding-path invariants.
- EvidenceGap claim references and inferred-constraint Blocker gate.

### Task 10 — Deterministic scorer and expert adjudication interface

- Score known required/forbidden Findings, Verdict and Gap counts.
- Route unexpected Findings to expert adjudication.
- Do not expose real Precision until adjudication is complete.

### Task 11 — Brownfield and Android profile

- Claim-driven Brownfield retrieval.
- Feature Tree/history as Challenge Seeds.
- Android mechanism-specific profile, not a fixed checklist.

### Task 12 — Dev/Holdout dataset + isolation

- Create 20 Dev + 10 Holdout cases.
- Cover design stage, lifecycle, lenses, output class and claim kinds.
- Implement `prepare_case.py` so answer keys and other cases cannot enter the review sandbox.

### Task 13 — Deterministic contract gate

- Add one command to run unittest, dataset validation and Skill-size checks.
- Any failure returns non-zero.

### Task 14 — Semantic RED/GREEN + Holdout acceptance

Requires a fresh-context/model runner not available in the current harness.

When available:

- Run Dev variants at least five fresh contexts while tuning.
- Freeze wording.
- Run unseen Holdout cases.
- Expert-adjudicate unexpected Findings.
- Calculate Recall, real Precision, clean-case FP and inter-run stability.
- If Holdout drives a wording change, invalidate that attempt and replace the exposed holdout case.

Until this task completes, status remains `PILOT`.

### Task 15 — Final independent review

- Review branch against this plan and Spec.
- Re-run contract gate.
- Compare branch with `main`.
- Do not merge/publish without explicit user action.

## Review Focus

1. No Product behavior invention.
2. No false defect from planned-mechanism code absence.
3. No direct Finding from historical Bug/RiskPattern.
4. No LLD requirements imposed on architecture/HLD.
5. No semantic quality claim based only on deterministic tests.

## Completion Evidence Required

Structural completion requires fresh output from:

```bash
python3 skills/technical-challenge-model/scripts/run_contract_tests.py
```

Semantic production acceptance additionally requires the fresh-context Holdout procedure in Task 14. Deterministic green alone is insufficient for production-quality claims.
