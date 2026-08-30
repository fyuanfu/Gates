# Gating Finding 四级分类

## 1. 一级分类：问题阶段 Stage

用于回答：

> **问题发生在哪个研发阶段？**

### 1.1 需求设计 Requirement Design

定义软件“要做什么”。

主要包括：

- 产品目标
- 用户需求
- 用户故事
- 业务流程
- 业务场景
- 业务规则
- 状态与状态转换
- 数据要求
- 验收标准
- 外部依赖
- 非功能需求
- 业务约束
- 产品决策

### 1.2 技术方案设计 Technical Design

定义需求“怎么通过软件实现”。

主要包括：

- 系统职责
- 模块职责
- 软件架构
- 组件设计
- 接口设计
- 数据模型
- 状态模型
- 调用流程
- 数据流
- 异常处理
- 并发设计
- 重试策略
- 恢复策略
- 幂等设计
- 缓存设计
- 持久化设计
- 性能设计
- 安全设计
- 技术决策

### 1.3 编码实现 Implementation

将批准的需求和技术方案转换成实际软件。

主要包括：

- 业务代码
- 状态处理
- 数据处理
- 接口调用
- 异常处理
- 并发实现
- 配置
- 资源
- 数据库变更
- 构建脚本
- 依赖
- Feature Flag
- 软件变更
- 构建产物

### 1.4 验证 Verification

证明需求、设计和实现是否正确完成。

主要包括：

- 验收义务
- 测试义务
- 测试用例
- Oracle
- 测试覆盖
- 回归范围
- 测试执行
- 测试数据
- 测试环境
- Evidence
- Completion Claim
- 验证结果

---

## 2. 二级分类：问题对象 Object

用于回答：

> **具体哪个对象存在问题？**

### 2.1 需求设计对象

- Goal：目标
- Story：用户故事
- Flow：业务流程
- Scenario：业务场景
- Rule：业务规则
- State：状态与状态转换
- Data：业务数据
- AC：验收标准
- Dependency：外部依赖
- NFR：非功能要求
- Constraint：业务或系统约束
- Decision：产品/业务决策

### 2.2 技术方案设计对象

- Responsibility：系统/模块职责
- Architecture：架构
- Component：组件
- Interface：接口
- Data Model：数据模型
- State Model：状态模型
- Control Flow：控制流程
- Data Flow：数据流
- Error Handling：异常处理
- Concurrency：并发方案
- Retry：重试方案
- Recovery：恢复方案
- Idempotency：幂等方案
- Cache：缓存方案
- Persistence：持久化方案
- Security：安全方案
- Performance：性能方案
- Technical Decision：技术决策

### 2.3 编码实现对象

- Code：代码
- Business Logic：业务逻辑
- State Handling：状态处理
- Data Processing：数据处理
- API Integration：接口集成
- Error Handling：异常实现
- Concurrency Implementation：并发实现
- Configuration：配置
- Resource：资源
- Database Migration：数据库变更
- Build：构建
- Dependency：依赖
- Change：代码变更
- Artifact：软件产物

### 2.4 验证对象

- Acceptance Obligation：验收义务
- Test Obligation：测试义务
- Test Case：测试用例
- Oracle：判定标准
- Test Coverage：测试覆盖
- Regression Scope：回归范围
- Test Execution：测试执行
- Test Data：测试数据
- Test Environment：测试环境
- Evidence：验证证据
- Completion Claim：完成声明
- Verification Result：验证结果

### 2.5 关系对象

除了单个对象，还必须检查对象之间的关系。

#### 需求内部关系

- Goal → Story
- Story → Flow
- Story → Scenario
- Scenario → Rule
- Scenario → State
- Scenario → Data
- Scenario → AC
- Rule → State

#### 需求到设计

- Requirement → Design
- Scenario → Responsibility
- Rule → Interface
- State → Component
- Data → Data Model
- NFR → Technical Design

#### 设计到实现

- Design → Code
- Interface → Implementation
- State Model → State Handling
- Error Strategy → Error Handling Code

#### 实现到验证

- AC → Test
- Scenario → Test
- Rule → Test
- Change → Affected Feature
- Affected Feature → Regression Test
- Test → Evidence
- Code Snapshot → Evidence

---

## 3. 三级分类：问题属性 Attribute

用于回答：

> **这个对象本来应该满足什么要求，但没有满足？**

### 3.1 完整性 Completeness

判断：

> 应该定义或实现的内容是否齐全。

典型问题：

- 内容缺失
- 分支遗漏
- 状态遗漏
- 规则遗漏
- 接口字段遗漏
- 实现路径遗漏

### 3.2 覆盖性 Coverage

判断：

> 已知问题空间是否被充分覆盖。

主要包括：

- 场景覆盖
- 流程覆盖
- 状态覆盖
- Rule 覆盖
- 数据空间覆盖
- 异常路径覆盖
- 影响范围覆盖
- 测试覆盖
- 回归覆盖

### 3.3 正确性 Correctness

判断：

> 当前定义是否符合已知的正确依据。

正确依据可能来自：

- 上游目标
- 业务规则
- 已批准决策
- 领域知识
- 外部契约
- 平台规则
- 技术约束

### 3.4 明确性 Clarity

判断：

> 一个定义是否只能产生一种合理解释。

典型问题：

- 模糊描述
- 术语含义不清
- 条件不明确
- 输入输出不明确
- 范围不明确

### 3.5 一致性 Consistency

判断：

> 不同对象之间是否互相矛盾。

主要包括：

- Rule ↔ Rule
- Scenario ↔ Rule
- Scenario ↔ State
- AC ↔ Scenario
- Requirement ↔ Design
- Design ↔ Code
- Code ↔ Test

### 3.6 可验证性 Verifiability

判断：

> 是否能够明确判断“对还是错”。

主要检查：

- 是否存在 Observable Result
- 是否存在 Oracle
- 是否定义成功条件
- 是否定义失败条件
- 是否能够形成明确 Verdict

### 3.7 决策闭合性 Decision Closure

判断：

> 会影响后续工作的关键问题是否已经形成明确决策。

例如：

- 是否自动重试
- 冲突以谁为准
- 删除是否可恢复
- 超时如何处理
- 数据一致性策略

### 3.8 可追溯性 Traceability

判断：

> 上下游对象能否明确建立对应关系。

例如：

- Story → Scenario
- Scenario → AC
- Requirement → Design
- Design → Code
- AC → Test
- Test → Evidence

### 3.9 符合性 Conformance

主要用于下游是否遵守上游批准内容。

例如：

- 设计是否符合需求
- 实现是否符合设计
- 测试是否验证了 AC
- 实际配置是否符合批准方案

### 3.10 证据充分性 Evidence Sufficiency

判断：

> 当前证据是否足以支持“已经完成、已经验证、没有问题”等结论。

主要包括：

- 是否存在 Evidence
- Evidence 是否有效
- Evidence 是否完整
- Evidence 是否覆盖所有义务
- Evidence 是否足以支撑 Verdict

### 3.11 当前性 Currentness

判断：

> Evidence 是否对应当前被评审的软件快照。

主要包括：

- Commit 是否一致
- Diff 是否一致
- 构建产物是否一致
- Test Run 是否针对当前代码
- Evidence 是否已经过期

---

## 4. 四级分类：Finding Type

用于回答：

> **质量属性没有满足后，具体表现为什么问题？**

### 4.1 缺失 Missing

应该存在，但不存在。

例如：

- Scenario 缺失
- Rule 缺失
- State 缺失
- 设计方案缺失
- 实现路径缺失
- Test 缺失
- Evidence 缺失

### 4.2 错误 Incorrect

已经存在，但内容不正确。

例如：

- Rule 错误
- 状态转换错误
- 接口设计错误
- 数据模型错误
- 代码逻辑错误
- 配置错误

判定 Incorrect 时必须存在可靠的正确性依据。

### 4.3 歧义 Ambiguous

存在多个合理解释，无法唯一确定行为。

例如：

- “快速”
- “适当”
- “必要时”
- “失败后重试”

但没有进一步限定。

### 4.4 不一致 Inconsistent

两个或多个对象之间相互冲突。

例如：

```text
Rule：
Paid 状态不允许修改地址

Scenario：
Paid 状态修改地址成功
```

### 4.5 不可验证 Unverifiable

无法通过明确证据判断是否满足要求。

例如：

```text
AC：
页面体验良好
```

不存在明确 Oracle。

### 4.6 未决 Unresolved

关键问题已经识别，但没有形成最终决策。

例如：

```text
网络失败：

A. 自动重试
B. 用户重试

TBD
```

### 4.7 不可追溯 Untraceable

无法找到上下游对应关系。

例如：

- Story 无 Scenario
- Requirement 无 Design
- Design 无 Code
- AC 无 Test
- Test 无 Evidence

### 4.8 无效 Invalid

某个对象虽然存在，但不能作为当前门禁判断的有效依据。

主要用于验证阶段。

例如：

- Test Result 属于旧 Commit
- Evidence 已经过期
- 测试执行环境错误
- 构建产物不是当前版本
- Evidence Hash 与当前代码不一致

---

## 5. 最终四级结构

```text
Finding
│
├── Level 1：Stage
│   ├── 需求设计
│   ├── 技术方案设计
│   ├── 编码实现
│   └── 验证
│
├── Level 2：Object
│   ├── 阶段内实体对象
│   └── 对象关系
│
├── Level 3：Attribute
│   ├── 完整性
│   ├── 覆盖性
│   ├── 正确性
│   ├── 明确性
│   ├── 一致性
│   ├── 可验证性
│   ├── 决策闭合性
│   ├── 可追溯性
│   ├── 符合性
│   ├── 证据充分性
│   └── 当前性
│
└── Level 4：Finding Type
    ├── 缺失
    ├── 错误
    ├── 歧义
    ├── 不一致
    ├── 不可验证
    ├── 未决
    ├── 不可追溯
    └── 无效
```

---

## 6. 标准表达方式

一个 Finding 应至少能够表达为：

```text
Stage / Object / Attribute / Finding Type
```

例如：

```text
需求设计 / Scenario / 覆盖性 / 缺失

需求设计 / Rule / 一致性 / 不一致

需求设计 / AC / 可验证性 / 不可验证

技术方案设计 / Interface / 完整性 / 缺失

技术方案设计 / State Model / 一致性 / 不一致

编码实现 / Code / 符合性 / 错误

编码实现 / Change Impact / 覆盖性 / 缺失

验证 / Test Case / 覆盖性 / 缺失

验证 / Oracle / 可验证性 / 不可验证

验证 / Evidence / 当前性 / 无效
```

最终可以统一理解为：

> **第一层定位阶段，第二层定位对象，第三层说明对象哪里不合格，第四层描述问题最终表现形式。**
