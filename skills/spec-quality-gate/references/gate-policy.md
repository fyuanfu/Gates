# 判级与门禁

严重度表示问题成立时的影响；confirmation_status 表示 confirmed / pending / rejected。不能因置信度低降低严重度。

| 级别 | 影响依据 |
|---|---|
| P0 | 授权需求证据支持的严重安全、隐私、资金或不可逆数据损失链路；不得仅凭假设或外部法规常识 |
| P1 | 核心业务承诺、关键用户结果或重要验收不可确定，或核心规则不能同时满足 |
| P2 | 影响有限的局部行为、局部验收或返工问题，核心承诺仍可实现和验收 |
| P3 | 不改变业务行为或验收的表达、术语、追踪问题 |

不同实现不自动等于 P1。关键性须引用需求或说明其与本次主目标的关系；无法确定且可能达到 P1 时保留 pending P1。
例：上传实际失败却显示完成属于核心结果 P1；非关键帮助提示的展示时机歧义通常 P2；不影响含义的错别字 P3。
“快速”若约束核心性能验收而不可判定为 P1；若只涉及非关键附属内容，可为 P2；不得把所有未声明“发布指标”的性能要求降为 P2。

按顺序计算：
1. 输入、契约、快照或阶段不完整：execution_error，结论不可用；保留此前候选证据。
2. 任意 confirmed P0/P1：review_failed；同时展示 pending 项。
3. 无已确认 P0/P1，但有 pending P0/P1：review_inconclusive。
4. 其余：review_passed，仍展示 confirmed/pending P2/P3。

无问题时 highest_severity=null。计数仅统计 confirmed，pending 单列。execution_error 不等于需求失败，review_inconclusive 也不等于通过。
