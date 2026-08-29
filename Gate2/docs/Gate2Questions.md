# Gate2 决策问题记录

> 文件：`Gate2/docs/Gate2Questions.md`  
> 状态：当前讨论已收敛  
> 日期：2026-08-29  
> 用途：记录 Gate2 Code Change Exit Gate 在进入正式 Spec 前的关键决策问题、已确认答案与红军评审结论。本文是决策过程记录，不替代正式 Spec 或 Decision Record。

---

## 1. 当前结论摘要

Gate2 被定义为 **Code Change Exit Gate**，评估对象是一次确定的 Code Change / PR，在其合入共享基线、进入后续 Feature 验收前作出准出决策。

Gate2 只有两个核心 assurance objective：

1. **Change Correctness**：本次 Change 实际承担的需求/设计承诺是否被正确实现，并具有足够、可信的证据。
2. **Change Impact Safety**：本次 Change 产生的合理可识别影响中，是否不存在未关闭的不可接受风险。

Build、Test、Code Review、Static Analysis 等不是与上述目标并列的 Gate2 目标，而是 Verification Activity / Evidence / Guardrail 的来源。Mandatory Policy 是一条受严格治理的硬约束阻断路径，但不是第三个质量目标。

Gate2 的最终 Verdict 暂定为：

- `PASS`
- `PASS WITH RISK`
- `BLOCK`

---

# 2. 第一轮：Gate2 到底是什么门禁

## Q1 — Gate2 最终要保证什么？

候选：

- A. 代码质量足够好
- B. 代码测试充分
- C. 这次代码变更已经被充分证明，可以安全向后流转
- D. 代码满足所有工程规范

**已确认：C**

Gate2 的顶层对象是 **Change Readiness**，而不是 Code Quality、Test Quality 或 CI Quality。

---

## Q2 — Gate2 真正要拦哪两类风险？

**已确认：只保留两个核心拦截目标。**

### T1 — Incorrect / Unproven Intended Change

阻止“该改的东西没有做对，或者没有足够证据证明做对”的变更。

典型情况：

- Required behavior 未实现；
- Requirement / Rule / State / Contract 实现错误；
- 关键异常或边界行为遗漏；
- 关键正确性证据缺失。

### T2 — Unsafe Change Impact

阻止“变更对既有行为造成不可接受影响，或者相关高风险影响没有得到关闭”的变更。

典型情况：

- 变更公共组件导致既有 Feature 回归；
- API / Schema / State semantics 变化影响调用方；
- 高风险受影响行为没有验证；
- 高风险影响仍然不确定。

---

## Q3 — Evidence Completeness 是否是第三个门禁目标？

候选：

- A. Correctness / Safety / Evidence Completeness 三个并列目标
- B. Correctness / Safety 是目标，Evidence Sufficiency 是作出 PASS 判断的前提

**已确认：B**

Evidence Completeness 不是最终想保证的软件属性，而是 Gate 有资格作出 PASS 判断的前提。

关键原则：

```text
BLOCK != 一定发现 Defect

BLOCK =
  已发现不可接受问题
  OR
  没有足够依据证明可以放行
```

---

## Q4 — Engineering Quality 是否作为第三个核心目标？

候选：

- A. 增加 Engineering Quality 作为第三个一级目标
- B. Build / Lint / Security / Review 等作为 Verification / Guardrail / Mandatory Policy，根据其风险含义决定是否阻断

**已确认：B**

Gate2 不采用：

```text
Correctness + Safety + Engineering Quality
```

的三目标模型。

例如：

- Compile failure → Artifact 不成立 / 无法验证 → BLOCK；
- Critical security issue → 不可接受 Safety Risk → BLOCK；
- 普通 style warning → 不独立构成 BLOCK。

---

# 3. 第二轮：Correctness 与 Safety 的边界

## Q5 — Change Correctness 以什么作为真值来源？

候选：

- A. Task
- B. Technical Design
- C. Requirement / Story / AC
- D. Requirement/AC → Design Commitment → Implementation → Evidence 的可追溯链

**已确认：D，后经红军评审进一步收紧。**

Design Commitment 可以细化实现约束，但 **不能成为独立于 Requirement 的第二真值源**。正确关系为：

```text
Requirement / AC
      ↓ constrains
Design Commitment
      ↓ realized by
Implementation
      ↓ verified by
Evidence
```

如果 Design 与上游 Requirement 冲突，即使 Implementation 完全符合 Design，也不能得到 Correctness PASS。

---

## Q6 — Gate2 是否要求证明整个 Feature 的所有需求行为？

候选：

- A. 是，证明完整 Feature
- B. 只证明本次 Change 实际承担的行为，但必须检查 Scope 是否漏报
- C. 只看 Diff
- D. 完全留给 Gate3

**已确认：B**

Gate2 是 **Change-level assurance**，不是 Feature-level acceptance。

但 Change Scope 不能只相信开发者或 Agent 自报，必须校验：

```text
Declared Change Scope
        vs
Actual Semantic Scope / Impact
```

否则可以通过缩小声明范围逃过门禁。

---

## Q7 — Change Safety 的影响边界怎么定？

候选：

- A. 只检查修改文件附近
- B. 只检查直接调用方
- C. 按可解释 Impact Model 扩散，直到规定的风险边界可以关闭

**已确认：C**

基本链路：

```text
Diff
 ↓
Changed Symbol / Contract / Data / State
 ↓
Dependency / Call / Data / State / Config / Timing relationships
 ↓
Affected Behavior
 ↓
Affected Scenario / Feature
 ↓
Verification / Regression Evidence
```

Gate2 不承诺证明整个系统无回归。

---

## Q8 — 未知影响是否 BLOCK？

候选：

- A. 只有确认 Regression 才 BLOCK
- B. 所有不确定影响都 BLOCK
- C. 按风险分级，高风险未知 BLOCK，低风险未知可 WARN / Risk Accept

**已确认：C**

典型应阻断的未知：

- Public API / Contract 改变但调用方影响未知；
- Schema migration 影响未知；
- 核心状态机语义变化但下游影响未知；
- 高价值路径没有足够回归证据。

---

# 4. 第三轮：什么情况必须 BLOCK

## Q9 — Correctness 什么情况下必须 BLOCK？

**已确认：采用以下阻断模型。**

满足任一关键条件即可阻断：

1. Required behavior 未实现；
2. Implementation 与 Requirement / Design Commitment（且 Design 不得与上游冲突）不一致；
3. Required Rule / State / Contract / Invariant 被违反；
4. Critical / High 需求或风险缺少有效证据；
5. 有效 Evidence 明确证明行为失败。

---

## Q10 — Change Safety 什么情况下必须 BLOCK？

**已确认。**

满足任一关键条件：

1. 已确认 Critical / High regression；
2. Critical / High affected behavior 未完成充分验证；
3. Critical dependency / contract / schema / state impact 仍 materially uncertain；
4. High / Critical residual risk 未按 Policy 获得有效接受。

---

## Q11 — Evidence 缺失是否一律 BLOCK？

候选：

- A. 全部 BLOCK
- B. 从不 BLOCK
- C. 是否阻断由对应 Requirement / Risk 的严重度决定

**已确认：C**

基本策略：

| Evidence Gap 对应风险 | 默认处理 |
|---|---|
| Critical | BLOCK |
| High | BLOCK |
| Medium | Policy 决定，可 WARN / Risk Accept |
| Low | 通常非阻断 |

风险驱动 Evidence，而不是 Test Type 驱动 Risk。

---

## Q12 — Code Quality Finding 什么时候可以 BLOCK？

**已确认：Code Quality Finding 不自动构成 BLOCK。**

采用映射：

```text
Finding
  ↓
Correctness Risk?  → BLOCK（按严重度）
Safety Risk?       → BLOCK（按严重度）
Mandatory Policy?  → BLOCK
Otherwise          → Non-blocking Finding / WARN
```

例如：

- 命名较差 → 通常非阻断；
- Race condition → Correctness / Safety Risk → 可阻断；
- 明确违反已生效的强制架构规则 → Mandatory Policy → BLOCK。

---

# 5. 第四轮：Mandatory Policy 与风险分级

## Q13 — Mandatory Policy 允许包含什么？

候选：

- A. 所有工程规范
- B. 只有安全和合规
- C. 只有“不满足时没有资格进入下一阶段”的不可协商硬约束

**已确认：C**

Mandatory Policy 至少应满足：

1. 事先明确存在；
2. 对当前仓库/模块/Change 类型适用；
3. 违反后组织明确要求阻断；
4. 能被客观判断，不依赖临时主观意见。

---

## Q14 — Reviewer 是否允许临时新增 Mandatory Policy？

候选：

- A. 可以
- B. 不可以；Reviewer 可以提出 Risk Finding，但不能临时创造 Mandatory Policy
- C. Reviewer 完全不能造成 BLOCK

**已确认：B**

关键原则：

```text
Mandatory Policy = ex-ante rule
不是 ex-post opinion
```

Reviewer 临时发现的严重问题，若形成 Correctness / Safety Risk，仍然可以按风险规则 BLOCK；但不能伪装成新的 Mandatory Policy。

---

## Q15 — Risk Severity 根据什么分级？

**已确认：V1 采用 Critical / High / Medium / Low，语义上至少考虑三维。**

1. **Impact**：失败后的损失有多大；
2. **Exposure / Likelihood**：问题多容易发生或被触发；
3. **Recovery / Detectability**：发生后是否容易发现、恢复、回滚。

不按 Finding 类型机械固定严重度。

---

## Q16 — Evidence Gap 的等级怎么定？

**已确认：主要继承它本应支持的 Requirement / Risk 的严重度。**

例如：

```text
High-risk Requirement
+ Missing Evidence
→ High Evidence Gap
```

而不是：

```text
Missing Unit Test → High
Missing UI Test   → Medium
```

---

# 6. 第五轮：什么叫 Evidence 闭环

## Q17 — Requirement / Risk 什么时候算验证闭环？

候选：

- A. 有 PASS Test 即闭环
- B. Reviewer 认为合理即闭环
- C. 语义明确 + Verification Method 合适 + Evidence 有效 + Oracle 满足 + 无冲突证据 + 残余风险可接受

**已确认：C**

概念模型：

```text
Closed =
  要证明的 Requirement/Risk 语义明确
+ Verification Method 与 Claim 匹配
+ Evidence 可追溯且来源可信
+ Evidence 与 Claim 相关
+ Oracle / Policy Assertion 有效
+ Result 满足预期
+ 无未解决的 contradictory evidence
+ Residual Risk 在 Policy 允许范围内
```

注意：现有 DR-0001 已决定 **Verification Obligation 不作为 V1 一等对象**。因此上述“obligation”只保留解释性语义，正式追溯链仍为 Requirement Object → Verification Activity/Test → Evidence。

---

## Q18 — 是否所有 Requirement 都必须通过动态 Test 才能关闭？

候选：

- A. 是
- B. Review / Static Analysis 可替代所有 Test
- C. Verification Method 由 Claim 类型决定

**已确认：C**

- Runtime behavior 原则上应有合适层级的动态可执行证据；
- Static constraint 可以由 Static Analysis / Architecture Check / Inspection 等关闭；
- Review 是 Verification Method，不是 Gate 本身。

---

## Q19 — PASS Test 是否必须验证 Evidence 本身有效？

候选：

- A. Test PASS 就相信
- B. 只有 Critical Test 检查
- C. Gate2 至少检查 Evidence 与 Claim 的可追溯性和基本有效性

**已确认：C**

最小链路：

```text
Requirement / Risk Claim
      ↓ mapped-to
Verification Activity / Test
      ↓
Executed / Produced?
      ↓
Relevant?
      ↓
Oracle / Assertion valid?
      ↓
Result interpretable?
      ↓
Evidence supports closure?
```

Gate2 只判断 **Evidence fitness for claim**，不扩张成全面 Test Quality Audit。

---

## Q20 — 残余风险是否允许被接受后放行？

候选：

- A. 任何残余风险都 BLOCK
- B. Reviewer 口头接受即可
- C. 允许显式 Risk Acceptance，但必须有权限、范围和审计记录

**已确认：C**

默认策略：

- Critical：正常 Gate2 流程中不可接受；
- High：默认 BLOCK，例外需要更高授权；
- Medium：可由 Policy 允许 Risk Accept；
- Low：通常非阻断。

Risk Acceptance 至少记录：

- Risk；
- Reason；
- Scope / Impact；
- Missing Evidence（如有）；
- Accepting Role / Owner；
- Follow-up / Expiration（适用时）。

---

## Q21 — Gate2 Verdict 使用几态？

候选：

- A. PASS / BLOCK
- B. PASS / PASS WITH RISK / BLOCK
- C. 增加 WARN / UNKNOWN / PARTIAL PASS 等更多状态

**已确认：B**

### PASS

- 不存在 blocking failure；
- 所有 required blocking claims 已充分关闭；
- 不存在未接受的不可接受残余风险。

### PASS WITH RISK

- 不存在 blocking failure；
- 存在已按 Policy 正式接受并记录的 residual risk。

### BLOCK

至少存在之一：

- Correctness 无法充分证明；
- 不可接受 Change Impact Risk 未关闭；
- Blocking Evidence Gap；
- Applicable Mandatory Policy violation。

> 待专门 Decision Record 将该 Verdict 词汇与项目 Overview 中较宽泛的 `PASS / WARN / BLOCK` 表述统一。

---

# 7. 红军评审：对已确认模型的反证与收紧

在 Q1–Q21 初步收敛后，对整个 Gate2 模型进行了红军式挑战。结论是不推翻核心设计，但增加以下五个收紧原则。

## R1 — Change Scope 不能只相信声明

风险：开发者/Agent 可通过少声明 Requirement ID 或缩小 Change Intent 来降低 Gate2 覆盖范围。

**收紧结论：**

Gate2 必须对比：

```text
Declared Scope
     vs
Actual Semantic Scope / Impact
```

Scope mismatch 本身形成 Finding，并按其带来的 Correctness / Safety Risk 处理。

---

## R2 — Design Commitment 不能成为独立真值源

风险：如果 Design 本身与 Requirement 冲突，Implementation 完全符合 Design 仍可能是错误实现。

**收紧结论：**

```text
Requirement / AC
      ↓
Design Commitment
      ↓
Implementation
```

Design 只能细化上游语义，不得覆盖或重新定义 Requirement。

---

## R3 — Change Safety 是 bounded assurance，不是 zero-regression guarantee

风险：Impact Analysis 永远存在未知未知，Gate2 无法证明整个系统“绝无回归”。

**收紧结论：**

Gate2 的 Safety Claim 只能是：

> 在规定、可解释、可审计的影响分析方法所识别的合理范围内，不存在未关闭的不可接受 Change Impact Risk。

Gate2 必须暴露影响分析的 boundary / confidence，而不能暗示全局完备性。

---

## R4 — Evidence Validity 不能膨胀为 Test Quality Audit

风险：继续增加 mock 合理性、覆盖率、测试结构、flakiness、测试代码风格等检查，会把 Gate2 变成另一个测试评审系统。

**收紧结论：**

Gate2 只验证：

> Evidence 是否足以支持当前 Requirement / Risk Claim。

不负责全面评价所有 Test Asset 的工程质量。

---

## R5 — Mandatory Policy 需要准入机制

风险：所有“重要规范”不断加入 Mandatory Policy 后，Gate2 会重新退化成传统 CI Quality Gate。

**收紧结论：Blocking Policy Admission Criteria 至少包括：**

1. 与生命周期准出风险直接相关；
2. 可自动或客观判断；
3. 有明确 Owner；
4. 有明确 Scope；
5. 有明确版本；
6. 有例外机制（若允许例外）；
7. 有风险、合规、安全、兼容或构建完整性依据。

不满足准入标准的工程规则默认不得成为 Gate2 blocking policy。

---

# 8. 与其他机制的边界结论

## Gate2 vs CI

```text
CI = Execution Platform / Evidence Producer
Gate2 = Evidence Evaluation + Lifecycle Verdict
```

CI Green 不自动等于 Gate2 PASS。

---

## Gate2 vs Code Review

```text
Code Review = Verification Method
Gate2 = Decision Layer
```

Review 产生 Finding / Evidence / Risk；Gate Policy 决定其是否阻断。

---

## Gate2 vs Gate3

```text
Gate2 = Change-level assurance
Gate3 = Feature-level acceptance
```

Gate2 不负责全量 Feature AC / User Journey / E2E 验收；Gate3 不应重新承担 Diff Impact Analysis 和 Code Change 级准出职责。

---

# 9. 已确认的 Gate2 顶层定义

> **Gate2 是针对一次代码变更的准出决策门禁。它验证本次变更实际承担的需求/设计承诺是否被正确实现，并评估由该变更产生的可识别影响风险是否已被充分关闭；当关键正确性无法证明、存在未关闭的不可接受影响风险，或违反既定强制政策时阻断准出。**

门禁主链：

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

---

# 10. 后续应通过正式 Artifact 解决的问题

以下不再作为顶层目标探索问题，而转入 Spec / Decision Record / Implementation：

1. 用专门 Decision Record 固化 Gate2 两个核心 assurance objective；
2. 固化 Mandatory Policy 的治理和准入规则；
3. 固化 bounded assurance 语义；
4. 统一 `PASS / PASS WITH RISK / BLOCK` 与项目总体 Verdict vocabulary；
5. 定义 Normalized Gate2 Input / Output Contract；
6. 定义版本化 Gate Policy 数据结构；
7. 在后续实现中定义 Impact Analysis producer 与 Gate2 evaluator 的边界。
