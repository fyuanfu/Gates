# Stage playbook and artifacts

This file is loaded by `SKILL.md` only when running a report. A separate process may load it after context compaction.

## S1 → G1: Reporting Brief

Discuss the audience, management decision, expected understanding, desired action, scope and reading mode. Create `brief.yaml` using `schemas/brief.schema.json`. Five fields must be substantive: `audience`, `desired_outcome`, `desired_action`, `core_thesis`, `title`. Explicitly distinguish objectives (desired) from evidence (known). No layout design.

## S2 → G2: Research, Claims and Narrative

Prepare `research-plan.md`: prioritized research questions, evidence gaps and stop rule. Capture each source using `reportctl intake` (local md/txt/docx/text PDF) or via authorized web Tool + local text snapshot. No implicit network call is performed by the CLI. Sources appear in `inputs/manifest.yaml`, raw bytes in `inputs/raw`, extracted text in `inputs/snapshots`.

Build `evidence.yaml` with `sources`, `evidence` and `claims`. For every factual Claim, record `evidence_refs` and `verification_result`; critical facts must be verified at G2. Document unsupported or partial evidence and never fill with invented facts. Create `narrative.md`: audience questions, narrative spine, causal links, objections, decision required, and section candidates. An independent fact-check performs source-to-claim entailment review. The machine validator verifies IDs, hashes and record shape, not semantic entailment.

## S3 → G3: Content baseline

Create `report-plan.yaml` with unique `S-01` sections, `key_message`, `role`, `covers`, `visual_intent`, and `content_path`; write each `content/S-*.md`. Each factual sentence or group needs an adjacent `{{claim:C-...}}` marker; report-plan `claim_refs` must exactly match actual body markers. Mark all key management actions and limitations via covers. Before G3, complete an independent **unmarked-factual-claim scan** and `reviews/content-review.yaml` (each mandatory dimension pass, open_blockers empty). The owner decides contested inference; unverified facts must be removed or clearly marked as hypotheses.

## S4 → G4: Design freeze

Create `design-spec.yaml` (approved background/text/accent hex, typography and spacing, `inline_only` policy). Author at least two contrasting previews as standalone HTML under `previews/` (e.g. narrative opening and dense evidence/comparison). At least one demonstrates a complex graphic or structured table. Record visual inspection observations and owner acceptance in `reviews/visual-review.md`. Use final design tokens in every generated page, not a different theme.

## S5 → G5: Full production and QA

Use `frontend-design` or a disclosed equivalent to write `output/index.html`. The built-in `render_html.py` offers an offline, conservative baseline from approved content. Do not fetch fonts or data. Write `reviews/reader-review.yaml`: independent reading from the audience's vantage (problem / proof / action / risk); must have dimension checks and no open P0/P1. Run `browser_qa.py`, inspect screenshots at all three viewports, record visual/semantic issues with severity and resolution; unresolved P0/P1 blocks approval. Run `reportctl validate --gate G5`, submit/owner approve, then `reportctl release`.

## CLI usage

```bash
python3 scripts/reportctl.py init ai-quality --root projects
python3 scripts/reportctl.py validate ai-quality --gate G1 --root projects
python3 scripts/reportctl.py submit ai-quality --gate G1 --root projects
# Show digest and await explicit real owner approval.
python3 scripts/reportctl.py approve ai-quality --gate G1 --digest <returned-hash> --confirmation-file projects/ai-quality/owner-G1.txt --root projects
python3 scripts/reportctl.py start-stage ai-quality --stage S2 --root projects
python3 scripts/reportctl.py intake ai-quality --file /path/source.md --classification public --root projects
python3 scripts/reportctl.py sync ai-quality --root projects
python3 scripts/reportctl.py status ai-quality --root projects
python3 scripts/reportctl.py resume ai-quality --root projects
python3 scripts/reportctl.py release ai-quality --root projects
```

`reject` requires `--feedback-file` and `--confirmation-file`, both explicitly authored by the owner. For approved stages, any change to a registered upstream byte snapshot should stale the affected gate and downstream gates. Use `revise --stage Sn` after correcting rejection; use `resume` to recover a stale/failed stage only when previous gate is approved. `status` is read-only; treat malformed state as an error, not permission to reconstruct approval.
