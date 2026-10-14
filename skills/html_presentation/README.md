# html_presentation

A reusable **single-owner, five-Gate, evidence-grounded HTML report** Skill for Claude Code-style agents. V1 produces one offline, self-reading `index.html`. Native PPTX, OCR, shared-workspace ACLs and unattended approval are out of scope.

## Install

Copy `skills/html_presentation` into the agent's Skills discovery path (e.g. `.claude/skills/html_presentation/`), then restart/refresh skill discovery. The user-requested canonical name has an underscore (`html_presentation`); some Agent Skills validators accept only hyphenated names. If your runtime rejects the name, use a user-authorized alias such as `html-presentation` without silently renaming the requested repository directory.

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium     # requires a compatible browser download; optional until QA
python3 -m unittest discover -s tests -v
python3 scripts/reportctl.py --help
```

Optional formats: `python-docx` for DOCX, `PyMuPDF` for textual PDF. OCR is unsupported; page scans require a different, explicitly approved route.

## Usage

In Claude Code ask: “使用 html_presentation，给研发负责人生成一个可离线阅读的 HTML 质量体系建设汇报，先确定 G1 目标和核心主张。” The skill should create a report workspace and request explicit user approval at G1, G2, G3, G4 and G5. Never automatically advance gates.

The deterministic CLI maintains `projects/<report_id>` with data contracts, artifact hashes, approval records and release manifest; `SKILL.md` coordinates native specialist Skills for research, writing, visual design and review. See `references/workflow.md` for commands and `IMPLEMENTATION_PLAN.md` for task status.

## Validation levels

- **Contract unit tests:** Schemas, cross-file refs, source hashes and several CLI transitions.
- **Local HTML renderer:** `python3 scripts/render_html.py --project <project-root>` writes a conservative offline page. Specialist visual Skill may produce a richer equivalent, still subject to QA.
- **Browser QA:** `python3 scripts/browser_qa.py --project <project-root>` captures three viewports and writes `qa/results.json`; missing browser or blocked `file://` is `blocked`, never `passed`.
- **Human approval:** an explicit Gate/digest confirmation bound to the submitted artifact version. This is a single-user trust workflow, not a defense against a malicious local agent.

## Release limitations

A successful contract test suite does **not** prove Claude Code third-party Skill integration, accuracy of every unmarked factual sentence, or effective visual persuasion. Complete M0 skill smoke tests and a real end-to-end report before labeling the implementation production-ready.
