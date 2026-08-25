# DR-0002：Task 以 Story 为主归属，并用 Requirement Coverage Review 保证实现完整性

- 状态：Accepted
- 日期：2026-08-25
- Related：`quality-gate-knowledge-overview-v0.1.md` §3.2、§4.3、§5.6；`examples/tasks.example.md`

## 背景

当前 Canonical Requirement Source 已形成 `Feature → Story → AC / Scenario / Rule / Transition / Invariant` 的需求结构。进入实现规划后，需要确定 Engineering Task 应关联到 Story 还是 Scenario，以及如何避免 Task 按 Story 组织后遗漏具体 Scenario / Rule / AC。

需要同时满足两个目标：

1. Task 的工程归属关系简单、稳定，符合常见敏捷 / SDD 工作分解；
2. 实现规划不能因为 Task 只挂 Story 而忽略 Story 下的 Required Scenario、AC、Rule 等行为要求。

## 决策

### 1. Task 的主归属关系为 Story

Story-specific Task 必须直接引用所属 Story ID：

```text
Story ── implemented-by ──> Task
```

Scenario 不作为 Task 的父级，也不要求建立 `Scenario → Task` 的 1:1 分解。

Setup、Foundational、Cross-cutting 等跨 Story Task 可以不绑定单一 Story，但必须明确其作用范围。

### 2. Task Planning 必须消费完整 Requirement Object

生成 / Review Tasks 时，不能只读取 Story 标题或 `i_want`，必须同时考虑该 Story 下所有 Required：

- Acceptance Criteria；
- Scenario；
- Rule；
- Transition / Invariant（存在时）；
- 适用 NFR / Contract（存在时）。

### 3. 在 Task 生成后、编码开始前执行 Requirement → Implementation Coverage Review

Coverage Review 检查每个 Required Requirement Object 是否：

- `COVERED`：有一个或多个 Task 明确覆盖；
- `REUSED_EXISTING_BEHAVIOR`：无需新增 Task，但明确复用已有实现，并能定位复用对象；
- `OUT_OF_SCOPE`：仅当 Canonical Requirement Source 已明确标记为本次范围外时成立；
- `GAP`：没有实现覆盖、没有可定位的既有实现，也不属于范围外。

未解释的 Required `GAP` 不应进入编码。

Coverage View 是 Review 的派生结果，不成为新的 Requirement Source。

### 4. Scenario → Task 只允许作为可选辅助关系

如影响分析、实现导航确有价值，可在 Task 或派生 Trace 中记录：

```text
Task ── supports ──> Scenario / AC / Rule
```

该关系为 N:M 的辅助追溯关系，不替代 `Task → Story` 主归属，也不要求每个 Task 强制填写。

### 5. 验收不承担正常补齐已知需求遗漏的职责

Gate3 / Acceptance 仍负责验证实际产品行为，但如果一个开发前已知且 Required 的 Scenario 到验收阶段才发现完全没有实现，应视为 Planning / Implementation Coverage 的逃逸，而不是正常需求补全流程。

## 采用理由

### 与 spec-kit 的任务组织方式一致

GitHub spec-kit 的 `tasks.md` 生成规则明确以 User Story 作为 Task 的主要组织维度，并要求 Story phase 的 Task 带 Story label；同时要求验证每个 User Story 是否拥有完成该 Story 所需的全部 Task、能够独立实现和验证。

参考：
- https://github.com/github/spec-kit/blob/main/templates/commands/tasks.md
- https://github.com/github/spec-kit/blob/main/templates/tasks-template.md

### 与 BDD / Example Mapping 的职责划分一致

Cucumber Example Mapping 在 Story 进入开发前，通过 Rule / Acceptance Criteria 与具体 Example 澄清 Story 的范围。这些 Example 用于理解行为和形成 Acceptance Test，而不是作为工程 Task 的父级。

参考：
- https://cucumber.io/docs/bdd/example-mapping/

### Scenario 与 Task 天然不是 1:1

一个 Task 可能同时支持多个 Scenario；一个 Scenario 也可能需要多个 Task。强制 `Scenario → Task` 父子结构会把 N:M 的追溯关系错误建模成工作分解层级。

## 未采用方案

### 方案 A：Task 只关联 Story，实现阶段不检查 Scenario / AC / Rule

未采用。会使 Task 组织简洁，但容易让具体行为分支在实现规划中消失，把已知需求遗漏推迟到验收阶段。

### 方案 B：Task 强制以 Scenario 为父级

未采用。Scenario 是行为实例，Task 是实现活动，两者不是稳定父子关系；会导致重复 Task、跨 Scenario 共用 Task 难以表达，并增加维护成本。

### 方案 C：每个 Task 强制关联 Story + 全部 Scenario

未采用。精细关系有时有价值，但对 Setup / Shared / Cross-cutting Task 和大量 N:M 情况成本过高。V1 保留 `supports` 为可选辅助关系，由 Coverage Review 保证完整性。

## 影响

### 修改

- `docs/quality-gate-knowledge-overview-v0.1.md`
  - §3.2 Task 定义；
  - 新增 §4.3 需求与实现主链；
  - 原 Change Safety / 最小追溯章节顺延；
  - 新增 Task 生成后、编码前的 Implementation Plan Coverage Review；
  - Gate3 明确“验收不是正常补漏机制”。
- 新增 `examples/tasks.example.md`。
- Decision Record Check 将 `examples/tasks.example.md` 纳入核心知识保护范围。

### 不修改

- `examples/feature-stories.example.yaml` 不增加 Task 字段；Engineering Task 继续位于 Canonical Requirement Source 之外。
- 不要求 Gate1-R 在 Requirement Ready 阶段必须已有 Task；Coverage Review 发生在 Task 生成后、编码开始前。
