# Code Agent Patterns：从代码生成到受控软件变更

> 基于 SE-ML **Agentic Coding: A Pattern Language** 及其 1～9 个 Agentic Coding Patterns 的工程化总结与扩展。
>
> 本文不是对九篇文章的逐篇翻译，而是把其中的思想重构为一套可以指导 Codex、Claude Code、GitHub Copilot Agent 等 Code Agent 进行真实软件开发的工作方法。

---

## 0. 摘要

随着 Code Agent 的代码生成能力越来越强，软件开发中的瓶颈正在发生变化：**生成代码越来越便宜，但理解、监督、验证、Review、恢复和维护仍然昂贵。**

因此，Agentic Software Development 的核心问题不再只是：

> Agent 能不能把代码写出来？

而变成：

> **如何让 Agent 在正确理解问题的前提下，以受控的范围完成变更，并用独立证据证明结果可信，同时保持失败可恢复、仓库可维护？**

SE-ML 的 Agentic Coding Pattern Language 给出了九个反复出现的工程模式：

1. Agent-Assisted Discovery
2. Specification-Driven Development
3. Plan-Driven Task Decomposition
4. Incremental Execution
5. Role-Based Development & Subagents
6. Memory & Context Management
7. Verification-First Engineering
8. Rollback & Reversibility
9. Cleanup & Hygiene

这九个 Pattern 不应被机械理解为固定的九步瀑布流程。更合理的理解是：它们共同建立了四类控制能力：

```text
Cognition Control   —— Agent 是否在正确理解系统？
Intent Control      —— Agent 是否在实现真正的目标？
Execution Control   —— Agent 如何、小到什么粒度、在什么 Context 下执行？
Risk Control        —— 如何发现错误、恢复错误并保持仓库健康？
```

本文最终将 Code Agent 的工作单位概括为：

```text
Verified State
      ↓
Controlled Change
      ↓
Independent Verification
      ↓
Verified State
```

而不是传统的：

```text
Prompt → Generate Code → Review
```

---

# 1. Code Agent 的核心工程问题：从“代码生成”转向“变更控制”

## 1.1 为什么“Agent 会写代码”还远远不够

一个 Code Agent 可以在很短时间内：

- 阅读大量代码；
- 搜索调用链；
- 生成实现；
- 修改多个文件；
- 补充测试；
- 运行构建命令；
- 修复测试失败；
- 更新文档。

这看起来已经覆盖了一个工程师的大部分操作，但速度越快，另一个问题越突出：**错误也可以以同样的速度传播。**

例如，一个看似很小的错误理解：

```text
“这个 Repository 是唯一的数据源”
```

如果这个判断实际上不成立，Agent 可能继续基于它：

```text
修改 Repository
    ↓
修改调用者
    ↓
调整缓存逻辑
    ↓
修改测试
    ↓
更新文档
```

最终几十个修改在局部上都“自洽”，但整个方案建立在错误的 Local Model 上。

这类问题的危险之处在于：**代码通常不是明显错误，而是 plausible but wrong——看起来合理但实际上错误。**

因此，Agent 软件工程的主要优化目标不能只是：

```text
提高生成速度
```

而应该变成：

```text
降低错误假设进入代码的概率
降低单次错误的 Blast Radius
提高错误被及时发现的概率
降低错误状态的恢复成本
保证每个完成状态仍然可维护
```

---

## 1.2 Code Agent 常见的九类失控风险

九个 Pattern 分别针对一类反复出现的问题。

| 风险 | 典型表现 | 对应 Pattern |
|---|---|---|
| 系统理解错误 | 不知道 ownership、依赖和真实行为就开始编码 | Discovery |
| 意图理解错误 | 完美执行 Prompt，却没有解决真实问题 | Specification |
| 任务边界错误 | Feature 太大，Agent 边做边偷偷拆任务 | Planning |
| 改动范围失控 | 一次修改几十个文件，问题难定位 | Incremental Execution |
| 角色混淆 | 同一个 Agent 设计、实现、证明自己正确 | Role-Based Development |
| Context 污染 | 长会话、旧信息和无关文件干扰当前判断 | Context Management |
| 虚假正确 | Agent 声称完成，但没有独立证据 | Verification First |
| 无法恢复 | 多个修改互相依赖，失败后只能整体丢弃 | Rollback |
| 仓库污染 | debug、TODO、dead code、临时文件长期残留 | Cleanup |

这九类风险共同说明：**Agent 不是简单的“更快的程序员”，而是一个需要被明确约束输入、状态、权限、范围和验证机制的软件变更执行器。**

---

# 2. Agentic Development 的整体控制模型

## 2.1 三段生命周期 + 两个横切控制面

九个 Pattern 可以组织成三个主要阶段：

```text
┌─────────────────────────────────────┐
│ A. Understanding & Definition       │
│                                     │
│ 1 Discovery                         │
│ 2 Specification                     │
│ 3 Task Decomposition                │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│ B. Controlled Execution             │
│                                     │
│ 4 Incremental Execution             │
│ 5 Role-Based Development            │
│ 6 Memory & Context Management       │
└──────────────────┬──────────────────┘
                   ↓
┌─────────────────────────────────────┐
│ C. Correctness & Recovery           │
│                                     │
│ 7 Verification First               │
│ 8 Rollback & Reversibility          │
│ 9 Cleanup & Hygiene                 │
└─────────────────────────────────────┘
```

但这里需要特别强调：**Role 和 Context 并不只是“第 5、6 步”。**

它们更像两个横切控制面：

```text
                Role Control
                     │
Discovery ─ Spec ─ Plan ─ Execute ─ Verify
                     │
               Context Control
```

任何阶段都需要回答：

- 当前应该由什么角色负责？
- 这个角色是否应该独立于前一个角色？
- 当前最小充分 Context 是什么？
- 哪些 Context 必须排除？
- 哪些结论应该外部化为 Durable Artifact？

---

## 2.2 四类控制面

从更高层看，这九个 Pattern 构成四类工程控制。

### 2.2.1 Cognition Control：认知控制

核心 Pattern：**Agent-Assisted Discovery**。

目标：

> 不允许 Agent 在错误的世界模型上工作。

关注：

- 当前系统真实行为是什么？
- 谁负责这个行为？
- 有哪些 dependency？
- 哪些是 Fact，哪些只是 inference？
- 哪些 assumption 必须验证？

---

### 2.2.2 Intent Control：意图控制

核心 Pattern：

- Specification-Driven Development
- Plan-Driven Task Decomposition

目标：

> 不允许 Business Intent 在 Prompt → Code 的过程中被悄悄替换。

形成链路：

```text
Business Intent
      ↓
Specification
      ↓
Plan
      ↓
Atomic Task
```

---

### 2.2.3 Execution Control：执行控制

核心 Pattern：

- Incremental Execution
- Role-Based Development
- Memory & Context Management

控制三个变量：

```text
WHO       —— 谁执行？
CONTEXT   —— 他知道什么？
SIZE      —— 一次改变多少？
```

---

### 2.2.4 Risk Control：风险控制

核心 Pattern：

- Verification-First Engineering
- Rollback & Reversibility
- Cleanup & Hygiene

回答三个问题：

```text
Can we detect it?   → Verification
Can we recover?     → Rollback
Can we stay healthy?→ Cleanup
```

---

# 3. Pattern 1：Agent-Assisted Discovery

## 3.1 解决的问题：Incomplete Local Model

Agent 和人进入一个新任务时，经常面对的是局部信息：

- 只看到了 PRD，没有看真实实现；
- 只看到了一个类，没有看上游和下游；
- 知道业务词汇，但不知道项目中的具体语义；
- 知道目标行为，但不知道系统当前为什么这样设计；
- 看到了 API，却不知道生命周期、线程、状态或平台约束。

真正危险的不是“不知道”，而是：**Agent 经常会把“不知道”自动补全成“可能是这样”。**

于是：

```text
Missing Information
      ↓
Plausible Inference
      ↓
Unverified Assumption
      ↓
Implementation Decision
      ↓
Defect
```

本应在理解阶段暴露的 comprehension defect，最后以 implementation defect 的形式出现。

---

## 3.2 Discovery 的目标不是“找代码”，而是建立 Reliable Local Model

Discovery 不等于 grep。

它至少需要建立以下模型：

```text
Task / Business Intent
        │
        ├── System Boundary
        ├── Ownership
        ├── Current Behavior
        ├── Domain Concepts
        ├── State / Rules / Invariants
        ├── Dependencies
        ├── External Constraints
        ├── Existing Verification
        └── Decision Surface
```

最后 Agent 和开发者应该能够回答：

> **如果我要改变这个行为，真正应该改变哪里；为什么是这里；可能影响谁；哪些事情我仍然不知道？**

---

## 3.3 Discovery 的六步流程

### Step 1 — Orient：确定方向

先从 Broad Orientation 开始，而不是马上钻入函数细节。

需要找到：

- subsystem；
- module；
- feature boundary；
- key files；
- ownership boundary；
- architecture entry point。

典型问题：

```text
这个功能位于哪个 subsystem？
真正负责最终行为的是哪个组件？
关键入口在哪里？
哪些模块只是适配层，哪些模块拥有业务规则？
```

### Step 2 — Understand：理解当前行为

需要建立：

- control flow；
- data flow；
- state transition；
- domain semantics；
- persistence behavior；
- error behavior。

不要满足于“这个类做登录”。需要进一步追问：

```text
登录状态从哪里来？
状态由谁保存？
什么时候失效？
失败如何传播？
重试由谁负责？
```

### Step 3 — Trace：追踪依赖

重点识别：

- upstream callers；
- downstream consumers；
- interfaces；
- shared state；
- cache / database；
- network services；
- platform lifecycle；
- configuration；
- tests。

核心问题不是：

> 修改这个函数能不能编译？

而是：

> **改变这个假设以后，哪些其他组件可能失去原本成立的条件？**

### Step 4 — Challenge：显性化未知和假设

要求 Agent 明确分类每个关键判断。

推荐 Finding Model：

| 类型 | 含义 |
|---|---|
| `FACT` | 可以直接由代码、文档、测试、配置证明 |
| `INFERENCE` | 从多个事实推导出的解释，但没有直接证据 |
| `ASSUMPTION` | 当前为了继续推理暂时采用的假设 |
| `UNKNOWN` | 缺少必要信息，当前无法确定 |
| `CONSTRAINT` | 必须满足的外部或内部约束 |
| `RISK` | 如果判断错误可能产生明显影响 |
| `DECISION_GAP` | 存在多个合法方向，需要人做设计/产品决策 |

这是 Discovery 最重要的控制手段之一。

### Step 5 — Explore Alternatives：探索方案空间

在形成实现方案之前，至少问：

```text
有哪些 2～3 个可行方向？
每个方向依赖哪些前提？
哪个方案改动面最小？
哪个方案符合当前架构？
哪个方案引入新的长期约束？
哪个方案需要额外产品/架构决策？
```

Discovery 不要求立即决策，但应该把 **Decision Surface** 显性化。

### Step 6 — Verify：从解释回到证据

所有重要结论最终都应该回到：

- source code；
- existing tests；
- architecture docs；
- configuration；
- API documentation；
- build/runtime evidence。

特别应该问：

> 哪些结论来自代码，哪些只是你的 inference？

---

## 3.4 Discovery 输出：`discovery.md`

建议输出结构：

```markdown
# Discovery: [Task]

## Task Understanding

## Relevant System

## Current Behavior

## Ownership

## Domain Model

## Dependency Map

## Constraints

## Findings
| ID | Type | Finding | Evidence | Confidence |

## Assumptions

## Unknowns

## Decision Gaps

## Alternatives

## Risks

## Recommended Next Step
```

---

## 3.5 Discovery Gate

以下情况应该 **BLOCK** 后续 Implementation：

- 关键行为 ownership 不明确；
- 关键 dependency 未定位；
- 设计方案依赖未验证 assumption；
- 当前系统行为仍然存在关键 unknown；
- 外部平台/API 能力没有证据；
- 多个方案之间存在真正的 Decision Gap，但尚未决策。

Discovery 的完成条件不是“知道所有事情”，而是：

> **所有对后续决策有影响的未知，都已经被解决或显性登记。**

---

# 4. Pattern 2：Specification-Driven Development

## 4.1 Prompt 不等于 Specification

普通 Prompt 很容易把需求、方案和命令混成一团：

```text
在 Header 加一个 Login Button，点击时调用 auth API，
再加 loading spinner，失败用 toast。
```

Agent 很可能非常准确地执行这些操作，但这并不意味着它理解真正 Intent。

真正需求可能只是：

> 用户应该能够从任意页面开始 OAuth 登录。

两者的区别在于：

```text
Prompt 强调：怎么做
Specification 强调：什么必须成立
```

Agentic Development 中，Intent 被委托给了 Agent，因此 Intent 与 Implementation 之间出现新的解释边界：

```text
Developer Intent
      ↓
Specification
      ↓
Agent Interpretation
      ↓
Implementation
```

Specification 的目的就是缩小这条链路上的语义损失。

---

## 4.2 Spec 的五个基本部分

推荐：

```text
Goal
Constraints
Context
Acceptance Criteria
Out of Scope
```

### Goal

定义完成后的期望状态，而不是执行动作。

### Constraints

包括：

```text
MUST
MUST NOT
PREFER
```

Constraints 对 Agent 特别重要，因为它不知道那些“团队觉得理所当然”的隐含规则。

### Context

只给理解任务所需背景：

- technical context；
- business context；
- legacy constraints；
- related work。

### Acceptance Criteria

必须可以验证。

避免：

```text
体验更好
代码更优雅
足够健壮
```

优先：

```text
网络恢复后 30 秒内重新调度失败任务；
重复恢复事件不得创建两个并发同步任务；
所有现有同步场景测试通过。
```

### Out of Scope

显式定义不做什么，是控制 Agent Gold-plating 的有效方法。

---

## 4.3 Declarative Spec 优于过度 Imperative Prompt

Spec 应尽量描述终态，而不是微操 Agent。

例如：

```markdown
## Goal
用户可以在网络恢复后自动继续此前因断网失败的同步任务。

## Constraints
- MUST 使用现有同步任务模型。
- MUST NOT 引入新的后台常驻 Service。
- MUST 保持幂等性。
- MUST NOT 修改服务端协议。

## Acceptance Criteria
- 断网失败后任务状态保持为可恢复状态。
- 网络恢复后任务被重新调度。
- 重复网络回调不会产生重复上传。
- App 重启后仍可恢复未完成任务。

## Out of Scope
- 不重新设计同步协议。
- 不修改云端 API。
```

这样的 Spec 允许 Agent探索最合适实现，同时又限制结果空间。

---

## 4.4 Legacy System 推荐 Double-Spec

对于已有系统，不要直接从“新需求”修改代码。

先写：

```text
Current Behavior Spec
        ↓
      GAP
        ↓
Desired Behavior Spec
```

因为 Legacy System 的最大风险往往不是“新功能做不出来”，而是：

> **不知道当前哪些行为其实是兼容性契约。**

Current Spec 与 Desired Spec 的差异，才是真正 Change Surface。

---

## 4.5 Specification Gate

进入 Planning 前至少确认：

- Goal 明确；
- Constraints 明确；
- AC 可验证；
- Out of Scope 明确；
- 与 Discovery Facts 不冲突；
- 关键 Decision Gap 已解决；
- 没有让 Agent 悄悄定义产品 Intent。

---

# 5. Pattern 3：Plan-Driven Task Decomposition

## 5.1 Specification ≠ Plan

必须明确区分：

```text
Specification = What must be true
Plan          = How to execute the change safely
Task          = Smallest executable/reviewable unit
```

即使 Spec 非常完整，也不代表应该让 Agent 直接“实现整个 Feature”。

如果缺少 Plan，Agent 会在执行过程中进行 **隐式任务拆分**：

```text
Feature
   ↓
Agent 自己决定先做什么
   ↓
发现问题
   ↓
临时增加 abstraction
   ↓
修改额外模块
   ↓
继续补测试
```

这时人已经很难区分：

- 哪些是原始需求；
- 哪些是计划；
- 哪些是 Agent 临时决定。

---

## 5.2 计划阶段重点防三个问题

### Drift

任务执行过程中逐步偏离原始目标。

### Gold-plating

Agent 为了“完整”和“专业”，增加本来不需要的 abstraction、framework、refactor。

### Context Pollution

一个任务太大，导致大量文件、讨论和工具结果都堆入同一 Context。

---

## 5.3 好 Task 的基本模型

推荐每个 Task 都至少包含：

```text
Task ID
Goal
Depends On
Scope
Allowed / Expected Files
Required Context
Constraints
Expected Output
Verification
Rollback
```

例如：

```markdown
### TASK-03 Persist resumable upload state

**Goal**
让因网络中断失败的上传任务可以跨进程保留恢复状态。

**Depends on**
TASK-01, TASK-02

**Scope**
- sync/data/
- sync/model/

**Do not touch**
- server API
- UI

**Context needed**
- sync-spec.md §3
- UploadTask state model
- existing repository implementation

**Verification**
- repository unit tests
- process-restart persistence test

**Rollback**
Revert TASK-03 checkpoint commit.
```

---

## 5.4 Atomic / Reviewable / Verifiable

好的 Task 不是“越小越好”，而是最小 **coherent unit**。

三个判定标准：

### Atomic

它实现一个清晰、独立的目标。

### Reviewable

Reviewer 能在有限 Context 内理解完整 Diff。

### Verifiable

完成后可以立即得到明确的 pass/fail Evidence。

如果一个 Task：

- 需要同时改 20+ 文件；
- Verification 只能等整个 Feature 做完；
- Scope 很难一句话说清楚；

那么它通常应该继续拆。

---

## 5.5 Task Decomposition 同时也是 Context Decomposition

这是 Planning 的一个关键价值。

错误方式：

```text
每个 Agent Task
= 整个 repo
+ 完整 spec
+ 完整 plan
+ 所有历史聊天
```

更好的方式：

```text
Task_i
     ↓
Minimum Sufficient Context_i
```

因此 Planning 时应该明确问：

> **What is the minimum context required for this task to be executed correctly?**

---

# 6. Pattern 4：Incremental Execution

## 6.1 为什么“大 Feature 一次实现”不适合 Agent

Agent 的 Generation Cost 很低，但：

```text
Generation Cost ↓
≠ Verification Cost ↓
≠ Review Cost ↓
≠ Recovery Cost ↓
```

一次改很多文件时，错误会出现依赖传播：

```text
Wrong Assumption
      ↓
Edit A
      ↓
Edit B depends on A
      ↓
Edit C depends on B
      ↓
Edit D depends on C
      ↓
Failure finally detected
```

此时虽然错误发生在 A，但真正失败可能只在 D 暴露。

---

## 6.2 Agent 的基本执行循环

```text
Select Approved Task
        ↓
Make Small Coherent Change
        ↓
Run Immediate Verification
        ↓
      PASS?
      /   \
    NO     YES
    ↓       ↓
Fix /    Checkpoint
Rollback    ↓
          Next Task
```

核心规则：

> **只从 Known-Good State 向下一个 Known-Good State 前进。**

---

## 6.3 Step Template

在 Task 内，还可以进一步定义 execution step：

```text
STEP
Action:
Files:
Expected effect:
Verify:
Stop condition:
Rollback:
```

这样 Agent 不只是收到“完成 TASK-03”，而知道何时应该停下来验证。

---

## 6.4 Change Budget

为了避免“Small Change”成为模糊口号，可以建立 Change Budget。

例如：

```text
Files touched       ≤ N
Components touched  ≤ N
New abstractions    ≤ N
Behavioral surfaces = explicitly listed
```

这里的 N 不需要形成组织级统一数字，重点是：**要求 Agent 在改动范围扩大时显式报告，而不是静默扩展。**

---

## 6.5 与 TDD 的结合

Incremental Execution 与 TDD 天然兼容：

```text
Write failing test
      ↓
Confirm it fails for the expected reason
      ↓
Minimal implementation
      ↓
Run test
      ↓
PASS
      ↓
Checkpoint
```

这里“先确认测试失败”非常重要，否则你无法证明测试真的观察到了目标行为。

---

# 7. Pattern 5：Role-Based Development & Subagents

## 7.1 为什么一个 Agent 从头做到尾有系统性风险

如果同一个 Session 同时扮演：

```text
Explorer
Architect
Planner
Implementer
Tester
Reviewer
```

会出现两个严重问题。

### Context Pollution

前面探索阶段形成的猜测、旧方案、废弃想法仍然占据 Context，并持续影响实现和 Review。

### Self-Legitimization

Agent：

```text
提出方案
   ↓
实现自己的方案
   ↓
写测试验证自己的实现
   ↓
Review 自己的代码
   ↓
宣布方案合理
```

它缺少真正的认知独立性。

---

## 7.2 典型角色

| Role | 主要职责 |
|---|---|
| Explorer | 阅读代码、建立 Local Model、输出 Finding |
| Architect | 设计边界、接口、关键 trade-off |
| Planner | 把 Spec 转为 Tasks |
| Implementer | 在明确 Scope 内完成修改 |
| Tester | 根据 Requirement/Oracle 设计和执行验证 |
| Spec Reviewer | 检查实现是否满足 Intent、AC 和 Scope |
| Code Reviewer | 检查代码质量、架构一致性、复杂度 |
| Documenter | 更新 Durable Artifact |

不是每个 Task 都要创建八个 Agent。

原则是：

> **只隔离那些共享同一 Context 会降低判断独立性的责任。**

---

## 7.3 Structured Handoff

不同 Agent 之间不应该默认传递整个 Transcript。

推荐 Handoff：

```markdown
# Handoff

## Objective

## Completed

## Facts & Evidence

## Decisions

## Constraints

## Open Issues

## Assumptions / Unknowns

## Relevant Artifacts

## Next Role Objective
```

Handoff 的本质是：

> **传递状态，而不是传递历史。**

---

## 7.4 Two-Stage Review

非常推荐把 Review 明确分成两层：

```text
Implementation
      ↓
1. Spec Compliance Review
      ↓ PASS
2. Code Quality Review
      ↓ PASS
Next Task
```

第一层问：

> **Did we build the right thing?**

检查：

- AC 是否满足；
- Scope 是否遵守；
- 有没有 unrequested behavior；
- 有没有漏掉 requirement。

第二层才问：

> **Did we build the thing right?**

检查：

- 架构；
- 可维护性；
- 复杂度；
- 风格；
- abstraction；
- 代码质量。

顺序很重要：一个实现即使写得非常漂亮，如果没有满足 Spec，也仍然是不合格实现。

---

# 8. Pattern 6：Memory & Context Management

## 8.1 Context 是 Agent 的输入参数

可以把 Agent 简化成：

```text
Output = Agent(Task, Context)
```

相同 Task，在不同 Context 下可能得到完全不同结果。

因此 Context 不应被视为聊天系统自动积累的背景，而应该被视为：

> **工程上需要设计、版本化和裁剪的输入。**

---

## 8.2 More Context ≠ Better Context

大 Context 会产生：

- token / latency 增加；
- 旧信息持续影响判断；
- 无关模块竞争注意力；
- 过期决策与当前决策冲突；
- 中间工具输出污染会话；
- 真正关键约束被淹没。

因此应追求：

```text
Minimum Sufficient Context
```

而不是：

```text
Maximum Available Context
```

---

## 8.3 Context Curating

### 应优先包含

- 当前 Task 的 Goal；
- 当前 Spec 相关部分；
- 相关代码；
- 相关测试；
- architecture constraints；
- invariants；
- API docs；
- existing good examples；
- explicit anti-patterns。

### 应主动排除

- unrelated modules；
- build output；
- generated files；
- 旧日志；
- 已废弃方案；
- unrelated conversation；
- 整个 Repo 的无差别 dump。

---

## 8.4 Context Memory 与 Persistent Memory

### Context Memory

存在于当前 Context Window：

```text
生命周期：当前 session
特点：短期、昂贵、会衰减
```

### Persistent Memory

存在于项目 Artifact：

```text
生命周期：跨 session
特点：持久、可 Review、可版本控制、按需加载
```

这意味着：

> **不要要求 Agent“记住项目”，而应该把项目知识写出来。**

---

## 8.5 推荐的 Durable Artifacts

| 知识 | 推荐 Artifact |
|---|---|
| Agent 长期约束 | `AGENTS.md` / `CLAUDE.md` |
| 做什么 | `spec.md` |
| 怎么执行 | `plan.md` |
| 当前工作单元 | `tasks.md` |
| 架构决策及原因 | `ADR/` / `DECISIONS.md` |
| 可复用流程知识 | `SKILL.md` |
| 当前会话交接状态 | `context.md` / `handoff.md` |
| Discovery 事实与未知 | `discovery.md` |
| 验证证据 | `verification.md` |

一个重要原则：

```text
What to build               → Spec
How to build this change    → Plan
Reusable procedure          → Skill
Repeated project constraint → Agent Config
Why architecture is so      → ADR
Current session state       → Handoff / Context
```

---

## 8.6 Retrieval-on-Demand

正确的 Context 策略应该是：

```text
默认给最少充分信息
        ↓
发现信息缺口
        ↓
针对性 Retrieve
        ↓
验证
        ↓
继续
```

而不是任务一开始就加载所有可能相关的资料。

---

# 9. Pattern 7：Verification-First Engineering

## 9.1 Agent 最大的质量风险是“看起来对”

AI 的危险输出不是明显语法错误，因为这类问题很容易被编译器发现。

更危险的是：

- syntactically correct but semantically wrong；
- 看起来存在但实际不存在的 API；
- 单元测试通过但集成场景错误；
- 自己生成的测试正好迎合自己的实现；
- 不必要的 abstraction；
- unrelated but plausible changes。

因此：

> Agent 自己说“Done”不是 Evidence。

---

## 9.2 Verification 应成为主控制循环

传统模式：

```text
Implementation
      ↓
Implementation
      ↓
Implementation
      ↓
Final Test
```

Verification-First：

```text
Change
  ↕
Verification
  ↓
Known-Good State
```

每个 meaningful change 后都应该存在独立验证。

---

## 9.3 Verification 的目的不是“证明正确”，而是尝试证伪

一个非常重要的原则：

> **选择当前成本最低、但最有机会推翻 Agent 输出的检查。**

例如刚修改类型签名：

```text
优先 Compile / Type Check
```

刚修改核心 business rule：

```text
优先 targeted unit/scenario test
```

修改跨模块接口：

```text
优先 integration verification
```

没有必要每一个字符修改都运行最昂贵 E2E，但也不能只选择“容易通过”的验证。

---

## 9.4 Verification Ladder

推荐建立分层验证：

```text
Syntax / Parse
      ↓
Compile / Type Check
      ↓
Lint / Static Analysis
      ↓
Unit Test
      ↓
Integration / API Test
      ↓
Scenario / Behavioral Test
      ↓
Diff Review
      ↓
Complexity Review
      ↓
Spec Compliance Review
      ↓
Human Review
```

不同层捕获不同 defect class，因此不能把“测试通过”等价为“实现正确”。

---

## 9.5 Oracle 应尽量独立于 Implementation

最危险的循环之一：

```text
Agent writes implementation
        ↓
Agent derives tests from implementation
        ↓
Tests confirm implementation
```

这会形成 sycophantic testing。

更可靠：

```text
Requirement / AC / Rule / Scenario
        ↓
Verification Oracle
        ↓
Test / Check
        ↓
Implementation
```

Review AI-generated tests 时始终问：

> **这个 Test 在验证 Requirement，还是只是在确认当前代码就是这样写的？**

---

## 9.6 Evidence-Based Completion

禁止只输出：

```text
Done.
Everything looks good.
Tests should pass.
```

推荐输出：

| Claim | Evidence | Source | Result |
|---|---|---|---|
| 任务状态可持久化 | Repository test | command/log | PASS |
| 恢复后重新调度 | scenario test | test id | PASS |
| 不产生重复任务 | concurrency test | test id | PASS |
| 未产生越界修改 | git diff review | diff scope | PASS |

最后才得到：

```text
Verdict: PASS / BLOCK / WARN
```

---

# 10. Pattern 8：Rollback & Reversibility

## 10.1 Rollback 是流程设计能力

很多团队只有在 Agent 改坏代码后才想到：

> 怎么撤销？

但 Agentic Workflow 中，Reversibility 必须在任务开始前设计。

因为 Agent 会非常快地创造 dependent edits：

```text
Known Good State
      ↓
Change A
      ↓
Change B depends on A
      ↓
Change C depends on B
      ↓
Change D depends on C
      ↓
Bug discovered
```

此时回到 B 或 C 未必得到 consistent state。

---

## 10.2 开始前建立 Verified Baseline

至少确认：

```text
Git clean
Build pass
Relevant tests pass
Lint/static checks pass
```

如果 Agent 开始工作前仓库本来就是红的，那么后续失败就无法可靠 attribution。

---

## 10.3 Semantic Checkpoint

Checkpoint 不应该只是“每隔 20 分钟 commit 一次”。

应该对应一个语义完整状态：

```text
TASK-01 verified
TASK-02 verified
TASK-03 verified
```

形成：

```text
Known Good State₀
      ↓ Task 1
Verify
      ↓
Known Good State₁
      ↓ Task 2
Verify
      ↓
Known Good State₂
```

---

## 10.4 Rollback Unit 与 Task Unit 对齐

理想情况下：

```text
1 Atomic Task
≈ 1 Reviewable Change
≈ 1 Verification Unit
≈ 1 Rollback Unit
```

这会显著降低错误恢复成本。

可用机制包括：

- Git commits；
- branches；
- worktrees；
- named checkpoints；
- snapshots；
- database/config backup。

---

# 11. Pattern 9：Cleanup & Hygiene

## 11.1 “功能可运行”不等于 Done

Agent 往往优化的是：

```text
Task appears complete
```

而不是：

```text
Repository remains healthy
```

所以容易残留：

- temp files；
- debug prints；
- commented code；
- unused imports；
- obsolete TODO；
- dead path；
- skipped tests；
- outdated docs；
- unused abstraction；
- WIP commit。

这些东西不会立刻导致 Feature 失败，却会持续提高未来理解、Review 和维护成本。

---

## 11.2 三层 Cleanup

### Immediate Cleanup

每个 Step 后：

- debug output；
- temporary files；
- 临时 workaround。

### Post-Task Cleanup

Task 完成后：

- unused code；
- comments；
- imports；
- tests；
- docs；
- diff scope。

### Periodic Cleanup

PR / 多任务完成后：

- accumulated cruft；
- outdated documentation；
- stale branches；
- repository-level dead code。

---

## 11.3 Failing Test 不是垃圾

必须防止 Agent 为了“让结果变绿”做：

```text
Failing Test
   ↓
Delete / Skip Test
   ↓
All tests green
```

Failing Test 首先是诊断信号。

除非 Requirement 已经明确改变并经过授权，否则不能把删除测试当作 Cleanup。

---

## 11.4 Cleanup 是 Definition of Done

建议 DoD：

```markdown
### Code
- [ ] no debug code
- [ ] no temporary files
- [ ] no unintended dead code
- [ ] formatted / lint clean

### Tests
- [ ] relevant tests pass
- [ ] no unauthorized skips/deletions

### Documentation
- [ ] affected docs updated
- [ ] obsolete comments removed

### Git
- [ ] diff contains only intended changes
- [ ] commits/checkpoints understandable
- [ ] no unrelated generated artifacts
```

---

# 12. 完整 Code Agent Workflow

把九个 Pattern 组合后，可以得到一个适合真实软件开发的生命周期。

```text
Business Intent / Change Request
            │
            ▼
┌────────────────────────────────────┐
│ 1. DISCOVERY                       │
│                                    │
│ System / Domain / Ownership        │
│ Dependency / Constraints           │
│ Fact / Assumption / Unknown        │
└────────────────┬───────────────────┘
                 │
            Discovery Gate
                 │
                 ▼
┌────────────────────────────────────┐
│ 2. SPECIFICATION                   │
│                                    │
│ Goal / Constraints / Context       │
│ Acceptance Criteria / Out of Scope │
└────────────────┬───────────────────┘
                 │
              Spec Gate
                 │
                 ▼
┌────────────────────────────────────┐
│ 3. PLAN & TASK DECOMPOSITION       │
│                                    │
│ Stage / Task / Dependency          │
│ Scope / Context / Verification     │
└────────────────┬───────────────────┘
                 │
              Plan Gate
                 │
                 ▼
            Approved Task
                 │
          ┌──────┴────────┐
          │               │
          ▼               ▼
    Role Selection   Context Package
          │               │
          └──────┬────────┘
                 ▼
┌────────────────────────────────────┐
│ 4. INCREMENTAL EXECUTION           │
│                                    │
│ Small Change                       │
│      ↓                             │
│ Immediate Verification             │
│      ↓                             │
│ PASS?                              │
└───────────┬─────────────┬──────────┘
            │YES          │NO
            ▼             ▼
       Checkpoint     Fix / Rollback
            │             │
            └──────┬──────┘
                   ▼
                Review
                   │
          Spec Compliance
                   ↓
             Code Quality
                   │
                PASS?
                   │
          ┌────────┴────────┐
          │                 │
        YES                 NO
          │                 │
          ▼                 └→ Fix / Re-review
      Next Task
          │
          ▼
      All Tasks Done
          │
          ▼
┌────────────────────────────────────┐
│ 5. FINAL VERIFICATION              │
│                                    │
│ AC / Tests / Diff / Integration    │
│ Evidence / Verdict                 │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│ 6. CLEANUP & HYGIENE               │
└────────────────┬───────────────────┘
                 │
                 ▼
          Verified Final State
```

---

# 13. Gates：什么时候允许 Agent 进入下一阶段

把 Pattern 工程化后，最有效的做法之一是建立 Gate，而不是依赖 Agent 自己判断“已经差不多了”。

## 13.1 Discovery Gate

### PASS

- ownership 明确；
- current behavior 有证据；
- critical dependencies 已识别；
- critical assumptions 已验证；
- unresolved unknown 已显性化；
- 必要 Decision Gap 已决策。

### BLOCK

存在会改变设计方向的关键 unknown / assumption。

---

## 13.2 Specification Gate

### PASS

- Goal 明确；
- Constraints 明确；
- AC 可验证；
- Out of Scope 明确；
- 与事实一致；
- 不存在关键 intent ambiguity。

---

## 13.3 Plan Gate

### PASS

- Task 足够 atomic；
- dependency 明确；
- Scope 明确；
- Context package 可定义；
- Verification 已定义；
- Rollback 路径存在。

---

## 13.4 Execution Gate

每个 Task 开始前检查：

```text
Baseline known-good?
Task approved?
Context sufficient?
Scope bounded?
Verification ready?
Rollback available?
```

---

## 13.5 Verification Gate

不能以：

```text
Agent claims success
```

作为 PASS。

至少应存在：

```text
Claim → Independent Evidence → Result
```

---

## 13.6 Completion Gate

最终 Done 必须同时满足：

```text
Functional Correctness
+ Spec Compliance
+ Code Quality
+ Evidence Complete
+ Repository Hygiene
```

---

# 14. Code Agent 标准工作协议

下面可以直接转化成 Agent Instructions / `AGENTS.md` / `CLAUDE.md` 的基础规则。

## 14.1 MUST

Agent MUST：

1. 在不熟悉的 subsystem 上修改代码前先执行 Discovery。
2. 区分 Fact、Inference、Assumption 和 Unknown。
3. 对关键技术能力和关键系统行为提供证据来源。
4. 从明确的 Specification 工作，而不是仅依赖临时 Prompt。
5. 在实现前明确当前 Task 的 Goal、Scope 和 Verification。
6. 一次只执行一个批准的 coherent change。
7. 每个 meaningful change 后立即运行 discriminating verification。
8. 对任何超出当前 Scope 的修改先显式报告。
9. 保持可恢复的 Known-Good checkpoint。
10. 完成前 Review 实际 Diff，而不是只看测试结果。
11. 以 Evidence 支持完成声明。
12. 把长期有效知识写入 Durable Artifact。
13. 将 Cleanup 作为任务完成的一部分。

---

## 14.2 MUST NOT

Agent MUST NOT：

1. 在关键事实未知时自行发明架构事实。
2. 把 inference 表述成已验证事实。
3. 静默扩大任务范围。
4. 为了“完整”自动加入无需求支持的 abstraction。
5. 在同一修改中混入无关 refactor。
6. 只依靠 self-review 证明实现正确。
7. 根据当前实现反向制造只会通过的测试。
8. 未经授权删除 failing tests。
9. 在 Verification 失败后继续执行依赖该结果的后续 Task。
10. 在没有 checkpoint 的情况下执行高风险大修改。
11. 把整个 repository / transcript 无差别塞入 Context。
12. 用“应该没问题”“看起来正确”代替 Evidence。

---

## 14.3 SHOULD

Agent SHOULD：

- 优先小 Diff；
- 优先已有 codebase patterns；
- 优先最便宜的 falsification check；
- 在任务范围改变时返回 Plan，而不是临时 improvisation；
- 对实现和 Review 使用独立 Context；
- 为长期任务维护 Handoff Artifact；
- 在必要时启动 fresh session；
- 把重复使用的流程固化为 Skill；
- 把重复发生的错误固化为 Agent Config 中的 anti-pattern。

---

# 15. 推荐的工程 Artifacts

一个较完整的 Code Agent 项目可以使用：

```text
repo/
├── AGENTS.md
├── docs/
│   ├── discovery/
│   │   └── feature-x-discovery.md
│   ├── specs/
│   │   └── feature-x-spec.md
│   ├── plans/
│   │   └── feature-x-plan.md
│   ├── tasks/
│   │   └── feature-x-tasks.md
│   ├── verification/
│   │   └── feature-x-verification.md
│   └── adr/
│       └── ADR-xxx.md
├── skills/
│   └── ...
└── ...
```

## 15.1 Artifact 生命周期

| Artifact | Producer | Consumer | 目的 |
|---|---|---|---|
| `discovery.md` | Explorer | Spec/Architect | 建立事实和未知 |
| `spec.md` | Product/Spec Agent + Human | Planner/Reviewer | 定义 Intent |
| `plan.md` | Planner | Implementer | 定义执行顺序 |
| `tasks.md` | Planner | Implementer/Subagents | 定义 atomic work |
| `handoff.md` | 任一角色 | Next Role | 跨 Context 传递状态 |
| `verification.md` | Test/Review Agent | Gate/Human | 记录 Evidence |
| `ADR` | Architect | Future Agents | 保存 Why |
| `AGENTS.md` | Team | All Agents | 永久约束和反模式 |
| `SKILL.md` | Team | Agents | 可复用 Procedure |

核心思想：

> Conversation 负责交互，Artifact 负责工程状态。

---

# 16. 常见 Anti-Patterns

## 16.1 Prompt-and-Pray

```text
“帮我把整个功能实现好。”
```

然后等待 Agent 输出大批代码。

问题：没有 Local Model、Scope、Verification 和 Rollback Boundary。

---

## 16.2 Coding Before Discovery

Agent 找到第一个看起来相关的类就开始修改。

问题：Code Location 不等于 Behavior Ownership。

---

## 16.3 One-Agent-Does-Everything

同一 Agent：

```text
探索 → 设计 → 实现 → 测试 → Review
```

问题：Context Pollution + Self-Legitimization。

---

## 16.4 Context Dumping

把整个 Repo、所有文档和完整会话一次塞给 Agent。

问题：More Context ≠ Better Context。

---

## 16.5 Big-Bang Implementation

一个 Prompt 改几十个文件。

问题：难以定位哪一个 assumption 首先失效。

---

## 16.6 Self-Generated Oracle

```text
实现 → 根据实现生成测试 → 测试通过
```

问题：测试可能只验证当前实现，而不是 requirement。

---

## 16.7 No Baseline

在 dirty / broken repository 上开始任务。

问题：无法区分 pre-existing failure 与 agent-introduced failure。

---

## 16.8 No Checkpoint

Agent 连续执行多个任务后才提交。

问题：Rollback Unit 过大。

---

## 16.9 Green-at-All-Costs

失败测试直接被删掉或 skip。

问题：通过删除 Evidence 制造虚假正确。

---

## 16.10 Done-Without-Cleanup

功能可运行就宣布完成。

问题：短期 Agent Productivity 转化为长期 Maintenance Debt。

---

# 17. 端到端案例：Android 网络恢复后继续同步

下面用一个小 Feature 串起所有 Pattern。

## 17.1 Business Intent

> 当 Android App 因网络断开导致云同步失败时，在网络恢复后自动继续尚未完成的同步任务。

不要立即要求 Agent 写 WorkManager 代码。

---

## 17.2 Discovery

Explorer 首先查明：

```text
FACT-01
当前上传由 SyncRepository 发起。
Evidence: ...

FACT-02
任务状态持久化到 Room。
Evidence: ...

FACT-03
当前网络失败会把任务标记为 FAILED，而不是 RETRY_PENDING。
Evidence: ...

UNKNOWN-01
App 被 force-stop 后是否还要求自动恢复？

ASSUMPTION-01
WorkManager 可以满足目标 Android API level 的网络约束调度。
Needs verification against project version/docs.

DECISION_GAP-01
恢复策略：立即重试还是指数退避？
```

此时如果 `UNKNOWN-01` 会改变方案，就应该阻塞进入 Implementation。

---

## 17.3 Specification

```markdown
## Goal
此前因网络不可用而未完成的云同步任务，在网络重新可用后自动继续。

## Constraints
- MUST 使用现有持久化任务模型。
- MUST 保持任务幂等。
- MUST NOT 修改服务端协议。
- MUST NOT 引入常驻后台 Service。

## Acceptance Criteria
- 网络失败不会丢失未完成任务。
- 网络恢复后任务可自动重新调度。
- 多次网络变化不会创建重复上传。
- 进程重启后未完成任务仍然可恢复。
- 现有手动同步行为不回归。

## Out of Scope
- 不修改服务端重试策略。
- 不重新设计同步 UI。
```

---

## 17.4 Plan

```text
TASK-01
明确 SyncTask 状态模型并增加 retryable state。
Verify: state unit tests

TASK-02
Repository 保存 network-retryable failure。
Depends on: TASK-01
Verify: repository tests

TASK-03
增加 network constraint scheduler。
Depends on: TASK-02
Verify: scheduler tests

TASK-04
实现 duplicate scheduling protection。
Depends on: TASK-03
Verify: concurrency/idempotency test

TASK-05
场景级验证：offline → failure → online → resumed。
Depends on: TASK-01..04
Verify: scenario test
```

---

## 17.5 Context Package

TASK-03 Implementer 只需要：

```text
TASK-03 scope
relevant Spec AC
SyncScheduler interface
current WorkManager version
existing worker examples
related tests
```

不需要加载整个 Gallery App。

---

## 17.6 Incremental Execution

TASK-03：

```text
Step 1: add scheduler contract
→ compile
→ checkpoint

Step 2: implement WorkManager adapter
→ targeted tests
→ checkpoint

Step 3: wire repository to scheduler
→ integration test
→ checkpoint
```

任一步失败，不继续执行下一步。

---

## 17.7 Independent Review

### Spec Compliance Reviewer

检查：

- 是否真的只在 retryable network failure 上重新调度；
- 是否满足 AC；
- 是否偷偷改了手动同步；
- 是否引入 out-of-scope 行为。

### Code Quality Reviewer

在 compliance PASS 后检查：

- WorkManager 使用是否符合项目现有 pattern；
- 是否产生不必要 abstraction；
- concurrency 是否清晰；
- 状态转换是否可维护。

---

## 17.8 Verification

最终证据：

```text
AC-01 → repository test → PASS
AC-02 → WorkManager scheduler test → PASS
AC-03 → duplicate scheduling test → PASS
AC-04 → process restart persistence test → PASS
AC-05 → regression suite → PASS
Diff scope review → PASS
Static/lint → PASS
```

---

## 17.9 Rollback

每个 Task 已对应独立 checkpoint。

如果 TASK-04 concurrency 方案失败，可以回到：

```text
Known Good State after TASK-03
```

而不是丢弃整个 Feature。

---

## 17.10 Cleanup

最后：

- 删除调试日志；
- 删除临时测试 helper；
- 确认没有 skipped test；
- 更新同步状态文档；
- Review final diff；
- 输出 final verification report。

此时才是真正的 Done。

---

# 18. 从九个 Pattern 得到的核心工程原则

## 原则 1：先理解，再改变

```text
Explanation before Implementation
Evidence before Trust
```

## 原则 2：Intent 必须外部化

```text
Business Intent
→ Spec
→ AC
```

不要让真正需求只存在聊天中。

## 原则 3：任务边界必须先于执行

```text
Plan before Execution
```

不要让 Agent 在写代码时顺便决定自己应该做什么。

## 原则 4：小步前进

```text
Small Change
→ Verify
→ Checkpoint
```

不是因为 Agent 写不了大修改，而是因为人无法便宜地验证和恢复大修改。

## 原则 5：Context 是需要治理的资产

```text
Relevant > Large
Authoritative > Conversational
Persistent Artifact > Agent Memory
```

## 原则 6：生产与验证需要认知独立性

```text
Implementation ≠ Oracle
Implementer ≠ Sole Reviewer
```

## 原则 7：完成必须有 Evidence

```text
Claim
→ Evidence
→ Verdict
```

## 原则 8：任何复杂变更都应该可逆

```text
No risky change without a recovery target.
```

## 原则 9：Repository Health 是交付物的一部分

```text
Done
=
Feature Correct
+ Evidence Complete
+ Repository Clean
```

---

# 19. 最终模型：Code Agent 的工作单位是什么

传统 AI Coding 容易把工作建模为：

```text
Prompt
   ↓
Generated Code
   ↓
Review
```

九个 Agentic Patterns 组合之后，更成熟的模型是：

```text
                 ┌─────────────────┐
                 │ Verified State₀ │
                 └────────┬────────┘
                          │
                  Explicit Intent
                          │
                  Controlled Scope
                          │
                     Small Change
                          │
               Independent Verification
                          │
                   PASS / Rollback
                          │
                 ┌────────▼────────┐
                 │ Verified State₁ │
                 └─────────────────┘
```

然后循环：

```text
Verified State₀
      ↓ Controlled Change₁
Verified State₁
      ↓ Controlled Change₂
Verified State₂
      ↓ Controlled Change₃
Verified State₃
```

因此，Code Agent 的真正工作单位不是：

> **Prompt → Code**

而是：

> **Verified State → Controlled Change → Verified State**

这也是九个 Pattern 可以统一起来的核心思想。

---

# 20. 一个可直接使用的 Code Agent Checklist

## Before Coding

- [ ] 我是否知道真正的 behavior owner？
- [ ] Current behavior 是否有证据？
- [ ] 关键 dependency 是否已经映射？
- [ ] Fact / Assumption / Unknown 是否分开？
- [ ] 是否存在阻塞性的 Decision Gap？
- [ ] 是否已经形成明确 Spec？
- [ ] AC 是否可验证？
- [ ] 当前 Task 是否 atomic / reviewable / verifiable？
- [ ] Baseline 是否 known-good？
- [ ] Rollback target 是否存在？

## During Coding

- [ ] 当前修改是否仍然在 Scope 内？
- [ ] 是否一次只处理一个 coherent change？
- [ ] 修改后是否立即执行 verification？
- [ ] Verification 是否有机会证伪当前实现？
- [ ] Context 是否已经出现污染或过期？
- [ ] 是否应该启动 fresh role/session？
- [ ] 是否正在产生无需求支持的 abstraction？

## Before Declaring Done

- [ ] 每个 AC 是否都有 Evidence？
- [ ] Spec Compliance Review 是否 PASS？
- [ ] Code Quality Review 是否 PASS？
- [ ] 有没有未经授权的 test skip/delete？
- [ ] Diff 是否只有预期修改？
- [ ] 是否完成 Cleanup？
- [ ] Durable Artifact 是否已更新？
- [ ] 最终状态是否可作为新的 Known-Good State？

---

# 21. 结论

Agentic Coding 的价值并不只是让软件工程师“少写代码”。如果只是把传统的编码任务一次性扔给 Agent，团队只是把人工编码风险替换成了高速自动生成风险。

真正成熟的 Code Agent 工程方法，应当做到：

```text
先发现事实，而不是先生成实现；
先定义 Intent，而不是依赖 Prompt 猜测；
先分解任务，而不是边做边决定；
小步修改，而不是批量堆积；
控制角色和 Context，而不是让一个 Session 无限膨胀；
用独立验证寻找反例，而不是相信 Agent 的自我评价；
在失败之前准备恢复路径；
把 Repository Health 纳入 Done。
```

可以将整套方法浓缩为：

```text
Reliable Agentic Development
=
Verified Understanding
× Explicit Intent
× Bounded Tasks
× Scoped Context
× Incremental Change
× Independent Verification
× Cheap Reversibility
× Repository Hygiene
```

当这些能力组合在一起时，Code Agent 才从“代码生成工具”升级为一个真正可以纳入工程流程的 **Controlled Change Agent**。

---

# 参考资料

本文主要基于 SE-ML 于 2026 年发布的 **Agentic Coding: A Pattern Language** 及其 Pattern Catalog：

1. Agentic Coding: A Pattern Language  
   https://se-ml.github.io/agentic_patterns/

2. Agent-Assisted Discovery  
   https://se-ml.github.io/agentic_patterns/01-agent-assisted-discovery/

3. Specification-Driven Development  
   https://se-ml.github.io/agentic_patterns/02-specification-driven-dev/

4. Plan-Driven Task Decomposition  
   https://se-ml.github.io/agentic_patterns/03-plan-driven-task-decomposition/

5. Incremental Execution  
   https://se-ml.github.io/agentic_patterns/04-incremental-execution/

6. Role-Based Development & Subagents  
   https://se-ml.github.io/agentic_patterns/05-role-based-development/

7. Memory & Context Management  
   https://se-ml.github.io/agentic_patterns/06-memory-context-management/

8. Verification-First Engineering  
   https://se-ml.github.io/agentic_patterns/07-verification-first/

9. Rollback & Reversibility  
   https://se-ml.github.io/agentic_patterns/08-rollback-reversibility/

10. Cleanup & Hygiene  
    https://se-ml.github.io/agentic_patterns/09-cleanup-hygiene/

> 注：SE-ML 原页面明确说明，这些 Pattern 是针对重复出现工程问题的 recurrent responses，不应被理解为固定 methodology，也不代表已经通过实证证明能保证改善。本文在原始 Pattern 之上增加了 Gate、Finding 分类、Artifact 映射和端到端 Workflow，用于把 Pattern Language 转化为可执行的 Code Agent 工程指导。
