# 蛋黄桌宠 Tauri + Vue3 Spike

这是蛋黄桌宠前端化产品版的第一阶段 Spike，使用官方 Tauri 2 + Vue3 + TypeScript 模板生成，并替换为双窗口结构。

## 窗口

- `main`：控制面板窗口，承载首页、形象、动作、对话、提醒、安全和技术路线原型。
- `pet`：透明无边框桌宠窗口，默认置顶、跳过任务栏，可拖动和隐藏。

## 数据边界

Rust 命令只读 `data-dev/current-runtime/danhuang/` 中的 manifest/settings 摘要和白名单图片资源，不向前端返回 Key、Token、聊天、待办、提醒历史、本机路径或日志。

## 开发命令

```powershell
cd E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct\src-tauri-vue
npm install
npm run type-check
npm run build
npm run tauri dev
```

## 当前边界

第一版不重做动作素材，继续复用当前 spritesheet/atlas。Live2D、Lottie、WebGL 和粒子 renderer 只在 UI 和文档中预留，不进入本轮实现。
