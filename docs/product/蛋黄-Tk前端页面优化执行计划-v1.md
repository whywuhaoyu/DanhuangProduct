# 蛋黄 Tk 前端页面优化执行计划 v1

## 文档状态

- 状态：已确认
- 适用范围：Tk/Python 线，E 盘运行镜像与 Tk 原型拆分实验
- 目标线别：Tk/Python 线
- 当前分支：`tk/main`
- 日期：2026-07-03
- 输入来源：用户要求继续优化当前 Tk 版本前端页面、当前代码与文档调研、Tk UI 截图问题反馈

## 版本记录

| 版本 | 日期 | 更新内容 |
| --- | --- | --- |
| v1.1 | 2026-07-03 | 第一批执行：对话页快捷按钮和 AI 操作按钮改为统一网格，降低窄窗口挤压风险 |
| v1 | 2026-07-03 | 固化 Tk 前端页面优化执行计划、验收矩阵、文档和 GitHub 提交边界 |

## 核心结论

当前本机工作分支是 `tk/main`，本轮只优化 Tk/Python 版本。Vue/Tauri 与 Tk 是平级版本，后续按 `vue/main` 单独推进，不把 Tk 页面实现直接改到 Vue，也不在 Tk 分支里改 Vue 代码。

Tk 控制面板已经具备暖色 Shell、分组导航、滚动正文、分类体系和部分页面降密度改造，但仍存在四类问题：

- 页面内部仍有较多横向 `pack(side="left")`，小宽度下容易挤压、竖排或遮挡。
- `messagebox`、裸 `tk.Button`、裸 `tk.Entry` 和局部 `modal_button` 仍分散存在，反馈体验不统一。
- 截图验收基线不完整，之前出现过“按钮挤在一起”“聊天输入框被挤掉”后才被发现。
- 控件体系还没有稳定资产化，后续页面优化容易重复造控件。

## 背景与问题

用户已明确当前主要优化 Tk 版本，并要求后续文档输出也要提交，同时 Tk 和 Vue 两个版本在 GitHub 上要区分维护。

当前 Tk 主程序仍集中在：

```text
data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py
```

模块化实验目录已经抽出部分纯逻辑和 UI 状态模型：

```text
src-prototype/modular/core/
src-prototype/modular/ui/
```

因此本轮优化不能只做视觉颜色调整，而要按“截图基线 -> 共享控件 -> 高频页面 -> 文档与打包”的顺序推进。

## 目标与非目标

目标：

- 建立 Tk 页面截图验收矩阵，防止挤压、遮挡和输入框丢失反复出现。
- 收敛 Tk 控件和反馈组件，减少页面内重复的按钮、输入框、弹窗写法。
- 优先优化首页、对话/聊天窗、提醒、AI、形象、动作这些高频页面。
- 每个批次完成后同步中文文档、验证结果和 Tk 包记录。
- 后续 GitHub 提交按 Tk/Vue 线别分开，不互相覆盖。

非目标：

- 本轮不开发 Vue/Tauri 页面。
- 本轮不引入 CustomTkinter、ttkbootstrap、PySide6 或 pywebview 作为正式依赖。
- 本轮不重做 spritesheet、不改变动作 ID、不迁移宠物目录。
- 本轮不把 `data-dev/`、`packages/`、隐私数据和本机日志提交到 GitHub。

## 功能范围

### P0：截图基线和页面防挤压

- 为控制面板建立截图矩阵：`首页 / 对话 / AI / 提醒 / 形象 / 动作 / 档案 / 故事 / 操作 / 安全 / 外观`。
- 每页至少覆盖 920x640 基准窗口；对历史出问题区域额外覆盖 900 宽、760 宽或聊天窗 520 宽。
- 验收重点固定为：按钮文字不竖排、状态 chip 不重叠、长说明不横向溢出、底部输入区不消失。
- 页面切换后滚动位置必须回到顶部。

### P0：共享 Tk 控件收敛

先在主程序内收敛，再迁移到模块化目录：

- `PanelButton`：统一 `primary / neutral / ghost / selected / danger / disabled / loading`。
- `PanelEntry`：统一输入框背景、边框、焦点态和错误提示位置。
- `PanelSelect`：统一下拉，优先修共享 `select_box()`，不逐页打补丁。
- `PanelCard`：统一卡片标题、说明、内容和危险区。
- `StatusPill`：状态必须有文字，不只靠颜色表达。
- `ActionGrid`：替代单行横向按钮堆叠，支持固定列数和换行。
- `PanelDialog`：替代高频 `messagebox`，支持确认、错误、成功和进度。
- `PanelToast`：用于保存、测试、复制、导出等轻反馈。

### P1：高频页面优化

- 首页：首屏展示当前宠物、陪伴等级、AI 状态、提醒摘要和 4-6 个快捷入口。
- 对话页：快速试聊、AI 状态、记忆、气泡样式使用统一卡片和按钮网格。
- 聊天窗：历史区单独滚动，底部输入区固定可见；快捷工具区用网格，不再横向硬塞。
- 提醒页：快速新增、筛选、列表卡片、编辑弹层和到点弹窗继续统一控件。
- AI 页：Provider 状态、模型、Key、测试结果和资料查询状态继续状态化，错误给恢复动作。
- 形象页：当前宠物、分类摘要、现实照片、家人形象列表和操作按钮继续防窄列挤压。
- 动作页：基础动作、扩展动作、推荐待补动作、上传 QA 结果分区展示。

### P2：低频页面和模块化

- 档案/故事：摘要卡、全文阅读器、状态 chip 抽成共享模式。
- 操作/安全/外观：统一按钮、确认弹窗、导出状态和气泡颜色预览。
- 稳定后把 Tk 控件工厂迁移到：

```text
src-prototype/modular/ui/tk_panel.py
```

并补充模块化单元测试。

## 交互入口

- 桌宠右键菜单：打开控制面板指定页面，例如 `提醒`、`AI`、`形象`、`动作`。
- 控制面板左侧导航：按 `日常 / 宠物资产 / 行为设置 / 设置与安全 / 高级` 分组。
- 聊天窗：从右键、首页、对话页进入，必须保持输入框可见。
- 安全页：保留导出安装包入口，但公开包继续排除隐私数据。

## 关键规则

- 当前分支是 `tk/main` 时，只改 Tk/Python 相关源码、文档和 Tk 验收记录。
- Vue/Tauri 线后续只在 `vue/main` 或 `feature/vue/*` 中处理。
- 共享产品契约可以同步到 `main`，但必须注明 Tk/Vue 两边同步状态。
- 每次 UI 改动后都要更新中文文档，不能只在聊天里说明。
- 每次 Tk 功能或 UI 批次完成后，都要重新打 Tk Windows exe，本地只保留最新包。
- 不提交 `data-dev/`、`packages/`、`archives/`、`node_modules/`、`target/`、API Key、DPAPI、聊天、待办、提醒历史和本机路径。

## 验收标准

- `python -m py_compile data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py` 通过。
- `python -m unittest discover -s src-prototype/modular/tests` 通过。
- `python src-prototype/modular/validate_phase3.py --pet-dir data-dev/current-runtime/danhuang --json` 无 warnings。
- 关键 JSON 可解析且 UTF-8 无 BOM。
- 目标页面截图进入 `qa/`，文件名包含 `tk`、页面、窗口尺寸和日期。
- 控制面板能从 E 盘运行镜像打开；右键菜单内部按钮能打开目标页面。
- 聊天窗底部输入框、发送按钮和快捷工具区在 520 宽截图中可见。
- Git diff 中不包含 Vue/Tauri 代码改动，除非本次明确是共享文档。

## 风险与取舍

- Tk 单文件较大，直接大拆分风险高；本轮先收敛控件，再模块化迁移。
- 截图自动化对 Windows 桌面窗口依赖较强，第一阶段允许人工截图，但必须留文件。
- `messagebox` 全量替换可能影响流程；优先替换控制面板内高频确认和错误反馈。
- `packages/` 不提交到 GitHub，包共享后续走 GitHub Releases 或本地拷贝。

## 待确认事项

- 是否需要把截图验收自动化为脚本，而不是人工留图。
- 是否需要为 `tk/main` 和 `vue/main` 分别建立 GitHub PR 模板。
- 是否需要把 Tk 控件 token 输出成单独设计规格，便于 Vue 后续复用。

## 执行记录

### 2026-07-03 第一批

- 目标线别：Tk/Python 线。
- 代码范围：`data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py` 与 `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`。
- 改动内容：新增控制面板内部 `panel_button_grid()`，将对话页“快速试聊”快捷按钮和“AI 与记忆”操作按钮改为 4 列网格，按钮自动换行，不再依赖单行横向堆叠。
- 版本号：Tk 运行版更新到 `0.11.46`，用于区分本批 UI 优化包。
- Vue/Tauri 状态：未同步实现；后续 Vue 线需要在 `vue/main` 中按同样交互原则单独处理。
- 打包记录：见 `docs/product/蛋黄-Tk前端页面优化打包记录-v1.md`。
