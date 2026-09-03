# Spec 质量门禁规范

> 版本：1.0  
> 适用阶段：需求与技术方案完成后、进入实现前  
> 目标：发现并阻断会实质影响范围、正确性、数据完整性、架构、安全、恢复或验收的问题。

## 1. 目标与边界

本门禁面向 PRD、Feature Spec、技术方案、接口契约、状态模型和验收标准，输出独立评审结论，不直接修改源文档或代码。

门禁必须发现并处理以下问题：

- **缺失**：必要场景、状态、规则、数据语义、依赖、失败恢复或验收标准没有定义；
- **模糊**：术语、边界、成功条件、失败条件、职责或接口行为无法唯一理解；
- **不一致**：同一文档前后矛盾，需求与设计、接口、状态模型或验收标准冲突；
- **不正确**：声明与代码、配置、契约、平台保证或可复现实验不符；
- **不可验证**：没有可观察结果、Oracle、适用条件或可执行验收方式；
- **未决策**：关键产品语义或技术取舍尚无责任人结论；
- **证据不足**：关键结论依赖未经证实的假设。

本门禁不负责：

- 替产品或架构 Owner 做高影响决策；
- 自动修改 PRD、设计或实现；
- 将探索问题直接当成缺陷；
- 穷举理论上的全部场景组合；
- 因为没有历史风险模式而判定不存在风险。

## 2. 核心原则

### P1：事实、决策、未知必须分离

- `FACT`：存在唯一可查证答案，Agent 必须优先从证据中查找；
- `DECISION`：存在多个合理选项，必须由有权限的 Owner 决定；
- `UNKNOWN`：当前信息或权限不足，必须记录证据需求、Owner 和关闭条件。

### P2：开放探索先于知识增强

风险模式库不能作为 Discovery 的白名单、召回边界或候选过滤条件。必须先在不读取风险模式库的情况下完成开放扫描并冻结 `Baseline Exploration Map`，再进行知识增强。

### P3：知识只做加法

启用风险模式库后，候选集合必须满足单调覆盖：

```text
CandidatesFinal
= CandidatesOpen
∪ CandidatesPattern
∪ CandidatesNovel
```

禁止使用风险模式匹配结果删除开放探索候选。`NO_PATTERN_MATCH` 表示新型候选，不表示低风险或无风险。

### P4：反例只生成一次并持续复用

D3 为高风险候选生成最小反场景。后续关键答案闭环检查必须优先复用已有反例，不得从头重复执行场景探索。只有答案引入新角色、状态、边界、副作用或假设时，才允许生成增量反例。

### P5：Socratic Challenge 是关闭门，不是第二次 Discovery

关键答案闭环检查只在中高风险节点准备关闭，或答案包含重要声明时触发。它验证答案是否：

1. 真正回答当前问题；
2. 能够关闭已有反例；
3. 有充分且适用的证据；
4. 引入了新的未证实假设。

### P6：候选问题不等于 Finding

只有在范围适用且证据、推理、反例和影响能够证明真实缺口时，才能形成 Finding。

## 3. 输入与输出

### 3.1 输入

- PRD、Feature Spec、用户故事与 AC；
- 技术方案、架构图、状态机、数据模型；
- API、协议和外部依赖契约；
- 当前代码、配置、测试和可复现结果；
- 平台或框架保证；
- 已审核风险模式库；
- 评审目标、范围、阶段和决策 Owner。

### 3.2 输出

门禁必须输出：

1. `Verdict`：`PASS | CONDITIONAL_PASS | BLOCK`；
2. `Resolved Decisions`；
3. `Confirmed Facts`；
4. `Open Decisions`；
5. `Findings`；
6. `Residual Unknowns`；
7. `Coverage Summary`；
8. 从 Finding 到候选分支、反例、锚点和源证据的追溯关系。

## 4. 总体流程

### 阶段 A：开放探索与建模

#### 01 建立挑战上下文

明确：

- 评审目标和生命周期阶段；
- 当前 Feature 的范围与排除项；
- 可使用的证据源；
- 产品、架构和技术决策 Owner；
- 不可逆、高安全性或高一致性风险操作；
- 本次门禁所依据的成功条件和核心不变量。

#### D1 建立 Feature 因果模型

D1 只提取或规范化源材料中存在的内容，不生成原文没有的新场景。

输出锚点包括：

- 目标、Actor、利益相关方；
- 核心对象、对象身份与所有权；
- 操作、状态变化和副作用；
- 入口、出口、成功和失败结果；
- 进程、持久化、设备、账号、网络和信任边界；
- 外部依赖；
- 不变量和不可逆操作；
- 来源证据。

硬约束：

```text
D1 只建模，不扩展问题空间，不生成候选 Finding。
```

#### D2 无知识库开放扫描

D2 在隔离风险模式库内容的情况下，基于 D1 因果模型扫描：

| 空间 | 扫描内容 |
| --- | --- |
| 场景 | 正常、替代、失败、恢复、中断、重复、跨入口、跨设备/账号/版本 |
| 状态 | 初始、中间、失败、重试、终态、非法和不可达转换 |
| 规则 | 条件、默认、优先级、冲突、超时、重试、幂等和终止 |
| 数据 | 身份、所有权、事实源、生命周期、一致性、删除、迁移、陈旧数据 |
| 依赖 | OS、框架、服务端、账号、权限、网络、数据库、SDK、配置 |
| 失败 | 部分失败、进程死亡、重启、重复、乱序、依赖降级、资源压力 |
| 环境 | 版本、设备形态、区域、网络、前后台、省电、登录和安装状态 |
| 质量 | 安全、隐私、性能、可恢复性、兼容性、可观测性、可验证性 |

D2 输出 `Baseline Exploration Map`，其中每个候选带有：

- `source_anchor`；
- `space`；
- `coverage: EXPLICIT | IMPLICIT | MISSING | CONTRADICTED`；
- `origin: FIRST_PRINCIPLES | SPACE_SCAN | CAUSAL_MUTATION`；
- `why_relevant`；
- `evidence_to_seek`。

#### K 已审核风险模式增强

D1 的锚点同时用于独立召回历史风险模式。知识增强与 D2 开放扫描并行，不允许在 D2 冻结前向其注入风险模式内容。

风险模式输出至少包含：

- 模式 ID 和名称；
- 适用条件；
- 触发机制；
- 典型失败链；
- 用户或系统后果；
- 历史来源和可信度；
- 与当前锚点的匹配理由。

风险模式是探索假设，不是事实、缺陷或过滤条件。

#### D3 合并候选并生成最小反例

D3 接收已经冻结的开放候选和独立召回的风险模式，执行：

1. 合并语义等价候选并保留全部来源；
2. 用历史模式补充开放扫描遗漏的已知风险；
3. 生成无法映射到现有模式的 `NOVEL` 候选；
4. 对高风险候选生成最小、现实、可验证的失败事件序列；
5. 标明被破坏的不变量和用户可观察后果。

硬约束：

- 风险模式只能增加或丰富候选；
- 不得因未匹配风险模式删除候选；
- D3 不重新扫描完整八空间；
- 每个反例必须引用 `branch_id`；
- 同一反例必须获得稳定 `counterexample_id`，供后续复用。

#### D4 相关性与风险筛选

只依据以下因素裁剪或排序：

- 是否改变用户可见行为；
- 是否跨越持久化、进程、设备、账号、所有权或信任边界；
- 是否可能造成丢失、损坏、泄露或长期不一致；
- 是否依赖隐藏保证；
- 正常路径与恢复路径是否产生不同结果；
- 是否影响可验证性和准出。

禁止依据“是否命中风险模式库”降低优先级。没有模式匹配的高影响候选应标记为 `NOVEL_RISK_CANDIDATE`。

#### D5 完整性分类

- `REQUIRED`：缺失可能导致错误、不安全、不一致、不可恢复或不可验证；
- `CONDITIONAL`：仅当指定能力、环境或依赖在范围内时必须定义；
- `OPTIONAL`：不违反当前承诺的扩展或优化；
- `NOT_APPLICABLE`：有证据或明确范围决策证明不适用。

不得因源文档未提及就判为 `OPTIONAL`。

#### D6 生成 Exploration Map

最终地图必须保留：

- 锚点与证据来源；
- 开放扫描、风险模式和新型候选的来源标记；
- 空间、覆盖状态和完整性分类；
- 最小反例及被破坏不变量；
- 风险与所需证据；
- 候选类型：`FACT | DECISION | UNKNOWN | FINDING_CANDIDATE`。

#### 03 建立统一候选账本与决策依赖树

将候选转换为统一节点，连接前置依赖。常见依赖顺序为：

```text
范围与语义
→ 身份与所有权
→ 生命周期与状态
→ 冲突与失败策略
→ 架构和机制
→ 验证与发布
```

### 阶段 B：动态求解与关键答案闭环

#### 04 优先自主查证 FACT

Agent 必须从代码、配置、接口、契约、测试或可复现观察中查证事实，同时寻找支持证据和冲突证据，并记录范围、时效性和置信度。

#### 05 选择最高价值前沿节点

前沿节点不得存在未解决前置依赖。优先处理：

- 能解锁更多下游节点；
- 后果严重或不可逆；
- 跨多个模块或角色；
- 不确定性高；
- 会改变范围、数据模型或架构的节点。

#### 06 按类型获取证据或决策

- `FACT`：Agent 自主查证；
- `DECISION`：一次只向 Owner 提出一个决策问题，并给出互斥选项和取舍；
- `UNKNOWN`：记录缺失证据、Owner、阻塞性和关闭条件。

#### 07 关键答案闭环检查

步骤 07 不是必经的第二次 Discovery。仅在以下任一条件成立时触发：

- 节点风险为 `MEDIUM | HIGH | CRITICAL`，且准备标记为 `RESOLVED`；
- 答案包含会影响范围、状态、数据、架构、安全或恢复的重要声明；
- 答案依赖“平台会处理”“应该可以”等隐藏保证；
- 答案声称已经解决 D3 的反例；
- 证据与结论之间可能存在推理跳跃。

闭环检查只执行：

1. `Answer Fit`：是否真正回答当前问题；
2. `Counterexample Closure`：是否关闭已有 D3 反例；
3. `Evidence Sufficiency`：证据是否直接、适用且覆盖声明范围；
4. `New Assumption Detection`：是否引入新假设、Actor、状态、边界或副作用。

如果没有新增高风险声明，只检查相对上次答案的变化，即 `Challenge Delta`，不得重复运行完整八项挑战。

挑战结果：

| 结果 | 节点处理 |
| --- | --- |
| `SUPPORTED` | 允许关闭 |
| `QUALIFIED` | 写入适用条件；必要时拆分新节点 |
| `REFUTED` | 保持打开并形成 Finding 候选 |
| `UNSUPPORTED` | 转为 Evidence Gap 或保持打开 |
| `DECISION_NEEDED` | 返回 Owner 决策 |
| `NEW_BRANCH` | 局部返回 D2/D3，不做全量重扫 |

低风险 FACT 存在直接证据、问题已被直接矛盾证明、或 UNKNOWN 尚无答案时，不执行完整 Challenge。

#### 08 更新决策树与探索空间

每次重要答案后必须：

- 提取事实、决策、假设和声明；
- 更新节点状态和证据；
- 解决、拆分、合并、失效或重分类节点；
- 检查与旧决策和源文档的矛盾；
- 仅对新暴露的空间执行增量 Discovery；
- 重新计算前沿节点。

#### 09 判断是否继续

- 存在可处理的阻塞前沿：返回步骤 05；
- 当前参与者无法解决阻塞前沿：停止询问并报告；
- 不存在阻塞前沿：进入 Finding 固化与 Gate 判定。

### 阶段 C：Finding 固化与准出

#### 10 生成正式 Finding

Finding 必须至少包含：

```yaml
id: F-001
severity: BLOCKER | HIGH | MEDIUM | LOW
type: MISSING | AMBIGUOUS | INCONSISTENT | INCORRECT | UNSUPPORTED_ASSUMPTION | EVIDENCE_GAP | UNDEFINED_BEHAVIOR | UNRESOLVED_DECISION | NON_VERIFIABLE
object: 受影响的需求、场景、状态、规则、接口或组件
attribute: 完整性、清晰性、一致性、正确性、健壮性、可验证性或可追溯性
problem: 具体问题
evidence: []
reasoning: 证据为何能够证明问题
counterexample_id: CE-001
impact: 用户或系统后果
required_resolution: 所需定义、决策或证据
owner: 责任角色
status: OPEN | RESOLVED | ACCEPTED_RISK
trace:
  anchor_id: A-001
  branch_id: B-001
  source_ids: []
```

#### 11 Gate 准出判定

##### PASS

- 无阻塞决策；
- 无未证实关键假设；
- REQUIRED 分支已定义或有充分证据证明不适用；
- 高风险反例已经被有效关闭；
- 验收标准具备明确 Oracle 和可观察结果。

##### CONDITIONAL_PASS

- 仅存在有边界的非阻塞 UNKNOWN；
- 每个 UNKNOWN 有 Owner、关闭条件和完成时限；
- 不影响核心语义、架构、安全、数据完整性或恢复机制。

##### BLOCK

存在以下任一情况：

- 未解决事项会改变范围、核心语义、架构或数据模型；
- 高风险反例无法被当前设计关闭；
- 关键声明被 `REFUTED` 或仍为 `UNSUPPORTED`；
- 需求与设计、接口或验收标准存在关键矛盾；
- REQUIRED 场景、状态、规则、失败恢复或验收标准缺失；
- 不可逆、安全、隐私或多设备一致性风险无明确策略。

## 5. 核心数据契约

### 5.1 Feature Anchor

```yaml
id: A-001
type: ACTOR | OBJECT | OPERATION | STATE | SIDE_EFFECT | BOUNDARY | DEPENDENCY | INVARIANT
value: "本地删除跨越数据库与云端边界"
source: "technical-design.md#delete-flow"
explicit: true
```

### 5.2 Exploration Branch

```yaml
id: B-001
question: "删除意图在进程死亡后是否仍可恢复？"
space: FAILURE
source_anchor_ids: [A-001]
origin:
  - FIRST_PRINCIPLES
coverage: MISSING
completeness: REQUIRED
risk: HIGH
evidence_to_seek:
  - "本地事务与任务持久化设计"
pattern_ids: []
```

### 5.3 Risk Pattern Match

```yaml
pattern_id: RP-DELETE-001
name: "已删除对象复活"
match_anchor_ids: [A-001]
applicability: CANDIDATE
match_reason:
  - "异步删除"
  - "跨设备同步"
provenance: "已审核历史缺陷"
```

### 5.4 Counterexample

```yaml
id: CE-001
branch_id: B-001
preconditions: []
events: []
failed_assumption: ""
violated_invariant_id: A-INV-001
observable_effect: ""
recoverable: UNKNOWN
```

### 5.5 Decision Tree Node

```yaml
id: N-001
question: "必须解决的问题"
type: FACT | DECISION | UNKNOWN
domain: SCENARIO | STATE | RULE | DATA | DEPENDENCY | FAILURE | ENVIRONMENT | OTHER
depends_on: []
risk: LOW | MEDIUM | HIGH | CRITICAL
status: OPEN | RESOLVED | ACCEPTED_RISK | NOT_APPLICABLE
answer: null
evidence: []
assumptions: []
counterexample_ids: []
new_branches: []
owner: null
closure_condition: null
```

## 6. 去重与性能规则

- D1 不生成场景，D2 不复制原文事实，D3 不重新扫描八空间；
- 语义等价候选合并，但必须保留所有来源和证据；
- 一个高风险候选默认只生成一个最小反例，除非不同边界导致不同后果；
- Challenge 优先复用 `counterexample_id`；
- 低风险且有直接证据的 FACT 可直接关闭；
- 新答案只触发受影响子树的增量 Discovery；
- 对无法映射历史模式的候选保留 `NOVEL` 标记；
- 不能用候选数量、问题数量或风险模式命中率代替质量判断。

## 7. 完成条件

门禁可以结束，但不得声称绝对穷尽。至少满足：

- 每个重要 Actor、对象、副作用、边界和依赖都被用于开放扫描；
- 高风险流程具备失败和恢复分支；
- 核心对象的生命周期和状态转换已覆盖；
- 跨边界数据的身份、所有权、一致性和删除语义已检查；
- 风险模式增强没有删除 Baseline 候选；
- 已执行一次“无现有模式可解释的新型风险”搜索；
- 所有阻塞性节点已解决或明确记录为阻塞；
- 所有高风险节点关闭前完成答案闭环检查；
- 所有正式 Finding 均有证据、推理、影响和追溯链；
- 剩余盲区和推迟范围已显式记录。

## 8. 验收标准

### AC-01 开放探索隔离

给定同一份输入，禁用风险模式库时仍能独立生成 `Baseline Exploration Map`。

### AC-02 知识单调性

启用风险模式库后，不得删除禁用知识库时产生的非重复候选；知识增强后的集合必须是 Baseline 的超集或语义等价集。

### AC-03 新型风险保留

任何没有风险模式匹配、但具有高影响或跨关键边界的候选，必须标记为 `NOVEL_RISK_CANDIDATE`，不得仅因无历史模式而被剪枝。

### AC-04 职责不重叠

- D1 输出锚点，不输出反场景；
- D2 输出候选分支，不输出 Finding；
- D3 的每个反例必须引用 D2 `branch_id`；
- Challenge 必须引用已有 `counterexample_id`，除非记录了新假设。

### AC-05 条件挑战

低风险、直接证据充分的 FACT 可以不执行完整挑战；中高风险节点在关闭前必须获得 `SUPPORTED` 或有边界的 `QUALIFIED` 结果。

### AC-06 防止虚假关闭

如果答案不能关闭已有反例、缺少适用证据或引入未证实关键假设，节点不得标记为 `RESOLVED`。

### AC-07 可追溯性

每个 BLOCKER/HIGH Finding 必须可追溯到源证据、Feature 锚点、候选分支、反例和决策树节点。

### AC-08 门禁独立性

执行门禁不得自动修改源 PRD、技术方案或代码；修改必须由后续明确授权的流程完成。

## 9. 质量保证测试

建议使用以下测试验证门禁自身：

- **空知识库测试**：没有任何风险模式时，D2 仍能完成开放探索；
- **风险模式留出测试**：隐藏部分模式，验证开放扫描能否独立发现对应风险；
- **术语扰动测试**：替换领域词汇，验证召回失败不会删除开放候选；
- **新型组合测试**：组合两个正常机制，验证能否发现非历史模式风险；
- **反例复用测试**：同一节点多轮回答时，不重复生成等价反例；
- **错误答案测试**：使用“平台会处理”等答案，验证节点不会虚假关闭；
- **低风险收敛测试**：低风险直接事实不会触发完整八项挑战；
- **追溯测试**：随机抽取 Finding，验证完整追溯链。

## 10. 最终能力边界

本门禁能够提高重要问题的发现率和结论可靠性，但不能证明理论上的绝对完整。最终结论必须同时报告：

- 已覆盖的问题空间；
- 风险边界；
- 知识库补充内容；
- 新型风险候选；
- 尚未获得的证据；
- 有意推迟或明确排除的范围。

核心职责可压缩为：

```text
D1：建立 Feature 因果模型
D2：无知识库开放探索
K ：独立补充已知风险
D3：合并候选并生成最小反例
03：建立依赖有序的问题账本
04–06：查事实、做决策、记录未知
07：关键答案关闭前的增量验证
08–09：更新并收敛
10–11：形成 Finding 并执行 Gate 判定
```
