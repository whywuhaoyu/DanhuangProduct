<INSTRUCTIONS>
项目中所有手写文本和源码文件必须使用 UTF-8（无 BOM）保存，禁止 ANSI、GBK、UTF-8 with BOM，避免中文乱码。

当前目录是蛋黄桌宠产品化工程根目录。所有归档、Tk 产品代码、产品文档、QA 输出和打包产物优先放在这里：

- `archives/`：只读原型归档，不提交到代码仓库。
- `src-prototype/`：Python/Tk 原型副本和后续拆分实验。
- `src-tauri-vue/`：历史 Tauri/Vue 实验分支，非当前主线；继续投入前需要重新确认。
- `docs/product/`：PRD、路线图、架构、UI、隐私、审计和执行追踪。
- `assets/`：产品化资产包，不直接混入运行期个人数据。
- `data-dev/`：本机开发数据，不进入公开包。
- `packages/`：安装包、导出包、构建产物，不提交到代码仓库。
- `qa/`：截图、contact sheet、动作验收记录。

安全规则：

- API Key、Token、DPAPI 加密内容、聊天、待办、提醒历史、陪伴状态、本机路径和日志不得进入公开包。
- 用户源图、纪念宠物照片和故事默认视为隐私资产；公开分享、上传生成或删除前必须二次确认。
- C 盘历史运行实例已同步到 `data-dev/current-runtime/danhuang/`；后续新增功能、UI 优化和试运行优先只在 E 盘本产品目录处理，不再以 C 盘为开发源。
- 当前产品主线收敛为 Python/Tk 版本；WPF 技术验证目录已移除，不再作为后续同步目标。
- 每次完成 Tk 版本功能优化、UI 优化或运行逻辑修复后，必须同步 E 盘运行镜像，并给 Tk 版本重新生成一个可执行 exe 包到 `packages/`。
- `packages/` 只保留最新一组 Tk Windows exe 包；新包验证通过后删除旧的 `danhuang-desktop-pet-windows-*` 文件夹和 zip，避免打包记录堆积占用空间。
</INSTRUCTIONS>
