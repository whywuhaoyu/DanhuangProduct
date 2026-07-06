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
| v1.20 | 2026-07-06 | 第二十七批执行：复制提示词反馈从系统弹窗改为 Toast，生成 0.11.71 发行包并只保留最新包 |
| v1.19 | 2026-07-06 | 第二十六批执行：添加现实照片窗口反馈从系统弹窗改为当前窗口 Toast，生成 0.11.70 发行包并只保留最新包 |
| v1.18 | 2026-07-06 | 第二十五批执行：形象页主形象和现实照片资产操作区网格化，生成 0.11.69 发行包并只保留最新包 |
| v1.17 | 2026-07-06 | 第二十四批执行：聊天窗口重复打开聚焦、聊天背景失败 Toast 和背景窗口快捷关闭，生成 0.11.68 发行包并只保留最新包 |
| v1.16 | 2026-07-06 | 第二十三批执行：到点提醒弹窗网格化、快捷键和焦点处理，生成 0.11.67 发行包并只保留最新包 |
| v1.15 | 2026-07-06 | 第二十二批执行：桌宠本体边缘巡游固定轴锁定和拖动方向清理，生成 0.11.66 发行包并只保留最新包 |
| v1.14 | 2026-07-06 | 第二十一批执行：导出安装包弹窗成功/失败/GitHub 前置错误从系统弹窗改为状态卡 + 面板 Toast，生成 0.11.65 发行包并只保留最新包 |
| v1.13 | 2026-07-06 | 第二十批执行：安全页个人备份/恢复/精灵图备份反馈从系统弹窗改为面板 Toast，生成 0.11.64 发行包并清理旧包 |
| v1.12 | 2026-07-05 | 第十九批执行：故事页删除确认和关键反馈从系统弹窗改为暖色面板组件，生成 0.11.63 发行包 |
| v1.11 | 2026-07-05 | 第十八批执行：动作页清空扩展动作精灵图确认从系统弹窗改为暖色面板确认，生成 0.11.62 发行包 |
| v1.10 | 2026-07-05 | 第十七批执行：形象页主像素图和参考图删除确认从系统弹窗改为暖色面板确认，生成 0.11.61 发行包 |
| v1.9 | 2026-07-05 | 第十六批执行：AI 清空陪聊记忆确认从系统弹窗改为暖色面板确认，生成 0.11.60 发行包 |
| v1.8 | 2026-07-05 | 第十四批执行：陪伴数据重置确认从系统弹窗改为暖色面板确认，生成 0.11.59 发行包 |
| v1.7 | 2026-07-05 | 第十三批执行：提醒删除确认从系统弹窗改为暖色面板确认，生成 0.11.58 发行包 |
| v1.6 | 2026-07-05 | 第十二批执行：提醒页未选中操作改为 Toast 反馈，稍后提醒文案人性化，生成 0.11.57 发行包 |
| v1.5 | 2026-07-05 | 第十一批执行：首次自动巡游遵守日常低打扰间隔，生成 0.11.56 发行包 |
| v1.4 | 2026-07-05 | 第十批执行：陪聊服务文案继续收口，聊天窗口输入区保持可见，生成 0.11.55 发行包 |
| v1.3 | 2026-07-05 | 第九批执行：陪聊设置页展示名与入口语言统一，生成 0.11.54 发行包 |
| v1.2 | 2026-07-05 | 第二批执行：重建当前根运行镜像，首页/行为/提醒/AI/安全高风险按钮区继续改为网格布局 |
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

- 首页：首屏展示当前宠物、陪伴等级、AI 状态、提醒摘要和 4-6 个快捷入口；0.11.59 已把陪伴数据重置确认改为暖色面板确认，后续继续下沉危险入口。
- 对话页：快速试聊、AI 状态、记忆、气泡样式使用统一卡片和按钮网格。
- 聊天窗：历史区单独滚动，底部输入区固定可见；快捷工具区用网格，不再横向硬塞。
- 聊天窗 0.11.68 已补重复打开后的恢复和输入框聚焦，聊天背景上传失败改为当前窗口 Toast，背景窗口支持 `Esc` 关闭。
- 提醒页：快速新增、筛选、列表卡片、编辑弹层和到点弹窗继续统一控件。
- 提醒页 0.11.57 已补未选中操作反馈和稍后提醒人性化文案；0.11.58 已把删除确认从系统弹窗改为暖色面板确认，后续继续补截图矩阵与键盘焦点。
- AI 页：Provider 状态、模型、Key、测试结果、资料查询状态和陪聊记忆清空继续状态化；0.11.60 已把清空记忆从系统弹窗改为暖色面板确认，错误给恢复动作。
- 形象页：当前宠物、分类摘要、现实照片、家人形象列表和操作按钮继续防窄列挤压；0.11.61 已把删除主像素图和删除参考图改为暖色面板确认，明确照片/副本删除边界。
- 形象页 0.11.69 已把当前主形象操作区和现实照片底部操作区改为共享按钮网格，避免资产操作在窄窗口横向挤压。
- 形象页 0.11.70 已把添加现实照片窗口的空提交和复制失败反馈改为当前窗口 Toast，并补 `Esc` 关闭和焦点提升。
- 形象/动作辅助链路 0.11.71 已把复制提示词、扩展动作提示词和使用教学的空内容、成功、失败反馈改为面板 Toast。
- 动作页：基础动作、扩展动作、推荐待补动作、上传 QA 结果分区展示；0.11.62 已把清空扩展动作精灵图改为暖色面板确认，明确动作页、右键动作栏和可播放动作边界。

### P2：低频页面和模块化

- 档案/故事：摘要卡、全文阅读器、状态 chip 抽成共享模式；0.11.63 已把删除故事确认和故事编辑器关键反馈改为暖色面板组件，明确只删除当前宠物的一条故事记录。
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

### 2026-07-05 第二批

- 目标线别：Tk/Python 线，当前根为 `E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk`。
- 运行镜像：已在当前根重建 `data-dev/current-runtime/danhuang/`，主程序由 `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py` 同步，资源从本机既有 Tk 运行资产复制；旧 `DanhuangProduct` 只作为本机资源来源，不再作为本批运行或打包目标。
- 改动内容：继续复用 `panel_button_grid()`，将首页/陪伴按钮、行为页预设与屏幕策略、提示词操作、提醒页常用时间和待办操作、安全页备份/导出操作、控制面板底部按钮改为固定列网格；AI 页 Provider 和测试结果操作改为网格布局。
- 反馈收敛：AI 页 Key 为空、Key 保存失败、测试前保存失败改为页内状态 + 暖色 Toast，避免继续弹系统消息框。
- 版本号：Tk 运行版更新到 `0.11.47`。
- Vue/Tauri 状态：未同步实现；本批不修改 `src-tauri-vue`。
- 验证状态：`py_compile`、27 个 modular 单元测试、`validate_phase3.py --pet-dir data-dev/current-runtime/danhuang --json` 已通过；截图和打包记录见打包文档。

### 2026-07-05 第三批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.48`。
- 审计口径：按付费用户 Beta 标准先处理可信安装、默认低打扰、控制面板收口、右键降噪入口、提醒反馈和公开包隐私边界，不继续堆新功能。
- 默认行为：发行包默认不置顶、低频说话、低速巡逻、边缘活动、多屏巡逻关闭；公开包配置不继承本机路径、GitHub 配置、跨屏设置和快捷动作。
- 主界面收口：默认导航只展示首页、对话、提醒、形象、动作、安全；高级模式再显示 AI、档案、故事、行为、操作、设置、巡逻、外观。
- 隐私边界：公开包 `pet-family.json` 只保留蛋黄，清空 `identity_image` 与 `reference_images`，不带用户上传源图、现实照片、身份参考图、跨宠物扩展动作或个人故事。
- 验证状态：legacy、运行镜像和发行包 `py_compile` 通过；28 个 modular 单元测试通过；当前运行镜像与发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8 无 BOM、隐私路径和密钥模式扫描通过。
- 截图状态：`qa/tk-ui-0.11.48-20260705/` 覆盖 14 个控制面板页、聊天窗口、右键菜单和提醒弹窗。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-122408/` 和 zip，旧 0.11.47 包未二次确认删除，记录为待清理。

### 2026-07-05 第四批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.49`。
- 审计口径：继续以付费用户全流程体验为准，优先修“桌宠会不会打扰我、我能不能立刻控制它”的信任问题。
- 严格问题：0.11.48 的行为页三档仍是旧开发者参数，安静模式没有真正关闭自动说话和巡游；首页也没有暴露陪伴强度。
- 改动内容：新增共享“陪伴模式”模型，安静、日常、活跃三档统一控制自动说话、自动巡游、巡游间隔、速度、范围、置顶和屏幕中心策略。
- 入口收口：首页新增陪伴模式卡片，行为页复用同一套模式入口，右键菜单新增“陪伴模式”分组；“暂停活动/恢复日常”也复用模式逻辑。
- 默认展示：公开包默认缩放从 `0.50` 收敛到 `0.46`，降低首次启动占屏和遮挡感。
- 验证状态：源码侧、当前运行镜像和发行包 `py_compile` 已通过；29 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8 无 BOM、隐私扫描、exe 8 秒启动烟测和截图矩阵已完成。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-131843/` 和 zip；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第五批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.50`。
- 审计口径：继续按付费用户可信度检查，优先修“模式显示和真实行为不一致”“普通用户看到开发者表单”的问题。
- 严格问题：旧设置文件缺失 `activity_mode` 时不会自动套用日常参数，导致运行镜像可能仍按旧的频繁说话、多屏巡游和进屏幕中心策略运行。
- 改动内容：旧设置缺失或无效 `activity_mode` 时迁移到日常低打扰边界；保留体型、气泡等视觉偏好，不保留旧的高打扰运动/说话参数。
- 设置收口：设置页改为本地文件夹卡片，当前桌宠目录内路径显示友好别名；GitHub macOS 构建工具默认折叠，保存和 workflow 写入使用面板 Toast。
- 验证状态：legacy、运行镜像和发行包 `py_compile` 已通过；30 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8 无 BOM、隐私扫描和 exe 8 秒启动烟测已完成。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-160513/` 和 zip；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第六批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.51`。
- 审计口径：继续按付费用户高频入口检查，优先修右键菜单在低矮屏幕过高、单宠包出现空入口的问题。
- 严格问题：0.11.50 右键菜单物理高度接近 941px，720p/768p 或远程桌面窗口下底部暂停/退出入口容易不可见。
- 严格问题：公开包是蛋黄单宠版，但右键菜单和包内说明仍提示“切换形象”，付费用户会认为这是无效功能或半成品。
- 改动内容：右键菜单布局改为 3 列紧凑布局，扩展动作主菜单只展示 3 个，其余进入“更多动作”；单宠包隐藏“切换形象”入口，多宠运行镜像保留。
- 使用说明：包内使用说明按导出宠物数量生成，单宠版只提示在形象页查看和管理资料，多宠包才提示右键切换。
- 验证状态：legacy 与运行镜像 `py_compile` 已通过；31 个 modular 单元测试通过；当前运行镜像 `validate_phase3.py` 输出右键布局 `columns=3/min_width=540/max_width=620` 且无 warnings。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-162937/` 和 zip；ZIP SHA256 `B4096078FACECCBD74A8E5AFE72F85A48E1BBC571ACF613AFA1E86FAF4932E01`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第七批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.52`。
- 审计口径：继续按付费用户小屏/远程桌面场景检查右键高频入口，要求暂停、隐藏气泡、退出不能被动作列表挤到不可见位置。
- 严格问题：0.11.51 虽然把菜单压到 3 列，但在 720 逻辑高度模拟下按钮区仍可能需要滚动；如果“窗口”分组在底部，用户必须先滚动才能暂停或退出，仍不合格。
- 改动内容：右键布局新增 `max_height_ratio=0.78` 和 `min_scroll_body_height=180`；Tk 渲染层把按钮区放入同色滚动容器，小屏时自动压高并支持鼠标滚轮。
- 入口收口：“窗口”分组前移到“常用”之后；“AI 配置”入口改名为“陪聊设置”，降低普通用户首屏工程感。
- 包边界：主程序 fallback 同步扩展动作上限为 3，并保留无 modular 目录时的高度计算，避免 PyInstaller 发行包离开发目录后行为漂移。
- 验证状态：legacy、运行镜像和最终发行包 `py_compile` 已通过；32 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均输出右键分组 `common/window/activity_modes/base_actions/extension_actions` 且无 warnings。
- 截图状态：已补最终发行包小屏模拟截图 `qa/tk-ui-0.11.52-20260705/16-right-menu-small-screen-scroll.png`；900x720 逻辑屏幕模拟下菜单为 `540x561`，`scrollable=true`，初始视图可见“暂停活动 / 隐藏气泡 / 退出”。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-164939/` 和 zip；ZIP SHA256 `AB7F239C26CE8870B51F4105EF6272B552D570D6590E969F208E28CAD52EF771`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第八批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.53`。
- 审计口径：继续按付费用户信任感检查 AI/陪聊入口和隐私安全页，要求无 Key 时不能显示已开启，本地路径不能像开发机调试页一样直接铺开。
- 严格问题：0.11.52 的 AI 页在 `Key 未配置` 时仍显示 `AI 对话 已开启`；安全页首屏直接展示包内 E 盘绝对路径，付费用户会认为产品泄露开发路径且状态不可信。
- 改动内容：新增 `ai_connection_summary()` 统一输出 `已关闭 / 待配置 / 已配置`；AI 页概览、对话页状态卡和首页/操作页入口改为“陪聊/云端陪聊/陪聊设置”；安全页通过 `local_path_label()` 展示“当前安装目录 / exports”等友好标签。
- 文案收口：导出弹窗、包内使用说明和 README 把“AI 配置”改为“陪聊服务配置”，保留 Key、模型、Base URL 等必要技术字段但不把普通入口做成 API 调试台。
- 验证状态：legacy、运行镜像和包内 app `py_compile` 已通过；32 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内数据级隐私扫描未发现真实 Key、DPAPI 密文、日志文件或私有路径。
- 截图状态：已补最终发行包截图 `qa/tk-ui-0.11.53-paid-trust-20260705/`，覆盖对话、AI 和安全页；AI 页显示“云端陪聊 / 待配置”，安全页显示“当前安装目录 / exports”。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-170551/` 和 zip；ZIP SHA256 `63FCF47D18D6672148E560F2658666EE2E3CE73D1D1596B47661629CC5A0C163`；EXE SHA256 `CFE0E33D88C1EAFFC058EC0742622481E9BA3B8CD3DBED71468657A758A20237`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第九批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.54`。
- 审计口径：继续按付费用户语言一致性检查入口和落地页，要求“陪聊设置”入口进入后不能再显示裸 `AI` 页面标题。
- 严格问题：0.11.53 右键、首页和说明文档已经收口为“陪聊设置/云端陪聊”，但控制面板页面标题仍显示 `AI`，像开发者内部页，破坏信任感。
- 改动内容：新增控制面板 `page_labels` 和 `page_label()`，内部页面 key 仍为 `AI`，但侧栏、页面标题和缺页提示展示为“陪聊设置”；新增“陪聊设置 / 云端陪聊”别名。
- 验证状态：legacy、运行镜像和包内 app `py_compile` 已通过；32 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8 无 BOM、隐私扫描和 exe 8 秒烟测通过。
- 截图状态：已补最终发行包截图 `qa/tk-ui-0.11.54-paid-language-20260705/ai-page-label.png`，页面标题显示“陪聊设置”。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-172236/` 和 zip；ZIP SHA256 `667C7513B33113AF31660AA42E1BB50B95C911BF339A34AA2B213956FC4C8632`；EXE SHA256 `DAB8003C2B01ED838D530722A525BEF22ABCFBBB0DFB925E162C68429B090B13`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第十批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.55`。
- 审计口径：继续按付费用户聊天路径检查，要求包内说明、聊天状态和连接测试反馈不用工程化故障词；聊天窗口在 560x680 下输入框必须可见。
- 严格问题：0.11.54 的使用说明、聊天 composer 和测试 Toast 已经比过去好，但仍残留接口调试口吻；同时截图发现聊天角色区把底部输入区挤出首屏。
- 改动内容：使用说明、发送提示、测试 Toast、Key 缺失、云端失败和资料整理状态统一为“云端陪聊 / 陪聊服务”；聊天窗口移出默认角色详细说明，保留当前角色摘要，聊天历史区初始高度降到 160。
- 验证状态：legacy、运行镜像和包内 app `py_compile` 已通过；32 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8 无 BOM、隐私扫描和 exe 8 秒烟测通过。
- 截图状态：已补最终发行包截图 `qa/tk-ui-0.11.55-paid-copy-20260705/chat-composer-copy-final-scaled.png`，输入框、发送按钮和“当前云端陪聊/本地陪伴”提示可见。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-173901/` 和 zip；ZIP SHA256 `8DFA38BC2A5A6E38D3908058C4648E63C8345D2A1AB13DAAC85FE3A845D74816`；EXE SHA256 `385ADD30621F437DD901155006BFAB32D3C68154BDF4015EDA1A5E8F22D03BD6`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第十一批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.56`。
- 审计口径：继续按付费用户桌宠本体体验检查，要求默认日常模式不能刚启动就自动乱动，自动巡游必须和首页/右键承诺的低打扰参数一致。
- 严格问题：0.11.55 初始化仍写死 `random.uniform(2.0, 4.0)`，导致 `roam_interval=120` 的日常模式在首次启动 2-4 秒后就可能开始自动巡游。
- 改动内容：新增 `next_roam_timestamp()`，`DanhuangPet.__init__()` 的首次自动巡游调度改为 `self.next_roam_time()`；后续调度继续复用同一 helper。
- 验证状态：legacy、运行镜像和包内 app `py_compile` 已通过；33 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8 无 BOM、隐私扫描和 exe 8 秒桌面烟测通过。
- 截图状态：已补最终发行包桌面烟测截图 `qa/tk-ui-0.11.56-motion-20260705/exe-smoke-desktop.png`；调度证据 `qa/tk-ui-0.11.56-motion-20260705/initial-roam-schedule.json` 显示 legacy、运行镜像、发行包日常模式首次自动巡游延迟均为 84-162 秒。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-174959/` 和 zip；ZIP SHA256 `3D44E5CD842EF16F51FC7B8B39D0CD048579370A9E52F472BCAAC3430B9E5EFB`；EXE SHA256 `BA1E6AFC7D1657276EBEC8FE9B2624150BF6CF4D311C05BC0D496C973A065DD7`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第十六批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.60`。
- 审计口径：继续按付费用户隐私信任检查陪聊设置页，要求“清空记忆”不能使用割裂的 Windows 系统确认框，且必须明确不会误删 Key、提醒、待办或陪伴等级。
- 严格问题：0.11.59 的陪伴重置已经统一确认体验，但 AI 页“清空记忆”仍直接调用 `messagebox.askyesno`；对纪念型桌宠用户来说，这是高敏隐私操作，文案不足会让用户担心误删更大范围数据。
- 改动内容：`clear_ai_memory()` 接入 `show_panel_confirm()`，确认卡说明只清空当前形象的最近聊天、长期记忆摘要和学习表达；清空成功后显示面板 Toast 并保留蛋黄气泡反馈。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；37 个 modular 单元测试通过；当前运行镜像与发行包 `validate_phase3.py` 均无 warnings；包内 JSON、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.60-ai-memory-confirm-20260705/ai-memory-confirm-evidence.json`、`qa/tk-ui-0.11.60-ai-memory-confirm-20260705/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-183625/` 和 zip；ZIP SHA256 `7A17B72AB8F081EDA9E80CC7FF3AA2B27114C7AA4350EF22B677EF9BFD4E1513`；EXE SHA256 `750762F8AF2ED89DBB25CCE0F6A8B640FEA284EBEC0694033AB1370755C94520`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第十七批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.61`。
- 审计口径：继续按付费用户纪念资产安全检查形象页，要求删除主像素图和参考照片时不能出现割裂的系统确认框，并且必须把“删除的是副本还是源文件”说清楚。
- 严格问题：0.11.60 已收敛提醒、陪伴和陪聊记忆确认，但形象页仍用 `messagebox.askyesno` 删除主像素图和参考图；用户会担心误删现实照片、故事记录或动作资源。
- 改动内容：`clear_pet_identity_image()` 和 `remove_reference_image_from_pet()` 接入 `show_panel_confirm()`；未设置主像素图时改为面板 Toast；确认卡分别说明主像素图副本、参考图上传副本和外部源文件边界。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；38 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.61-pet-asset-confirm-20260705/pet-asset-confirm-evidence.json`、`qa/tk-ui-0.11.61-pet-asset-confirm-20260705/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-184801/` 和 zip；ZIP SHA256 `7DF0A9CC7B6A917F62E8F26F63F74444CEEF5527BAED74252F916454A9E56DA7`；EXE SHA256 `E9D4F7AF7924C25F24A7C1FBE4E198E824EEC47A9178EA64BC4C33BB38659118`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第十八批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.62`。
- 审计口径：继续按付费用户动作资产安全检查动作页，要求“清空动作精灵图”不能使用割裂的系统确认框，并且必须说明会影响动作页、右键动作栏和可播放动作。
- 严格问题：0.11.61 已收敛形象资产删除确认，但动作页清空扩展动作仍用 `messagebox.askyesno`；用户会担心误删基础动作、形象照片或聊天记忆，也不清楚右键动作会不会同步移除。
- 改动内容：`remove_extension_action_asset()` 接入 `show_panel_confirm()`；未上传精灵图时改为面板 Toast；确认卡说明只清理当前形象的扩展动作副本，清空后可重新上传。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；39 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.62-action-clear-confirm-20260705/action-clear-confirm-evidence.json`、`qa/tk-ui-0.11.62-action-clear-confirm-20260705/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-185625/` 和 zip；ZIP SHA256 `B0A8B21A2500CB815B93897E13B88621C4AAC95A0EC8568005F517AFB1EB703C`；EXE SHA256 `E55B05562723023E9B6C70AF49235E769DA83C3FEFBDE1E117C150D7E8FB9334`；旧包未二次确认删除，记录为待清理。

### 2026-07-05 第十九批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.63`。
- 审计口径：继续按付费用户纪念内容体验检查故事页，要求删除故事、空内容、图片/背景失败、无 AI 和生成失败不能再弹系统窗口。
- 严格问题：0.11.62 已收敛动作资产确认，但故事页仍在删除、空内容、无 AI/无故事等路径使用 `messagebox`；用户写纪念故事时被系统弹窗打断，且删除边界不够像产品。
- 改动内容：`delete_story()` 接入 `show_panel_confirm()`；`show_panel_toast()` 新增可选 `parent`；故事编辑器和摘要/角色提示词提示改为面板 Toast。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；40 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.63-story-feedback-20260705/story-feedback-evidence.json`、`qa/tk-ui-0.11.63-story-feedback-20260705/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260705-191215/` 和 zip；ZIP SHA256 `30AD25B5B1C32826F864550BAC06FECD2D2C5544967E64872413999D5B9F7DED`；EXE SHA256 `A56AFE11A4D077ADBFA0ECF4FE4727C1DADA91F5A26E26E518EB90E45C1C3C20`；旧包未二次确认删除，记录为待清理。

### 2026-07-06 第二十批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.64`。
- 审计口径：继续按付费用户本地数据信任检查安全页，要求个人备份、恢复配置和备份精灵图不能再用割裂的系统错误框或静默成功。
- 严格问题：0.11.63 已收敛故事页，但安全页个人备份仍在恢复失败和精灵图缺失时使用 `messagebox.showerror`；导出/备份成功只让宠物说话，用户无法确认文件落到哪里。
- 改动内容：`export_configuration()`、`restore_configuration()`、`backup_spritesheet()` 接入面板 Toast；恢复配置补非法 JSON/不可读文件降级提示；成功提示展示友好路径标签。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；41 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.64-safety-backup-feedback-20260706/safety-backup-feedback-evidence.json`、`qa/tk-ui-0.11.64-safety-backup-feedback-20260706/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260706-204857/` 和 zip；ZIP SHA256 `9EE8176BF939C2D10C1F60C509843AEBA671E51DBDD5046BDCA2513BFB2A5FC1`；EXE SHA256 `9BA8968EA7BBAC8DEB5E7F0C0DEE913679DE7A61A3A1EB846A26BE0F120CFBFB`。
- 包清理状态：按用户最新要求，`packages/` 只保留最新一组 Tk Windows 包目录和 zip；本批已删除 42 个旧 `danhuang-desktop-pet-windows-*` 目录/zip。

### 2026-07-06 第二十一批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.65`。
- 审计口径：继续按付费用户公开分发和安装信任检查安全页，要求导出安装包弹窗的成功、失败和 GitHub 前置错误不能再弹割裂的 Windows 系统窗口。
- 严格问题：0.11.64 已收敛个人备份反馈，但导出安装包弹窗仍在导出完成、导出失败、缺少 GitHub 仓库/Token、macOS 远端构建结果和 workflow 写入路径使用 `messagebox`，付费用户会感觉这是开发工具而不是可交付产品。
- 改动内容：导出安装包弹窗复用 `set_export_status()` 和 `show_panel_toast(parent=window)`；Token 保存、workflow 写入、Windows/macOS 导出结果和 GitHub 前置错误统一为状态卡 + Toast。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；42 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.65-installer-export-feedback-20260706/installer-export-feedback-evidence.json`、`qa/tk-ui-0.11.65-installer-export-feedback-20260706/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260706-210701/` 和 zip；ZIP SHA256 `24F268CC65760B2F8EDBD142FA0067D938169495F9CADE13A76D7FEFDF5B9FEA`；EXE SHA256 `91129C3F83A8C6E66953A73115BF2396FE841191807EB894CCF8CBD36C3226E8`。
- 包清理状态：按用户最新要求，`packages/` 只保留最新一组 Tk Windows 包目录和 zip；旧 0.11.64 包已删除。

### 2026-07-06 第二十二批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.66`。
- 审计口径：继续按付费用户桌面本体体验检查运动手感，要求边缘巡游不能逐渐向屏幕中间偏移，拖动松手后不能残留错误左右跑动方向。
- 严格问题：前序批次主要收敛控制面板和弹窗；桌宠本体运动仍缺少边缘固定轴的可测试保障，且惯性结束没有显式清理拖动方向状态。
- 改动内容：新增 `lock_edge_roam_position()` 纯函数；边缘巡游目标写入 `edge` 并在 `update_roam()` 每帧锁轴；`stop_position_motion()`、进入惯性和惯性结束时清理拖动方向。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；44 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.66-pet-motion-edge-lock-20260706/pet-motion-edge-lock-evidence.json`、`qa/tk-ui-0.11.66-pet-motion-edge-lock-20260706/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260706-211839/` 和 zip；ZIP SHA256 `B99C42C1981B0F05225DBE1956400AB843106E6AF246B8AE946AACF845C320A3`；EXE SHA256 `EC10930053D9EF34F727F25BE7B5C74F502226C431406FBC2C8F46244D7B11F4`。
- 包清理状态：按用户最新要求，`packages/` 只保留最新一组 Tk Windows 包目录和 zip；旧 0.11.65 包已删除。

### 2026-07-06 第二十三批

- 目标线别：Tk/Python 线，版本号更新到 `0.11.67`。
- 审计口径：继续按付费用户提醒依赖场景检查到点弹窗，要求用户能快速完成、稍后或关闭，不被横向挤压按钮和弱焦点打断。
- 严格问题：旧到点提醒弹窗虽然已是暖色卡片，但状态 chip 和操作按钮仍偏横向堆叠；窗口出现后没有明确焦点和键盘快捷处理，用户需要精细点击才能完成/稍后。
- 改动内容：到点提醒弹窗状态 chip、主操作和稍后提醒改为固定网格；新增 `Ctrl+Enter` 完成、`1/2/3` 稍后提醒、`Esc` 关闭；弹窗打开后置顶、获取焦点并聚焦“完成”，关闭时清理 `self.reminder_popup`。
- 验证状态：legacy、当前运行镜像和发行包 app `py_compile` 已通过；45 个 modular 单元测试通过；当前运行镜像和发行包 `validate_phase3.py` 均无 warnings；包内 JSON、UTF-8、真实隐私扫描、zip 缓存残留检查和 exe 8 秒桌面烟测已完成。
- 截图状态：已补 QA 证据和桌面烟测截图 `qa/tk-ui-0.11.67-reminder-popup-shortcuts-20260706/reminder-popup-shortcuts-evidence.json`、`qa/tk-ui-0.11.67-reminder-popup-shortcuts-20260706/exe-smoke-desktop.png`。
- 打包状态：已生成 `packages/danhuang-desktop-pet-windows-20260706-212948/` 和 zip；ZIP SHA256 `04F0DB5EBCB602D5C880BE4DCF06613A56CAE195715D9E18EE183E820E53D2BD`；EXE SHA256 `82F2EA4F91512143DAD7CD705BA8A85794E2197CC877B299000B1B66F4326C10`。
- 包清理状态：按用户最新要求，`packages/` 只保留最新一组 Tk Windows 包目录和 zip；旧 0.11.66 包已删除。
