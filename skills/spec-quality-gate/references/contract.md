# 数据契约

manifest.json：`{"primary_documents":["/absolute/prd.md"],"authoritative_references":[]}`。相对路径以 manifest 所在目录解析。范围以这些完整文档为准；V1 不支持静默章节过滤。

prepare 创建 packet.json，含 documents：path、role、sha256、lines；每行可用 1 起始行号定位。finalize 检查文件仍与快照一致。

review.json 必须包含：
- inventory：数组，每条含 id、source（path、line）、behavior、observable_results（数组）；没有需求 ID 时使用局部生成 ID，不因缺 ID 报错。
- documents_reviewed：完整 path 数组，与 packet 一致；表示实际阅读全文，不可提前填。
- stages_completed：coverage、clarity_verifiability、consistency、confirmation。
- findings：数组；契约详见 assets/review.schema.json。

Finding：id、type（MISSING/AMBIGUOUS/INCONSISTENT/UNVERIFIABLE）、severity（P0～P3）、confirmation_status、subject、claim、impact、question、evidence、counter_evidence、search_log、resolution_reason。
证据对象为 path、line、quote；quote 必须是对应原文行中连续的非空文本。冲突需提供双方证据。search_log 是含 path、query、result 的数组，覆盖每份授权文档；result 说明该处是否解决候选问题。不能伪造“已搜索”。

脚本校验可验证结构、定位、快照和自报覆盖，不验证语义推理或阅读真实性。文档解析、全文阅读和证据确认仍由 Agent 执行。
