# Gate2 Aim

## 1. Gate2 定位

Gate2 是 **Feature 实现完成后的独立验收门禁（Feature Acceptance Gate）**。

它的目的不是重新做一次完整 Code Review，也不是简单检查“测试是否通过”，而是：

> **阻止尚未被可信证据证明“行为完整、语义一致、行为正确且影响可接受”的 Feature 进入下一阶段。**

Gate2 关注的是 **Feature 是否已经成立，以及我们是否有足够可信的证据证明它成立**。

---

## 2. Gate2 最终准出目标

Gate2 的准出条件为：

```text
Feature Ready
=
Complete
∧ Consistent
∧ Correct
∧ Impact-safe
∧ Proven
```

五个维度并非完全同类，其逻辑结构如下：

```text
Feature Ready

1. Quality
   ├─ Complete
   ├─ Correct
   └─ Impact-safe

2. Semantic Alignment
   └─ Consistent

3. Assurance
   └─ Proven
```

---

## 3. 五个核心检查目标

### 3.1 Complete — 行为完整性

核心问题：

> **承诺要实现的行为是否全部形成闭环？**

检查对象包括：

- Story / Feature Goal
- AC
- Scenario
- Rule / Invariant
- State / Transition
- Data / Contract
- 必要的异常、边界行为
- 明确承诺的关键 NFR

典型问题：

- AC 未实现；
- Scenario 遗漏；
- Rule 未落到代码；
- 状态转换缺失；
- 异常路径只定义未实现；
- 只有 Stub、脚手架或接线，没有真实行为；
- Requirement 有实现但没有形成验证闭环。

结论：

```text
该做的，是否都做了？
```

---

### 3.2 Consistent — 语义一致性

核心问题：

> **需求、设计、实现、验证之间是否保持同一语义，没有发生漂移或重定义？**

重点检查：

```text
Story ↔ AC
AC ↔ Scenario
Scenario ↔ Rule / State / Data
Requirement ↔ Technical Design
Technical Design ↔ Implementation
Requirement ↔ Test / Oracle
Code Revision ↔ Build Artifact ↔ Evidence
```

典型问题：

- Design 重新定义 Requirement；
- Code 与批准的关键设计语义不一致；
- Test Oracle 与 AC 真正要求不一致；
- Story、AC、Scenario 相互冲突；
- Evidence 来自不同 Revision；
- AI 在设计、编码、测试过程中形成“内部自洽但整体偏离需求”的实现链。

结论：

```text
整条交付链，是否在表达和实现同一件事？
```

---

### 3.3 Correct — 行为正确性

核心问题：

> **已经实现的行为是否真的符合预期 Oracle？**

基本判定链：

```text
Requirement
    ↓
Expected Behavior / Oracle
    ↓
Actual Behavior
    ↓
Expected == Actual ?
```

重点检查：

- 正常路径是否正确；
- Rule 条件、动作和优先级是否正确；
- State Transition 是否正确；
- Data 处理是否正确；
- 边界条件是否正确；
- 异常、拒绝、重试、恢复是否正确；
- 实现是否违反会直接影响行为正确性的关键技术约束。

结论：

```text
做出来的东西，是否真的做对了？
```

---

### 3.4 Impact-safe — 影响安全性

核心问题：

> **新 Feature 是否造成不可接受的已有行为退化？**

检查链路：

```text
Feature Change
      ↓
Changed Components / Contracts
      ↓
Impact Analysis
      ↓
Impacted Existing Behaviors
      ↓
Regression Obligations
      ↓
Evidence
```

重点关注：

- 关联 Feature 回归；
- 公共模块行为破坏；
- 数据状态破坏；
- 契约兼容性问题；
- Feature 相关安全 / 隐私风险；
- 数据迁移风险；
- 失败恢复风险；
- 跨场景副作用。

Gate2 不负责证明整个系统“零回归”，而是要求：

> **对本次变更合理识别出的影响范围和高风险行为完成验证。**

结论：

```text
新 Feature 做对以后，有没有把已有系统搞坏？
```

---

### 3.5 Proven — 证明充分性

核心问题：

> **我们是否拥有足够可信的证据证明前面的结论成立？**

AI Native 场景必须遵循：

```text
Claim ≠ Evidence
```

Agent 声称：

- implementation complete；
- tests passed；
- all requirements satisfied；

都不能直接作为 Gate PASS 依据。

完整证明链应为：

```text
Claim
  ↓
Requirement / Obligation
  ↓
Implementation
  ↓
Verification
  ↓
Oracle
  ↓
Evidence
  ↓
Final Revision
```

Evidence 至少应检查：

| 属性 | 核心问题 |
|---|---|
| Relevance | Evidence 是否真的证明目标 Requirement？ |
| Oracle | 是否能区分正确和错误？ |
| Freshness | 是否来自最终 Revision？ |
| Identity | 执行主体、环境、配置是否明确？ |
| Observability | 是否观察到了真正目标行为？ |
| Integrity | Evidence 是否完整、真实、可访问？ |
| Conflict | 是否存在冲突证据？ |

以下内容不能单独作为 Feature Ready 的证明：

- compile PASS；
- CI PASS；
- 测试报告存在；
- Coverage 达标；
- 源码字符串扫描；
- Stub / synthetic conformance；
- 旧 Revision 报告；
- 预构建二进制；
- 开发 Agent 自我声明。

结论：

```text
我们凭什么相信前四个结论是真的？
```

---

## 4. Gate2 顶层检查矩阵

| 检查对象 | Complete | Consistent | Correct | Impact-safe | Proven |
|---|---|---|---|---|---|
| **Story / AC** | 承诺是否全部闭环 | Story、AC、Scenario 语义是否一致 | 最终行为是否满足验收语义 | 是否改变相关已有行为 | 是否有下层行为与 Evidence 支撑 |
| **Scenario / Rule / State / Data** | 是否全部实现 | 相互之间及与 AC 是否一致 | 行为、规则、状态、数据是否正确 | 是否产生跨场景 / Contract 副作用 | 是否有有效 Oracle 与执行 Evidence |
| **Technical Design** | 关键设计约束是否落实 | 是否重定义或偏离 Requirement | 是否能正确支撑目标行为 | 是否引入系统级高风险影响 | 关键设计结论是否可验证 |
| **Implementation / Diff** | 是否真正实现而非 Stub | 是否与 Requirement / Design 保持一致 | 实现语义是否正确 | 是否存在未声明或高风险副作用 | 是否属于最终 Revision |
| **Impact / Existing Behavior** | 合理影响范围是否识别 | 影响判断是否与变更语义一致 | 受影响行为是否仍正确 | 是否存在不可接受回归 | 是否有风险匹配的 Regression Evidence |
| **Verification / Oracle** | 关键 Obligation 是否都有验证 | Test Oracle 是否与 Requirement 一致 | Oracle 是否能够判定正确性 | 是否覆盖高风险影响 | Evidence 是否 fresh / relevant / observable |
| **Evidence** | 是否覆盖所有阻断级 Obligation | Evidence 与代码 / 测试 / Revision 是否一致 | 是否真正支撑对应 Claim | 是否证明关键影响安全 | 来源、环境、Revision、结果是否可信 |
| **Finding Closure** | 历史阻断项是否全部处理 | 修复是否针对原 Finding | 修复是否真正有效 | 是否引入新问题 | 是否有当前 Revision Closure Evidence |

---

## 5. Gate2 检查主流程

```text
Feature Implementation Finished
            │
            ▼
1. Freeze Snapshot
            │
            ▼
2. Build Verification Obligations
            │
            ▼
3. Check Implementation Completeness
            │
            ▼
4. Check Semantic Consistency
            │
            ▼
5. Validate Behavior Correctness
            │
            ▼
6. Analyze Impact Safety
            │
            ▼
7. Validate Evidence Quality
            │
            ▼
8. Recheck Findings / High-risk Replay
            │
            ▼
9. Gate Verdict
```

### Step 1 — Freeze Snapshot

明确本次 Gate 的：

- Feature ID；
- Requirement Version；
- Design Version；
- Commit / Revision / Hash；
- Build Artifact；
- Test Artifact；
- Environment。

所有 Evidence 必须绑定该最终快照。

### Step 2 — Build Verification Obligations

从：

```text
Story
AC
Scenario
Rule
State
Data
NFR
```

提取：

```text
Requirement Obligations
```

再结合 Diff 和影响分析形成：

```text
Impact Obligations
```

最终：

```text
Feature Obligation Set
=
Requirement Obligations
+
Impact Obligations
```

原则：

> **不是“有什么测试就检查什么”，而是“应该证明什么，再寻找对应证据”。**

### Step 3 — Check Implementation Completeness

对每个 Obligation 检查：

```text
Requirement
    ↓
Implementation
```

识别未实现、部分实现、Stub、Fake、只接线无真实行为等问题。

### Step 4 — Check Semantic Consistency

检查：

```text
Requirement
↕
Design
↕
Implementation
↕
Verification
↕
Evidence
```

是否发生语义漂移、冲突或重定义。

### Step 5 — Validate Behavior Correctness

建立：

```text
Requirement
    ↓
Oracle
    ↓
Execution / Inspection
    ↓
Actual Result
```

判断实际行为是否符合预期。

### Step 6 — Analyze Impact Safety

从 Diff、依赖、共享组件、Contract、State、Data 等识别受影响已有行为，并形成 Regression Obligations。

### Step 7 — Validate Evidence Quality

检查每个关键结论的 Evidence 是否：

- relevant；
- fresh；
- observable；
- revision-bound；
- non-conflicting；
- non-skipped；
- non-stale；
- 具有有效 Oracle。

### Step 8 — Recheck Findings / High-risk Replay

对于历史 Finding：

```text
Finding
  ↓
Fix
  ↓
Closure Evidence
  ↓
Current Revision
```

Finding 不能因为重新扫描时没有再次发现而自动消失。

对于 P0 / P1、高风险 Scenario、关键用户路径、负向路径或高风险数据操作，Gate 可以独立执行最短复现，以增强 Assurance。

### Step 9 — Gate Verdict

最终形成 Gate Verdict。

---

## 6. Finding 分类

Gate2 Finding Type 固定为：

```text
Incomplete
Inconsistent
Incorrect
Unsafe
Unproven
```

含义：

### Incomplete

承诺行为或验证义务没有完整闭环。

### Inconsistent

需求、设计、实现、验证或 Evidence 之间存在语义冲突或漂移。

### Incorrect

行为已实现，但实际结果不符合定义或 Oracle。

### Unsafe

变更导致不可接受的回归、兼容性、状态、安全或其他系统影响。

### Unproven

当前可能没有发现明确错误，但缺乏足够可信 Evidence 证明结论。

Finding Type、检查对象和 Severity 必须保持正交：

```text
WHERE
→ Object Type / Object ID

WHAT
→ Incomplete / Inconsistent / Incorrect / Unsafe / Unproven

HOW BAD
→ P0 / P1 / P2 / P3
```

---

## 7. Gate Verdict

### PASS

满足：

```text
Complete
AND Consistent
AND Correct
AND Impact-safe
AND Proven
AND No Blocking Finding
```

### FAILED

存在确定性的阻断级：

- Incomplete P0/P1；
- Inconsistent P0/P1；
- Incorrect P0/P1；
- Unsafe P0/P1；
- 阻断级 Unproven。

### HUMAN_GATE

适用于：

- 高风险结论无法自动证明；
- 关键 Evidence 无法获得；
- 风险接受需要人工决策；
- Requirement / Design 本身存在未关闭决策缺口；
- P0 或自动修复预算耗尽。

---

## 8. Gate2 明确不负责什么

Gate2 不是：

- 全量 Code Quality Gate；
- 完整 Code Review 替代品；
- 全量测试矩阵执行器；
- 完整测试质量审计；
- 全系统零回归证明器；
- Release / Deployment Gate；
- 自动风险接受器。

以下内容只有在直接影响 Feature Ready 时才升级为 Gate2 Blocking Finding：

- 一般代码风格；
- 普通可维护性问题；
- 非关键架构偏差；
- 一般复杂度问题；
- 与本 Feature 无直接关系的工程治理问题。

---

## 9. Gate2 最终主链

Gate2 后续所有 Skill、Agent 和 CI 实现都应围绕以下主链展开：

```text
What must be true?
        │
        ▼
Verification Obligations
        │
        ▼
Requirement / Impact Commitment
        │
        ▼
Implementation
        │
        ▼
Consistency Check
        │
        ▼
Oracle
        │
        ▼
Verification
        │
        ▼
Evidence
        │
        ▼
Evidence Assurance
        │
        ▼
Finding
        │
        ▼
Verdict
```

---

## 10. 最终定义

> **Gate2 是 Feature 实现完成后的独立验收门禁。它从需求与变更影响承诺出发建立验证义务，检查需求、设计、实现、验证之间是否完整、一致且正确，确认变更没有造成不可接受的已有行为退化，并要求所有关键结论都由绑定最终代码快照的可信 Evidence 支撑。只有当 Feature 同时满足 Complete、Consistent、Correct、Impact-safe 和 Proven，且不存在阻断级 Finding 时，才能准出。**