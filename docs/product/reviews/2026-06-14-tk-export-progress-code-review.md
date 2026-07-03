# Tk 导出反馈优化代码审查报告

日期：2026-06-14

## 审查范围

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/IMPLEMENTATION_TRACKER.md`

## 审查结论

未发现阻断问题。

本次改动只调整安全页和导出弹窗的 UI 反馈：新增导出状态卡、结果路径展示、失败日志路径和恢复建议；Windows 本地导出与 macOS 源码包导出改为后台线程执行。未改变导出包隐私默认值，真实 Key、DPAPI 密文、聊天、待办、提醒历史和本机路径仍按原有规则排除或显式选择。

## 重点检查

- 后台导出期间底部按钮会禁用，降低重复点击风险。
- 导出成功后弹窗保留压缩包路径、入口脚本路径和导出目录，便于用户检查结果。
- 导出失败后同一状态卡显示 `desktop-pet-error.log` 路径和恢复建议。
- 已补充弹窗销毁后的回调保护，避免后台线程完成后更新已销毁 Tk 控件。
- 敏感扫描未发现新增真实 Key、Token、私钥或 C 盘旧运行路径；只命中既有 DPAPI 前缀函数。

## 验证说明

- 语法检查：通过。
- 运行 JSON 解析：通过。
- UTF-8 BOM 检查：通过。
- E 盘源文件与 E 盘运行镜像哈希一致。
- 未启动 GUI，未实际生成导出包；导出过程仍需用户做一次人工验收。

## 剩余验证

- 从 E 盘运行镜像打开控制面板安全页，确认“导出状态和路径”卡片显示正常。
- 打开 Windows 导出弹窗，确认导出中按钮禁用、成功路径保留、失败时日志路径可见。
- macOS 远端构建路径需要在 GitHub Token 和 workflow 配置齐备后人工验收。
