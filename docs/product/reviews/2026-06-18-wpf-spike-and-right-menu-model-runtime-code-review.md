# WPF Spike 与右键菜单模型接入代码审查

日期：2026-06-18

范围：

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- `src-windows-wpf/Danhuang.WpfSpike/`
- `src-windows-wpf/DanhuangProduct.sln`
- `.gitignore`
- 本轮同步更新的产品设计和执行文档

## 结论

Approved。

本轮改动继续保持 E 盘产品工程边界，没有修改 C 盘当前运行实例。Tk 右键菜单接入采用“modular 模型可用则使用、不可用则回退旧逻辑”的保守路径；WPF Spike 是可构建的最小技术验证外壳，不包含用户隐私数据。

## 发现

### Critical

无。

### Improvements

- Tk 右键菜单目前只消费 `ui/tk_right_menu.py` 的动作列表字段，常用入口、窗口操作、布局 token 和更多动作弹层渲染仍在单文件中。下一步应继续收敛渲染层，而不是停留在半接入状态。
- WPF Spike 已验证 build，但尚未启动做窗口截图或交互录屏；透明区域、拖动、置顶和窗口缩放仍需要桌面端人工或脚本化验收。

### Nitpicks

- 当前 PowerShell 会话未刷新 PATH 时需要用 `C:\Program Files\dotnet\dotnet.exe`，文档已记录。新终端通常可直接使用 `dotnet`。

## 验证记录

- `python -m py_compile`：E 盘 legacy monolith、E 盘运行镜像和相关 modular 文件通过。
- 运行时导入探针：两份 E 盘单文件均显示 `APP_VERSION=0.11.37`，且 `MODULAR_BUILD_RIGHT_MENU_MODEL is not None`。
- `python -m unittest discover -s src-prototype\modular\tests`：18 个测试通过。
- `python src-prototype\modular\validate_phase3.py --pet-dir data-dev\current-runtime\danhuang --json`：输出 5 个 ready 宠物、54 个可播放动作、11 个扩展动作，并显示当前宠物右键 UI 摘要。
- `dotnet build .\DanhuangProduct.sln`：0 警告、0 错误。

## 剩余风险

- 尚未启动 E 盘 Tk 运行镜像进行真实右键点击验收。
- 尚未启动 WPF Spike 进行桌面截图或多屏/DPI 验收。
- WPF Spike 目前没有真实 sprite atlas、右键菜单、托盘、SQLite、本地加密或安装包能力。
