# technical-challenge-model 实现方案

本目录保存 `technical-challenge-model` 的正式设计规格与实施计划。

## 文档

- [implementation-spec.md](./implementation-spec.md)  
  Technical Challenge Model 的正式实现规格，定义目标、边界、领域模型、Finding 双路径、Evidence Policy、Verdict/Assurance、Brownfield/Android 扩展以及 Eval Contract。

- [implementation-plan.md](./implementation-plan.md)  
  基于 Superpowers 流程的可执行实施计划，覆盖 TDD、Skill 结构、Schema/Validator、Eval Harness、Dev/Holdout 以及最终验收门槛。

## 对应实现

Skill 实现位于：

```text
skills/technical-challenge-model/
```

当前状态：

```text
PILOT
```

Deterministic contract 已完成；fresh-context semantic acceptance 仍是从 PILOT 升级到 SEMANTIC_ACCEPTED 的发布门槛。
