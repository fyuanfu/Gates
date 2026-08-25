# Decision Record Backfill Backlog

本文件用于识别 `quality-gate-knowledge-overview-v0.1.md` 中哪些既有“已确认”结论值得补 Decision Record。

原则：**不机械地为 C-001～C-018 每条各建一个 DR。** 多条结论如果属于同一个不可分割的设计决策，应由同一 DR 记录其背景、方案和 trade-off。

## P0：应优先补录

| 候选 DR | 覆盖 Overview 结论 | 决策主题 | 为什么优先 |
|---|---|---|---|
| DR-0003 | C-001、C-002、C-004 | 四层 Gate 总体模型与“Gate ≠ Checklist / Traceability” | 是整个 Gates 项目的顶层边界，后续所有 Skill 和 Policy 都依赖 |
| DR-0004 | C-003、C-005、C-006、C-007、C-008 | Requirement Semantic SSOT、最小对象模型与 `feature_story_bundle` | 决定需求同源、Schema 和所有下游引用方式，最容易因模板变化重新争论 |
| DR-0005 | C-009、C-010、C-011 | Gate1 Engineering Ready 目标与 Behavior / Oracle / Contract Unknown 三类阻断 | 当前项目主线，直接决定 Gate1 Skill 的职责和阻断边界 |
| DR-0006 | C-012、C-013、C-014、C-015 | Gate2 Merge Ready 边界、两类安全证据链、只消费已有测试 | 决定 Gate2 与 Testing / Gate3 的边界，已有多轮演进历史 |
| DR-0007 | C-016 | LLM 负责分析，确定性 Versioned Policy 负责最终 Verdict | 是跨 Gate 的核心治理原则，应独立记录，避免未来把 Agent 判断直接当 Gate Verdict |

## P1：在进入对应阶段前补录

| 候选 DR | 覆盖 Overview 结论 | 决策主题 | 触发时机 |
|---|---|---|---|
| DR-0008 | C-017 | Gate3 Feature Ready 与 Gate4 Release Ready 的生命周期边界 | Gate3 进入实现前 |
| DR-0009 | C-018 | Testing 的目标是可信 Evidence / Behavior Verdict，而不是“跑绿” | Testing Skill 或 Gate3 正式接入前 |

## 已有 DR

| DR | 覆盖内容 |
|---|---|
| DR-0001 | Verification Obligation 在 V1 不作为独立 Traceability Object；Requirement 直接被 Test / Verification Activity 验证 |
| DR-0002 | Task 以 Story 为主归属；Task Planning / Review 必须覆盖 Required AC / Scenario / Rule 等 Requirement Object；验收不作为正常补漏机制 |

## 补录规则

1. **触发式补录优先于考古式补录。** 某个既有结论再次被修改、质疑或进入实现时，先补对应 DR。
2. 补录时只使用能够确认的已有结论、Artifact 和当前约束；不要伪造过去讨论中不存在的理由。
3. 如果无法确定当时的全部历史理由，在 DR 中明确写成“当前可确认的决策依据”，而不是假装还原完整历史。
4. 补录完成后：
   - 更新本 backlog；
   - 更新 `docs/decisions/README.md` 索引；
   - 在 Overview 对应稳定结论旁增加 Decision ID。
5. 如果一个候选 DR 在补录过程中发现其实包含多个独立决策，应拆分，并重新编号后续候选。

## 当前覆盖情况

- Overview 历史已确认结论：C-001 ～ C-018，共 18 条。
- 已有正式 DR：DR-0001、DR-0002。
- DR-0002 是 2026-08-25 新形成的 Task / Implementation Coverage 决策，不属于 C-001～C-018 的历史补录。
- 历史结论建议继续补录为：5 个 P0 DR + 2 个 P1 DR。
- 不建议创建 18 个逐条镜像 DR；DR 应记录“决策”，不是复制 Overview 的结论登记表。
