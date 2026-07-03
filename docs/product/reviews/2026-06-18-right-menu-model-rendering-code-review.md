# 代码审查：右键面板 model 渲染接入

日期：2026-06-18

## Summary

本次审查范围：

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- `src-prototype/modular/tests/test_ui_phase3.py`
- `src-prototype/modular/tests/test_runtime_integration_phase3.py`
- `CHANGELOG.md`
- `docs/product/IMPLEMENTATION_TRACKER.md`
- `docs/product/PROTOTYPE_MODULARIZATION_PLAN.md`
- `docs/product/DANHUANG_UI_DESIGN_BRIEF.md`

变更目标是让 E 盘两份 Tk 单文件的右键快捷面板优先消费 `ui/tk_right_menu.py` 的完整 `sections/items/footer/layout/header` 合同，而不是只读取动作列表。

## Findings

### Critical

未发现阻断问题。

### Improvements

未发现必须在本轮回改的问题。当前实现保留了 modular 不可用时的旧硬编码分组兜底，降低运行风险。

### Nitpicks

未记录。

## Review Notes

- 右键标题、副标题、自动关闭时长和外部点击检测延迟开始消费 model，后续可继续把尺寸约束和弹层结构迁出单文件。
- 常用入口、基础动作、扩展动作、更多动作 footer、管理动作和窗口命令统一按 model item 的 `command/page/variant/enabled/action_id/loops` 渲染。
- `open_pet_switcher` 和 `open_more_actions` 仍使用特殊按钮命令，不走通用“先关闭右键面板再执行”的包装，避免弹层打开前被销毁。
- “更多动作”弹层优先消费 `hidden_extension_buttons`，使弹层文案、可用态和播放循环数与主右键面板同源。
- 单元测试补充了 right-menu 可渲染命令合同，运行集成测试同步检查 `APP_VERSION=0.11.39`。

## Conclusion

Approved。下一步建议继续把宠物切换弹层也抽成 view model，并把右键面板尺寸约束从文档/模型落实到 Tk 布局层。
