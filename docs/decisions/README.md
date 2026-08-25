# Gates Decision Records

本目录保存 Gates 项目的重要决策历史，回答：**为什么当前体系是这样设计的、曾考虑过什么、后来是否被替代。**

`quality-gate-knowledge-overview-v0.1.md` 继续只维护“当前有效状态”；Decision Record（DR）维护“决策历史”；Git Commit / PR 维护“具体发生了什么变更”。

```text
Discussion / Issue
        ↓ 收敛
Decision Record (why)
        ↓ 生效
Knowledge Overview (current state)
        ↓ 落地
Schema / Example / Skill / Policy
        ↓
PR / Commit (what changed)
```

## 1. 什么时候必须创建 DR

以下任一内容的语义发生新增、删除或改变时，必须创建新的 DR：

- Gate 的目标、边界、职责或生命周期位置；
- Requirement / Traceability / Evidence 等核心对象模型；
- Canonical Schema 或 SSOT 约束；
- 关键 Traceability Relationship；
- Gate Policy、阻断条件、Verdict 规则；
- 关键术语定义；
- 会影响多个 Artifact 或后续 Agent 行为的设计原则。

以下变化通常不需要 DR：

- 错别字、排版、链接修复；
- 不改变语义的措辞优化；
- 仅增加例子且不改变规范；
- 纯目录整理。

当前自动检查采用保守 V1：修改受保护的核心知识文件时，PR 必须同时包含一个 `docs/decisions/DR-*.md` 变更。后续若误报明显，再增加受控的 non-semantic exemption，而不是先放宽约束。

## 2. DR 状态

| 状态 | 含义 |
|---|---|
| `Proposed` | 候选决策，尚未成为当前事实 |
| `Accepted` | 已生效，Overview / Schema / Skill 应与之保持一致 |
| `Superseded` | 已被后续 DR 替代；历史内容保留，不改写为新结论 |
| `Rejected` | 明确评估后未采用 |
| `Deprecated` | 不再建议使用，但不一定存在一条直接替代决策 |

Accepted DR 原则上不可重写其历史理由。决策变化时创建新 DR，并在旧 DR 上标记 `Superseded by DR-xxxx`。

## 3. 编号与文件名

- 编号格式：`DR-0001`、`DR-0002`……单调递增，不复用。
- 文件名：`DR-0001-short-kebab-title.md`。
- 一个 DR 只解决一个可以清晰陈述的决策问题。
- 多个紧密耦合、必须一起成立的结论可以放在同一 DR；不要机械地“一条结论一个文件”。

## 4. DR 与 Overview 的关系

Overview 负责“现在是什么”，DR 负责“为什么”。

建议在 Overview 的稳定结论旁增加：

```text
**状态：已确认 · Decision: DR-xxxx**
```

如果一个章节由多条 DR 共同支撑，可以列多个 Decision ID，但不要把完整决策过程复制回 Overview。

## 5. Issue / PR / Commit 关联规则

### Discussion / Issue

复杂决策可以先在 Chat 或 GitHub Issue 中探索。Issue 是讨论容器，不是最终事实源。

当讨论形成稳定结论后：

1. 创建 DR；
2. DR 的 `Related` 中引用相关 Issue / PR（存在时）；
3. 将决策同步到 Overview 和受影响 Artifact；
4. 通过同一个 PR 合入。

### Pull Request

涉及关键知识变更的 PR 应同时包含：

- 新增或更新的 DR；
- 当前状态文件（通常是 Overview）的同步修改；
- 必要的 Schema / Example / Skill / Policy 修改。

推荐 PR 描述包含：

```text
Decision: DR-xxxx
Supersedes: DR-yyyy   # 如适用
Affected artifacts:
- ...
```

### Commit

Commit 回答 `what changed`，不代替 DR 的 `why`。

推荐格式：

```text
docs: simplify verification traceability model [DR-0001]
```

如果一个 PR 有多个提交，至少最终语义变更提交或 squash commit 应包含对应 DR ID。

## 6. 决策索引

| ID | 决策 | 状态 | 日期 |
|---|---|---|---|
| [DR-0001](./DR-0001-verification-obligation-not-first-class.md) | Verification Obligation 不作为 V1 一等追溯对象 | Accepted | 2026-08-25 |

## 7. 历史补录策略

不一次性为所有旧结论“考古式补 DR”。

采用增量补录：

1. 从今天之后的新决策开始强制记录；
2. 对 Overview 中影响最大、最容易重复争论的历史结论优先补录；
3. 某个旧结论再次被修改或讨论时，必须先建立或补齐对应 DR；
4. 补录优先级见 [decision-backlog.md](./decision-backlog.md)。

## 8. 模板

新建 DR 时使用 [DR-TEMPLATE.md](./DR-TEMPLATE.md)。
