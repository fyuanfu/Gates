# Gate1 Engineering Readiness Gate — Specification

## 1. Problem Statement

AI Agent 在软件开发过程中，即使需求、技术设计或关键决策信息不完整，也可能继续编码，并通过合理化假设自行补齐缺失内容。

这会导致以下问题：

- 需求意图被错误解释；
- Agent 越权做出产品、架构、风险或契约决策；
- Spec 与 Technical Design 之间存在遗漏、冲突或语义漂移；
- 关键行为虽然能够实现，但完成后无法明确判断是否正确；
- 文档 Review 停留在“完整性、清晰性”等表层质量检查，不能真正回答“现在是否可以安全开始实现”。

Gate1 需要解决的核心问题不是“文档质量是否足够高”，而是：

> 当前工程输入是否已经达到 Engineering Ready，使实现者无需做未经授权的关键决策，即可依据现有信息完成确定性实现，并且实现结果原则上可被验证。

---

## 2. Goal

Gate1 是 **Engineering Readiness Gate**。

其目标是：

> 在编码开始前，识别并阻断会迫使实现者猜测、越权决策或导致关键行为无法验证的工程输入缺口，确保当前变更已经具备足够明确、完整、一致、可实现且可验证的实现依据。

Gate1 的最终问题只有一个：

> **Can implementation safely start?**

---

## 3. Non-Goals

Gate1 不负责：

- 证明代码实现已经正确；
- 执行完整自动化测试；
- 要求所有 Feature 都编写完整 SDD；
- 要求所有 PRD 提供接口级 Assertion；
- 用总分代替准出判断；
- 自动把行业最佳实践转化为项目 Requirement；
- 让 LLM 自由脑补并直接生成 Blocking Finding；
- 替代 Gate2 的代码、测试实现和执行验证。

---

## 4. Core Invariants

### 4.1 No Unauthorized Decision

如果继续实现需要做出一个未被显式授权的关键决策，Gate1 必须阻断。

### 4.2 Fail Closed on Unknown Authority

如果某个 Decision Gap 无法匹配明确的 Decision Authority Policy，则默认：

> **Human Required**

Agent 不得自行假定拥有决策权限。

### 4.3 Evidence Required for Blocking

Blocking Finding 必须具有可审计 Evidence。

LLM 判断、通用最佳实践或启发式知识本身不能单独形成 Blocker。

### 4.4 Heuristic Knowledge Is Challenge-Only

> Heuristic knowledge may generate questions, but must not independently generate blocking findings.

### 4.5 Artifact Responsibility Determines Verification Depth

不同文档使用不同 Verification 标准：

- Spec / Requirement：定义 **什么算正确**
- Technical Design / SDD：定义 **系统中的什么可观察条件能够证明正确**
- Implementation / Test：定义 **如何执行判断**

### 4.6 Missing Documentation Is Not Automatically a Gap

缺少某个章节、Scenario、Diagram 或字段本身不构成 Blocking Finding。

只有当缺失造成实质性实现分叉、未经授权决策或验证不确定性时，才形成 Readiness Gap。

### 4.7 Conflict Must Be Surfaced

当多个权威输入冲突时，不允许静默选择其中一个。

冲突本身必须成为 Finding，并进入 Resolution。

### 4.8 Risk Cannot Silently Downgrade a Blocker

Agent 无权自行把 Blocking Gap 标记为 Accepted Risk。

Risk Acceptance 必须由显式授权的角色或 Policy 完成。

---

## 5. Gate Scope

Gate1 是一个统一 Gate，内部包含两个 Readiness Profile：

```text
                 Gate1
                   |
          +--------+--------+
          |                 |
   Spec Readiness      Design Readiness
          |                 |
          +--------+--------+
                   |
          Engineering Ready
```

### 5.1 Spec Readiness

判断业务和行为意图是否已经闭合。

### 5.2 Design Readiness

判断系统责任和工程实现边界是否已经闭合。

### 5.3 Conditional Design Requirement

并非所有变更都要求独立 Technical Design / SDD。

Gate1 必须先判断：

> Does this change require an explicit technical design artifact?

通常以下变化应要求 Design：

- 跨模块责任变化；
- 新数据模型或 Schema Migration；
- 状态机变化；
- API / Contract 变化；
- 数据一致性变化；
- 新基础设施或外部依赖；
- 并发、性能、安全、可靠性关键设计；
- 高风险或难以回滚的架构变化。

低风险、局部且遵循既有模式的变更可以仅通过 Spec Readiness。

---

## 6. Inputs

### 6.1 Review Artifacts

Gate1 可以接受：

- PRD
- Product Spec
- Engineering Spec
- User Story
- Acceptance Criteria
- Scenario / Flow
- Technical Design
- SDD
- API / Data Contract
- Design Decision

不强制固定文档模板。

### 6.2 Project Knowledge

用于描述当前系统事实：

- Current Architecture
- Existing Contracts
- Data Model
- State Model
- Existing Feature Behavior
- Platform Constraints
- Approved ADR
- Module Responsibilities

### 6.3 Governance Knowledge

用于定义强约束和 Agent 权限：

- Engineering Policy
- Architecture Policy
- Security Policy
- Compatibility Policy
- Reliability Policy
- Decision Authority Policy

### 6.4 Challenge Knowledge

用于主动寻找潜在盲点：

- Domain Scenarios
- Risk Patterns
- Failure Modes
- Platform Failure Patterns
- Common Boundary Conditions

### 6.5 Historical Evidence

用于针对项目历史真实失败进行重点挑战：

- Critical Bugs
- Incidents
- Regressions
- Historical Failure Patterns

---

## 7. Knowledge Authority Model

Gate1 必须区分知识的使用权限。

### 7.1 Authoritative Knowledge

可作为事实 Evidence。

示例：

- Approved Spec
- Current Contract
- Approved ADR
- Current architecture declaration

### 7.2 Constraint Knowledge

可用于判定规则违反。

示例：

- Mandatory engineering policy
- Security policy
- Compatibility requirement
- Decision authority rule

### 7.3 Heuristic Knowledge

只能用于产生 Candidate Challenge。

示例：

- Industry best practice
- Generic LLM knowledge
- Common failure pattern
- Historical analogy
- Community recommendation

### 7.4 Source Precedence

默认优先级：

1. Mandatory Governance / Policy
2. Approved Current Requirement / Spec — 定义目标行为
3. Approved ADR / Architecture Constraints
4. Approved Technical Design
5. Current External / API / Data Contract
6. Current Implementation Behavior — 描述 As-Is，不覆盖目标 Spec
7. Historical Behavior / Historical Defect
8. Heuristic / Best Practice

若不同来源发生冲突：

> 不直接按优先级静默覆盖，而是利用优先级判断 Authority，同时生成 Conflict Finding。

---

## 8. Knowledge Provenance Requirements

任何可能用于 Blocking Finding 的知识至少必须具有：

- source
- knowledge_type
- authority
- scope
- applicability
- status: active / deprecated / superseded
- version 或 timestamp（适用时）

如果 freshness 或 applicability 无法确认：

> 该知识不得单独用于 Blocker，只能降级为 Challenge 或 Warning Evidence。

---

## 9. Spec Readiness Model

Gate1 不要求 Spec 必须包含固定章节，而是检查语义责任是否闭合。

### 9.1 Intent

必须能够明确：

- 用户或业务目标；
- 变更意图；
- 成功结果。

### 9.2 Behavior

关键行为必须能够确定：

- 主路径；
- 条件变化；
- 必要异常路径；
- 操作结果。

### 9.3 Rules

必须明确影响行为选择的：

- Business Rule
- Preconditions
- Boundary Conditions
- Rule Priority
- Invariants

### 9.4 State

如果 Feature 涉及状态变化，必须能够确定：

- Relevant States
- Legal Transitions
- Key Invalid Transitions
- Recovery State

不要求文档必须显式使用 State Machine 格式。

### 9.5 Boundary

对当前 Feature 实质相关的边界必须定义，例如：

- failure
- cancellation
- retry
- duplicate operation
- dependency unavailable
- interruption
- concurrency

是否必须定义由 Materiality Test 决定。

### 9.6 Verification

关键 Requirement / Scenario / Rule 必须能够回答：

> 什么结果算正确？

至少形成：

```text
Behavior
  -> Verification Obligation
  -> Expected Outcome / Success Criterion
```

Spec 不要求具体 Test Seam、Assertion 或 Executable Oracle。

---

## 10. Design Readiness Model

Design Readiness 判断需求责任是否已被系统设计充分承接。

### 10.1 Responsibility

每个关键需求责任必须存在明确系统 Owner。

### 10.2 Interaction

需要跨组件协作的行为必须定义关键 Interaction。

### 10.3 Contract

跨边界交互必须定义必要 Contract，包括：

- input/output
- error semantics
- data semantics
- ordering
- idempotency（适用时）
- compatibility（适用时）

### 10.4 State & Data

必须明确关键：

- state ownership
- persistence
- consistency
- lifecycle
- migration

### 10.5 Failure Handling

对实质相关失败模式，必须明确：

- failure semantics
- retry
- rollback
- fallback
- recovery
- partial failure

### 10.6 Constraints

关键工程约束必须被设计承接，例如：

- performance
- security
- compatibility
- resource
- reliability
- platform constraints

### 10.7 Observability

关键设计责任必须能够回答：

> 系统中的什么可观察状态、输出、Contract 或 Invariant 能够证明该责任成立？

这形成 **Engineering-level Verification**。

Design 阶段不要求具体测试代码。

---

## 11. Verification Maturity Model

### Level 1 — Behavioral Verification

适用于 Requirement / Spec。

回答：

> What is correct?

产物：

- Expected Outcome
- Success Criterion
- Verification Obligation

### Level 2 — Engineering Verification

适用于 Technical Design / SDD。

回答：

> What observable system condition proves it?

产物：

- Observable State
- Output
- Contract
- Invariant
- Observation Point

### Level 3 — Executable Verification

属于 Implementation / Gate2。

回答：

> How does the test judge it?

产物：

- Test Seam
- Assertion
- Evaluator
- Test Implementation
- Runtime Evidence

Gate1 不要求 Level 3 完成。

---

## 12. Gap Taxonomy

### 12.1 Specification Gap

意图已经存在，但未被充分表达或约束。

可细分为：

- Behavior Gap
- Scenario Gap
- Rule Gap
- State Gap
- Data / Contract Gap
- Dependency Gap
- Constraint Gap
- Error / Recovery Gap
- Non-functional Gap
- Design Specification Gap

### 12.2 Decision Gap

存在多个合理、行为不同的合法方案，而现有 Evidence 无法唯一决定。

Decision Type 包括：

- Behavioral Decision
- Business Rule Decision
- Architecture Decision
- Contract Decision
- Risk / Safety Decision
- Implementation Decision

### 12.3 Verification Gap

分为：

#### Behavioral Verification Gap
不知道什么结果算正确。

#### Engineering Verification Gap
知道业务正确结果，但在要求 Design 的场景下无法映射到系统可观察条件。

#### Executable Verification Gap
知道观测点，但缺少可执行测试机制。

Executable Verification Gap 通常属于 Gate2，不单独阻断 Gate1。

---

## 13. Quality Dimensions

Quality Dimension 用于描述 Finding 的表现形式，而不是顶层 Gap 类型。

包括：

- Completeness
- Clarity
- Consistency
- Correctness
- Feasibility
- Verifiability
- Traceability

每个 Finding 可以同时具有：

```text
Gap Type: Decision Gap
Dimension: Completeness
```

---

## 14. Gap Discovery Engine

### 14.1 Semantic Extraction

先从输入文档提取结构化语义：

- Intent
- Actor
- Scenario
- Rule
- State
- Data
- Boundary
- Expected Outcome
- Responsibility
- Contract
- Constraint
- Observation

### 14.2 Structured Challenges

针对不同语义对象执行 Challenge Rules。

示例：

#### Scenario Challenge
- normal path
- failure
- cancellation
- duplicate trigger
- interrupted execution
- dependency unavailable

#### State Challenge
- initial state
- legal transition
- invalid transition
- intermediate state
- recovery state

#### Rule Challenge
- condition completeness
- boundary value
- rule conflict
- rule priority

### 14.3 Materiality Test

Candidate Gap 必须通过：

1. 该问题属于当前 Feature 合理运行域；
2. 现有 Evidence 无法唯一确定结果；
3. 缺失会导致实质性实现分叉、关键风险或验证不确定性。

否则不形成 Blocking Finding。

### 14.4 Evidence Resolution

Challenge 产生 Candidate 后，必须搜索：

- 当前 Artifact
- 关联 Artifact
- Approved Requirement
- Design
- Project Knowledge
- Policy
- Contract
- ADR

只有经过 Evidence Resolution 才能升级为正式 Finding。

---

## 15. Specification Gap vs Decision Gap Algorithm

```text
Undefined / ambiguous issue
        |
        v
Search authoritative evidence
        |
        v
Can outcome be uniquely derived?
   | YES
   +----> No Decision Gap
   |
   NO
   |
   v
Is behavior direction already fixed,
but details are incomplete?
   | YES
   +----> Specification Gap
   |
   NO
   |
   v
Are two or more materially different
valid choices still possible?
   | YES
   +----> Decision Gap
```

工程默认：

> 如果存在两个以上合理合法行为选择，且 Evidence 无法排除其中任何一个，则默认 Decision Gap。

---

## 16. Design Responsibility Closure

Design Gap Discovery 不从“是否有 Diagram”开始，而从责任闭环开始：

```text
Requirement Responsibility
        ->
Ownership
        ->
Interaction
        ->
Contract
        ->
State / Data
        ->
Failure Semantics
        ->
Observability
```

关键责任链任何必要环节断裂，都形成 Candidate Design Gap。

---

## 17. Cross-Artifact Consistency

V1 至少检查：

### 17.1 Coverage

Requirement / Scenario 是否被 Design 承接。

### 17.2 Contradiction

Design 是否违反 Spec、Policy 或 Contract。

### 17.3 Semantic Drift

相同概念在不同 Artifact 中语义是否发生未说明变化。

### 17.4 Unowned Responsibility

Spec 定义了责任，但 Design 没有明确系统 Owner。

---

## 18. Traceability

Gate1 不强制统一 ID 或 Trace Matrix 格式。

但关键行为必须能够建立：

```text
Requirement / Scenario
        ->
System Responsibility
        ->
Design Element
```

映射可以来源于：

- Explicit ID
- Section Reference
- Semantic Mapping
- Trace Table

若关键行为无法找到 Design Responsibility，则形成 Coverage / Unowned Responsibility Finding。

---

## 19. Decision Authority Model

### 19.1 Agent Autonomous

Agent 可以在授权范围内自行选择。

典型：

- 私有命名；
- 等价局部代码结构；
- 不改变外部行为的实现细节。

### 19.2 Policy Constrained

Agent 只有在满足明确规则时才能自行决定。

典型：

- 已有架构模式内的技术选择；
- 有明确默认配置的工程参数；
- Policy 已约束的兼容策略。

### 19.3 Human Required

影响下列任一内容时，默认需要 Human Decision，除非 Policy 明确授权：

- external behavior
- business rule
- user-visible semantics
- persistent data semantics
- security / privacy
- compatibility contract
- system architecture boundary
- material reliability risk
- irreversible / costly-to-reverse decision

### 19.4 Unknown Authority

无法匹配 Authority Rule：

> Human Required.

---

## 20. Finding Model

一个正式 Finding 至少包含：

```text
Finding
- id
- claim
- gap_type
- gap_subtype
- quality_dimension
- source_artifact
- discovered_from
- evidence[]
- rule_violated
- impact
- decision_authority
- severity
- required_resolution
- status
```

### 20.1 Evidence

Evidence 应尽量指向具体：

- artifact
- section
- statement
- rule
- contract
- knowledge source

### 20.2 Gap Ownership

Finding 按问题责任来源分类，而不是按在哪里发现分类。

例如：

> 在 Design Review 中发现 Requirement 没定义跨设备删除行为

应记录：

```text
Gap Type: Specification Gap
Source Artifact: Requirement
Discovered From: Design Analysis
```

---

## 21. Severity and Blocking Rules

### 21.1 Blocker

以下情况默认 Block：

- 继续实现需要未经授权的 Decision；
- 关键行为无法确定 Expected Outcome；
- Mandatory Policy 被违反；
- Current Contract 被违反且无批准变更；
- Requirement 与 Design 存在影响行为的矛盾；
- 关键 Design Responsibility 未闭合；
- 要求 Design 的变更缺少必要 Design；
- 关键知识冲突尚未 Resolution；
- 关键 Engineering Verification 无法建立。

### 21.2 Warning

例如：

- 非关键描述不够清晰；
- 不影响实现选择的文档质量问题；
- 可验证但追踪表达弱；
- Heuristic Challenge 未得到足够 Evidence；
- freshness 不足、但尚不足以证明冲突。

### 21.3 Accepted Risk

必须满足：

- 风险已明确；
- 影响已理解；
- 有授权 Role / Human 接受；
- 有 owner；
- 有 reason；
- 有 scope；
- 有 expiry 或 reevaluation condition（适用时）。

Agent 不得自行接受 Blocking Risk。

---

## 22. Verdict Algorithm

### READY

满足：

- 无 unresolved Blocker；
- 所有 Human Required Decision 已 Resolution；
- Required Design 已 Ready；
- Behavioral Verification 已闭合；
- 要求 Design 时，关键 Engineering Verification 已闭合。

### READY WITH RISKS

满足：

- 无 unresolved Blocker；
- 存在明确、已授权接受的剩余风险；
- Risk Acceptance Evidence 完整。

### NOT READY

存在任一：

- unresolved Blocker；
- unauthorized Decision Gap；
- blocking Specification Gap；
- blocking Behavioral Verification Gap；
- required Engineering Verification Gap；
- unresolved mandatory Policy / Contract conflict。

不采用 0–100 分作为最终准出依据。

---

## 23. Processing Pipeline

```text
Review Artifacts
      +
Knowledge Pack
      |
      v
Artifact Classification
      |
      v
Design Requirement Assessment
      |
      v
Semantic Extraction
      |
      v
Structured Challenges
      |
      v
Materiality Test
      |
      v
Evidence Resolution
      |
      v
Gap Classification
      |
      v
Cross-Artifact Analysis
      |
      v
Decision Authority Check
      |
      v
Severity / Risk Acceptance
      |
      v
Verdict
```

---

## 24. User Stories

1. As a developer, I want Gate1 to tell me whether the current inputs are sufficient to start implementation, so that I do not need to guess product or design intent.
2. As an AI coding agent, I want explicit Decision Authority rules, so that I know when I may decide and when I must stop.
3. As a requirement author, I want Gate1 to identify material behavioral gaps, so that I can resolve them before implementation.
4. As an architect, I want Gate1 to detect design responsibilities that are not closed, so that critical system decisions are not deferred into code.
5. As a tester, I want key behavior to have clear Verification Obligations before coding, so that correctness is judgeable later.
6. As a quality owner, I want every Blocking Finding to contain evidence and violated rules, so that Gate decisions are auditable.
7. As a product owner, I want business decisions to remain human-controlled unless explicitly delegated, so that Agent behavior does not silently redefine the product.
8. As a developer, I want small low-risk changes to avoid unnecessary SDD ceremony, so that Gate1 does not impose documentation overhead without value.
9. As a reviewer, I want Requirement and Design to use different verification maturity standards, so that reviews remain appropriate to artifact responsibility.
10. As a quality owner, I want historical defects and risk patterns to challenge new changes, so that recurring blind spots are identified early.
11. As a reviewer, I want heuristic knowledge to generate questions but not blockers, so that generic AI knowledge does not override project truth.
12. As an architect, I want Spec and Design coverage to be checked, so that every critical requirement responsibility has a system owner.
13. As a developer, I want conflicting project knowledge to be surfaced explicitly, so that the system does not silently choose stale or incorrect sources.
14. As a gate owner, I want READY WITH RISKS to require authorized risk acceptance, so that blockers cannot be bypassed by Agent reclassification.
15. As a quality owner, I want Gate1 to produce deterministic Verdict rules, so that the same critical gap does not randomly pass or fail depending on prompt wording.

---

## 25. Implementation Decisions

### 25.1 Architecture

Implement Gate1 as a staged analysis pipeline rather than a single LLM prompt.

Logical components：

- Artifact Classifier
- Knowledge Resolver
- Semantic Extractor
- Design Requirement Assessor
- Challenge Engine
- Materiality Evaluator
- Evidence Resolver
- Gap Classifier
- Cross-Artifact Analyzer
- Decision Authority Resolver
- Severity Engine
- Verdict Engine
- Report Generator

### 25.2 Rule + LLM Hybrid

LLM responsibilities：

- semantic extraction
- candidate scenario generation
- semantic mapping
- contradiction hypothesis generation
- reasoning explanation

Deterministic / policy responsibilities：

- authority resolution
- mandatory rule evaluation
- severity mapping
- blocker determination
- risk acceptance validation
- final Verdict

### 25.3 Evidence First

Candidate Finding 不能直接进入 Verdict。

必须经过 Evidence Resolution。

### 25.4 Explicit Knowledge Types

Knowledge ingestion 必须保留 authority、scope、source、freshness 和 status。

### 25.5 Traceability Without Mandatory Format

内部可以建立 canonical trace graph，但不要求输入文档采用固定模板。

### 25.6 V1 Knowledge Scope

V1 只要求：

1. Project Facts
2. Decision Policy
3. Review Rules
4. Risk Patterns
5. Historical Critical Failures

不在 V1 建设大而全的企业知识图谱。

---

## 26. Testing Decisions

### 26.1 Test External Gate Behavior

测试应围绕 Gate1 的可观察行为，而不是 LLM 内部推理过程。

### 26.2 Required Test Areas

至少覆盖：

- Artifact classification
- Spec vs Design readiness profile
- Design-required decision
- Specification Gap classification
- Decision Gap classification
- Verification Gap classification
- Materiality filtering
- Knowledge authority handling
- Conflict detection
- Decision Authority resolution
- Unknown Authority fail-closed behavior
- Severity mapping
- Risk Acceptance authorization
- Verdict calculation
- Evidence completeness

### 26.3 Golden Scenario Tests

建立一组固定输入 Artifact + Knowledge Pack，验证：

- Expected Findings
- Expected non-Findings
- Expected Severity
- Expected Verdict

### 26.4 Adversarial Tests

至少包括：

- LLM 使用最佳实践制造伪 Blocker；
- 过时 Knowledge 与当前 Spec 冲突；
- Agent 尝试把 Human Required Decision 解释成实现细节；
- Missing Scenario 但实际不 material；
- 多个合理方案但 Agent 擅自选择；
- READY WITH RISKS 缺少授权；
- Design 缺失但变更实际上不需要 Design；
- Spec 已定义行为但 Design 语义漂移。

---

## 27. Outputs

### 27.1 Human-readable Report

至少包含：

- Verdict
- Blocking Findings
- Accepted Risks
- Warnings
- Missing Decisions
- Verification Gaps
- Cross-artifact inconsistencies
- Evidence references
- Required resolutions

### 27.2 Machine-readable Output

至少包含：

- artifact classification
- design_required
- findings[]
- decisions[]
- risk_acceptances[]
- traceability[]
- verdict
- evidence[]

---

## 28. Out of Scope for V1

- 自动生成完整测试代码；
- 自动执行 Gate2 测试；
- 自动修改 Requirement / SDD；
- 自动代表 Human 接受 Risk；
- 自动改变 Approved ADR / Policy；
- 维护完整企业知识图谱；
- 在线生成所有测试用例；
- 用代码覆盖率代替 Requirement Readiness；
- 对所有场景做无限制 LLM Brainstorm。

---

## 29. Acceptance Criteria

### AC1 — Unauthorized Decision Blocking

Given 当前输入存在两个以上合理且行为不同的合法方案  
And 无 Evidence 能唯一确定方案  
And Decision Authority 不是 Agent Autonomous 或 Policy Constrained  
When Gate1 执行  
Then Finding 必须被分类为 Decision Gap  
And Verdict 不得为 READY。

### AC2 — Heuristic Knowledge Cannot Block Alone

Given 一个 Candidate Gap 仅由通用最佳实践或 LLM 知识支持  
And 无 Authoritative / Constraint Evidence  
When Gate1 执行  
Then 该问题不得单独形成 Blocking Finding。

### AC3 — Materiality Filtering

Given 文档未描述一个潜在边界场景  
But 该场景不会造成有意义的实现分叉、关键风险或验证不确定性  
When Gate1 执行  
Then 不得因为“文档未写”直接 Block。

### AC4 — Spec Verification Standard

Given 输入是 Requirement / Spec  
When Gate1 检查可验证性  
Then 应要求 Expected Outcome / Success Criterion  
And 不得要求具体 Assertion 或测试接口。

### AC5 — Design Verification Standard

Given 输入包含 Required Technical Design  
When Gate1 检查关键行为  
Then 应能够映射到 Observable State / Output / Contract / Invariant  
And 不要求测试代码已实现。

### AC6 — Conditional Design Requirement

Given 变更低风险、局部且遵循现有设计模式  
When Gate1 评审  
Then 不得仅因为缺少独立 SDD 而 Block。

Given 变更涉及高风险架构、Contract、数据或状态变化  
When 缺少必要 Design  
Then Gate1 必须产生 Blocking Finding。

### AC7 — Cross-artifact Contradiction

Given Spec 与 Design 对同一关键行为定义矛盾  
When Gate1 执行  
Then 必须产生 Contradiction Finding  
And 在 Resolution 前 Verdict 为 NOT READY。

### AC8 — Unknown Authority Fail Closed

Given Decision Gap 无法匹配任何 Authority Rule  
When Gate1 处理  
Then authority 必须默认为 Human Required。

### AC9 — Risk Acceptance Authorization

Given 一个 Blocking Risk 被标记为 Accepted Risk  
But 缺少授权主体或 Acceptance Evidence  
When Gate1 计算 Verdict  
Then 不得进入 READY WITH RISKS。

### AC10 — Evidence-backed Findings

Given 一个 Blocking Finding  
Then 输出必须包含 Claim、Evidence、Gap Type、Rule Violated、Impact 和 Required Resolution。

### AC11 — Knowledge Freshness

Given 一个知识源的 freshness / applicability 无法确认  
When 它是唯一支持 Blocker 的 Evidence  
Then Gate1 不得仅依赖该知识 Block。

### AC12 — Final Verdict

Given 无 unresolved Blocker  
And 所有 Human Required Decision 已解决  
And 所有 Required Readiness Profile 均满足  
When Gate1 计算 Verdict  
Then 输出 READY 或 READY WITH RISKS。

Given 存在任一 unresolved Blocker  
Then 输出 NOT READY。

---

## 30. Success Metrics

建议 V1 重点观察：

- Blocking Finding precision
- False-block rate
- Human-confirmed material gap recall
- Unauthorized-decision catch rate
- Cross-artifact inconsistency detection rate
- Evidence completeness rate
- Verdict reproducibility
- Risk-acceptance bypass rate
- Gate1 引入的额外评审成本

不建议使用“发现问题数量”作为核心成功指标。

---

## 31. Further Notes

Gate1 的核心价值不是把文档变得更完美，而是降低：

> **Implementation Decision Entropy**

即在编码开始前，把所有会改变外部行为、系统契约、关键风险或验证结果的未授权选择显式化并完成 Resolution。

因此 Gate1 最终应被看作一个：

> **Evidence-grounded Engineering Readiness Decision System**

而不是传统的 AI 文档 Review Bot。
