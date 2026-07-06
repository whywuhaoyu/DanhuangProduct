# 蛋黄桌宠

蛋黄桌宠是一个 Windows 桌面陪伴软件。它会以透明小宠物的形式停在桌面边缘，支持聊天、本地提醒、动作互动、宠物形象管理和本机隐私数据导出。

## 适用人群

- 想在电脑桌面上保留一个低打扰陪伴入口的人。
- 想用本地待办提醒、宠物气泡和简单聊天辅助日常节奏的人。
- 需要自行配置 AI Provider，但不希望 API Key、聊天、待办和故事被打进公开包的人。

## 安装启动

当前产品主线是 Python/Tk 版本，工程根目录为：

```text
E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk
```

开发机启动当前运行镜像：

```powershell
PowerShell -ExecutionPolicy Bypass -File "E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk\data-dev\current-runtime\danhuang\start-danhuang-desktop-pet.ps1"
```

如果需要在终端里看报错：

```powershell
& "C:\Users\27176\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk\data-dev\current-runtime\danhuang\run-danhuang-desktop-pet.py"
```

普通用户拿到 Windows 分发包后，优先运行包内 `安装免Python版.bat`。如果包内已经带有 `app/dist/DanhuangDesktopPet/DanhuangDesktopPet.exe`，安装不需要本机 Python。

## 核心功能

- 右键宠物：聊天、控制面板、提醒、陪聊设置、安静一下、陪伴模式、暂停活动和动作播放；有多个可切换形象时才显示“切换形象”，小屏下按钮区可滚动。
- 控制面板：默认只展示首页、对话、提醒、形象、动作和安全；高级模式再显示陪聊设置、故事、行为、设置、巡逻和外观。
- 本地提醒：快速记录生活事项，支持稍后提醒、完成/重开、置顶、时间轴和详细编辑。
- 云端陪聊：用户自行在“陪聊设置”里配置服务和 API Key；Base URL 等参数默认收在高级连接参数里。
- 隐私安全：安全页可打开本地数据目录、导出个人备份、生成公开分发包。

## 配置说明

- 发行包默认不置顶、0.46 体型缩放、边缘活动、低频自动说话，避免首次启动打扰工作。
- 首页和右键菜单都提供“安静 / 日常 / 活跃”三档陪伴模式；安静模式关闭自动说话和巡游，日常模式低频沿边活动，活跃模式更常互动但仍默认不跑进屏幕中心。
- 右键“安静一下”会临时延后自动说话和自动活动；“暂停活动”会切到安静模式，再次点击可恢复日常。
- 高级模式里的设置页只展示本地文件夹和折叠的开发者工具；普通用户不需要配置 GitHub、Token 或 workflow。
- API Key 只保存到本机；保存后界面只显示掩码，不写入导出包、聊天记录或日志。

## 数据与隐私

聊天、待办、提醒历史、故事、陪伴状态和设置都保存在本机运行目录。公开分发包默认清空个人数据模板，不包含 API Key、DPAPI 密文、聊天、待办、提醒历史、日志或本机路径。

## 常见问题

如果宠物挡住工作内容，右键选择“安静一下”或“暂停活动”，也可以在控制面板的高级模式里调整巡逻范围、置顶和说话间隔。

如果云端陪聊没有回复，先到“陪聊设置”检查服务、模型和 Key，再展开高级连接参数查看 Base URL。

如果安装包被安全软件提醒，先确认来源可信。当前脚本不会写开机自启，也不会写注册表 Run 项。

## 卸载升级

Windows 免 Python 版默认安装到 `%LOCALAPPDATA%\DanhuangDesktopPet`。删除桌面快捷方式并删除该目录即可卸载。升级安装会尽量保留目标电脑已有的等级、聊天、记忆、待办、提醒历史和本机 API Key。

## 更多文档

- 产品需求：[docs/product/蛋黄桌宠产品需求.md](docs/product/蛋黄桌宠产品需求.md)
- 路线图：[docs/product/产品路线图.md](docs/product/产品路线图.md)
- UI 优化清单：[docs/product/当前Tk桌宠UI优化清单.md](docs/product/当前Tk桌宠UI优化清单.md)
- 执行追踪：[docs/product/执行追踪.md](docs/product/执行追踪.md)
- 打包记录：[docs/product/蛋黄-Tk前端页面优化打包记录-v1.md](docs/product/蛋黄-Tk前端页面优化打包记录-v1.md)
