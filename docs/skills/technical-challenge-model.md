# Technical Challenge Model V1 — 生产级 Skill 实现规格

> 状态：Implementation Baseline / PILOT until semantic holdout validation  
> Skill：`technical-challenge-model`  
> 目标：在实现开始前，以已确认需求行为与现有系统约束为锚点，挑战 Technical Design 是否能够正确成立。

## 1. 使命

本 Skill 不回答“这个架构是否更优雅”，而回答：

> 该技术方案在真实系统约束和合理技术失败条件下，是否能够完整、正确地实现已接受的行为义务，并保持既有系统必须维持的约束？

核心链：

```text
RequirementObligation + SystemConstraint
                ↓
          DesignDecision
                ↓
            Mechanism
                ↓
              Claim
       (precondition is a kind)
                ↓
         Counterexample
                ↓
      Evidence Resolution
                ↓
             Finding
```

固定原则：

1. Requirement Anchored
2. System-Constraint Aware
3. Decision Centered
4. Preconditions First
5. Counterexample + Evidence Driven

## 2. 与 PRD Challenge 的边界

PRD Challenge 定义 **What behavior should exist?**

Technical Challenge 验证 **Can this design actually guarantee that accepted behavior?**

Technical Challenge MUST NOT：

- 发明新产品行为；
- 用技术偏好替代缺陷证据；
- 把 implementation-independent 的业务异常重新包装成技术 Finding；
- 因当前代码没有一个 `planned` mechanism 就判定设计缺失；
- 因历史 Bug 曾发生就判定当前设计仍有相同缺陷。

## 3. 核心语义对象

### 3.1 RequirementObligation

来源于已接受的 PRD / AC / Scenario / Rule / State / Invariant / NFR。Technical Challenge 只能消费，不得新增产品含义。

### 3.2 SystemConstraint

描述当前变化必须继续保持的 Brownfield 约束。

Authority：

```text
verified | curated | inferred
```

只有 `verified` / `curated` 可直接锚定正式 Finding。 `inferred` 必须先验证；未验证时只能形成 EvidenceGap/OpenDecision 或 Challenge Seed。

### 3.3 DesignDecision

改变该决策会显著改变系统行为、状态模型、数据一致性、依赖、质量属性或失败模式的架构/设计选择。

### 3.4 Mechanism

Decision 的具体实现机制。必须标记：

```text
existing | planned | modified | removed
```

证据使用必须随生命周期变化。

### 3.5 Claim

所有需要证据判断的技术陈述统一使用 Claim：

```text
precondition | design-guarantee | existing-system-fact |
platform | api | performance | compatibility
```

**Precondition 是 Claim kind，不创建第二套 Precondition 实体。**

### 3.6 Counterexample

针对关键 Claim 的实现相关反例。它必须描述具体技术 Mutation、Failure Path 和潜在违反的 Requirement/SystemConstraint。

### 3.7 Evidence

Evidence 不做全局强弱排序；根据 Claim 类型判断 adequacy。

### 3.8 Finding 与三类非 Finding 输出

输出分开：

```text
Technical Finding
RequirementGap
EvidenceGap
OpenDecision
```

不得互相替代。

## 4. Design Stage

输入必须标识：

```text
architecture | high_level | detailed
```

| Stage | Challenge Depth |
|---|---|
| architecture | 边界、主要决策、依赖、状态所有权、质量/故障策略 |
| high_level | 组件职责、协议、状态/持久化、恢复、兼容、主要并发语义 |
| detailed | 状态转换、顺序、事务边界、retry、key lifecycle、migration、并发 guard |

不得用 LLD 标准评审 HLD/Architecture。

## 5. 两条正式 Finding Path

### 5.1 Coverage Finding

```text
Accepted Obligation / verified-or-curated Constraint
→ Coverage MISSING / CONTRADICTED
→ appropriate evidence
→ DESIGN_COVERAGE_GAP / DESIGN_CONTRADICTION
```

Counterexample 不是必需项。

### 5.2 Counterexample Finding

```text
Decision
→ Mechanism
→ critical Claim
→ plausible Counterexample
→ Obligation/Constraint violation
→ appropriate evidence
→ Technical Finding
```

该路径必须引用 `claim_id` 与 `counterexample_id`。

## 6. Coverage

状态：

```text
COVERED | PARTIAL | MISSING | CONTRADICTED | UNCLEAR
```

先做 Coverage，再做深度 Challenge。显式行为没有任何 mechanism 时，应直接发现 Coverage Gap，而不是为了形式强造 Counterexample。

## 7. Counterexample Search

Mutation Library：

```text
Duplicate
Delay
Drop
Reorder
Restart
Partial Success
Stale State
Concurrent Execution
Dependency Degradation
```

执行：

1. 选择关键 Claim；
2. 否定该 Claim；
3. 选择一个技术上合理的 Mutation；
4. 沿相关 Mechanism 传播；
5. 观察 resulting state；
6. 检查是否违反 Requirement/SystemConstraint；
7. 使用匹配 Claim 类型的证据确认或反驳。

## 8. Evidence Policy

| Claim | Appropriate Evidence |
|---|---|
| platform | 官方平台契约 + 必要时 focused test |
| existing-system-fact | 当前代码/runtime/static analysis |
| api | API contract / server implementation |
| performance | benchmark/load measurement |
| failure recovery | fault-injection/recovery test 或权威契约 |
| compatibility | schema/version contract/migration test |
| planned design guarantee | Technical Design + compatible external contracts |

Mechanism lifecycle：

- `existing`：当前代码/runtime 是主要证据；
- `planned`：当前代码不存在不是反证；
- `modified`：必须同时检查 existing behavior 与 proposed delta；
- `removed`：必须检查现存 dependents 和 removal impact。

“搜索没找到”只能表述为 searched scope 中未找到 supporting evidence，除非搜索范围具有 authoritative/exhaustive 证明力。

## 9. Gap 和 Gate 语义

### RequirementGap

产品期望行为本身未定义。不能由 Technical Challenge 决定。

### EvidenceGap

关键事实/设计 Claim 未得到适当证据支持。

`critical=true` 仅当当前 Design Stage 的 Gate 必须依赖该 Claim 才能审批。Critical EvidenceGap 可以阻断 Gate，但仍保持为 EvidenceGap，不升级成伪 Finding。

### OpenDecision

产品行为和事实都足够，但 Architecture Owner 尚未在已知可行替代方案中做出必要选择。

## 10. Severity、Verdict 与 Assurance

Finding Severity：

```text
BLOCKER | HIGH | MEDIUM | LOW
```

Verdict：

```text
BLOCKED | NEEDS_DECISION | PASS_WITH_ACTIONS | PASS
```

当前确定性 adjudication：

```text
BLOCKER Finding 或 critical EvidenceGap -> BLOCKED
blocking RequirementGap/OpenDecision -> NEEDS_DECISION
其他 Finding/EvidenceGap/OpenDecision -> PASS_WITH_ACTIONS
否则 -> PASS
```

Assurance：

```text
DOCUMENT_ONLY
CONTEXT_GROUNDED
REPOSITORY_GROUNDED
EVIDENCE_VERIFIED
```

Verdict 表示评审结论；Assurance 表示结论的证据强度。Document-only PASS 不能被解释为已通过运行时验证。

## 11. Brownfield Context

检索必须由 Claim 驱动：

```text
Level 1: Design 显式引用的 module/symbol
Level 2: Decision direct dependencies
Level 3: 支持/反驳当前 Claim 的 targeted retrieval
```

Feature Tree、Historical Requirement、Bug、RiskPattern 用于：

- 找 Existing SystemConstraint 候选；
- 选择 Challenge Lens；
- 提醒兼容/演进风险。

它们本身不是当前 Finding 的证明。

## 12. Android Profile

Android 专项知识只在 Mechanism 命中时加载。覆盖 WorkManager、Room/SQLite、Coroutine/Flow、Connectivity、Binder、Background execution、persisted state、permission/storage 等平台失败模式。

不得把 Android profile 退化成固定 Checklist。

## 13. Canonical Output

`report.json` 是唯一 Canonical Model；`report.md` 只从已验证 JSON 确定性渲染。

固定集合：

```text
obligations
system_constraints
decisions
mechanisms
claims
coverage
counterexamples
evidence
findings
requirement_gaps
evidence_gaps
open_decisions
```

不得单独维护 `preconditions[]`。

## 14. Deterministic Tooling

V1 scripts：

```text
validate_report.py
adjudicate_report.py
render_report.py
run_contract_tests.py
```

Eval scripts：

```text
prepare_case.py
validate_dataset.py
score_case.py
aggregate_results.py
```

Validator 负责 Draft 2020-12 结构子集和 cross-reference/domain invariant；Verdict 由脚本确定，不由 prose 自由判断。

## 15. Evaluation Contract

Dataset 固定拆分：

```text
20 Dev
10 Holdout
```

覆盖至少：

- 3 Design Stages；
- 4 Mechanism Lifecycles；
- coverage/idempotency/concurrency/ordering/lifecycle/atomicity/persistence/dependency/compatibility/migration/architecture-conformance；
- Finding / RequirementGap / EvidenceGap / OpenDecision / PASS；
- 主要 Claim kinds。

### Isolation

Review Agent sandbox 只能看到：

```text
SKILL.md
references/
selected case input.md
selected explicit context/
```

禁止暴露：

```text
expected answer
other cases
prior outputs
aggregate scores
```

### Expert Oracle

未出现在 expected answer 中的 Finding 不自动视为 False Positive，必须专家裁决：

```text
valid | invalid | duplicate | unverifiable
```

专家裁决未闭环时，不得宣称真实 Finding Precision。

### Holdout

Dev 用于 RED/GREEN/REFACTOR。Holdout 只能在 Skill wording 冻结后用于 acceptance。若因 Holdout 失败而修改 Skill，则该 Holdout 已泄漏，必须移入 Dev 并换新 unseen case。

## 16. Release Status

当前运行环境缺少 fresh-context/subagent/model runner，因此 V1 可以完成 deterministic contract implementation，但不能在本环境真实执行 5x fresh semantic RED/GREEN 和 holdout semantic acceptance。

在完成该验证前：

```text
release_status = PILOT
```

禁止声称 Recall/Precision 阈值已经得到验证。

## 17. Definition of Done

结构实现完成必须满足：

- Skill 和所有 references 存在；
- SKILL.md 保持紧凑并且 frontmatter 只描述 trigger；
- report schema + cross-reference validator 通过；
- 两条 Finding Path 有确定性测试；
- Design Stage 有 dataset 覆盖；
- planned/existing/modified/removed 有证据规则；
- inferred constraint 不能直接支持 Blocker；
- Dev/Holdout 隔离脚本有测试；
- 30 case dataset contract 通过；
- deterministic contract tests 全绿；
- Semantic fresh-context acceptance 未完成时状态只能为 PILOT。
