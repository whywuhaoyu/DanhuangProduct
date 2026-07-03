# DanhuangProduct

这是蛋黄桌宠从个人原型走向产品化的工程根目录。

## 当前状态

- C 盘运行版已同步到 `data-dev/current-runtime/danhuang/`，后续开发和试运行优先只使用 E 盘镜像。
- 产品化工程放在 `E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct`。
- 已冻结原型归档：`archives/DanhuangPrototype-20260614-121543`。
- 已复制当前 Tk 单文件原型到 `src-prototype/legacy-monolith/`，用于后续拆分验证。
- 已生成当前审计文件到 `docs/product/current-audit/`。
- Tk Phase 3 正在拆分运行层 UI：右键菜单、气泡 view model/renderer 和基础窗口尺寸已优先接入 E 盘运行镜像。
- 当前电脑的可运行主线是 Python/Tk 版本；另一台电脑的 Vue/Tauri 版本作为并行产品化分支维护。WPF Spike/技术验证目录已移除，不再作为当前产品路线。

## 工作原则

1. 后续新增功能、UI 优化和试运行优先只在 E 盘进行；C 盘不再作为开发源。
2. E 盘产品化工程承载长期文档、新代码、运行镜像、审计、QA 和构建产物。
3. Python/Tk 和 Vue/Tauri 分别通过 `tk/main`、`vue/main` 维护，目录边界清晰隔离；WPF 当前版本已移除。
4. 用户照片、故事、聊天、待办、API Key 和日志默认不公开、不进安装包。
5. 每次完成 Tk 功能优化、UI 优化或运行逻辑修复后，都要同步 E 盘运行镜像，并重新生成 Windows 可执行 exe 包。

## 运行当前 E 盘版本

推荐从产品工程里的当前运行镜像启动：

```powershell
PowerShell -ExecutionPolicy Bypass -File "E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct\data-dev\current-runtime\danhuang\start-danhuang-desktop-pet.ps1"
```

这个脚本会先停止旧的 C 盘蛋黄进程和 E 盘镜像进程，再用本机 Codex Python runtime 启动当前 `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`。

如果需要在终端里看报错，用可见 Python 直接运行：

```powershell
& "C:\Users\27176\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct\data-dev\current-runtime\danhuang\run-danhuang-desktop-pet.py"
```

确认当前运行的是 E 盘版本：

```powershell
Get-CimInstance Win32_Process | Where-Object { ($_.Name -in @("python.exe","pythonw.exe")) -and ($_.CommandLine -like "*run-danhuang-desktop-pet.py*") } | Select-Object ProcessId,Name,CommandLine
```

## 入口文档

- 产品需求：[docs/product/PRODUCT_REQUIREMENTS.md](docs/product/PRODUCT_REQUIREMENTS.md)
- 路线图：[docs/product/ROADMAP.md](docs/product/ROADMAP.md)
- 目标架构：[docs/product/ARCHITECTURE_TARGET.md](docs/product/ARCHITECTURE_TARGET.md)
- UI 重构：[docs/product/UI_REDESIGN_SPEC.md](docs/product/UI_REDESIGN_SPEC.md)
- 目录治理：[docs/product/DIRECTORY_GOVERNANCE.md](docs/product/DIRECTORY_GOVERNANCE.md)
- Git 分支维护：[docs/product/GIT_BRANCH_WORKFLOW_20260703.md](docs/product/GIT_BRANCH_WORKFLOW_20260703.md)
- Vue 版本跨电脑推送：[docs/product/Vue版本跨电脑推送操作文档_20260703.md](docs/product/Vue版本跨电脑推送操作文档_20260703.md)
- 隐私和商业化：[docs/product/PRIVACY_COMMERCIALIZATION.md](docs/product/PRIVACY_COMMERCIALIZATION.md)
- 执行追踪：[docs/product/IMPLEMENTATION_TRACKER.md](docs/product/IMPLEMENTATION_TRACKER.md)
