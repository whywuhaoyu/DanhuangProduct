# Tk 原型模块化拆分计划

## 目标

把当前 `run-danhuang-desktop-pet.py` 从单文件原型拆成可维护结构，保持行为不变，先拆再改。

## 当前结构风险

- 主文件 15,945 行。
- `DanhuangPet` 单类 429 个方法。
- `open_control_panel` 单方法约 3,874 行。
- UI、动画、AI、待办、导出、宠物资产、状态持久化混在同一个类。

## 第一阶段：纯数据和配置

状态：已落地。

目标目录：

```text
src-prototype/modular/core/
  pet_model.py
  companion_state.py
  settings_store.py
```

拆分范围：

- 宠物注册表读取。
- 当前宠物状态。
- 陪伴等级字段。
- settings 默认值和迁移。

验收：

- JSON 可解析。
- 默认值和当前行为一致。
- 不改变 C 盘运行数据。
- 验证入口：`python src-prototype\modular\validate_phase1.py --pet-dir archives\DanhuangPrototype-20260614-121543 --json`。
- 单元测试：`python -m unittest discover -s src-prototype\modular\tests`。

实现说明：

- `pet_model.py` 负责宠物注册表、动作元数据、扩展动作条和当前宠物摘要。
- `settings_store.py` 负责设置默认值、类型转换、范围夹取、气泡颜色校验、右键动作过滤和分发快照清理。
- `companion_state.py` 负责按宠物隔离的陪伴状态、旧全局状态迁移入口、等级计算和分发版空状态。
- 新模块默认值不写入本机私有绝对路径；读取已有 `pet-family.json` 时仍保留文件中的真实数据，便于归档验证。

## 第二阶段：AI 和待办

状态：已落地。

目标目录：

```text
src-prototype/modular/core/
  ai_providers.py
  todos.py
  reminder_history.py
```

拆分范围：

- Provider 配置读取和脱敏。
- API Key 本地加密边界。
- 待办增删改查。
- 提醒历史。

验收：

- Provider 列表可展示。
- 不输出密钥。
- 待办查询不会误判为新增。
- 验证入口：`python src-prototype\modular\validate_phase2.py --pet-dir data-dev\current-runtime\danhuang --json`。
- 单元测试：`python -m unittest discover -s src-prototype\modular\tests`。

实现说明：

- `ai_providers.py` 负责 Provider 默认配置、已保存配置规范化、当前 Provider 选择、连接地址拼接和公开摘要脱敏；真实加密 Key 只保留在受保护字段中，导出视图只暴露是否已保存。
- `todos.py` 负责待办默认值、时间文本解析、聊天新增意图、查询意图区分、完成/稍后/重复待办生成、到期待办筛选和本地查询回复。
- `reminder_history.py` 负责提醒事件规范化、最近事件截断、时间轴文本和分发版空状态。
- Phase 2 仍是模块化核心抽取，不改动单文件运行入口；后续运行集成时再把 Tk 主程序调用切到这些模块。

## 第三阶段：动作和窗口

状态：进行中，第二批 UI 状态模型已落地，右键菜单全量渲染合同、主面板样式/尺寸/定位模型、气泡定位、气泡图片 renderer 和基础窗口尺寸已开始接入 E 盘单文件运行镜像。

目标目录：

```text
src-prototype/modular/assets/
  atlas.py
  manifest.py
src-prototype/modular/ui/
  tk_pet_window.py
  tk_bubble.py
  tk_bubble_render.py
  tk_right_menu.py
```

拆分范围：

- spritesheet 加载和尺寸校验。
- 动作 manifest、扩展动作 strip 校验、右键动作可用性摘要。
- 动作状态机。
- 透明窗口。
- 气泡。
- 右键菜单。

验收：

- 启动后形象不变。
- 拖动、右键、气泡、多屏行为不退化。
- 动作尺寸和基线不变化。
- 验证入口：`python src-prototype\modular\validate_phase3.py --pet-dir data-dev\current-runtime\danhuang --json`。
- 单元测试：`python -m unittest discover -s src-prototype\modular\tests`。

已落地：

- `assets/atlas.py` 负责 spritesheet 网格、标准动作行、扩展动作 strip 尺寸、帧数和时长校验。
- `assets/manifest.py` 负责宠物动作 manifest、动作标签、复合跑动、右键动作选择和 family 级动作摘要。
- `ui/tk_right_menu.py` 负责右键快捷面板分组、基础动作、扩展动作、更多动作和窗口命令的纯 view model。
- `ui/tk_bubble.py` 负责气泡样式、颜色、尺寸估算、阴影色和屏幕内位置计算的纯 view model。
- `ui/tk_bubble_render.py` 负责 soft、rounded、cloud、thought、note、caption 六种气泡样式的 Pillow 图片绘制。
- `ui/tk_pet_window.py` 负责桌宠窗口尺寸、默认位置、屏幕夹取、置顶透明度和巡逻策略摘要。
- E 盘 `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py` 和 `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py` 已在 modular 模块存在时使用 `ui/tk_right_menu.py` 输出的基础动作、可见扩展动作和隐藏扩展动作；模块不可用时仍回退旧逻辑。
- 两份 E 盘单文件已进一步消费 `ui/tk_right_menu.py`：右键面板标题、副标题、常用入口、基础动作、扩展动作、更多动作 footer、窗口命令、按钮 variant、enabled 状态和自动关闭/外部点击延迟均优先来自 model；模块不可用时仍回退旧硬编码分组。
- 两份 E 盘单文件已开始消费 `ui/tk_right_menu.py` 的 pet switcher model：右键“切换形象”弹层的标题、当前宠物排序、最多展示数量、隐藏数量、空态和管理入口均优先来自 model；宠物照片仍由 Tk 渲染层按 `pet_id` 读取。
- 两份 E 盘单文件已开始消费 `ui/tk_right_menu.py` 的 popup layout 和定位模型：右键子弹层间距、屏幕边距、关闭延迟、更多动作展示上限、右侧优先和溢出翻左策略均优先来自 model；Tk 层仍负责实际窗口创建和 `place_window()`。
- 两份 E 盘单文件已开始消费 `ui/tk_right_menu.py` 的 style/layout/主面板定位模型：右键面板 shell/header/body、按钮 variant、禁用态、切换形象弹层选中态、更多动作弹层 footer、主面板宽度约束和避让宠物定位均优先来自 model；Tk 层仍负责实际控件创建。
- 两份 E 盘单文件已开始消费 `ui/tk_bubble.py`：气泡样式、文字颜色、文本宽度、显示时长和屏幕内位置由 view model 托管；Canvas 文本实测和逐字显示仍保留旧 Tk 路径。
- 两份 E 盘单文件已开始消费 `ui/tk_bubble_render.py`：气泡图片绘制优先使用 modular renderer；模块不可用或渲染失败时保留旧单文件绘制函数回退。
- 两份 E 盘单文件已开始消费 `ui/tk_pet_window.py`：基础窗口尺寸由 view model 托管，并暴露 `pet_window_view_model()` 供后续设计/验证读取；真实渲染尺寸、当前图片尺寸、拖动和多屏巡逻仍保留旧 Tk 路径。
- 新增 `tests/test_runtime_integration_phase3.py`，覆盖 legacy monolith 和 E 盘运行镜像的 modular UI 模型导入边界。

待拆：

- 继续把单文件 Tk 运行入口接入 `ui/tk_pet_window.py`：透明窗口属性、拖动、DPI、多屏行为和巡逻边界。
- 继续把单文件 Tk 运行入口接入气泡模块：关闭、逐字显示、预览和外观页实时渲染。
- 继续收敛 `ui/tk_right_menu.py` 接入：把右键窗口命令扩展为更完整的 view model，减少单文件内的 Tk 专用状态分支。

## 第四阶段：控制面板

目标目录：

```text
src-prototype/modular/ui/
  tk_panel.py
  pages/
    home.py
    pets.py
    companion.py
    behavior.py
    dialogue.py
    reminders.py
    generation.py
    safety.py
```

拆分范围：

- 固定框架。
- 左侧导航。
- 页面注册。
- 每个页面独立构建。

验收：

- 每页可打开。
- 滚动正常。
- 下拉和滑杆可操作。
- 页面失败时显示降级页并写日志。

## 每步固定验证

```powershell
python -m py_compile run-danhuang-desktop-pet.py
```

同时检查：

- `desktop-pet-settings.json`
- `pet-family.json`
- `companion-state.json`
- `danhuang-todos.json`
- `danhuang-ai-providers.json`

如果改动影响运行版，验证后重启：

```powershell
PowerShell -ExecutionPolicy Bypass -File "C:\Users\27176\.codex\pets\danhuang\start-danhuang-desktop-pet.ps1"
```
