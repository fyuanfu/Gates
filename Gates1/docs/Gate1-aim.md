# Gate1 目标总结（Gate1-aim）

## 1. 文档目的

本文档用于定义 Gate1 的顶层目标、检查逻辑与准出边界，回答以下问题：

1. Gate1 最终要证明什么？
2. Gate1 需要完成哪些证明义务？
3. Gate1 实际检查哪些对象？
4. 发现的问题如何分类？
5. 什么情况下应当阻断进入实现？
6. Gate1 不负责证明什么？

本文档当前聚焦“目标定义”，不展开具体 Agent 实现、Prompt、规则库结构和报告格式。

---

## 2. Gate1 的总目标

### 2.1 总体目标：Engineering Ready

Gate1 的目标不是检查“文档写得是否漂亮”，也不是证明 Feature 已经实现正确，而是判断：

> **当前需求与设计定义是否已经达到 Engineering Ready，能够安全进入实现阶段。**

Engineering Ready 的工作性定义为：

> **进入实现所需要的关键行为、关键决策、验收依据和工程约束已经达到足够成熟度，不要求研发在编码过程中猜关键业务行为，也不要求测试在后续阶段猜什么才算正确，同时不存在已知的关键工程约束冲突。**

因此，Gate1 的核心价值是：

- 将需求与设计中的关键缺口前移到编码前暴露；
- 阻止研发在信息不足时自行补业务或架构决策；
- 为后续实现、测试和 Gate 验证建立明确的判断基线；
- 降低“代码已经写完后才发现需求没定义清楚”的返工。

---

## 3. Gate1 的核心原则

### 3.1 Gate1 不是“找文档问题”，而是证明是否可进入实现

Missing、Ambiguous、Inconsistent 等问题分类只是 Finding 的表现形式。

Gate1 真正要回答的是：

> **这个 Spec 是否已经具备进入实现的条件？**

因此 Gate1 必须先定义“需要证明什么”，再定义“检查什么对象”，最后定义“问题以什么形式出现”。

---

## 4. Gate1 的总体结构

Gate1 建议采用以下四层结构：

```text
                Gate1 总目标
             Engineering Ready
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
 Discovery Adequacy      Definition Readiness
                                │
               ┌────────────────┼────────────────┬────────────────┐
               ↓                ↓                ↓                ↓
       Behavior Coverage  Decision Closure  Acceptance      Constraint /
                                            Determinacy     Feasibility
               │
               ↓
            检查对象
 Scenario / Rule / State / Data / Contract /
 Dependency / NFR / UI / AC / Interface ...
               │
               ↓
            Finding 属性
 Missing / Ambiguous / Inconsistent / Invalid
```

这里需要明确：

- **证明义务**：Gate1 要证明什么；
- **检查对象**：实际被检查的需求/设计元素；
- **Finding 属性**：检查失败时问题表现为什么类型。

三者不能混为一层。

---

# 5. Gate1 的证明义务

## 5.1 Discovery Adequacy：探索充分性

### 目标

在当前 Scope、已有领域知识、已知风险模式和工程上下文下，对需求空间进行规定深度的系统性探索。

它解决的问题是：

> **我们是不是只检查了“已经写出来的东西”，却根本没有探索那些应该被考虑的问题？**

### 为什么必须有这一层

如果只检查 Closure，可能出现：

```text
未解决 Scenario：0
未解决 Decision：0
未定义 Oracle：0
```

但真实原因只是：

> 根本没有探索失败场景、状态空间、边界条件和风险模式。

因此：

> **Closure 不等于 Coverage。**

### Gate1 可以承诺的程度

Gate1 不承诺穷尽所有 Unknown Unknown。

Gate1 应承诺：

> 在当前 Scope、已有领域知识、已知风险模式和规定的探索维度下，已经完成系统性挑战，不存在明显未被探索的高影响空间。

### 典型探索维度

包括但不限于：

- Flow / User Journey
- Scenario
- State / State Transition
- Rule / Invariant
- Data / Contract
- Boundary
- Failure / Recovery
- Dependency
- Permission
- Concurrency / Timing
- Compatibility
- Performance / Reliability
- Security / Privacy
- Known Risk Pattern

---

## 5.2 Behavior Coverage：行为覆盖

### 目标

明确系统在当前 Scope 下需要支持哪些关键行为。

核心问题：

> **事情考虑全了吗？**

### 主要检查内容

包括：

- 主流程是否定义；
- 关键异常是否定义；
- 边界条件是否定义；
- 关键状态转换是否定义；
- 已知风险模式是否有对应行为；
- 组合条件下是否存在明显行为缺口。

### PASS 的工作性标准

> 当前 Scope + 已知领域规则 + 已知风险模式能够推导出的关键场景，均已被显式描述；不存在已经识别但尚未进入 Spec 的高影响行为。

### 不承诺

不承诺：

> 所有可能场景已经穷尽。

---

## 5.3 Decision Closure：决策闭合

### 目标

确保实现阶段不再遗留需要研发自行决定的关键业务、状态、契约或策略问题。

核心问题：

> **遇到这些情况，到底应该怎么办，已经决定了吗？**

例如：

- 部分成功还是整体回滚；
- 重试几次；
- 数据冲突以哪一侧为准；
- 状态失败后进入什么状态；
- 权限被拒绝后如何处理；
- PRD、UI、技术设计冲突时哪一个是权威来源。

### PASS 的工作性标准

> 不存在会导致研发在实现阶段自行决定关键业务行为、状态语义、接口契约、错误处理或验收结果的高影响未决问题。

可以进一步压缩为：

> **研发不需要猜。**

### Gate1 的责任边界

Gate1：

- 负责发现未决策问题；
- 负责识别决策影响；
- 负责确定是否阻断。

Gate1 不负责：

> 替产品、架构或业务 Owner 做所有业务决策。

### 重要边界

Decision Closure 保证：

> **关键决策已经完成。**

但不保证：

> **这个决策一定是最佳决策。**

因此：

> Decision Closure ≠ Decision Optimality。

---

## 5.4 Acceptance Determinacy：验收可判定性

### 目标

确保后续实现完成后，能够客观判断是否做对。

核心问题：

> **以后怎么证明它是对的？**

### 主要检查内容

每个关键行为应能够形成：

```text
Scenario
   ↓
Expected Behavior
   ↓
Observable Result
   ↓
Oracle / Acceptance Criterion
```

### PASS 的工作性标准

> 每个关键场景都存在明确、可观察、可判定的验收依据，不依赖测试人员或研发人员临场解释“什么算正确”。

可以进一步压缩为：

> **测试不需要猜。**

### Gate1 不负责什么

Gate1 负责定义：

> **怎么判对。**

Gate1 不负责证明：

> **代码已经做对。**

后者属于 Gate2 / Gate3 等后续验证阶段。

---

## 5.5 Constraint / Feasibility Closure：约束与可实现性闭合

### 目标

确保已经定义清楚的行为，在当前已知工程约束下不存在明显不可实现或约束冲突。

核心问题：

> **这个定义即使很完整、很明确，也真的能做吗？**

例如：

- 平台能力不支持；
- 上游接口不存在；
- 关键数据无法获得；
- 性能指标明显不可达到；
- 权限模型与方案冲突；
- 安全/隐私规范不允许；
- 依赖团队没有承诺；
- 既有领域 Invariant 与新设计冲突。

### PASS 的工作性标准

> 当前已知平台、架构、数据、依赖、安全、性能等关键约束不存在已确认的阻断性冲突；关键外部依赖具备明确的可实现路径或已获得承诺。

### 边界

Gate1 不需要完成完整实现验证，也不需要证明最终性能已经达标。

Gate1 要判断的是：

> **当前定义是否存在已知的工程不可实现性或关键约束冲突。**

---

# 6. 检查对象

Behavior / Decision / Acceptance 不是实际检查对象，而是证明义务。

Gate1 实际需要检查的对象包括：

| 检查对象 | 主要作用 |
|---|---|
| Scope | 定义当前 Feature 的边界 |
| Story / Goal | 描述用户目标和业务价值 |
| Flow / Journey | 暴露端到端路径空间 |
| Scenario | 描述具体可验证行为 |
| Rule | 描述业务约束与条件 |
| Invariant | 描述不可被破坏的约束 |
| State / Transition | 描述生命周期与状态变化 |
| Data / Business Object | 描述数据语义和对象关系 |
| Contract / Interface | 描述系统边界与接口契约 |
| UI / Interaction | 描述用户可见行为与交互 |
| Dependency | 描述上下游依赖 |
| NFR | 描述性能、可靠性、安全等非功能要求 |
| Acceptance Criterion | 描述验收边界 |
| Oracle | 描述正确性的判定依据 |

不同证明义务会作用于不同对象，同一个对象也可能同时接受多个证明义务的检查。

---

# 7. Finding 分类

Gate1 Finding 建议至少包括以下四类：

## 7.1 Missing

该定义本来必须存在，但缺失。

例如：

- 部分失败场景未定义；
- 状态转换未定义；
- 关键接口契约缺失；
- 场景没有验收标准。

---

## 7.2 Ambiguous

已经有定义，但无法唯一解释。

例如：

- “适当重试”；
- “及时刷新”；
- “友好提示”；
- “性能良好”。

不同实现者可能得到不同理解。

---

## 7.3 Inconsistent

多个来源对同一问题存在冲突。

例如：

- PRD 说失败整体回滚；
- 技术设计说允许部分成功；
- AC 又按全部成功验收。

---

## 7.4 Invalid / Incorrect

定义本身完整、明确、一致，但违反已知事实、平台约束、领域规则或权威契约。

例如：

- 违反 Android 平台权限限制；
- 违反既有领域 Invariant；
- 与已经确认的 API Contract 冲突；
- 与安全或隐私规则冲突。

### Important

Invalid / Incorrect 必须基于明确的权威依据，例如：

- Platform Constraint
- Domain Rule / Invariant
- Architecture Decision
- API Contract
- Security / Privacy Requirement
- Approved Upstream Commitment

不得基于 Agent 主观偏好判定“产品设计不好”。

---

# 8. 证明义务与 Finding 的关系

Finding 分类不能代替 Gate1 的证明义务。

正确关系是：

```text
证明义务
   ↓
作用于检查对象
   ↓
检查失败
   ↓
Finding
   ↓
Missing / Ambiguous / Inconsistent / Invalid
   ↓
Impact / Severity
   ↓
Block / Warn / Info
```

因此：

> **证明义务定义 Gate1 要证明什么。**

> **检查对象定义 Gate1 在哪里寻找证据。**

> **Finding 分类定义失败以什么形式表现。**

---

# 9. 为什么不能只按照 Finding 分类直接找问题

仅扫描 Missing / Ambiguous / Inconsistent / Invalid 存在一个根本问题：

> **它们没有定义“什么东西本来就应该存在”。**

例如 Agent 被要求：

> Find all missing things.

它仍然需要知道：

- 哪些 Scenario 应该存在；
- 哪些状态必须定义；
- 哪些决策应该闭合；
- 哪些验收标准必须存在；
- 哪些约束必须检查。

因此 Finding Taxonomy 只能回答：

> **问题长什么样。**

而不能回答：

> **应该检查哪些问题空间。**

如果没有证明义务和检查对象模型，Gate1 很容易退化为：

> 文档找茬工具。

而不是：

> Engineering Ready Gate。

---

# 10. Gate1 的准出逻辑

Gate1 的最终 Verdict 建议遵循：

```text
Discovery Adequacy
       ↓
Behavior Coverage
       ↓
Decision Closure
       ↓
Acceptance Determinacy
       ↓
Constraint / Feasibility Closure
       ↓
Finding Impact Assessment
       ↓
PASS / BLOCK / PASS WITH WARNING
```

---

# 11. Blocking 原则

Gate1 不应该因为任何 Finding 都阻断。

建议只有满足以下条件之一时才 Block：

### 11.1 行为缺失会显著改变实现范围

例如：

- 关键失败场景缺失；
- 核心状态缺失；
- 高风险边界未定义。

### 11.2 未决策问题会迫使研发自行做关键决定

例如：

- 业务规则；
- 状态语义；
- 数据一致性策略；
- 关键接口契约；
- 错误恢复策略。

### 11.3 缺少可判定的验收依据

导致后续无法客观判断实现是否正确。

### 11.4 已发现明确的工程约束冲突

例如：

- 平台能力不支持；
- 安全规范冲突；
- 外部依赖无法满足；
- 关键性能要求明显不可实现。

---

# 12. Gate1 的非目标

Gate1 不承担以下职责：

### 12.1 不保证所有 Unknown Unknown 被发现

Gate1 只能通过系统性探索降低未知空间，而不能证明探索穷尽。

### 12.2 不证明最终实现正确

代码正确性属于后续实现验证和 Gate2 / Gate3。

### 12.3 不替业务 Owner 做关键业务决策

Gate1 负责发现 Decision Gap 和阻断，而不是擅自补齐产品决策。

### 12.4 不保证决策最优

Gate1 关注：

> 是否有决策。

不是：

> 是否做出了理论上的最佳决策。

### 12.5 不要求设计在 Gate1 阶段达到实现级细节

Gate1 的标准是：

> 足够支撑安全实现。

不是：

> 所有代码结构、接口细节、测试代码都已经提前完成。

---

# 13. Gate1 的一句话定义

管理汇报版本：

> **Gate1 用于保证进入开发前，该考虑的关键行为已经被系统性探索，该决定的关键问题已经决定，该验收的行为已经定义清楚，而且这些定义不存在已知的关键工程约束冲突。**

进一步压缩：

> **研发不需要猜怎么做，测试不需要猜怎么算对，而且当前方案不存在已知的关键不可实现问题。**

---

# 14. 当前模型的关键结论

当前 Gate1 模型建议明确以下结论：

1. **Gate1 总目标是 Engineering Ready，而不是文档质量检查。**
2. **Discovery Adequacy 是 Closure 的前置条件。**
3. **Behavior Coverage、Decision Closure、Acceptance Determinacy、Constraint/Feasibility Closure 是 Gate1 的核心证明义务。**
4. **Scenario、Rule、State、Data、Contract、Dependency、NFR、AC 等才是实际检查对象。**
5. **Missing / Ambiguous / Inconsistent / Invalid 是 Finding 属性，而不是 Gate1 顶层目标。**
6. **Finding 是否阻断必须进一步依据 Impact / Severity 判断。**
7. **Gate1 不承诺穷尽 Unknown Unknown，也不承担实现正确性证明。**

---

# 15. 后续仍需继续决策的问题

在进入正式 Spec 前，仍建议继续探索以下问题：

1. 四类核心证明义务之间是否存在重叠，应如何划清边界；
2. 每类证明义务具体覆盖哪些检查对象；
3. Discovery Adequacy 如何定义最低探索深度；
4. Behavior Coverage 的“关键场景”如何判定；
5. Decision Gap 中哪些允许 Agent 自行决定，哪些必须人工决策；
6. Acceptance Determinacy 在 Gate1 阶段要求到 AC、Oracle 还是 Test Obligation 的哪一层；
7. Feasibility Closure 要做到“无已知冲突”还是需要正向可行性证据；
8. Invalid / Incorrect 的权威知识源范围如何限定；
9. Finding 的 Severity 和 Block / Warn / Info 规则如何定义；
10. Gate1 自身如何提供 Evidence，证明检查已经覆盖规定空间。

---

## 16. 当前状态

**状态：目标模型已基本形成，但尚未冻结。**

目前已经完成：

- Gate1 总目标定义；
- 顶层证明义务定义；
- 检查对象与证明义务分层；
- Finding 分类模型；
- 基本 Blocking 原则；
- Gate1 非目标与责任边界。

建议完成第 15 节剩余决策后，再进入正式 Gate1 Spec。
