# DR-0003：引入 Universal Converge 实现收敛门禁

- **Status**: Accepted
- **Date**: 2026-09-04
- **Owners**: Gates maintainers
- **Related**: `skills/universal-converge/`

## 1. Context

Gates 已包含需求挑战和缺口发现能力，但交付阶段仍需要一个独立、只读的证据闭环门禁，回答“当前实现是否已经收敛到已确认的产品与工程意图”。该门禁必须适配不同仓库的 Artifact 结构，并避免把任务完成状态、符号命名、测试源码存在或模型推导当成行为已满足的证明。

## 2. Decision

在 `skills/universal-converge/` 引入 Universal Converge Skill，并采用以下执行契约：

1. 从已接纳的 Requirement、Acceptance Criteria、Rule、Invariant、Contract 和 approved engineering decision 中提取原子化 Verification Claim。
2. 对每个 material claim 追踪 design allocation、implementation/configuration/schema、verification source/result 和 counter-evidence。
3. Finding 类型固定为 `MISSING`、`PARTIAL`、`CONTRADICTS`、`UNVERIFIABLE`、`UNTRACEABLE`、`UNREQUESTED`；layer 固定为 `intent`、`design`、`implementation`、`behavior`、`traceability`。
4. Gate Verdict 固定为 `PASS`、`PASS_WITH_WARNINGS`、`BLOCK`，按确定性优先级计算，不使用平均分或多数表决。
5. 权威意图采用显式准入；文件名、目录、任务状态、实现现状或新旧顺序本身不建立权威性。零个 `REQUIRED` / `APPROVED` claim 时必须 fail closed 为 `BLOCK`。
6. Skill 对被审查系统保持只读；可以按请求创建新的 Converge 报告，但不自动修改输入 Artifact 或实施修复。

## 3. Rationale

- Claim 将产品语言转换为可独立判定的义务，同时保持实现中立。
- Positive evidence 与 counter-evidence 的双向搜索减少“看起来实现了”的误判。
- 权威准入和零 Claim 失败关闭避免空集合产生虚假的 `PASS`。
- 将复杂规则放入 `references/`，使主 Skill 保持可导航，同时保留规范化的证据、finding 和报告契约。
- 将验证缺口归入 `traceability`，与 Gates 的五层 Finding 模型保持一致。

## 4. Alternatives Considered

### 方案 A：仅依赖 Task、PR 描述或完成标记

- 优点：执行成本低。
- 缺点：不能证明接受条件、异常路径或工程约束真实成立。
- 未采用原因：Work Artifact 只适合导航和旁证，不能作为 Intent 或 behavior proof。

### 方案 B：只检查测试是否存在或通过

- 优点：结果易于自动化。
- 缺点：测试可能遗漏条件、oracle 不充分或与当前 revision 无关。
- 未采用原因：无法覆盖 design allocation、implementation path 和 counter-evidence。

### 方案 C：发现缺口后由同一 Skill 自动修复

- 优点：表面流程更短。
- 缺点：审查者同时改变被审查对象，会破坏门禁独立性并扩大权限。
- 未采用原因：Converge 保持只读，修复交给后续独立工作流。

## 5. Consequences

### 正向影响

- Gates 获得从 accepted intent 到 evidence、finding 和 gate verdict 的统一交付门禁。
- 结论可以追溯到稳定 source、claim 和 evidence 位置。
- 不同 Artifact 命名和工程流程可以复用同一 Skill。

### 成本 / 风险

- 高风险 claim 必须执行正向与反向证据搜索，审查成本高于关键词匹配。
- 缺少权威状态、实现 Artifact 或必要证据时会保守地 `BLOCK` 或产生 warning。
- 大范围审查需要严格控制 scope 和上下文加载。

## 6. Affected Artifacts

- `skills/universal-converge/SKILL.md`
- `skills/universal-converge/references/artifact-and-claim-model.md`
- `skills/universal-converge/references/evidence-model.md`
- `skills/universal-converge/references/findings-and-verdict.md`
- `skills/universal-converge/references/report-contract.md`
- `skills/universal-converge/agents/openai.yaml`
- `skills/universal-converge/assets/icon.svg`
- `docs/decisions/README.md`

## 7. Supersession

- **Supersedes**: None
- **Superseded by**: None
