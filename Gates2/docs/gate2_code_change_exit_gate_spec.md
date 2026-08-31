# Gate2 Code Change Exit Gate Specification

> 文件：`Gate2/docs/gate2_code_change_exit_gate_spec.md`  
> 状态：Spec Draft / 已完成目标层决策，待 Decision Record 固化  
> 日期：2026-08-29  
> Source Issue: `#2 [Spec] Gate2 Code Change Exit Gate`

---

## Problem Statement

Gate2 需要在一次确定的代码 Change / PR 合入共享基线前，回答一个明确的生命周期决策问题：**该变更是否已经被充分证明可以安全向后流转**。

当前风险不是缺少 Build、Test、Review、Lint 等检查工具，而是这些活动容易被直接等同为 Gate2 本身，导致门禁退化为检查项集合；同时如果没有明确阻断目标，Gate2 会与 Gate3 Feature Acceptance、CI、Code Review 重叠，并且容易不断扩张为通用 Code Quality Gate。

Gate2 必须稳定区分：

- **门禁目标**：要阻止什么风险流入下一阶段；
- **Verification Activity**：用什么方式产生证据；
- **Evidence**：实际观察或分析得到的可审计结果；
- **Policy**：什么风险与证据状态必须阻断；
- **Verdict**：是否允许 Change 合入共享基线。

Gate2 V1 还必须遵循现有 Decision Record：`Verification Obligation` 只作为解释性概念，不建模为拥有独立 ID / Schema / 生命周期的一等对象；Test / Verification Activity 直接关联 Requirement Object。

## Solution

建设一个 **Code Change Exit Gate**。Gate2 以一次确定的 Change / PR 为评估对象，围绕两个核心阻断目标形成证据驱动的准出判断：

1. **Change Correctness**：阻止本次 Change Scope 承担的 Requirement / Design Commitment 未被正确实现，或关键正确性无法被充分证明的变更。
2. **Change Impact Safety**：阻止由本次 Change 引起的可识别影响中存在未关闭的不可接受风险，或高风险影响尚无法被充分证明安全的变更。

Gate2 不把 Engineering Quality、Build、Test、Review、Static Analysis 作为与上述目标并列的门禁目标。这些属于 Verification / Guardrail / Mandatory Policy，其输出作为 Gate2 Evidence 或阻断依据。

Gate2 的主判定链：

```text
Change
  ↓
Declared Scope + Actual Semantic Scope Check
  ↓
Requirement / Design Commitment + Impact Analysis
  ↓
Verification Activity
  ↓
Evidence
  ↓
Evidence Fitness / Risk Evaluation
  ↓
Closure State
  ↓
Versioned Gate Policy
  ↓
PASS / PASS WITH RISK / BLOCK
```

其中 Change Safety 是 **bounded assurance**：Gate2 不宣称发现所有未知影响，而是在规定、可解释的影响分析方法所识别的合理范围内，要求不可接受风险得到关闭。

## User Stories

1. As a developer, I want Gate2 to tell me whether my Change is safe to merge, so that I know whether it can enter the next lifecycle stage.
2. As a developer, I want Gate2 to distinguish an incorrect intended change from an unsafe side effect, so that remediation is targeted.
3. As a developer, I want a missing high-risk verification evidence path to block the Change even when CI is green, so that lack of proof cannot masquerade as correctness.
4. As a developer, I want low-risk evidence gaps to be reported without necessarily blocking, so that Gate2 remains usable rather than becoming an all-or-nothing checklist.
5. As a reviewer, I want each blocking decision to trace back to Requirement, Change, Finding/Risk, Evidence, and Policy, so that the verdict is auditable.
6. As a reviewer, I want Gate2 to validate the declared Change Scope against the actual semantic impact of the Diff, so that a Change cannot escape review by declaring an artificially small scope.
7. As a reviewer, I want Design Commitments to remain subordinate to upstream Requirement / AC semantics, so that a correctly implemented but incorrect design cannot receive a false PASS.
8. As a reviewer, I want Review findings to contribute evidence and risk without making Code Review itself the gate, so that review and gate responsibilities remain separate.
9. As a test/verification owner, I want tests and other verification activities to directly reference stable Requirement IDs, so that V1 keeps the traceability model minimal.
10. As a test/verification owner, I want Gate2 to assess whether evidence is fit for the claim it supports, so that a passing but irrelevant test does not close a requirement.
11. As a quality owner, I want Gate2 to evaluate impact safety using an explicit impact-analysis method, so that regression selection is explainable rather than intuition-driven.
12. As a quality owner, I want high or critical unclosed impact risk to block merge, so that uncertain high-risk changes cannot silently flow downstream.
13. As a policy owner, I want mandatory blocking policies to be predeclared, scoped, objective, and versioned, so that reviewers cannot invent blocking rules ad hoc.
14. As a policy owner, I want non-mandatory code-quality findings to map through correctness/safety risk before blocking, so that Gate2 does not become a generic lint gate.
15. As a risk owner, I want residual risk acceptance to be explicit, attributable, and bounded, so that exceptions are auditable rather than informal waivers.
16. As a release/feature validation owner, I want Gate2 to operate at Change level rather than re-run full Feature acceptance, so that Gate2 and Gate3 remain distinct.
17. As a CI owner, I want CI to execute build/test/static checks while Gate2 consumes their results as evidence, so that execution and decision responsibilities remain separated.
18. As an AI coding agent, I want a deterministic Gate2 verdict contract, so that I know when to stop, remediate, or escalate instead of continuing implementation through unresolved high-risk gaps.

## Implementation Decisions

### 1. Gate2 lifecycle position and evaluated object

- Gate2 runs on a **specific Code Change / PR before merge to the shared baseline**.
- Gate2 is a Change-level exit decision, not Feature-level acceptance.
- Gate3 remains responsible for complete Feature / Candidate business acceptance.

### 2. Two core gate objectives

#### G2-T1 Change Correctness

Gate2 SHALL determine whether the behavior and constraints actually undertaken by the Change are correctly implemented and adequately supported by valid evidence.

A Change is correctness-blocking when any required high/critical commitment is:

- not implemented;
- implemented inconsistently with upstream Requirement semantics;
- in conflict with required Rule / State / Contract / Invariant;
- contradicted by valid evidence;
- or lacks sufficient valid evidence to justify release from Gate2.

Design Commitments may refine implementation expectations but SHALL NOT override or redefine Requirement / AC semantics.

### 3. G2-T2 Change Impact Safety

Gate2 SHALL determine whether reasonably identifiable semantic impacts of the Change contain unclosed unacceptable risk.

Impact analysis SHALL start from the actual Change and may expand through relevant code, call, data, state, contract, configuration, resource, or timing relationships until the defined analysis boundary is reached.

Gate2 SHALL NOT claim proof of zero regression. The assurance claim is bounded to the impacts discoverable by the configured analysis method and available project knowledge.

A Change is safety-blocking when:

- a Critical/High regression is confirmed;
- a Critical/High affected behavior lacks adequate verification;
- a Critical dependency/contract/schema/state impact remains materially uncertain;
- or a High/Critical residual risk remains unaccepted according to policy.

### 4. Change Scope must be checked, not trusted

Gate2 SHALL compare declared Change intent/scope with actual semantic impact. Scope mismatch is a Finding and may escalate into correctness or safety risk.

The developer or AI agent cannot reduce Gate2 coverage merely by declaring fewer Requirement IDs or a smaller intended scope.

### 5. Verification Obligation is explanatory, not a V1 entity

V1 SHALL preserve the accepted repository decision that Verification Obligation is not a first-class traceability object.

The V1 traceability path is:

```text
Requirement Object
  ↓ verified-by / covered-by
Test / Verification Activity
  ↓ produces
Execution / Evidence
  ↓ supports
Finding / Risk / Verdict
```

AC, Scenario, Rule, Transition, Invariant, NFR, or Contract provide the semantics of what must be demonstrated.

### 6. Evidence fitness instead of full test-quality auditing

Gate2 SHALL evaluate whether evidence is **fit to support the specific Requirement/Risk claim**. It SHALL NOT attempt to perform a complete audit of every test asset.

At minimum, evidence used to close a blocking claim must establish:

- provenance / execution identity;
- relevance to the Requirement or affected behavior;
- a valid observable Oracle or policy assertion;
- an interpretable result;
- no unresolved contradictory evidence.

A passing test alone does not imply closure if it does not exercise or observe the relevant claim.

### 7. Verification method is claim-dependent

- Runtime behavior SHOULD be supported by dynamic executable evidence at an appropriate seam.
- Static constraints MAY be closed by static analysis, architecture checks, inspection, or other objective verification activities.
- Review is a verification method that produces Findings/Evidence; it is not itself the gate.
- CI is an execution platform that produces evidence; it is not itself the gate.

### 8. Risk severity

V1 SHALL use `Critical / High / Medium / Low` severity.

Severity SHALL reflect at least:

- impact magnitude;
- exposure / likelihood of manifestation;
- recoverability / detectability.

Evidence-gap severity SHALL inherit primarily from the Requirement/Risk it is supposed to support rather than from the test type that is missing.

### 9. Mandatory Policy is a narrow third blocking path, not a third quality objective

A Mandatory Policy violation MAY block independently of the two core risk objectives, but only when the policy is predeclared and admitted as a hard organizational constraint.

A Blocking Mandatory Policy must be:

- defined before evaluation;
- objectively testable or reviewable;
- scoped to applicable repository/module/change classes;
- owned;
- versioned;
- equipped with an explicit exception mechanism where exceptions are permitted;
- justified by lifecycle, risk, compliance, security, compatibility, or build integrity needs.

Reviewers SHALL NOT create new Mandatory Policies during an individual review.

### 10. Risk acceptance and verdict

Gate2 V1 SHALL support three final verdicts:

- `PASS`: no blocking failure; all required blocking claims are sufficiently closed; no unaccepted unacceptable residual risk exists.
- `PASS WITH RISK`: no blocking failure remains, but explicitly accepted residual risk exists and is recorded with owner/reason/scope/follow-up metadata.
- `BLOCK`: correctness cannot be adequately demonstrated, unacceptable impact risk remains open, or an applicable Mandatory Policy is violated.

Default acceptance policy:

- Critical: not acceptable within normal Gate2 flow;
- High: BLOCK by default; exceptional acceptance requires explicit higher authorization;
- Medium: may be accepted by policy;
- Low: normally non-blocking / informational unless policy states otherwise.

### 11. Primary implementation/test seam

The preferred V1 seam is a single Gate2 evaluation boundary:

```text
Normalized Change Assessment Input
        ↓
Gate2 Decision Engine
        ↓
Verdict + Reasons + Traceability
```

Internal analyzers may evolve independently, but the externally observable contract SHALL remain the main integration-test seam. Avoid creating many low-level testing seams unless a concrete implementation constraint requires them.

### 12. Minimal normalized inputs

The Gate2 evaluator should be able to consume normalized representations of:

- Change identity and Diff-derived change facts;
- declared intent / Requirement references;
- applicable Design Commitments and upstream traceability;
- impact-analysis results and confidence/boundary metadata;
- Verification Activity and Evidence results;
- Findings and risk assessments;
- applicable versioned Mandatory Policies;
- explicit risk-acceptance records.

The spec does not require all upstream producers to use one physical file format in V1; normalization may occur at the Gate2 boundary.

### 13. Decision output

A Gate2 decision SHALL expose at minimum:

- final verdict;
- correctness status and blocking reasons;
- impact-safety status and blocking reasons;
- mandatory-policy violations;
- evidence gaps that materially affected the decision;
- accepted residual risks;
- policy/version identity;
- trace links sufficient to explain why each blocking or accepted-risk decision occurred.

## Testing Decisions

### Testing principle

Tests SHALL assert externally observable Gate2 decision behavior rather than internal implementation structure. The highest available seam is preferred: normalized input in, verdict/reasons out.

### Primary decision-engine scenarios

The implementation SHALL have durable tests covering at least:

1. Correct intended change + sufficient evidence + no unsafe impact -> `PASS`.
2. Required high-risk behavior not implemented -> `BLOCK`.
3. Requirement/design semantic conflict -> `BLOCK` even when implementation matches the design.
4. High-risk Requirement with missing evidence -> `BLOCK`.
5. Passing but irrelevant evidence -> claim remains open -> `BLOCK` when blocking severity applies.
6. Confirmed high/critical regression -> `BLOCK`.
7. High-risk impact uncertainty without accepted risk -> `BLOCK`.
8. Medium residual risk with valid acceptance record -> `PASS WITH RISK`.
9. Low-risk evidence gap under permissive policy -> non-blocking outcome with explanatory finding.
10. Mandatory Policy violation -> `BLOCK` independent of passing functional tests.
11. Non-mandatory style/maintainability finding without correctness/safety impact -> does not independently block.
12. Declared scope narrower than actual semantic impact -> produces scope-mismatch finding and corresponding risk evaluation.
13. Reviewer-created ad hoc policy not present in the policy set -> cannot independently block as Mandatory Policy.
14. Contradictory evidence -> claim cannot be considered closed until conflict is resolved.
15. Impact analysis explicitly bounded with no unacceptable identified risk -> may pass without claiming global no-regression proof.

### Prior art

The repository currently contains documentation, decision records, examples, and Skills rather than an existing Gate2 executable decision engine. Therefore there is no executable in-repo Gate2 test seam to reuse yet. V1 should establish the normalized decision boundary as the reusable prior-art seam for subsequent Gate2 analyzers and integrations.

## Out of Scope

- Full Feature / Story acceptance across all AC and end-to-end journeys; owned by Gate3.
- Proving that no unknown regression exists anywhere in the product.
- Comprehensive test-code quality auditing.
- Replacing Code Review.
- Replacing CI execution infrastructure.
- Generating or maintaining a first-class Verification Obligation entity in V1.
- Requiring every Finding to block.
- Treating every code-quality or maintainability issue as a Gate2 objective.
- Defining the full CIRT impact-analysis algorithm in this spec; Gate2 only defines the contract and safety expectations it must satisfy.
- Defining Gate3 or Gate4 policy.
- Automatically accepting Critical residual risk.

## Further Notes

### Relationship to existing repository decisions

This spec preserves the accepted decision that Verification Obligation is explanatory only in V1 and that tests/verification activities directly trace to Requirement Objects.

It also preserves the implementation-planning principle that Story is the primary Task ownership container and Requirement Coverage Review is responsible for detecting known implementation gaps before coding; Gate2 should treat such escaped gaps as findings rather than redefining Task ownership.

### Required Decision Record before implementation

The repository governance states that semantic changes to Gate boundaries, core object model, traceability, Gate Policy, or key terminology require a Decision Record. Before implementation, the following Gate2 decisions should therefore be captured in a dedicated DR:

- Gate2 has exactly two core assurance objectives: Change Correctness and Change Impact Safety;
- Mandatory Policy is a narrow hard-constraint blocking path, not a third quality objective;
- Change Safety is bounded assurance rather than a zero-regression guarantee;
- final Gate2 verdict vocabulary is `PASS / PASS WITH RISK / BLOCK`.

The verdict vocabulary must explicitly reconcile the existing overview's broader `PASS / WARN / BLOCK` wording so there is one canonical Gate2 policy semantics.

### Completion criterion

This spec is ready for implementation decomposition when:

- the required Gate2 Decision Record is accepted;
- the normalized Gate2 decision input/output contract can be specified without introducing new requirement semantics;
- blocking policies can be represented as versioned data/configuration;
- the primary decision-engine scenarios above can be expressed as deterministic tests.
