# 代码审查：右键主面板样式和定位模型接入

## Summary

本轮变更目标是继续收敛 Phase 3 右键菜单拆分：把右键主面板宽度约束、按钮最小高度、列数、主面板避让定位、按钮 variant 和弹层颜色 token 从 Tk 单文件迁入 `ui/tk_right_menu.py`，并让 E 盘两份运行入口优先消费这些模型。

审查范围：

- `src-prototype/modular/ui/tk_right_menu.py`
- `src-prototype/modular/tests/test_ui_phase3.py`
- `src-prototype/modular/tests/test_runtime_integration_phase3.py`
- `src-prototype/modular/validate_phase3.py`
- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- 本轮同步更新的 README、WPF 运行说明和产品文档。

## Findings

### Critical

无。

### Improvements

无阻塞项。当前接入保留了 modular 模型不可用时的旧颜色、旧布局和旧定位回退，符合 E 盘运行镜像小步迁移边界。

### Nitpicks

无。

## Review Notes

- `right_menu_style_tokens()` 使用深拷贝导出 token，避免调用方误改全局样式常量；单元测试已覆盖隔离性。
- `compute_menu_position()` 保持右侧优先，并按左侧、下方、上方、点击点顺序退让；屏幕夹取和宠物避让边距均来自 layout model。
- Tk 层继续负责实际控件创建、图片引用、`place_window()` 和失败回退；纯模型只输出可测试的 token、尺寸约束和坐标，边界清晰。
- 两份 E 盘运行入口的 `APP_VERSION` 和新增 modular 导入项已同步到 `0.11.42`。
- `validate_phase3.py` 增加 `layout` 和 `style_variants`，可以支撑外部设计工具和 WPF 后续承接右键面板状态。

## Verification

- `python -m py_compile ...`：通过。
- `python -m unittest discover -s src-prototype\modular\tests`：25 tests OK。
- `python src-prototype\modular\validate_phase3.py --pet-dir data-dev\current-runtime\danhuang --json`：通过，输出 right_menu layout 和 style variants。

## Conclusion

Approved。残余风险是本轮尚未做真实 Tk 右键面板截图验收；下一步如果继续改交互视觉，应补右键主面板、切换形象弹层和更多动作弹层的桌面截图基线。
