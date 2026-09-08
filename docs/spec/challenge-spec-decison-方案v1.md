# challenge-spec-decison-方案v1

> 版本：v1  
> 主题：`challenge-spec-decisions` 的职责重构、Challenge Model 定义与工程化实现方案  
> 目标：将原本职责偏宽的 `challenge-spec-decisions` 收缩为面向 Requirement Model 的专职红军挑战能力，减少与需求发现、场景建模、决策求解、Gate Closure 的重复。

---

# 1. 背景、目标与优化结论

## 1.1 原 challenge-spec-decisions 的目标

`challenge-spec-decisions` 最初的设计目标，是在需求形成过程中主动挑战关键决策，避免 Agent 在信息不充分、场景未展开、约束未显性化时直接接受当前 Spec。

原能力大致包含：

- 风险模式召回；
- 关键决策扫描；
- 反例搜索；
- 苏格拉底式追问；
- 隐含假设挑战；
- Scenario / Rule 补充；
- Decision Discovery；
- Decision Resolution；
- Finding 记录；
- 问题闭环判断。

这套设计的优点是覆盖面广，能够较早发现需求中的隐含风险。

但随着 Spec 质量保证体系逐渐完善，问题也越来越明显：

> 一个 Skill 同时承担 Discovery、Modeling、Resolve、Challenge、Verify，多种职责开始相互重叠。

结果是：它虽然“什么都能做”，但很难保证每一类动作的边界稳定，也容易和其他 Skill 重复发现、重复提问、重复记录。

---

## 1.2 当前存在的问题

### 问题一：Challenge 与需求澄清混在一起

例如：

> 网络失败以后是否自动重试？

如果系统原本没有这个 Decision，这属于 **Decision Discovery / Resolution**。

而：

> 已决定“最多重试 3 次”，但验证码 5 分钟后失效，如果第三次重试发生在第 6 分钟怎么办？

这才是 **Challenge**。

原 Skill 中这两种问题都可能被统一当成“Challenge Question”，导致职责不清。

---

### 问题二：Challenge 与 Scenario Discovery 重复

原 Skill 中常见的挑战问题包括：

- 断网怎么办？
- App 被杀怎么办？
- 多个验证码怎么办？
- 多条规则同时匹配怎么办？

但如果这些问题只是为了展开正常、异常、边界状态，它们本质上属于：

> **Scenario / Behavior Modeling**

如果 Challenge 再重复枚举一遍完整场景空间，就会与 Scenario Discovery 发生明显重复。

---

### 问题三：Challenge 与 Gate Closure 重复

Challenge 可能发现：

- retry 与 expiry 冲突；
- “及时发送”不可验证；
- 某个 Rule 没有 Scenario；
- 某个 Assumption 没有证据。

如果 Gate Closure 又重新开放式探索这些问题，就会形成第二轮 Challenge。

因此必须明确：

> Challenge 的主要职责是发现新问题；Gate 的主要职责是验证问题是否已经闭环。

---

### 问题四：Finding、Question、Decision、Risk 多份记录

如果同一个问题分别进入：

- `questions.md`
- `risks.md`
- `decisions.md`
- `challenge.md`
- `spec.md`

就会形成多个事实源。

例如：

```text
Unknown:
网络失败是否重试？

Decision:
网络失败最多重试 3 次

Rule:
网络失败最多重试 3 次

Spec:
网络失败最多重试 3 次
```

如果这些信息分别维护，Agent 很容易出现改了一处、漏了其他位置的问题。

---

## 1.3 本次优化目标

本次优化不是继续增加更多 Challenge 技巧，而是先解决能力边界问题。

目标包括：

1. 将 `challenge-spec-decisions` 明确定位为 **Challenge Model 的主要实现 Skill**；
2. 将开放式需求澄清、普通 Scenario Exploration、Decision Resolution、Gate Closure 从本 Skill 中迁出；
3. 保留并强化风险召回、结构扫描、Counterexample、Interaction、Contradiction 等红军能力；
4. 将 Socratic Questioning 从开放式访谈调整为 **Finding-driven Targeted Question**；
5. 使用统一 Finding 数据模型，避免同一问题多份记录；
6. 建立 Finding 去重、合并和路由机制；
7. 明确 Challenge 的进入条件和停止条件；
8. 让 Challenge 输出可以稳定交给其他 Agent / Skill 继续处理。

---

## 1.4 核心结论：从“决策发现 + 挑战”收缩为 Challenge Model

优化前：

```text
Challenge
+ Clarify
+ Discover
+ Scenario Explore
+ Decision Resolve
+ Verify Closure
```

优化后：

```text
Challenge Requirement Model
        ↓
Produce / Merge Findings
        ↓
Route Findings
```

核心变化可以概括为：

> **Resolve 负责“没有答案时得到答案”；Challenge 负责“已有答案时尝试打破答案”。**

因此：

```text
Decision Resolution:
没有答案 → 找答案

Challenge:
已有模型 → 尝试证明它不成立、不完整、不一致或不稳健
```

---

## 1.5 在整体 Spec 质量保证体系中的位置

推荐的总体模型为：

```text
Discover Reality
      ↓
Model Behavior
      ↓
Resolve Uncertainty
      ↓
Challenge Model
      ↓
Gate Closure
```

其中：

- **Discover Reality**：发现事实、约束、已有系统能力；
- **Model Behavior**：形成 Domain / Scenario / Rule / State / Invariant；
- **Resolve Uncertainty**：解决尚未决定的问题；
- **Challenge Model**：主动攻击已有模型；
- **Gate Closure**：确认问题已经闭环，判断是否 Engineering Ready。

`challenge-spec-decisions` 应处于第四层：

```text
Requirement Model
        ↓
challenge-spec-decisions
        ↓
Finding
        ↓
Reality Discovery / Behavior Modeling / Decision Resolver
        ↓
Gate Closure
```

它不是 Spec 质量保证总控器，而是其中的专职红军攻击器。

---

# 2. 原方案红军评审与职责重构

## 2.1 原有能力拆解

原 `challenge-spec-decisions` 可拆解为以下能力：

### 2.1.1 Risk Recall

根据已审核风险模式库召回潜在风险，例如：

- duplicate delivery；
- timeout ambiguity；
- partial success；
- stale state；
- retry vs expiration；
- race condition；
- external dependency failure。

这类能力属于 Challenge，应保留。

---

### 2.1.2 Systematic Scan

系统扫描当前 Spec / Requirement Model：

```text
Decision ↔ Rule
Rule ↔ Rule
Rule ↔ State
Scenario ↔ Scenario
Assumption ↔ Evidence
Invariant ↔ Behavior
```

寻找结构性问题。

这属于 Challenge，应保留并加强。

---

### 2.1.3 Counterexample Search

主动构造反例，例如：

```text
What if not?
What if twice?
What if delayed?
What if concurrent?
What if partial?
What if reordered?
What if stale?
What if duplicated?
```

它的目标不是扩完整 Scenario Space，而是找出能够使当前 Rule / Decision 失败的输入、状态或序列。

这属于 Challenge 的核心能力。

---

### 2.1.4 Socratic Questioning

原 Skill 中既包括：

- 开放式追问需求；
- 也包括针对 Finding 的定向追问。

前者容易与 grilling / clarify 重复，后者有保留价值。

因此应从：

```text
Open-ended Grilling
```

收缩为：

```text
Finding-driven Targeted Question
```

---

### 2.1.5 Decision Discovery

例如：

> 这里似乎没有定义失败以后是否重试。

这本质上是在发现 Decision Unknown。

它应该被记录为 Finding，但不应该由 Challenge Skill 负责完整求解。

因此：

```text
Challenge
→ Finding: Missing Decision
→ Route to Decision Resolver
```

---

### 2.1.6 Decision Resolution

例如：

> 失败后应该重试 1 次、3 次还是无限重试？

这是典型 Decision Resolver 的职责。

Challenge 可以提出候选风险和反例，但不应该替产品或业务直接完成最终决策。

---

### 2.1.7 Finding

Finding 是 Challenge 最重要的输出，应从辅助记录升级为统一核心产物。

Finding 不只是“问题描述”，还需要明确：

- Challenge target；
- Challenge type；
- failure mechanism；
- evidence；
- impact；
- confidence；
- required action；
- route；
- status。

---

## 2.2 与其他能力的重复分析

## 2.2.1 与 Reality Discovery 的重复

以下问题：

- Android 是否支持某种后台行为？
- 某 API 是否存在？
- 某第三方平台是否允许自动发送？
- 当前代码是否已经实现某能力？

属于 **Fact / Constraint Unknown**。

Challenge 可以发现“这个假设没有证据”，但不应该直接把整套事实调查流程放进自己内部。

正确关系：

```text
Challenge:
发现 Assumption 无证据

        ↓

Finding:
F-001 Evidence missing

        ↓

Route:
Reality Discovery
```

---

## 2.2.2 与 Behavior / Scenario Modeling 的重复

Scenario Discovery 负责：

> 系统性展开行为状态空间。

例如：

```text
Network:
available / unavailable / intermittent

Code:
none / one / multiple

Rule:
none / one / multiple
```

Challenge 不应该再完整枚举这些空间。

Challenge 应在已有 Scenario Model 上做更强的攻击：

```text
Network unavailable
+
App killed
+
Code expired
+
Retry restored
```

这不是普通场景展开，而是 **Interaction Challenge**。

因此：

```text
Scenario Discovery
= Coverage-oriented behavior expansion

Challenge
= Failure-oriented model attack
```

---

## 2.2.3 与 Decision Resolution 的重复

边界定义：

```text
Decision Resolver:
未决问题 → 得到一个决策

Challenge:
已有决策 → 寻找其失效条件
```

例如：

```text
Q: 网络失败是否重试？
```

属于 Decision Resolver。

而：

```text
Decision:
网络失败最多重试 3 次

Challenge:
如果验证码 5 分钟过期，
第三次重试发生在第 6 分钟怎么办？
```

属于 Challenge。

---

## 2.2.4 与 Gate Closure 的重复

Challenge：

> 发现 retry 与 expiry 冲突。

Gate：

> 检查 F-017 是否已解决、Rule 是否更新、Scenario 是否覆盖、Oracle 是否可验证。

因此应建立：

```text
Challenge
    ↓
Finding
    ↓
Resolve
    ↓
Gate Closure
```

而不是：

```text
Challenge
    ↓
Gate 再重新做一轮 Challenge
```

---

## 2.3 应保留的核心能力

优化后应保留：

1. Risk Pattern Recall；
2. Requirement Model Structural Scan；
3. Assumption Challenge；
4. Invariant Challenge；
5. Counterexample Search；
6. Interaction Challenge；
7. Sequence / Ordering Challenge；
8. Contradiction Detection；
9. Finding Creation / Merge；
10. Challenge Coverage Reporting。

---

## 2.4 应迁出的能力

以下能力应从本 Skill 中迁出：

### 开放式需求澄清

例如：

> 你希望验证码发给一个人还是多个人？

迁移至：

```text
Decision Resolver / Grilling
```

### 普通 Scenario 枚举

例如：

> 断网、超时、进程被杀、无验证码、多验证码。

迁移至：

```text
Behavior Modeling / Scenario Discovery
```

### 完整 Decision Frontier 建立

迁移至：

```text
Resolve Uncertainty
```

Challenge 可以针对已有高风险 Decision 选择 Target，但不维护整个业务决策树。

### 最终 Product Decision

迁移至：

```text
Decision Resolver / Human
```

### Gate Closure

迁移至：

```text
Gate Evaluator
```

---

## 2.5 优化前后职责对比

| 能力 | 原方案 | 优化后 |
|---|---|---|
| Risk Recall | 保留 | 保留 |
| Systematic Scan | 保留 | 强化 |
| Counterexample | 保留 | 强化 |
| Interaction Challenge | 部分存在 | 明确新增为核心 |
| Contradiction | 部分存在 | 明确为核心 |
| Socratic Grilling | 开放式 | 收缩为 Finding-driven |
| Scenario Exploration | Challenge 内完成 | 迁出 |
| Decision Discovery | Challenge 内完成 | 仅形成 Finding |
| Decision Resolution | Challenge 内可能完成 | 迁出 |
| Closure Check | Challenge 内可能完成 | 迁出 |
| Finding | 辅助产物 | 核心产物 |

最终职责可以压缩为：

```text
Input:
已有 Requirement Model

Operation:
Attack Model

Output:
Findings + Coverage

Non-goal:
替用户完成需求设计
```

---

# 3. 优化后的 Challenge Model

## 3.1 Challenge 的正式定义

`Challenge Model` 定义为：

> 针对已经形成的 Requirement Model 和关键 Decisions，通过风险召回、结构扫描、反例构造、跨场景组合、时序扰动和矛盾检测，主动寻找假设失效、规则冲突、不变量破坏、交互风险以及决策脆弱性的红军评审过程。

它的目标不是：

> “把需求补全”。

而是：

> **尝试证明当前需求模型在某些条件下不成立。**

---

## 3.2 Challenge 对象

Challenge Target 主要来自 Requirement Model：

```text
Requirement Model
├── Intent
├── Decision
├── Rule
├── Assumption
├── Invariant
├── Scenario
├── State
├── Constraint
├── Dependency
└── Evidence
```

并不是所有对象都要等量攻击。

优先级建议：

```text
High-impact Decision
        ↓
Invariant
        ↓
Unsupported Assumption
        ↓
Rule dependency
        ↓
Cross-scenario interaction
        ↓
Low-risk local behavior
```

---

## 3.3 五类核心 Challenge

## 3.3.1 Assumption Challenge

目的：

> 找出当前模型依赖但没有显式证明的前提。

典型攻击方式：

```text
Why must this be true?
What if this assumption is false?
What evidence supports it?
Who owns this assumption?
Can the environment violate it?
```

示例：

```text
Assumption:
运营商不会重复投递同一 SMS

Challenge:
如果重复投递怎么办？

Finding:
系统缺少 SMS 幂等语义。
```

---

## 3.3.2 Invariant Challenge

目的：

> 构造能够破坏系统必须始终成立的不变量的状态或序列。

示例 Invariant：

```text
同一验证码不得被重复转发。
```

Challenge：

```text
发送实际成功
+
ACK 丢失
+
客户端 Retry
```

结果：

```text
Invariant violated:
同一验证码被发送两次
```

---

## 3.3.3 Counterexample Challenge

目的：

> 为当前 Rule / Decision 构造最小失败样例。

常见变换：

```text
normal → missing
once → twice
immediate → delayed
single → multiple
success → partial success
ordered → reordered
fresh → stale
independent → concurrent
```

例如：

```text
Rule:
提取第一个 6 位数字作为验证码

Counterexample:
短信中订单号 123456，
验证码 887721

结果：
Rule 失效。
```

---

## 3.3.4 Interaction Challenge

目的：

> 找出多个单独正确的 Rule / Scenario 组合后产生的错误。

例如：

```text
Rule A:
网络恢复自动重试

Rule B:
验证码超过 5 分钟失效
```

分别看都合理。

组合：

```text
网络 6 分钟后恢复
```

就产生冲突。

Interaction Challenge 应重点覆盖：

```text
A + B
A → B
B → A
A || B
A failure + B success
A success + B failure
```

---

## 3.3.5 Contradiction Challenge

目的：

> 寻找 Requirement Model 内部互相不能同时成立的声明。

扫描对象：

```text
Decision ↔ Decision
Decision ↔ Constraint
Rule ↔ Rule
Rule ↔ Invariant
Scenario ↔ Rule
Assumption ↔ Evidence
```

示例：

```text
R-010:
任何网络失败最多重试 3 次

R-011:
验证码超过 5 分钟禁止发送
```

如果没有优先级规则，就存在 contradiction / ambiguity。

---

## 3.4 Challenge 与 Scenario Discovery 的边界

必须严格区分：

```text
Scenario Discovery
= 展开状态空间

Challenge
= 攻击已有模型
```

Scenario Discovery 问：

```text
网络有哪些状态？
验证码有哪些状态？
发送有哪些结果？
```

Challenge 问：

```text
这些状态组合以后，
当前 Rule / Decision 还能成立吗？
```

因此：

> 普通异常场景不是天然属于 Challenge。

只有当 Agent 使用异常、组合、时序或反例去证明某个 Target 脆弱时，它才属于 Challenge。

---

## 3.5 Challenge 与 Decision Resolution 的边界

最重要的判断规则：

```text
没有答案
→ Resolve

已经有答案
→ Challenge
```

如果 Challenge 发现：

```text
Missing Decision
```

它只负责创建 Finding：

```text
type: missing_decision
```

然后路由到 Decision Resolver。

---

## 3.6 Challenge 与 Gate Closure 的边界

Challenge 的成功标准：

> 找到了高价值 Finding，或者证明当前 Target 经挑战后没有明显脆弱性。

Gate 的成功标准：

> 已有 Finding 已闭环，Spec 达到进入下一阶段的准出标准。

因此：

```text
Challenge = discovery of defects
Gate = verification of closure
```

---

# 4. challenge-spec-decisions 优化后的执行流程

## 4.1 输入与前置条件

Challenge 不应在 Requirement Model 完全为空时启动。

最低输入建议：

```text
Spec / Story / Requirement
+
至少一种结构化对象：
Decision / Rule / Scenario / Assumption / Invariant
```

标准输入：

```text
Requirement Model
Risk Pattern Library
Existing Findings
Challenge Scope
Evidence Index
```

前置条件：

1. 当前 Feature / Story 范围明确；
2. Challenge target 有可定位对象；
3. Existing Findings 已加载，防止重复；
4. 已存在至少一个可攻击的 Decision / Rule / Assumption / Invariant。

---

## 4.2 Step 1：建立 Challenge Target Inventory

不是对整篇 Spec 无差别攻击，而是先建立候选目标。

Target 类型：

```text
Decision
Rule
Assumption
Invariant
Scenario Interaction
Constraint
Dependency
```

Target 属性：

```yaml
id: D-008
type: decision
impact: high
uncertainty: medium
dependencies:
  - R-014
  - INV-003
evidence_strength: medium
existing_findings:
  - F-017
```

Target 排序建议考虑：

```text
Impact
×
Uncertainty
×
Dependency Count
×
Irreversibility
×
Evidence Weakness
```

优先攻击：

- 影响多个下游对象的 Decision；
- 没有证据支持的关键 Assumption；
- 安全、数据一致性、资金、权限相关 Invariant；
- 与多个 Rule 相连的交互节点。

---

## 4.3 Step 2：D1 Risk Pattern Recall

从风险模式库召回攻击方向。

例如：

```text
retry
→ duplicate execution
→ stale state
→ timeout ambiguity
→ retry storm
→ expiration conflict
```

Risk Pattern 应包含：

```yaml
id: RP-RETRY-001
name: retry-vs-expiration
trigger:
  - retry
  - ttl
challenge:
  - Can retry happen after the business object expires?
typical_impact:
  - invalid operation
  - stale delivery
```

### 风险模式库的边界

必须明确：

> Risk Pattern Library 是 Recall Accelerator，不是 Completeness Oracle。

也就是说：

```text
风险库能帮助 Agent 快速想到哪里攻击，
但不能决定 Agent 只能攻击哪里。
```

否则已知风险库会限制探索空间。

---

## 4.4 Step 3：D2 Structural / Systematic Scan

Risk Recall 之后，Agent 需要脱离风险库，对 Requirement Model 自身做结构扫描。

建议扫描：

### Decision Scan

```text
Decision 有无未声明前提？
Decision 是否与 Constraint 冲突？
Decision 是否对所有下游 Rule 生效？
```

### Rule Scan

```text
Rule 是否有边界？
Rule 与其他 Rule 是否存在优先级问题？
Rule 是否依赖未显性化 State？
```

### Assumption Scan

```text
Assumption 是否有 Evidence？
Assumption 是否可以被环境破坏？
Assumption 是否被当成 Requirement 使用？
```

### Invariant Scan

```text
有哪些 sequence 可以破坏 Invariant？
Invariant 是否在失败路径仍成立？
```

### Scenario Interaction Scan

```text
两个正常 Scenario 是否共享状态？
一个 Scenario 的输出是否影响另一个 Scenario？
```

---

## 4.5 Step 4：D3 Counterexample Search

对每个高价值 Target 构造反例。

建议使用统一变换库：

```text
absence
duplication
delay
reordering
concurrency
partial failure
stale state
capacity limit
permission loss
dependency failure
restart
retry
rollback
configuration change
```

Counterexample 不是随机脑暴，而应明确绑定 Target：

```yaml
target: R-014
transformation: duplication
example:
  input: same SMS delivered twice
  result: two ForwardAttempts created
expected_invariant: at_most_once_forwarding
```

---

## 4.6 Step 5：Interaction & Sequence Challenge

这是新版 Challenge 中应加强的能力。

单场景测试往往无法发现：

```text
A 正确
B 正确
A + B 错误
```

推荐探索：

### 状态组合

```text
NetworkUnavailable
+
CodeExpired
```

### 时序交换

```text
UpdateRule → ReceiveSMS
ReceiveSMS → UpdateRule
```

### 并发

```text
ReceiveSMS A || ReceiveSMS B
```

### Partial Success

```text
remote success
+
local failure
```

### Restart

```text
Pending
→ ProcessKilled
→ Restore
```

---

## 4.7 Step 6：形成统一 Finding

Challenge 不直接修改业务决策，先统一形成 Finding。

建议结构：

```yaml
id: F-017
target:
  type: rule
  id: R-014

challenge_type: contradiction

statement: >
  Retry policy can trigger forwarding after the verification code has expired.

counterexample:
  - SMS received at 10:00
  - network unavailable
  - network restored at 10:06
  - retry is still allowed by R-014

violated:
  - INV-003

impact:
  severity: high
  consequence: expired verification code can be forwarded

evidence:
  - R-014
  - R-011

confidence: high

required_resolution:
  type: decision
  question: >
    Does expiration override remaining retry attempts?

status: open
route_to: decision-resolver
```

Finding 应成为 Challenge 的核心 SSOT。

---

## 4.8 Step 7：Finding 路由

根据问题类型路由：

```text
Fact / Evidence problem
→ Reality Discovery

Missing business behavior
→ Behavior Modeling

Missing / ambiguous decision
→ Decision Resolver

Requirement contradiction
→ Spec / Rule owner

Architecture implication
→ Architecture / Plan

Resolved finding
→ Gate Closure
```

Challenge 的职责在路由完成后结束。

---

## 4.9 Challenge 的停止条件

Challenge 不可能证明“绝对没有问题”。

因此需要工程化停止条件。

建议满足以下条件时结束本轮：

1. Challenge Scope 内所有高优先级 Target 已至少经过一种独立 Challenge；
2. 高风险 Decision 已完成 Counterexample 或 Interaction Challenge；
3. Critical / High Finding 已全部形成明确 route；
4. 连续一轮扫描没有新增高价值 Finding；
5. 已有 Finding 能够复用的，不再重复创建；
6. 剩余未挑战 Target 风险低于阈值；
7. Challenge Coverage Report 已生成。

停止并不表示 Spec 已通过，只表示：

> 本轮 Challenge 已完成。

真正的准出由 Gate Closure 判断。

---

# 5. 工程实现与数据模型优化

## 5.1 Skill 的输入输出契约

### Input

```yaml
challenge_scope:
  feature_id: FEATURE-001

requirement_model:
  decisions: ...
  rules: ...
  scenarios: ...
  assumptions: ...
  invariants: ...
  constraints: ...

risk_patterns: ...

existing_findings: ...
```

### Output

```yaml
challenge_result:
  targets:
    total:
    challenged:
    remaining:

  findings:
    - F-017
    - F-018

  merged_findings:
    - F-003

  coverage:
    assumption:
    invariant:
    counterexample:
    interaction:
    contradiction:

  unresolved_targets: ...
```

---

## 5.2 Finding Single Source of Truth

不推荐使用：

```text
questions.md
risks.md
findings.md
decisions.md
challenge.md
```

分别存储问题状态。

推荐：

```text
Structured Requirement Model
         +
Finding Registry
```

其中 Finding 记录问题状态。

例如：

```yaml
id: F-021
status: open
type: missing_decision
target: R-008
route_to: decision-resolver
resolved_by: null
```

决策完成后：

```yaml
status: resolved
resolved_by: D-014
```

这样不需要从 `questions.md` 删除，再向 `decisions.md` 添加，再同步 `challenge.md`。

---

## 5.3 Finding 去重机制

Challenge 最容易出现的问题之一，是多个路径发现同一个问题。

例如：

```text
Risk Recall
→ retry vs expiration

Counterexample
→ retry after 6 minutes

Contradiction Scan
→ R-010 conflicts with R-011
```

它们可能其实是同一个 Finding。

推荐使用 Finding Fingerprint：

```text
Target
+
Challenge Type
+
Failure Mechanism
```

例如：

```text
R-014
+
expiration_conflict
+
retry_after_expiry
```

如果 Fingerprint 已存在：

```text
create new finding
```

改为：

```text
merge evidence
+
increase confidence
+
append counterexample
```

---

## 5.4 Risk Pattern Library 的定位

风险模式库应提供：

```text
trigger
attack direction
typical failure mechanism
related invariants
common evidence
```

不建议把完整业务答案写入风险模式。

原因是：

> Risk Pattern 应帮助 Challenge 思考，而不是替 Requirement Model 做决策。

风险库来源建议区分：

```text
Reviewed
Observed
Candidate
Deprecated
```

Challenge 默认优先使用 Reviewed，但仍允许独立探索。

---

## 5.5 Socratic Questioning 的重新定位

原模式：

```text
Need
→ Ask
→ Ask
→ Ask
```

优化后：

```text
Target
→ Challenge
→ Counterexample
→ Finding
→ Targeted Question
```

例如：

```text
Decision:
失败最多重试 3 次

Counterexample:
第 3 次重试发生在验证码过期后

Finding:
retry conflicts with expiration

Question:
“验证码过期是否应覆盖剩余重试次数？”
```

这个问题有：

- 明确 Target；
- 明确 Failure；
- 明确为什么要问；
- 明确答案会修改哪个 Decision / Rule。

这比开放式 Socratic Grilling 更适合作为 Challenge 内部能力。

---

## 5.6 与其他 Skills / Agents 的接口

推荐架构：

```text
               Requirement Model
                      │
       ┌──────────────┼──────────────┐
       │              │              │
Reality Discovery  Behavior Model  Decision Resolver
       ▲              ▲              ▲
       │              │              │
       └──────────────┼──────────────┘
                      │
              challenge-spec-decisions
                      │
                   Findings
                      │
                 Gate Closure
```

### Challenge → Reality Discovery

条件：

```text
Finding.type = evidence_gap
```

### Challenge → Behavior Modeling

条件：

```text
Finding.type = behavior_gap
```

### Challenge → Decision Resolver

条件：

```text
Finding.type = missing_decision
or
Finding.type = decision_conflict
```

### Challenge → Gate

只有 Finding 已解决以后进入 Gate。

---

## 5.7 防重复设计原则

新版 Skill 建议强制以下规则：

1. **每次 Challenge 必须有 Target。**
2. Challenge 不进行无目标开放式访谈。
3. Challenge 不重新展开完整 Scenario Space。
4. Challenge 不自行完成最终 Product Decision。
5. Challenge 不承担 Gate Closure。
6. Finding 必须有唯一 ID。
7. Existing Finding 必须先查重，再创建。
8. Risk Recall 不能替代独立 Model Scan。
9. 一个 Counterexample 必须明确攻击哪个 Rule / Decision / Assumption / Invariant。
10. Question 必须由 Finding 驱动。
11. Challenge 输出必须能路由到明确责任能力。
12. spec.md 不是问题状态的唯一存储位置，结构化模型优先。

---

# 6. 示例、迁移方案与最终建议

## 6.1 Android 验证码转发示例

假设已有 Requirement Model：

```text
D-001:
使用企业微信转发验证码

R-014:
网络失败最多自动重试 3 次

R-011:
验证码收到 5 分钟后禁止发送

INV-003:
不得发送已经失效的验证码
```

---

### Step 1：选择 Target

```text
Target:
R-014 retry rule
```

原因：

- 影响最终发送行为；
- 与时效相关；
- 与失败恢复相关；
- 下游依赖多。

---

### Step 2：Risk Recall

风险库召回：

```text
retry-vs-expiration
duplicate retry
retry after restart
remote-success-local-failure
```

---

### Step 3：Structural Scan

发现：

```text
R-014
→ retry 3 times

R-011
→ no send after 5 minutes
```

但没有声明规则优先级。

---

### Step 4：Counterexample

```text
10:00 收到短信
10:01 第一次发送失败
10:03 第二次失败
10:06 网络恢复
```

根据 `R-014`：

```text
仍可第三次 Retry
```

根据 `R-011`：

```text
已经禁止发送
```

---

### Step 5：形成 Finding

```yaml
id: F-017
target: R-014
challenge_type: contradiction
statement: Retry policy conflicts with expiration rule.
severity: high
status: open
route_to: decision-resolver
```

---

### Step 6：Targeted Question

不是问：

> “失败情况下你希望怎么办？”

而是问：

> “当验证码已经超过 5 分钟有效期，但仍剩余重试次数时，是否应立即取消剩余重试？建议 expiration 优先于 retry。”

这是 Finding-driven Question。

---

### Step 7：Decision Resolver

形成：

```text
D-014:
Expiration overrides retry budget.
```

进一步更新：

```text
R-014:
网络失败最多重试 3 次，但任何 Retry 都不得发生在验证码失效之后。
```

---

### Step 8：Gate Closure

Gate 检查：

```text
F-017 = resolved
D-014 exists
R-014 updated
相关 Scenario 存在
Oracle 可验证
```

Challenge 到此不再继续参与。

---

## 6.2 原 challenge-spec-decisions 到新版的迁移映射

| 原能力 | 新版处理 |
|---|---|
| 风险模式召回 | 保留 |
| D2 Systematic Scan | 保留并结构化 |
| Counterexample | 保留并加强 |
| Socratic Grilling | 收缩为 Finding-driven |
| Scenario Exploration | 迁移至 Behavior Modeling |
| Domain Exploration | 迁移至 Behavior Modeling |
| Fact Research | 迁移至 Reality Discovery |
| Decision Frontier | 迁移至 Decision Resolver |
| Decision Resolution | 迁移至 Decision Resolver |
| Closure Check | 迁移至 Gate Closure |
| Finding | 升级为核心输出 |
| Risk Library | 保留，但限定为 Recall Accelerator |

---

## 6.3 推荐的最终 Skill 流程

最终建议将 `challenge-spec-decisions` 收敛成以下流程：

```text
Load Requirement Model
        ↓
Load Existing Findings
        ↓
Build Challenge Target Inventory
        ↓
Prioritize Targets
        ↓
D1 Risk Pattern Recall
        ↓
D2 Structural / Systematic Scan
        ↓
D3 Counterexample Search
        ↓
Interaction / Sequence Challenge
        ↓
Contradiction Detection
        ↓
Create / Merge Findings
        ↓
Route Findings
        ↓
Generate Challenge Coverage Report
```

其中不再包含：

```text
Open-ended requirement interview
Full scenario discovery
Final decision making
Gate verdict
```

---

## 6.4 成功标准

新版 `challenge-spec-decisions` 的质量，不应通过“问了多少问题”衡量。

建议评价以下指标：

### Finding 价值

```text
High-value Findings / Total Findings
```

### 重复率

```text
Duplicated Findings / Total Findings
```

### Target 覆盖

```text
High-risk Targets Challenged / High-risk Targets
```

### Challenge 多样性

是否覆盖：

```text
Assumption
Invariant
Counterexample
Interaction
Contradiction
```

### 路由完整性

```text
Findings with clear route / Total Findings
```

### 闭环可追踪性

```text
Finding
→ Decision / Rule / Model Update
→ Gate Evidence
```

应该可以追踪。

---

## 6.5 最终建议

`challenge-spec-decisions` 不应继续演进为一个“万能需求分析 Skill”。

它最有价值的定位是：

> **Requirement Model 的专职红军攻击器。**

它不负责构建全部需求世界，而负责在当前世界已经被描述以后，主动寻找：

```text
Assumption failure
Invariant violation
Counterexample
Interaction failure
Sequence failure
Contradiction
```

最终架构应形成：

```text
Discover Reality
        ↓
Model Behavior
        ↓
Resolve Uncertainty
        ↓
challenge-spec-decisions
        ↓
Findings
        ↓
Resolve
        ↓
Gate Closure
```

新版 Skill 的核心原则可以归纳为：

> **有 Target 地攻击，而不是无边界地追问；  
> 用 Finding 连接发现与解决，而不是在 Challenge 内完成所有工作；  
> 用 Counterexample、Interaction 和 Contradiction 证明模型脆弱，而不是重复做 Scenario 枚举。**

这样才能让 `challenge-spec-decisions` 与整个 Spec Quality Assurance System 形成清晰、正交、可持续演进的关系。
