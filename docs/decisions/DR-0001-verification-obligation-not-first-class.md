# DR-0001：Verification Obligation 不作为 V1 一等追溯对象

- **Status**: Accepted
- **Date**: 2026-08-25
- **Owners**: Gates 项目
- **Related**: `docs/quality-gate-knowledge-overview-v0.1.md` §4.2、§5、§15

## 1. Context

当前 `quality-gate-knowledge-overview-v0.1.md` 的需求与验证主链中存在：

```text
Requirement Object
        ↓
Verification Obligation
        ↓
Test
```

但 Gates 当前 Canonical Requirement Source、对象模型、示例和追溯文件中都没有把 `Verification Obligation` 定义为一个可落盘的一等对象，也没有定义：

- 独立 ID；
- Schema；
- 生命周期；
- 创建者；
- 与 AC / Scenario / Rule / Transition / Invariant 的确定关系；
- Test 应直接关联 Requirement 还是关联 Verification Obligation。

因此它在当前 V1 中增加了新的概念和追溯成本，却没有提供与复杂度匹配的独立价值。

## 2. Decision

V1 **不将 `Verification Obligation` 建模为独立 Traceability Object**。

需求与验证主链采用：

```text
Requirement Object
    ↓ verified-by
Test / Verification Activity
    ↓ produces
Execution / Evidence
    ↓ supports
Finding / Verdict
```

其中：

- AC、Scenario、Rule、Transition、Invariant 等 Requirement Object 共同定义“需要验证什么”；
- Test / Verification Activity 定义“如何验证”；
- Evidence 定义“验证实际得到什么”；
- Gate Policy 基于 Requirement、Evidence、Finding 和风险作出 Verdict。

`Verification Obligation` 只保留为**解释性概念**：它表示“某个 Requirement 为被认为满足而必须得到证明的内容”，但当前不拥有独立 ID、Schema、存储位置或生命周期。

Gate1 不要求 Test Implementation 或 Test Execution 已经存在，但必须保证关键 Requirement 已达到可验证状态：预期结果、Oracle、边界和必要契约足够明确，使后续验证活动无需重新发明业务语义。

## 3. Rationale

1. 当前 AC / Scenario / Rule / Transition / Invariant 已经承担需求和验证目标的语义来源职责。
2. Test 可以通过稳定 Requirement ID 直接建立 `verified-by` / `covers` 关系。
3. 新增 Verification Obligation 会引入新的 ID、Schema、生成、维护和双层映射成本。
4. 当前没有证据证明该独立节点能显著提升 Gate1/Gate2/Gate3 的自动化、影响分析或审计能力。
5. V1 的原则是先建立最小、可执行、可解释的追溯链，而不是提前构建完整知识图谱。

## 4. Alternatives Considered

### 方案 A：Verification Obligation 作为独立一等对象

优点：

- 可以显式区分 `what is required` 与 `what must be proven`；
- 未来可能支持自动生成 Verification Plan、形式化验证或多种 Verification Activity 聚合。

缺点：

- 当前没有稳定 Schema 和生命周期；
- 与 AC / Scenario / Rule 的职责边界容易重叠；
- Test 关联关系增加一跳；
- 增加团队认知和 Agent 处理复杂度。

**未采用。** 当前收益不足以覆盖复杂度。

### 方案 B：删除概念且不保留解释

优点：模型最简单。

缺点：无法表达“Requirement 必须具有可验证性和明确 Oracle”这一重要设计思想。

**未采用。** 保留为解释性概念更合适。

## 5. Consequences

### 正向影响

- 主链减少一个没有工程落点的节点；
- Test 可以直接引用 Requirement Object；
- Gate1 的职责更清晰：检查 Requirement 是否 Engineering Ready / Verifiable，而不是要求生成新的 VO 对象；
- 降低 Canonical Schema 和 Traceability Model 的维护成本。

### 成本 / 风险

- 如果未来需要统一表达非 Test 型验证活动或形式化 proof obligation，当前模型可能需要再次引入独立 Verification Requirement / Obligation 对象；
- 若重新引入，必须通过新的 DR 明确其独立语义、ID、Schema、Owner、生命周期和收益。

## 6. Affected Artifacts

- `docs/quality-gate-knowledge-overview-v0.1.md`
- 后续 Gate1 Traceability 规则
- 后续 Test / Verification Activity 追溯关系

`examples/feature-stories.example.yaml` 不需要增加 Verification Obligation 字段。

## 7. Supersession

- **Supersedes**: Overview 中将 Verification Obligation 作为 V1 一等节点的旧表述
- **Superseded by**: None
