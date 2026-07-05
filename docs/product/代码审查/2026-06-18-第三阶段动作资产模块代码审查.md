# Phase 3 动作资产模块代码审查

日期：2026-06-18

## 范围

- `src-prototype/modular/assets/atlas.py`
- `src-prototype/modular/assets/manifest.py`
- `src-prototype/modular/validate_phase3.py`
- `src-prototype/modular/tests/test_assets_phase3.py`
- 相关产品文档和设计说明同步

## 结论

通过。未发现阻塞问题。

本次改动只抽取只读动作资产和 manifest 逻辑，不修改 C 盘运行实例，不替换 spritesheet，不写入 `pet-family.json`、设置、待办、聊天或提醒历史。

## 审查发现

### 已修复：复合跑动动作可用性

初版 manifest 把 `running` 当成必须存在独立 atlas 行的动作。现有运行逻辑里“跑一小段”是复合动作，依赖 `running-right` 和 `running-left`，基础动作包也应可用。

修复：

- `action_supported()` 对 `running` 改为检查左右跑动动作。
- `build_action_entry()` 对 `running` 改为使用左右跑动帧判断可播放。
- 单元测试新增基础 5 行 atlas 下 `running` 仍可播放的断言。

### 已修复：默认 manifest 不暴露解析后绝对路径

初版 `build_pet_action_manifest()` 默认返回解析后的 `spritesheet_path`，如果后续误用于公开导出，可能带入本机路径。

修复：

- 默认 `include_private_paths=False`。
- 默认移除 atlas 和 atlas_grid 中的 `path` 字段。
- 仅在显式传入 `include_private_paths=True` 时返回解析路径。
- 单元测试覆盖默认不输出 `spritesheet_path` 和 atlas `path`。

## 验证

- `python -m py_compile ...`：通过。
- `python -m unittest discover -s src-prototype\modular\tests`：15 tests OK。
- `python src-prototype\modular\validate_phase1.py --pet-dir archives\DanhuangPrototype-20260614-121543`：通过。
- `python src-prototype\modular\validate_phase2.py --pet-dir data-dev\current-runtime\danhuang`：通过。
- `python src-prototype\modular\validate_phase3.py --pet-dir data-dev\current-runtime\danhuang`：通过，读取到 5 个 ready 宠物、54 个可播放动作、11 个扩展动作。
- JSON 解析：278 个文件通过。
- UTF-8 BOM 检查：492 个文本/源码文件通过。
- 新增 Phase 3 代码和设计文档隐私关键词扫描：未发现 DPAPI 前缀、本机私有路径、样例本地图或 API Key 形式密钥。

## 残余风险

- Phase 3 第一批仍是纯逻辑抽取，Tk 单文件运行入口尚未切换到新模块。
- 透明窗口、气泡、右键快捷面板还未拆到 `ui/` 模块；下一步拆这些 UI 层时需要真实桌面烟测和截图验收。
