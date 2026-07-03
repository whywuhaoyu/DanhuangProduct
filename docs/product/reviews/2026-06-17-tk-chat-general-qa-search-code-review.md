# Tk AI 通用问答与搜索增强代码审查

时间：2026-06-17

范围：

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `src-prototype/legacy-monolith/CHANGELOG.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/PRODUCT_REQUIREMENTS.md`
- `docs/product/UI_REDESIGN_SPEC.md`
- `docs/product/wpf-tech-spike/WPF_TECH_SPIKE_SPEC.md`

## 结论

通过。

本次改动增强了 AI 聊天的资料查询入口和搜索层兜底：显式查询词之外，通用知识问题会自动进入资料查询；DuckDuckGo Lite 解析失败或结果不足时，会补充中文维基百科 OpenSearch 结果，并做去重合并。

## 审查要点

- 正确性：`is_general_knowledge_query()` 覆盖“什么是、谁是、为什么、怎么、如何、多少、哪里、哪年、有哪些”和英文 `what/who/why/how/where/when/which`；`is_research_query()` 继续优先保留显式搜索词和历史日期规则。
- 陪伴边界：`你是谁、你叫什么、想你、陪我、摸摸、安慰我` 等陪伴语境被排除，不会误触发联网查询。
- 搜索兜底：原 `web_search_results()` 拆为 DuckDuckGo 主源、中文维基百科备用源和去重合并；主搜索源异常时不会直接让问答链路失败。
- 隐私安全：未新增 API Key、Token、聊天、待办或本机路径写入；搜索请求只使用用户当轮提问生成的查询词。
- 可维护性：搜索来源分层清晰，后续可继续添加新闻源、天气源、汇率源或官方 API 适配，而不影响聊天主流程。

## 验证

- `python -m py_compile src-prototype/legacy-monolith/run-danhuang-desktop-pet.py data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- E 盘运行 JSON 共 19 个文件解析通过。
- 意图识别验证：
  - `什么是量子计算`、`为什么天空是蓝色`、`有哪些好用的AI工具`、`how to make tea` -> 触发资料查询。
  - `你是谁`、`想你了` -> 不触发资料查询。
- 实网搜索验证：
  - `什么是量子计算`、`为什么天空是蓝色` 均返回 5 条网页结果。
- 备用源验证：
  - 模拟 DuckDuckGo 失败后，`量子计算` 通过中文维基百科 OpenSearch 返回 3 条结果。

## 剩余风险

- 当前搜索仍是轻量 HTML/API 摘要，不等于完整浏览器阅读；后续可继续加天气、汇率、新闻垂类源和结果来源展示。
