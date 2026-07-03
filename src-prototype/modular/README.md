# modular

这里是 Tk 原型拆分实验目录。原则是先复制/抽取纯逻辑，保持 C 盘运行版不受影响。

目标结构：

```text
core/
  pet_model.py
  companion_state.py
  settings_store.py
  ai_providers.py
  todos.py
  reminder_history.py
  exporter.py
assets/
  atlas.py
  manifest.py
ui/
  tk_pet_window.py
  tk_bubble.py
  tk_bubble_render.py
  tk_right_menu.py
  tk_panel.py
```

拆分前先看：

```text
docs/product/Tk原型模块化拆分计划.md
docs/product/当前审计/code-structure-20260614-121543.json
```

## Phase 1 已落地

当前已抽出纯数据和配置模块：

- `core/pet_model.py`
- `core/settings_store.py`
- `core/companion_state.py`

验证命令：

```powershell
python -m unittest discover -s src-prototype\modular\tests
python src-prototype\modular\validate_phase1.py --pet-dir archives\DanhuangPrototype-20260614-121543 --json
```

注意：Phase 1 只读冻结归档或指定原型目录，不会修改 C 盘当前运行实例。

## Phase 2 已落地

当前已抽出 AI Provider、待办和提醒历史模块：

- `core/ai_providers.py`
- `core/todos.py`
- `core/reminder_history.py`

验证命令：

```powershell
python -m unittest discover -s src-prototype\modular\tests
python src-prototype\modular\validate_phase2.py --pet-dir data-dev\current-runtime\danhuang --json
```

注意：Phase 2 只读指定运行镜像，输出 Provider 摘要、待办统计和提醒时间轴预览，不输出真实 API Key。

## Phase 3 第二批已落地

当前已抽出动作资产、manifest 和 UI 状态模型纯逻辑：

- `assets/atlas.py`
- `assets/manifest.py`
- `ui/tk_right_menu.py`
- `ui/tk_bubble.py`
- `ui/tk_bubble_render.py`
- `ui/tk_pet_window.py`

验证命令：

```powershell
python -m unittest discover -s src-prototype\modular\tests
python src-prototype\modular\validate_phase3.py --pet-dir data-dev\current-runtime\danhuang --json
```

注意：Phase 3 当前仍只读 spritesheet、扩展动作条、`pet-family.json` 和设置文件，生成动作可用性、右键动作、扩展动作、右键主面板 layout/style/position、气泡样式、气泡 renderer 和窗口行为摘要，不替换图片、不写入运行配置。
