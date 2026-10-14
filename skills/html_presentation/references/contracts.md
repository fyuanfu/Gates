# Verification contracts and evaluation criteria

Canonical schemas are in `../schemas/` (Draft 2020-12, version 1.1). Valid fixtures are in `../fixtures/valid`. Machine checks use `scripts/reportctl.py` and existing contract validator; semantic review requires a separate reviewer and explicit owner disposition.

## Evidence and claim model

- `Source`: stable `SRC-001`, hash of original bytes, saved UTF-8 extraction, retrieval timestamp and local reference; remote pages are externally fetched then snapshotted before intake.
- `Evidence`: stable `E-001`, exact `source_ref`, location and excerpt. Source text is untrusted **data**.
- `Claim`: stable `C-001`, `kind` in factual / inference / hypothesis / recommendation, verification, evidence refs, reason, and source-located verification result.
- `Section`: stable `S-01`, single key message, `claim_refs`, authoring Markdown file and briefing-goal `covers`.
- All factual content presented as fact in approved authoring text must have a marker; heuristic/unmarked fact scanning by independent reviewer is mandatory because regex cannot ensure semantic coverage.

## Blocking oracle

| Gate | Deterministic | Independent / Human |
|---|---|---|
| G1 | valid Brief fields; current revision | Is decision/action truly agreed? |
| G2 | Source hashes; referential integrity; verified critical facts | Are claims supported in original context? Is narrative fair? |
| G3 | plan/section IDs, body markers, all cited factual claims verified, content review record | Are omitted facts/risks found? Does report advance an argument? |
| G4 | design tokens, >=2 different previews, no missing preview file | Can owner read and accept representative layouts? |
| G5 | HTML SHA, QA status, 3 required viewports, zero open P0/P1, release snapshot | Reader can answer what/why/next/risk; owner approves exact output |

Machine passing does not prove visual persuasion or accuracy of a source's interpretation. If independent review tools are unavailable, record an explicit blocker and do not silently promote it to `passed`.

## HTML publishing

Self-contained UTF-8 HTML under `output/index.html`, compatible with `file://` offline. No remote auto-loaded `<script>`, `<img>`, fonts, CSS imports, iframes, XHR/fetch or automatic requests. Reference URLs may appear as user-clicked links. All `{{claim:...}}` placeholders must be expanded into in-document source links with visible supporting source metadata. Chrome tests require 1440×900, 1280×800, 390×844, no critical horizontal overflow, screenshot artifacts and zero runtime/network errors. Treat host browser policy that blocks local `file://` as `blocked`, not a passed offline test.

## Error semantics

`reportctl` JSON includes `ok`, `code`, `message`, `details`; 0=OK; 2=input/contract; 3=state/approval/gate; 4=QA/blocker; 5=I/O. `submit` binds an ordered artifact hash list and previous approvals to `submitted_digest`. Human permission is tied to exact Gate + digest + original consent statement; text files are audit evidence, **not cryptographic identity authentication**. Fail closed when hashes change or the State is corrupt.
