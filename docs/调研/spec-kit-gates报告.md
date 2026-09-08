# Spec Kit Gates 质量评估机制调查报告

> 文件名：`spec-kit-gates报告.md`  
> 调研对象：GitHub Spec Kit  
> 调研日期：2026-09-08  
> 用途：作为自有 Gates 质量体系设计、职责划分、Finding 分类、准出标准与闭环机制的参考

---

## 1. 背景与目标

### 1.1 调研背景

在 AI Agent 驱动的软件研发流程中，问题已经不再只是“代码是否正确”，而是需要沿着完整的软件意图传递链持续保证质量：

```text
业务意图
  ↓
Specification
  ↓
Architecture / Plan
  ↓
Tasks
  ↓
Implementation
  ↓
Evidence / Verification
```

其中任何一层发生信息损失，都会导致后续实现偏离原始目标。

典型问题包括：

- 需求存在关键未决策项，但 Agent 已经开始设计；
- 需求语句本身没有歧义，但重要异常场景根本没有定义；
- `spec.md` 已定义要求，但 `plan.md` 或 `tasks.md` 没有承接；
- `spec / plan / tasks` 三份文档彼此一致，但代码实际上没有完整实现；
- 开发实现了需求之外的行为，形成 Scope Creep；
- 同一个问题在多个检查阶段重复发现，却没有明确的问题 Owner 和回流规则。

GitHub Spec Kit 在其 Spec-Driven Development（SDD）流程中提供了多个质量相关命令，其中四个命令对建立软件研发质量门具有特别强的参考价值：

- `/speckit.clarify`
- `/speckit.checklist`
- `/speckit.analyze`
- `/speckit.converge`

本报告不把这四个命令简单理解为“四次检查”，而是将其抽象为四个不同层次的质量控制能力：

```text
Q1 Clarify   ：需求决策是否已经确定？
Q2 Checklist ：需求本身是否写得完整、清晰、可验证？
Q3 Analyze   ：需求 → 设计 → 任务的传递是否完整、一致？
Q4 Converge  ：最终代码是否真正兑现这些意图？
```

这四层共同形成：

> **Intent Determination → Specification Quality → Artifact Alignment → Implementation Fidelity**

即：

> **意图确定性 → 规格质量 → 工程制品一致性 → 实现忠实度**

---

### 1.2 报告目标

本报告目标不是编写 Spec Kit 使用手册，而是回答以下几个与自有 Gates 设计直接相关的问题：

1. Spec Kit 四个质量能力分别解决什么问题？
2. 每一层检查对象、方法和判断标准是什么？
3. 四层之间哪些能力看起来相似，实际为什么不应合并？
4. 如何定义每一层的 Finding Ownership，避免重复检查和责任模糊？
5. 哪些机制可以直接借鉴到自有 Gate1 / Gate2？
6. 哪些能力 Spec Kit 本身没有覆盖，需要自有 Gates 补充？
7. 如何建立统一的：
   - Finding Model
   - Severity Model
   - Evidence Model
   - Entry / Exit Criteria
   - 闭环模型

最终目标是把 Spec Kit 从“工具命令集合”抽象为一套可复用的质量架构参考。

---

### 1.3 Spec Kit 在 SDD 流程中的位置

Spec Kit 当前主要命令包括：

```text
constitution
     ↓
specify
     ↓
clarify
     ↓
plan
     ↓
tasks
     ↓
implement
     ↓
converge
```

同时提供两个重要的质量辅助能力：

```text
checklist
analyze
```

其中：

- `clarify` 官方建议在 `plan` 前完成；
- `checklist` 是可按领域和使用目的动态生成的 requirements-quality artifact，不被严格限定在单一生命周期位置；
- `analyze` 明确要求在 `tasks.md` 完成之后、实现之前执行；
- `converge` 明确要求在实现之后，对当前代码状态进行意图一致性检查。

因此，本报告中的：

```text
Clarify → Checklist → Analyze → Converge
```

不是在声称 Spec Kit 官方定义了一个严格连续的四命令流水线，而是把这四种能力抽象为 **四层质量门模型**。

推荐理解方式：

```text
Specification
    │
    ├── Q1 Clarify
    │      消除关键 Unknown
    │
    ├── Q2 Checklist
    │      检查 Requirement Quality
    │
Plan / Tasks
    │
    ├── Q3 Analyze
    │      检查 Artifact Alignment
    │
Implementation
    │
    └── Q4 Converge
           检查 Code ↔ Intent
```

---

### 1.4 本报告关注范围

本报告重点关注：

- Requirement / Specification Quality
- 跨制品一致性
- Traceability
- Coverage
- Intent 到 Code 的映射
- Finding 分类
- Severity
- Evidence
- Gate Entry / Exit Criteria
- 问题回流与闭环

不重点讨论：

- Spec Kit CLI 安装细节；
- Agent integration 安装；
- Git extension；
- taskstoissues；
- 具体编程语言或框架；
- CI/CD 实现方式。

---

### 1.5 对自有 Gates 的借鉴原则

借鉴 Spec Kit 时应遵循五个原则。

#### 原则一：借鉴“问题模型”，而不是复制命令

自有 Gates 不需要机械复制：

```text
clarify
checklist
analyze
converge
```

更重要的是复制其背后的四类质量问题：

```text
Decision Unknown
Requirement Quality Gap
Artifact Mapping Gap
Implementation Gap
```

#### 原则二：每一层必须有唯一主责问题

如果四层都检查：

- 完整性；
- 清晰性；
- 一致性；

那么最终一定发生严重重复。

应该定义：

```text
Clarify   → Decision Unknown Owner
Checklist → Requirement Quality Owner
Analyze   → Artifact Alignment Owner
Converge  → Implementation Fidelity Owner
```

#### 原则三：允许重复“发现”，但禁止重复“治理”

后续阶段发现前序问题是正常的。

例如 Analyze 发现需求歧义，并不意味着 Analyze 应承担 Clarify 的职责。

正确模型：

```text
发现问题
   ↓
分类 Finding
   ↓
定位 Owner
   ↓
回流到 Owner 层修复
```

#### 原则四：Gate 必须有 Evidence

任何 Verdict 必须能够回答：

> 为什么 Pass？  
> 为什么 Block？  
> 哪条要求？  
> 哪个证据？  
> 谁负责修复？

#### 原则五：Coverage 不等于 Correctness

例如：

```text
FR-001 → T012
```

只能证明需求有 Task 承接，不能证明：

```text
T012 是正确的
代码实现了 T012
代码行为满足 FR-001
```

所以必须同时建立：

```text
Coverage + Consistency + Evidence + Verification
```

---

# 2. Spec Kit 四层质量门总体模型

## 2.1 完整流程位置

从完整 SDD 角度看，四层检查分别位于不同信息成熟阶段。

```text
                        ┌───────────────┐
                        │ Constitution  │
                        └───────┬───────┘
                                │
                                ▼
                        ┌───────────────┐
                        │    Specify    │
                        └───────┬───────┘
                                │
                                ▼
                    ┌─────────────────────┐
                    │ Q1 Clarify          │
                    │ 决策是否确定？       │
                    └──────────┬──────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
          ┌───────────────┐       ┌──────────────────┐
          │ Q2 Checklist  │       │      Plan        │
          │ 规格质量如何？ │       └────────┬─────────┘
          └───────────────┘                │
                                          ▼
                                  ┌───────────────┐
                                  │     Tasks     │
                                  └───────┬───────┘
                                          │
                                          ▼
                                  ┌──────────────────┐
                                  │ Q3 Analyze       │
                                  │ 制品是否对齐？    │
                                  └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │   Implement      │
                                  └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │ Q4 Converge      │
                                  │ 实现是否兑现？    │
                                  └──────────────────┘
```

注意：

- `Checklist` 可以根据目的在 Spec 阶段生成，也可以结合已有 Plan / Tasks 作为上下文生成专项质量检查表；
- 从自有 Gate 设计角度，建议把它定位为 **Specification Quality Gate**，核心检查对象仍然是“要求写得是否足够好”，而不是代码实现。

---

## 2.2 四层质量门定义

| 层 | 名称 | 核心对象 | 核心问题 | 主 Finding |
|---|---|---|---|---|
| Q1 | Clarify | Spec / Requirement | **我们是否知道到底要什么？** | Decision Unknown |
| Q2 | Checklist | Spec / Requirement Quality | **该定义的是否都定义清楚了？** | Requirement Quality Gap |
| Q3 | Analyze | Spec + Plan + Tasks | **工程转换过程中是否丢失、冲突？** | Artifact Mapping Gap |
| Q4 | Converge | Intent + Current Code | **当前实现是否真正兑现意图？** | Implementation Gap |

---

## 2.3 四层递进关系

四层不是简单从“粗”到“细”，而是检查对象发生了变化。

### 第一层：Intent Determination

```text
未知决策
    ↓
确定决策
```

### 第二层：Specification Quality

```text
确定的意图
    ↓
完整、清晰、可验证的规格
```

### 第三层：Artifact Alignment

```text
Specification
    ↓
Plan
    ↓
Tasks
```

检查意图是否在工程转换中保持。

### 第四层：Implementation Fidelity

```text
Specification / Plan / Tasks
            ↓
          Code
```

检查当前代码是否与声明意图一致。

因此整个模型是：

```text
意图没有确定
    ↓ Clarify
意图确定但表达质量不足
    ↓ Checklist
表达完整但工程分解发生损失
    ↓ Analyze
工程制品正确但实现出现偏差
    ↓ Converge
Converged
```

---

## 2.4 四层职责边界

四层最重要的不是“检查了多少内容”，而是边界是否明确。

| 问题 | Clarify | Checklist | Analyze | Converge |
|---|---:|---:|---:|---:|
| 关键业务决策未知 | **Owner** | 可发现 | 可发现 | 可发现 |
| Requirement 缺异常场景 | 可发现 | **Owner** | 可发现 | 通常较晚 |
| Requirement 描述不可测 | 可发现 | **Owner** | 可发现 | 间接发现 |
| Requirement 未进入 Plan | - | - | **Owner** | 可间接发现 |
| Requirement 未进入 Task | - | - | **Owner** | 可间接发现 |
| Plan 与 Spec 冲突 | - | 辅助 | **Owner** | 可发现 |
| Task 无需求来源 | - | - | **Owner** | 可发现 |
| Code 缺实现 | - | - | - | **Owner** |
| Code 部分实现 | - | - | - | **Owner** |
| Code 与需求相反 | - | - | - | **Owner** |
| Code 实现了未请求功能 | - | - | 可发现 Task 层异常 | **Owner** |

---

## 2.5 四层 Finding Ownership

推荐将 Finding 主类型明确固定为：

```text
Q1 Decision Unknown
Q2 Requirement Quality Gap
Q3 Artifact Mapping Gap
Q4 Implementation Gap
```

进一步细化：

### Q1

```text
UNKNOWN_DECISION
AMBIGUOUS_DECISION
UNRESOLVED_ASSUMPTION
```

### Q2

```text
MISSING_REQUIREMENT
UNCLEAR_REQUIREMENT
UNTESTABLE_REQUIREMENT
INCONSISTENT_REQUIREMENT
SCENARIO_COVERAGE_GAP
EDGE_CASE_GAP
NFR_GAP
DEPENDENCY_GAP
```

### Q3

```text
UNMAPPED_REQUIREMENT
UNMAPPED_TASK
SPEC_PLAN_CONFLICT
PLAN_TASK_CONFLICT
TERMINOLOGY_DRIFT
CONSTITUTION_VIOLATION
ARTIFACT_UNDERSPECIFICATION
```

### Q4

```text
MISSING
PARTIAL
CONTRADICTS
UNREQUESTED
```

这种划分非常适合作为自有 Gates 的 Finding Type 一级分类。

---

## 2.6 四层输入、输出与生命周期位置

| Gate | Input | Output | 主要时间点 |
|---|---|---|---|
| Clarify | spec.md + constitution | 更新后的 spec.md / clarification | Plan 前 |
| Checklist | spec / plan / tasks 中相关上下文 | `checklists/*.md` | Spec 质量评审阶段，可专项运行 |
| Analyze | spec.md + plan.md + tasks.md + constitution | 只读分析报告 | Tasks 后、Implement 前 |
| Converge | spec + plan + tasks + constitution + current code | Finding + append-only Convergence Tasks | Implement 后 |

---

# 3. 四层质量门详细分析

## 3.1 Q1 Clarify：需求决策确定性门

### 3.1.1 目标

Clarify 的目标不是“让文档更长”，也不是把所有细节全部问一遍。

核心目标是：

> **发现那些会实质影响架构、数据模型、任务拆分、测试设计、UX 行为、运维准备或合规判断的关键未知决策，并在进入 Plan 前解决。**

例如：

```text
上传失败后支持重试
```

这里可能包含多个实现方向：

- 用户手动重试；
- 自动重试；
- 固定次数；
- 指数退避；
- 网络恢复后自动继续；
- App 重启后继续；
- 从头重传；
- checkpoint resume。

如果这些决策没有确定，直接进入 Plan，Agent 必须自行补全。

这会带来：

```text
隐式假设
→ 架构偏差
→ Task 偏差
→ 测试 Oracle 偏差
→ 后期返工
```

---

### 3.1.2 检查对象

Clarify 主要针对当前 Feature Spec，同时考虑 Constitution 中的治理约束。

典型对象包括：

- User Goal；
- Scope；
- User Role；
- Requirement；
- Scenario；
- Data；
- State；
- Interaction；
- NFR；
- External Dependency；
- Failure Behavior；
- Constraint；
- Terminology；
- Acceptance Criteria；
- Placeholder。

---

### 3.1.3 核心问题

Clarify 本质是在问：

> **这个地方是否仍然存在多个合理解释，而不同解释会导致明显不同的实现或验证方式？**

例如：

```text
系统应快速完成搜索
```

这里既存在 Requirement Quality 问题，也存在一个未决策问题：

> “快速”的业务预期到底是多少？

如果没有明确阈值，性能设计和验收 Oracle 都无法确定。

---

### 3.1.4 检查方法

官方 Clarify 的核心机制可以抽象为：

```text
Load Spec
   ↓
Structured Coverage Scan
   ↓
Clear / Partial / Missing
   ↓
Candidate Unknowns
   ↓
Impact × Uncertainty
   ↓
Top Questions
   ↓
Sequential Ask
   ↓
Decision
   ↓
Encode Back to Spec
```

这一点非常值得自有 Gates 借鉴：

> Clarify 不应该输出一张巨大问题清单让用户自己处理，而应该对问题做风险优先级排序。

---

### 3.1.5 Coverage Scan

Clarify 对 Spec 进行结构化扫描，核心领域包括：

#### Functional Scope & Behavior

- 核心用户目标；
- Success Criteria；
- Explicit Out-of-scope；
- 用户角色差异。

#### Domain & Data Model

- Entity；
- Attribute；
- Relationship；
- Identity / Uniqueness；
- Lifecycle；
- State Transition；
- Data Volume / Scale Assumption。

#### Interaction & UX Flow

- Critical Journey；
- Error State；
- Empty State；
- Loading State；
- Accessibility；
- Localization。

#### Non-Functional Quality

- Performance；
- Scalability；
- Reliability；
- Availability；
- Observability；
- Security；
- Privacy；
- Compliance。

#### Integration & External Dependencies

- 外部服务；
- API；
- Failure Mode；
- Import / Export；
- Protocol；
- Version。

#### Edge Case & Failure Handling

- Negative Scenario；
- Rate Limit；
- Conflict Resolution。

#### Constraints & Tradeoffs

- Technical Constraint；
- Trade-off；
- Rejected Alternative。

#### Terminology & Consistency

- Canonical Term；
- Synonym；
- Deprecated Term。

#### Completion Signal

- AC 是否可测试；
- DoD 是否可测量。

#### Misc / Placeholder

- TODO；
- unresolved decision；
- “robust / intuitive / fast”等模糊形容词。

---

### 3.1.6 Clear / Partial / Missing 分类

每个领域可以抽象为：

#### Clear

信息已经足以支撑后续设计与验证。

#### Partial

已经有部分定义，但仍存在影响实现的重要信息缺口。

#### Missing

重要领域完全没有定义。

例如：

| Domain | Status | 示例 |
|---|---|---|
| 上传成功行为 | Clear | 明确返回成功状态 |
| 网络中断恢复 | Partial | 写了“支持恢复”，未定义如何恢复 |
| 用户取消 | Missing | 完全未描述 |

---

### 3.1.7 问题优先级方法

官方采用近似：

```text
Priority ≈ Impact × Uncertainty
```

高优先问题：

- 会改变架构；
- 会改变数据模型；
- 会改变 API contract；
- 会改变安全策略；
- 会改变测试 Oracle；
- 会改变核心用户行为。

低优先问题：

- UI 文案；
- 风格偏好；
- 可在 Plan 中自然决定的内部实现细节；
- 对验证没有实质影响的问题。

因此 Clarify 的关键不是“问得多”，而是：

> **最大化每一个问题带来的风险降低。**

---

### 3.1.8 Finding 类型

建议自有 Gate 中把 Clarify Finding 标准化为：

| Type | 定义 |
|---|---|
| `UNKNOWN_DECISION` | 必须做选择，但当前没有决策 |
| `AMBIGUOUS_DECISION` | 当前描述支持多个互斥解释 |
| `UNRESOLVED_ASSUMPTION` | 关键设计建立在未确认假设上 |
| `MISSING_POLICY` | 关键业务行为没有策略定义 |
| `UNQUANTIFIED_TARGET` | 需要量化但没有明确指标 |

---

### 3.1.9 准入与准出标准

#### Entry

至少具备：

- Feature Goal；
- 初始 Spec；
- 核心 User Story / Requirement。

#### Exit

建议自有 Gate 标准：

```text
Critical Unknown = 0
High-impact Ambiguity = 0
Unresolved Security/Privacy Decision = 0
Unresolved Core State/Failure Policy = 0
```

允许：

- 明确记录的 Low-risk Assumption；
- 明确 Deferred 到 Plan 的技术选择；
- 不影响核心行为的开放问题。

最核心准出判断：

> **不同工程师/Agent 阅读当前 Spec，不应该因为关键业务未决策而得到两套都“合理”的核心实现。**

---

### 3.1.10 输出物

官方 Clarify 会把确认结果编码回 Spec。

自有 Gates 可以进一步标准化输出：

```yaml
clarifications:
  - id: CL-001
    source: FR-008
    question: 网络恢复后上传如何处理？
    decision: 从checkpoint自动续传
    impact: high
    status: resolved
```

关键原则：

> 决策不能只存在于聊天上下文中，必须回写到可持续维护的 Artifact。

---

### 3.1.11 能发现与不能发现的问题

#### 擅长发现

- 不确定决策；
- 模糊行为；
- 隐含假设；
- 缺失 Failure Policy；
- 状态生命周期未定义；
- 关键 NFR 未量化。

#### 不擅长证明

- Plan 是否正确；
- Task 是否覆盖；
- Code 是否实现；
- Test 是否通过；
- Runtime 行为是否可靠。

因此：

> Clarify 是 **Decision Quality Gate**，不是完整的 Requirement Quality Gate。

---

## 3.2 Q2 Checklist：规格质量门

### 3.2.1 目标

Checklist 的核心理念是：

> **Unit Tests for Requirements Writing**

可以理解为：

```text
如果 Spec 是用自然语言写的程序，
Checklist 就是这个“自然语言程序”的 Unit Test。
```

Checklist 不检查：

```text
按钮有没有点击成功
API 有没有返回 200
代码有没有实现异常处理
```

而检查：

```text
按钮行为要求是否定义完整
API 成功/失败要求是否写清
异常处理规则是否存在
```

因此它的检查对象不是 Implementation，而是 Requirement Writing Quality。

---

### 3.2.2 “Requirements Unit Test”理念

传统测试：

```text
Implementation
    ↓
Expected Behavior
```

Checklist：

```text
Requirement Text
    ↓
Quality Criterion
```

例如：

错误方式：

```text
[ ] Verify upload retries after network recovery
```

这是 Implementation Verification。

正确方式：

```text
[ ] 是否定义网络恢复后的重试行为？ [Coverage]
```

或者：

```text
[ ] “自动恢复”是否定义恢复触发时机和最大等待时间？ [Clarity]
```

---

### 3.2.3 检查对象

Checklist 可以根据领域生成，例如：

```text
security.md
api.md
ux.md
reliability.md
performance.md
privacy.md
```

其上下文可以来自：

- spec.md；
- plan.md；
- tasks.md；

但无论读取哪些 Artifact，它的检查目标仍然必须是：

> **Requirements 是否写得足够完整、明确、一致和可验证。**

---

### 3.2.4 核心质量维度

#### Completeness

该定义的要求是否存在？

例如：

```text
是否定义所有 API Failure Mode 的处理要求？
```

#### Clarity

Requirement 是否有唯一、具体解释？

```text
“快速响应”是否定义具体时间阈值？
```

#### Consistency

不同 Requirement 是否冲突？

```text
离线模式与“所有操作必须实时同步云端”是否矛盾？
```

#### Measurability

是否可以建立客观 Oracle？

```text
“体验流畅”如何判定？
```

#### Scenario Coverage

是否覆盖：

- Primary；
- Alternate；
- Exception；
- Recovery；
- Non-functional Scenario。

#### Edge Case Coverage

是否定义：

- Boundary；
- Empty；
- Invalid；
- Concurrent；
- Timeout；
- Partial Failure；
- Resource Exhaustion。

#### NFR

是否明确：

- Performance；
- Reliability；
- Security；
- Privacy；
- Accessibility；
- Observability；
- Availability。

#### Dependency & Assumption

依赖和假设是否已经：

- 明确；
- 可追踪；
- 有验证方式；
- 有失败策略。

---

### 3.2.5 Checklist 生成方法

其逻辑可以抽象为：

```text
User Focus
   +
Feature Context
   ↓
Identify Quality Domain
   ↓
Select Requirement Quality Dimensions
   ↓
Generate Reviewer Questions
   ↓
Trace to Spec or Mark as Gap
   ↓
checklists/<domain>.md
```

Checklist 可以针对不同风险动态生成，而不是只维护一份万能模板。

这对自有 Gates 很重要：

> **固定 Checklist 适合标准合规项；动态 Checklist 更适合 Feature-specific 风险。**

推荐采用：

```text
Baseline Checklist
        +
Risk-driven Dynamic Checklist
```

组合模式。

---

### 3.2.6 Requirement Gap 分类

建议标准化为：

| Type | 含义 |
|---|---|
| `MISSING_REQUIREMENT` | 某项必要要求完全不存在 |
| `UNCLEAR_REQUIREMENT` | 有要求但描述不清 |
| `UNTESTABLE_REQUIREMENT` | 无法形成客观 Pass / Fail |
| `INCONSISTENT_REQUIREMENT` | 与其他要求冲突 |
| `SCENARIO_COVERAGE_GAP` | 缺主要/替代/异常/恢复场景 |
| `EDGE_CASE_GAP` | 缺边界条件 |
| `NFR_GAP` | 非功能要求缺失或不完整 |
| `DEPENDENCY_GAP` | 外部依赖行为未定义 |
| `ASSUMPTION_GAP` | 假设未显性化或未验证 |

---

### 3.2.7 Checklist 与测试用例的边界

这是最需要严格控制的地方。

#### Checklist

回答：

> **规格有没有定义正确的问题？**

#### Test Condition

回答：

> **哪些行为必须验证？**

#### Test Case

回答：

> **具体怎么验证？**

例如：

```text
Requirement:
网络恢复后自动续传。
```

Checklist：

```text
是否定义断网期间用户取消上传时的预期行为？
```

Test Condition：

```text
断网 → 用户取消 → 网络恢复
```

Test Case：

```text
Given 上传进度40%
And 网络断开
When 用户点击取消
And 网络恢复
Then 不应自动恢复上传
```

三者不能混淆。

---

### 3.2.8 准入与准出标准

#### Entry

- Requirement 已经基本成形；
- Clarify 的高风险未知项已完成主要收敛。

#### Exit

建议：

```text
Critical Requirement Gap = 0
Core Scenario Coverage Gap = 0
Untestable Core AC = 0
Security/Privacy Requirement Gap = 0
Core Failure/Recovery Requirement Gap = 0
```

不建议仅使用：

```text
Checklist Pass Rate >= 90%
```

因为 10% 未通过中可能恰好包含安全或核心数据一致性要求。

因此 Gate 应该：

> **Severity-aware，而不是纯百分比。**

---

### 3.2.9 输出物

例如：

```md
# Reliability Checklist

- [ ] CHK001 是否定义所有外部服务不可用时的系统行为？ [Coverage]
- [ ] CHK002 “自动恢复”是否定义最大恢复时延？ [Clarity]
- [ ] CHK003 是否定义用户取消与自动重试之间的优先级？ [Consistency]
- [ ] CHK004 是否定义重复请求的幂等要求？ [Gap]
```

自有 Gates 可以进一步为每项加入：

```text
Severity
Source
Owner
Decision
Status
Evidence
```

---

### 3.2.10 能发现与不能发现的问题

#### 能发现

- 需求没写全；
- 需求写得含糊；
- 需求无法测试；
- 场景覆盖不够；
- NFR 缺失；
- Requirement 冲突。

#### 不能证明

- Plan 是否承接；
- Tasks 是否覆盖；
- Code 是否实现；
- Runtime 是否满足指标。

因此：

> Checklist 是 **Requirement Quality Gate**。

---

## 3.3 Q3 Analyze：跨制品一致性门

### 3.3.1 目标

Analyze 发生了检查对象的根本变化。

Clarify / Checklist 主要针对：

```text
Spec 是否好？
```

Analyze 针对：

```text
Spec
 ↓
Plan
 ↓
Tasks
```

是否发生信息丢失、冲突或孤儿项。

核心目标：

> **保证 Requirement Intent 在工程化转换过程中保持 Traceability、Coverage 和 Consistency。**

---

### 3.3.2 检查对象

官方 Analyze 读取：

```text
spec.md
plan.md
tasks.md
constitution.md
```

Spec 重点：

- Overview；
- Functional Requirements；
- Success Criteria；
- User Stories；
- Edge Cases。

Plan 重点：

- Architecture / Stack；
- Data Model；
- Phase；
- Technical Constraint。

Tasks 重点：

- Task ID；
- Description；
- Phase；
- Parallel Marker；
- File Path。

Constitution 作为最高约束。

---

### 3.3.3 Requirement Inventory

Analyze 首先需要把自然语言文档转成可比较的语义模型。

例如：

```text
FR-001 用户可以上传文件
FR-002 上传过程中断网必须恢复
FR-003 用户取消后不得自动恢复
SC-001 95%上传请求10秒内进入传输状态
```

形成：

```yaml
requirements:
  FR-001:
    type: functional
  FR-002:
    type: reliability
  FR-003:
    type: behavior
```

这是后续 Traceability 的基础。

---

### 3.3.4 Requirement → Plan → Task 映射

理想关系：

```text
FR-002
   ↓
Plan: WorkManager + CheckpointStore
   ↓
T012 Create UploadWorker
T013 Persist checkpoint
T014 Restore pending upload
```

典型异常：

#### Requirement Lost

```text
FR-002
   ↓
Plan: none
   ↓
Tasks: none
```

#### Partial Propagation

```text
FR-002
   ↓
Plan: WorkManager
   ↓
Tasks: 创建 Worker
```

但没有 checkpoint persistence。

#### Orphan Task

```text
T020 添加云端诊断日志上传
```

没有任何 Requirement / Plan 来源。

---

### 3.3.5 六类分析方法

#### Duplication

发现近似重复 Requirement。

风险：

- 后续修改不一致；
- Task 重复；
- Oracle 重复或矛盾。

#### Ambiguity

发现遗留的：

- vague adjective；
- placeholder；
- undefined target。

注意：

> Analyze 可以“发现”残余歧义，但治理 Owner 仍然应回到 Clarify / Requirement 层。

#### Underspecification

例如：

- Requirement 有动作但没有对象；
- Story 与 AC 不一致；
- Task 引用了 Spec / Plan 中不存在的组件。

#### Constitution Alignment

Constitution 中 MUST 是强约束。

任何冲突应视为最高优先级问题之一。

#### Coverage Gap

检查：

```text
Requirement → Task ?
Task → Requirement ?
```

以及：

```text
Buildable Success Criteria → Task ?
```

#### Inconsistency

包括：

- Terminology Drift；
- Entity Drift；
- Architecture Conflict；
- Task Ordering Conflict；
- Requirement Conflict。

---

### 3.3.6 Traceability 与 Coverage

可以建立 Coverage：

```text
Requirement Coverage
=
有至少一个Task映射的Buildable Requirement
/
全部Buildable Requirement
```

例如：

```text
20 requirements
18 mapped
Coverage = 90%
```

但是 Coverage 只能证明：

> 有映射。

不能证明：

> 映射正确。

所以建议至少同时维护：

```text
Coverage
Consistency
Traceability
Critical Gap Count
```

---

### 3.3.7 Finding 严重级别

官方 Analyze 提供 CRITICAL / HIGH / MEDIUM / LOW 的分级启发。

可抽象为：

#### CRITICAL

- 违反 Constitution MUST；
- 核心 Artifact 缺失；
- 基线功能 Requirement 完全无 Task Coverage。

#### HIGH

- Requirement 冲突；
- Security / Performance 等关键属性模糊；
- AC 不可测试；
- 高价值功能的映射不完整。

#### MEDIUM

- Terminology Drift；
- NFR Task Coverage 缺失；
- Edge Case 不完整。

#### LOW

- 文案；
- 小重复；
- 不影响执行的表达问题。

---

### 3.3.8 准入与准出标准

#### Entry

```text
spec.md exists
plan.md exists
tasks.md complete
```

#### Exit

推荐自有标准：

```text
CRITICAL = 0
HIGH = 0
Core FR Task Coverage = 100%
Core AC Task Coverage = 100%
Constitution MUST Violation = 0
Unmapped Critical Task = 0
```

MEDIUM 可以：

```text
Accept
Defer
Create Debt
```

但必须显式决策。

---

### 3.3.9 输出指标

建议至少输出：

```text
Total Requirements
Total Tasks
Requirement Coverage %
AC Coverage %
Ambiguity Count
Duplication Count
Inconsistency Count
Unmapped Task Count
Critical Issues
High Issues
```

并生成：

```text
Requirement → Task Coverage Table
```

例如：

| Requirement | Has Task | Task IDs | Verdict |
|---|---|---|---|
| FR-001 | Yes | T001,T005 | Covered |
| FR-002 | Yes | T012 | Partial |
| FR-003 | No | - | Gap |

---

### 3.3.10 Read-only 原则与问题回流机制

官方 Analyze 明确采用 **Strictly Read-only**。

这是非常值得借鉴的设计。

原因是：

> 检查者不应该在检查过程中悄悄改变被检查对象，从而让证据链消失。

正确流程：

```text
Analyze
   ↓
Finding
   ↓
Owner Classification
   ↓
Spec issue → 回到 Spec / Clarify
Plan issue → 回到 Plan
Task issue → 回到 Tasks
   ↓
Fix
   ↓
Analyze Again
```

形成：

```text
Detect ≠ Repair
```

这对于建立可信 Gate 非常重要。

---

## 3.4 Q4 Converge：实现一致性门

### 3.4.1 目标

Converge 的核心目标：

> **检查当前代码库与 Spec / Plan / Tasks 所声明意图之间还有哪些差距。**

它不是：

```text
Git Diff Review
```

而是：

```text
Declared Intent
      ↓
Current Code
      ↓
Gap
```

因此它关注：

> 当前状态是否满足意图。

而不是：

> 这次 Commit 改了什么。

---

### 3.4.2 Intent Inventory

Converge 首先建立 Intent Inventory。

来源包括：

- FR；
- Buildable SC；
- User Story Acceptance Scenario；
- Plan Decision；
- Constitution MUST / buildable constraint。

例如：

```text
FR-001 上传文件
FR-002 网络恢复续传
US1/AC3 用户取消后不得恢复
PLAN-003 使用WorkManager
CONST-002 所有后台任务必须可观测
```

这一步非常重要，因为没有 Intent Inventory 就无法系统判断 Code Gap。

---

### 3.4.3 Intent → Code Mapping

下一步是建立：

```text
Intent
  ↓
Code Scope
  ↓
Evidence
```

Code Scope 主要来自：

- Plan 中声明的组件 / 文件；
- Tasks 中引用的文件；
- Requirement 关键词所定位的相关代码。

例如：

```text
FR-002
 ↓
UploadWorker.kt
CheckpointStore.kt
UploadRepository.kt
```

---

### 3.4.4 Code Evidence

每个 Finding 都应该有可检查证据。

例如：

```yaml
finding:
  id: F-012
  source: FR-002
  type: partial
  evidence:
    - UploadWorker.kt
    - CheckpointStore.kt
  summary: 网络恢复存在，但没有恢复上传分片位置
```

Evidence 的价值在于：

> 把“LLM 认为不对”转化为“可以由人复核的工程判断”。

---

### 3.4.5 四类实现 Gap

#### Missing

声明要求完全没有实现。

```text
Intent: 必须保存checkpoint
Code: 无checkpoint逻辑
```

#### Partial

实现存在，但没有完整满足要求。

```text
Intent: 最大重试3次
Code: 只实现了单次retry
```

#### Contradicts

代码行为与 Intent 相反。

```text
Intent: 用户取消后不得自动上传
Code: 网络恢复后仍然自动重新enqueue
```

#### Unrequested

代码实现了没有被 Spec / Plan / Tasks 请求的行为。

例如：

```text
自动上传诊断日志
```

但需求和设计都没有说明。

Unrequested 不一定错误，但必须：

```text
Justify
Document
or Remove
```

它实际上提供了很好的 Scope Creep 监控能力。

---

### 3.4.6 Severity 模型

建议：

#### CRITICAL

- Constitution MUST 被代码违反；
- P1 核心功能 Missing；
- 核心行为 Contradicts；
- 数据安全 / 丢失风险。

#### HIGH

- Core FR Missing；
- Core AC Partial；
- 核心异常场景未实现。

#### MEDIUM

- Secondary Requirement Partial；
- 非关键 Unrequested；
- 非核心 NFR 不完整。

#### LOW

- Minor Gap；
- Polish；
- Low-risk Unrequested。

---

### 3.4.7 Convergence Tasks 生成机制

官方 Converge 最有特点的设计是：

> **不直接改代码。**

其唯一写操作是：

```text
Append new Convergence Phase to tasks.md
```

例如：

```md
## Phase 6: Convergence

- [ ] T042 Implement checkpoint resume required by FR-008
- [ ] T043 Fix cancellation behavior required by US2/AC3
- [ ] T044 Review unrequested diagnostics upload and justify or remove
```

然后再次：

```text
Implement
   ↓
Converge
```

形成迭代闭环：

```text
Intent
 ↓
Implementation
 ↓
Converge
 ↓
Remaining Tasks
 ↓
Implementation
 ↓
Converge
```

---

### 3.4.8 准入与准出标准

#### Entry

至少：

```text
spec.md
plan.md
tasks.md
current code
```

并且当前 tasks 已经过 Implementation。

#### Exit

建议自有 Gate：

```text
CRITICAL Implementation Gap = 0
HIGH Implementation Gap = 0
Core FR Missing = 0
Core AC Contradiction = 0
Unjustified High-risk Unrequested = 0
```

最终状态：

```text
Converged
```

其含义应该是：

> **在当前声明的意图范围内，没有剩余的阻断级实现差距。**

不是：

> 产品没有任何 Bug。

---

### 3.4.9 Converge 与 Code Review / Diff Analysis 的区别

这是自有 Gate2 中必须明确的边界。

#### Code Review

核心问题：

```text
这次代码改得好不好？
```

关注：

- coding defect；
- maintainability；
- API misuse；
- architecture；
- security；
- readability；
- concurrency；
- resource management。

#### Diff Analysis

核心问题：

```text
这次 Change 影响了什么？
```

关注：

```text
Changed Code
→ Impact Scope
→ Regression Risk
```

#### Converge

核心问题：

```text
当前代码是否满足声明意图？
```

关注：

```text
Intent
→ Code Evidence
→ Gap
```

所以三者互补：

```text
Converge      = Intent Fidelity
Code Review   = Engineering Correctness
Impact Scan   = Change Risk
```

不能互相替代。

---

### 3.4.10 Converged 的定义

推荐自有 Gates 将 Converged 定义为：

```text
所有 Blocker Intent 均找到充分 Code Evidence；
没有 Critical / High Missing、Partial、Contradicts；
高风险 Unrequested 已获得决策；
所有剩余问题均已明确接受、延期或转为 Debt。
```

注意：

> Converged 是“意图与实现收敛”，不是整个软件质量完成。

还需要：

- Static Analysis；
- Unit Test；
- API / Integration Test；
- Scenario Validation；
- Performance；
- Security；
- Runtime Evidence；
- Release Guard。

---

# 4. 四层之间的关系、重叠与防重复机制

## 4.1 Clarify 与 Checklist 的区别

这是最容易发生重复的两层。

### Clarify

问：

> **到底想要什么？**

问题本质：

```text
Decision Unknown
```

例如：

```text
网络恢复后“继续上传”
```

“继续”是：

- 从头重传；
- checkpoint resume；
- 用户手动操作？

需要决策。

---

### Checklist

问：

> **即便已经知道想要什么，要求本身是否定义充分？**

假设已经明确：

```text
网络恢复后从checkpoint自动续传。
```

Checklist 继续发现：

```text
是否定义连续失败最大次数？
是否定义用户取消优先级？
是否定义认证过期？
是否定义checkpoint失效？
```

问题本质：

```text
Requirement Coverage / Quality Gap
```

因此：

```text
Clarify   = Resolve Unknown
Checklist = Validate Requirement Quality
```

---

## 4.2 Checklist 与 Analyze 的区别

### Checklist

检查：

```text
Requirement 本身好不好？
```

例如：

```text
是否定义上传最大文件大小？
```

### Analyze

检查：

```text
已经定义的 Requirement 是否进入 Plan / Tasks？
```

例如：

```text
FR-010 最大文件大小2GB
         ↓
Plan ?
         ↓
Task ?
```

因此：

```text
Checklist = Horizontal Specification Quality
Analyze   = Vertical Artifact Traceability
```

---

## 4.3 Analyze 与 Converge 的区别

Analyze：

```text
Spec
 ↓
Plan
 ↓
Tasks
```

Converge：

```text
Spec / Plan / Tasks
        ↓
       Code
```

例如：

```text
FR-008 → Plan → T012
```

Analyze 可以判定：

```text
Covered
```

但是实际代码：

```text
T012 标记完成
但功能根本没有正确实现
```

只有 Converge 才能发现。

所以：

```text
Analyze 解决 “计划上有没有”
Converge解决 “事实上有没有”
```

---

## 4.4 为什么相同问题可能在不同层被再次发现

例如：

```text
“快速完成上传”
```

Clarify 可以发现：

> “快速是多少？”

Checklist 可以发现：

> AC 不可测。

Analyze 可以发现：

> Performance Requirement 仍然模糊。

Converge 甚至可能发现：

> 没有任何性能实现证据。

这不是四层设计失败。

真正的问题在于：

> **谁拥有这个 Finding？**

应该统一归类：

```text
Requirement Decision / Quality Finding
```

并回流到 Requirement Owner。

因此需要区分：

```text
Detection Layer
≠
Ownership Layer
```

---

## 4.5 Finding Owner 原则

建议规则：

### Rule 1

如果问题需要改变：

```text
业务决策
```

Owner = Clarify。

### Rule 2

如果问题需要改变：

```text
Requirement 描述
```

Owner = Checklist / Spec。

### Rule 3

如果问题需要改变：

```text
Plan / Task 映射
```

Owner = Analyze 对应 Artifact。

### Rule 4

如果 Spec / Plan / Task 不需要改变，只需要：

```text
修改实现
```

Owner = Converge / Implementation。

---

## 4.6 问题回流机制

推荐：

```text
Finding
   ↓
Classify Root Layer
   ↓
┌─────────────┬──────────────┬─────────────┬──────────────┐
│ Clarify     │ Checklist    │ Analyze     │ Converge     │
│ Decision    │ Requirement  │ Artifact    │ Code         │
└──────┬──────┴──────┬───────┴──────┬──────┴──────┬───────┘
       │             │              │             │
       ↓             ↓              ↓             ↓
     Spec          Spec          Plan/Tasks      Code
       │             │              │             │
       └─────────────┴──────────────┴─────────────┘
                           ↓
                     Re-evaluate Gate
```

---

## 4.7 四层统一分类模型

可以统一成四大类：

### Class A：Decision Unknown

问题：

> 还没有做出必要决策。

Owner：

```text
Clarify
```

### Class B：Requirement Quality Gap

问题：

> 已有意图，但规格表达不完整/不明确/不可验证。

Owner：

```text
Checklist / Spec Quality
```

### Class C：Artifact Mapping Gap

问题：

> Requirement 在 Plan / Tasks 转换过程中丢失、冲突或孤立。

Owner：

```text
Analyze
```

### Class D：Implementation Gap

问题：

> Code 没有兑现声明意图。

Owner：

```text
Converge
```

这四类可以直接成为自有 Gates 的一级 Finding Taxonomy。

---

## 4.8 四层统一准出模型

所有 Gate 统一采用：

```text
Input
 ↓
Inspection
 ↓
Finding
 ↓
Severity
 ↓
Evidence
 ↓
Decision
 ↓
Verdict
```

Verdict 建议统一：

```text
PASS
PASS_WITH_WARNINGS
BLOCK
NOT_READY
```

### PASS

无阻断项。

### PASS_WITH_WARNINGS

只有已接受的 Medium / Low Finding。

### BLOCK

存在 Critical / High 必须修复项。

### NOT_READY

输入 Artifact 不满足 Entry Criteria。

---

## 4.9 四层质量链路示意

```text
                    ┌─────────────────────┐
                    │ Business Intent     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Q1 Clarify          │
                    │ Decision Unknown    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Q2 Checklist        │
                    │ Requirement Quality │
                    └──────────┬──────────┘
                               │
                               ▼
                     Spec / Plan / Tasks
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Q3 Analyze          │
                    │ Artifact Alignment  │
                    └──────────┬──────────┘
                               │
                               ▼
                         Implementation
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Q4 Converge         │
                    │ Intent Fidelity     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Verification / Gate │
                    └─────────────────────┘
```

---

# 5. 对自有 Gates 体系的借鉴与映射

## 5.1 Spec Kit 可直接借鉴的设计

### 1. 分层检查，而不是万能 Reviewer

不同阶段解决不同类型问题。

### 2. Intent Inventory

把自然语言 Requirement 转换成可映射的稳定意图项。

### 3. Finding Type 明确分类

尤其 Converge：

```text
missing
partial
contradicts
unrequested
```

非常适合实现级 Gap。

### 4. Read-only Analysis

检查过程不自动偷偷修复。

### 5. Severity

不是“发现问题数量”，而是基于风险做 Gate。

### 6. Append-only Remediation

Finding → 新 Task，而不是修改历史 Task。

### 7. Evidence

每个实现 Gap 必须有 Code Evidence。

### 8. Constitution Authority

把组织级原则作为高优先约束。

---

## 5.2 不建议直接复制的部分

### 1. 不应只依赖自然语言 Agent 判断

企业级 Gate 需要增加：

- structured schema；
- deterministic rule；
- repository fact；
- build/test evidence。

### 2. 不应把 Coverage 当成充分条件

```text
Requirement → Task
```

只是第一层 Traceability。

### 3. Converge 不能替代 Code Review

Intent 对齐和工程正确性是两个问题。

### 4. Checklist 不能变成无限问题生成

需要 Risk Budget 和重点领域优先级。

### 5. Clarify 的问题数限制只是交互策略

“最多 5 个问题”适合对话体验，但自有 Gate 不应把：

```text
5 questions
```

误认为质量充分性的数学标准。

真正标准应是：

```text
Critical Unknown 是否关闭。
```

---

## 5.3 自有 Gate1 与 Spec Kit 的映射

自有 Gate1 目标通常是：

> **Engineering Ready / Requirement Ready**

可以吸收：

```text
Clarify
+
Checklist
+
Analyze中的需求侧一致性能力
```

### 5.3.1 Clarify 能力

用于检查：

- Unknown；
- Assumption；
- Scenario Policy；
- State；
- Rule；
- Data；
- NFR Target；
- Dependency Failure。

输出：

```text
Decision Ledger
```

### 5.3.2 Checklist 能力

用于检查：

```text
Completeness
Clarity
Consistency
Measurability
Scenario Coverage
Edge Case
NFR
Dependency
```

输出：

```text
Spec Quality Findings
```

### 5.3.3 Analyze 中需求侧能力

如果 Gate1 阶段已经存在：

- architecture draft；
- allocation；
- interface draft；

可以检查：

```text
Requirement → Architecture
Requirement → Verification Objective
```

但不要把完整 Task Coverage 强行提前到需求阶段。

---

## 5.4 自有 Gate2 与 Spec Kit 的映射

Gate2 目标通常是：

> **Development Ready / Coding Exit / Implementation Quality**

可吸收：

```text
Analyze
+
Converge
+
Code Review
+
Static Analysis
+
Test Evidence
```

### 5.4.1 Analyze 中开发侧能力

检查：

```text
Requirement → Plan
Plan → Task
Requirement → Task
```

回答：

> 是否都计划到了？

### 5.4.2 Converge 能力

检查：

```text
Intent → Current Code
```

回答：

> 是否真的做到了？

### 5.4.3 Code Review / Static Analysis / Test 的补充关系

完整 Gate2 应该是：

```text
                 ┌──────────────┐
                 │   Analyze    │
                 │ Plan/Task对齐 │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Converge   │
                 │ Intent→Code  │
                 └──────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     Code Review    Static Scan      Tests
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                    Evidence
                        ▼
                     Verdict
```

---

## 5.5 建议的统一 Finding Model

建议自有 Gates 使用两层分类。

### Level 1：Root Category

```text
DECISION
REQUIREMENT
ARTIFACT
IMPLEMENTATION
ENGINEERING
VERIFICATION
```

### Level 2：Finding Type

示例：

```yaml
finding:
  id: F-001
  root_category: REQUIREMENT
  type: SCENARIO_COVERAGE_GAP
  severity: HIGH
  source: FR-008
  evidence:
    - spec.md#FR-008
  owner: requirement
  status: open
```

这样以后可以兼容：

- Clarify；
- Checklist；
- Analyze；
- Converge；
- CR；
- Test；
- Runtime。

---

## 5.6 建议的 Severity Model

Severity 不应该由“哪个工具发现”决定。

建议统一基于：

```text
Severity
≈ Impact × Likelihood × Detectability / Recoverability
```

工程上可以简化：

### CRITICAL

- 数据丢失；
- 安全/隐私严重风险；
- Constitution MUST；
- 核心功能完全缺失；
- 无法发布。

### HIGH

- 核心 Requirement 未满足；
- 主要场景错误；
- 重要状态 / Rule 冲突；
- 高概率用户可见问题。

### MEDIUM

- 次要场景；
- 可降级问题；
- 非核心 NFR；
- 可接受技术债。

### LOW

- 文案；
- 小范围一致性；
- 低风险优化。

---

## 5.7 建议的 Entry / Exit Criteria

### Gate1 Entry

```text
Business Goal exists
Feature Scope exists
Core Stories exist
Initial Requirements exist
```

### Gate1 Exit

```text
Critical Unknown = 0
Critical Requirement Gap = 0
Core Scenario / State / Rule defined
Core AC testable
Critical Dependency known
Critical NFR defined
```

### Gate2 Entry

```text
Gate1 PASS
Plan available
Tasks available
Implementation available
```

### Gate2 Exit

```text
Analyze CRITICAL/HIGH = 0
Core Requirement Task Coverage = 100%
Converge CRITICAL/HIGH = 0
Required Static Checks PASS
Required Tests PASS
Evidence complete
```

---

## 5.8 建议的 Evidence 与 Traceability 模型

推荐统一链：

```text
Story
 ↓
AC
 ↓
Scenario
 ↓
Rule / State / Data
 ↓
Requirement
 ↓
Plan Decision
 ↓
Task
 ↓
Code
 ↓
Test / Static / Review Evidence
 ↓
Verdict
```

每个节点拥有稳定 ID。

例如：

```text
US-001
 AC-001
  SCN-001
   RULE-003
    FR-008
     PLAN-012
      T-033
       CODE: UploadWorker.kt
        TEST: UploadResumeTest
         EVIDENCE: CI#1023
```

这样 Gate 才能从“AI 评审”升级为：

> **可追踪的质量决策系统。**

---

## 5.9 Spec Kit 能力之外仍需补充的质量能力

Spec Kit 四层主要覆盖“意图到实现”的一致性。

自有 Gates 仍然需要补充：

### 1. Feasibility / Technical Discovery

在深度需求澄清前回答：

```text
技术上可不可行？
关键平台限制是什么？
外部系统允许吗？
```

### 2. Architecture Quality

例如：

- coupling；
- scalability；
- recovery；
- fault isolation；
- backward compatibility。

### 3. Change Impact Analysis

```text
Diff
→ Impact Anchor
→ Feature / Scenario
→ Risk
→ Regression Tests
```

### 4. Code Review

检查 Implementation Engineering Quality。

### 5. Static Analysis

Lint / SAST / API misuse / concurrency / resource。

### 6. Verification

- UT；
- API Test；
- Scenario Test；
- System Test。

### 7. Runtime / Observability

静态检查无法证明：

- 真机性能；
- 流量；
- 容量；
- 云依赖；
- 灰度行为。

### 8. Validation

最终还要回答：

> **做出来的东西是否真正满足业务和用户目标？**

而不仅仅是：

> Spec 是否被忠实实现。

---

# 6. 建议的自有 Gates 参考框架

## 6.1 总体原则

建议自有 Gates 不以“工具”为一级结构，而以质量问题为结构：

```text
Gate1：Specification Assurance
Gate2：Implementation Assurance
Gate3：Scenario / Acceptance Assurance
Gate4：Release / Runtime Assurance
```

Spec Kit 四层作为 Gate1 / Gate2 的重要参考能力。

---

## 6.2 四层质量问题模型

可以正式沉淀为：

```text
┌───────────────────────────┐
│ 1. Decision Unknown       │
│ 我们到底要什么还没决定    │
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ 2. Requirement Quality Gap│
│ 意图已定，但规格不充分     │
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ 3. Artifact Mapping Gap   │
│ 工程转换过程中意图丢失     │
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ 4. Implementation Gap     │
│ 代码没有兑现声明意图       │
└───────────────────────────┘
```

这是本次调查最值得借鉴的核心。

---

## 6.3 标准检查矩阵

| Layer | Target | Method | Finding | Evidence | Owner |
|---|---|---|---|---|---|
| Q1 Clarify | Spec Decision | Coverage + Questioning | Unknown | Decision/Spec | Product/Requirement |
| Q2 Checklist | Requirement Quality | Quality Checklist | Requirement Gap | Spec Reference | Requirement |
| Q3 Analyze | Spec/Plan/Tasks | Semantic Mapping | Artifact Gap | Mapping Table | Architect/Dev |
| Q4 Converge | Code | Intent-to-Code Assessment | Implementation Gap | Code Evidence | Developer |

---

## 6.4 Gate 准出判定模型

不建议：

```text
Score > 80 → Pass
```

推荐：

```text
Hard Rules
+
Severity Findings
+
Evidence Completeness
+
Accepted Risk
```

判定：

```text
IF required_artifact_missing:
    NOT_READY
ELSE IF critical > 0:
    BLOCK
ELSE IF high > 0:
    BLOCK
ELSE IF accepted_medium > 0:
    PASS_WITH_WARNINGS
ELSE:
    PASS
```

---

## 6.5 Finding → Decision → Task → Evidence 闭环

一个成熟 Gate 不应止于 Finding。

推荐：

```text
Finding
   ↓
Root Cause Layer
   ↓
Decision
   ↓
Remediation Task
   ↓
Implementation
   ↓
Evidence
   ↓
Recheck
   ↓
Close
```

Finding Schema 示例：

```yaml
id: F-023
gate: G2
source: FR-008
category: IMPLEMENTATION
type: PARTIAL
severity: HIGH

summary: >
  网络恢复逻辑存在，但未从checkpoint恢复上传位置。

evidence:
  - src/upload/UploadWorker.kt
  - src/upload/CheckpointStore.kt

decision: fix
owner: upload-team

remediation:
  task: T-052

verification:
  required:
    - code-evidence
    - unit-test
    - scenario-test

status: open
```

---

## 6.6 推荐落地优先级

建议不要一次实现全部能力。

### Phase 1：建立统一 Finding Model

首先统一：

```text
Decision Unknown
Requirement Gap
Artifact Gap
Implementation Gap
```

否则不同 Skill 会产生大量重复 Finding。

### Phase 2：建立 Intent Inventory

为：

```text
Story / AC / Requirement / Rule / State / Data
```

建立稳定 ID。

### Phase 3：实现 Gate1

优先：

```text
Clarify
+
Checklist
```

目标：

> Engineering Ready。

### Phase 4：实现 Analyze

建立：

```text
Requirement → Plan → Task
```

Traceability。

### Phase 5：实现 Converge

建立：

```text
Intent → Code Evidence
```

### Phase 6：接入现有工程质量能力

```text
Code Review
Static Analysis
Unit Test
API Test
Scenario Test
```

### Phase 7：统一 Verdict

形成：

```text
Gate Report
+
JSON
+
Evidence Chain
```

---

## 6.7 最终参考架构

建议最终形成：

```text
                         Business Goal
                              │
                              ▼
                    ┌──────────────────┐
                    │ Domain / Tech    │
                    │ Feasibility      │
                    └────────┬─────────┘
                             │
                             ▼
╔════════════════════════════════════════════════════════════╗
║ Gate1 — Specification Assurance                          ║
║                                                          ║
║  Clarify                                                  ║
║  Decision Unknown                                         ║
║      ↓                                                    ║
║  Checklist                                                ║
║  Requirement Quality Gap                                  ║
╚═══════════════════════╤════════════════════════════════════╝
                        │
                        ▼
                 Architecture / Plan
                        │
                        ▼
                      Tasks
                        │
                        ▼
╔════════════════════════════════════════════════════════════╗
║ Gate2 — Implementation Assurance                         ║
║                                                          ║
║  Analyze                                                  ║
║  Artifact Mapping Gap                                     ║
║      ↓                                                    ║
║  Implement                                                ║
║      ↓                                                    ║
║  Converge                                                 ║
║  Implementation Gap                                       ║
║      ↓                                                    ║
║  CR + Static + UT + API Test                              ║
╚═══════════════════════╤════════════════════════════════════╝
                        │
                        ▼
╔════════════════════════════════════════════════════════════╗
║ Gate3 — Scenario / Acceptance Assurance                  ║
║ Scenario / AC / Risk / Cross-feature Verification        ║
╚═══════════════════════╤════════════════════════════════════╝
                        │
                        ▼
╔════════════════════════════════════════════════════════════╗
║ Gate4 — Release / Runtime Assurance                      ║
║ Device / Traffic / Capacity / Observability / Rollback   ║
╚════════════════════════════════════════════════════════════╝
```

本报告对 Spec Kit 的最终评价是：

> Spec Kit 最值得借鉴的并不是四个命令本身，而是它已经隐含建立了一条从“未决策需求”到“代码实现差距”的分层质量链。自有 Gates 应进一步把这种链路工程化：建立统一 Finding Taxonomy、稳定 Intent ID、Evidence、Severity、Entry/Exit Criteria 和可闭环的 Verdict。

---

# 附录

## A. 四层质量门对比表

| 维度 | Clarify | Checklist | Analyze | Converge |
|---|---|---|---|---|
| 主要对象 | Spec | Requirement Quality | Spec/Plan/Tasks | Intent/Code |
| 生命周期 | Plan 前 | 灵活，推荐 Spec Quality 阶段 | Tasks 后 Implement 前 | Implement 后 |
| 主要目标 | 消除未知决策 | 验证规格质量 | 跨制品一致性 | 实现忠实度 |
| 主 Finding | Unknown | Requirement Gap | Artifact Gap | Implementation Gap |
| 是否写文件 | 更新 Spec | 生成/追加 Checklist | 否，Read-only | 只追加 Tasks |
| 是否检查代码 | 否 | 否 | 否 | 是 |
| 是否负责修复 | 通过决策修改 Spec | Reviewer 处理 | 否 | 不改代码 |
| 典型退出 | Critical Unknown=0 | Critical Req Gap=0 | Critical/High=0 | Critical/High Gap=0 |

---

## B. Finding Type 对照表

| Layer | Finding Type |
|---|---|
| Clarify | UNKNOWN_DECISION |
| Clarify | AMBIGUOUS_DECISION |
| Clarify | UNRESOLVED_ASSUMPTION |
| Checklist | MISSING_REQUIREMENT |
| Checklist | UNCLEAR_REQUIREMENT |
| Checklist | UNTESTABLE_REQUIREMENT |
| Checklist | INCONSISTENT_REQUIREMENT |
| Checklist | SCENARIO_COVERAGE_GAP |
| Checklist | EDGE_CASE_GAP |
| Checklist | NFR_GAP |
| Analyze | UNMAPPED_REQUIREMENT |
| Analyze | UNMAPPED_TASK |
| Analyze | SPEC_PLAN_CONFLICT |
| Analyze | PLAN_TASK_CONFLICT |
| Analyze | TERMINOLOGY_DRIFT |
| Analyze | CONSTITUTION_VIOLATION |
| Converge | MISSING |
| Converge | PARTIAL |
| Converge | CONTRADICTS |
| Converge | UNREQUESTED |

---

## C. Severity 对照表

| Severity | 建议定义 | Gate |
|---|---|---|
| CRITICAL | 核心功能、安全、数据、强制原则，不能继续 | BLOCK |
| HIGH | 核心 Requirement / AC 明显缺失或错误 | BLOCK |
| MEDIUM | 次要场景、NFR、可接受风险 | PASS_WITH_WARNING / Decision |
| LOW | 文案、轻微一致性、优化项 | PASS |

---

## D. Entry / Exit Criteria 对照表

| Gate | Entry | Exit |
|---|---|---|
| Clarify | 初始 Spec | Critical Unknown=0 |
| Checklist | 基本确定的 Requirement | Critical Requirement Gap=0 |
| Analyze | Spec+Plan+Tasks | Critical/High=0，核心 Coverage=100% |
| Converge | 已实现代码 + Artifacts | Critical/High Implementation Gap=0 |

---

## E. 示例：文件上传需求的四层评估过程

初始需求：

```text
用户可以将文件上传到云端。
```

### E.1 Clarify

发现：

```text
上传过程中网络中断后怎么办？
```

决策：

```text
网络恢复后从最近checkpoint自动续传。
```

结果：

```text
Decision Unknown → Resolved
```

---

### E.2 Checklist

继续检查：

```text
是否定义最大重试次数？
是否定义用户取消后的行为？
是否定义认证过期？
是否定义checkpoint失效？
是否定义同名文件处理？
```

发现：

```text
用户取消与自动恢复优先级没有定义。
```

结果：

```text
Requirement Quality Gap
```

修复：

```text
用户主动取消后，该上传任务进入Cancelled，
网络恢复不得自动重新启动。
```

---

### E.3 Analyze

Spec：

```text
FR-008 网络恢复后自动从checkpoint续传
FR-009 用户取消后不得恢复
```

Plan：

```text
WorkManager
CheckpointStore
```

Tasks：

```text
T012 Create UploadWorker
T013 Network Constraint
```

Analyze：

```text
FR-008 → Task Partial
```

原因：

```text
没有任何 Task 负责保存/加载checkpoint。
```

结果：

```text
Artifact Mapping Gap
```

---

### E.4 Converge

Task 修复并实施后：

Code：

```text
UploadWorker
CheckpointStore
```

检查：

```text
FR-009 用户取消后不得恢复
```

Code 实际：

```text
网络恢复后所有未完成任务都会重新enqueue，
包括Cancelled任务。
```

Finding：

```yaml
type: contradicts
severity: HIGH
source: FR-009
```

结果：

```text
Implementation Gap
```

修复后重新 Converge：

```text
Converged
```

这说明同一个 Feature 在四个阶段发现的是四种完全不同的问题：

```text
Clarify   → 不知道该怎么做
Checklist → 该定义的没定义
Analyze   → 定义了但任务没承接
Converge  → 任务有了但代码做错
```

---

## F. Spec Kit 官方命令与产物关系表

| Command | 主要作用 | 主要输入 | 主要输出 |
|---|---|---|---|
| `speckit.specify` | 建立 Feature Spec | 用户目标 | spec.md |
| `speckit.clarify` | 解决未充分定义区域 | spec.md | 更新 spec.md |
| `speckit.plan` | 技术实现规划 | spec.md | plan.md / data-model / contracts 等 |
| `speckit.checklist` | 生成 Requirement Quality Checklist | Feature Context | checklists/*.md |
| `speckit.tasks` | 生成可执行任务 | spec + plan | tasks.md |
| `speckit.analyze` | 跨 Artifact 一致性 / Coverage | spec+plan+tasks | 分析报告 |
| `speckit.implement` | 执行任务 | tasks | code |
| `speckit.converge` | 当前代码与意图收敛 | artifacts + code | Findings + Convergence Tasks |

---

# 参考资料

以下内容以 2026-09-08 GitHub `github/spec-kit` 主分支为准：

1. Spec Kit README  
   https://github.com/github/spec-kit/blob/main/README.md

2. Clarify command template  
   https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md

3. Checklist command template  
   https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md

4. Analyze command template  
   https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md

5. Converge command template  
   https://github.com/github/spec-kit/blob/main/templates/commands/converge.md

6. Plan command template  
   https://github.com/github/spec-kit/blob/main/templates/commands/plan.md

7. Tasks template  
   https://github.com/github/spec-kit/blob/main/templates/tasks-template.md

---

# 结论摘要

Spec Kit 四种质量能力可以抽象为：

```text
Clarify
= 决策确定性

Checklist
= 规格自身质量

Analyze
= 工程制品传递质量

Converge
= 实现忠实度
```

推荐自有 Gates 最终不要复制四个命令，而是建立四个稳定质量问题域：

```text
1. Decision Unknown
2. Requirement Quality Gap
3. Artifact Mapping Gap
4. Implementation Gap
```

并统一采用：

```text
Intent ID
→ Finding
→ Severity
→ Evidence
→ Owner
→ Remediation Task
→ Verification
→ Verdict
```

从而把 AI 的“审查意见”升级为可追踪、可判定、可闭环的软件质量门禁体系。
