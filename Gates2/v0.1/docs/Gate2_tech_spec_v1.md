# Gate2 Technical Spec V1

> 文件名：`Gate2_tech_spec_v1.md`  
> 版本：V1  
> 来源：`Gate2_spec_report.html`  
> 定位：Feature 开发完成后的工程准出（Engineering Exit Gate）

---

## 1. 文档目的

本文档定义 Gate2 V1 的技术实现规格。

Gate2 位于 Feature 开发完成与用户 / UAT 验收之间，其目标不是替代 UAT，也不是重新进行需求评审，而是在进入用户验收前，由研发侧完成一次**有证据的工程验收**。

Gate2 需要证明以下闭环成立：

```text
批准的需求 / 设计意图
        ↓
实际实现
        ↓
验证证据
        ↓
变更风险
        ↓
当前 Candidate
        ↓
Gate Verdict
```

Gate2 最终输出可审计的 Finding、Evidence 和准出结论。

---

## 2. Gate2 定位

### 2.1 Gate2 要解决的问题

Gate2 最终只回答四个问题：

| # | 目标 | 核心问题 | 判定重点 |
|---|---|---|---|
| 1 | Implementation | 做对了吗？ | 批准的需求和设计是否被正确实现，是否存在漏实现、错误实现或语义偏差 |
| 2 | Verification | 证明了吗？ | 关键需求行为是否存在有效测试，并在当前 Candidate 上形成可信 Evidence |
| 3 | Safety | 搞坏了吗？ | 本次 Diff 是否引入不可接受的回归、兼容、安全、接口或工程风险 |
| 4 | Readiness | 能验收了吗？ | 当前 Candidate 是否能正常 Build、安装 / 部署、启动并通过 Critical Smoke |

### 2.2 Gate2 不做什么

Gate2 V1 不承担以下职责：

- 不重新定义产品需求；
- 不替代 Gate1 的需求 / 技术方案完整性评审；
- 不替代最终 UAT；
- 不把“存在测试文件”直接等价为“需求已经被证明”；
- 不把单次 LLM Opinion 直接作为唯一 Hard Block 依据；
- 不在执行过程中逐项要求人工确认。

---

## 3. 总体原则

### 3.1 核心闭环

```text
Baseline
Spec / AC / Rule / Design
        ↓
Implementation
Diff / Code / Config
        ↓
Verification & Risk Check
Test / Impact / CI / Security
        ↓
Evidence
Current Candidate Facts
        ↓
Finding
        ↓
Policy
        ↓
PASS / BLOCK
```

### 3.2 核心原则

> **LLM 找问题，Evidence 定事实。**

LLM 用于扩大检查空间，负责：

- 语义理解；
- 需求与实现关联；
- 需求与测试关联；
- 跨文件逻辑检查；
- 影响范围推理；
- 风险发现；
- Finding 归因和解释。

确定性工具负责提供事实证据，例如：

- Build；
- Compile；
- Test Execution；
- Static Analysis；
- Security Scanner；
- Contract Checker；
- Dependency / Call Graph；
- Install / Deploy；
- Smoke Test。

LLM 发现的问题必须尽可能转化成可审计 Finding，并绑定 Evidence。

---

## 4. Gate2 V1 输入

Gate2 Skill 至少需要读取以下输入域。

### 4.1 Baseline

批准的产品与技术基线：

```text
Spec
Acceptance Criteria
Rule
Technical Design
```

Baseline 用于回答：

> 本次 Feature 被批准要求实现什么？

### 4.2 Candidate

当前待准出的实际交付对象：

```text
Commit / Patchset
Diff
Code
Config
Build Artifact
```

Candidate 用于回答：

> 本次实际交付了什么？

### 4.3 Verification Assets

用于证明行为正确性的验证资产：

```text
Test
Assertion / Oracle
Test Result
Execution Environment
Execution Target
```

### 4.4 Engineering Evidence

用于证明工程状态和变更安全性的事实：

```text
Build Result
Compile Result
Static Analysis Result
Security Result
Contract Check Result
Dependency / Call Information
Regression Result
Install / Deploy Result
Smoke Result
```

---

## 5. Gate2 总体执行流程

Gate2 Skill 采用**自动执行、最终集中输出**模式。

执行过程中不进行逐项人工确认。

```text
01 读取 Baseline
        ↓
02 读取 Candidate
        ↓
03 实现语义检查
        ↓
04 Verification 检查
        ↓
05 Impact 检查
        ↓
06 工程检查
        ↓
07 Candidate Readiness
        ↓
08 Evidence 汇聚
        ↓
09 Finding 验证
        ↓
10 Policy & Report
```

---

## 6. Stage 01：读取 Baseline

### 输入

```text
Spec
AC
Rule
Design
```

### 目标

建立本次 Gate2 检查使用的批准意图基线。

### 输出

形成统一的 Baseline Context，供后续：

- 实现一致性检查；
- Verification 检查；
- 设计一致性检查；
- Finding Traceability 使用。

---

## 7. Stage 02：读取 Candidate

### 输入

```text
Commit / Patchset
Diff
Code
Config
Build Artifact
```

### 目标

冻结本次 Gate2 所判断的 Candidate。

所有测试结果、Build 结果和 Evidence 必须能够追溯到该 Candidate。

### 核心要求

不得使用：

- 其他 Commit 的测试结果；
- 过期 Build；
- 无法确认版本的日志；
- 无法追溯到当前 Candidate 的 Evidence。

---

## 8. Stage 03：Implementation Consistency Check

### 8.1 目标

回答：

> **批准的需求和设计是否被正确实现？**

检查关系：

```text
Spec / AC / Rule / Design
            ↕
      Actual Diff / Code
```

### 8.2 主要检查项

Gate2 至少检查：

1. Required AC 是否漏实现；
2. Required AC 是否只实现一部分；
3. Rule 是否在实现中丢失；
4. 实际代码行为是否与需求语义冲突；
5. 是否存在错误实现；
6. 是否存在未经批准的行为变化；
7. 是否偷偷改变已有行为；
8. 重大设计决策是否被绕过；
9. Config 是否导致实际行为偏离批准意图。

### 8.3 输出

可能形成：

```text
Implementation Gap
Open Risk
Evidence Gap
```

---

## 9. Stage 04：Verification Sufficiency Check

### 9.1 目标

回答：

> **关键需求行为是否已经被有效证明？**

检查链路：

```text
Requirement
    ↓
Verification
    ↓
Test
    ↓
Assertion / Oracle
    ↓
Execution Result
    ↓
Evidence
```

### 9.2 主要检查项

Gate2 至少检查：

1. Required Behavior 是否有验证；
2. Test 是否真正对应 Requirement；
3. Test 是否只覆盖局部实现而没有证明需求行为；
4. Assertion / Oracle 是否足够强；
5. 是否存在“测试执行了，但没有有效断言”的情况；
6. 测试结果是否为 PASS；
7. 测试结果是否来自当前 Candidate；
8. 测试环境是否能够支撑该结论；
9. Required Behavior 是否存在 Verification Gap。

### 9.3 关键规则

```text
有 Test
≠
Requirement 已被证明
```

必须建立：

```text
Requirement
→ Test
→ Result
→ Current Candidate Evidence
```

### 9.4 输出

可能形成：

```text
Verification Gap
Evidence Gap
Implementation Gap
```

---

## 10. Stage 05：Change Impact & Regression Check

### 10.1 目标

回答：

> **本次变更是否可能破坏已有系统？**

检查链路：

```text
Diff
 ↓
Impact
 ↓
Risk
 ↓
Regression Verification
 ↓
Evidence
```

### 10.2 主要检查项

至少覆盖：

- API / Contract 变化；
- Config 变化；
- Shared State 变化；
- 依赖变化；
- 调用链变化；
- 公共模块变化；
- 兼容性风险；
- 已有 Feature 行为影响；
- 高风险影响是否存在 Regression Evidence。

### 10.3 判定原则

发现潜在 Impact 不等于直接 BLOCK。

需要继续判断：

```text
Impact
→ Risk
→ 是否需要验证
→ 是否已有 Regression Evidence
→ 风险是否关闭
```

无法关闭的高风险项形成 Finding。

### 10.4 输出

可能形成：

```text
Regression Risk
Open Risk
Evidence Gap
```

---

## 11. Stage 06：Engineering Check

### 11.1 目标

使用确定性工具检查工程级失败。

### 11.2 主要检查对象

```text
Build
Compile
Static Analysis
Security
Contract
Compatibility
```

### 11.3 规则

对于确定性失败，可以直接形成高置信度 Finding。

例如：

```text
Build Failed
Security Critical Finding
Contract Breaking Change
Compile Failed
```

这类结果不需要依赖 LLM Opinion 才能成立。

### 11.4 输出

主要形成：

```text
Engineering Failure
```

必要时同时形成：

```text
Regression Risk
Open Risk
```

---

## 12. Stage 07：Candidate Readiness Check

### 12.1 目标

回答：

> **当前 Candidate 是否真正可以交给用户 / UAT 验收？**

### 12.2 检查链路

```text
Build
  ↓
Install / Deploy
  ↓
Launch
  ↓
Critical Smoke
```

### 12.3 主要检查项

1. Candidate 是否唯一可追溯；
2. Build 是否成功；
3. 是否可以正常安装 / 部署；
4. 是否可以正常启动；
5. Critical Smoke 是否通过；
6. Feature Flag 是否正确；
7. Endpoint 是否正确；
8. Config 是否正确；
9. 当前 Candidate 是否满足基础验收条件。

### 12.4 输出

可能形成：

```text
Engineering Failure
Evidence Gap
Open Risk
```

---

## 13. Stage 08：Evidence Aggregation

### 13.1 目标

将前面所有检查结果绑定到当前 Candidate，并形成统一 Evidence。

### 13.2 Evidence 基本要求

有效 Evidence 至少应满足：

```text
Correct Target
Current Version
Traceable
Reproducible / Auditable
Relevant to Finding or Requirement
```

### 13.3 无效 Evidence 示例

- 来自旧 Commit；
- 无法确认执行对象；
- 只有截图，没有上下文；
- Test PASS，但无法追溯到对应 Requirement；
- 日志存在，但无法支持结论；
- 只有 LLM 推断，没有外部事实支撑。

---

## 14. Stage 09：Finding Validation

### 14.1 目标

将原始检查结果收敛成可信、可处理、可审计的问题项。

### 14.2 自动处理

Finding 输出前至少执行：

```text
去重
↓
Evidence 补充
↓
事实核验
↓
Traceability 补充
↓
Severity / Blocking 属性计算
```

### 14.3 Finding 最终六类

#### F1. Implementation Gap

定义：

> 要求与实际实现存在缺口。

典型场景：

- Required Behavior 未实现；
- 部分实现；
- 错误实现；
- 实现语义与批准需求冲突。

---

#### F2. Verification Gap

定义：

> 应当被证明的行为没有得到有效证明。

典型场景：

- 没有 Test；
- Test 与 Requirement 不对应；
- Oracle 太弱；
- 缺少 Required Scenario 的验证；
- Test 未执行。

---

#### F3. Regression Risk

定义：

> 本次变更可能破坏已有系统，且风险尚未被充分关闭。

典型场景：

- 公共模块变更；
- API / Contract 变化；
- Shared State 变化；
- 高风险调用链受影响；
- 缺少必要 Regression Evidence。

---

#### F4. Engineering Failure

定义：

> Build、Static、Security、Contract 等确定性工程检查失败。

典型场景：

- Build Failed；
- Compile Failed；
- Critical Static Finding；
- Critical Security Finding；
- Contract Breaking Failure。

---

#### F5. Evidence Gap

定义：

> 证据缺失、过期、版本错误或不可追溯。

典型场景：

- 使用旧 Candidate 结果；
- 结果与 Commit 无法关联；
- 缺少日志 / 报告；
- Evidence 无法支持 Finding 关闭。

---

#### F6. Open Risk

定义：

> 已发现风险尚未关闭，也没有完成合法风险接受。

典型场景：

- 已知风险没有修复；
- 风险没有验证；
- 风险超出允许阈值；
- 风险被口头接受但没有正式记录。

---

## 15. Stage 10：Blocking Policy

Gate2 V1 最终只保留四条最高层阻断策略。

### B1｜没有正确实现

阻断条件：

> Required Feature Behavior 未实现或实现错误。

典型 Finding：

```text
Implementation Gap
```

---

### B2｜没有有效证明

阻断条件：

> Required Behavior 没有当前 Candidate 上有效的 PASS Evidence。

典型 Finding：

```text
Verification Gap
Evidence Gap
```

---

### B3｜存在不可接受风险

阻断条件：

> Build / Test / Security / Regression / Compatibility 等风险超过准出阈值。

典型 Finding：

```text
Regression Risk
Engineering Failure
Open Risk
```

---

### B4｜Candidate 不可验收

阻断条件：

> Build / Install / Deploy / Smoke / Config 不满足进入用户验收的基础条件。

典型 Finding：

```text
Engineering Failure
Evidence Gap
Open Risk
```

---

## 16. Verdict

Gate2 V1 对当前 Candidate 输出：

```text
PASS
BLOCK
```

### PASS

满足：

- Required Behavior 已正确实现；
- Required Behavior 已得到有效证明；
- 不存在不可接受的变更风险；
- Candidate 满足验收基础条件；
- 不存在触发 B1～B4 的阻塞项。

### BLOCK

任一 B1～B4 被触发即 BLOCK。

---

## 17. LLM 与确定性工具职责边界

| 检查关系 | LLM 负责 | 确定性工具负责 | 原则 |
|---|---|---|---|
| Requirement ↔ Implementation | 语义偏差、遗漏、跨文件逻辑问题 | Repository Fact、Diff | LLM 发现问题，Evidence 验证事实 |
| Requirement ↔ Test | 测试缺口、Oracle 是否足够 | Test Execution、Result | 有 Test 不代表证明了 Requirement |
| Diff ↔ Impact | 影响范围、回归风险推理 | Dependency Graph、Call Graph、Regression Result | 风险未闭环则形成 Finding |
| Build / Static / Security / Contract | 解释、关联、归因 | Build、Scanner、Contract Checker | 确定性失败可直接 Hard Block |

### 关键约束

单次 LLM 判断不得直接成为唯一 Hard Block 证据。

对于语义类 Finding，优先补充：

```text
Code Fact
Diff Fact
Test Fact
Runtime Fact
Build / Tool Result
```

再进入 Blocking Policy。

---

## 18. Gate2 Report 输出

Gate2 Skill 最终一次性输出报告，不在执行中逐条打断开发者确认。

报告至少包含：

```text
Gate2 Report
├─ Candidate
├─ Verdict
├─ Blocking Findings
├─ Non-Blocking Findings
├─ Requirement / Implementation Trace
├─ Verification Trace
├─ Impact / Regression Result
├─ Engineering Result
├─ Candidate Readiness Result
└─ Evidence
```

### 18.1 Blocking Finding 最小字段

建议 V1 至少包含：

```yaml
id:
type:
title:
description:
affected_requirement:
affected_code:
evidence:
blocking_policy:
status:
```

### 18.2 Evidence 最小字段

建议 V1 至少包含：

```yaml
id:
type:
source:
candidate:
result:
location:
timestamp:
```

---

## 19. Gate2 闭环

Gate2 不是一次性报告，而是 Candidate 准出的闭环。

```text
Gate2 Skill
   ↓
Gate2 Report
Blocking Findings + Evidence
   ↓
开发团队 Review
   ↓
修复 / 补 Evidence / 风险关闭
   ↓
重新执行 Gate2
   ↓
PASS
```

执行期间不人工逐项确认。

人工参与点位于：

> **Gate2 Report 输出之后。**

开发团队根据最终 Blocking Findings：

- 修复实现；
- 补充验证；
- 补充 Evidence；
- 关闭风险；
- 对合法允许的风险执行项目定义的风险处理流程。

之后重新运行 Gate2。

---

## 20. Gate2 V1 实现验收标准

Gate2 Skill V1 至少满足以下要求。

### AC-G2-01：能够读取 Baseline

能够读取并识别：

- Spec；
- AC；
- Rule；
- Design。

### AC-G2-02：能够绑定当前 Candidate

所有 Gate2 结论必须绑定明确 Candidate。

### AC-G2-03：能够执行实现一致性检查

能够发现明显：

- 漏实现；
- 部分实现；
- 错误实现；
- 语义冲突。

### AC-G2-04：能够执行 Verification 检查

能够建立：

```text
Requirement → Test → Result → Evidence
```

并识别 Verification Gap。

### AC-G2-05：能够执行 Impact / Regression 检查

能够根据 Diff 识别潜在影响，并检查高风险影响是否已有验证证据。

### AC-G2-06：能够接入确定性工程结果

至少能够消费：

- Build；
- Test；
- Static；
- Security；
- Contract；
- Smoke

等工具结果。

### AC-G2-07：能够统一 Evidence

能够识别：

- Evidence 缺失；
- Evidence 过期；
- Candidate 不一致；
- Evidence 不可追溯。

### AC-G2-08：Finding 统一分类

所有最终 Finding 必须收敛到六个根类之一：

```text
Implementation Gap
Verification Gap
Regression Risk
Engineering Failure
Evidence Gap
Open Risk
```

### AC-G2-09：统一阻断策略

所有 BLOCK 必须能够追溯到：

```text
B1
B2
B3
B4
```

之一。

### AC-G2-10：自动执行

Gate2 执行过程中不得依赖人工逐项确认。

### AC-G2-11：一次性输出最终报告

最终报告必须包含：

- Verdict；
- Blocking Findings；
- Evidence；
- Traceability。

### AC-G2-12：支持重新执行形成闭环

修复或补充证据后，应能够针对新 Candidate 或更新后的 Candidate 再次执行 Gate2 并重新计算 Verdict。

---

## 21. V1 最小实现架构

```text
                  Gate2 Skill
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 Baseline Reader  Candidate Reader  Tool Result Reader
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                Gate2 Context
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Implementation   Verification      Impact
   Checker          Checker          Checker
        │              │              │
        └──────────────┼──────────────┘
                       ▼
              Engineering Checker
                       │
                       ▼
             Candidate Readiness
                       │
                       ▼
               Evidence Engine
                       │
                       ▼
               Finding Engine
                       │
                       ▼
                Policy Engine
                       │
                ┌──────┴──────┐
                ▼             ▼
               PASS          BLOCK
                       │
                       ▼
                 Gate2 Report
```

---

## 22. 核心数据关系

Gate2 的最核心关系不是“检查若干孤立对象”，而是建立以下可追溯链路：

```text
Requirement
   │
   ├────────────→ Implementation
   │                  │
   │                  ▼
   │                Diff
   │
   ├────────────→ Verification
   │                  │
   │                  ▼
   │                Test
   │                  │
   │                  ▼
   │                Result
   │
   └────────────→ Evidence
                      │
                      ▼
                    Finding
                      │
                      ▼
                    Policy
                      │
                      ▼
                    Verdict
```

Gate2 V1 的实现应围绕这条链路组织，而不是把 Build、Test、Scanner、LLM Review 做成彼此独立的检查脚本集合。

---

## 23. 一句话定义

> **Gate2 的核心不是再增加一轮测试，而是建立“需求意图 → 实际实现 → 验证证据 → 风险 → 准出结论”的自动闭环，让 Feature 在进入用户验收之前，研发侧先完成一次有证据的工程验收。**
