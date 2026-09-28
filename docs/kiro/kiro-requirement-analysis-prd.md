# Kiro Requirements Analysis
## 功能需求文档

**文档性质**：根据 Kiro 官方公开资料反向整理  
**目标功能**：Analyze Requirements  
**所在阶段**：

```text
Feature Intent
     ↓
requirements.md
     ↓
★ Requirements Analysis
     ↓
design.md
     ↓
tasks.md
     ↓
Implementation
```

---

# 1. 背景

Kiro Spec 工作流将软件开发过程划分为 Requirements、Design 和 Tasks 等阶段。

`requirements.md` 是后续 Design 和 Implementation 的需求依据。

即使 Requirement 已经采用 User Story 和 EARS Acceptance Criteria 的结构化形式表达，仍可能存在以下问题：

- Requirement 粒度不合适；
- Requirement 存在多种合理解释；
- 多条 Requirement 之间存在逻辑冲突；
- Requirement 依赖未明确表达的概念、行为或假设；
- 部分输入、状态、失败条件或边界场景没有定义系统行为。

这些问题如果在 Design 或 Implementation 后才发现，将导致不同实现者——包括 AI Coding Agent——基于不同理解自行补充决策。

因此，需要在进入 Design 之前提供一个独立的 **Requirements Analysis** 阶段，对整个 Requirement Set 进行深度分析。

---

# 2. Goal

Requirements Analysis SHALL 在进入 Design 前分析 `requirements.md`，发现可能导致错误实现或不同实现的 Requirement 问题，并通过用户可理解的澄清问题将这些问题显式化。

系统 SHALL 帮助用户识别：

```text
Wrong level of detail
Ambiguity
Logical inconsistency
Conflicting constraints
Unstated assumptions
Completeness gaps
Missing edge cases
Unexpected accepted/rejected behaviors
```

Requirements Analysis SHALL NOT 替用户决定最终业务意图。

**用户是 Requirement Intent 的最终 Oracle。**

系统负责发现：

```text
“这里存在一个需要决定的问题”
```

用户负责决定：

```text
“正确的需求应该是什么”
```

---

# 3. Scope

Requirements Analysis 的输入范围 SHALL 为当前 Spec 中的完整 `requirements.md`。

系统 SHALL 同时分析：

```text
Single Requirement
+
Acceptance Criteria within one story
+
Requirements across stories
+
Interactions between requirements
```

系统 SHALL NOT 仅逐条独立检查 Requirement。

跨 Requirement 的逻辑关系属于本功能的核心分析范围。

---

# 4. Preconditions

WHEN 用户已经生成 `requirements.md`

THE SYSTEM SHALL 提供 **Analyze Requirements** 入口。

Analyze Requirements SHALL 位于：

```text
Requirements
        ↓
Analyze Requirements
        ↓
Design
```

用户 MAY 跳过 Requirements Analysis，直接进入 Design。

Requirements Analysis SHALL 是一个可选步骤，而不是所有 Spec 强制执行的步骤。

---

# 5. Requirement Quality Refinement

## 5.1 Observable Behavior

WHEN Requirement 仅表达高层目标而没有明确可观察行为

THE SYSTEM SHALL 标记 Requirement 的粒度不足。

例如：

```text
The system shall support authentication.
```

系统 SHALL 判断该 Requirement 是否能够明确识别：

```text
Trigger / Input
Condition
Expected observable behavior
```

---

## 5.2 Excessive Implementation Detail

WHEN Requirement 描述具体实现机制，而不是系统必须表现出的行为

THE SYSTEM SHALL 识别该 Requirement 中的 implementation detail。

例如：

```text
The system shall implement soft deletion
using a deleted flag in the database.
```

系统 SHOULD 引导 Requirement 表达为 observable behavior，而不是指定实现方案。

Requirement SHOULD 尽可能保持：

```text
WHAT
而不是
HOW
```

---

## 5.3 Testability

THE SYSTEM SHALL 判断 Acceptance Criterion 是否能够转换成可验证的行为约束。

一个可测试 Requirement SHOULD 能够识别：

```text
Input / Event
Condition / State
Expected Behavior / Output
```

---

## 5.4 EARS Structure

WHEN Requirement 使用 EARS notation

THE SYSTEM SHALL 检查条件、事件、状态以及系统响应之间的语义关系。

系统 MAY 对不适合当前语义的 EARS Pattern 提出修改建议。

---

# 6. Ambiguity Analysis

## 6.1 Multiple Plausible Interpretations

WHEN 一个 Requirement 存在多个合理且语义不同的解释

THE SYSTEM SHALL 将该 Requirement 标记为 Ambiguous。

例如：

```text
The system shall remove the record.
```

可能意味着：

```text
Interpretation A:
record no longer exists

Interpretation B:
record remains stored
but is no longer visible to the user
```

系统 SHALL NOT 任意选择其中一个解释作为用户真实意图。

---

## 6.2 Multiple Formalizations

THE SYSTEM SHALL 能够针对同一个 Requirement 生成多个 Formal Interpretation。

系统 SHALL 比较这些 interpretation 的逻辑语义，而不仅比较文本差异。

例如：

```text
A ∧ B
```

与：

```text
B ∧ A
```

SHALL NOT 因表达顺序不同而被认为存在语义歧义。

---

## 6.3 Semantic Divergence

WHEN 两个合理 interpretation 在某些输入或系统状态下会产生不同结果

THE SYSTEM SHALL 找到能够区分这些 interpretation 的 scenario。

系统 SHOULD 将该 semantic difference 转换为用户能够理解的具体问题。

例如：

```text
删除后，该记录是否仍需要保留供管理员访问？
```

而不是仅提示：

```text
“remove” 存在歧义。
```

---

## 6.4 Unable to Reliably Interpret

WHEN Requirement 可以产生大量彼此不同、无法形成稳定语义的 Formal Interpretation

THE SYSTEM SHALL abstain from selecting an interpretation。

系统 SHALL 请求用户重新明确 Requirement，而不是猜测其含义。

---

# 7. Logical Consistency Analysis

## 7.1 Cross-Requirement Conflict

THE SYSTEM SHALL 判断是否存在某个有效状态，使两个或多个 Requirement：

```text
同时被触发
AND
要求互不兼容的结果
```

例如：

```text
R1:
IF inventory unavailable
THEN order SHALL be backordered

R2:
Order SHALL never be backordered
```

WHEN：

```text
inventory unavailable
```

两条 Requirement 同时适用

THE SYSTEM SHALL 识别该 Requirement Set 存在 logical inconsistency。

---

## 7.2 Conflicting Constraints

THE SYSTEM SHALL 检测 Functional Requirement 与其他 Functional / Non-functional Constraint 之间不能同时满足的情况。

WHEN 不存在任何 implementation 能够同时满足相关 Requirement

THE SYSTEM SHALL 将其报告为 Conflict。

---

## 7.3 Conflict Localization

WHEN 系统发现 Logical Conflict

THE SYSTEM SHOULD 标识：

```text
涉及哪些 Requirements
+
导致冲突的条件或状态
+
两个 Requirement 分别要求什么行为
```

系统 SHOULD 尽可能将 Finding 缩小到直接参与冲突的 Requirement 集合。

---

# 8. Unstated Assumption Analysis

WHEN Requirement 引用了未定义的概念、状态、行为或前提

THE SYSTEM SHALL 将其识别为潜在的 Unstated Assumption。

例如 Requirement：

```text
WHEN the owner deletes a property...
```

但 Specification 没有定义：

```text
什么构成 owner
property ownership 如何确定
删除时 property 是否一定存在
```

系统 SHOULD 将这些隐含前提显式化，以便用户确认：

```text
这是有意的 domain assumption
还是
Specification 中遗漏的信息
```

系统 SHALL NOT 自动将隐含假设视为真实业务规则。

---

# 9. Completeness Analysis

## 9.1 Behavioral Coverage Gap

THE SYSTEM SHALL 搜索是否存在有效的输入/状态组合，使 Specification 中没有任何具体 Requirement 定义系统行为。

形式上：

```text
存在 Scenario S

AND

没有 Requirement 定义
System 在 S 中应该做什么
```

WHEN 存在这种情况

THE SYSTEM SHALL 产生 Completeness Finding。

---

## 9.2 Missing Edge Cases

THE SYSTEM SHALL 特别分析 Happy Path 之外的场景，包括：

```text
Failure modes
Boundary conditions
Concurrent access
Invalid input/state
Exceptional conditions
```

WHEN 一个合理 edge case 没有对应行为定义

THE SYSTEM SHALL 将其作为 Missing Edge Case 提交给用户确认。

---

## 9.3 Intentional Silence

WHEN Specification 对某种 Scenario 没有定义行为

THE SYSTEM SHALL NOT 自动认定该 Requirement 一定错误。

系统 SHALL 询问用户该 silence 是：

```text
A. Intentional
B. Missing Requirement
```

---

# 10. Scenario Analysis

系统 SHALL 基于 Formal Requirement Model 分析具体行为 Scenario。

---

## 10.1 Accepted Scenario

THE SYSTEM SHALL 能够生成满足当前 Requirement Set 的具体行为 Scenario。

即：

```text
Scenario S
      +
Current Specification
      ↓
SAT
```

表示当前 Specification **允许** Scenario S。

---

## 10.2 Rejected Scenario

THE SYSTEM SHALL 能够生成被当前 Requirement Set 禁止的具体行为 Scenario。

即：

```text
Scenario S
      +
Current Specification
      ↓
UNSAT
```

表示当前 Specification **不允许** Scenario S。

---

## 10.3 Surprising Scenario

WHEN 一个 accepted 或 rejected Scenario 与 User Story 所表达的目标相比表现异常或值得怀疑

THE SYSTEM SHOULD 将该 Scenario 提交给用户确认。

例如：

```text
Current Specification allows:
fresh data exists
but cached data is still returned
```

系统 SHOULD 询问用户：

```text
Is this behavior intended?
```

而不是自行修改 Requirement。

---

# 11. Finding Types

Requirements Analysis SHALL 至少能够产生以下用户可见 Finding：

```text
1. Ambiguity
2. Logical inconsistency / Conflict
3. Unstated assumption
4. Completeness gap
5. Missing edge case
6. Accepted scenario requiring confirmation
7. Rejected scenario requiring confirmation
```

Requirement Refinement 阶段还 SHOULD 识别：

```text
Wrong level of detail
Non-testable requirement
Solution/implementation leakage
```

---

# 12. Finding Presentation

WHEN 一个 Finding 已准备完成

THE SYSTEM SHALL 将其逐步输出到 Chat，而无需等待完整分析结束。

每一个 Finding SHOULD 包含：

```text
① 涉及的 Requirement
② 问题的自然语言解释
③ 能够触发问题的具体情况（适用时）
④ 推荐的解决选项
```

系统 SHALL 隐藏内部 Formal Logic、SMT Encoding 和 Solver 细节。

用户无需理解 formal methods 即可完成需求澄清。

---

# 13. Clarification Interaction

每个需要业务 Intent 判断的 Finding SHALL 被转换成一个用户可以直接回答的问题。

系统 SHOULD 优先提供有限的具体选项。

例如：

```text
“remove the record” 当前有两种解释：

A. Permanently delete the record
B. Retain the record but hide it from normal users

Which behavior do you intend?
```

用户 SHALL 能够：

```text
选择建议选项
输入自定义答案
dismiss finding
```

WHEN 用户认为 ambiguity 是有意存在的

THE SYSTEM SHALL 允许用户 dismiss 该问题。

---

# 14. Requirement Update

WHEN 用户解决一个 Finding

THE SYSTEM SHALL 根据用户选择更新 `requirements.md`。

更新后的 Requirement SHALL 将用户刚刚做出的 Intent Decision 显式表达出来。

系统 SHALL 避免让该决策继续停留为：

```text
implicit assumption
```

或者：

```text
conversation-only knowledge
```

---

# 15. Re-analysis

WHEN 用户手工修改 `requirements.md`

THE SYSTEM SHALL 允许再次执行 Analyze Requirements。

重新分析时，系统 SHALL 分析：

```text
modified requirements
+
their interactions with other requirements
```

以判断修改是否：

```text
解决原 Finding
产生新的 conflict
产生新的 ambiguity
改变 completeness
```

---

# 16. Formal Analysis Requirements

系统内部 MAY 使用 Formal Logic 表达 Requirement。

Acceptance Criteria SHOULD 被映射为类似：

```text
Antecedent
    ⇒
Consequent
```

例如：

```text
order_submitted
AND inventory_available
    ⇒
order_fulfilled
```

Formal Model SHOULD 包含：

```text
Schema
Assertions
Background Assertions
```

系统 MAY 使用 SMT Solver 对 Formal Model 执行：

```text
Satisfiability checking
Logical equivalence checking
Conflict detection
Completeness analysis
Scenario generation
```

Formal Model 属于内部分析机制，SHALL NOT 要求用户直接编辑或理解 SMT 表达。

---

# 17. Domain Assumption Handling

系统 SHALL 考虑 Requirement 中没有显式表达、但 Logical Analysis 所依赖的 Domain Knowledge。

例如：

```text
duration cannot be negative

an order cannot be refunded before payment

certain system states are mutually exclusive
```

WHEN Domain Assumption 不能从 Requirement 中可靠确定

THE SYSTEM SHOULD 谨慎使用该 assumption。

系统 SHALL 避免仅因为未经确认的 background assumption 而确定业务 Intent。

---

# 18. Non-goals

Requirements Analysis SHALL NOT：

```text
替用户确定产品需求

自动选择多个合理需求解释中的“正确答案”

将技术实现方案作为业务 Requirement

要求用户阅读 SMT / Formal Logic

证明业务 Intent 本身是正确的

替代后续 Design Review

验证最终 Code 是否正确实现 Requirement
```

Requirements Analysis 的目标是：

```text
Requirement Quality
&
Requirement Intent Clarification
```

而不是：

```text
Implementation Verification
```

---

# 19. User-visible End State

Requirements Analysis 完成后，用户 SHOULD 获得一个经过澄清的 `requirements.md`。

该 Requirement Set SHOULD 相比分析前：

```text
more testable
more explicit
less ambiguous
logically consistent
better covered
```

用户确认完成后，可以继续：

```text
requirements.md
      ↓
Proceed to Design
      ↓
design.md
```

---

# 20. Core Success Criterion

Requirements Analysis 的成功标准不是：

```text
“AI 判断 Requirements 是正确的”
```

而是：

```text
对于能够通过 Requirement 本身发现的
ambiguity / conflict / assumption / gap，

系统能够在进入 Design 和 Code 前
将真正需要 Human Intent Decision 的位置暴露出来，
并将用户的决策写回 Specification。
```

---

## 参考资料

- Kiro 官方文档：Analyze Requirements
- Kiro 官方文章：Deep Spec Analysis / Requirements Analysis

> 注：本文档不是 Kiro 官方内部 PRD，而是依据 Kiro 官方公开文档与技术文章，对其 Requirements Analysis 功能进行反向需求整理。
