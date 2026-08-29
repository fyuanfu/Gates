# Gate1 设计探索问题清单

> 目的：记录 Gate1（Engineering Readiness Gate）在进入最终 Spec 前已经讨论的问题、已确认决策，以及仍需判断是否继续探索的开放问题。

## 1. 已确认的核心问题与决策

### Q1. Gate1 的评审对象是什么？
**决策：** Requirement / Spec + Technical Design / SDD。  
Gate1 不只评审 PRD，而是判断进入编码前的工程输入是否足够。

### Q2. Engineering Ready 的核心含义是什么？
**决策：** 实现者可以在不做未经授权关键决策的情况下，根据现有输入完成确定性实现，并且实现结果原则上可验证。

### Q3. 什么问题应该阻断 Gate1？
**决策：** 不是所有文档缺陷都阻断。仅当继续实现会迫使开发者/Agent 猜测、越权决策或导致关键行为无法验证时，形成 Blocker。

### Q4. Agent 是否可以自行做决策？
**决策：** 可以，但必须受显式 Decision Authority 约束：
- Agent Autonomous
- Policy Constrained
- Human Required

### Q5. Gate1 的 Gap 顶层分类是什么？
**决策：**
- Specification Gap
- Decision Gap
- Verification Gap

Quality Dimension（完整性、明确性、一致性、正确性、可实现性、可验证性、可追溯性）作为问题表现维度，而不是顶层 Gap 分类。

### Q6. Specification Gap 是否需要细分？
**决策：** 需要按实现依赖的信息对象细分，例如：
- Behavior / Scenario
- Rule
- State
- Data / Contract
- Dependency
- Constraint
- Error / Recovery
- Non-functional
- Design

### Q7. Decision Gap 如何分类？
**决策：** 决策类型和决策权限分离。

Decision Type 示例：
- Behavioral
- Business Rule
- Architecture
- Contract
- Risk / Safety
- Implementation

Decision Authority：
- Agent Autonomous
- Policy Constrained
- Human Required

### Q8. Gate1 对 Oracle / 可验证性的要求到什么程度？
**修订后的决策：** 根据 Artifact Responsibility 分层。

#### Spec / Requirement
要求：
- Expected Outcome
- Success Criterion
- Verification Obligation

回答：**什么算正确？**

不要求具体测试接口、Assertion 或 Executable Oracle。

#### Technical Design / SDD
进一步要求将关键行为映射到：
- Observable State
- Output
- Contract
- Invariant
- Engineering Observation Point

回答：**系统中的什么现象能够证明它正确？**

#### Implementation / Test
Executable Oracle、Assertion、Evaluator 和测试代码进入 Gate2/实现测试阶段。

### Q9. Gate1 Verdict 如何表达？
**决策：**
- READY
- READY WITH RISKS
- NOT READY

不使用总分代替门禁结论。

### Q10. Gate1 是一个统一 Gate 还是多个 Gate？
**决策：** 一个 Gate，两个 Readiness Profile：
- Spec Readiness
- Design Readiness

最终合并为 Engineering Ready Verdict。

### Q11. 是否所有变更都必须有 SDD？
**决策：** 否。根据变更复杂度和风险判断是否需要显式 Design Artifact。

### Q12. Spec Ready 检查什么？
**决策：** 评审语义责任，而不是章节模板：
- Intent
- Behavior
- Rules
- State
- Boundary
- Verification

### Q13. Design Ready 检查什么？
**决策：**
- Responsibility
- Interaction
- Contract
- State & Data
- Failure Handling
- Constraints
- Observability

### Q14. Spec 和 Design 是否需要追踪关系？
**决策：** 关键行为必须可追踪到 System Responsibility / Design Element，但不强制固定模板或 ID 格式。

### Q15. Finding 应按哪里发现还是按问题责任来源分类？
**决策：** 按缺陷责任来源分类。发现位置与 Gap Ownership 分离。

### Q16. Spec Gap Discovery 基于什么？
**决策：** 结构化语义模型 + 挑战式探索，而不是纯模板检查或 LLM 自由脑暴。

### Q17. 缺少一个场景是否自动成为 Finding？
**决策：** 否。必须通过 Materiality Test：
1. 场景属于当前 Feature 合理运行域；
2. 现有事实不能唯一决定结果；
3. 缺失会产生有意义的实现分叉或验证不确定性。

### Q18. Specification Gap 与 Decision Gap 如何区分？
**决策：**
- 已有行为方向但表达不完整/含糊 → Specification Gap
- 存在两个以上合理合法方案，现有证据无法唯一决定 → 默认 Decision Gap

### Q19. Design Gap Discovery 从哪里开始？
**决策：** 从 Responsibility Closure 出发：
Responsibility → Ownership → Interaction → Contract → State/Data → Failure Semantics → Observability。

### Q20. Cross-artifact consistency V1 检查什么？
**决策：**
- Coverage
- Contradiction
- Semantic Drift
- Unowned Responsibility

### Q21. 一个合格 Finding 需要什么 Evidence？
**决策：** Finding 至少包含：
- Claim
- Evidence
- Gap Type
- Rule Violated
- Impact
- Required Resolution

LLM 判断本身不能单独作为阻断证据。

---

## 2. 已确认的知识输入模型

Gate1 不应只使用 Review Artifacts，还需要 Knowledge Inputs。

### A. Review Artifacts
- PRD / Spec
- AC / Scenario
- SDD / Technical Design

### B. Project Knowledge
- Architecture
- Existing Contracts
- Constraints
- ADR
- Existing behavior / state / data model

### C. Governance Knowledge
- Decision Authority
- Engineering Policies

### D. Challenge Knowledge
- Domain scenarios
- Risk Patterns
- Failure Modes

### E. Historical Evidence
- Critical bugs
- Incidents
- Historical failure patterns

### 知识权威分级
- **Authoritative Knowledge**：可作为事实证据
- **Constraint Knowledge**：可用于判定规则违反
- **Heuristic Knowledge**：只能触发 Challenge，不能单独形成 Blocking Finding

核心不变量：

> Heuristic knowledge may generate questions, but must not independently generate blocking findings.

---

## 3. 进入最终 Spec 前的收口评审

以下问题此前提出过，但尚未显式确认。经收口评审，它们中有一部分会直接改变 Gate1 的 Verdict 行为，因此不能简单视为实现细节。

### OQ1. 多源知识发生冲突时，权威优先级如何确定？
例如：
- Spec 与 ADR 冲突
- SDD 与现有 Contract 冲突
- 代码现实与文档声明冲突
- Policy 与历史行为冲突

**为什么必须决策：**  
如果没有优先级，Agent 无法判断“谁是事实”，也无法稳定地产生 Contradiction Finding。

**建议默认：**
1. Explicit governance / mandatory policy
2. Approved current requirement/spec（定义目标行为）
3. Approved ADR / architecture constraints
4. Approved technical design
5. Current external/API/data contracts
6. Current implementation behavior（只描述 As-Is，不自动覆盖目标 Spec）
7. Historical behavior
8. Heuristic / best practice

冲突本身必须显式报告，不能静默覆盖。

### OQ2. Blocker / Warning / Risk 的确定性规则是什么？
**为什么必须决策：**  
已经定义 Gap，但还没有完整 Severity → Verdict Algorithm。

**建议默认：**
- 导致未经授权决策 → Blocker
- 导致关键行为无法判定正确性 → Blocker
- 违反 Mandatory Policy / Contract → Blocker
- 设计责任关键链路未闭合 → Blocker
- 非关键文档质量问题 → Warning
- 已明确理解、可接受且有 Owner 的剩余风险 → Accepted Risk

### OQ3. READY WITH RISKS 的 Risk Acceptance 权限是谁？
**为什么必须决策：**  
否则 Agent 可以自行把 Blocker 降成 Risk，绕过 Gate。

**建议默认：**
- Agent 不得自主接受 Blocking Risk
- 只有显式授权的 Human / Role / Policy 可以 Risk Accept
- Risk Acceptance 必须记录 owner、reason、scope、expiry/reevaluation condition

### OQ4. Decision Authority Policy 的匹配失败怎么办？
例如一个新的决策类型不在规则库里。

**为什么必须决策：**  
这是 Agent 是否继续实现的安全默认值。

**建议默认：**
> Fail closed：无法匹配到明确授权时，默认 Human Required。

### OQ5. Knowledge Freshness / Provenance 最低要求是什么？
**为什么必须决策：**  
过时架构、旧 Contract 或历史规则可能制造错误 Blocker。

**建议默认：**
每条可作为 Blocking Evidence 的知识至少具有：
- source
- scope
- authority/type
- version or timestamp（如适用）
- applicability
- status: active / deprecated / superseded

无法确认 freshness 的知识只能降级为 Challenge / Warning Evidence。

---

## 4. 收口结论

当前仍存在 5 个会改变 Gate1 运行语义和 Verdict 的开放决策：
1. Knowledge Conflict Precedence
2. Severity / Blocking Rules
3. Risk Acceptance Authority
4. Unknown Decision Authority 默认行为
5. Knowledge Provenance / Freshness

这些问题不是低层实现细节，而是 Gate1 的安全边界和门禁判定规则。

不过它们都可以由当前已经确认的原则唯一推导出一个保守的一致方案。若采用本文件中的“建议默认”，则不需要继续进行新一轮探索，可以直接进入最终 Spec。
