# AI Native 软件质量门禁知识总览

> 版本：V0.1  
> 日期：2026-08-25  
> 文档状态：第一版收敛基线，尚未全部定稿  
> 当前主线：先收敛 Gate1 V1，再衔接 Gate2；Gate3、Gate4 暂不展开实现  
> 用途：作为后续讨论的唯一入口，保存“当前有效状态”；重要决策的历史原因由 `docs/decisions/` 中的 Decision Record（DR）保存。

---

## 0. 文档使用规则

### 0.1 状态定义

| 状态 | 含义 | 后续处理 |
|---|---|---|
| `已确认` | 已形成稳定共识并作为当前设计输入 | 除非出现新证据、反例或新的 DR，否则不重新讨论 |
| `待确认` | 已有较强候选结论，但尚未完成最终决策或仍有冲突 | 进入开放问题清单，按优先级闭合 |
| `已被替代` | 曾经使用过，但已被更新结论或新版本取代 | 仅保留历史解释，不再作为设计输入 |
| `暂不处理` | 有价值，但不进入当前阶段范围 | 放入后续路线图，不阻断当前工作 |

### 0.2 维护原则

1. 本文只保存“当前状态”，不复刻完整讨论过程。
2. 同一结论只有一个当前状态；出现新结论时必须说明替代了什么。
3. `已确认`结论默认不再重新论证，除非出现新证据、反例、范围变化或新的 Decision Record。
4. `待确认`问题必须有具体决策问题，不能只写“后续完善”。
5. 每次讨论结束后，至少更新：当前状态、开放问题、交付件索引、下一步。
6. 聊天记录是探索过程，不是软件质量体系的事实源。
7. 影响 Gate 边界、核心对象模型、Canonical Schema、Traceability Relationship、Gate Policy 或关键术语的语义变化，必须创建 Decision Record。
8. Decision Record 回答“为什么这样决定”；Overview 回答“现在是什么”；Git PR / Commit 回答“具体改了什么”。
9. Accepted DR 不通过改写历史理由来适配新结论；决策变化时创建新的 DR，并用 `Superseded by` 建立替代关系。

### 0.3 Decision Record 入口

- 决策索引与治理规则：`docs/decisions/README.md`
- DR 模板：`docs/decisions/DR-TEMPLATE.md`
- 历史补录清单：`docs/decisions/decision-backlog.md`
- 当前首个正式决策：`DR-0001`——Verification Obligation 不作为 V1 一等追溯对象

---

# 1. 当前结论摘要

## 1.1 北极星目标

**状态：已确认**

建设一套贯穿软件研发生命周期的质量门禁体系，在关键状态流转点，基于明确对象、可追溯关系、可信证据和版本化策略，作出 `PASS / WARN / BLOCK` 等准入或准出决策。

门禁不是：

- 检查项集合；
- 文档评分器；
- Code Review 的别名；
- 自动化测试平台；
- LLM 自由给出的质量意见；
- 一个审批按钮。

门禁的共同逻辑是：

```text
被评估对象
    ↓
Finding
    ↓
Risk
    ↓
Evidence
    ↓
Versioned Policy
    ↓
Verdict
```

其中：

- `Finding`：发现的事实、缺口、冲突或失败。
- `Risk`：Finding 对当前生命周期决策造成的潜在影响。
- `Evidence`：支持 Finding 或证明要求已满足的可审计证据。
- `Policy`：预先定义、可版本化的判定规则。
- `Verdict`：策略执行后的准入或准出结论。

## 1.2 当前建设策略

**状态：已确认**

```text
先闭环，再扩展
先最小关系模型，再完整知识图谱
先确定性检查，再增强语义分析
先高置信阻断，再扩展低置信发现
先 Gate1 / Gate2，再 Gate3 / Gate4
```

第一阶段不追求“发现所有问题”，而是先阻止明确不应进入下一阶段的问题，并保证每次阻断可解释、可定位、可解除。

---

# 2. 当前质量体系总图

## 2.1 四层门禁

| 门禁 | 生命周期位置 | 核心评估对象 | 核心决策问题 | 当前状态 |
|---|---|---|---|---|
| Gate1 | 进入编码前 | Feature / Story 及其 Product、UX、Technical Spec | 是否达到 Engineering Ready，工程是否无需发明关键行为、Oracle 或跨边界契约即可安全开工 | 正在收敛 V1 |
| Gate2 | Change / PR 合入共享基线前 | 一次确定的代码 Change | Change 是否正确、安全，并有与风险匹配的证据，可以 Merge | 已有 V2 方案，尚待试点验证 |
| Gate3 | Feature 提测或业务验收前 | 完整 Feature / Candidate | 需求承诺的业务行为是否被完整实现并通过验收 | 原则已明确，详细方案暂缓 |
| Gate4 | Release / 灰度 / 全量前 | Release Candidate / Release | 版本在真实环境风险是否可接受，是否具备监控、降级和回滚能力 | 原则已明确，详细方案暂缓 |

## 2.2 共同基础

四层门禁共同依赖：

```text
Requirement Semantic SSOT
        +
Stable Identity
        +
Traceability Model
        +
Version / Baseline
        +
Evidence Model
        +
Versioned Gate Policy
```

### 判断

**状态：已确认**

- SSOT 保证业务事实不会被产品、开发、测试和 Agent 分别重新定义。
- 可追溯性保证需求、实现、验证、证据和裁决能够建立关系。
- Evidence 证明某项要求是否真实满足。
- Policy 决定什么 Finding/Risk 必须阻断。
- Gate 执行策略并作出生命周期决策。

因此：

> SSOT 和可追溯性是可信、可解释、可自动化门禁的重要基础，但它们本身不等于门禁。

---

# 3. 需求语义单一事实源（Requirement Semantic SSOT）

## 3.1 当前定义

**状态：已确认**

SSOT 不是要求所有内容必须放在同一个物理文档，而是：

> 一个业务事实只能有一个权威定义；其他文档、Task、Test 和 Agent 输出只能通过稳定 ID 引用、派生或验证，不能复制后重新解释。

推荐表达为：

```text
Define Once
Reference Everywhere
```

## 3.2 最小需求对象模型

**状态：已确认**

```text
Feature
  ↓ contains
Story
  ├── has → Acceptance Criteria
  ├── contains → Scenario
  ├── governed by → Rule（按需）
  ├── exercises → State / Transition（按需）
  └── constrained by → Invariant / NFR（按需）
```

| 对象 | 当前职责定义 | 状态 |
|---|---|---|
| Feature | 一个完整业务能力或明确交付目标，可包含多个 Story | 已确认 |
| Story | 一个可独立交付的端到端用户能力，是交付容器而非需求全集 | 已确认 |
| Acceptance Criteria | Story 级验收合同，回答满足什么结果才可接受 | 已确认 |
| Scenario | 特定上下文、事件和结果下的具体行为实例，通常使用 Given / When / Then | 已确认 |
| Rule | 具有跨 Scenario 复用、独立决策或影响分析价值的业务约束 | 已确认 |
| State / Transition | 在存在真实生命周期和状态变化分析价值时，表达状态及合法转换 | 已确认 |
| Invariant | 跨多个 Scenario / State 必须始终成立的约束 | 已确认 |
| Task | 实现活动，只引用 Requirement，不重新定义业务要求 | 已确认 |
| Test | 验证资产，通过 Requirement ID 建立 Oracle，不成为新的需求源 | 已确认 |

## 3.3 SSOT 约束

**状态：已确认**

1. Story、AC、Scenario、Rule、State、Transition、Invariant 的正文只定义一次。
2. 每个可追溯对象具有稳定、唯一、机器可解析的 ID。
3. 下游 Task、Design、Test 通过 ID 引用 Requirement Object。
4. 业务要求变化必须先修改 Canonical Requirement Source。
5. Requirement Source 必须进入版本控制并形成 Baseline。
6. 关系尽量只持久化一个方向，反向索引由工具派生。
7. Rule、State、Transition、Invariant 是按需模型，不为模板完整而强制创建。
8. Test 中的 expected value 可以是测试实现细节，但不得独立改变业务语义。

## 3.4 当前 Canonical Story Schema

**状态：已确认**

当前采用 `feature_story_bundle` 作为 Canonical Requirement Source 的组织结构，使用 `feature-stories.example.yaml` 作为团队填写和 Agent 消费的标准示例。

### 3.4.1 文件组织

- 一个文件描述一个 Feature；
- 一个 Feature 通过 `stories[]` 包含多个 Story；
- Feature 公共的范围、文档引用、依赖和 Unknown 只定义一次；
- Story 只维护自身特有的依赖、Unknown、AC、Scenario，以及按需提取的行为模型；
- 当前契约类型为 `feature_story_bundle`，版本从 `1.0` 开始。

### 3.4.2 最小必需内容

每个 Feature 必须具有稳定唯一的 `id`、`name`、适用范围和权威文档引用。

每个 Story 至少必须包含：

1. 稳定唯一的 Story ID 和名称；
2. `as_a / i_want / so_that` 用户故事；
3. 一个或多个 Story-level Acceptance Criteria；
4. 一个或多个具体 Scenario；
5. Scenario 的 `Given / When / Then`；
6. Scenario 通过 `verifies` 对 AC 建立正向引用；
7. 已分析的 `dependencies` 和 `unknowns`，没有内容时使用空数组表达“已检查但当前没有”。

### 3.4.3 默认语义

- 写入 `acceptance_criteria` 的 AC 默认全部属于本次验收合同；
- 写入 `scenarios` 的 Scenario 默认全部属于本次必需行为范围；
- 不再重复维护 `required: true`；
- 不使用 `required: false` 表示暂不交付内容；暂不交付内容进入 `out_of_scope` 或独立的 Deferred Backlog；
- AC 描述 Story 必须满足的可验证结果，不写具体业务分支；
- Scenario 描述具体条件、事件和可观察结果，不复制 AC 或 Rule 正文；
- Scenario、AC、Rule 等对象的 ID 必须包含 Story 前缀，避免多 Story 文件内发生冲突。

### 3.4.4 分层与按需模型

- Feature 级 `dependencies / unknowns` 表达影响整个 Feature 的事实；
- Story 级 `dependencies / unknowns` 只表达该 Story 特有的事实；
- 同一个依赖或 Unknown 只允许定义一次，不得在 Feature 和 Story 两层复制；
- Rule / State / Transition / Invariant / NFR 只有具备独立语义、复用、验证或影响分析价值时才创建；
- Scenario 通过 `exercises_rules` 引用 Rule；通过 `exercises_transitions` 引用 Transition；反向关系由工具派生。

### 3.4.5 Schema 边界

Canonical Requirement Source 不包含：

- Engineering Task；
- Test Implementation 和 Test Execution；
- Code Change；
- Evidence、Finding、Policy 或 Gate Verdict。

字段语义和确定性校验规则由 Gate1 Skill 或独立机器 Schema 维护，不再通过带有大量注释的空模板向填写者传递。`feature-stories.example.yaml` 只呈现真实业务事实和追溯关系。

---

# 4. 可追溯性模型

## 4.1 定义

**状态：已确认**

可追溯性不是复制更多内容，而是通过稳定 ID 和显式关系，使系统可以回答：

- 这个实现是为了哪个需求？
- 这个测试验证哪个行为或规则？
- 这个 Evidence 对应哪个需求版本、代码版本和执行？
- 一个需求变化会影响哪些设计、代码和测试？
- 一个 Gate Verdict 由哪些 Finding、Evidence 和 Policy 得出？

## 4.2 需求与验证主链

**状态：已确认 · Decision: DR-0001**

```text
Business Objective / Feature Goal
        ↓
Feature
        ↓
Story
        ↓
Requirement Object
(Scenario / AC / Rule / Transition / Invariant)
        ↓ verified-by
Test / Verification Activity
        ↓ execution
Execution
        ↓ produces
Evidence
        ↓
Finding
        ↓
Policy
        ↓
Verdict
```

说明：

- Requirement Object 是“验证什么”的语义事实源。
- Test / Verification Activity 是“如何验证”；Test 只是 Verification Activity 的一种。
- Evidence 是“验证实际得到什么”。
- Gate1 主要建立 Requirement Object、稳定关系和可验证性骨架；关键 Requirement 必须具备明确 Oracle / 可观察结果，但 Gate1 不要求 Test Implementation 或 Test Execution 已经存在。
- Gate2 扩展到 Task、Change、Code、Developer Test 和合入证据。
- Gate3 扩展到 Feature 业务验收 Evidence 和 Feature Verdict。
- Gate4 扩展到 Release、真实环境信号、灰度 Evidence 和 Release Verdict。
- `Verification Obligation` 仅保留为解释性概念，表示“Requirement 为被认为满足而必须得到证明的内容”，V1 不赋予独立 ID、Schema、存储位置和生命周期。详见 `DR-0001`。

## 4.3 Change Safety 链

**状态：已确认**

```text
Change
  ↓
Diff
  ↓
Impact Anchor / Affected Technical Object
  ↓
Affected Existing Scenario / Rule / State / Contract
  ↓
Regression Risk
  ↓
Existing Test
  ↓
Evidence
  ↓
Change Safety Verdict
```

## 4.4 最小追溯原则

**状态：已确认**

- 追溯关系必须机器可解析，不能只存在于自然语言说明中。
- 引用对象必须真实存在，不允许悬空引用。
- Requirement ID 在语义修改后应保持身份稳定；删除的 ID 不复用。
- Evidence 必须绑定 Requirement Revision、Code Commit / Build 和 Test Execution。
- 旧 Evidence 不自动证明修改后的新 Requirement。
- `Story → Scenario → Existing Tests` 是 Gate2 的主要正向导航关系之一。
- `Test → AC / Rule / Scenario / Transition / Invariant` 用于表达精确覆盖，不应反向成为 Requirement Source。

---

# 5. Gate1：Engineering Ready

## 5.1 Gate1 的业务目标

**状态：已确认**

Gate1 的目标不是证明 Spec 没有任何问题，也不是发现所有 Unknown，而是：

> 判断当前范围是否达到 Engineering Ready，阻止工程在关键产品行为、客观验收标准或跨边界契约未闭合时进入实现。

更直接地说：

> 如果 Code Agent 或开发者必须替产品、业务、UX、架构或外部依赖 Owner 发明一个关键决定，Gate1 应阻断。

如果无法确定待评估范围或权威输入，Gate1 应返回 `CANNOT_EVALUATE`，而不是猜测 `PASS/BLOCK`。

## 5.2 Gate1 V1 的三类高置信阻断对象

**状态：已确认**

| 类型 | 定义 | 典型阻断情形 |
|---|---|---|
| Behavior Unknown | 必需的外部可观察行为无法由权威来源唯一确定 | 同一条件下存在多个合理但结果不同的实现选择；关键分支没有定义结果 |
| Oracle Unknown | 关键要求无法转化为基于可观察 Evidence 的客观 PASS/FAIL | “快速、稳定、友好”等要求没有阈值、测量条件或期望结果 |
| Contract Unknown | 跨模块、进程、服务、存储或外部依赖的必要契约未闭合 | 输入输出、错误模型、数据归属、超时重试、幂等或兼容性需由实现者自行决定 |

阻断谓词：

```text
unresolved
AND high_confidence
AND non_local_decision
AND material_effect
AND kind IN {
  BEHAVIOR_UNKNOWN,
  ORACLE_UNKNOWN,
  CONTRACT_UNKNOWN
}
```

只有同时满足以上条件才 `BLOCK`；否则输出 `WARN`。

## 5.3 Gate1 不阻断什么

**状态：已确认**

- 纯粹的写作风格或文档美观问题；
- 已固定外部行为下的可逆、局部实现选择；
- 没有材料影响的推测性边缘场景；
- 不影响当前范围的非关键 Unknown；
- 只能证明“可能有风险”但缺乏具体决策问题和证据的怀疑；
- 产品价值是否值得做——这属于产品决策，不由 Gate1 代替。

## 5.4 “同源、可追溯、行为覆盖、决策闭合”如何进入 Gate1

**状态：待确认——这是当前综合判断，尚需正式确认**

| 项目 | 在 Gate1 中的角色 | 建议判定 |
|---|---|---|
| 同源要求 | 确保权威来源唯一、身份稳定、无需求分叉，是 Gate1 能够可靠分析的确定性前置 | 违反唯一事实源、ID、版本或 canonical owner 约束时可直接 BLOCK |
| 可追溯性要求 | 确保 Feature、Story 与 Requirement Object 关系可遍历，并能够定位后续需要验证的 Requirement | 必需关系断裂、引用悬空或 Requirement 无法定位时可直接 BLOCK |
| 行为覆盖缺口 | 通过 Scenario、State、Rule、边界扰动等探针暴露 Known Unknown，是发现机制，不等于证明完整性 | 高置信且导致 Behavior/Oracle/Contract Unknown 才 BLOCK；其他情况 WARN |
| 关键决策闭合 | Gate1 的最终阻断结果：实现是否仍需发明非局部、会产生材料影响的决定 | 未闭合的高置信关键决策 BLOCK |

候选结构：

```text
Gate1 业务目标
└─ 判断 Engineering Ready
   ├─ 确定性基础：SSOT + 最小可追溯性
   ├─ 语义发现：行为覆盖与决策面探查
   └─ 阻断结果：Behavior / Oracle / Contract Unknown 未闭合
```

## 5.5 Gate1 V1 输入、过程与输出

### 输入

**状态：待确认**

候选最小输入：

- 明确的 Feature / Change Scope；
- 权威 Product Spec；
- 适用的 UX Spec；
- 适用的 Technical Spec / ADR；
- API、Schema、数据、依赖或跨边界 Contract；
- 当前 Requirement Revision / Baseline；
- 可选的历史缺陷模式和领域风险规则。

待确认点：Gate1 是一次性同时准出 Requirement + Design，还是内部拆成有依赖关系的 `Gate1-R` 和 `Gate1-D`。

### 过程

**状态：已确认到原则层，执行细则待确认**

1. 冻结评估范围和权威来源。
2. 执行 SSOT 和稳定身份的确定性检查。
3. 建立 Feature → Story → Requirement Object（Scenario / AC / Rule / Transition / Invariant）的最小追溯骨架，并确认关键 Requirement 可以形成明确 Oracle / 验证目标。
4. 抽取外部行为、状态转换、业务规则、数据语义、依赖边界、AC 和可测 NFR。
5. 对相关决策面执行边界、状态、规则、失败、Oracle 和 Contract 探针。
6. 搜索权威来源，区分有答案、冲突、缺失、模糊和未闭合。
7. 分类为 Behavior / Oracle / Contract Unknown 或非阻断 Warning。
8. 用确定性 Policy 生成 Verdict。

### 输出

**状态：已确认到原则层，Schema 待统一**

- `PASS / WARN / BLOCK / CANNOT_EVALUATE`；
- Structured Findings；
- Finding 对应的 Decision Surface；
- 来源 Evidence 和已搜索的权威来源；
- 缺失的具体决定；
- 建议 Owner；
- 明确的 Unblock Condition；
- Requirement Baseline；
- 机器可读 JSON/YAML；
- 由机器输出派生的人类可读报告。

## 5.6 Gate1 V1 明确不承诺

**状态：已确认**

- 证明需求绝对完整；
- 发现所有 Unknown Unknown；
- 自动替业务 Owner 作决策；
- 以 LLM 置信度或文档总分直接决定放行；
- 要求 Task、Code、Test Execution、Evidence 已经存在；
- 代替完整 Product Review、UX Review 或 Architecture Review；
- 对不影响当前范围的所有 NFR、风险和边缘组合做穷举检查。

## 5.7 Gate1 当前实现状态

**状态：待确认**

现有 `gate1-v1-skill.zip` 已实现一版围绕 Behavior / Oracle / Contract Unknown 的 Skill 原型，包含：

- `SKILL.md`；
- discovery probes；
- blocking rules；
- JSON result schema；
- 示例结果。

当前判断：它可以作为“关键 Unknown 识别与裁决”的实现起点，但还不能直接视为最新 Gate1 总体基线，原因是仍需确认并补齐：

1. SSOT 确定性检查是否直接纳入同一个 Skill；
2. 最小追溯关系校验是否成为前置阶段；
3. 四项候选目标与三类 Unknown 的正式层次关系；
4. Gate1-R / Gate1-D 是否拆分；
5. 与 `feature-stories.example.yaml`、`ssot_checklist.md` 的统一输入契约。

---

# 6. Gate2：Code Change / Merge Ready

## 6.1 Gate2 定位

**状态：已确认**

Gate2 面向一次明确的 Code Change / Patchset / PR，在进入共享主干或集成基线前回答：

1. `Change Correctness`：本次 Change 声称实现的行为是否正确实现？
2. `Change Safety`：本次 Change 是否破坏已有行为？
3. `Implementation Quality`：实现方式是否满足必要工程质量约束？
4. `Evidence Sufficiency`：与 Change 风险匹配的必要 Evidence 是否充分？

Gate2 不是整个 Feature 的提测门禁；完整业务行为验收属于 Gate3。

## 6.2 Gate2 两条证据链

**状态：已确认**

### Change Correctness

```text
Change
  ↓
Story / Scenario / AC / Rule
  ↓
Existing Test
  ↓
Evidence
  ↓
Change Correctness Verdict
```

### Change Safety

```text
Change
  ↓
Diff / Impact
  ↓
Affected Existing Scenario / Risk
  ↓
Regression Test
  ↓
Evidence
  ↓
Change Safety Verdict
```

## 6.3 Gate2 V1/V2 约束

**状态：已确认**

- 只选择和调度已有测试资产。
- 不在线生成、修改、调试、修复或自愈测试脚本。
- Required Verification 没有已有测试时输出 `TEST_ASSET_GAP`，而不是现场生成测试。
- Required Test 没有有效执行证据时输出 `TEST_EVIDENCE_GAP`。
- 测试通过率不是 Gate Verdict；核心是 Required Requirement / Risk 是否具有有效 Evidence。
- LLM 可辅助理解、影响分析、Finding 生成和解释，但最终 Verdict 由确定性 Policy Engine 产生。

## 6.4 本地开发与线上 Gate2 边界

**状态：已确认**

开发本地负责：

- 代码和测试设计、实现、调试；
- 确保 Test 可执行、已调通、ID 稳定；
- 建立 Story → Scenario → Test 关系；
- 将测试资产登记到 Test Asset Registry。

线上 Gate2 负责：

- 解析 Change Scope；
- 分析 Impact / Risk；
- 选择已有测试；
- 检查 Coverage Gap；
- 调度已有测试或解析已有报告；
- 标准化 Evidence；
- 执行 Gate Policy；
- 生成 Verdict、JSON 和 HTML 报告。

因此：

> Gate2 是验证与准出系统，不是测试开发系统。

## 6.5 Gate2 当前待确认项

**状态：待确认**

- 首个 Android 试点 Feature 和代码库；
- Change Scope 解析的 V1 最小算法；
- Impact Anchor / Risk Pattern 的第一版覆盖范围；
- Required Test Coverage 的硬阻断策略；
- Test Failure、Infrastructure Failure 和 Flaky Test 的策略；
- Waiver 的责任人、时效和审计规则；
- MVP 成功指标和历史基线。

---

# 7. Gate3：Feature / Behavior Ready

## 7.1 当前定位

**状态：已确认到原则层**

Gate3 面向完整 Feature 或可验收 Candidate，判断：

> 所有承诺的 Story、Scenario、AC、Rule、Invariant 和适用 NFR 是否获得可信 Evidence，并能形成 Feature Behavior Verdict。

Gate3 与 Gate2 的核心区别：

| Gate2 | Gate3 |
|---|---|
| 评估一次 Change 是否可以 Merge | 评估完整 Feature 是否满足业务承诺 |
| 关注 Change Correctness、Safety、Implementation Quality | 关注端到端业务行为、跨 Story 协同和 Feature 验收 |
| 证据可以集中于变更范围和受影响回归 | 证据必须覆盖完整 Required Acceptance Scope |

## 7.2 暂缓内容

**状态：暂不处理**

- Gate3 完整输入 Schema；
- Feature Candidate Manifest；
- 多 Story 聚合 Verdict；
- 设备矩阵、系统/E2E 和人工探索的 Evidence 融合；
- Feature 级风险接受和豁免规则；
- Gate3 Skill 实现。

---

# 8. Gate4：Release Ready

## 8.1 当前定位

**状态：已确认到原则层**

Gate4 面向 Release Candidate、灰度批次和全量版本，判断：

> 版本在真实设备、真实依赖和真实流量环境下的剩余风险是否可接受，是否具备监控、降级、暂停和回滚能力。

主要关注：

- 真机与兼容性；
- 容量、性能和资源；
- 可靠性和恢复；
- 安全、隐私和合规；
- 线上指标和异常聚类；
- 灰度放量策略；
- 降级与回滚可用性。

## 8.2 暂缓内容

**状态：暂不处理**

- Gate4 完整 Schema；
- 灰度分批阈值；
- 真实流量和监控指标接入；
- 自动暂停、降级和回滚策略；
- Release Verdict 与 Feature Verdict 的聚合逻辑；
- Gate4 Skill 实现。

---

# 9. Testing 基线与门禁的关系

## 9.1 当前 Testing 定义

**状态：已确认**

Testing 不是“生成脚本并跑绿”，而是：

> 围绕产品质量要求和风险建立可追溯 Oracle，通过经过验证的测试或实验产生可信 Evidence，并形成可审计的 Behavior / Product Verdict。

因此：

- `Test Correctness` 不等于 `Test PASS`；
- 测试脚本本身必须先证明可信；
- 产品缺陷、脚本缺陷、环境缺陷必须区分；
- Test 是产生 Evidence 的机制之一，不是 Gate Verdict 本身；
- Gate 消费测试 Evidence，但必须依据需求覆盖、风险和策略作出裁决。

## 9.2 当前 Testing Skill 状态

**状态：暂不处理于当前 Gate1 主线**

Testing Q1–Q50 已作为后续 Testing Skill 的正式基线，但当前不与 Gate1 V1 同时实现，避免再次扩大范围。

---

# 10. 已确认结论登记

以下结论除非出现新证据或新的 Decision Record，否则不再重新讨论。

| ID | 已确认结论 |
|---|---|
| C-001 | 质量门禁是在生命周期流转点基于 Evidence 和 Policy 作出准入/准出决策，不是检查项集合 |
| C-002 | 当前采用 Gate1 Requirement/Engineering Ready、Gate2 Code Change/Merge Ready、Gate3 Feature Ready、Gate4 Release Ready 四层主线 |
| C-003 | SSOT 表示一个业务事实只定义一次，不表示所有内容必须存放在一个物理文档 |
| C-004 | 可追溯性是门禁基础之一，但不等于门禁 |
| C-005 | Story 是端到端交付容器，Scenario 是具体行为实例，AC 是 Story 级验收合同，Rule 是按需提取的独立约束 |
| C-006 | Rule、State、Transition、Invariant 均按需建模，不为模板完整而强制创建 |
| C-007 | 当前 Canonical Requirement Source 采用一个 Feature 包含多个 Story 的 `feature_story_bundle`；保留 Story 级 AC，标准示例为 `feature-stories.example.yaml` |
| C-008 | 需求、关系和证据必须具有 Stable ID、Revision/Baseline 和机器可解析引用 |
| C-009 | Gate1 的目标是 Engineering Ready，不承诺证明 Spec 绝对完整或发现所有 Unknown Unknown |
| C-010 | Gate1 V1 首先阻断 Behavior、Oracle、Contract 三类高置信且未闭合的关键 Unknown |
| C-011 | Gate1 不替产品决定业务价值，不替 Owner 发明产品行为或跨边界契约 |
| C-012 | Gate2 评估一次 Change 是否可以进入共享基线，不是完整 Feature 提测门禁 |
| C-013 | Gate2 必须区分 Change Correctness、Change Safety 和 Implementation Quality |
| C-014 | Gate2 V1/V2 只使用已有测试；无测试时报告 TEST_ASSET_GAP，不在线生成测试 |
| C-015 | 测试通过率不能直接等价于 Gate PASS；必须检查 Required Requirement / Risk 和 Evidence Sufficiency |
| C-016 | LLM 可生成 Finding 和辅助分析，但最终 Verdict 应由版本化的确定性 Policy Engine 产生 |
| C-017 | Gate3 负责完整 Feature 业务行为验收，Gate4 负责版本、灰度和真实环境风险 |
| C-018 | Testing 的最终目标是产生可信 Evidence 和 Behavior/Product Verdict，而不只是让测试跑绿 |
| C-019 | Verification Obligation 在 V1 不作为独立 Traceability Object；Requirement Object 直接由 Test / Verification Activity 验证。Decision: DR-0001 |

历史 C-001～C-018 的 DR 补录优先级见 `docs/decisions/decision-backlog.md`。

---

# 11. 待确认问题登记

## 11.1 P0：阻断 Gate1 V1 定稿

| ID | 具体决策问题 | 推荐默认值 | 影响 |
|---|---|---|---|
| Q-001 | 同源、可追溯、行为覆盖、决策闭合与三类 Unknown 的层次关系是否采用本文 5.4 的结构 | 采用：前两项是确定性基础，行为覆盖是发现机制，关键决策闭合是阻断结果 | 决定 Gate1 Skill 总体架构 |
| Q-002 | Gate1 是否拆成内部有依赖关系的 Gate1-R 和 Gate1-D | 推荐拆成两个检查点、一个对外 Gate1 Verdict | 决定输入、Owner 和执行时机 |
| Q-003 | Gate1 V1 的最小 Canonical Input 是否固定为 Feature Scope + Requirement Source + 适用 UX/Technical/Contract | 采用；缺少强制输入时 CANNOT_EVALUATE | 决定 Skill 输入契约 |
| Q-004 | Gate1 V1 强制的 SSOT / Traceability 规则具体是哪一组 | 从 `ssot_checklist.md` 选择 Gate1 阶段适用子集，暂不要求 Task/Test 已存在 | 决定确定性硬检查 |
| Q-005 | 最小追溯链是否固定为 Feature → Story → Requirement Object（Scenario / AC / Rule / Transition / Invariant），且 Gate1 只要求关键 Requirement 可验证、不要求 Test 已存在 | 推荐采用；Task/Code/Test/Evidence 不进入 Gate1 强制存在链 | 决定 Schema 和断链规则 |
| Q-006 | Behavior Coverage 的最低完成条件是什么 | 不宣称完整；要求所有显式关键 Decision Surface 已抽取并执行适用探针 | 决定覆盖缺口的可解释性 |
| Q-007 | 现有 `gate1-v1-skill.zip` 是升级为新版本还是作为语义分析子 Skill | 推荐作为 `semantic-readiness-analyzer` 子能力，由 Gate1 Orchestrator 组合 SSOT/Trace 检查 | 决定代码结构和交付形式 |

## 11.2 P1：不阻断目标定稿，但阻断真实试点

| ID | 具体决策问题 | 推荐默认值 |
|---|---|---|
| Q-008 | Product、UX、Architecture、Dependency Contract Finding 的 Owner 如何分配 | 按 Decision Domain 分配，不由单一 Gate Owner 代决策 |
| Q-009 | WARN、BLOCK、WAIVER 的审批和时效如何定义 | BLOCK 只能由对应 Decision Owner 解除或正式 Waiver；Waiver 必须过期 |
| Q-010 | 首个 Android 试点对象是什么 | 选择边界清晰、已有 Spec/Test、历史缺陷可回放的单 Feature |
| Q-011 | Gate1 的成功指标是什么 | 误阻断率、关键问题前移发现率、平均闭环时间、后续逃逸率、重复讨论率 |
| Q-012 | Gate2 的成功指标是什么 | 必需测试召回率、影响覆盖缺口率、阻断有效率、误阻断率、缺陷逃逸率 |

---

# 12. 已被替代的观点和资产

| ID | 已被替代内容 | 当前替代结论 |
|---|---|---|
| S-001 | Gate1 第一版要检查并证明需求在所有维度都完整 | Gate1 V1 只阻断高置信、未闭合、需要工程发明关键决定的问题；不能证明绝对完整 |
| S-002 | Gate1 通过一个综合文档质量分数决定放行 | Gate Verdict 基于结构化 Finding、Evidence 和版本化 Policy，不使用模糊总分 |
| S-003 | LLM 直接自由决定 PASS/BLOCK | LLM 辅助发现与解释；最终 Verdict 由确定性 Policy Engine 产生 |
| S-004 | 可追溯性本身就是门禁 | 可追溯性是基础；门禁还需要对象、Evidence、Policy 和执行机制 |
| S-005 | SSOT 等于所有人阅读同一份 PRD | SSOT 是一个事实一个权威定义，允许不同受控投影和下游引用 |
| S-006 | 所有 Story 必须拥有 Rule、State、Transition 和 Invariant | 这些对象按需创建，只有具备独立语义和分析价值时才建模 |
| S-007 | Story 不需要 AC，所有 Scenario 通过即代表 Story 验收 | 当前 `feature_story_bundle` 保留 Story 级 AC，并明确 AC 与 Scenario 的不同职责 |
| S-008 | 同时持久化 Scenario → Rule 和 Rule → Scenario 等双向关系 | 只持久化一个规范方向，反向索引由工具派生 |
| S-009 | Gate2 可以在门禁运行时在线生成、修改或修复测试 | Gate2 V1/V2 只消费预先准备并调通的测试；缺失即报告资产缺口 |
| S-010 | 大量测试通过即可证明 Gate2 PASS | 必须证明 Required Scenario / AC / Risk 拥有充分有效 Evidence |
| S-011 | Gate2 与 Feature 提测门禁可以合并 | Gate2 保护 Change Merge；Gate3 保护 Feature 业务验收，二者分离 |
| S-012 | 早期五层 Gate 模型直接作为当前实现基线 | 当前主线采用四层 Gate1–Gate4；旧五层材料仅作为历史参考 |
| S-013 | Verification Obligation 作为 Gate1 V1 独立一等追溯节点 | V1 将其降级为解释性概念；Requirement Object 直接 `verified-by` Test / Verification Activity。Decision: DR-0001 |

## 12.1 旧版资产状态

| 资产 | 当前状态 | 处理建议 |
|---|---|---|
| `story-v2.yaml` | 已被替代 | 不再使用 |
| `story-v3.yaml` | 已被替代 | 其“删除 AC”的方案不再采用，当前模型保留 Story 级 AC |
| `story-v3.1.yaml` | 已被替代 | 单 Story、注释型模板不再作为当前输入结构 |
| `story-v3.2.yaml` | 已被替代 | 其中 AC、Scenario 和 Rule 的语义继续有效；物理结构由 `feature_story_bundle` 取代 |
| `gates.md` / `gates(1).md` 中的五层模型 | 已被替代或仅供历史参考 | 不作为当前门禁数量和边界的事实源 |
| `story开发交付模板.md` | 部分有效 | 概念仍可参考，输入结构与关系方向以 `feature-stories.example.yaml` 为准 |
| `gate1-v1-skill.zip` | 原型/待升级 | 保留三类 Unknown 分析能力，与 SSOT/Traceability 检查重新组合 |

---

# 13. 暂不处理事项

| ID | 暂不处理内容 | 原因 | 重新进入条件 |
|---|---|---|---|
| D-001 | 证明或自动发现所有 Unknown Unknown | 技术上无法保证，会使 Gate1 无限扩张 | 有明确高价值风险模式和可验证探针时逐步加入 |
| D-002 | 完整 Requirement Knowledge Graph | 当前只需最小可追溯链，完整图谱成本高 | Gate1/Gate2 最小链稳定并证明收益后 |
| D-003 | Gate3 完整 Skill 和 Schema | 当前主线尚未完成 Gate1 | Gate1 V1 试点完成后 |
| D-004 | Gate4 完整 Skill、灰度和回滚自动化 | 依赖运行平台、监控和组织策略 | Gate3 与 Release 平台接口明确后 |
| D-005 | Gate2 在线测试生成、调试、修复和 Self-healing | 会混淆测试开发和准出，降低 Evidence 可信度 | 不进入当前 Gate2 路线；如未来研究需独立系统 |
| D-006 | 第一版覆盖全部 NFR、全部风险和全部组合场景 | 会导致不可落地和高误报 | 按历史缺陷、关键业务和高风险模式逐步扩展 |
| D-007 | 同时实现 Gate1、Gate2、Gate3、Gate4 | 造成范围失控，无法验证单层收益 | 每一层有真实试点和效果数据后再进入下一层 |
| D-008 | 将 Testing Skill 并入 Gate1 V1 | Testing 已有独立基线，但不属于当前 Gate1 实现最小闭环 | Gate1 对 Requirement 可验证性和后续 Verification Activity 接口稳定后衔接 |

---

# 14. 当前有效交付件索引

| 交付件 | 作用 | 当前状态 |
|---|---|---|
| `quality-gate-knowledge-overview-v0.1.md` | 整个质量门禁体系的当前入口和状态基线 | 当前有效 |
| `docs/decisions/README.md` | Decision Record 索引、治理规则、Issue/PR/Commit 关联规范 | 当前有效 |
| `docs/decisions/DR-TEMPLATE.md` | 新决策记录统一模板 | 当前有效 |
| `docs/decisions/DR-0001-verification-obligation-not-first-class.md` | Verification Obligation V1 建模决策 | Accepted |
| `docs/decisions/decision-backlog.md` | C-001～C-018 历史决策补录优先级 | 当前有效 |
| `.github/workflows/decision-record-check.yml` | 核心知识 Artifact 变化时检查是否同步 DR | 当前有效；需将该 Check 配为 required 才能硬阻止 Merge |
| `feature-stories.example.yaml` | 一个 Feature 包含多个 Story 的 Canonical Requirement Source 标准示例 | 当前有效 |
| `story-v3.2.yaml` | 旧版单 Story 注释型模板 | 已被替代，保留为历史参考 |
| `ssot_checklist.md` | SSOT、Stable ID、Reference、Baseline 和 Gate 分层检查清单 | 当前有效，Gate1 子集待裁剪 |
| `story-test-map.yaml` | Story → Scenario → Existing Tests 正向追溯示例 | 当前有效，Gate2 使用 |
| `gate2_V2.md` | Gate2 定位、流程、Finding/Evidence/Policy、MVP 和报告方案 | 当前有效方案，待试点 |
| `gate1-v1-skill.zip` | Behavior/Oracle/Contract Unknown 发现与阻断原型 | 部分有效，待与新目标统一 |
| `gate1-industry-tools-research-zh.md` | Gate1 业界工具与 Gate1-R/Gate1-D 拆分研究 | 研究输入，不等于已确认设计 |
| `业务行为模型模板_v1.0.md` | PRD 到 Design/Test 的业务行为建模参考 | 概念参考，当前输入结构以 `feature-stories.example.yaml` 为准 |
| `story开发交付模板.md` | Engineering Ready Story 的人类可读模板和完整示例 | 部分有效，待与 Canonical Schema 对齐 |
| `AI_Native_软件质量门禁建设进展_单页汇报.html` | 整体门禁建设的汇报视图 | 汇报参考，不作为细节事实源 |

---

# 15. 当前冲突与解释

## 15.1 Gate1 三类 Unknown 与四项候选目标是否冲突

**当前判断：不必冲突，但尚需正式确认。**

- 三类 Unknown 回答“最终阻断什么”。
- 同源和可追溯回答“Gate1 是否拥有可靠、可定位的分析基础”。
- 行为覆盖回答“如何主动暴露隐藏假设和 Known Unknown”。
- 关键决策闭合回答“什么时候可以进入实现”。

如果把四项都定义为同层业务目标，就会出现重复和边界混乱；如果按本文 5.4 分层，则可以统一。

## 15.2 Gate1 是 Requirement Ready 还是同时包括 Design Ready

**当前状态：待确认。**

已有讨论中同时存在两种表达：

1. Gate1 是 Product、UX、Technical Spec 的统一 Engineering Ready Gate。
2. Gate1 内部拆成 `Gate1-R: Requirement Ready` 与 `Gate1-D: Design Ready`。

当前推荐第二种，但保留一个对外 Gate1：

```text
Gate1-R PASS
    ↓
Gate1-D PASS
    ↓
Gate1 Overall PASS
```

这样既不增加外部四层门禁数量，也避免在需求尚未基线时评审技术方案。

## 15.3 Gate1 是否要求已有 Test

**状态：已确认 · Decision: DR-0001。**

Gate1 不要求 Test Implementation 或 Test Execution 已经存在，但必须具有明确、可验证的 Requirement：关键行为能够形成客观 Oracle、可观察结果或 Verification Strategy，使开发和后续测试无需重新发明业务语义。

---

# 16. 下一阶段唯一工作目标

当前不再扩展新的门禁理论。下一阶段只完成：

> 将 Gate1 V1 收敛成一个统一、可实现、可试点的契约。

完成 Gate1 V1 定稿需要依次闭合：

1. 确认本文 5.4 的层次结构。
2. 确认 Gate1-R / Gate1-D 是否作为内部两阶段。
3. 固定 Gate1 最小输入和 Canonical Schema。
4. 从 `ssot_checklist.md` 裁剪 Gate1 确定性规则。
5. 固定最小追溯链和断链规则。
6. 将现有三类 Unknown Skill 作为语义分析子能力接入。
7. 固定 Finding、Evidence、Policy、Verdict 输出 Schema。
8. 用一个 Android Feature 进行历史回放试点。

## 16.1 Gate1 V1 的建议完成定义

**状态：待确认**

- 一个真实 Feature 能提供完整输入；
- SSOT/Traceability 确定性检查可重复执行；
- Behavior/Oracle/Contract Unknown 能输出带证据的 Finding；
- 相同输入和 Policy 得到相同 Verdict；
- 每个 BLOCK 都有 Owner 和明确 Unblock Condition；
- 人工能够审计并纠正 Finding；
- 历史问题回放能证明至少拦截一类真实缺陷根因；
- 输出既有机器可读结果，也有派生的人类可读报告。

---

# 17. 下次讨论恢复卡片

```text
当前总目标：建设 AI Native 软件质量门禁体系
当前阶段：只收敛 Gate1 V1
Gate1 业务目标：判断 Engineering Ready
已确认阻断：高置信、未闭合的 Behavior / Oracle / Contract Unknown
已确认基础：Requirement Semantic SSOT + 最小可追溯性
验证主链：Requirement Object → Test / Verification Activity → Evidence → Verdict
DR 机制：Overview 管当前结论；docs/decisions 管为什么这样决定
当前关键待确认：四项候选目标与三类 Unknown 的层次关系
推荐结构：SSOT/Trace 是基础，行为覆盖是发现机制，关键决策闭合是结果
下一决策：确认该结构，并决定是否内部拆分 Gate1-R / Gate1-D
暂不讨论：Gate3、Gate4、完整知识图谱、在线测试生成
```

---

# 18. 证据来源

本版主要根据以下既有交付件、已确认讨论和 Decision Record 整理：

- `docs/decisions/DR-0001-verification-obligation-not-first-class.md`
- `feature-stories.example.yaml`
- `story-v3.2.yaml`（历史输入，用于说明模型演进）
- `ssot_checklist.md`
- `story-test-map.yaml`
- `gate2_V2.md`
- `gate1-v1-skill.zip`
- `gate1-industry-tools-research-zh.md`
- `story开发交付模板.md`
- `业务行为模型模板_v1.0.md`
- `gates.md` / `gates(1).md`
- `AI_Native_软件质量门禁建设进展_单页汇报.html`

旧资产只用于识别演进过程和冲突，不自动继承为当前结论。
