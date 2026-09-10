---
name: spec-quality-gate
description: 评审 PRD、Feature Spec 和交互需求的缺失、歧义、冲突及不可验证问题，按 P0～P3 输出证据和需求质量结果；不评审技术实现。
---
# 需求质量评审（原型）

在授权范围内发现需求问题；通过仅表示完整评审未发现已确认 P0/P1，不代表整体开发就绪。

## 执行
1. 确认用户提供的主文档与明确指定的权威业务参考。V1 接受本地 UTF-8 `.md` / `.txt`；链接、图片、PDF、原型需先由用户提供可核对文本版本。不得悄悄忽略不支持的输入。
2. 阅读 [门禁规则](references/gate-policy.md)、[数据契约](references/contract.md) 和 [统一提示词](prompts/requirement-review.md)。默认当前 Agent 串行执行，不要求子 Agent。
3. 新建本次独立输出目录，生成 manifest.json。执行 `python3 <skill>/scripts/gate.py prepare manifest.json run-dir`，读取 packet.json 中所有文档。失败时保留 execution_error。
4. 建立有原文行号的需求清单 inventory（字段见契约），作为索引，不能替代原文。按统一提示词完成四阶段评审，可纠正抽取遗漏。
5. 写 review.json，包含 inventory、完整阅读声明、四阶段完成记录和候选问题账本；排除的问题保留 rejected 状态与原因。不能把空 Findings 当作已完成评审。
6. 执行 `python3 <skill>/scripts/gate.py finalize run-dir review.json`，由脚本计算 gate-result.json、findings.json 和 gate-report.md。以脚本结果为准。
7. 输出状态、P0/P1、待确认项、P2/P3和读取限制。原文只读，不替 Owner 决策。报告遵循宿主保存规则。

## 原型验证
执行 `python3 <skill>/scripts/test_gate.py` 验证确定性结果和错误路径；这不证明语义召回率。真实 PRD 上需人工对照验证后才能考虑自动阻断。
