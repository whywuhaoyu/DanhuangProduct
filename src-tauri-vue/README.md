# 蛋黄桌宠 Tauri + Vue3

这是蛋黄桌宠前端化产品版，使用 Tauri 2 + Vue3 + TypeScript。当前仓库只同步源码和安全工程配置，不包含个人运行镜像、聊天、待办、提醒、宠物照片、API Key 或打包产物。

## 窗口

- `main`：控制面板窗口，承载首页、形象、档案、故事、动作、对话、AI、提醒、外观、行为和安全页。
- `pet`：透明无边框桌宠窗口，默认置顶、跳过任务栏，可拖动、巡游、显示气泡和右键互动。

## 数据边界

Rust 命令只通过白名单路径读取产品根目录下的 `data-dev/current-runtime/danhuang/` 运行镜像。该目录是本机开发数据，不随本仓库同步。

前端不直接扫描任意本机目录；API Key 只在 Rust 侧从 DPAPI 加密字段或环境变量读取，不向 Vue 返回、不写日志。

如果本仓库被单独 clone 到另一台电脑，请设置：

```powershell
$env:DANHUANG_PRODUCT_ROOT="D:\DanhuangProduct"
```

该目录需要包含 `data-dev/current-runtime/danhuang/`。也可以把完整产品根和本仓库保持原来的父子目录结构，让程序自动向上查找运行镜像。

## 开发命令

```powershell
npm install
npm run type-check
npm run build
npm run tauri dev
```

开发环境检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-dev.ps1
```

## 调试打包

Windows 当前默认 bundle target 是已验证通过的 NSIS：

```powershell
npm run tauri build
```

产物路径：

```text
src-tauri\target\release\bundle\nsis\蛋黄桌宠_0.1.0_x64-setup.exe
```

MSI/WiX 链路曾在 `light.exe` 阶段失败，后续需要 MSI 时再单独排查。

## 同步到 GitHub

本仓库默认按私有仓库发布。首次发布前需要本机 GitHub CLI 完成登录：

```powershell
gh auth login --hostname github.com --git-protocol https --web
```

登录完成后执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish-github.ps1
```

默认目标仓库：

```text
whywuhaoyu/danhuang-desktop-pet-tauri-vue
```

如需公开仓库，追加 `-Public`。

## 当前边界

当前版本继续复用 spritesheet/atlas 和 strip 动作资产。Live2D、Lottie、WebGL 和粒子 renderer 作为后续 renderer 预留。
