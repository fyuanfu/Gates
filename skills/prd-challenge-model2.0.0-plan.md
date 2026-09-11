# PRD Challenge Model 2.0.0 · RGQ 实施 Plan

## 1. 目标与边界

将现有 `prd-challenge-model` 演进为一套可执行的 Requirement Quality Gate（RGQ），在已经批准的产品目标与范围内检查需求质量，并保持原有 Challenge、Disproof、Evidence、Severity、Completion Guard 与确定性 Verdict 能力。

RGQ 只评审需求行为质量，不评审产品价值、优先级、ROI、范围选择、技术可行性、架构、API、数据库或代码。Scope Snapshot 是输入约束，不是评审对象。

质量检查覆盖六个域：

1. Coverage：范围内的行为、场景、规则和异常是否完整；
2. Robustness：失败、恢复、边界、状态、时序、数据、权限和并发能否打破需求；
3. Clarity：是否存在会产生不同实现或验收结果的歧义；
4. Consistency：局部规则和全局关键决策是否冲突；
5. Verifiability：关键行为是否有可观察结果和确定性判定规则；
6. Traceability：Requirement、Behavior、Rule/Constraint/NFR 与 Verification 是否闭环。

## 2. 方案 Review 后的调整

| 原建议 | Review 结论 | 2.0.0 决策 |
|---|---|---|
| 新建独立 RGQ Skill | 与现有 Skill 高度重叠 | 不新建，增量升级 `prd-challenge-model` |
| Intent & Scope Review | 已进入价值层 | 删除；只记录 `scope_snapshot` |
| 完整 Requirement Knowledge Graph | 成本高且容易制造伪精度 | 使用最小 Typed Slice Relations |
| 一个 Requirement 一个单值角色 | AC 可能同时定义与验证行为 | Binding 使用去重的 `roles[]` |
| 所有 Rule/NFR 都必须连到 Behavior | 明确的全局规则会产生误报 | 支持有证据的 `traceability_exemption` |
| Testability 布尔值即可 | 无法沉淀可验收的 Oracle | 增加 Verification Profile |
| Open Question 可阻塞执行 | 混淆产品未决与评审失败 | Question 不触发 incomplete；执行问题才触发 |
| 全量加载平台风险库 | 增加成本并诱发越界问题 | Android 明确在范围内且风险信号命中才加载 |

## 3. Canonical Model 2.0.0

### 3.1 输入身份

- Artifact 保存精确字节的 `content_sha256` 与可选 `source_version`；
- `review_context` 保存 Skill 版本、Scope Snapshot 和 Input Fingerprint；
- Input Fingerprint 由 Scope Snapshot 与按 ID 排序的 Artifact 哈希确定性生成；
- 旧 1.x JSON 不静默兼容，必须重新执行 Review。

### 3.2 Typed Slice Relations

- `requirement_bindings`: `requirement_id + roles[]`；
- 支持角色：定义行为、验证行为、定义状态、规则、约束或 NFR；
- `cross_slice_links`: `USES_RULE`、`SUBJECT_TO_CONSTRAINT`、`SUBJECT_TO_NFR`、`RELATED_BEHAVIOR`；
- 校验器验证引用存在、目标 Slice 类型匹配、禁止自引用和重复绑定；
- 只有源需求明确给出全局适用范围时，Rule/Constraint/NFR 才可使用 `traceability_exemption`；BEHAVIOR 不得豁免。

### 3.3 Behavior Coverage Map

每个完成 Fast Scan 的 BEHAVIOR Slice 必须且只能各评估一次：

`ACTOR / TRIGGER / PRECONDITION / SUCCESS / FAILURE / RECOVERY / STATE / FEEDBACK`

状态为 `DEFINED / PARTIAL / MISSING / NOT_APPLICABLE`，并关联 Requirement IDs 和理由。Coverage Gap 只是 Candidate；只有产生允许的下游后果且通过 Disproof 才形成 Finding。

### 3.4 Verification Profile

每个完成 Fast Scan 的 Slice 必须给出：

- `status`: COMPLETE / PARTIAL / MISSING / NOT_APPLICABLE；
- `basis`: EXPLICIT_SOURCE / NORMALIZED_FROM_SOURCE / ABSENT / NOT_APPLICABLE；
- 条件、可观察预期结果、判定规则；
- 缺失元素与证据 Requirement IDs。

只允许从源需求提取或等价规范化，不允许替产品方创造 Oracle。NFR/Constraint 继续使用 Measurement Profile 检查条件、环境、起止点和阈值。

### 3.5 Traceability Guard

追踪关系保存在 typed bindings/links 中；下列 Gap 由校验/渲染阶段动态派生，不在 JSON 中重复持久化：

- Behavior 缺少定义来源；
- AC 未验证任何 Behavior；
- Behavior Verification 不完整；
- Rule/Constraint/NFR 未被 Behavior 使用且没有合法全局豁免。

派生 Gap 仍是 Candidate，不自动构成 Finding。Traceability Guard 未运行属于执行失败并产生 `review_incomplete`。

## 4. 固定执行流水线

按以下阶段执行，不能以空 Findings 代替完成证明：

1. 固化调用参数与 Scope Snapshot；
2. 计算 Artifact Hash 与 Input Fingerprint；
3. 解析 Artifact 并建立 Artifact Index；
4. 提取原子 Requirement 并建立 Requirement Index；
5. 构建 Typed Review Slices；
6. 校验 Slice Integrity；
7. 构建 Behavior Coverage Map；
8. 执行 Clarity 与 Local Consistency；
9. 执行 Testability 与 Verification Review；
10. 对每个 Slice 执行 Minimal Challenge；
11. 执行 Global Critical Decision Guard；
12. 按信号选择风险模式；
13. 仅对命中信号的 Slice 执行 Deep Challenge；
14. 映射允许的下游后果；
15. 过滤增强建议、偏好、技术建议和无证据猜测；
16. 主动搜索反证；
17. 完成 Candidate 生命周期分类；
18. 执行 Traceability Guard；
19. 去重并按 P0～P3 定级；
20. 执行 Completion Guard；
21. 生成并校验 `review.json`；
22. 确定性 adjudicate、复验并渲染 `review.md`。

## 5. Verdict 与问题语义

- `review_incomplete`: 只由阻塞的执行问题产生，例如输入缺失、解析失败、Requirement 未分配、完整性未解决、必要阶段未执行、指纹无效、校验或渲染失败；
- `review_failed`: 已完成评审且存在 P0/P1 Finding；
- `review_passed`: 已完成评审且不存在 P0/P1 Finding；允许存在 P2/P3、Observation 和 Open Question；
- answer-required Open Question 必须关联已确认 Finding，不能代替 Finding，也不能使已完成评审变成 incomplete。

## 6. 风险挑战扩展

核心风险族增加 Data Effect、Permission 与 Concurrency，同时保留状态、时序、失败、恢复、依赖、边界、部分成功和重复动作等能力。

Android 风险库独立存放，并同时满足以下条件才加载：

1. 产品范围明确为 Android；
2. 行为包含相应平台依赖；
3. 命中相应确定性风险信号。

平台风险用于挑战产品行为，不用于提出实现方案或扩大设备、OS、OEM 支持范围。

## 7. 输出与可审计性

- `review.json` 保存完整机器可读矩阵和证据；
- `review.md` 只渲染关键缺口、Verification Readiness、Traceability Gaps、Findings、Questions 和 Execution Issues；
- P0/P1 必须有 Failure Witness 或 Contradiction Proof；
- 每个 Finding 都必须引用原文、关联 Requirement/Slice、完成规定强度的 Disproof；
- Verdict 只能由脚本根据 Canonical Model 生成。

## 8. 验证计划与准出标准

### 确定性 Contract Tests

- 既有 11 个 Fixture 全部通过；
- Schema 版本与根对象封闭；
- Input Fingerprint、防悬空引用、重复 ID、Coverage 汇总、Verification 完整性；
- Typed Link 目标类型、BEHAVIOR 禁止 Traceability 豁免；
- 未运行 Traceability Guard 时 fail-closed；
- Open Question 与 Execution Issue 的语义分离；
- 两个风险库结构与按需启用规则；
- Renderer 固定章节顺序；
- Semantic Evaluator 自测。

### 语义 Forward Evals

`evals/cases` 提供 12 个不向 Reviewer 暴露预期答案的用例，覆盖假成功、失败恢复、确定性 Oracle、模糊成功定义、行为无 AC、孤儿 AC、全局规则免误报、权限拒绝/撤销、Android 进程恢复、明确 Out-of-Scope、纯技术输入和完整无缺陷需求。

每个结果必须先通过 Contract Validator，再由 `scripts/evaluate_semantics.py` 检查 Verdict、必须发现、禁止误报和最大 Finding 数。

### Release Gate

发布前必须同时满足：

1. `scripts/run_contract_tests.py` 全部通过；
2. 所有 Python 脚本可编译；
3. `quick_validate.py` 通过 Skill 结构校验；
4. 至少对高风险缺陷用例和干净用例执行独立前向评测；
5. Branch diff 只包含 `skills/prd-challenge-model/**` 与本 Plan；
6. 目标分支基于提交时确认的 `main`，使用非强制 ref 更新。

## 9. 实施清单

- [x] Schema 与 Canonical Model 升级为 2.0.0
- [x] Artifact Hash、Scope Snapshot 与 Input Fingerprint
- [x] Typed Bindings、Cross-Slice Links 与受控 Traceability Exemption
- [x] Behavior Coverage Map
- [x] Verification Profile
- [x] Traceability Guard 与派生 Gap
- [x] Open Question / Execution Issue 语义修正
- [x] Data、Permission、Concurrency 核心风险族
- [x] Android 条件风险库
- [x] Workflow、Prompts、Contracts、Renderer 与入口说明
- [x] Deterministic Contract Tests
- [x] 12 个 Semantic Eval Cases 与 Evaluator
- [x] 独立 Forward Eval 通过（SEM-001 高风险缺陷、SEM-012 干净样本）
- [x] 最终验证通过并提交到 `prd-challenge-model2.0.0`
