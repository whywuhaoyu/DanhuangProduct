# Tk Search Source Upgrade Code Review

Date: 2026-06-17

Scope:

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `src-prototype/legacy-monolith/CHANGELOG.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/UI_REDESIGN_SPEC.md`
- `docs/product/wpf-tech-spike/WPF_TECH_SPIKE_SPEC.md`
- `docs/product/IMPLEMENTATION_TRACKER.md`

## Findings

No blocking issues found in the reviewed search upgrade.

## Review Notes

- Knowledge-style questions now clean entity phrases such as `什么是`, `谁是`, `是什么`, `是谁`, and `什么意思` before search, which improves hit quality for encyclopedia-style queries.
- Non-recency knowledge searches try a Chinese Wikipedia summary first, then merge DuckDuckGo, Bing fallback, and Wikipedia OpenSearch results.
- Recency-sensitive searches such as news, current prices, weather, and latest events still prioritize web search and are not forced through encyclopedia summaries.
- Local fallback replies now include source type and URL, so users can see where the summary came from even when cloud AI is unavailable.

## Validation

- `python -m py_compile src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- Query cleaning checks:
  - `什么是量子计算 -> 量子计算`
  - `谁是苏轼 -> 苏轼`
  - `苏轼是谁 -> 苏轼`
  - `量子计算是什么 -> 量子计算`
- Live search checks:
  - `什么是量子计算` returns a Chinese Wikipedia summary plus web results
  - `谁是苏轼` returns a Chinese Wikipedia summary plus web results
  - `为什么天空是蓝色` returns web results
  - `2026年AI新闻` returns recency-oriented web results
- Local fallback reply includes source labels and URLs.

## Residual Risk

- DuckDuckGo and Bing HTML parsing can change. The code keeps multiple sources and failure isolation, but a future parser break should be handled by adding another source or moving to an official API if productized.
