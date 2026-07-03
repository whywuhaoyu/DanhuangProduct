# Tk AI Provider 页反馈优化代码审查

## 审查范围

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/IMPLEMENTATION_TRACKER.md`

## 变更摘要

- 新增 `ai_testing_provider_id`，用于标记当前正在测试的 AI 厂商。
- AI Provider 页测试开始和结束时刷新当前 AI 页，按钮在测试中显示“测试中...”并禁用。
- 新增 `ai_provider_panel_selected_id`，刷新 AI 页后保留用户最后选中的厂商，避免测试非当前厂商时跳回当前启用厂商。
- “清除 Key”改为暖色本地确认弹窗，清除前说明影响范围；未保存 Key 时只给页内状态反馈。

## 审查结论

Approved。

未发现阻断问题。改动集中在 AI Provider 页 UI 反馈层，未改变 AI 请求参数、Key 加密存储格式、Provider 配置结构和测试成功后的启用逻辑。

## 重点核查

| 维度 | 结果 | 说明 |
| --- | --- | --- |
| 正确性 | 通过 | 测试开始设置运行中标记，成功/失败回调清理标记并刷新 AI 页，避免按钮长期禁用。 |
| 兼容性 | 通过 | `save_provider_api_key()`、`set_active_ai_provider()` 和原测试 worker 入口保留，真实 Key 仍不显示、不导出。 |
| 可用性 | 通过 | 清除 Key 从系统确认框改为本地暖色确认弹窗，危险操作文案说明影响范围。 |
| 边界处理 | 通过 | 面板父窗口选择已包 `tk.TclError`，避免面板销毁态打开确认弹窗时报错。 |
| 隐私边界 | 通过 | 未记录、展示或导出真实 Key；清除动作只写空本机加密 Key。 |

## 验证记录

- `python -m py_compile src-prototype/legacy-monolith/run-danhuang-desktop-pet.py data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`：通过。
- E 盘源副本和运行镜像 SHA256 一致：`91439C0FDA54F2BD5FE552334CFD0E74AED0367FCFB49419E56F77315DD9999A`。
- 关键运行 JSON 解析通过：设置、宠物家庭、陪伴状态、AI Provider、待办、提醒历史。
- 已检查本次触及文件无 UTF-8 BOM。

## 剩余风险

- 本轮未启动 Tk GUI 做截图验收；需要后续在真实运行实例中确认 AI 页测试中按钮禁用、清除 Key 弹窗位置和刷新后选中厂商保持。
- 测试成功/失败 Toast、替换 Key 的本地风格确认弹窗仍在后续 UI 清单中。
