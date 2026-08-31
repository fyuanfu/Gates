<!-- Converted from Gate2_矩阵检查目标.html -->

# Gate2 矩阵检查目标

Feature 开发完成 → 用户 / UAT 验收前的工程准入门禁

> **总目标：** 确认 Feature 已达到用户验收的工程准入条件：批准的功能意图已经形成可工作的集成实现； 研发阶段要求完成的验证已经产生当前候选版本上的有效证据； 变更引入的回归、接口、安全和工程风险已被检查并处于允许范围； 所有阻断 Finding 已关闭或经过明确风险接受。

## 1. 检查模型总览

先把“检查对象”和“检查属性”正交拆开；Evidence、Finding、Block 是后续判定机制，不与检查对象混层。

- **Object · 检查对象 · 7**：Feature 意图、Plan、Diff、测试义务、执行结果、Candidate、Finding
- **Property · 检查属性 · 5**：一致性、完整性、验证结果、变更安全、证据有效性
- **Finding · 根 Finding · 6**：实现、验证、回归、工程、证据、开放风险
- **Block · 最高层阻断规则 · 4**：未实现、未证明、不可接受风险、Candidate 不可验收

**流程：** 需求意图（Spec / Story / AC / Rule） → 实际实现（Plan / Diff / Interfaces） → 验证体系（Obligation / Test / Result） → 交付对象（Candidate Build / Runtime） → 门禁结论（Evidence → Finding → Verdict）

## 2. Gate2 总体检查矩阵

**检查属性：** 一致性 ｜ 完整性 / 覆盖 ｜ 验证结果 ｜ 变更安全性 ｜ 证据有效性

| 层级              | 检查对象                         | ① 一致性                       | ② 完整性 / 覆盖          | ③ 验证结果                         | ④ 变更安全性                      | ⑤ 证据有效性                         |
|-------------------|----------------------------------|--------------------------------|--------------------------|------------------------------------|-----------------------------------|--------------------------------------|
| L1 / 实现忠实性   | **A. Feature 意图 / Spec / AC**  | 实现是否符合批准意图           | 所有必须需求是否都有实现 | —                                  | 是否错误改变既有语义              | 是否可追踪到实现和验证               |
| L1 / 实现忠实性   | **B. 技术方案 / Plan**           | 实际实现是否符合批准方案       | 承诺的实现项是否完成     | —                                  | 是否出现未经批准的架构 / 接口变化 | Plan 与实际 Diff 是否对应            |
| L2 / 工程安全     | **C. 实际代码变更 / Diff**       | Diff 是否服务于 Feature 目标   | 是否存在漏实现           | Build / Static / Security 是否通过 | 是否产生回归、兼容、依赖风险      | 是否能解释重要变更来源               |
| L3 / 验证充分性   | **D. 测试义务 / Test Assets**    | 测试是否验证真正的需求行为     | 必须验证项是否有测试     | 测试本身是否可执行                 | 是否覆盖主要影响面                | Requirement → Test 是否可追踪        |
| L4 / 证据有效性   | **E. 测试执行结果**              | 执行版本是否就是当前 Candidate | 必须测试是否全部执行     | Pass / Fail / Skip / Flaky         | 回归测试是否通过                  | 结果是否来自当前版本 / 正确环境      |
| L5 / 候选构建就绪 | **F. Candidate Build / Runtime** | 构建内容是否对应批准变更       | Feature 所需组件是否完整 | Build / Deploy / Smoke 是否成功    | 配置、接口、环境是否安全          | Build / Commit / Config 是否唯一对应 |
| L6 / Finding 闭环 | **G. Finding / Risk / Waiver**   | Finding 是否对应真实问题       | 阻断问题是否全部处理     | Fix 是否重新验证                   | 剩余风险是否在允许范围            | 是否有责任人、理由、审批与有效期     |

> **分层说明：**总体矩阵中的层级与后文 L1–L6 章节保持一致：L1 实现忠实性、L2 工程安全、L3 验证充分性、L4 证据有效性、L5 Candidate 就绪、L6 Finding 闭环。

> **关键约束：** AC、Rule、Scenario、Test Case 不再分别作为 Gate2 的“目标”。 它们分别是 **Feature 意图**、**验证义务** 和 **Evidence** 体系中的组成部分。

## 3. L1：实现是否忠于批准的 Feature

这一层最适合引入 LLM 做语义审计，但 LLM Finding 本身不应天然等于 Hard Block。

| 检查对象            | 检查属性          | Evidence                        | 典型 Finding                   | Block 条件                                   |
|---------------------|-------------------|---------------------------------|--------------------------------|----------------------------------------------|
| Feature / Spec / AC | 需求 → 实现一致性 | Spec / AC + Diff + Repository   | `IMPLEMENTATION_MISMATCH`      | **Hard Block：**影响 Required AC / 核心行为  |
| Feature / Spec / AC | 实现完整性        | Requirement → Code Mapping      | `MISSING_IMPLEMENTATION`       | **Hard Block：**Mandatory Requirement 未实现 |
| Feature / Spec / AC | 未声明行为变化    | Baseline Behavior + Spec + Diff | `UNAUTHORIZED_BEHAVIOR_CHANGE` | 影响既有公开行为且未批准 → Block             |
| Plan / Design       | 方案一致性        | Plan / Design + Diff            | `PLAN_DEVIATION`               | 改变接口、架构、安全等重大决策 → 条件 Block  |
| Plan / Design       | 范围一致性        | Planned Scope + Diff            | `OUT_OF_SCOPE_CHANGE`          | 高风险或语义变更未声明 → Block               |

> **LLM 在这里最适合找：**遗漏实现、错误实现、计划偏移、未经声明的语义变化、跨文件逻辑问题。

## 4. L2：实际变更是否工程上安全

这一层优先使用 deterministic tools；能交给编译器、测试器、扫描器判断的，不交给 LLM 做最终结论。

| 检查对象 | 检查属性   | Evidence                                | Finding                  | Block 条件                                         |
|----------|------------|-----------------------------------------|--------------------------|----------------------------------------------------|
| Diff     | 可构建性   | CI Build                                | `BUILD_FAILED`           | **Hard Block**                                     |
| Diff     | 静态正确性 | Compiler / Lint / Static Analyzer       | `STATIC_ERROR`           | Error / Mandatory Rule → Block                     |
| Diff     | 安全性     | SAST / Dependency / Secret Scan         | `SECURITY_FINDING`       | Critical / High 或政策阈值 → Block                 |
| Diff     | 接口兼容性 | API / Schema / Contract Diff            | `BREAKING_CHANGE`        | 未批准 Breaking Change → Block                     |
| Diff     | 架构约束   | Architecture Rules / Structural Tests   | `ARCHITECTURE_VIOLATION` | Mandatory Rule → Block                             |
| Diff     | 配置完整性 | Config / Flag / Manifest Check          | `CONFIGURATION_ERROR`    | 导致功能不可用 / 部署风险 → Block                  |
| Diff     | 影响面     | Dependency / Call Graph + LLM Reasoning | `REGRESSION_RISK`        | 本身通常不直接 Block；若缺少必须验证，则转为 Block |

## 5. L3：应该证明的东西是不是都证明了

检查对象不是“有没有 Test Case”，而是“Mandatory Verification Obligation 是否被有效验证”。

**流程：** Requirement / Risk → What must be proven? → Test Obligation → Test / Check

| 检查对象        | 检查属性      | Evidence                           | Finding                 | Block 条件                                   |
|-----------------|---------------|------------------------------------|-------------------------|----------------------------------------------|
| Test Obligation | 覆盖完整性    | Requirement / AC → Test Mapping    | `MISSING_TEST_COVERAGE` | Mandatory Obligation 无验证 → **Block**      |
| Test            | 相关性        | Test Behavior vs Obligation        | `IRRELEVANT_TEST`       | 导致 Mandatory Obligation 实际未验证 → Block |
| Test            | Oracle 有效性 | Assertion / Expected Behavior      | `WEAK_ORACLE`           | 无法证明 Required Behavior → Block           |
| Test Assets     | 可执行性      | Executable Test / Config           | `NON_EXECUTABLE_TEST`   | Mandatory Obligation 因此无法验证 → Block    |
| Regression Set  | 影响覆盖      | Impact Analysis → Regression Tests | `REGRESSION_GAP`        | 高风险影响路径无验证 → 条件 Block            |

> **重要：**“有 Test Case” ≠ “已经证明 Requirement”。如果测试只执行了动作，却没有验证关键结果，应判定为 `WEAK_ORACLE` 或 `MISSING_VERIFICATION`。

## 6. L4：测试证据是否来自当前 Candidate

Gate2 只接受“当前候选版本上的有效 Evidence”。旧版本结果、错误环境、Skip 都不能默认算 Pass。

| 检查对象       | 检查属性   | Evidence                  | Finding                 | Block                                 |
|----------------|------------|---------------------------|-------------------------|---------------------------------------|
| Test Execution | 执行完整性 | Test Run Manifest         | `NOT_EXECUTED`          | Mandatory Test 未执行 → **Block**     |
| Test Execution | 结果       | Test Result               | `TEST_FAILED`           | Required Test Fail → **Block**        |
| Test Execution | Skip       | Test Result               | `REQUIRED_TEST_SKIPPED` | Mandatory → Block                     |
| Test Execution | Flaky      | Historical + Current Runs | `UNSTABLE_EVIDENCE`     | 无法形成稳定证据 → 条件 Block         |
| Test Execution | 版本有效性 | Commit SHA / Build ID     | `STALE_EVIDENCE`        | 不是当前 Candidate → **等同无证据**   |
| Test Execution | 环境有效性 | Env / Device / Config     | `INVALID_ENVIRONMENT`   | 环境不满足测试前提 → Evidence Invalid |

> **门禁原则：**Missing Evidence ≠ PASS。状态至少应包含 **PASS / FAIL / UNKNOWN**，而不是只有 PASS / FAIL。

## 7. L5：Candidate Build 是否真正值得交给 UAT

Gate2 的最终检查对象不是源码，而是用户马上要验收的那个 Candidate。

| 检查对象        | 属性            | Evidence                              | Finding                  | Block                         |
|-----------------|-----------------|---------------------------------------|--------------------------|-------------------------------|
| Candidate Build | 唯一性          | Commit SHA / Build ID / Artifact Hash | `UNTRACEABLE_BUILD`      | **Block**                     |
| Candidate Build | 可安装 / 可部署 | Deploy / Install Result               | `DEPLOY_FAILED`          | **Block**                     |
| Candidate Build | 基本运行能力    | Smoke                                 | `SMOKE_FAILED`           | **Block**                     |
| Candidate Build | 功能集成完整    | Integration Checks                    | `INTEGRATION_INCOMPLETE` | 核心 Feature → Block          |
| Runtime         | 关键依赖可用    | Dependency Health                     | `DEPENDENCY_NOT_READY`   | 导致 UAT 无法有效进行 → Block |
| Runtime         | 配置正确        | Config / Flags / Endpoints            | `CANDIDATE_CONFIG_ERROR` | **Block**                     |

> 这一层回答的不是“代码写完了吗”，而是：**这个 Feature 是否已经从“代码完成”变成“可验收产品”**。

## 8. L6：Finding 是否真正关闭

| 检查属性           | Evidence                   | Finding                   | Block                     |
|--------------------|----------------------------|---------------------------|---------------------------|
| Finding 是否修复   | Fix Diff                   | `OPEN_FINDING`            | Blocking Severity → Block |
| Fix 是否重新验证   | Rerun Evidence             | `UNVERIFIED_FIX`          | Blocking Finding → Block  |
| 是否是假阳性       | Technical Evidence         | False Positive Resolution | 有合理证据可 Close        |
| 是否接受风险       | Waiver                     | `ACCEPTED_RISK`           | 满足授权规则 → 不 Block   |
| Waiver 是否有效    | Approver / Expiry / Reason | `INVALID_WAIVER`          | Block                     |
| 是否存在未归属问题 | Ownership                  | `UNOWNED_FINDING`         | Critical / High → Block   |

> 最终规则应是：**High Finding AND not resolved AND not validly waived → BLOCK**，而不是简单地“High Finding = Block”。

## 9. Finding 根分类

第一版建议只保留 6 个根 Finding，其他均作为 subtype，避免分类膨胀。

| 根 Finding              | 定义                                  | 典型子类                                                                 |
|-------------------------|---------------------------------------|--------------------------------------------------------------------------|
| **Implementation Gap**  | 批准意图与实际实现存在缺口            | Missing Implementation / Mismatch / Unauthorized Change / Plan Deviation |
| **Verification Gap**    | 应该证明的行为没有得到有效证明        | Missing Test / Weak Oracle / Not Executed / Regression Gap               |
| **Regression Risk**     | 变更可能破坏已有系统且风险未关闭      | Impact Gap / Compatibility Risk / Dependency Risk                        |
| **Engineering Failure** | 确定性工程检查失败                    | Build / Static / Security / Contract / Architecture                      |
| **Evidence Gap**        | Evidence 缺失、过期、错误版本或不可信 | Stale / Missing / Invalid Environment / Untraceable                      |
| **Open Risk**           | 已发现风险没有关闭或没有合法接受      | Open Finding / Unverified Fix / Invalid Waiver / Unowned Risk            |

## 10. 最高层 Block Policy

- **B1 · 承诺没有实现**：Mandatory Feature Behavior 未实现或实现错误 → BLOCK
- **B2 · 承诺没有证明**：Mandatory Verification Obligation 无有效 Evidence → BLOCK
- **B3 · 存在不可接受风险**：Security / Regression / Compatibility / Engineering Risk 超过阈值 → BLOCK
- **B4 · Candidate 不可验收**：Build / Deploy / Smoke / Env / Config Invalid → BLOCK

> 所有细则应归入这四条最高层策略，而不是让门禁规则扩展成几十个互不相关的判断项。

## 11. LLM 与确定性门禁的职责边界

| 能力                                    | LLM            | 确定性工具          | 是否适合直接 Block                  |
|-----------------------------------------|----------------|---------------------|-------------------------------------|
| Spec ↔ Implementation 语义一致性        | **主力**       | 辅助                | LLM Finding 需验证后 Block          |
| Plan ↔ Diff 偏移                        | **主力**       | 范围规则可辅助      | 重大偏移需验证后 Block              |
| Diff ↔ Tests 缺口                       | **主力**       | 映射规则可辅助      | 缺少 Mandatory Verification → Block |
| Impact / Regression Risk 推理           | **主力**       | 依赖图 / 调用图辅助 | 风险未闭环时条件 Block              |
| Build / Compile / Lint                  | 不承担最终判定 | **主力**            | **可直接 Hard Block**               |
| Test Execution / Result                 | 解释与归因     | **主力**            | **可直接 Hard Block**               |
| Security / Contract / Artifact Identity | 辅助解释       | **主力**            | **可直接 Hard Block**               |

> **核心原则：**LLM 找问题，Evidence 定事实。LLM 的语义判断适合生成候选 Finding，但不宜单独作为最终 Hard Gate。

## 12. 最终 Gate2 逻辑

**流程：** 实现对象（Spec / Plan / Diff / Interfaces） + 验证对象（Obligation / Test / Result） + 交付对象（Candidate Build / Runtime）

**流程：** 检查属性（一致性 / 完整性 / 验证结果 / 变更安全 / Evidence） → Finding（6 个根类 + subtype） → Blocking Policy（B1 / B2 / B3 / B4） → Verdict（PASS / PASS WITH ACCEPTED RISK / BLOCK）

> **Gate2 的本质：** 不是检查 AC、Rule、Test、Code 等一堆对象是否“质量好”，而是证明 **Feature 的批准意图 → 实现 → 验证 → 当前 Candidate** 是否形成完整、可信、可审计的闭环。

## 13. 调查依据（上一轮结论所引用的公开实践）

- Anthropic / Claude：AI-Native SDLC Playbook — 以 spec、plan、diff、tests、review findings 形成 AI-native review 链路。
- GitHub：Rulesets / Required Status Checks / Code Quality Thresholds — 确定性 CI、扫描、覆盖率等作为可阻断门禁。
- Microsoft Azure Test Plans：Requirement / Feature → Test Case → Test Result → Build / Defect 的可追溯与 UAT 组织方式。
- OpenAI：Harness Engineering — agent 获取 repository、UI、日志、指标、测试证据后进行验证与 review，而非只依据 Diff 猜测。

说明：本报告用于固化上一轮调查结论，不把 LLM 直接判定视为行业统一标准；LLM 自动硬阻断目前仍属于需谨慎采用的前沿实践。

文件：Gate2_矩阵检查目标.html · 适用阶段：Feature 开发完成后、用户/UAT 验收前
