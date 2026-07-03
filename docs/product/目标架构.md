# 目标架构

## 当前判断

当前 Tk 原型已经证明了核心体验价值，但仍需要继续拆分和工程化：

- `run-danhuang-desktop-pet.py` 已达到 15,945 行。
- `DanhuangPet` 单类有 429 个方法。
- `open_control_panel` 单方法约 3,874 行。

当前路线已调整为 Tk-only：

- Python/Tk 运行版是当前唯一产品主线。
- 模块化拆分继续围绕 `src-prototype/modular/` 和 E 盘运行镜像推进。
- WPF 技术验证目录已按 2026-07-03 决策移除，不再作为后续同步目标。
- 每次完成 Tk 优化后，都要同步运行镜像并重新生成 Windows exe 包。

## Python/Tk 原型拆分目标

```text
src-prototype/
  legacy-monolith/
    run-danhuang-desktop-pet.py
  modular/
    core/
      pet_model.py
      ai_providers.py
      todos.py
      exporter.py
      companion_state.py
      motion_state.py
    ui/
      tk_pet_window.py
      tk_panel.py
      tk_bubble.py
      tk_right_menu.py
    assets/
      atlas.py
      manifest.py
```

拆分顺序：

1. 先抽纯数据模型和 JSON 读写。已完成。
2. 再抽 AI Provider 和待办提醒。已完成。
3. 再抽宠物窗口、气泡和右键菜单。进行中：右键菜单 view model/style/position、气泡 view model/renderer 和基础窗口尺寸已开始接入 E 盘单文件运行镜像。
4. 最后拆控制面板。

约束：

- 每拆一步保持现有行为不变。
- 每拆一步跑语法检查和启动烟测。
- 不在拆分过程中改宠物人格、动作语义或用户数据格式。

## 数据方案

- 当前 JSON 作为迁移输入。
- 短期继续使用本地 JSON，模块化后再评估 SQLite 迁移。
- API Key 和 Token 使用系统本地加密，不写入明文配置。
- 宠物资产使用 manifest：宠物信息、动作列表、帧数、持续时间、资源 hash、版权来源。

## 跨平台共享

- 共享账号、宠物 manifest、资产包、订阅和云同步协议作为远期方向。
- 不共享 UI 实现。
- Windows 当前用 Python/Tk 打包 exe。
- macOS 用 SwiftUI/AppKit。
- 移动端做陪伴管理 App，不承诺系统级常驻桌宠。
