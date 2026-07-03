# Phase 3 UI 状态模型代码审查

日期：2026-06-18

范围：

- `src-prototype/modular/ui/tk_right_menu.py`
- `src-prototype/modular/ui/tk_bubble.py`
- `src-prototype/modular/ui/tk_pet_window.py`
- `src-prototype/modular/validate_phase3.py`
- `src-prototype/modular/tests/test_ui_phase3.py`

## 结论

Approved。

本轮新增的是 Tk 渲染层之前的纯状态模型，不写运行配置、不替换素材、不触碰 C 盘运行实例。审查后未发现阻塞性正确性、安全或隐私问题。

## 发现

### Critical

无。

### Improvements

- 已修正：气泡尺寸估算原先按总字符数估行，显式换行文本可能低估高度；现在按每一行独立换行统计。
- 已修正：窗口行为摘要中的浮点数可能出现 `0.35000000000000003` 这类无意义长小数；现在对输出做稳定舍入。

### Nitpicks

无。

## 验证建议

继续保留当前验证边界：

- 纯模型先通过 `py_compile`、单元测试和 `validate_phase3.py`。
- 后续把单文件 Tk 运行入口接入这些模型时，再补右键面板、气泡和多屏窗口的人工或脚本化桌面截图验收。

## 剩余风险

- 这批模型尚未接入 `run-danhuang-desktop-pet.py`，因此只能证明菜单/气泡/窗口行为的数据结构可用，不能替代实际 Tk 点击、外部点击关闭、多屏拖动和气泡绘制验收。
