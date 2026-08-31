# Gate1 实现方案草案

> 文件名：`gate1_spec_draft_0831.md`  
> 版本：Draft 0.1  
> 日期：2026-08-31  
> 目标：定义 Gate1 在“编码开始前”的实现级检查方案，包括输入、检查阶段、统一检查模型、问题项、阻断规则、测试设计与追溯闭环。

---

# 1. Gate1 定位

Gate1 是进入编码前的**实现就绪门禁**。

本轮只设计 Gate1，不展开 Gate2～Gate4。

Gate1 的目标不是要求所有未知都被消灭，而是确保：

- 需求定义已经达到可实现状态；
- 技术方案已经正确承接需求；
- 测试设计已经完成；
- 关键 Story、AC、Rule、设计决策已经建立测试覆盖；
- 不存在需要开发者或编码智能体自行补充的高影响未决决策。

Gate1 最终通过的核心条件为：

```text
需求就绪
AND
技术方案就绪
AND
测试设计就绪
AND
不存在未关闭的高影响决策缺口
        ↓
    Gate1 PASS
```

---

# 2. Gate1 总结性目标

Gate1 的总结性目标是：

> 在编码开始前，确认需求定义、技术方案和验证设计已经形成完整、明确、一致、可实现、可验证且可追溯的工程闭环，使开发者或编码智能体无需自行补充会改变关键结果的重要决策，并且所有关键需求、规则和设计承诺都有明确测试用例负责验证。

Gate1 回答三个问题：

```text
① WHAT 是否清楚？
   要做什么？

② HOW 是否成立？
   准备怎么实现？

③ HOW TO PROVE 是否清楚？
   怎么证明做对了？
```

因此 Gate1 的检查对象分为三层：

```text
需求定义
WHAT
   ↓
技术方案
HOW
   ↓
测试设计
HOW TO PROVE
```

---

# 3. Gate1 总体流程

Gate1 对外是一个门禁，对内分为三个主要检查阶段和一个跨对象闭环检查阶段。

```text
                    Gate1
                      │
                      ▼
        ┌────────────────────────┐
        │ ① 需求定义检查         │
        │    WHAT                │
        └───────────┬────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │ ② 技术方案检查         │
        │    HOW                 │
        └───────────┬────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │ ③ 测试设计检查         │
        │    HOW TO PROVE        │
        └───────────┬────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │ ④ 跨对象闭环检查       │
        │ WHAT ↔ HOW ↔ PROVE    │
        └───────────┬────────────┘
                    │
                    ▼
               问题项集合
                    │
                    ▼
               实质影响判断
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        通过       警告       阻断
```

---

# 4. Gate1 输入

Gate1 不强制研发团队使用固定文档模板。

允许输入来源包括：

- PRD；
- Spec；
- Story；
- AC；
- UX / UI 交互说明；
- 业务规则；
- API / 接口文档；
- 技术设计；
- 架构文档；
- 实现计划；
- Task；
- 测试设计；
- 安全规范；
- 隐私规范；
- 平台约束；
- 非功能约束；
- 代码库知识；
- 历史设计决策；
- 其他与本 Feature 相关的工程资料。

Gate1 不直接对文档格式做强耦合，而是先将不同来源转换为统一内部语义模型。

---

# 5. 标准化语义模型

Gate1 首先由大模型对输入材料进行语义归一化。

统一内部模型建议如下：

```text
Gate1 Canonical Model
│
├── 目标
├── 范围
├── Story
│
├── 行为
│   ├── 场景
│   ├── 流程
│   ├── Rule
│   ├── State
│   └── 异常 / 边界
│
├── 数据
├── 接口契约
├── 依赖
├── 工程约束
│
├── 设计决策
├── 技术方案
├── 实现任务
│
└── Test Case
```

每一个标准化对象必须保留来源信息。

示例：

```yaml
id: RULE-012
type: rule

statement:
  "冻结账户禁止创建新的支付订单"

source:
  document: prd.md
  section: 5.3

confidence: 0.97
```

核心要求：

> Gate1 后续形成的所有问题项，都必须能够回溯到原始证据。

---

# 6. 统一检查属性

Gate1 对需求、技术方案和测试设计统一使用六项质量属性。

| 属性 | 核心判断 |
|---|---|
| 完整性 | 必须存在的关键定义是否遗漏 |
| 明确性 | 已有定义是否存在多种合理解释 |
| 一致性 | 不同定义之间是否发生冲突 |
| 可实现性 | 在平台、依赖、架构和资源约束下是否能够实现 |
| 可验证性 | 完成后是否能够客观判断正确与否 |
| 可追溯与覆盖 | 上游定义是否被下游完整承接 |

统一检查模型为：

```text
检查对象 × 质量属性
        ↓
    候选问题项
```

---

# 7. 阶段一：需求定义检查

需求阶段回答：

> 我们到底要做什么，是否已经定义到足以进入技术设计和编码？

## 7.1 检查对象

| 一级对象 | 二级对象 |
|---|---|
| 意图与范围 | Goal、Actor、Scope、Out-of-Scope |
| 行为 | Story、Scenario、Flow |
| 规则 | Rule、Invariant |
| 状态 | State、Transition |
| 数据 | Business Object、Field、Lifecycle |
| 契约 | API、Protocol、Dependency |
| 边界 | Boundary、Error、Failure、Recovery |
| 约束 | Security、Privacy、Performance、Compatibility、Platform |
| 验收 | AC、Expected Result |

## 7.2 检查方式

需求检查包含两种方式：

### 7.2.1 已定义内容检查

对文档中已经存在的对象执行：

```text
Object × Quality Attribute
```

例如：

- 已有 Rule 是否完整；
- 已有 Scenario 是否明确；
- AC 是否可验证；
- State 是否与 Scenario 一致；
- API 与业务规则是否冲突。

解决的是：

> 已经写出来的内容质量怎么样？

### 7.2.2 主动遗漏探索

Gate1 不能只 Review 已有内容，还必须主动寻找本来应该存在、但没有写出来的定义。

探索空间至少包括：

- 角色空间；
- 流程空间；
- 状态空间；
- 规则空间；
- 数据空间；
- 权限空间；
- 依赖空间；
- 时间空间；
- 并发空间；
- 异常空间；
- 恢复空间；
- 性能空间；
- 兼容空间；
- 生命周期空间。

例如：

```text
需求：
用户可以下载照片。
```

主动探索可能得到：

```text
网络中断怎么办？
存储空间不足怎么办？
重复下载怎么办？
权限被撤销怎么办？
文件已存在怎么办？
进程被杀怎么办？
后台限制怎么办？
```

这些探索结果首先只形成：

```text
Gap Candidate
```

不能直接阻断。

---

# 8. 阶段二：技术方案检查

技术方案阶段回答：

> 技术方案是否正确、完整地承接了需求定义？

## 8.1 主要检查对象

- 架构决策；
- 组件职责；
- 数据流；
- 状态处理；
- API 设计；
- 数据持久化；
- 并发策略；
- 异常处理；
- 安全设计；
- 兼容设计；
- 实现计划；
- 关键技术决策。

同样执行：

```text
设计对象 × 六项质量属性
```

## 8.2 需求到设计的覆盖检查

技术方案检查不仅判断“设计本身好不好”，还必须判断“设计有没有承接需求”。

核心关系：

```text
Requirement / Story / AC / Rule / Constraint
                 ↓
          Design Commitment
```

例如：

```text
RULE-12
冻结账号禁止支付
       │
       ▼
DESIGN-08
PaymentGuard
       │
       ▼
已覆盖
```

如果出现：

```text
RULE-12
       │
       X
没有任何设计承接
```

则形成问题项。

## 8.3 反向来源检查

Gate1 还必须检查：

```text
Design Decision
      ↓
是否存在 Requirement / Constraint 来源
```

如果一个关键设计决策找不到需求、约束或风险来源，则应形成问题项，避免技术方案自行扩张需求范围。

---

# 9. 阶段三：测试设计检查

测试设计是 Gate1 的硬性准入条件。

Gate1 通过前：

> 测试用例设计必须已经完成。

这里要求的是**测试设计完成**，不是要求自动化测试代码已经实现。

测试代码实现属于编码阶段。

---

# 10. 测试用例最低结构

每一个测试用例至少应该包含：

```yaml
id: TC-023

title:
  冻结账户发起支付

story:
  - STORY-04

ac:
  - AC-07

rules:
  - RULE-12

design_decisions:
  - DD-08

preconditions:
  - account.status = FROZEN

action:
  - create_payment()

expected:
  - request rejected
  - error = ACCOUNT_FROZEN

test_level:
  medium

environment:
  payment-service: mock

automation:
  status: planned
```

最低要求包括：

- 前置条件；
- 输入或测试数据；
- 操作；
- 预期结果；
- 测试层级；
- 环境和依赖；
- 关联 Story；
- 关联 AC；
- 关联 Rule；
- 关联设计决策；
- 自动化状态。

---

# 11. 测试追溯模型

Gate1 不要求每个 Test Case 机械同时绑定 Story、AC、Rule、设计决策四类对象。

正确模型是建立验证覆盖图谱。

```text
                        Story
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
             AC          Rule     Design Decision
              │           │           │
              └───────────┼───────────┘
                          ▼
                      Test Case
```

需要检查四类覆盖关系。

## 11.1 Story 覆盖

```text
Story
  ↓
是否存在对应验收测试用例
```

## 11.2 AC 覆盖

```text
AC
 ↓
是否存在 Test Case
```

## 11.3 Rule 覆盖

```text
Rule
 ↓
是否存在 Test Case
```

## 11.4 设计决策覆盖

对于具有可验证行为或质量承诺的关键设计决策：

```text
Design Decision
       ↓
是否存在 Test Case
```

例如：

```text
DD-12:
离线缓存采用 stale-while-revalidate
```

应存在对应测试用例验证其行为。

---

# 12. 验证覆盖矩阵

Gate1 建议生成统一验证覆盖矩阵。

示例：

| Story | AC | Rule | Design Decision | Test Case | 状态 |
|---|---|---|---|---|---|
| S01 | AC01 | R01 | DD03 | TC01 | 已覆盖 |
| S01 | AC02 | R03 | DD04 | TC02 / TC03 | 已覆盖 |
| S01 | AC03 | — | DD05 | — | 缺失 |
| S02 | AC07 | R12 | DD08 | TC23 | 已覆盖 |

Gate1 需要能够直接识别：

- Story 无测试覆盖；
- AC 无测试覆盖；
- Rule 无测试覆盖；
- 关键 Design Decision 无测试覆盖。

---

# 13. Test Case 自身质量检查

Gate1 不能只检查“有没有 Test Case ID”。

还必须检查测试用例本身是否有效。

| 属性 | 检查内容 |
|---|---|
| 完整性 | 前置条件、输入、操作、预期结果是否完整 |
| 明确性 | 操作和预期结果是否无歧义 |
| 一致性 | Expected 是否与 AC / Rule 一致 |
| 可执行性 | 前置条件和测试环境是否真实可建立 |
| 可判定性 | Expected 是否能够客观断言 |
| 可追溯性 | 是否真正覆盖其声明的 Story / AC / Rule / Design Decision |

因此 Test Case 本身也是 Gate1 的正式检查对象。

---

# 14. 阶段四：跨对象闭环检查

单独需求、技术方案和测试设计都写得好，不代表 Gate1 可以通过。

Gate1 必须检查：

```text
WHAT
 │
 ▼
HOW
 │
 ▼
HOW TO PROVE
```

形成完整工程闭环：

```text
Story
  ↓
AC / Rule
  ↓
Design Decision
  ↓
Implementation Task
  ↓
Test Case
```

这里不要求所有关系 1:1。

允许：

```text
1 Requirement → N Test Cases
N Rules → 1 Design Decision
1 Design Decision → N Tasks
```

Gate1 检查的是：

> 覆盖关系是否闭合，而不是关系是不是一对一。

---

# 15. 候选问题项与反证搜索

大模型首次发现的问题不能直接成为正式问题项。

所有发现先形成：

```text
Candidate Finding
```

例如：

```text
“没有发现存储空间不足时的下载行为。”
```

随后必须执行反证搜索。

搜索范围包括：

- PRD；
- Story；
- AC；
- Rule；
- UX；
- API；
- 技术方案；
- 测试用例；
- 平台规范；
- 安全规范；
- 相关既有 Feature 定义。

如果发现：

```text
Rule-18:
存储不足返回 STORAGE_FULL
```

则候选问题项关闭。

如果完整搜索后仍不存在相关定义，才升级为正式问题项。

核心原则：

> 没看到，不等于不存在。

---

# 16. 问题项标准结构

建议 Gate1 正式问题项采用如下结构：

```yaml
finding_id: G1-F-017

stage:
  requirement

object:
  type: scenario
  id: SC-08

attribute:
  completeness

problem:
  存储空间不足时的下载行为未定义

evidence:
  - source: prd.md
    section: download

counter_evidence_search:
  status: not_found

impact:
  - user_behavior
  - acceptance_result

decision_required:
  是否保留下载任务以及如何提示用户

severity:
  high

disposition:
  block

status:
  open
```

问题项必须至少包含：

- 所属检查阶段；
- 检查对象；
- 失败属性；
- 问题描述；
- 证据；
- 反证搜索结果；
- 影响维度；
- 需要补充的决策；
- 严重度；
- 门禁处置；
- 当前状态。

---

# 17. 严重度与门禁结论分离

严重度和是否阻断不能混为一个维度。

建议拆分：

```text
Severity：
Critical / High / Medium / Low

Disposition：
BLOCK / WARN / INFO
```

例如：

```text
High Finding
+
已有批准的安全默认值
=
WARN
```

而不是简单规定：

```text
High = BLOCK
```

---

# 18. 实质影响判断

问题项不直接等于阻断。

Gate1 需要判断：

> 如果这个问题不解决，实现者或编码智能体是否必须自行做一个高影响决策？

重点评估七个影响维度：

- 用户行为；
- 业务语义；
- 数据语义；
- 外部契约；
- 关键架构；
- 安全 / 隐私 / 合规；
- 验收结果。

核心阻断条件：

```text
Unresolved Finding
+
High-impact Decision
        ↓
      BLOCK
```

---

# 19. 决策权限策略

Gate1 建议建立显式的决策权限策略。

## 19.1 编码智能体允许自主决定

包括：

- 局部变量命名；
- 内部函数拆分；
- 代码格式；
- 已有架构模式下的常规实现；
- 无外部行为影响的重构；
- 项目规范已经明确规定的默认方式。

## 19.2 编码智能体不得自主决定

包括：

- 用户行为；
- 业务规则；
- 状态语义；
- 数据生命周期；
- 公共接口语义；
- 权限；
- 隐私；
- 安全；
- 关键架构模式；
- 错误恢复语义；
- 验收结果。

如果后一类决策没有明确：

```text
未定义
   ↓
问题项
   ↓
阻断
   ↓
人工决策
```

---

# 20. 六类典型阻断模式

阻断模式不是检查对象，也不是质量属性。

它们是问题项经过实质影响判断后的典型阻断结果。

## 20.1 关键定义缺失

例如：

> 删除到底是永久删除还是进入回收站没有定义。

如果不同选择会改变用户行为、业务语义或验收结果，则阻断。

## 20.2 关键定义存在多种合理解释

例如：

> “失败后自动重试。”

但未定义：

```text
3 次？
无限？
指数退避？
前台？
后台？
```

如果不同实现会产生不同关键行为，则阻断。

## 20.3 关键定义互相冲突

例如：

```text
AC：
删除立即不可恢复

Design：
删除后保留30天
```

存在关键语义冲突，应阻断。

## 20.4 要求或技术方案不可成立

例如：

> Android 平台机制不支持技术方案假设的后台执行行为。

如果无法可信实现，则阻断。

## 20.5 关键行为无法验证

例如：

```text
AC：
页面打开速度要快
```

没有客观判据，则无法形成可信验收，应阻断。

## 20.6 追溯链断裂

例如：

```text
AC-17
  ↓
没有 Test Case
```

或者：

```text
RULE-08
  ↓
没有 Design Commitment
```

或者：

```text
Design Decision-12
  ↓
没有验证
```

对于关键对象，覆盖链断裂应阻断。

---

# 21. Gate1 最终 PASS 条件

Gate1 最终通过条件压缩为四项。

## 21.1 需求定义就绪

不存在未关闭的、高影响需求定义问题。

## 21.2 技术方案就绪

所有关键需求、规则和工程约束都有可信设计承接。

## 21.3 测试设计就绪

关键 Story、AC、Rule 和可验证的关键设计决策已经存在 Test Case 覆盖。

## 21.4 高影响决策全部关闭

不存在需要开发者或编码智能体自行处理的高影响未决决策。

最终：

```text
Requirement Ready
      AND
Design Ready
      AND
Verification Ready
      AND
No Material Decision Gap
              ↓
          Gate1 PASS
```

---

# 22. Gate1 最终执行链路

```text
              输入 Artifact
                    │
                    ▼
           ① 语义归一化
                    │
                    ▼
           Canonical Model
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
  ② 已定义质量检查       ③ 主动缺口探索
 Object × Attribute      Exploration Space
          │                   │
          └─────────┬─────────┘
                    ▼
            Candidate Finding
                    │
                    ▼
             ④ 反证搜索
                    │
                    ▼
               正式问题项
                    │
                    ▼
          ⑤ 实质影响分析
                    │
                    ▼
          Decision Authority
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        PASS       WARN      BLOCK
                              │
                              ▼
                         Human Decision
                              │
                              ▼
                         Finding Close
                              │
                              ▼
                         Gate1 PASS
```

---

# 23. Gate1 的核心闭环

Gate1 最终建立的是一个三角闭环：

```text
                    需求
                   WHAT
                  /    \
                 /      \
                /        \
               ▼          ▼
          技术方案 ───── 测试设计
             HOW       HOW TO PROVE
```

含义：

- 需求定义正确世界；
- 技术方案承诺如何构造这个世界；
- 测试用例在编码前定义如何证明这个世界被正确构造。

Gate1 不只是“需求质量检查”，也不只是“设计 Review”。

其本质是：

> 在编码开始前，把需求、技术方案和验证设计收敛为一个可执行、可验证、可追溯的工程契约。

---

# 24. 后续实现需要继续细化的内容

本草案完成 Gate1 总体机制和核心检查逻辑的定义。

下一步进入实现级 Spec 时，需要进一步细化：

1. Canonical Model 的完整 JSON Schema；
2. 各类检查对象的 Schema；
3. Test Case Schema；
4. Story / AC / Rule / Design Decision / Test Case 关系模型；
5. 候选问题项 Schema；
6. 正式 Finding Schema；
7. Severity Policy；
8. BLOCK Policy；
9. Decision Authority Policy；
10. Exploration Space 知识库；
11. 反证搜索策略；
12. LLM Prompt / Agent 分工；
13. Evidence 定位格式；
14. Gate1 JSON 输出格式；
15. Gate1 HTML 报告格式；
16. CI 接口；
17. Finding 生命周期；
18. 人工决策与回写机制。

---

# 25. 当前已确认的关键决策

| 决策项 | 当前结论 |
|---|---|
| 本轮范围 | 只设计 Gate1 |
| Gate1 时点 | 技术方案完成后、编码前 |
| Gate1 内部顺序 | 先检查需求，再检查技术方案，再检查测试设计 |
| 输入方式 | 接受多种文档，内部统一语义模型 |
| 检查方式 | 已定义内容 Review + 主动缺口探索 |
| LLM 职责 | 语义发现、证据分析、影响分析 |
| 最终阻断 | 由显式 Policy 决定 |
| 未定义决策 | 低风险允许默认，高影响必须升级 |
| 测试要求 | Gate1 前测试设计必须完成 |
| 自动化测试代码 | 不要求 Gate1 前实现 |
| 测试追溯 | 绑定 Story、AC、Rule、关键设计决策 |
| 覆盖原则 | 关键对象必须有测试覆盖，不要求机械 1:1 |
| Finding 证据 | 必须有 Evidence，并执行反证搜索 |
| 严重度与阻断 | 两个维度分离 |

---

> 本文档为 Gate1 实现方案草案，下一步可在此基础上进一步转换为正式实现 Spec。
