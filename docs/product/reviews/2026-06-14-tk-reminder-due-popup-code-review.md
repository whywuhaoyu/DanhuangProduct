# Tk Reminder Due Popup Code Review

日期：2026-06-14

## 审查范围

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/IMPLEMENTATION_TRACKER.md`

本轮变更聚焦 `open_reminder_popup()`：将到点提醒弹窗改为暖色提醒卡，增加状态 chip、待办属性摘要、备注预览、分层操作和关闭不改状态路径。

## Findings

### Critical

无。

### Improvements

无。本轮审查中已处理长内容风险：提醒时间改用短格式 `todo_due_text()`，备注在弹窗内截断为预览，避免固定高度弹窗被长日期或长备注撑坏。

### Nitpicks

无。

## 业务符合性

- 完成仍调用 `complete_todo()`，保留完成、重复生成、保存和气泡反馈逻辑。
- 稍后提醒仍调用 `snooze_todo()`，保留 15 分钟、1 小时、明天三条原有路径。
- “打开提醒页”会先写回 `todo_selected_id`，再打开控制面板提醒页，便于列表定位当前待办。
- “关闭”和 Escape 只关闭弹窗，不改变待办状态，符合“关闭不等于完成或稍后”的交互边界。
- 弹窗未新增外部依赖、未改变待办 JSON 数据结构、未触碰 C 盘运行目录。

## 验证

- `python -m py_compile src-prototype/legacy-monolith/run-danhuang-desktop-pet.py data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- 运行镜像关键 JSON 解析通过：settings、family、companion state、AI providers、todos、reminder history。
- 本轮触达文件未检测到 UTF-8 BOM。
- 源文件与 E 盘运行镜像 SHA256 一致：`DC56C9580A7AAA6F3D00F4F96D558FFEE6D1B915A4623384A2C2F648E69E250C`。
- `git status --short` 不可用：当前目录不是 Git 仓库。

## 结论

Approved。

残余风险：本轮未启动 Tk GUI 做截图验收；仍需要后续人工确认到点弹窗在真实窗口中的高度、按钮排列、关闭、完成、稍后和打开提醒页路径。
