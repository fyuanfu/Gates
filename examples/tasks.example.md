# Tasks Example：笔记回收站

> Requirement Source：`examples/feature-stories.example.yaml`  
> Decision：`DR-0002`  
> 规则：Story-specific Task 必须引用 Story ID；Scenario / AC / Rule 不作为 Task 父级。Task Planning / Review 必须覆盖 Story 下全部 Required Requirement Object。

## Phase 1：Setup / Shared

- [ ] T001 配置回收站 Feature 模块基础结构（Shared，无单一 Story 归属）

## Phase 2：US-NOTE-017 恢复删除的笔记

**Story：`US-NOTE-017`**

- [ ] T002 [US-NOTE-017] 实现 `RestoreNoteUseCase`，协调恢复流程
- [ ] T003 [US-NOTE-017] 实现原目录存在时恢复到原目录、原目录不存在时 fallback 到默认目录的 Repository / Domain 逻辑
- [ ] T004 [US-NOTE-017] 更新恢复成功后的 UI / State，使笔记重新处于可使用状态

### Implementation Coverage Review（派生视图，不是 Requirement Source）

| Requirement | Status | Implementation Coverage |
|---|---|---|
| `US-NOTE-017-AC01` | COVERED | T002, T004 |
| `US-NOTE-017-AC02` | COVERED | T002, T003 |
| `US-NOTE-017-R01` | COVERED | T003 |
| `US-NOTE-017-S01` | COVERED | T002, T003, T004 |
| `US-NOTE-017-S02` | COVERED | T002, T003, T004 |

说明：上表用于 Review “实现计划是否覆盖完整需求”，不要求把每个 Scenario ID 永久写入每个 Task。若后续影响分析需要，可增加可选 `supports` 关系。

## Phase 3：US-NOTE-018 永久删除笔记

**Story：`US-NOTE-018`**

- [ ] T005 [US-NOTE-018] 实现永久删除确认流程
- [ ] T006 [US-NOTE-018] 实现确认后的永久删除 Repository / Storage 操作
- [ ] T007 [US-NOTE-018] 实现取消删除并保持笔记位于回收站的 UI / State 行为

### Implementation Coverage Review（派生视图，不是 Requirement Source）

| Requirement | Status | Implementation Coverage |
|---|---|---|
| `US-NOTE-018-AC01` | COVERED | T005, T007 |
| `US-NOTE-018-AC02` | COVERED | T006 |
| `US-NOTE-018-S01` | COVERED | T005, T006 |
| `US-NOTE-018-S02` | COVERED | T005, T007 |

## Review Rule

Task 生成后、编码开始前，Review 至少检查：

1. 每个 Required Story 是否存在必要实现 Task；
2. 每个 Required AC / Scenario / Rule / Transition / Invariant 是否得到实现覆盖，或有可定位的既有实现复用说明；
3. Canonical Requirement Source 中仍属于 Required Scope 的对象不得用 `OUT_OF_SCOPE` 绕过；
4. 无法解释的 `GAP` 阻止进入编码；
5. Task 不得重新定义或发明 Requirement Source 中不存在的关键业务行为。

允许的 Coverage Status：

- `COVERED`
- `REUSED_EXISTING_BEHAVIOR`
- `OUT_OF_SCOPE`（仅当 Canonical Requirement Source 已明确范围外）
- `GAP`
