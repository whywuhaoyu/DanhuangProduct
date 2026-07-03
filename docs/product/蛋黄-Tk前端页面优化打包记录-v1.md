# 蛋黄 Tk 前端页面优化打包记录 v1

## 文档状态

- 状态：已确认
- 适用范围：Tk/Python 线，Windows 免 Python exe 包
- 目标线别：Tk/Python 线
- 日期：2026-07-03
- 输入来源：Tk 前端页面优化第一批、用户要求每次优化后生成 Tk exe 包

## 版本记录

| 版本 | 日期 | 更新内容 |
| --- | --- | --- |
| v1 | 2026-07-03 | 记录 0.11.46 Tk 前端页面优化包路径、哈希和验证结果 |

## 核心结论

已基于 Tk 版本 `0.11.46` 生成新的 Windows 免 Python exe 包。包产物仍留在本机 `packages/`，不进入 GitHub 代码仓库；GitHub 只提交本记录和源码/文档变更。

## 包路径

```text
E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct\packages\danhuang-desktop-pet-windows-20260703-171629
E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct\packages\danhuang-desktop-pet-windows-20260703-171629-exe.zip
```

## 哈希

```text
SHA256: CCF47F5E0709BA0D78ABCA3EB5FF4BE024AB7ECF4668B9123C3CD2D53970B4D9
```

## 包含资源

- Tk 主程序：`run-danhuang-desktop-pet.py`
- 默认蛋黄资源：`spritesheet.webp`、`pet.json`、图标、对话库、灵魂设定、提示词包
- 干净模板数据：设置、AI Provider 预设、空待办、空提醒历史、空聊天记忆、空陪伴状态
- Windows 一键构建和安装脚本
- 免 Python exe：`app/dist/DanhuangDesktopPet/DanhuangDesktopPet.exe`

## 排除的个人数据

- API Key、DPAPI 密文
- 聊天记忆、长期记忆、待办、提醒历史
- 个人故事、用户源图、现实照片
- 本机日志和本机路径
- 其他未勾选宠物资源

## 验证入口

- `python -m py_compile` 覆盖 E 盘运行镜像和 legacy monolith。
- `python -m unittest discover -s src-prototype/modular/tests` 通过 27 个测试。
- `validate_phase3.py` 输出 5 个 ready 宠物、54 个可播放动作、11 个扩展动作，`warnings` 为空。
- 包内关键 JSON 可解析。
- 包内 `manifest.json` 显示 `app_version=0.11.46`、`python_bundled=true`。
- 包内临时 `app/build` 和 `app/DanhuangDesktopPet.spec` 已清理。
- exe 5 秒启动烟测通过，结束后无 `DanhuangDesktopPet` 残留进程。

## 已知风险

- 本轮未做完整人工 UI 截图矩阵，后续仍需补 `首页 / 对话 / AI / 提醒 / 形象 / 动作 / 档案 / 故事 / 操作 / 安全 / 外观` 截图基线。
- 旧包未自动删除；删除 `packages/` 旧包属于清理动作，需要用户确认后执行。

## 回退方式

- 运行旧包：`packages/danhuang-desktop-pet-windows-20260703-165013-exe.zip`
- 代码回退：回退 `run-danhuang-desktop-pet.py` 中 `panel_button_grid()` 及对话页两处按钮网格调用。
