# 代码审查：气泡 renderer 模块拆分

## Summary

本轮变更把 Tk 桌宠气泡图片绘制从两份 E 盘单文件主程序中抽到 `src-prototype/modular/ui/tk_bubble_render.py`，并让 `render_bubble_image()` 优先调用 modular renderer。旧单文件绘制函数继续保留为回退路径，避免 renderer 导入失败或渲染异常时破坏桌面气泡显示。

审查范围：

- `src-prototype/modular/ui/tk_bubble_render.py`
- `src-prototype/modular/ui/__init__.py`
- `src-prototype/modular/validate_phase3.py`
- `src-prototype/modular/tests/test_ui_phase3.py`
- `src-prototype/modular/tests/test_runtime_integration_phase3.py`
- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- 本轮同步的产品文档和执行追踪

## Findings

### Critical

无。

### Improvements

无必须修改项。

### Nitpicks

无。

## Review Notes

- Correctness：`render_bubble_image()` 的 modular 调用只接管图片生成，不改变 Tk Canvas 文本测量、逐字显示、气泡定位或生命周期；失败时回退旧绘制函数。
- Maintainability：六种气泡样式的 Pillow 绘制逻辑已经集中到独立模块，后续 WPF 或主题 token 对照可以从 renderer 层读取样式边界。
- Edge cases：renderer 颜色输入做了 `fill/outline` 和旧 `bubble_fill/bubble_outline` 两种键兼容；非法颜色回退默认值。
- Testability：Phase 3 单元测试覆盖六种样式输出 RGBA 图片；运行集成测试覆盖两份运行入口加载 `MODULAR_RENDER_BUBBLE_IMAGE`。
- Security/privacy：未新增路径写入、网络请求、用户数据读取或密钥处理；未修改 C 盘 live runtime。

## Verification

- `python -m py_compile src-prototype\modular\ui\tk_bubble_render.py src-prototype\modular\ui\tk_bubble.py src-prototype\modular\validate_phase3.py src-prototype\legacy-monolith\run-danhuang-desktop-pet.py data-dev\current-runtime\danhuang\run-danhuang-desktop-pet.py`
- `python -m unittest discover -s src-prototype\modular\tests`：26 tests OK
- `python src-prototype\modular\validate_phase1.py --pet-dir data-dev\current-runtime\danhuang --json`
- `python src-prototype\modular\validate_phase2.py --pet-dir data-dev\current-runtime\danhuang --json`
- `python src-prototype\modular\validate_phase3.py --pet-dir data-dev\current-runtime\danhuang --json`
- JSON 解析：278 个非归档/非包内 JSON 通过
- UTF-8 BOM 检查：511 个非归档/非包内源码/文档文件通过
- 本轮 14 个变更文件敏感信息形态扫描通过
- 两份 E 盘 Tk 主程序 SHA256 一致：`5D80EBD915B864060EE2FE10ED891ACC536E9F5E7498FF5328051A7949587C75`
- WPF build：0 warning，0 error；未启动 WPF 窗口

## Conclusion

Approved。下一步建议继续拆气泡生命周期和外观页预览，或转向 `ui/tk_pet_window.py` 的透明窗口属性、拖动和多屏巡逻边界。
