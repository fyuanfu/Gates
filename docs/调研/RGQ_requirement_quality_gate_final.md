# RGQ：需求质量 Gate 业界研究、框架对比与最终方案

> 版本：Final v1.0  
> 日期：2026-09-11  
> 目标：在**既定产品目标与迭代范围内**，高效、高质量地发现 PRD / 交互需求中的真实缺陷，特别是容易导致实现错误、用户可感知错误结果和验收争议的需求遗漏；不承担产品价值判断，不擅自扩大 Scope。

---

## 1. Executive Summary

本研究对比了四类业界实践：

1. **INCOSE / ISO/IEC/IEEE 29148**：回答“什么叫高质量需求”；
2. **GitHub spec-kit**：回答“如何把需求澄清、Checklist、跨制品一致性检查接入 AI 开发流程”；
3. **AWS AI-DLC**：回答“如何用阶段、独立 Reviewer、Human Gate、审计证据治理 AI 开发”；
4. **Microsoft HVE Core 的 Requirements Quality Gate**：给出了一个非常具体的工程化范例——按 ISO 29148 属性评分、设 hard threshold、输出机器可消费的 Gate Report。

最终结论：**需求质量 Gate 不应该等同于 Checklist，也不应该等同于 LLM Review。** 更合理的结构是：

```text
Scope Guard
    ↓
Requirement Model
    ↓
Fast Quality Scan
    ↓
Coverage / Scenario Discovery
    ↓
Consistency + Verifiability + Brownfield Compatibility
    ↓
Independent Adjudication
    ↓
P0/P1 Gate Decision
```

其中：

- **INCOSE** 提供质量语义；
- **spec-kit** 提供 Clarify / Checklist / Analyze 的职责分离思想；
- **AI-DLC** 提供 Brownfield Reverse Engineering、独立 Reviewer、Human Gate、Evidence/Audit 思想；
- **Microsoft** 提供评分、阻断阈值、结构化输出的工程模式；
- RGQ 在此基础上增加一个关键能力：**在不扩大 Scope 的情况下主动发现遗漏场景，尤其异常场景、状态组合、依赖失败和 Brownfield 已存在行为所暴露的隐含需求。**

RGQ 的核心目标不是把文档写得“漂亮”，而是：

> **尽可能在编码之前阻断那些会导致“实现看起来正确，但用户得到错误结果”的需求问题。**

---

## 2. 研究结论：业界需求质量 Gate 实际上由五层组成

成熟的需求质量治理通常不是单一 Checklist，而是五层能力组合。

| 层级 | 解决的问题 | 典型手段 |
|---|---|---|
| L1 语言/结构质量 | 一条需求是否写清楚 | Requirement smell、规则、模板、术语检查 |
| L2 语义质量 | 是否完整、明确、可验证 | ISO 29148 / INCOSE 属性、LLM semantic review |
| L3 集合与覆盖质量 | 多条需求之间是否漏、冲突 | completeness、consistency、scenario/state coverage |
| L4 上下文兼容性 | 是否与现有系统、交互、依赖冲突 | Brownfield scan、traceability、existing behavior evidence |
| L5 治理与准出 | 什么问题必须拦住 | independent review、severity、hard gate、audit trail |

这五层不能互相替代。

例如：

- 只做 requirement smell，可以找到“快速、适当、正常”等模糊词，但很难发现“上传途中断网后 UI 仍显示上传成功”这种**场景缺口**；
- 只让 LLM 自由 Review，容易产生范围扩张、重复问题、严重度膨胀和幻觉；
- 只做 Checklist，容易产生“全部打勾但关键场景仍漏掉”的假安全感；
- 只做 Human Review，质量依赖 reviewer 经验，且难规模化、难形成持续积累。

因此 Gate 必须同时拥有**规则检测、语义推理、场景探索、证据约束和治理机制**。

---

## 3. INCOSE / ISO 29148：定义“什么是好需求”

### 3.1 个体需求质量

INCOSE Guide to Writing Requirements v4 与 ISO/IEC/IEEE 29148 使用的一组核心概念包括：

- Necessary
- Appropriate
- Unambiguous
- Complete
- Singular
- Feasible
- Verifiable
- Correct
- Conforming

INCOSE 同时强调：要求“符合写作规则”只是必要条件，并不足以保证整个需求集合质量；需求工程不是单纯的文字编辑，而是工程分析活动。

### 3.2 需求集合质量

对 RGQ 更重要的是 **set-level quality**。INCOSE 对需求集合强调：

- Complete
- Consistent
- Feasible
- Comprehensible
- Able to be validated
- Correct

这说明一个重要事实：

> **一条条需求写得都很好，不代表需求集合完整。**

“遗漏场景”本质上属于 set-level completeness，而不是单句 grammar / smell 问题。

### 3.3 对 RGQ 的价值

INCOSE 最适合作为 RGQ 的**质量语义底座**，但不适合原样成为软件 PRD Gate。

原因：

- Necessary 会进入“需求是否应该做”的价值判断；
- Appropriate 可能进入需求层级与架构层级判断；
- Feasible 往往需要技术、成本、周期等上下文；
- Conforming / Singular 很重要，但通常不是导致用户严重错误的首要因素。

因此 RGQ 应做 Tailoring，而不是照搬。

### 3.4 RGQ 采用的 INCOSE 子集

**Hard-quality dimensions：**

- Unambiguous
- Complete（statement + set）
- Consistent
- Verifiable
- Correct（相对于明确来源、交互或既有事实）

**Soft-quality dimensions：**

- Singular
- Conforming
- terminology/style

**默认不作为本 Gate 评价对象：**

- Necessary —— 属于价值/范围层；
- Appropriate —— 只在明显层级错置导致需求不可理解时提示，不做产品价值挑战；
- Feasible —— 只有在需求自身与明确约束直接矛盾时才报告，不主动做技术方案评审。

---

## 4. GitHub spec-kit：把需求质量嵌进 SDD 流程

当前 spec-kit 的推荐链路是：

```text
constitution
→ specify
→ clarify
→ plan
→ checklist
→ tasks
→ analyze
→ implement
→ converge
```

其中与需求 Gate 最相关的是三个能力。

### 4.1 Clarify

作用：针对 underspecified area 提出有限、聚焦的问题，并将答案回写到 `spec.md`。

启示：

- **发现问题**与**解决问题**应分开；
- 不应该让 Agent 默默补全需求；
- 未决需求应显式化。

### 4.2 Checklist

spec-kit 将 Checklist 描述为类似“requirements 的 unit tests”：检查完整性、清晰性、无歧义、一致性等。

更值得借鉴的是：**custom checklist 是 reviewer-owned artifact，Agent 不应默默自我批准。**

### 4.3 Analyze

`analyze` 主要检查 `spec.md → plan.md → tasks.md` 的冲突、遗漏与覆盖关系。

这实际上是另一种 Gate：

> requirement quality ≠ downstream artifact alignment。

因此 RGQ 不应该把 Spec→Plan→Task 的实现一致性混进“需求文档质量 Gate”本身。

### 4.4 spec-kit 的不足

如果目标是发现 PRD 真实缺陷，单独采用 spec-kit 仍有几个缺口：

1. Checklist 更多依赖已有 Requirement Model，本身不保证能主动发现新的遗漏场景；
2. Brownfield existing behavior 不是 requirement quality review 的强制输入；
3. 没有针对“异常场景/状态空间/依赖失败”的系统性探索模型；
4. Gate severity 与 P0/P1 阻断语义较弱；
5. 对 findings 的 evidence / confidence / scope anchor 没有形成 RGQ 所需的强约束。

因此 RGQ 应借 spec-kit 的**职责分离**，而不是复制它的 Checklist。

---

## 5. AWS AI-DLC：Gate 治理与 Brownfield 思想最值得借鉴

AI-DLC 当前是一个完整的 AI 驱动研发生命周期，分为 Initialization、Ideation、Inception、Construction、Operation 等阶段，并在阶段或 Stage 处设置 verification / approval gate。

### 5.1 Brownfield Reverse Engineering

AI-DLC 在 Brownfield 场景中会先做 Reverse Engineering，再进入 Requirements Analysis。

这是 RGQ 非常应该吸收的一点。

因为对存量 Android 产品，PRD 中大量“隐含需求”来自：

- 已存在状态机；
- 旧版本行为；
- 外部服务交互；
- 数据兼容；
- 中断/恢复；
- 历史错误处理；
- 平台生命周期。

只读 PRD，很容易把这些隐含上下文全部丢掉。

但 RGQ 需要严格限定：

> Brownfield 代码/文档只用于发现**既有行为、约束和直接依赖**，不得转变成代码设计评审。

### 5.2 Independent Reviewer

AI-DLC 在部分阶段使用独立 reviewer。Reviewer 读取 stage definition、Q&A 和 artifacts，但不依赖 builder 自己的 memory/plan 来形成判断。

这是一个非常好的反自证机制。

RGQ 应采用：

```text
Discovery Agent
      ↓ findings
Independent Adjudicator
      ↓
verified findings + severity + gate
```

而不是由同一个 Agent 一边找问题、一边判自己找得是否正确。

### 5.3 Human Approval Gate

AI-DLC 的 reviewer verdict 并不等于自动决策全部替代人；在关键阶段 reviewer findings 会作为 Human Gate 的 decision support。

RGQ 也应遵循：

- Agent 判断“是否存在需求缺陷”；
- 产品/需求 owner 决定“如何修改需求”；
- Agent 不自行发明产品决策。

### 5.4 Evidence / Audit

AI-DLC 重视 stage state、artifact、audit trail、source-bound evidence。

RGQ 应借鉴为：

- 每个 finding 必须指向文档锚点；
- Brownfield finding 必须引用现有行为证据；
- P0/P1 必须给出因果链；
- Gate Decision 必须可以回溯到 findings；
- 需求修改后可重新运行并比较 finding closure。

---

## 6. Microsoft HVE Core：最接近“可执行 Gate”的参考实现

Microsoft 开源的 HVE Core 中存在直接面向 Requirements Quality 的 Gate 设计。

其典型做法是：

- 对 FR / NFR / Constraint 按 ISO 29148 属性做 0–3 评分；
- 0 = absent；
- 1 = implied；
- 2 = explicit；
- 3 = traceable；
- 对部分核心属性设 hard threshold；
- 输出标准化 `QUALITY_REPORT`；
- Gate Decision 与 findings 分离。

PRD Quality Report 中还包含：

- summary counts；
- severity breakdown；
- FR→AC coverage；
- FR→Goal coverage；
- top findings；
- recommendations；
- machine-readable gate decision。

### 6.1 值得直接借鉴

1. **不要只输出自然语言 Review；输出稳定 schema。**
2. **不要用平均分决定 Gate。** 某一个关键属性失败就应该阻断。
3. `finding` 与 `gate decision` 分离。
4. blocker threshold 必须显式。
5. 人读报告和 Agent 消费报告应来自同一个事实源。

### 6.2 不应直接照搬

Microsoft 示例把 `Necessary` 作为核心 hard-gate 属性之一。

对于本 RGQ，这会越界到“为什么要做这个需求”。

因此最终方案明确做 Tailoring：

> **RGQ 不评价已经批准的 Intent / Scope 是否值得做，只评价 Scope 内需求是否足够明确、完整、一致、可验证，以及是否漏掉直接相关场景。**

---

## 7. 最新研究对方案的两个启示

### 7.1 Requirement Smell 适合做第一层快速扫描

2024 年 IEEE TSE 的 Paska 工作将 NLP、结构规则和 controlled natural language 结合，用于检测自然语言需求中的 smell，并在工业数据上进行了大规模评价。

启示：

- vague term；
- non-atomic；
- incomplete condition；
- incomplete system response；
- incorrect structure；

这类问题非常适合**低成本 Fast Scan**。

但 smell detection 不能替代场景探索。

### 7.2 LLM-as-a-Judge 可以用于质量属性评估，但不能单独成为 Gate

2026 年 Requirements Engineering 的实证工作已经使用独立 LLM evaluator 对 requirement 的 Unambiguity、Verifiability、Singularity 做自动质量评价。

启示：

- LLM 可以作为语义 reviewer；
- 但评价必须有明确 rubric；
- 独立 evaluator 比“同一生成 Agent 自我检查”更合理；
- 最终仍需 evidence、scope 和 severity 约束。

---

# 8. 最终方案：RGQ Requirement Quality Gate

## 8.1 Gate 目标

RGQ 的唯一核心目标：

> **在开发开始之前，发现那些会导致实现错误、用户错误结果、验收争议或后续高成本返工的需求缺陷。**

### 重点发现

- 缺失行为；
- 缺失异常场景；
- 状态/转换遗漏；
- 规则遗漏；
- 数据/边界条件遗漏；
- 外部依赖失败行为遗漏；
- 交互与 PRD 不一致；
- 多条需求互相矛盾；
- 无法确定正确结果；
- 不可验证/不可验收；
- 与 Brownfield 已知行为或直接约束冲突。

### 明确不做

- 不质疑需求有没有商业价值；
- 不重新定义产品目标；
- 不主动扩展本迭代 Scope；
- 不评审技术方案优劣；
- 不评审代码工程质量；
- 不生成实现方案；
- 不把“最好还可以支持 XXX”当 requirement defect。

---

# 9. Scope Guard：防止“场景探索 = 扩大需求”

这是整个 RGQ 最重要的安全边界。

任何新发现的候选场景必须存在至少一个 **Scope Anchor**：

```yaml
scope_anchor:
  requirement: REQ-xxx
  operation: 当前需求明确存在的操作
  business_object: 当前需求涉及的对象
  direct_dependency: 当前流程明确依赖的系统/资源/服务
  existing_behavior: Brownfield 中直接相关的已存在行为，可选
```

候选场景只有满足以下规则之一，才能进入 Gate：

1. 当前 operation 在不同合法状态下的行为；
2. 当前 operation 的直接失败路径；
3. 当前 operation 被中断、取消、重试、恢复；
4. 当前 operation 与明确依赖之间的异常；
5. 当前需求已经涉及的数据边界或权限边界；
6. Brownfield 中同一业务行为已有但 PRD 未说明的相关状态/约束；
7. 当前交互明确暴露但 PRD 未定义的结果。

以下内容必须排除：

- 新角色；
- 新业务能力；
- 新产品场景；
- 新商业规则；
- “以后可能有用”的能力；
- 仅因为 reviewer 想到就加入的 adjacent feature。

输出中必须包含：

```yaml
in_scope_reason: "为什么该问题属于本次需求"
```

没有 `in_scope_reason` 的 finding 不允许成为 P0/P1。

---

# 10. RGQ 执行架构

```text
PRD / Interaction / Requirement Docs
              │
              │ optional: Brownfield evidence
              ▼
┌───────────────────────────────┐
│ 0. Scope Guard               │
│ approved goal/scope boundary │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 1. Requirement Model Builder │
│ Req / AC / Scenario / Rule   │
│ State / Data / Dependency    │
│ UI transition / Unknown      │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 2. Fast Quality Scan         │
│ smells / ambiguity / local   │
│ completeness / verifiability│
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 3. Coverage Discovery        │
│ nominal / off-nominal       │
│ state / boundary / failure  │
│ interrupt / retry / recover │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 4. Cross-check               │
│ consistency / traceability   │
│ interaction / brownfield    │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 5. Independent Adjudicator   │
│ evidence / dedupe / severity │
│ scope check / confidence     │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│ 6. Gate Decision             │
│ P0/P1 => REVIEW_FAILED       │
│ P2/P3 => PASS_WITH_WARNINGS  │
└───────────────────────────────┘
```

---

# 11. Stage 1：Requirement Model Builder

不要直接对整篇 PRD 做自由式 Review。

首先把需求变成一个轻量、可检查模型：

```text
Requirement
 ├─ Actor
 ├─ Trigger
 ├─ Preconditions
 ├─ Main Behavior
 ├─ Observable Outcome
 ├─ Acceptance Criteria
 ├─ Business Rules
 ├─ State / Transition
 ├─ Data / Boundary
 ├─ External Dependency
 ├─ Interaction / UI Response
 └─ Unknown
```

同时维护关系：

```text
Requirement → Scenario
Requirement → Rule
Scenario → State
Scenario → Dependency
Scenario → Observable Outcome
Requirement → AC
UI Behavior ↔ Requirement
```

这一层的目的不是制造大量中间文档，而是给后续 Coverage Scan 提供结构。

---

# 12. Stage 2：Fast Quality Scan

Fast Scan 处理低成本、高确定性的质量问题。

## 12.1 规则类检查

- vague terms；
- open-ended clauses；
- 未定义术语；
- “etc.” / “normal” / “appropriate” / “及时”等不可验证表达；
- 条件缺失；
- 响应缺失；
- 一条 Requirement 混入多个独立义务；
- AC 没有可观察结果；
- UI 文案与 PRD 结果语义冲突。

## 12.2 Semantic checks

重点采用：

- Unambiguous；
- Local Complete；
- Verifiable；
- Correct relative to source；
- Local Consistency。

Fast Scan 找到的问题不应直接全部进入阻断列表，而是先成为 `candidate findings`。

---

# 13. Stage 3：Coverage Discovery —— RGQ 与普通 Checklist 的核心区别

Coverage Discovery 主动寻找“文档没写出来但当前需求必须回答”的问题。

## 13.1 标准探索维度

对于每一个主 Scenario，根据适用性选择探索：

### State

- before / during / after；
- first-time / existing；
- foreground / background；
- logged-in / logged-out；
- enabled / disabled；
- partially completed。

### Interruption

- user cancel；
- process killed；
- app exit；
- activity recreation；
- device reboot；
- task interrupted。

### Dependency

- unavailable；
- timeout；
- partial success；
- stale result；
- duplicated callback；
- response arrives late；
- remote success but local failure / reverse。

### Data

- empty；
- duplicate；
- stale；
- invalid；
- boundary；
- partial；
- incompatible version。

### Retry / Recovery

- retry；
- duplicate request；
- resume；
- reconciliation；
- rollback；
- idempotency。

### User-visible Oracle

最关键的问题始终是：

> **在这个条件下，用户最终应该看到什么？系统内部状态应该是什么？两者是否可能不一致？**

例如：

```text
上传云服务
   ↓
网络在 remote commit 前断开
   ↓
本地 callback / UI 如何判断？
   ↓
如果 UI 显示“上传完成”，remote 实际未成功
   ↓
这是本需求 Scope 内的严重需求缺口，而不是新增功能。
```

---

# 14. Brownfield 模式

Brownfield 是 RGQ 相对普通 PRD Review 的增强项。

## 14.1 可读取

- 当前代码中的业务状态/入口；
- API / callback / error contract；
- 旧需求文档；
- 当前交互；
- 历史 bug；
- existing tests；
- feature flag / platform constraint。

## 14.2 只用于回答

1. 当前需求触碰了哪些已有行为？
2. 是否存在 PRD 没说但系统一定会遇到的状态？
3. 是否存在直接依赖的失败模式？
4. PRD 是否与当前已知行为冲突？
5. 当前修改是否让一个已有 invariant 失去定义？

## 14.3 禁止

- 评论类设计好不好；
- 要求重构；
- 评价架构合理性；
- 将代码 smell 当需求问题；
- 因为代码支持某能力就要求 PRD 把它纳入 Scope。

---

# 15. Stage 4：Consistency / Traceability / Verifiability

检查三个层次。

## 15.1 文档内部

```text
Requirement ↔ AC
Requirement ↔ Rule
Scenario ↔ State
Scenario ↔ Observable Outcome
PRD ↔ Interaction
```

典型 Finding：

- PRD 说失败保持原状态，交互图却显示成功页；
- Rule A 说可重试，Rule B 说失败后任务终止；
- AC 只验证“按钮出现”，没有验证业务结果；
- requirement 写“上传成功”，但 success 的定义不存在。

## 15.2 跨文档

只检查需求相关制品：

- PRD；
- interaction；
- requirement appendix；
- policy/business rule；
- direct external contract（必要时）。

不在本 Gate 检查 Plan / Tasks / Code implementation completeness。

## 15.3 Verifiability

每一个 critical requirement 至少要能形成一个轻量 verification obligation：

```text
Given: 条件/状态
When: 行为/触发
Then: 可观察结果
Evidence: test / inspection / analysis / demonstration
```

这里不是生成 Test Case，而是在检查：

> **我们是否知道什么结果才算“对”？**

如果不知道，就是 requirement defect。

---

# 16. Stage 5：Independent Adjudicator

Discovery Agent 只能产生候选问题；Adjudicator 才决定 finding 是否成立。

每个 finding 必须经过：

```text
1. Scope check
2. Evidence check
3. Duplicate check
4. Counter-evidence search
5. Impact check
6. Severity classification
7. Confidence classification
```

## 16.1 Counter-evidence Search

在判定缺失之前，必须主动寻找：

- 是否在别的章节已经定义；
- 是否在 Interaction 中定义；
- 是否由明确统一规则覆盖；
- 是否由平台既定 contract 唯一决定；
- 是否是 reviewer 自己假设的问题。

这一步用于显著降低 false positive。

---

# 17. Finding 模型

推荐统一成：

```yaml
id: RGQ-F-001
severity: P1
category: SCENARIO_GAP
status: CONFIRMED

scope_anchor:
  requirement: REQ-12
  scenario: cloud-upload
  in_scope_reason: "网络是该上传操作的直接依赖，失败结果属于当前操作语义"

location:
  artifact: prd.md
  section: "Cloud Upload"

problem: >
  PRD 定义了上传成功 UI，但没有定义上传过程中网络断开时
  成功状态的判定以及恢复后的行为。

evidence:
  - "REQ-12 定义上传结束后显示 Uploaded"
  - "当前流程存在远端提交步骤"

risk: >
  UI 可能显示上传成功，但云端实际不存在文件，形成用户可见的错误成功状态。

missing_decision:
  - "什么条件才算 upload committed?"
  - "断网后 UI 状态是什么?"

verification_obligation: >
  在 remote commit 未确认时，系统不得向用户呈现最终成功状态。

confidence: HIGH
blocking: true
```

---

# 18. Finding 分类

建议不要创建过多一级分类。

## 一级分类

1. `INCOMPLETE`
2. `AMBIGUOUS`
3. `INCONSISTENT`
4. `UNVERIFIABLE`
5. `BROWNFIELD_CONFLICT`

## 二级标签

```text
SCENARIO
STATE
RULE
DATA
BOUNDARY
DEPENDENCY
INTERRUPTION
RETRY
RECOVERY
INTERACTION
NFR
TERMINOLOGY
TRACEABILITY
```

例如：

```text
INCOMPLETE / SCENARIO
INCOMPLETE / STATE
INCONSISTENT / INTERACTION
UNVERIFIABLE / RULE
BROWNFIELD_CONFLICT / DEPENDENCY
```

这样既保持模型精简，又保留分析价值。

---

# 19. Severity 与 Gate 规则

## P0

需求缺陷可能导致：

- 严重安全 / 隐私 / 合规问题；
- 不可恢复数据损坏或大面积错误；
- 核心业务无法形成安全且唯一的实现语义；
- 多个 requirement 对关键行为存在直接、不可调和冲突。

## P1

需求缺陷很可能导致：

- 核心用户流程产生明显错误结果；
- 成功/失败状态判断错误；
- 重复执行、遗漏执行、状态错误；
- 关键异常场景完全没有定义；
- 开发和测试对同一需求可以合理得出不同结果；
- 关键 AC 无法验收。

## P2

- 次要流程存在缺口；
- 有默认行为可以工作，但需求应补充；
- 对实现有风险但不大概率造成核心错误。

## P3

- 表述优化；
- 术语统一；
- 文档维护性；
- 非关键 singular / formatting 问题。

## Gate Decision

```text
存在任何 Confirmed P0/P1
        => REVIEW_FAILED

只有 P2/P3
        => PASS_WITH_WARNINGS

无有效 finding
        => PASS
```

禁止使用“平均质量分 > 80 就 PASS”。

**一个 P1 不能被十个满分项平均掉。**

---

# 20. Human-readable Report

报告必须先给结论，再给证据，而不是输出几十页 Checklist。

建议：

```markdown
# RGQ Review

Gate: REVIEW_FAILED
P0: 0
P1: 2
P2: 3
P3: 4

## Blocking Findings
### RGQ-F-001 [P1] Upload interruption behavior undefined
- Anchor
- Problem
- Evidence
- User impact
- Missing decision
- Suggested requirement clarification

## Non-blocking Findings
...

## Coverage Summary
- Scenarios reviewed
- State transitions reviewed
- Dependency failure paths reviewed
- Unknowns

## Excluded as Out-of-Scope
...
```

`Excluded as Out-of-Scope` 很重要，它让 reviewer 能看到 Agent 想到了什么，但确认这些内容**没有污染 Gate**。

---

# 21. Machine-readable Report

```yaml
schema_version: rgq.review.v1
review_target: feature-x

gate:
  result: REVIEW_FAILED
  review_failed: true
  blocking_findings:
    - RGQ-F-001
    - RGQ-F-004

summary:
  P0: 0
  P1: 2
  P2: 3
  P3: 4

coverage:
  requirements: 12
  scenarios: 19
  states: 8
  dependencies: 4
  unknowns: 3

findings: []

out_of_scope_candidates: []

review_metadata:
  mode: brownfield
  source_revision: <optional>
  reviewer: rgq-adjudicator
```

Human HTML/Markdown 和 JSON/YAML 必须来自同一份 finding ledger，避免两个报告互相不一致。

---

# 22. 性能与效率设计

如果每个需求都全量红军攻击，RGQ 很容易膨胀。

因此推荐三层执行。

## L0 Structural Scan

低成本：

- 文档结构；
- IDs；
- smell；
- terminology；
- obvious ambiguity；
- Req↔AC link。

## L1 Semantic Review

默认执行：

- completeness；
- consistency；
- verifiability；
- interaction alignment。

## L2 Targeted Red-team Coverage

仅针对以下高风险点展开：

- external dependency；
- async operation；
- stateful workflow；
- destructive operation；
- background execution；
- retry/recovery；
- cross-device/cloud；
- permission/security；
- data migration；
- Brownfield behavior change。

因此不是：

```text
每条需求 × 所有风险模式
```

而是：

```text
Requirement
   ↓
Risk Trigger Detection
   ↓
select relevant probes
   ↓
Targeted Challenge
```

这样可以提升效率，同时不明显降低有效问题发现率。

---

# 23. Red-team Review

下面对上述方案本身进行攻击。

## Attack 1：还是一个高级 Checklist，会漏未知场景

**问题成立。**

如果 Coverage Discovery 只是固定枚举网络、权限、重试，最终还是 Checklist。

### 修复

Coverage Discovery 分成两部分：

```text
Known Risk Probes
        +
Model-derived Counterexample Search
```

Agent 必须先根据 Requirement Model 生成：

- 关键状态；
- 关键不变量；
- 关键依赖；
- 成功 Oracle；

再尝试构造能打破 Oracle / invariant 的直接反例。

风险库用于召回，不限制探索空间。

---

## Attack 2：异常场景探索极易扩大 Scope

**这是最大风险。**

### 修复

引入强制 `Scope Anchor + in_scope_reason`。

没有 anchor：

```text
→ OUT_OF_SCOPE_CANDIDATE
→ 永远不能成为 blocker
```

---

## Attack 3：LLM 会制造“看起来合理”的 P1

**问题成立。**

### 修复

P0/P1 必须同时满足：

```text
explicit anchor
+ missing/contradictory behavior
+ concrete failure chain
+ observable impact
+ counter-evidence search passed
```

否则最多 P2 或 `NEEDS_CLARIFICATION`。

---

## Attack 4：同一个 Agent 找问题再给自己打分，会自证

**问题成立。**

### 修复

独立 Adjudicator；独立上下文；只读取 source + candidate ledger，不读取 discovery agent 的隐藏推理过程。

---

## Attack 5：引入 Brownfield 后会变成设计/代码 Review

**问题成立。**

### 修复

Brownfield evidence 只允许抽取：

```text
behavior
state
dependency
contract
constraint
historical failure
```

禁止产生：

```text
refactor suggestion
architecture critique
code smell
implementation optimization
```

---

## Attack 6：INCOSE 属性很多，会导致大量低价值噪声

**问题成立。**

### 修复

INCOSE 是 quality vocabulary，不是全部 blocker。

RGQ blocker 只围绕：

```text
ambiguity
incompleteness
inconsistency
unverifiability
brownfield conflict
```

Singular / Conforming 等默认降为 hygiene。

---

## Attack 7：Complete 是无限目标，永远可以再找一个场景

**问题成立。**

### 修复

RGQ 不追求“宇宙级 completeness”，定义为：

> **Within-scope sufficiency：对当前 Feature 明确操作、状态、直接依赖和已知风险，已足够支持唯一实现语义和可验证 Oracle。**

停止条件：

- 每个核心 requirement 有 observable outcome；
- 主 Scenario 有主要 off-nominal closure；
- 高风险 direct dependency 有失败语义；
- 关键 state transition 无 open decision；
- 没有 unresolved P0/P1。

---

## Attack 8：Severity 会被无限拔高

### 修复

严重度按照**结果影响**而不是“写得差不差”：

```text
P1 ≠ 需求写得很模糊
P1 = 该模糊会让核心行为出现两个合理实现，并可能产生明显错误结果
```

必须在 finding 中写出 impact chain。

---

## Attack 9：平均评分会掩盖局部致命问题

### 修复

评分只用于辅助诊断，不用于总分准出。

Gate 使用 blocker semantics：

```text
P0/P1 count > 0 => FAIL
```

---

## Attack 10：Review 太慢，团队最终关闭 Gate

### 修复

- risk-adaptive depth；
- deterministic scan 优先；
- only high-risk scenario gets deep challenge；
- finding dedup；
- 首屏只显示 blockers；
- P3 不进入主报告；
- 规则库/历史风险库只做召回，不逐条扫描所有规则。

---

# 24. 红军 Review 后的最终决策

最终保留以下设计：

1. **Gate boundary first** —— 先防 Scope 扩张；
2. **Requirement Model before Review** —— 不直接自由 Review 文档；
3. **Fast Scan + Coverage Discovery** —— 兼顾效率和遗漏发现；
4. **Scenario discovery 是核心差异化能力**；
5. **Brownfield 是 context evidence，不是 code review**；
6. **Independent Adjudicator** —— 防止自证；
7. **Evidence-first P0/P1** —— blocker 必须有因果链；
8. **P0/P1 hard gate** —— 不用平均分；
9. **Human + machine dual output**；
10. **Risk-adaptive execution** —— 避免 Gate 过重。

---

# 25. 推荐 Skill 结构

如果后续实现为生产级 Skill，推荐：

```text
skills/
└── rgq/
    ├── SKILL.md
    ├── references/
    │   ├── quality-model.md
    │   ├── scope-guard.md
    │   ├── coverage-probes.md
    │   ├── brownfield-policy.md
    │   ├── severity-rubric.md
    │   ├── adjudication-rules.md
    │   └── report-schema.md
    └── schemas/
        └── rgq-review.schema.json
```

不建议把 coverage / ambiguity / consistency 各自拆成独立 Skill。

它们应该是同一个 Requirement Gate 的内部阶段，因为：

- 共用 Requirement Model；
- 共用 scope boundary；
- findings 需要统一去重和裁决；
- severity 必须统一；
- 分散 Skill 容易重复扫描与互相矛盾。

如果需要并行 Agent，可在 Skill 内 dispatch，而不是暴露多个用户级 Skill。

---

# 26. 推荐运行模式

```text
/rgq-review <PRD / interaction docs>
```

自动判断：

```text
Greenfield
  → PRD + interaction review

Brownfield
  → PRD + interaction
  → bounded existing-system evidence scan
```

内部：

```text
build-model
→ fast-scan
→ risk-select
→ coverage-discovery
→ cross-check
→ adjudicate
→ gate
→ report
```

---

# 27. 成功指标

不要使用“发现了多少问题”作为主要 KPI，否则 Agent 会主动制造问题。

推荐指标：

### Finding Quality

- P0/P1 Valid Finding Rate；
- False Positive Rate；
- duplicate finding rate；
- out-of-scope finding rate。

### Escape

- 开发后才发现的 requirement defect 数；
- 测试阶段 requirement clarification 数；
- 上线后 root cause = requirement gap 的问题数。

### Efficiency

- review duration；
- 人工确认 finding 的时间；
- 每个有效 P0/P1 的 review cost。

### Coverage Yield

- 普通 quality scan 找到的问题；
- coverage discovery 额外找到的问题；
- Brownfield context 额外找到的问题。

其中最重要的实验是：

> **关闭 Coverage Discovery 与打开 Coverage Discovery 做 A/B，观察有效 P0/P1 增量。**

它能验证 RGQ 相比普通 checklist 的真正价值。

---

# 28. 最终定位

RGQ 不应成为：

```text
AI 帮你检查 PRD 有没有写规范
```

而应成为：

```text
Requirement Model
       ↓
Quality + Coverage Challenge
       ↓
Evidence-based Findings
       ↓
Independent Adjudication
       ↓
Requirement Delivery Gate
```

一句话定义：

> **RGQ 是一个以“防止错误需求进入开发”为目标、以 INCOSE 质量模型为底座、吸收 spec-kit 的职责分离、AI-DLC 的独立 Reviewer / Brownfield / Human Gate、以及工程化 scoring/report 思想，并强化 Scope 内场景缺口发现能力的需求交付 Gate。**

---

# 29. Sources

## GitHub spec-kit

- GitHub spec-kit — Agentic SDD reference  
  https://github.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md
- GitHub spec-kit — Quickstart  
  https://github.com/github/spec-kit/blob/main/docs/quickstart.md
- GitHub spec-kit repository  
  https://github.com/github/spec-kit

## AWS AI-DLC

- AI-DLC Introduction  
  https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/00-introduction.md
- AI-DLC Phases and Stages  
  https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/04-phases-and-stages.md
- AI-DLC Agents  
  https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/06-agents.md
- AI-DLC State and Audit  
  https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/10-state-and-audit.md
- AI-DLC Workflow Profiles  
  https://github.com/awslabs/aidlc-workflows/blob/main/docs/guide/workflow-profiles.md

## INCOSE / ISO / NASA

- INCOSE Guide to Writing Requirements v4  
  https://portal.incose.org/Web/iCore/Store/StoreLayouts/Item_Detail.aspx?Category=EBOOKS&iProductCode=GUIDEWRITEREQ
- INCOSE Requirements Working Group — Poorly Formed Requirements Assessment / GtWR material  
  https://www.incose.org/docs/default-source/working-groups/requirements-wg/monthlymeetings2024/gtwr_bad_rqmt_assessment_lir_012924.pdf
- NASA Software Engineering Handbook — Software Requirements  
  https://swehb.nasa.gov/spaces/SWEHBVD/pages/102695421/SWE-050+-+Software+Requirements
- NASA Systems Engineering Handbook — How to Write a Good Requirement  
  https://www.nasa.gov/reference/system-engineering-handbook-appendix/

## Engineering implementations

- Microsoft HVE Core — ISO 29148 Quality Gate  
  https://github.com/microsoft/hve-core/blob/main/.github/skills/project-planning/requirements-author/references/brd/iso-29148-quality-gate.md
- Microsoft HVE Core — PRD Quality Report  
  https://github.com/microsoft/hve-core/blob/main/.github/skills/project-planning/requirements-author/references/prd/prd-quality-report-v1.md

## Research

- Veizaga, Shin, Briand — Automated Smell Detection and Recommendation in Natural Language Requirements, IEEE TSE, 2024  
  https://doi.org/10.1109/TSE.2024.3361033
- Paiva et al. — From issue titles to requirements: an empirical study of LLMs and prompt engineering strategies, Requirements Engineering, 2026  
  https://link.springer.com/article/10.1007/s00766-026-00462-z
