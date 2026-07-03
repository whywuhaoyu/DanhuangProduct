# Tk Chat Capability Status Code Review

日期：2026-06-17

范围：

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- 本轮相关产品文档同步项

## 结论

通过。未发现需要阻塞发布的正确性、安全或隐私问题。

## 审查要点

- 聊天能力状态条只展示云端连接状态、时间直答、资料查询模式、待办数量和兜底开关，不展示真实 API Key。
- `refresh_chat_tool_status_strip()` 对控件销毁和空引用做了保护，聊天窗关闭时会清理 `chat_tool_status_widgets`。
- 状态刷新挂在 `set_ai_status()`、`set_chat_status()` 和 `finish_chat_reply()`，能覆盖 AI 开关、请求状态和聊天创建待办后的常见刷新路径。
- 源程序和 E 盘运行镜像已通过 `py_compile`，SHA256 一致。

## 剩余风险

- 本轮未做自动化桌面截图比对，聊天窗状态条的视觉间距、文本换行和小窗效果仍需要人工打开 E 盘运行版确认。
- `provider_api_key()` 会在状态条刷新时判断 Key 是否存在；当前只用于布尔状态，不输出 Key，但后续若高频刷新需要考虑缓存非敏感的“是否配置”状态。
