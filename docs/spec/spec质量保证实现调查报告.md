# Spec 质量保证实现调查报告

> 调查时间：2026-09-08  
> 主题：利用 AI Agent 对软件需求（Spec）进行细化、澄清、挑战与质量保证，并形成可工程化的实现方案。

---

# 1. 背景、目标与调查范围

## 1.1 背景

在 AI Coding / Agentic Software Engineering 中，一个常见问题是：**Agent 在需求信息不充分时仍然会快速进入设计和编码**。这会把需求阶段尚未解决的模糊、遗漏、假设和冲突带入架构、任务和代码，最终形成高成本返工。

传统的“需求澄清”通常采用人工评审、问答列表、PRD 补充或 Acceptance Criteria 细化。引入 AI Agent 后，需求澄清能力显著增强：Agent 可以阅读代码和文档、主动研究技术事实、持续追问、构建领域模型、展开场景、生成反例并进行一致性检查。

但新的问题随之出现：

1. **不同 Agent / Skill 在做重复的事情**：Discovery、Clarify、Domain Modeling、Scenario、Challenge 都可能发现同一个问题。
2. **所有 Unknown 都被当成人工问答**：本应由 Agent 自己查证的技术事实也被抛给用户。
3. **Scenario 与 Challenge 职责不清**：两者都在不断 Brainstorm 边界条件和异常场景。
4. **Challenge 与 Quality Gate 职责不清**：两者都在发现遗漏、矛盾和不可验证问题。
5. **多份 Artifact 保存相同事实**：`unknowns.md`、`decisions.md`、`rules.md`、`spec.md` 容易产生重复和不一致。
6. **把本应循环运行的能力设计成流水线阶段**：一次回答就可能改变后续全部决策空间，使前面建立的模型迅速过期。

因此，需要解决的已不只是“如何让 Agent 多问几个问题”，而是：

> **如何建立一套围绕统一 Requirement Model 运行的 Spec Quality Assurance System，使 AI Agent 能够发现事实、建模行为、消除不确定性、攻击关键假设，并最终判断 Spec 是否达到 Engineering Ready。**

---

## 1.2 调查目标

本文重点回答五个问题：

1. 目前业界有哪些适用于 AI Agent 的需求发现、澄清和 Spec 质量保证方法？
2. 这些方法分别解决哪类需求不确定性（Unknown）？
3. 如果将它们组合在一起，哪些能力会产生重复？
4. 如何重新划分职责，使各能力尽量正交？
5. 如何将这一思路实现为可运行的 Agent / Skill / Requirement Model？

本文关注的是 **Coding 之前的 Spec Quality**，主要目标包括：

- 完整性（Completeness）
- 清晰性（Clarity）
- 一致性（Consistency）
- 可验证性（Verifiability）
- 可追溯性（Traceability）
- 现实约束适配（Reality / Feasibility Alignment）
- 未决问题闭环（Unknown / Decision Closure）

代码是否正确实现 Spec 属于后续 Implementation Conformance / Convergence 范围，不是本文的核心对象。

---

## 1.3 调查观察：业界正在从“写完整 Prompt”转向“决策发现工作流”

从 2025～2026 年的 Agentic Software Engineering 实践看，需求工作正在出现三个明显变化。

### 变化一：在 Specify 之前增加 Discovery / Assessment

GitHub Spec Kit 当前提供独立的 `assess` 扩展，在 Spec-Driven Development 之前执行：

```text
Idea
  ↓
Intake
  ↓
Research
  ↓
Define
  ↓
Shape
  ↓
Decide
  ↓
GO / NEEDS CLARIFICATION / KILL
  ↓
Specify
```

其核心思想是：在投入规格化和实现之前，先获得支持或反对该想法的证据，并确认问题、目标和方案边界。

### 变化二：把“问用户”改为“根据 Unknown 类型选择求解方式”

Matt Pocock 的 Wayfinder / Grilling 体系将阻塞决策的工作区分为：

- Research：Agent 自己调查事实；
- Grilling：需要真正的人来作出业务/产品决策；
- Prototype：语言讨论不足以解决时，用低成本原型提升讨论精度；
- Task：需要先完成某项外部动作才能继续决策。

这意味着需求澄清不再等于 Question List，而更接近：

```text
Unknown
  ↓
Classify
  ↓
Research / Ask / Prototype / Model
  ↓
Resolution
```

### 变化三：用具体 Example 和 Domain Language 发现隐藏需求

BDD / Example Mapping 强调：抽象的 Story 或 Rule 很容易看起来“正确”，而具体 Example 会暴露上下文、边界条件、隐藏假设和不同 Outcome。

Example Mapping 将讨论中的信息显式分类为：

```text
Story
Rules
Examples
Questions
```

这与 Agent 的 Requirement Model 非常契合：Agent 不只是生成 Given/When/Then，而是通过 Example 反向发现 Rule、Unknown 和新 Scenario。

---

# 2. AI Agent 需求澄清与 Spec 质量方法调查

本章不按工具名称简单罗列，而按照“它主要消除哪一种不确定性”进行分类。

## 2.1 Reality / Evidence Discovery：先弄清现实世界

### 2.1.1 主要目的

回答：

> **当前现实到底是什么？原始诉求所依赖的技术、业务和系统事实是否成立？**

典型调查对象包括：

- 当前代码与已有行为；
- 系统架构与组件边界；
- 第三方 API 与平台能力；
- Android / iOS / Web 平台限制；
- 安全、隐私、合规政策；
- 历史设计决策；
- 业务政策和组织约束；
- 已知失败模式；
- 原始需求中的 Assumption 是否有证据支撑。

### 2.1.2 代表性实践

**Spec Kit Assess** 将 Discovery 独立放在 SDD 前面，执行 `intake → research → define → shape → decide`，最后输出 go / needs-clarification / kill。

**Agent-Assisted Discovery** 一类实践则要求 Agent 在修改系统之前先建立局部心智模型：阅读代码、架构、依赖和现有行为，减少基于想象直接设计的风险。

### 2.1.3 最重要的工程原则

**Fact Unknown 不应默认询问用户。**

例如：

```text
Android 后台是否允许某行为？
微信是否提供指定 API？
当前代码是否已经实现重试？
某接口是否具备幂等能力？
```

这类问题应该优先通过文档、代码、实验或外部研究解决。

建议输出统一的事实账本：

```yaml
facts:
  - id: F-001
    statement: "..."
    evidence: "..."
    confidence: high

constraints:
  - id: C-001
    statement: "..."
    source: "..."
```

而不是分别维护 `feasibility.md`、`technical-facts.md`、`context-findings.md` 三套重复事实。

---

## 2.2 Interactive Clarification：针对真正需要人的决策进行求解

### 2.2.1 Socratic / Adaptive Grilling

其重点不是“列出所有问题”，而是：

1. 根据当前模型识别最重要的 Unknown；
2. 一次解决一个关键问题；
3. 前一个答案改变模型；
4. 重新计算下一步应该问什么。

因此更合理的形式是：

```text
Current Model
    ↓
Unresolved Decisions
    ↓
Rank by impact / dependency
    ↓
Select one
    ↓
Ask
    ↓
Record Decision
    ↓
Update Model
    ↓
Recompute Frontier
```

这比一次生成 20 个澄清问题更适合复杂需求。

### 2.2.2 Decision Mapping / Wayfinder

当一个业务诉求过大，无法在一次 Session 内解决时，可以建立 Decision Map。

关键思想是：

> Ticket 应表达“需要决定什么”，而不是“需要实现什么”。

例如：

```text
目标：云相册同步

├─ 同步方向？
│  ├─ 单向
│  └─ 双向
├─ 冲突策略？
│  ├─ server wins
│  ├─ last write wins
│  └─ merge
└─ 删除语义？
   ├─ local only
   └─ propagated delete
```

Decision Map 的价值是显式管理依赖关系和当前 Frontier，而不是把大需求拆成一串实现 Task。

### 2.2.3 Prototype-driven Clarification

以下问题经常无法单靠语言解决：

- UI 应该怎样表现？
- 某种状态机是否自然？
- 用户操作反馈是否容易理解？
- 某种交互是否真实可用？

此时可以：

```text
Unknown
  ↓
Hypothesis A / B
  ↓
Cheap Prototype
  ↓
Human feedback
  ↓
Decision
```

Prototype 的目标不是提前生产代码，而是**通过具体制品降低决策不确定性**。

---

## 2.3 Requirement Modeling：把自然语言变成可以推理的模型

### 2.3.1 Domain Modeling

自然语言需求中的许多问题，本质上不是 Story 缺失，而是概念不稳定。

例如“账户”可能分别表示：

```text
User
Customer
Login Identity
Subscription
Billing Account
```

如果一个词在不同上下文承担多个含义，后续 Scenario、API、数据库和测试都会发生歧义。

Domain Modeling 的核心工作包括：

- 识别对象；
- 统一术语；
- 识别同义词和 overloaded term；
- 建立对象关系；
- 澄清生命周期和状态；
- 通过实际 Scenario stress-test 模型；
- 将重要且稳定的概念变成 Ubiquitous Language。

### 2.3.2 Scenario / Example Discovery

Scenario 的主要作用不是编写测试用例，而是**展开行为状态空间**。

例如原始需求：

> 上传文件到云端。

必须进一步明确：

```text
文件是什么？
通过什么网络？
客户端处于什么生命周期状态？
服务器是否可用？
鉴权是否有效？
上传过程中网络是否变化？
服务器成功但 ACK 丢失怎么办？
```

BDD 的 concrete example 常采用：

```text
Context
  +
Action / Event
  +
Expected Outcome
```

具体 Example 可以反向发现：

- 新 Rule；
- 新对象；
- 新状态；
- 新 Unknown；
- 需要拆出的 Story；
- 原始 Assumption。

### 2.3.3 Domain 与 Scenario 不是前后两个阶段

二者实际是共同演化关系：

```text
Domain Model
     ↓
Generate Scenario
     ↓
Scenario exposes Object / Rule / State
     ↓
Update Domain Model
     ↓
Generate new Scenario
```

因此不应该强制：

```text
先完整 Domain Modeling
→ 再 Scenario Discovery
```

而应该把它们视为同一个 Behavior Modeling Operation 的两个视图。

---

## 2.4 Verification & Challenge：发现新的问题，与检查是否闭环

### 2.4.1 Spec-driven Clarification / Checklist / Analyze

当前 Spec Kit 将多个质量动作分开：

- `clarify`：针对 Spec 中 underspecified areas 进行定向问答，并将答案写回 Spec；
- `checklist`：检查需求本身是否完整、清晰、一致，类似对自然语言规格执行质量测试；
- `analyze`：在 spec / plan / tasks 出现后做跨 Artifact 的一致性与覆盖分析，只读报告冲突和缺口。

这种分离很有价值，因为它表明：

> **补充信息、检查单个 Spec 的质量、检查多个 Artifact 之间的一致性，本来就是不同动作。**

### 2.4.2 Adversarial Challenge

Challenge 不应该只是再列一轮 edge cases，而应该主动攻击当前 Requirement Model 的脆弱点，例如：

```text
Assumption
Invariant
Cross-scenario interaction
Race / Sequence
Contradiction
Unproven dependency
Hidden coupling
```

例如：

```text
Rule A：网络失败最多重试 3 次
Rule B：验证码超过 5 分钟不得发送
```

Challenge 应追问：

> 如果第 3 次 Retry 发生在第 5 分钟之后，哪个规则优先？

这不是普通“多考虑一个异常场景”，而是在攻击规则组合的完整语义。

### 2.4.3 Multi-Agent Review

可以让不同 Agent 分别从产品、架构、开发、测试、安全等角度审查同一个 Requirement Model。

但 Multi-Agent 的主要价值应该是**增加独立观察角度**，而不是让五个 Agent 各自重新生成一套完整需求。

否则容易产生：

- 重复 Finding；
- 多套术语；
- 相互冲突的建议；
- 高 token 成本；
- 很难判断谁拥有最终事实。

因此 Multi-Agent 必须共享同一个 SSOT，并对 Finding 做去重和合并。

---

## 2.5 方法能力对比

| 方法 | 主要对象 | 主要解决的 Unknown | 核心输出 | 最容易重复的能力 |
|---|---|---|---|---|
| Reality / Evidence Discovery | 外部现实、代码、依赖 | Fact / Constraint | Fact、Constraint、Evidence | Feasibility、Context Discovery |
| Domain Modeling | 概念、对象、术语 | Domain Unknown | Concept、Relation、Glossary | Scenario Discovery |
| Scenario / Example Mapping | 行为和上下文 | Behavior Unknown | Scenario、Rule、Question | Challenge |
| Grilling | 产品/业务选择 | Decision / Intent | Decision | Decision Mapping |
| Wayfinder | 大型决策空间 | Decision Dependency | Frontier、Decision Tickets | Grilling |
| Prototype | 难以语言决定的问题 | Experience / Design Unknown | Decision Evidence | Grilling |
| Clarify | Spec 局部模糊 | Underspecified Requirement | Updated Spec | Grilling |
| Challenge | 假设、组合关系 | Risk / Contradiction | Finding、新 Unknown | Scenario、Gate |
| Checklist / Gate | 已有 Spec | Closure / Quality | Verdict | Challenge |
| Analyze | 多 Artifact | Coverage / Consistency | Cross-artifact Finding | Gate / Converge |

**关键结论：**这些方法并非可以直接首尾连接成一个 9 阶段流程；如果缺少统一的数据模型和职责边界，组合越多，重复越严重。

---

# 3. 现有方案的红军评审与问题分析

## 3.1 原 L0～L6 模型回顾

初始组合方案是：

```text
L0 Feasibility / Evidence Discovery
        ↓
L1 Context & Domain Discovery
        ↓
L2 Decision Frontier
        ↓
L3 Socratic / Grilling
        ↓
L4 Scenario + Rule + Example
        ↓
L5 Adversarial Challenge
        ↓
L6 Spec Quality Gate
```

这套模型最大的优点是覆盖全面：它几乎把现实约束、业务决策、领域建模、行为展开、反例挑战和最终 Gate 全部包括进来了。

但红军评审的核心问题是：

> **完整不等于正交。**

如果多个阶段对同一个 Unknown 都有“发现”和“修改”权限，Agent 实际运行时会不断重复。

---

## 3.2 五组主要重复

### 3.2.1 Feasibility ↔ Context Discovery

两者都会调查：

- 平台能力；
- 外部 API；
- 当前架构；
- 已有代码；
- 技术限制；
- 合规要求。

例如“个人微信能否后台自动发送消息”既可以算 Feasibility，也可以算 External Context。

**问题：**

同一个事实可能被记录成：

```text
Feasibility Finding F-001
Context Constraint C-008
```

导致重复、状态不同步甚至结论冲突。

**建议：**合并为 `Reality Discovery`，统一记录 Fact / Constraint / Evidence。

---

### 3.2.2 Decision Frontier ↔ Grilling

Decision Frontier 负责识别“还需要决定什么”，Grilling 负责逐个询问。

表面看这是两个阶段，实际上它们是同一个循环的两个动作：

```text
Find Decision
   ↓
Select Decision
   ↓
Resolve Decision
   ↓
Update Model
   ↓
Recompute Decisions
```

最大的风险是：如果先完整生成 20 个 Decision，再开始 Grilling，第一个答案就可能让后面的多个 Decision 消失、变化或产生新依赖。

因此 Frontier 不能是一次性 Artifact，而应该是**实时计算出来的当前状态**。

**建议：**合并为 `Decision Resolution Loop`。

---

### 3.2.3 Domain Modeling ↔ Scenario Discovery

领域对象往往通过 Scenario 才被发现，而 Scenario 又依赖 Domain Model 才能系统展开。

例如：

```text
收到验证码 → 转发
```

最初可能只有：

```text
SMS
VerificationCode
Recipient
```

当出现“网络恢复后重试”场景时，才会发现需要：

```text
ForwardAttempt
RetryPolicy
Expiration
```

当出现“多个规则同时匹配”时，又会发现：

```text
RulePriority
RuleSelection
```

因此 Domain 与 Scenario 是双向演化关系。

**建议：**统一放入 `Behavior Modeling`，不再作为严格的先后阶段。

---

### 3.2.4 Scenario Discovery ↔ Challenge

这是最容易重复的一组。

Scenario Discovery 可能展开：

```text
Network = available / unavailable
Code = one / none / multiple
Rule = none / one / multiple
Delivery = success / timeout / failure
```

Challenge 又可能提出：

```text
如果断网？
如果多个验证码？
如果多条规则？
如果超时？
```

这实际上重复执行同一类状态空间探索。

**建议明确职责：**

**Scenario Discovery：Coverage-oriented behavior exploration**

主要展开：

- 对象状态；
- 输入分类；
- 环境条件；
- 正常 / 异常结果；
- Rule 对 Example 的映射。

**Challenge：Adversarial model attack**

只重点攻击：

- Assumption；
- Invariant；
- 多 Scenario 组合；
- 时序和并发；
- Rule 之间的冲突；
- 隐藏耦合；
- 未被证明的事实依赖。

Challenge 不应重新执行一次普通 Edge Case Brainstorming。

---

### 3.2.5 Challenge ↔ Quality Gate

Challenge 可能发现：

- “及时”不可验证；
- Retry 与 Expiry 矛盾；
- 某种状态没有定义；
- Rule 缺少失败行为。

如果 Gate 又重新开放式寻找同样的问题，二者仍然重复。

因此必须明确：

```text
Challenge = 发现新的问题（Discovery）
Gate      = 判断已知问题是否闭环（Verification）
```

Gate 应以结构化规则为主，例如：

```text
是否仍有 P0/P1 Unknown？
每个关键 Decision 是否有 Resolution？
每个 Rule 是否可验证？
关键 Scenario 是否有明确 Outcome？
是否存在已知 Contradiction？
Assumption 是否有 Evidence 或明确风险接受？
```

Gate 不应主要依赖“再想想还有什么问题”。

---

## 3.3 重复产生的三个根因

### 根因一：把 Operation 错误设计成 Phase

现实的需求澄清并不是：

```text
Domain 完成
  ↓
Scenario 完成
  ↓
Decision 完成
```

而更接近：

```text
Scenario → 新 Domain Object
Domain Object → 新 State
State → 新 Scenario
Scenario → 新 Unknown
Unknown → Decision
Decision → 修改 Rule
Rule → 再产生 Scenario
```

这是一个持续迭代的图，而不是瀑布。

---

### 根因二：Discover / Resolve / Verify 三种目的被混在一起

一个需求质量系统至少有三种本质不同的动作：

```text
DISCOVER
发现目前还不知道什么、模型缺什么

RESOLVE
通过 Research / Ask / Prototype / Modeling 解决 Unknown

VERIFY
判断重要问题是否已经闭环、Spec 是否满足准入标准
```

如果同一个 Skill 同时承担三种任务，就很容易反复产生同样的问题。

---

### 根因三：Artifact 被当成事实源，而不是视图

一种常见设计是：

```text
facts.md
unknowns.md
decisions.md
rules.md
scenarios.md
spec.md
```

例如：

```text
Unknown：网络失败是否重试？
      ↓
Decision：网络失败重试 3 次
      ↓
Rule：网络失败最多重试 3 次
      ↓
Spec：网络失败最多重试 3 次
```

同一信息被复制到四处。随后只要修改其中三处，就形成不一致。

因此应采用：

> **Structured Requirement Model = Single Source of Truth；Markdown / HTML / Spec = Generated Views。**

---

# 4. 推荐的 Spec 质量保证总体模型

## 4.1 从“七阶段流水线”改为“围绕 Requirement Model 的五类操作”

推荐模型：

```text
                         ┌────────────────────┐
                         │ Requirement Model  │
                         └─────────▲──────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          │                        │                        │
 Discover Reality ───→ Model Behavior ───→ Resolve Uncertainty
          ▲                        │                        │
          │                        ▼                        │
          └────────────── Challenge Model ←────────────────┘
                                   │
                                   ▼
                              Gate Closure
                                   │
                       ┌───────────┴───────────┐
                       │                       │
                    Not Ready             Ready
                       │                       │
                       └──→ 回到对应 Operation │
                                               ▼
                                      Engineering Ready
```

五类能力不是必须严格顺序执行的 Phase，而是由当前 Requirement Model 的状态触发。

---

## 4.2 Discover Reality

### 目标

确认所有重要需求推理建立在真实证据上，而不是 Agent 或用户的无意识假设上。

### 处理对象

```text
Fact Unknown
Constraint Unknown
Existing Behavior Unknown
External Dependency Unknown
Feasibility Unknown
```

### 主要动作

- Search / Research；
- Read Code / Docs；
- Inspect Architecture；
- Execute Experiment；
- 查询外部 API / Policy；
- 收集支持和反对证据。

### 输出

```text
Fact
Constraint
Evidence
Confidence
Assumption（暂时无法验证时）
```

### 边界

不负责替用户作产品选择。

例如：

```text
“微信是否支持该 API？” → Discover Reality
“如果个人微信不支持，是否接受企业微信？” → Resolve Uncertainty
```

---

## 4.3 Model Behavior

### 目标

将松散自然语言变成 Agent 可以持续推理的结构化行为模型。

### 统一管理

```text
Concept / Entity
Relationship
State
Event
Scenario
Rule
Invariant
Assumption
Actor
Input / Output
```

### 核心关系

建议至少表达：

```text
Story / Goal
   ↓
Rule
   ↓ illustrated by
Scenario / Example

Scenario
   ├─ Context
   ├─ Event
   └─ Outcome

Entity
   ↓
State Transition

Rule
   ↓ constrained by
Invariant / Constraint
```

### 关键原则

Domain、Scenario、Rule、State 不是四个阶段，而是**同一个 Requirement Model 的不同视图**。

---

## 4.4 Resolve Uncertainty

### 目标

系统消除阻塞 Spec 收敛的重要 Unknown。

### 第一步：Unknown 分类

建议至少支持：

| Unknown 类型 | 典型问题 | 默认求解器 |
|---|---|---|
| Fact Unknown | 平台是否支持？ | Research |
| Constraint Unknown | 当前代码允许什么？ | Research / Code Discovery |
| Intent Unknown | 为什么需要该能力？ | Ask |
| Domain Unknown | “账户”具体指什么？ | Model + Ask |
| Behavior Unknown | 断网后怎样？ | Scenario Exploration |
| Decision Unknown | 重试 3 次还是不重试？ | Ask / Decision |
| Experience Unknown | 哪种 UI 更自然？ | Prototype |
| Risk / Assumption | 这个前提可靠吗？ | Challenge |

### 第二步：Decision Frontier

Frontier 不作为独立阶段，而是根据模型实时计算：

```text
所有 unresolved Unknown
        ↓
按以下维度排序
        ↓
Blocking level
Decision dependency
Risk
Downstream impact
Cost of late change
        ↓
选择最高优先级 Unknown
```

### 第三步：选择 Resolver

```text
Can evidence resolve it?
   ├─ YES → Research
   └─ NO
       ↓
Is it a human/product decision?
   ├─ YES → Ask / Grilling
   └─ NO
       ↓
Would a concrete artifact reduce uncertainty?
   ├─ YES → Prototype
   └─ NO → Modeling / Escalation
```

### 第四步：写回模型

每个 Decision 至少记录：

```yaml
id: D-008
question: "网络失败后是否自动重试？"
status: decided
resolution: "自动重试，最多 3 次，但不能超过验证码有效期"
reason: "..."
evidence: []
impacts:
  - R-014
  - S-021
```

---

## 4.5 Challenge Model

### 目标

不是“把 Scenario 再想一遍”，而是主动寻找当前模型最可能被现实打穿的位置。

### 建议的 Challenge 维度

#### 1. Assumption Attack

```text
你为什么相信该前提一定成立？
证据在哪里？
如果它不成立会怎样？
```

#### 2. Invariant Attack

```text
该不变量在失败、恢复、并发情况下是否仍然成立？
```

#### 3. Interaction Attack

单个 Scenario 都正确，但组合起来是否冲突？

例如：

```text
网络恢复
+
验证码过期
+
后台重试
```

#### 4. Sequence / Race Attack

例如：

```text
规则更新 || 短信到达
取消操作 || 服务器返回成功
App 重启 || Retry Scheduler 触发
```

#### 5. Contradiction Attack

检查：

```text
Rule ↔ Rule
Rule ↔ Scenario
Decision ↔ Constraint
Goal ↔ Out-of-scope
```

#### 6. Counterexample Attack

针对 Rule 构造一个具体反例，尝试证明当前规则表达不足。

### 输出

Challenge 只产生：

```text
Finding
Counterexample
New Unknown
Model Change Proposal
```

不直接偷偷替用户完成重大产品决策。

---

## 4.6 Gate Closure

### 目标

Gate 回答的不是：

> “还能不能再想到一个问题？”

而是：

> **目前已经识别出来的重要问题是否达到预定关闭条件？**

### 推荐 Gate 维度

#### Completeness

- Goal / Actor / Trigger / Outcome 是否明确？
- 关键对象、状态和 Rule 是否存在？
- 关键失败模式是否有行为定义？
- 外部依赖是否明确？

#### Clarity

检查模糊词：

```text
快速
及时
合理
正常
支持
自动
必要时
尽可能
```

是否转换成可判断的业务语义。

#### Consistency

- Rule 是否互相冲突？
- Decision 是否与 Constraint 冲突？
- 不同 Scenario 是否给同一状态定义不同 Outcome？
- canonical terminology 是否一致？

#### Verifiability

每个关键 Rule 是否能回答：

```text
Given what context?
When what happens?
What observable outcome proves the rule?
```

#### Unknown Closure

- 是否仍有 blocking Unknown？
- 是否存在未解决 P0/P1 Finding？
- Assumption 是否有 Evidence 或显式风险接受？

#### Traceability

至少能够形成：

```text
Goal / Story
   ↓
Rule
   ↓
Scenario / Example
   ↓
Decision / Evidence
```

### Verdict

建议 Gate 只输出有限状态：

```text
PASS
PASS_WITH_RISK
BLOCKED
```

避免模糊的“整体看起来还不错”。

---

# 5. 工程实现方案

## 5.1 Requirement Model：建立 Single Source of Truth

建议系统的核心不是 `spec.md`，而是一个结构化 Requirement Model。

```text
Requirement Model
│
├── Intent / Goal
├── Actor
├── Fact
├── Constraint
├── Concept / Entity
├── Relationship
├── State
├── Event
├── Rule
├── Scenario / Example
├── Invariant
├── Assumption
├── Unknown
├── Decision
├── Finding
└── Evidence
```

推荐所有节点具有统一元数据：

```yaml
id: R-014
type: rule
statement: "网络失败最多自动重试 3 次，且不得超过验证码有效期"
status: active
source:
  - D-008
related:
  - S-021
  - S-022
evidence: []
confidence: high
updated_at: 2026-09-08
```

---

## 5.2 Unknown 分类与自动路由

Unknown 应该成为系统中的一等对象，而不是散落在 Markdown 中的问号。

示例：

```yaml
id: U-017
type: decision
question: "验证码提取失败时是否转发原始短信？"
status: unresolved
severity: high
blocking: true
owner: human
resolver: grilling
related:
  - S-009
  - R-006
```

路由规则：

```text
Fact / Constraint
    → Reality Discoverer

Intent / Product Decision
    → Decision Resolver → Human

Domain ambiguity
    → Behavior Modeler / Human

Behavior gap
    → Scenario Exploration

Experience / UI ambiguity
    → Prototype

Assumption / Risk
    → Challenger
```

这样可以从机制上阻止 Agent 遇到任何问题都去“请用户补充”。

---

## 5.3 Agent / Skill 架构

推荐的能力边界：

```text
                Requirement Model
                       ▲
       ┌───────────────┼────────────────┐
       │               │                │
Reality Discoverer  Behavior Modeler  Decision Resolver
       │               │                │
       └───────────────┼────────────────┘
                       │
                Model Challenger
                       │
                  Gate Evaluator
```

### 5.3.1 Reality Discoverer

**输入：** Fact / Constraint Unknown  
**允许：** 查询代码、文档、Web、实验、增加 Evidence  
**输出：** Fact / Constraint / Evidence / Assumption  
**禁止：** 替业务方做产品偏好决策

### 5.3.2 Behavior Modeler

**输入：** 原始需求、Fact、Decision、已有 Requirement Model  
**允许：** 增加/调整 Concept、State、Rule、Scenario  
**输出：** 更新后的行为模型、新 Unknown  
**禁止：** 无依据地将 Unknown 自动假设成确定 Rule

### 5.3.3 Decision Resolver

**输入：** unresolved Unknown / Decision Frontier  
**允许：** Ask / Research / Prototype 路由  
**输出：** Decision Resolution  
**禁止：** 一次性询问大量低优先级问题；自行代表用户回答 HITL 决策

### 5.3.4 Model Challenger

**输入：** 稳定到一定程度的 Requirement Model  
**允许：** Counterexample、Assumption Attack、Interaction Analysis、Contradiction Finding  
**输出：** Finding / New Unknown  
**禁止：** 重复普通 Scenario Coverage Scan

### 5.3.5 Gate Evaluator

**输入：** Requirement Model + Gate Policy  
**允许：** 计算质量指标、报告未闭环项、给出 Verdict  
**输出：** PASS / PASS_WITH_RISK / BLOCKED  
**禁止：** 进行开放式需求 Brainstorming 或偷偷修改产品决策

---

## 5.4 Artifact 设计：文档是 View，不是真相源

不推荐：

```text
unknowns.md        ← 一份事实
     ↓
decisions.md       ← 再复制一次
     ↓
rules.md           ← 再复制一次
     ↓
spec.md            ← 再复制一次
```

推荐：

```text
             Requirement Model
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
    spec.md      scenarios.md   quality-report.md
       ↓             ↓             ↓
  人/Agent阅读    BDD/测试使用     Gate/评审使用
```

例如 `spec.md` 中的 Rule 不手工独立维护，而由 Requirement Model 渲染。

这样修改：

```text
Decision D-008
```

只需要更新一次，相关 Rule、Scenario、Spec View 重新生成即可。

---

## 5.5 防重复机制

### 机制一：统一 ID

所有重要节点有唯一 ID：

```text
F-* Fact
C-* Constraint
R-* Rule
S-* Scenario
U-* Unknown
D-* Decision
A-* Assumption
FD-* Finding
E-* Evidence
```

### 机制二：Finding 去重

创建新 Finding 前至少比较：

```text
same target
same concern type
same violated rule / assumption
semantic similarity
```

已有 Finding 时优先追加 Evidence，而不是重新创建。

### 机制三：Owner / Capability Boundary

每种节点状态的主要 Owner 明确，例如：

```text
Fact → Reality Discoverer
Domain Model → Behavior Modeler
Decision → Decision Resolver
Challenge Finding → Challenger
Verdict → Gate Evaluator
```

其他 Agent 可以引用，但不应重复生成另一套同义事实。

### 机制四：Unknown 状态机

```text
DISCOVERED
   ↓
CLASSIFIED
   ↓
ROUTED
   ↓
RESOLVING
   ↓
RESOLVED
   ↓
VERIFIED
```

避免：问题已经回答，但下一轮 Agent 因为不知道状态又重新提问。

### 机制五：Challenge 之前先执行 Coverage Check

如果某个异常已经有 Scenario 覆盖：

```text
“无网络” → S-018 已存在
```

Challenge 不再以“如果无网络怎么办？”重新创建 Finding，而应继续攻击更深一层：

```text
S-018 与 Retry Rule / Expiry Rule 组合是否一致？
```

---

## 5.6 Gate Policy 示例

可以将 Gate 编码成策略：

```yaml
gate:
  blocking_unknowns: 0
  unresolved_p0_findings: 0
  unresolved_p1_findings: 0

  require:
    - every_critical_rule_has_scenario
    - every_critical_scenario_has_observable_outcome
    - every_external_dependency_has_constraint_or_evidence
    - every_high_risk_assumption_is_verified_or_accepted
    - no_known_rule_contradictions
    - terminology_is_canonical

  verdicts:
    pass: "all blocking rules satisfied"
    pass_with_risk: "no blocker, accepted residual risks exist"
    blocked: "one or more blocking rules violated"
```

其价值在于让 Engineering Ready 从主观判断转为可解释的 Verdict。

---

# 6. 端到端案例与结论

## 6.1 原始需求

以一个 Android 业务诉求为例：

> 手机收到验证码短信后，自动提取验证码，并通过微信发送给预先配置的人员。

初始模型只有：

```text
SMS
  ↓
Extract Code
  ↓
Send via WeChat
```

如果直接进入 Task 分解和编码，大量隐含问题会进入实现阶段。

---

## 6.2 Discover Reality

系统首先识别 Fact Unknown：

```text
Android 是否能稳定接收所需短信？
相关权限和后台限制是什么？
个人微信是否提供后台自动发送给指定联系人的官方能力？
企业微信是否存在可替代能力？
```

Agent 自己研究，不立即询问用户。

假设调查得到：

```text
F-001：Android 可以在满足权限和系统约束时接收 SMS 事件。
C-001：后台行为受 Android 版本/OEM 策略限制。
F-002：个人微信缺少满足目标的稳定官方后台自动发送能力。
F-003：企业微信存在更适合自动化集成的能力路径。
```

于是出现真正需要人决定的问题：

```text
U-001：如果个人微信无法可靠全自动发送，V1 是否接受企业微信？
```

这说明 Reality Discovery 成功避免了“先细化一个实际上走不通的实现方案”。

---

## 6.3 Model Behavior

用户决定 V1 接受企业微信后，Behavior Modeler 从原始句子抽取：

```text
IncomingMessage
VerificationCode
ForwardRule
Recipient
ForwardAttempt
DeliveryResult
```

进一步定义：

```text
ForwardRule
├─ senderMatcher
├─ contentMatcher
├─ recipient
├─ priority
└─ enabled
```

并建立 Happy Path：

```text
Given 一个启用的银行验证码转发规则
When 收到与该规则匹配的短信
Then 提取验证码
And 发送给规则指定的 Recipient
And 记录 ForwardAttempt 成功
```

随后 Scenario Exploration 展开：

```text
规则：无匹配 / 单匹配 / 多匹配
验证码：唯一 / 无法识别 / 多候选
网络：可用 / 不可用 / 波动
投递：成功 / 超时 / 鉴权失败 / 服务端错误
```

在这一过程中模型自动发现更多对象：

```text
RetryPolicy
Expiration
MessageIdentity
RulePriority
```

体现 Domain 与 Scenario 的共同演化，而不是重复执行两轮工作。

---

## 6.4 Resolve Uncertainty

系统发现：

```text
U-005：多条 ForwardRule 同时匹配时如何选择？
```

分类：`Decision Unknown`。

Decision Resolver 询问用户，而不是由 Agent 自己决定。

用户选择：

> 使用优先级最高的启用规则。

形成：

```yaml
id: D-005
status: decided
resolution: "Select highest-priority enabled matching rule"
```

Model 自动产生：

```text
R-007：当多个 Rule 同时匹配时，必须选择 priority 最高的 enabled Rule。
```

Scenario：

```text
Rule A priority 10
Rule B priority 20
二者同时匹配
→ Rule B
```

当出现新的 Unknown：

```text
U-009：无网络时失败是否自动重试？
```

用户决定：最多重试 3 次。

接着 Scenario 暴露：

```text
如果第 3 次重试时验证码已经过期呢？
```

于是形成新的 Decision：

> Expiry 优先于 Retry Count。

最终 Rule：

```text
R-012：网络失败可以自动重试，最多 3 次；任何 Retry 都不得发生在验证码有效期之后。
```

这说明 Decision Frontier 必须动态重算，而不是在流程开头一次性列完。

---

## 6.5 Challenge Model

此时普通 Scenario 已较完整，Challenger 不再重复询问“如果断网怎么办”。

它转而攻击模型：

### Attack 1：重复投递假设

```text
Assumption：同一 SMS 只收到一次。
```

Counterexample：运营商重复投递同一内容。

产生：

```text
U-015：系统如何定义同一 Message？
R-020：同一逻辑消息不得被重复转发。
```

### Attack 2：ACK 丢失与 Retry 的组合

```text
企业微信已经成功接收请求
但客户端没有收到 Response
→ 客户端 Retry
→ 用户收到两次验证码
```

Challenge 暴露的是**幂等语义**，而不是一个普通“失败场景”。

### Attack 3：Retry 与 Expiry 规则冲突

检查：

```text
R-012 Retry
R-013 Expiration
```

确认优先级已定义，否则创建 Contradiction Finding。

### Attack 4：时序竞争

```text
配置规则正在修改
||
SMS 同时到达
```

要求明确本次匹配使用哪个版本的 Rule Snapshot。

这说明 Challenge 的独立价值来自对 Assumption / Interaction / Sequence / Contradiction 的攻击，而不是重新做 Scenario List。

---

## 6.6 Gate Closure

Gate Evaluator 根据结构化模型运行：

```text
Blocking Unknown = 0 ?
P0/P1 Finding = 0 ?
关键 Rule 是否有 Example？
关键 Scenario 是否有 Observable Outcome？
外部依赖是否有 Evidence / Constraint？
高风险 Assumption 是否有处置？
Rule 是否存在已知冲突？
术语是否统一？
```

假设仍存在：

```text
U-022：企业微信鉴权失效后的用户可见行为未决定。
severity = high
blocking = true
```

则 Verdict：

```text
BLOCKED
```

而不是“当前 PRD 大体完整，可以先开发”。

当 U-022 被解决、模型重新验证后：

```text
PASS_WITH_RISK
```

可能仍保留 OEM 后台限制这一已知残余风险，但该风险已被明确接受、记录并有 Evidence。

此时才进入 Engineering Ready。

---

## 6.7 最终结论

本次调查最重要的结论不是“应该再增加多少个需求分析 Skill”，而是：

> **Spec Quality Assurance 的核心应该从“多个阶段、多个文档、多个 Agent 分别分析”转变为“多个正交 Operation 围绕一个持续演化的 Requirement Model 工作”。**

推荐最终结构为：

```text
Discover Reality
      ↓
Model Behavior
      ↓
Resolve Uncertainty
      ↕
Challenge Model
      ↓
Gate Closure
```

但它们不是固定的瀑布阶段。真实控制逻辑应该是：

```text
Requirement Model 状态变化
        ↓
识别当前最重要的 Gap / Unknown
        ↓
路由到合适 Operation
        ↓
更新同一个 Requirement Model
        ↓
重新计算 Frontier 和质量状态
        ↓
达到 Gate Closure
```

其关键设计原则可以归纳为七条：

1. **Reality before reasoning**：能查证的事实先查证，不把所有问题交给用户。
2. **Model before prose**：先建立结构化 Requirement Model，再生成 Spec 文档。
3. **Unknown must be typed**：每个 Unknown 必须分类，才能正确路由。
4. **Decision Frontier is dynamic**：决策空间随着答案持续变化，不一次性冻结。
5. **Scenario explores coverage; Challenge attacks assumptions**：二者必须有明确边界。
6. **Challenge discovers; Gate verifies closure**：Gate 不重复开放式探索。
7. **One source of truth**：Fact、Decision、Rule、Scenario 等结构化模型是事实源，Markdown/HTML 是 View。

最终要建设的不是一个单独的 `clarify` 命令，而是一套：

> **Requirement Model + Discovery + Modeling + Decision Resolution + Challenge + Quality Gate**

构成的 **Spec Quality Assurance System**。

其目标不是让需求“看起来写得更完整”，而是让进入设计和编码阶段之前的关键事实、决策、规则、场景、假设和风险都能够被追踪、挑战和验证。

---

## 6.8 主要参考资料（截至 2026-09-08）

1. GitHub Spec Kit — README / Idea Assessment Pipeline  
   https://github.com/github/spec-kit/blob/main/README.md

2. GitHub Spec Kit — Assess Extension  
   https://github.com/github/spec-kit/blob/main/extensions/assess/README.md

3. GitHub Spec Kit — Agentic SDD Reference  
   https://github.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md

4. GitHub Spec Kit — Clarify Command  
   https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md

5. Matt Pocock Skills — Wayfinder  
   https://github.com/mattpocock/skills/blob/main/docs/engineering/wayfinder.md

6. Matt Pocock Skills — Domain Modeling  
   https://github.com/mattpocock/skills/blob/main/docs/engineering/domain-modeling.md

7. Matt Pocock Skills — Ask Matt / Grilling / Prototype Routing  
   https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md

8. Cucumber — Example Mapping  
   https://cucumber.io/docs/bdd/example-mapping/

9. Cucumber — Better requirements by harnessing the power of examples  
   https://cucumber.io/blog/bdd/better-requirements-by-harnessing-the-power-of-exa/

10. Cucumber — BDD Discovery / Formulation / Automation  
    https://cucumber.io/blog/bdd/seb-rose-on-bdd-cucumber-cyber-dojo-and-testers-in/