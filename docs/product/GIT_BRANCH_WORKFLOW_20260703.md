# 蛋黄 GitHub 分支维护方案

日期：2026-07-03

适用仓库：https://github.com/whywuhaoyu/DanhuangProduct.git

## 目标

两台电脑可以并行推进不同实现路线：

- 当前电脑：Python/Tk 版本进度更快，作为短期可运行主线。
- 另一台电脑：Vue/Tauri 版本进度更快，作为新 UI/产品化主线。

核心原则：先把两边当前进度分别推到独立分支，确认 GitHub 上都有备份后，再讨论合并共享文档、资产和能力，不用一个版本覆盖另一个版本。

## 推荐分支

| 分支 | 用途 | 目录边界 |
| --- | --- | --- |
| `main` | 稳定产品文档、仓库规范、共享资产索引 | `README.md`、`AGENTS.md`、`.gitignore`、`docs/product/`、经确认可公开的 `assets/` |
| `tk/main` | 当前 Python/Tk 可运行版本 | `src-prototype/`、Tk 相关文档、Tk 打包脚本或说明 |
| `vue/main` | Vue/Tauri 版本 | `src-tauri-vue/`、Vue/Tauri 相关文档 |
| `feature/tk/*` | Tk 新功能或 UI 修复 | 只改 Tk 边界，除非同步更新共享文档 |
| `feature/vue/*` | Vue/Tauri 新功能或 UI 修复 | 只改 Vue 边界，除非同步更新共享文档 |
| `backup/*` | 首次上云前的原始快照 | 只用于兜底，不做长期开发 |

## 不能提交的内容

这些内容继续只留本机：

- `data-dev/`：当前运行数据、聊天、提醒、待办、AI 配置、陪伴状态。
- `packages/`：exe、zip、PyInstaller 构建产物。
- `archives/`、`archive-staging/`：历史原型归档和中转内容。
- `node_modules/`、`dist/`、`src-tauri-vue/src-tauri/target/`：前端和 Rust 构建产物。
- `.agents/`、`.codex/`、`.env*`、密钥证书、日志、锁文件。
- 未确认可公开的宠物源图、纪念照片、故事和截图。

例外：`src-tauri-vue/src-tauri/Cargo.lock` 是 Tauri 应用依赖锁定文件，需要提交，保证两台电脑构建一致。

打包产物如果需要共享，后续用 GitHub Releases 上传，不放进代码仓库。

## 当前电脑首次推送

如果 `git status` 提示 `not a git repository`，可以在当前目录初始化；如果已经初始化过，直接确认 remote 即可：

```powershell
cd E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct
git init -b main
git remote add origin https://github.com/whywuhaoyu/DanhuangProduct.git
git remote -v
```

先推共享骨架：

```powershell
git add .gitignore .editorconfig AGENTS.md README.md CHANGELOG.md docs assets
git status --short
git diff --cached --stat
git commit -m "chore: seed DanhuangProduct workspace"
git push -u origin main
```

再推 Tk 主线：

```powershell
git switch -c tk/main
git add src-prototype docs README.md CHANGELOG.md
git status --short
git diff --cached --stat
git commit -m "feat(tk): add current Tk desktop pet baseline"
git push -u origin tk/main
git tag tk-v0.11.43
git push origin tk-v0.11.43
```

如果远端已经不是空仓库，先执行：

```powershell
git fetch origin
git branch -r
```

看到远端已有分支后，不要直接 `push --force`。优先把本机进度推到 `backup/tk-20260703-current-pc`：

```powershell
git switch -c backup/tk-20260703-current-pc
git add .gitignore .editorconfig AGENTS.md README.md CHANGELOG.md docs assets src-prototype
git commit -m "backup: current Tk workspace before branch split"
git push -u origin backup/tk-20260703-current-pc
```

## 另一台电脑 Vue 推送

另一台电脑不要在当前 Tk 分支上直接覆盖 `src-tauri-vue/`。推荐新克隆仓库，再把那台电脑的 Vue 最新代码复制进 `src-tauri-vue/`：

详细命令见：[Vue 版本跨电脑推送操作文档](Vue版本跨电脑推送操作文档_20260703.md)。

```powershell
git clone https://github.com/whywuhaoyu/DanhuangProduct.git
cd DanhuangProduct
git switch -c vue/main origin/main
```

复制 Vue/Tauri 最新代码到 `src-tauri-vue/` 后：

```powershell
git add src-tauri-vue docs README.md CHANGELOG.md
git status --short
git diff --cached --stat
git commit -m "feat(vue): add current Vue Tauri baseline"
git push -u origin vue/main
git tag vue-snapshot-20260703
git push origin vue-snapshot-20260703
```

如果另一台电脑也已经有本地 Git 历史，先把它推到备份分支：

```powershell
git remote add origin https://github.com/whywuhaoyu/DanhuangProduct.git
git switch -c backup/vue-20260703-other-pc
git push -u origin backup/vue-20260703-other-pc
```

## 日常开发流程

Tk 优化：

```powershell
git switch tk/main
git pull --ff-only
git switch -c feature/tk/ui-panel-layout
# 修改、验证、打包
git add src-prototype docs README.md CHANGELOG.md
git commit -m "fix(tk): improve panel layout"
git push -u origin feature/tk/ui-panel-layout
```

Vue 优化：

```powershell
git switch vue/main
git pull --ff-only
git switch -c feature/vue/chat-input-layout
# 修改、验证
git add src-tauri-vue docs README.md CHANGELOG.md
git commit -m "fix(vue): improve chat input layout"
git push -u origin feature/vue/chat-input-layout
```

合并时通过 GitHub Pull Request 合到对应主线：Tk 功能合到 `tk/main`，Vue 功能合到 `vue/main`。只有共享文档、共享资产索引、产品需求变更才合到 `main`。

## 防丢代码检查清单

每次推送前检查：

- `git status --short`：确认没有把 `data-dev/`、`packages/`、`node_modules/`、`target/`、`.codex/`、`.agents/` 加进去。
- `git diff --cached --stat`：确认本次提交体积合理，不包含几百 MB 构建产物。
- `git branch --show-current`：确认当前在 `tk/main`、`vue/main` 或对应 feature 分支。
- `git push -u origin <branch>`：首次推新分支用 `-u` 绑定远端。
- 不使用 `git push --force`，除非先确认远端分支没有另一台电脑的新提交。

每次 Tk 优化完：

- 源码和文档提交到 `tk/main` 或 `feature/tk/*`。
- exe 仍然打包到 `packages/`，本地只保留最新包。
- 需要跨电脑取包时，把 zip 上传 GitHub Releases，并在标签里标明 Tk 版本。
