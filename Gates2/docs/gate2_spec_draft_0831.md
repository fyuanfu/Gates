# Gate2 Skill 完整实现方案

## 1. 目标

Gate2 位于：

```text
Feature 开发完成
        ↓
      Gate2
        ↓
用户 / UAT 验收
```

Gate2 的目标不是重新评审需求，也不是代替 UAT，而是判断：

> 当前 Feature Candidate 是否已经具备进入用户验收的工程条件。

Gate2 最终必须回答四个核心问题：

```text
1. 批准要求是否被正确实现？
2. 应该证明的行为是否已经被有效证明？
3. 本次变更是否引入不可接受的回归或工程风险？
4. 当前 Candidate 是否真实可供验收？
```

最终形成：

```text
Feature Intent
      ↓
Implementation
      ↓
Verification
      ↓
Evidence
      ↓
Finding
      ↓
Verdict
```

最终 Verdict：

```text
PASS
PASS_WITH_ACCEPTED_RISK
BLOCK
```

---

## 2. 核心设计原则

### 2.1 Gate2 不重新做 Gate1

Gate2 将已经批准的：

- Spec
- Story
- AC
- Rule
- Design Decision
- Technical Plan

视为需求和设计 Baseline。

Gate2 不负责重新探索：

- 是否遗漏新的 Scenario；
- Requirement 是否完整；
- Rule 本身是否合理；
- 产品决策是否正确。

这些属于 Gate1。

Gate2 只判断：

> 实际实现是否忠于已经批准的 Baseline。

### 2.2 Gate2 运行过程无人工确认

Gate2 Skill 必须能够一次执行到底：

```text
输入
 ↓
解析
 ↓
检查
 ↓
证据搜集
 ↓
Finding
 ↓
自动验证
 ↓
Block Policy
 ↓
最终报告
```

执行过程中：

```text
不暂停询问开发
不要求人工确认 Finding
不等待人工决策
```

如果 Skill 无法确定：

```text
不是猜测 PASS
而是产生 Evidence Gap / UNKNOWN
```

必要时直接形成阻塞项。

人工参与发生在：

```text
Gate2 最终报告
       ↓
开发团队 Review
       ↓
修复 / 解释 / 风险接受
       ↓
再次运行 Gate2
```

---

## 3. Gate2 Skill 总体架构

```text
                   Gate2 Skill
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Baseline Loader  Change Loader Evidence Loader
          │            │            │
          └────────────┼────────────┘
                       ▼
               Context Builder
                       │
                       ▼
              Gate2 Check Engine
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
Implementation     Verification      Change Safety
   Checker            Checker           Checker
                                           │
                                           ▼
                                  Candidate Checker
                       │
                       ▼
                Finding Engine
                       │
                       ▼
              Evidence Validator
                       │
                       ▼
                Policy Engine
                       │
                       ▼
                 Gate2 Report
```

---

## 4. Skill 输入

Gate2 Skill 不依赖某一种固定文档格式，但需要形成统一内部模型。

### 4.1 Baseline 输入

优先读取：

```text
Spec
Story
AC
Rules
Approved Design Decisions
Technical Design
Implementation Plan
```

内部转换为：

```yaml
requirements:
  - id: AC-01
    type: acceptance_criterion
    required: true
    statement: ...
    source: spec.md

rules:
  - id: RULE-03
    required: true
    statement: ...

design_decisions:
  - id: DD-02
    category: api
    statement: ...
```

---

## 5. Candidate 输入

必须明确 Gate2 检查的是哪个 Candidate。

最低要求：

```yaml
candidate:
  commit_sha:
  build_id:
  artifact:
  branch:
  configuration:
  environment:
```

核心原则：

> 所有 Hard Gate Evidence 必须绑定当前 Candidate。

如果测试结果属于旧 commit：

```text
STALE_EVIDENCE
```

而不是 PASS。

---

## 6. Change 输入

Gate2 必须读取：

```text
base commit
head commit
changed files
diff
新增/删除/修改代码
配置变更
依赖变更
API / schema 变化
```

形成：

```yaml
change_set:
  base:
  head:
  files:
  semantic_changes:
```

Diff 是 Gate2 最核心的事实来源之一。

---

## 7. Test / Evidence 输入

包括：

```text
Test Case
自动化测试
测试代码
测试执行结果
CI Result
Build Result
Static Analysis
Security Scan
Coverage
Contract Check
Smoke Result
Deploy / Install Result
```

统一转成：

```yaml
evidence:
  - id:
    type:
    candidate:
    source:
    result:
    timestamp:
    target:
```

---

## 8. Gate2 六层检查流程

### L1 实现忠实性检查

目标：

> 已批准的 Feature 是否被正确实现。

输入：

```text
Spec / Story / AC / Rule
Design Decision
Plan
Diff
Repository Context
```

#### L1.1 Requirement → Implementation Mapping

对每个 Required Requirement：

```text
AC / Rule
    ↓
找到相关代码变化
    ↓
建立 Implementation Mapping
```

输出：

```yaml
requirement: AC-01
implementation:
  - file:
  - symbol:
  - diff:
status:
```

状态：

```text
IMPLEMENTED
PARTIAL
NOT_FOUND
CONFLICT
```

#### L1.2 语义一致性检查

LLM 判断：

```text
Requirement
    ↕
Implementation
```

检查：

- 实现是否满足需求；
- 是否只实现一部分；
- 是否改变需求语义；
- 是否加入未经批准的新行为；
- Rule 是否被违反。

产生：

```text
IMPLEMENTATION_MISMATCH
MISSING_IMPLEMENTATION
UNAUTHORIZED_BEHAVIOR_CHANGE
```

#### L1.3 Plan / Design 检查

Plan 不要求机械一致。

只重点判断重大决策：

```text
API
Architecture Boundary
Data Model
Schema
Security
External Dependency
Concurrency Strategy
Lifecycle Strategy
```

发现重大偏离：

```text
PLAN_DEVIATION
DESIGN_DECISION_VIOLATION
```

普通实现细节变化：

```text
不产生 Block Finding
```

---

## 9. L2 工程安全检查

这一层优先使用确定性工具。

检查：

```text
Build
Compile
Lint
Static Analysis
Security
Dependency
Secret
Contract
Schema
Architecture Rule
Configuration
```

输出典型 Finding：

```text
BUILD_FAILED
STATIC_ERROR
SECURITY_FINDING
BREAKING_CHANGE
ARCHITECTURE_VIOLATION
CONFIGURATION_ERROR
```

原则：

> 能由 deterministic tool 给结论，就不用 LLM 替代。

LLM 的职责主要是：

```text
解释
关联
归因
风险聚合
```

而不是替代 Build/Test/Scanner。

---

## 10. L3 验证充分性检查

目标：

> 应该证明的行为是不是都有验证。

### 10.1 构建 Required Verification

优先读取已有 Test Obligation。

如果存在：

```text
直接消费
```

如果不存在：

Gate2 Skill 从以下输入推导：

```text
AC
Rule
Risk
重要 Design Decision
```

形成：

```yaml
verification_obligations:
  - id: VO-01
    source: AC-01
    description: 上传成功后文件进入 Uploaded 状态
    required: true
    generated_by: gate2
```

必须明确：

```text
source-provided
gate2-derived
```

避免把 LLM 推导结果冒充上游正式定义。

---

## 11. L3.2 Test Mapping

建立：

```text
Requirement
      ↓
Verification Obligation
      ↓
Test
```

示例：

```yaml
requirement: AC-02
obligation: VO-02
tests:
  - UploadFailureStateTest
```

如果没有对应 Test：

```text
MISSING_TEST_COVERAGE
```

---

## 12. L3.3 Test Quality / Oracle 检查

Gate2 不能只检查：

```text
有没有 Test
```

还需要判断：

```text
这个 Test 是否真的证明 Obligation
```

LLM 分析：

```text
Given / Setup
Action
Assertion
Expected Result
```

例如：

```text
要求：
上传失败恢复 READY

Test：
点击 Upload 后断言 Loading 出现
```

即使 Test PASS：

```text
也不能证明 Requirement
```

输出：

```text
WEAK_ORACLE
IRRELEVANT_TEST
MISSING_VERIFICATION
```

---

## 13. L4 当前 Candidate Evidence 检查

Gate2 必须建立：

```text
Test
 ↓
Execution
 ↓
Candidate
 ↓
Result
```

每个 Required Verification 状态：

```text
PASS
FAIL
UNKNOWN
```

UNKNOWN 包括：

```text
未执行
结果缺失
旧 Candidate
错误环境
结果不可解析
测试被 Skip
```

具体 Finding：

```text
NOT_EXECUTED
TEST_FAILED
REQUIRED_TEST_SKIPPED
STALE_EVIDENCE
INVALID_ENVIRONMENT
UNSTABLE_EVIDENCE
```

原则：

> Missing Evidence ≠ PASS。

---

## 14. L5 Change Impact / Regression Safety

这是 Gate2 的第二个主要 LLM 能力。

输入：

```text
Diff
Repository
Dependency
Call Graph
Feature / Scenario Mapping
Existing Tests
```

流程：

```text
Diff
 ↓
Changed Symbols
 ↓
Dependencies / Callers
 ↓
Affected Feature / Behavior
 ↓
Risk
 ↓
Existing Regression Tests
```

### 14.1 影响识别

寻找：

```text
直接修改对象
上游调用
下游依赖
共享数据
共享状态
公共 API
公共资源
配置
生命周期
并发路径
```

### 14.2 风险形成

输出：

```yaml
impact:
  target:
  affected_behavior:
  reason:
  risk_level:
```

### 14.3 回归证据召回

Gate2 默认：

```text
只召回已有测试
```

不自动生成正式新测试。

如果：

```text
高风险影响
+
没有有效 Existing Test
```

产生：

```text
REGRESSION_GAP
```

---

## 15. L6 Candidate Readiness

最终检查对象不是代码，而是 Candidate。

检查：

```text
Build
Install / Deploy
Startup
Critical Smoke
Runtime Configuration
Required Dependency
Feature Flag
Endpoint
Artifact Identity
```

典型 Finding：

```text
UNTRACEABLE_BUILD
DEPLOY_FAILED
SMOKE_FAILED
INTEGRATION_INCOMPLETE
DEPENDENCY_NOT_READY
CANDIDATE_CONFIG_ERROR
```

目的：

> 不允许把明显无法有效验收的 Candidate 送给 UAT。

---

## 16. 非功能检查

完整 Gate2 不做全量系统级 NFR 验收。

采用：

> Change-triggered Non-functional Gate。

只有本次变更触发相关风险时才要求对应 Evidence。

例如：

```text
新增并发处理
→ concurrency evidence

数据库 schema 改动
→ migration / compatibility evidence

网络重试策略变化
→ resilience evidence

权限 / credential 修改
→ security evidence

大数据处理路径变化
→ performance evidence
```

如果没有风险触发：

```text
不要求 Gate2 执行全量性能 / 稳定性 / 兼容性测试
```

这些留给后续 Feature / Release Gate。

---

## 17. Finding Engine

所有检查统一产出 Finding。

一级分类只保留六类：

```text
1. Implementation Gap
2. Verification Gap
3. Regression Risk
4. Engineering Failure
5. Evidence Gap
6. Open Risk
```

Finding 数据模型：

```yaml
finding:
  id:
  category:
  subtype:
  severity:
  object:
  requirement:
  evidence:
  description:
  reasoning:
  confidence:
  block_candidate:
  verification_status:
```

---

## 18. LLM Finding 自动验证机制

由于执行过程中不允许人工确认，因此必须设计自动验证阶段。

流程：

```text
LLM Finding
     ↓
Can deterministic evidence verify?
     │
 ┌───┴────┐
 YES      NO
 │         │
 ▼         ▼
Test      Repo Evidence
Scanner   Cross-source consistency
Build     Multiple-agent review
Contract  Confidence / evidence sufficiency
 │         │
 └────┬────┘
      ▼
Finding Status
```

状态：

```text
CONFIRMED
SUPPORTED
UNRESOLVED
REJECTED
```

---

## 19. 不确定 Finding 的处理

Gate2 不询问人工。

如果：

```text
Finding 具有高影响
+
当前 Evidence 无法排除风险
```

输出：

```text
UNRESOLVED_BLOCKING_RISK
```

进入 BLOCK。

如果：

```text
低影响
+
证据不足
```

可输出：

```text
WARNING
```

但必须在最终报告明确展示。

---

## 20. 多 Agent / 多 Pass Review

为了降低单次 LLM 判断偏差，建议 Gate2 Skill 不做一次大 Prompt。

拆成多个独立 Pass：

```text
Pass 1  Requirement Compliance Review
Pass 2  Implementation Completeness Review
Pass 3  Test Adequacy Review
Pass 4  Impact / Regression Review
Pass 5  Design / Architecture Decision Review
Pass 6  Finding Verification Review
```

最后由：

```text
Finding Consolidator
```

负责：

```text
去重
冲突合并
证据补充
严重度统一
```

---

## 21. Evidence Validator

任何参与 Hard Block 的 Finding 必须记录证据来源。

支持：

```text
Code Evidence
Diff Evidence
Test Evidence
Build Evidence
Scanner Evidence
Contract Evidence
Repository Evidence
Runtime Evidence
```

Evidence 至少需要：

```yaml
evidence:
  source:
  candidate:
  location:
  content_summary:
  generated_at:
  validity:
```

---

## 22. Evidence 可信度规则

优先级：

```text
Executable Evidence
      >
Deterministic Analysis
      >
Repository Fact
      >
Cross-source LLM Reasoning
      >
Single LLM Judgment
```

原则：

> 单独的 LLM Opinion 不应成为唯一 Hard Block Evidence。

但如果：

```text
LLM 发现重大风险
+
事实证据可以证明风险存在
+
缺少能够证明其安全的反向 Evidence
```

Gate2 可以产生 BLOCK。

---

## 23. Block Policy Engine

最终只保留四条顶层阻断政策。

### B1 Implementation

```text
Mandatory Feature Behavior
未实现 / 实现错误
→ BLOCK
```

### B2 Verification

```text
Mandatory Verification Obligation
没有当前 Candidate 上有效 PASS Evidence
→ BLOCK
```

### B3 Safety

```text
Build / Test / Security /
Regression / Compatibility /
Engineering Risk
超过 Policy Threshold
→ BLOCK
```

### B4 Candidate

```text
Candidate 无法
Build / Install / Deploy /
Start / Smoke / 正确配置
→ BLOCK
```

所有细 Finding 最终映射到：

```text
B1 / B2 / B3 / B4
```

---

## 24. Finding 生命周期

完整生命周期：

```text
DETECTED
   ↓
VERIFIED / SUPPORTED
   ↓
BLOCKING / NON_BLOCKING
   ↓
REPORT
```

本次 Gate2 Skill 运行期间：

```text
不等待 Close
```

因为修复发生在报告输出以后。

下一次重新执行 Gate2：

```text
Finding disappeared
→ RESOLVED

Finding remains
→ OPEN

Evidence proves false positive
→ REJECTED
```

---

## 25. Accepted Risk 处理

由于 Gate2 本次执行不允许人工确认：

```text
Gate2 不在运行过程中创建 Waiver。
```

仅消费：

> 执行前已经存在并有效的 Approved Waiver。

Waiver 必须包含：

```yaml
waiver:
  finding/risk:
  approved_by:
  reason:
  scope:
  expires_at:
```

没有预先批准 Waiver：

```text
Blocking Finding
→ BLOCK
```

最终报告后开发和责任人可以决定：

```text
修复
或
申请 Risk Acceptance
```

随后重新执行 Gate2。

---

## 26. Skill 工作流

完整运行顺序：

```text
START
 │
 ▼
1. Detect Candidate
 │
 ▼
2. Load Approved Baseline
 │
 ▼
3. Load Change Set / Diff
 │
 ▼
4. Load Test & CI Evidence
 │
 ▼
5. Build Requirement Model
 │
 ▼
6. Requirement → Implementation Mapping
 │
 ▼
7. Implementation Semantic Review
 │
 ▼
8. Engineering Checks
 │
 ▼
9. Build Verification Obligations
 │
 ▼
10. Obligation → Test Mapping
 │
 ▼
11. Test Oracle Adequacy Review
 │
 ▼
12. Candidate Test Result Validation
 │
 ▼
13. Change Impact Analysis
 │
 ▼
14. Regression Evidence Check
 │
 ▼
15. Candidate Readiness Check
 │
 ▼
16. Non-functional Risk Trigger Check
 │
 ▼
17. Consolidate Findings
 │
 ▼
18. Auto Verify Findings
 │
 ▼
19. Apply Block Policies
 │
 ▼
20. Produce Gate2 Report
 │
 ▼
END
```

---

## 27. Skill 内部模块建议

```text
gate2/
├── SKILL.md
├── workflows/
│   ├── load-context.md
│   ├── implementation-review.md
│   ├── verification-review.md
│   ├── impact-review.md
│   ├── evidence-validation.md
│   └── verdict.md
│
├── schemas/
│   ├── baseline.schema.yaml
│   ├── candidate.schema.yaml
│   ├── obligation.schema.yaml
│   ├── evidence.schema.yaml
│   └── finding.schema.yaml
│
├── policies/
│   ├── block-policy.yaml
│   ├── severity-policy.yaml
│   └── waiver-policy.yaml
│
└── templates/
    ├── gate2-report.html
    └── gate2-report.json
```

---

## 28. SKILL.md 的职责

SKILL.md 只承担：

```text
什么时候执行 Gate2
输入发现顺序
整体工作流
调用各检查阶段
失败处理
输出要求
```

不要把几十条具体规则全部堆入 SKILL.md。

详细规则放到：

```text
workflows/
policies/
schemas/
```

避免 Skill 主文件失控。

---

## 29. 输出 1：Gate2 JSON

用于机器消费。

```yaml
gate:
  id: gate2
  candidate:
  verdict: BLOCK

summary:
  requirements:
  verification:
  regression:
  engineering:
  candidate:

blocking_findings:
  - id:
    policy: B2
    requirement:
    evidence:

warnings:

evidence_matrix:
```

---

## 30. 输出 2：Gate2 HTML 报告

供开发团队 review。

报告建议固定为：

### 30.1 Gate Summary

```text
Candidate
Verdict
Blocking Finding Count
Warning Count
Evidence Completeness
```

### 30.2 Block Items

优先展示：

```text
BLOCK-01
对应 Requirement
问题
证据
为什么阻塞
建议处理方向
```

### 30.3 Feature Implementation Matrix

```text
Requirement
Implementation
Status
Finding
```

### 30.4 Verification Matrix

```text
Requirement
Verification Obligation
Test
Execution
Evidence
Verdict
```

### 30.5 Regression / Impact Matrix

```text
Changed Area
Affected Behavior
Risk
Regression Test
Evidence
```

### 30.6 Engineering Checks

```text
Build
Static
Security
Contract
Config
```

### 30.7 Candidate Readiness

```text
Build
Install
Deploy
Smoke
Environment
```

### 30.8 Findings

全部 Finding 明细。

---

## 31. 最关键的 Evidence Matrix

最终建议形成统一矩阵：

```text
Requirement
    ↓
Implementation
    ↓
Verification Obligation
    ↓
Test / Check
    ↓
Execution
    ↓
Evidence
    ↓
Finding
    ↓
Verdict
```

例如：

| Requirement | Implementation | Verification | Test | Result | Evidence | Finding | Verdict |
|---|---|---|---|---|---|---|---|
| AC-01 | UploadManager | VO-01 | UploadSuccessTest | PASS | build-123 | — | PASS |
| AC-02 | RetryHandler | VO-02 | — | UNKNOWN | — | Verification Gap | BLOCK |

这张矩阵是 Gate2 最核心的产物。

---

## 32. Gate2 Skill 最终职责边界

Gate2 做：

```text
实现一致性
实现完整性
验证充分性
当前 Evidence
变更安全
必要回归
工程检查
Candidate Readiness
Finding
Block Verdict
```

Gate2 不做：

```text
重新设计 Requirement
重新补完整产品 Spec
完整 UAT
完整系统验收
全量 Release Validation
自动修改业务决策
运行过程中要求人工判断
```

---

## 33. 最终实现定义

Gate2 Skill 可以最终定义为：

> 一个面向 Feature Candidate 的自动化工程准出 Skill。它以批准后的需求与设计作为 Baseline，结合实际 Diff、Repository、测试资产、CI 与运行证据，通过确定性检查和 LLM 语义审计，自动识别实现偏差、验证缺口、回归风险、工程失败和证据缺口，并依据统一 Block Policy 生成可审计的 Gate2 Verdict。执行过程中不依赖人工确认，最终报告交由开发团队 review、修复或进行风险接受。

其核心不是：

```text
LLM Review Code
```

而是：

```text
Baseline
   ↓
Implementation
   ↓
Verification
   ↓
Evidence
   ↓
Risk
   ↓
Verdict
```

这是整个 Gate2 Skill 的主干。
