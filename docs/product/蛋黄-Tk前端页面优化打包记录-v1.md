# 蛋黄 Tk 前端页面优化打包记录 v1

## 文档状态

- 状态：已确认
- 适用范围：Tk/Python 线，Windows 免 Python exe 包
- 目标线别：Tk/Python 线
- 日期：2026-07-06
- 输入来源：Tk 前端页面优化、付费用户严苛审计收口、用户要求每次优化后生成 Tk exe 包

## 版本记录

| 版本 | 日期 | 更新内容 |
| --- | --- | --- |
| v1 | 2026-07-03 | 记录 0.11.46 Tk 前端页面优化包路径、哈希和验证结果 |
| v2 | 2026-07-05 | 记录 0.11.47 Tk 前端网格加固包路径、哈希、截图和验证结果 |
| v3 | 2026-07-05 | 记录 0.11.48 付费 Beta 收口包路径、哈希、截图矩阵和隐私边界修正 |
| v4 | 2026-07-05 | 记录 0.11.49 陪伴模式加固包路径、哈希、截图矩阵和右键菜单宽度修正 |
| v5 | 2026-07-05 | 记录 0.11.50 设置可信度和旧配置迁移包路径、哈希、截图和验证结果 |
| v6 | 2026-07-05 | 补充 0.11.50 DPI 修正截图证据和透明 Tk 窗口截图规则，不新增包 |
| v7 | 2026-07-05 | 记录 0.11.51 右键紧凑菜单和单宠空入口修复包路径、哈希和验证结果 |
| v8 | 2026-07-05 | 记录 0.11.52 右键小屏滚动兜底、窗口操作前移、最终包哈希和截图证据 |
| v9 | 2026-07-05 | 记录 0.11.53 陪聊状态可信度、安全页路径去工程化、最终包哈希和截图证据 |
| v10 | 2026-07-05 | 记录 0.11.54 陪聊设置语言一致性、最终包哈希和截图证据 |
| v11 | 2026-07-05 | 记录 0.11.55 陪聊文案收口、聊天输入区可见性、最终包哈希和截图证据 |
| v12 | 2026-07-05 | 记录 0.11.56 首次自动巡游低打扰修复、最终包哈希和桌面烟测证据 |
| v13 | 2026-07-05 | 记录 0.11.57 提醒操作反馈和稍后提醒文案修复、最终包哈希和桌面烟测证据 |
| v14 | 2026-07-05 | 记录 0.11.58 提醒删除确认统一、最终包哈希和桌面烟测证据 |
| v15 | 2026-07-05 | 记录 0.11.59 陪伴数据重置确认统一、最终包哈希和桌面烟测证据 |
| v16 | 2026-07-05 | 记录 0.11.60 AI 清空记忆确认统一、最终包哈希和桌面烟测证据 |
| v17 | 2026-07-05 | 记录 0.11.61 形象资产删除确认统一、最终包哈希和桌面烟测证据 |
| v18 | 2026-07-05 | 记录 0.11.62 动作精灵图清空确认统一、最终包哈希和桌面烟测证据 |
| v19 | 2026-07-05 | 记录 0.11.63 故事页删除确认和关键反馈统一、最终包哈希和桌面烟测证据 |
| v20 | 2026-07-06 | 记录 0.11.64 安全页个人备份反馈统一、最终包哈希、桌面烟测和旧包清理证据 |

## 核心结论

已基于 Tk 版本 `0.11.64` 在当前根 `E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk` 生成新的 Windows 免 Python exe 包。包产物仍留在本机 `packages/`，不进入 GitHub 代码仓库；GitHub 只提交本记录和源码/文档变更。

按照用户最新要求，`packages/` 每次打包后只保留最新一组 Tk Windows 包目录和 zip。本批新包验证通过后，已删除 42 个旧 `danhuang-desktop-pet-windows-*` 目录/zip。

本批发行包按“蛋黄单宠版”处理：`pet-family.json` 只包含 `danhuang`，`identity_image=""`，`reference_images=[]`，不带用户上传源图、现实照片、身份参考图、个人故事或跨宠物扩展动作。

0.11.64 的新增重点是安全页个人数据操作可信度：导出配置、恢复配置和备份精灵图统一使用面板 Toast；恢复失败和精灵图缺失不再弹出 Windows 系统错误框，成功后显示友好路径标签。

## 包路径

```text
E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk\packages\danhuang-desktop-pet-windows-20260706-204857
E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk\packages\danhuang-desktop-pet-windows-20260706-204857.zip
```

## 哈希

```text
ZIP SHA256: 9EE8176BF939C2D10C1F60C509843AEBA671E51DBDD5046BDCA2513BFB2A5FC1
EXE SHA256: 9BA8968EA7BBAC8DEB5E7F0C0DEE913679DE7A61A3A1EB846A26BE0F120CFBFB
```

## 包含资源

- Tk 主程序：`run-danhuang-desktop-pet.py`
- 默认蛋黄资源：`spritesheet.webp`、`pet.json`、图标、对话库、灵魂设定、提示词包
- 干净模板数据：设置、陪聊服务 Provider 预设、空待办、空提醒历史、空聊天记忆、空陪伴状态
- Windows 一键构建和安装脚本
- 免 Python exe：`app/dist/DanhuangDesktopPet/DanhuangDesktopPet.exe`

## 排除的个人数据

- API Key、DPAPI 密文
- 聊天记忆、长期记忆、待办、提醒历史
- 个人故事、用户源图、现实照片、身份参考图
- 本机日志和本机路径
- 其他未勾选宠物资源

## 验证入口

- `python -m py_compile` 覆盖 legacy monolith、E 盘运行镜像和发行包 app。
- `python -m unittest discover -s src-prototype/modular/tests` 通过 41 个测试。
- 当前运行镜像 `validate_phase3.py` 输出 5 个 ready 宠物、54 个可播放动作、11 个扩展动作，右键菜单布局为 `columns=3/min_width=540/max_width=620/max_height_ratio=0.78`，分组顺序为 `common/window/activity_modes/base_actions/extension_actions`，`warnings` 为空。
- 发行包 `validate_phase3.py --pet-dir packages/danhuang-desktop-pet-windows-20260706-204857/app --json` 输出 1 个 ready 宠物、19 个蛋黄动作、0 个扩展动作，右键菜单布局 `columns=3/min_width=540/max_width=620/max_height_ratio=0.78`，分组顺序为 `common/window/activity_modes/base_actions/extension_actions`，`warnings` 为空。
- 包内 29 个 JSON 可解析；源码、文档和本批发行包内文本文件未检测到 UTF-8 BOM 或非法 UTF-8。
- 包内 `manifest.json` 显示 `app_version=0.11.64`、`python_bundled=true`、`windows_exe=app/dist/DanhuangDesktopPet/DanhuangDesktopPet.exe`、`missing_assets=[]`。
- 包内默认设置显示 `activity_mode=daily`、`scale=0.46`、`talk_interval=150.0`、`roam_interval=120.0`、`multi_monitor_roam=false`、`roam_allow_center=false`。
- 包内临时 `app/build`、`app/__pycache__` 和 `app/DanhuangDesktopPet.spec` 已清理；最终 zip 内无 `build`、`.spec`、`__pycache__` 残留。
- 包内 48 个文本文件真实隐私扫描未发现 API Key、DPAPI 加密 blob、Token、本机路径或日志文件；空待办、空提醒、空聊天记忆、初始陪伴模板和 `reference_images=[]` 已确认。
- 0.11.64 安全页个人备份反馈证据：`qa/tk-ui-0.11.64-safety-backup-feedback-20260706/safety-backup-feedback-evidence.json`。legacy 和当前运行镜像均显示“导出配置 / 恢复配置 / 备份精灵图”反馈已接入 `show_panel_toast()`，且旧 `messagebox.showerror("恢复失败"` 和 `messagebox.showerror("备份失败"` 已移除。
- 0.11.63 故事页反馈确认证据：`qa/tk-ui-0.11.63-story-feedback-20260705/story-feedback-evidence.json`。legacy 和当前运行镜像均显示“删除故事”已接入 `show_panel_confirm()`，故事保存、空内容、图片/背景失败、无 AI/无故事和生成失败提示已接入面板 Toast，且旧 `messagebox.askyesno("删除故事"` 已移除。
- 0.11.62 动作精灵图清空确认证据：`qa/tk-ui-0.11.62-action-clear-confirm-20260705/action-clear-confirm-evidence.json`。legacy 和当前运行镜像均显示“清空动作精灵图”已接入 `show_panel_confirm()`，且旧 `messagebox.askyesno("清空动作精灵图"` 已移除。
- 0.11.61 形象资产删除确认证据：`qa/tk-ui-0.11.61-pet-asset-confirm-20260705/pet-asset-confirm-evidence.json`。legacy 和当前运行镜像均显示“删除主像素图 / 删除参考图”已接入 `show_panel_confirm()`，且旧 `messagebox.askyesno("删除主像素图"` 和 `messagebox.askyesno("删除参考图"` 已移除。
- 0.11.60 AI 清空记忆确认证据：`qa/tk-ui-0.11.60-ai-memory-confirm-20260705/ai-memory-confirm-evidence.json`。legacy 和当前运行镜像均显示“清空陪聊记忆”已接入 `show_panel_confirm()`，且旧 `messagebox.askyesno(f"清空{self.active_pet_name()}记忆"` 已移除。
- 0.11.59 陪伴重置确认证据：`qa/tk-ui-0.11.59-companion-reset-confirm-20260705/companion-reset-confirm-evidence.json`。legacy 和当前运行镜像均显示“重置陪伴数据”已接入 `show_panel_confirm()`，且旧 `messagebox.askyesno("重置陪伴数据"` 已移除。
- exe 8 秒桌面启动烟测通过，截图见 `qa/tk-ui-0.11.64-safety-backup-feedback-20260706/exe-smoke-desktop.png`；结束后无本次启动的 `DanhuangDesktopPet` 残留进程。
- 0.11.49 完整截图矩阵仍保留在 `qa/tk-ui-0.11.49-20260705/`；0.11.50 针对性设置页截图补到 `qa/tk-ui-0.11.50-20260705/12-settings-package-folded.png`。
- 0.11.50 已补 DPI 修正 QA：`qa/tk-ui-0.11.50-20260705/00-desktop-pet-dpi-scaled-window.png`、`16-right-menu-dpi-scaled-window.png`、`contact-sheet-0.11.50-dpi-qa.png` 和 `screenshot-summary-0.11.50-dpi-qa.json`。当前机器全屏截图为物理像素 `2560x1440`，Tk 返回逻辑像素 `2048x1152`；透明 Tk 顶层窗口截图必须按 `1.25` 比例换算坐标，否则会出现空白桌宠或右键菜单裁偏的假阳性。
- 0.11.51 已补右键菜单截图：`qa/tk-ui-0.11.51-20260705/16-right-menu-compact-single-pet.png`。发行包右键菜单逻辑尺寸为 `540x593`，125% DPI 下物理截图为 `675x741`；`common_commands` 不包含 `open_pet_switcher`。
- 0.11.52 已补小屏滚动兜底截图：`qa/tk-ui-0.11.52-20260705/16-right-menu-small-screen-scroll.png`。最终发行包在 900x720 逻辑屏幕模拟下右键菜单逻辑尺寸压到 `540x561`，125% DPI 下物理截图为 `675x701`；`scrollable=true`，初始视图可见“暂停活动 / 隐藏气泡 / 退出”。
- 0.11.53 已补付费信任修复截图：`qa/tk-ui-0.11.53-paid-trust-20260705/`。最终 zip 临时解压副本的对话、AI、安全页显示“云端陪聊 / 待配置”和“当前安装目录 / exports”，未在首屏暴露 E 盘绝对路径。
- 0.11.54 已补付费语言一致性截图：`qa/tk-ui-0.11.54-paid-language-20260705/ai-page-label.png`。最终发行包源码打开控制面板 `AI` key 时，页面标题显示“陪聊设置”。
- 0.11.55 已补聊天窗口截图：`qa/tk-ui-0.11.55-paid-copy-20260705/chat-composer-copy-final-scaled.png`。最终发行包源码打开 560x680 聊天窗口时，输入框、发送按钮和“当前云端陪聊/本地陪伴”提示可见；本机截图按 1.25 DPI 比例换算坐标。
- 0.11.56 已补桌面烟测截图：`qa/tk-ui-0.11.56-motion-20260705/exe-smoke-desktop.png`。发行包 exe 可启动并在桌面右下角显示桌宠本体。
- 0.11.57 已补提醒反馈证据和桌面烟测截图：`qa/tk-ui-0.11.57-reminder-feedback-20260705/reminder-feedback-evidence.json`、`qa/tk-ui-0.11.57-reminder-feedback-20260705/exe-smoke-desktop.png`。
- 0.11.58 已补提醒删除确认证据和桌面烟测截图：`qa/tk-ui-0.11.58-reminder-delete-confirm-20260705/reminder-delete-confirm-evidence.json`、`qa/tk-ui-0.11.58-reminder-delete-confirm-20260705/exe-smoke-desktop.png`。
- 0.11.59 已补陪伴重置确认证据和桌面烟测截图：`qa/tk-ui-0.11.59-companion-reset-confirm-20260705/companion-reset-confirm-evidence.json`、`qa/tk-ui-0.11.59-companion-reset-confirm-20260705/exe-smoke-desktop.png`。
- 0.11.60 已补 AI 清空记忆确认证据和桌面烟测截图：`qa/tk-ui-0.11.60-ai-memory-confirm-20260705/ai-memory-confirm-evidence.json`、`qa/tk-ui-0.11.60-ai-memory-confirm-20260705/exe-smoke-desktop.png`。
- 0.11.61 已补形象资产删除确认证据和桌面烟测截图：`qa/tk-ui-0.11.61-pet-asset-confirm-20260705/pet-asset-confirm-evidence.json`、`qa/tk-ui-0.11.61-pet-asset-confirm-20260705/exe-smoke-desktop.png`。
- 0.11.62 已补动作精灵图清空确认证据和桌面烟测截图：`qa/tk-ui-0.11.62-action-clear-confirm-20260705/action-clear-confirm-evidence.json`、`qa/tk-ui-0.11.62-action-clear-confirm-20260705/exe-smoke-desktop.png`。
- 0.11.63 已补故事页反馈确认证据和桌面烟测截图：`qa/tk-ui-0.11.63-story-feedback-20260705/story-feedback-evidence.json`、`qa/tk-ui-0.11.63-story-feedback-20260705/exe-smoke-desktop.png`。
- 0.11.64 已补安全页个人备份反馈证据和桌面烟测截图：`qa/tk-ui-0.11.64-safety-backup-feedback-20260706/safety-backup-feedback-evidence.json`、`qa/tk-ui-0.11.64-safety-backup-feedback-20260706/exe-smoke-desktop.png`。

## 已知风险

- 干净 Windows 用户环境验收尚未执行，仍需单独验证首次安装、桌面快捷方式、升级保留数据、无自启动和安全软件提醒。
- 包内仍带源码版安装脚本和高级构建脚本，但普通用户说明已优先指向 `安装免Python版.bat`；GitHub 构建配置在软件内已默认折叠。
- `packages/` 当前只保留最新 0.11.64 目录和 zip：`packages/danhuang-desktop-pet-windows-20260706-204857/`、`packages/danhuang-desktop-pet-windows-20260706-204857.zip`。旧包已按用户最新要求清理，不再累积。

## 回退方式

- 本地只保留最新包；如需回退上一版，需要从 Git 历史恢复 0.11.63 源码后重新打包，或从外部备份取回旧 zip。
- 代码回退：回退 `APP_VERSION=0.11.63`，恢复 `export_configuration()`、`restore_configuration()` 和 `backup_spritesheet()` 的上一版反馈实现并移除对应测试；注意这会恢复安全页个人备份失败时弹出 Windows 系统错误框的付费用户体验风险。
