# Gate2 V1 Specification

> 文件：`Gates2/v1/docs/gate2_spec_v1.md`  
> 状态：V1 Baseline  
> 日期：2026-08-31  
> 规范来源：`Gates2/docs/gate2_code_change_exit_gate_spec.md`  
> 检查维度来源：`Gates2/docs/Gate2_矩阵检查目标.html`  
> 决策说明：本文不修改或覆盖任何既有文档；本文是基于现有 Gate2 Code Change Exit Gate 语义与矩阵检查能力形成的 V1 统一规范。

---

## 1. Purpose

Gate2 V1 是一个 **Code Change Exit Gate**。

它在一次确定的 Code Change / PR 合入共享基线前运行，回答：

> 当前 Change 是否已经在规定的检查目标上达到可准出的工程状态，并有足够可信的证据支撑该结论？

Gate2 V1 不承担完整 Feature Acceptance，也不替代 Gate3、Code Review、CI 或 UAT。

本文采用以下双重约束：

1. **行为、边界、阻断规则与风险语义**以 `gate2_code_change_exit_gate_spec.md` 为规范来源；
2. **检查目标与检查矩阵结构**以 `Gate2_矩阵检查目标.html` 为能力模型来源，并在 V1 中正式提升为 Gate2 顶层目标。

---

## 2. Lifecycle Position

Gate2 V1 运行位置：

```text
Approved Requirement / Design Context
            ↓
        Code Change / PR
            ↓
          Gate2 V1
            ↓
      Shared Baseline / Merge
            ↓
     Later Feature Acceptance
```

Gate2 V1 的评估对象是：

```text
A specific Code Change / PR
```

不是：

```text
The whole Feature
The whole Product
The whole Release
```

因此，所有检查都必须受 **Change Scope** 约束。

---

## 3. Gate2 V1 Top-Level Goals

Gate2 V1 正式定义五个顶层目标：

```text
G2-G1 Consistency
G2-G2 Completeness & Coverage
G2-G3 Verification Result
G2-G4 Change Safety
G2-G5 Evidence Validity
```

五个目标是 Gate2 V1 的正式检查与判定维度。

### 3.1 G2-G1 Consistency — 一致性

目标：

> 本次 Change 相关的 Requirement、Design Commitment、Implementation、Verification、Evidence 是否保持同一语义，没有发生冲突、漂移或错误重定义。

重点检查：

```text
Requirement / AC
      ↕
Design Commitment
      ↕
Implementation / Diff
      ↕
Verification Activity / Test
      ↕
Evidence
```

核心规则：

- Requirement / AC 是上游语义约束；
- Design Commitment 可以细化实现约束，但不得覆盖或重定义 Requirement / AC；
- Implementation 即使完全符合 Design，若 Design 与 Requirement 冲突，也不能获得一致性 PASS；
- Verification Oracle 必须验证真正的 Requirement 语义；
- Evidence 必须绑定当前 Change / Revision / Candidate Context。

典型问题：

- `IMPLEMENTATION_MISMATCH`
- `PLAN_DEVIATION`
- `DESIGN_DECISION_VIOLATION`
- `OUT_OF_SCOPE_CHANGE`
- `IRRELEVANT_TEST`
- `STALE_EVIDENCE`
- `CONTRADICTORY_EVIDENCE`

---

### 3.2 G2-G2 Completeness & Coverage — 完整性与覆盖

目标：

> 本次 Change 实际承担的 Requirement / Design Commitment 是否完整实现，并且所有需要达到阻断级证明标准的内容是否具有必要验证覆盖。

V1 的完整性边界明确为：

```text
Completeness Scope
=
Requirements / Design Commitments actually undertaken by this Change
+
Requirements / Risks discovered to be materially affected by actual semantic scope
```

Gate2 V1 不要求证明整个 Feature 的全部 Requirement 已完成。

Gate2 SHALL 比较：

```text
Declared Change Scope
        vs
Actual Semantic Scope / Impact
```

开发者或 Agent 不能通过缩小声明范围降低 Gate2 覆盖。

重点检查：

- Required Requirement 是否存在未实现；
- 是否只有 Stub、Fake、脚手架、接线而没有真实行为；
- Required Rule / State / Contract / Invariant 是否漏实现；
- Change 实际影响到的高风险行为是否被纳入验证范围；
- 是否存在关键 Verification Gap；
- Scope mismatch 是否导致漏检。

典型问题：

- `MISSING_IMPLEMENTATION`
- `PARTIAL_IMPLEMENTATION`
- `MISSING_TEST_COVERAGE`
- `MISSING_VERIFICATION`
- `REGRESSION_GAP`
- `SCOPE_MISMATCH`

---

### 3.3 G2-G3 Verification Result — 验证结果

目标：

> 对本次 Change 所需的 Verification Activity，其实际执行结果是否足以支持准出判断。

Verification Activity 可以包括：

- automated test；
- integration / contract test；
- static analysis；
- architecture check；
- build / compile；
- security scan；
- inspection / review；
- smoke / runtime check；
- 其他可客观验证的工程活动。

Gate2 V1 不把 Test 等同于 Gate，也不把 CI Green 等同于 PASS。

基本链路：

```text
Requirement / Risk Claim
        ↓
Verification Activity
        ↓
Execution
        ↓
Observed Result
        ↓
Interpretation
```

Verification Result 至少要区分：

```text
PASS
FAIL
UNKNOWN
SKIPPED
FLAKY / UNSTABLE
NOT_EXECUTED
```

其中：

- `FAIL` 不得被当作成功证据；
- `UNKNOWN` 不得被当作 PASS；
- `SKIPPED` 对阻断级 Requirement/Risk 等价于缺失有效证明；
- `FLAKY` 必须按风险和 Policy 判断是否足以关闭 Claim。

---

### 3.4 G2-G4 Change Safety — 变更安全性

目标：

> 本次 Change 产生的合理可识别影响中，是否不存在未关闭的不可接受风险。

Gate2 V1 对 Change Safety 采用 bounded assurance：

```text
Gate2 does not prove zero regression.
Gate2 proves that reasonably identifiable material impacts
within the configured analysis boundary are sufficiently closed.
```

基本链路：

```text
Diff
 ↓
Changed Symbol / Contract / Data / State / Config / Resource / Timing
 ↓
Dependency / Call / Data / State Relationships
 ↓
Affected Behavior
 ↓
Affected Scenario / Existing Capability
 ↓
Risk
 ↓
Verification / Regression Evidence
```

重点检查：

- 已确认 Critical / High regression；
- API / Contract / Schema / State semantics 变化；
- Shared component / common path 影响；
- 数据迁移风险；
- concurrency / timing / retry / lifecycle 风险；
- security / privacy / compatibility 风险；
- 高风险 affected behavior 是否缺少验证；
- 高风险影响是否仍 materially uncertain。

Change Safety 在以下情况默认 BLOCK：

- confirmed Critical / High regression；
- Critical / High affected behavior 未充分验证；
- Critical dependency / contract / schema / state impact materially uncertain；
- High / Critical residual risk 未按 Policy 获得有效接受。

---

### 3.5 G2-G5 Evidence Validity — 证据有效性

目标：

> 用于支持 Gate2 结论的 Evidence 是否与 Claim 相关、可信、可追溯、可解释，并属于当前 Change/Revision。

核心原则：

```text
Claim ≠ Evidence
Test PASS ≠ Claim Closed
CI Green ≠ Gate PASS
```

Evidence 至少应检查：

| 属性 | 检查问题 |
|---|---|
| Provenance | Evidence 从哪里产生、由什么 Activity 产生？ |
| Relevance | Evidence 是否真正支持目标 Requirement / Risk？ |
| Oracle | 是否存在能区分正确/错误的有效断言或规则？ |
| Freshness | 是否来自当前 Revision / Candidate？ |
| Identity | Commit / Build / Config / Environment 是否明确？ |
| Observability | 是否观察到了真正目标行为？ |
| Integrity | Evidence 是否完整、可信、可访问？ |
| Conflict | 是否存在未关闭的冲突 Evidence？ |
| Interpretability | Result 是否可解释并能支持 closure？ |

Evidence Gap 不作为独立的第三类质量目标，而作为正式 Gate Goal `Evidence Validity` 的失败状态；其阻断严重度主要继承所支持 Requirement / Risk 的严重度。

默认策略：

| Evidence Gap 对应风险 | 默认处理 |
|---|---|
| Critical | BLOCK |
| High | BLOCK |
| Medium | Policy 决定，可 Risk Accept |
| Low | 通常非阻断 |

---

## 4. Relationship to Existing Assurance Concepts

现有 Spec 中的两个 assurance concepts 在 V1 中继续保留，但不再作为顶层 Gate Goal。

### 4.1 Change Correctness

`Change Correctness` 在 V1 中作为综合 Assurance Capability：

```text
Change Correctness
=
Consistency
+ Completeness & Coverage
+ Verification Result
+ Evidence Validity
```

它用于表达：

> 本次 Change 实际承担的需求与设计承诺是否被正确、完整地实现，并获得足够可信的证明。

### 4.2 Change Impact Safety

`Change Impact Safety` 映射到新的顶层 Goal：

```text
Change Impact Safety
→ G2-G4 Change Safety
```

现有 Spec 中关于 impact analysis、bounded assurance、high-risk unknown、residual risk 的规则继续适用。

---

## 5. Gate2 V1 Check Objects

Gate2 V1 采用矩阵式能力模型。检查对象与检查目标正交。

V1 主要检查对象：

```text
A. Change Intent / Applicable Requirement / AC
B. Design Commitment / Technical Plan
C. Actual Code Change / Diff
D. Verification Need / Test Assets / Verification Activities
E. Execution Results / Evidence
F. Candidate Build / Runtime Context
G. Finding / Risk / Risk Acceptance
```

说明：

- 原矩阵中的 Feature Intent 在 V1 中作为能力输入保留，但执行时只取与当前 Change 相关的 Applicable Requirement；
- Candidate Build / Runtime 是检查对象和证据来源，不构成独立 Gate Goal；
- “Candidate 是否可供 UAT”不属于 V1 判定语义；V1 只判断 Change 是否允许流入共享基线/下一生命周期阶段。

---

## 6. Verification Obligation Rule

Gate2 V1 遵守已接受的 DR-0001：

> `Verification Obligation` 不作为 V1 一等追溯对象。

因此不得引入：

```text
VO-01
VerificationObligation schema
独立 Verification Obligation 文件
独立生命周期
独立 owner
独立 persistence model
```

允许将“what must be proven”作为分析过程中的解释性概念，但正式追溯链必须保持：

```text
Requirement Object
    ↓ verified-by / covered-by
Test / Verification Activity
    ↓ produces
Execution / Evidence
    ↓ supports
Finding / Risk / Goal Status / Verdict
```

---

## 7. Formal Finding Taxonomy

Gate2 V1 正式采用六类根 Finding taxonomy：

```text
IMPLEMENTATION_GAP
VERIFICATION_GAP
REGRESSION_RISK
ENGINEERING_FAILURE
EVIDENCE_GAP
OPEN_RISK
```

### 7.1 IMPLEMENTATION_GAP

表示本次 Change 承担的 Required Requirement / Design Commitment 存在：

- 未实现；
- 部分实现；
- 实现错误；
- 语义偏差；
- 关键设计承诺未落实；
- 未声明的高风险行为变更。

典型 subtype：

```text
MISSING_IMPLEMENTATION
PARTIAL_IMPLEMENTATION
IMPLEMENTATION_MISMATCH
PLAN_DEVIATION
DESIGN_DECISION_VIOLATION
OUT_OF_SCOPE_CHANGE
```

### 7.2 VERIFICATION_GAP

表示应该被验证的 Requirement / Risk 缺乏合适 Verification Activity 或验证覆盖不足。

典型 subtype：

```text
MISSING_TEST_COVERAGE
MISSING_VERIFICATION
IRRELEVANT_TEST
WEAK_ORACLE
INSUFFICIENT_REGRESSION_COVERAGE
```

### 7.3 REGRESSION_RISK

表示 Change 对既有行为、Contract、Data、State、Dependency、Configuration 等产生潜在或已确认的不安全影响。

典型 subtype：

```text
CONFIRMED_REGRESSION
BREAKING_CHANGE
CONTRACT_RISK
SCHEMA_RISK
STATE_RISK
DEPENDENCY_RISK
SECURITY_RISK
REGRESSION_GAP
```

### 7.4 ENGINEERING_FAILURE

表示确定性工程活动发现失败，或适用 Mandatory Policy 被违反。

典型 subtype：

```text
BUILD_FAILED
COMPILE_FAILED
STATIC_ERROR
SECURITY_FINDING
ARCHITECTURE_VIOLATION
CONFIGURATION_ERROR
DEPLOY_FAILED
SMOKE_FAILED
```

说明：Engineering Failure 不天然等于第三个 Gate 目标；它必须通过 Goal Risk 或 Mandatory Policy 产生最终阻断语义。

### 7.5 EVIDENCE_GAP

表示 Evidence 无法有效支持目标 Claim。

典型 subtype：

```text
NOT_EXECUTED
STALE_EVIDENCE
REQUIRED_TEST_SKIPPED
INVALID_ENVIRONMENT
UNSTABLE_EVIDENCE
UNTRACEABLE_BUILD
IRRELEVANT_EVIDENCE
CONTRADICTORY_EVIDENCE
```

### 7.6 OPEN_RISK

表示已识别风险尚未关闭、无法排除，或存在显式 Residual Risk。

典型 subtype：

```text
UNRESOLVED_BLOCKING_RISK
MATERIAL_UNCERTAINTY
RESIDUAL_RISK
RISK_ACCEPTANCE_REQUIRED
```

---

## 8. Finding Data Model

Gate2 V1 Finding 至少应支持：

```yaml
finding:
  id:
  category: IMPLEMENTATION_GAP | VERIFICATION_GAP | REGRESSION_RISK | ENGINEERING_FAILURE | EVIDENCE_GAP | OPEN_RISK
  subtype:
  severity: Critical | High | Medium | Low
  goal:
    - G2-G1
    - G2-G2
    - G2-G3
    - G2-G4
    - G2-G5
  object_type:
  object_id:
  requirement_refs: []
  change_refs: []
  evidence_refs: []
  description:
  reasoning:
  confidence:
  status:
  blocking:
  policy_refs: []
  risk_acceptance_ref:
```

一个 Finding 可以影响多个 Gate Goal。

Finding category、Severity、Goal、Object 必须保持正交：

```text
WHERE  → Object
WHAT   → Finding Category / Subtype
GOAL   → Which Gate2 Goal is affected
HOW BAD→ Severity
POLICY → Whether it blocks
```

---

## 9. Severity Model

Gate2 V1 正式使用：

```text
Critical
High
Medium
Low
```

不使用 `P0 / P1 / P2 / P3` 作为 Gate2 V1 风险等级。

Severity 至少考虑：

1. Impact magnitude；
2. Exposure / Likelihood；
3. Recovery / Detectability。

Evidence Gap 的 Severity 主要继承它本应支持的 Requirement / Risk，而不是由缺失的 Test Type 决定。

---

## 10. Goal Status

五个顶层 Goal 都必须产生独立状态。

V1 推荐 Goal Status：

```text
PASS
PASS_WITH_RISK
BLOCK
```

含义：

### PASS

该 Goal 下：

- 没有 blocking finding；
- 所需高风险 Claim 已得到充分 closure；
- 没有未接受的 unacceptable residual risk。

### PASS_WITH_RISK

该 Goal 下：

- 没有未关闭 blocking failure；
- 存在显式 Residual Risk；
- 风险已按 Policy 完成有效接受；
- Risk Acceptance 有 owner / reason / scope / expiry or follow-up 等必要元数据。

### BLOCK

该 Goal 下存在：

- 不可接受的确定性失败；
- 阻断级 Requirement 未实现；
- 阻断级 Verification / Evidence Gap；
- Critical / High 未关闭风险；
- materially uncertain high-risk impact；
- 适用 Mandatory Policy violation。

---

## 11. Mandatory Policy

Mandatory Policy 是 Gate2 V1 的横切阻断路径：

```text
Mandatory Policy
≠ sixth Gate Goal
≠ Engineering Quality Goal
```

Blocking Mandatory Policy 必须：

- 事先定义；
- 对当前 repository / module / change class 适用；
- 客观可判断；
- 有明确 owner；
- versioned；
- 组织已明确规定其违反必须阻断；
- 若允许 exception，则有明确 exception mechanism。

Reviewer 不得在单次 Gate2 运行时临时创造 Mandatory Policy。

Reviewer 发现的新问题可以形成 Finding / Risk，并通过五个 Goal 和 Severity 进入 Policy Evaluation。

---

## 12. Risk Acceptance

Risk Acceptance 必须是显式、可审计对象。

至少包含：

```yaml
risk_acceptance:
  risk_id:
  severity:
  owner:
  approver:
  reason:
  scope:
  conditions:
  follow_up:
  expires_at:
  policy_version:
```

默认策略：

- Critical：正常 Gate2 Flow 不接受；
- High：默认 BLOCK；特殊接受需要更高授权；
- Medium：可由 Policy 允许接受；
- Low：通常 non-blocking / informational，除非 Policy 另有规定。

---

## 13. Overall Verdict

Gate2 V1 最终 Verdict 固定为：

```text
PASS
PASS WITH RISK
BLOCK
```

不得使用：

```text
FAILED
HUMAN_GATE
PASS_WITH_ACCEPTED_RISK
WARN
```

作为 V1 最终 Verdict 枚举。

### 13.1 PASS

```text
All Gate Goals = PASS
AND No Blocking Mandatory Policy Violation
AND No Unaccepted Unacceptable Residual Risk
```

### 13.2 PASS WITH RISK

```text
No Gate Goal = BLOCK
AND At least one Gate Goal = PASS_WITH_RISK
AND All blocking-level risks are either closed or validly accepted by policy
AND No unresolved Mandatory Policy violation
```

### 13.3 BLOCK

满足任一：

```text
Any Gate Goal = BLOCK
OR Applicable Blocking Mandatory Policy violated
OR Unaccepted unacceptable residual risk exists
```

---

## 14. Gate2 V1 Overall Check Matrix

| Layer | Check Object | G2-G1 Consistency | G2-G2 Completeness & Coverage | G2-G3 Verification Result | G2-G4 Change Safety | G2-G5 Evidence Validity |
|---|---|---|---|---|---|---|
| L1 | Change Intent / Requirement / AC | 实现是否符合上游语义 | Change 承担的 Required Requirement 是否完整实现 | 必要时是否可被客观验证 | 是否错误改变已有语义 | Requirement 是否可追溯到实现与验证 |
| L1 | Design Commitment / Plan | 是否与 Requirement 一致、实现是否忠于关键设计 | 承诺的关键实现项是否完成 | 关键设计约束是否有适当 Verification | 是否引入未声明高风险架构/API/State 变化 | Design 与 Diff / Evidence 是否可追溯 |
| L2 | Actual Diff / Change Facts | Diff 是否与声明 Intent 一致 | 是否存在漏实现或 Scope mismatch | Build / Static / Security / Contract 等结果 | 是否产生回归、兼容、依赖、数据、状态风险 | 重要 Change Fact 是否有可信来源 |
| L3 | Verification Activity / Test Assets | Test / Check 是否验证真正的 Requirement | 阻断级 Requirement / Risk 是否都有合适 Verification | Activity 是否可执行、是否实际运行 | 是否覆盖重要 affected behavior | Requirement → Activity 是否可追溯 |
| L4 | Execution Result / Evidence | Execution 是否对应当前 Change / Revision | 所需活动是否全部形成有效结果 | PASS / FAIL / SKIP / UNKNOWN / FLAKY | Regression / Impact Evidence 是否支持安全结论 | Freshness / Identity / Oracle / Integrity / Conflict 是否满足 |
| L5 | Candidate Build / Runtime Context | Build / Config 是否对应目标 Change | Change 所需 artifact / config 是否完整 | Build / Deploy / Smoke 等结果 | Config / Runtime / Interface 是否暴露高风险 | Commit / Build / Config / Env 是否唯一对应 |
| L6 | Finding / Risk / Risk Acceptance | Finding 是否对应真实语义冲突 | 阻断级缺口是否全部处理 | Fix 是否重新验证 | Residual Risk 是否在允许范围 | Closure Evidence 与 Acceptance 是否可审计 |

说明：

- Layer 是执行组织方式，不是额外 Gate Goal；
- Check Object 是被分析对象；
- 五个 G2-G* 是正式 Gate2 V1 顶层目标；
- 同一个对象可以被多个 Goal 检查；
- 同一个 Finding 可以影响多个 Goal。

---

## 15. Gate2 V1 Evaluation Flow

```text
1. Freeze Change Snapshot
        ↓
2. Load Applicable Requirement / Design Context
        ↓
3. Determine Declared Scope
        ↓
4. Analyze Actual Semantic Scope / Impact
        ↓
5. Run Five-Goal Matrix Evaluation
        ↓
6. Collect Verification Results
        ↓
7. Validate Evidence Fitness
        ↓
8. Generate / Normalize Findings
        ↓
9. Assign Severity and Goal Impact
        ↓
10. Apply Mandatory Policy
        ↓
11. Evaluate Residual Risk / Risk Acceptance
        ↓
12. Compute Goal Status
        ↓
13. Compute Overall Verdict
```

---

## 16. Evidence Fitness / Claim Closure

一个 Requirement / Risk Claim 被认为 closed，至少需要：

```text
Claim semantics are clear
+ Verification Method matches Claim
+ Verification Activity exists where required
+ Activity was executed / produced valid evidence
+ Evidence is relevant and current
+ Oracle / Assertion is valid
+ Result supports expected behavior
+ No unresolved contradictory evidence
+ Residual Risk is acceptable under policy
```

因此：

```text
BLOCK != only known defect
```

也可以是：

```text
BLOCK = insufficient basis to safely release the Change
```

---

## 17. Deterministic Tools and LLM Responsibilities

### Deterministic tools

优先用于产生事实证据：

- compiler / build；
- automated test；
- static analyzer；
- dependency / secret / security scanner；
- contract / schema checker；
- architecture rule checker；
- runtime / smoke / deployment checker；
- repository / diff / graph fact extraction。

### LLM

主要用于：

- Requirement ↔ Implementation 语义分析；
- Requirement ↔ Verification 相关性分析；
- Oracle strength 判断；
- cross-file semantic reasoning；
- impact discovery；
- risk hypothesis；
- evidence correlation；
- finding explanation / attribution。

LLM Finding 本身不天然等于 Hard Block。

高影响 Finding 必须尽可能通过 Repo Fact、Execution Evidence、Cross-source consistency 或 Policy 形成可审计支撑。

---

## 18. Primary Decision Scenarios

Gate2 V1 至少应覆盖以下 durable scenarios：

1. Change 正确、完整、验证充分、无不安全影响、Evidence 有效 → `PASS`。
2. Required high-risk behavior 未实现 → `IMPLEMENTATION_GAP` → `BLOCK`。
3. Requirement / Design semantic conflict，即使代码符合 Design → Consistency `BLOCK`。
4. Change 实际 Scope 大于声明 Scope，并产生高风险未覆盖行为 → Completeness / Change Safety `BLOCK`。
5. High-risk Requirement 缺 Verification Activity → `VERIFICATION_GAP` → `BLOCK`。
6. Test PASS 但 Oracle 与 Requirement 无关 → Evidence / Verification 不能 closure → `BLOCK`（若对应风险为 High/Critical）。
7. Test 未执行、Skip 或结果来自旧 Revision → `EVIDENCE_GAP`；按对应风险决定 BLOCK。
8. Confirmed Critical / High regression → Change Safety `BLOCK`。
9. Critical / High impact materially uncertain 且无有效风险接受 → Change Safety `BLOCK`。
10. Medium Residual Risk 有有效 Risk Acceptance → 对应 Goal `PASS_WITH_RISK`，Overall `PASS WITH RISK`。
11. Low-risk Evidence Gap 且 Policy 允许 → non-blocking finding，可 `PASS` 或 `PASS WITH RISK` 取决于是否形成显式 accepted residual risk。
12. Mandatory Policy violation → Overall `BLOCK`，无论功能测试是否通过。
13. 普通 style / naming finding 未映射到五个 Goal 的阻断风险，也不违反 Mandatory Policy → 不独立 BLOCK。
14. Contradictory Evidence 未解决 → Claim 不得 closure。
15. Impact Analysis 明确 bounded，边界内无不可接受风险 → 可通过 Change Safety，但不得声称全系统 zero regression。

---

## 19. Minimal Normalized Input

Gate2 V1 Decision Engine 应至少消费：

```yaml
change:
  id:
  base_revision:
  head_revision:
  declared_scope:
  diff_facts: []

requirements:
  applicable: []

design_commitments:
  applicable: []

impact_analysis:
  method:
  boundary:
  affected_behaviors: []
  uncertainties: []

verification_activities: []
execution_results: []
evidence: []
findings: []
mandatory_policies: []
risk_acceptances: []
```

V1 不要求所有上游数据使用单一物理格式；允许在 Gate2 boundary 进行 normalization。

---

## 20. Minimal Decision Output

Gate2 V1 输出至少包括：

```yaml
verdict: PASS | PASS_WITH_RISK | BLOCK

goals:
  consistency:
    status:
    findings: []
  completeness_coverage:
    status:
    findings: []
  verification_result:
    status:
    findings: []
  change_safety:
    status:
    findings: []
  evidence_validity:
    status:
    findings: []

blocking_reasons: []
mandatory_policy_violations: []
accepted_residual_risks: []
policy_version:
traceability:
```

说明：外部展示词汇固定为：

```text
PASS
PASS WITH RISK
BLOCK
```

若实现层使用 machine enum，推荐：

```text
PASS
PASS_WITH_RISK
BLOCK
```

---

## 21. Out of Scope

Gate2 V1 不负责：

- 完整 Feature / Story Acceptance；
- 全部 AC 的 Feature-level E2E 验收，除非它们实际属于当前 Change Scope；
- UAT；
- Release / Deployment Gate；
- 全系统 zero-regression proof；
- 完整 Test Quality Audit；
- 替代 Code Review；
- 替代 CI；
- 自动接受 Critical Residual Risk；
- 创建一等 Verification Obligation 对象；
- 将所有 Code Quality Finding 自动升级为 Blocking Finding。

---

## 22. V1 Normative Decisions

本文冻结以下 Gate2 V1 决策：

1. Gate2 V1 是 Change-level Code Change Exit Gate；
2. 五个检查维度正式提升为 Gate2 V1 顶层 Goal；
3. 五个 Goal 为：Consistency / Completeness & Coverage / Verification Result / Change Safety / Evidence Validity；
4. `Change Correctness` 降为综合 Assurance Capability，不再是顶层 Goal；
5. `Change Impact Safety` 映射为正式顶层 Goal `Change Safety`；
6. Completeness 只检查本次 Change 实际承担以及实际语义影响触发的 Requirement / Design Commitment；
7. Verification Obligation 仅作解释性概念，不作为一等对象；
8. 六类 Finding taxonomy 正式化；
9. Severity 固定为 Critical / High / Medium / Low；
10. 五个 Goal 分别产生 PASS / PASS_WITH_RISK / BLOCK 状态；
11. Overall Verdict 固定为 PASS / PASS WITH RISK / BLOCK；
12. Mandatory Policy 是横切阻断路径，不是第六个 Goal；
13. Candidate Build / Runtime 是检查对象和 Evidence 来源，不是独立 Gate Goal；
14. 所有已有 Gate2 文档保持不变，本文件作为 `Gates2/v1` 下的 V1 统一规范独立存在。

---

## 23. Final Definition

Gate2 V1 可以定义为：

> 一个面向特定 Code Change / PR 的证据驱动准出门禁。它以 Consistency、Completeness & Coverage、Verification Result、Change Safety、Evidence Validity 五个顶层目标对 Change 进行矩阵式检查，以六类正式 Finding 表达发现，以 Critical / High / Medium / Low 表达风险严重度，以 Mandatory Policy 和显式 Risk Acceptance 约束阻断与例外，并最终输出 `PASS / PASS WITH RISK / BLOCK`。Gate2 的完整性只覆盖当前 Change 实际承担及其真实语义影响所触发的 Requirement / Design Commitment，不承担完整 Feature Acceptance。