# Changelog

## 0.11.75-tk-uploaded-action-choice-polish - 2026-07-06

- 继续按付费用户严苛审计动作资产链路：推荐扩展动作和新增宠物基础动作已经上传时，不再弹 Windows 系统三选一确认框。
- 新增 `show_panel_choice()` 暖色选择弹窗，保留“清空动作 / 重新选择 / 稍后再说”三种结果，体验与面板确认、Toast 保持一致。
- “重新选择”会直接打开动作条文件选择器；如果用户取消，原已上传动作保持不变。
- 本批只改动作上传确认交互和版本号，不改动作 ID、动作精灵图契约、右键动作栏或宠物数据结构。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.75-uploaded-action-choice-20260706/uploaded-action-choice-evidence.json`、`qa/tk-ui-0.11.75-uploaded-action-choice-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-225828.zip`，ZIP SHA256 `7DC902567167FCB8EDF51B5385D8A1532F818EA93409C775B376A76F4A69DCC3`，EXE SHA256 `2630F7061E700876DFEA9201377F5FACCAADAD8F4623AC1130B7DEE5402B8059`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-225828/` 和对应 zip。

## 0.11.74-tk-extension-action-feedback-polish - 2026-07-06

- 继续按付费用户严苛审计动作资产链路：扩展动作上传窗口的动作名称为空、动作条不合格和建议检查反馈统一改为当前窗口 Toast。
- `save_extension_action_asset()` 新增可选 `feedback_parent` 参数，推荐待补动作上传路径也能把反馈锚定到控制面板。
- 保留“动作已上传”的三态选择框给下一批单独重做，避免把清空/重选/取消复杂确认混入本批。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.74-extension-action-feedback-20260706/extension-action-feedback-evidence.json`、`qa/tk-ui-0.11.74-extension-action-feedback-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-224054.zip`，ZIP SHA256 `CAD47DB60C0A6BC6D86C6E75D97DF044633615B069A70C4748F855412747FBE6`，EXE SHA256 `C3787BF32F612264806212DD9A0B253EC7B4FF4E2B356DBDE3D1FE2ADAD5C851`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-224054/` 和对应 zip。

## 0.11.73-tk-new-pet-import-feedback-polish - 2026-07-06

- 继续按付费用户严苛审计新增宠物链路：新增宠物向导的创建失败、基础动作缺失、拖拽格式不支持和拖拽异常反馈统一改为当前窗口 Toast。
- `create_pet_from_assets()` 新增可选 `feedback_parent` 参数，导入校验错误可以锚定到新增宠物窗口。
- 基础动作条上传校验错误和建议检查不再弹系统窗口，减少上传素材时被工程弹窗打断。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.73-new-pet-import-feedback-20260706/new-pet-import-feedback-evidence.json`、`qa/tk-ui-0.11.73-new-pet-import-feedback-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-223303.zip`，ZIP SHA256 `89D0453FB2D1C8A165035DE2873BCEC665265BA4EB17915823FA939E6FFA84C4`，EXE SHA256 `637B629CC9733738A4D6AE8E4CEFABB0D7A36AE0C1267F9F8457003B992326ED`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-223303/` 和对应 zip。

## 0.11.72-tk-identity-image-feedback-polish - 2026-07-06

- 继续按付费用户严苛审计形象导入链路：更换主像素图时，图片不存在或无法读取不再弹 Windows 系统错误框，改为面板 Toast。
- `update_pet_identity_image()` 新增可选 `feedback_parent` 参数；`choose_pet_identity_image()` 默认把反馈锚定到当前控制面板。
- 主像素图失败反馈和现实照片、提示词复制反馈保持一致，减少用户上传私密形象资产时的工程感和割裂感。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.72-identity-image-feedback-20260706/identity-image-feedback-evidence.json`、`qa/tk-ui-0.11.72-identity-image-feedback-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-223000.zip`，ZIP SHA256 `9C012538AEABCEB4331CB30C370509188F945AB21F6A526E1EFFBD47EA3D93FD`，EXE SHA256 `E54260A1B62BFE19712397C196A90335E579DD189CA1E5DE9A25D47C4C9EDBBC`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-223000/` 和对应 zip。

## 0.11.71-tk-clipboard-feedback-polish - 2026-07-06

- 继续按付费用户严苛审计动作/新增宠物辅助链路：复制提示词、扩展动作提示词和使用教学的空内容、成功、失败反馈统一改为面板 Toast。
- `copy_text_to_clipboard()` 新增可选 `parent` 参数，后续二级窗口可以把复制反馈锚定到当前窗口；旧调用保持兼容。
- 复制成功时保留桌宠气泡，并新增短 Toast，用户能明确知道内容已经进入剪贴板。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.71-clipboard-feedback-20260706/clipboard-feedback-evidence.json`、`qa/tk-ui-0.11.71-clipboard-feedback-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-222245.zip`，ZIP SHA256 `ECD08291CF3C08066B16C29DEBF7E06E58460E1368AD1C0C79419EF987EAE761`，EXE SHA256 `956CC86B2466CAE7093369F9665FBA64F4AB72A757AE331AE753A0D59371CB55`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-222245/` 和对应 zip。

## 0.11.70-tk-reference-image-feedback-polish - 2026-07-06

- 继续按付费用户严苛审计形象页私密照片入口：添加现实照片窗口空提交不再弹 Windows 系统警告框，改为锚定当前窗口的暖色 Toast。
- 复制现实照片失败时，底层 `add_reference_paths_to_pet()` 可传入 `feedback_parent`，失败反馈显示在当前窗口而不是系统错误框。
- 添加现实照片窗口补统一关闭路径、`Esc` 关闭和打开后焦点提升。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.70-reference-image-feedback-20260706/reference-image-feedback-evidence.json`、`qa/tk-ui-0.11.70-reference-image-feedback-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-221117.zip`，ZIP SHA256 `0B9FD5EF147B237D3712023F9620345D9A0050710F1691C6B014634DE6E8510D`，EXE SHA256 `CCEE5F92D2F236720360F8C77CA5E5A23BE33CC6479AFC08B7B0A4045A2BF0A8`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-221117/` 和对应 zip。

## 0.11.69-tk-pet-identity-actions-grid - 2026-07-06

- 继续按付费用户严苛审计形象页资产体验：当前主形象操作区改为共享按钮网格，避免更换主像素图、添加现实照片、管理动作、编辑资料和删除主像素图在窄窗口下横向挤压。
- 用户上传现实照片区域底部操作改为两列按钮网格，减少“添加现实照片 / 新增宠物”贴边或错位风险。
- 危险操作“删除主像素图”保留红色危险样式，但纳入同一网格体系，点击目标和视觉层级更稳定。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.69-pet-identity-actions-grid-20260706/pet-identity-actions-grid-evidence.json`、`qa/tk-ui-0.11.69-pet-identity-actions-grid-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-215245.zip`，ZIP SHA256 `49D5EE65CDC78989167AE84BA3B3CEE1BD0D17A0A8B5DB6150FDC12CAC3A2FF1`，EXE SHA256 `F93D7FEE936432BD0D95DAA616D1028B08D36F0EBFA186182B1568D7B00D7746`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-215245/` 和对应 zip。

## 0.11.68-tk-chat-focus-background-polish - 2026-07-06

- 继续按付费用户严苛审计聊天体验：聊天窗口重复打开时会恢复窗口、提升焦点并重新聚焦输入框，减少从右键/控制面板回到聊天时的手动点击。
- 聊天背景上传失败不再使用 Windows 系统错误框，改为锚定聊天背景窗口的暖色 Toast。
- 聊天背景窗口补 `Esc` 关闭和打开后焦点提升，关闭按钮、窗口关闭和快捷键走同一清理路径。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.68-chat-focus-background-20260706/chat-focus-background-evidence.json`、`qa/tk-ui-0.11.68-chat-focus-background-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-214445.zip`，ZIP SHA256 `DD419374923D44476FA038F6D93CFB1F5B87692E978DDB843A6D0B82948959F3`，EXE SHA256 `45824B693D170F065571EF10284BE0AC91DAE5A645016390C23EFB8630588E74`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-214445/` 和对应 zip。

## 0.11.67-tk-reminder-popup-shortcuts - 2026-07-06

- 继续按付费用户严苛审计提醒到点体验：提醒弹窗的状态 chip、主操作和稍后提醒操作改为固定网格，降低横向挤压和按钮错位风险。
- 到点弹窗新增快速处理键：`Ctrl+Enter` 完成，`1/2/3` 分别稍后 15 分钟、1 小时和明天，`Esc` 关闭且不改变待办状态。
- 弹窗打开后会置顶、获取焦点并聚焦“完成”按钮；关闭时清理 `self.reminder_popup` 引用，减少下一次提醒窗口状态残留。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.67-reminder-popup-shortcuts-20260706/reminder-popup-shortcuts-evidence.json`、`qa/tk-ui-0.11.67-reminder-popup-shortcuts-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-212948.zip`，ZIP SHA256 `04F0DB5EBCB602D5C880BE4DCF06613A56CAE195715D9E18EE183E820E53D2BD`，EXE SHA256 `82F2EA4F91512143DAD7CD705BA8A85794E2197CC877B299000B1B66F4326C10`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-212948/` 和对应 zip。

## 0.11.66-tk-pet-motion-edge-lock - 2026-07-06

- 继续按付费用户严苛审计桌宠本体运动体验：主屏边缘巡游目标记录当前边，并在每帧移动前锁住固定轴，避免沿边走时逐渐向屏幕中间偏移。
- 拖动松手进入惯性和惯性结束时清理拖动方向状态，减少慢速拖动或松手后残留左/右跑动方向的割裂感。
- `ui/tk_pet_window.py` 新增 `lock_edge_roam_position()` 纯函数，legacy 单文件优先调用 modular helper，失败时保留本地 fallback。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.66-pet-motion-edge-lock-20260706/pet-motion-edge-lock-evidence.json`、`qa/tk-ui-0.11.66-pet-motion-edge-lock-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-211839.zip`，ZIP SHA256 `B99C42C1981B0F05225DBE1956400AB843106E6AF246B8AE946AACF845C320A3`，EXE SHA256 `EC10930053D9EF34F727F25BE7B5C74F502226C431406FBC2C8F46244D7B11F4`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-211839/` 和对应 zip。

## 0.11.65-tk-installer-export-feedback-polish - 2026-07-06

- 继续按付费用户严苛审计安全页公开分发体验：导出安装包弹窗的成功、失败、缺少 GitHub 仓库、缺少 GitHub Token 和 macOS 远端构建结果统一改为状态卡 + 面板 Toast。
- GitHub Token 保存和 workflow 模板写入不再弹 Windows 系统信息框，改为锚定导出弹窗的 Toast；失败时记录日志并显示可恢复提示。
- 普通导出接口保留完成提示，但改为当前面板 Toast，减少分发/打包链路中的工程味系统弹窗。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.65-installer-export-feedback-20260706/installer-export-feedback-evidence.json`、`qa/tk-ui-0.11.65-installer-export-feedback-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-210701.zip`，ZIP SHA256 `24F268CC65760B2F8EDBD142FA0067D938169495F9CADE13A76D7FEFDF5B9FEA`，EXE SHA256 `91129C3F83A8C6E66953A73115BF2396FE841191807EB894CCF8CBD36C3226E8`。
- 按最新打包规则清理 `packages/`，只保留 `danhuang-desktop-pet-windows-20260706-210701/` 和对应 zip。

## 0.11.64-tk-safety-backup-feedback-polish - 2026-07-06

- 继续按付费用户严苛审计安全页个人数据体验：导出配置、恢复配置和备份精灵图统一改为面板 Toast 反馈。
- 恢复配置遇到不可读文件、非法 JSON 或非蛋黄配置结构时，不再弹出 Windows 系统错误框，改为控制面板内错误提示。
- 导出配置和备份精灵图成功后显示友好路径标签，便于用户确认个人备份已经落盘。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.64-safety-backup-feedback-20260706/safety-backup-feedback-evidence.json`、`qa/tk-ui-0.11.64-safety-backup-feedback-20260706/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260706-204857.zip`，ZIP SHA256 `9EE8176BF939C2D10C1F60C509843AEBA671E51DBDD5046BDCA2513BFB2A5FC1`，EXE SHA256 `9BA8968EA7BBAC8DEB5E7F0C0DEE913679DE7A61A3A1EB846A26BE0F120CFBFB`。
- 按最新打包规则清理 `packages/` 历史 Tk Windows 包，只保留 `danhuang-desktop-pet-windows-20260706-204857/` 和对应 zip。

## 0.11.63-tk-story-feedback-confirm-polish - 2026-07-05

- 继续按付费用户严苛审计故事/档案体验：“删除故事”不再弹出 Windows 系统确认框，改为统一暖色面板确认。
- 确认文案明确只移除当前宠物的一条故事、日记或思念记录，不删除图片文件、聊天记忆、提醒、陪伴等级或其他宠物故事。
- 故事编辑器的空内容、图片/背景失败、无可用图片、无 AI/无故事/生成失败等提示改为面板 Toast；二级编辑窗口可通过 `show_panel_toast(parent=...)` 把反馈锚定到当前窗口。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.63-story-feedback-20260705/story-feedback-evidence.json`、`qa/tk-ui-0.11.63-story-feedback-20260705/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-191215.zip`，ZIP SHA256 `30AD25B5B1C32826F864550BAC06FECD2D2C5544967E64872413999D5B9F7DED`，EXE SHA256 `A56AFE11A4D077ADBFA0ECF4FE4727C1DADA91F5A26E26E518EB90E45C1C3C20`。

## 0.11.62-tk-action-clear-confirm-polish - 2026-07-05

- 继续按付费用户严苛审计动作资产体验：“清空动作精灵图”不再弹出 Windows 系统确认框，改为统一暖色面板确认。
- 确认文案明确扩展动作会从动作页、右键动作栏和当前形象的可播放动作里移除，不删除基础动作、主像素图、现实照片、参考图或聊天记忆。
- 未上传动作精灵图时改为面板 Toast 提示；清空完成后显示面板 Toast，并保留重新上传同名动作的路径。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.62-action-clear-confirm-20260705/action-clear-confirm-evidence.json`、`qa/tk-ui-0.11.62-action-clear-confirm-20260705/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-185625.zip`，ZIP SHA256 `B0A8B21A2500CB815B93897E13B88621C4AAC95A0EC8568005F517AFB1EB703C`，EXE SHA256 `E55B05562723023E9B6C70AF49235E769DA83C3FEFBDE1E117C150D7E8FB9334`。

## 0.11.61-tk-pet-asset-confirm-polish - 2026-07-05

- 继续按付费用户严苛审计纪念资产体验：“删除主像素图”和“删除参考图”不再弹出 Windows 系统确认框，改为统一暖色面板确认。
- 主像素图确认文案明确只处理桌宠目录里的主像素图副本，不删除现实照片、参考图、动作精灵图或聊天记忆。
- 参考图确认文案明确不会删除本机外部源文件；只有桌宠目录中的上传副本会被清理，原始照片、主像素图、动作精灵图和故事记录不受影响。
- 未设置主像素图时改为面板 Toast 提示，减少形象页系统弹窗割裂感。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.61-pet-asset-confirm-20260705/pet-asset-confirm-evidence.json`、`qa/tk-ui-0.11.61-pet-asset-confirm-20260705/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-184801.zip`，ZIP SHA256 `7DF0A9CC7B6A917F62E8F26F63F74444CEEF5527BAED74252F916454A9E56DA7`，EXE SHA256 `E9D4F7AF7924C25F24A7C1FBE4E198E824EEC47A9178EA64BC4C33BB38659118`。

## 0.11.60-tk-ai-memory-confirm-polish - 2026-07-05

- 继续按付费用户严苛审计陪聊隐私体验：“清空记忆”不再弹出 Windows 系统确认框，改为统一暖色面板确认。
- 确认文案明确只清空当前形象的最近聊天、长期记忆摘要和学习表达，不删除 API Key、提醒、待办或陪伴等级。
- 清空完成后显示面板 Toast，并保留蛋黄气泡反馈；Provider 配置、API Key/DPAPI 保存、提醒和陪伴 JSON 契约不变。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.60-ai-memory-confirm-20260705/ai-memory-confirm-evidence.json`、`qa/tk-ui-0.11.60-ai-memory-confirm-20260705/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-183625.zip`，ZIP SHA256 `7A17B72AB8F081EDA9E80CC7FF3AA2B27114C7AA4350EF22B677EF9BFD4E1513`，EXE SHA256 `750762F8AF2ED89DBB25CCE0F6A8B640FEA284EBEC0694033AB1370755C94520`。

## 0.11.59-tk-companion-reset-confirm-polish - 2026-07-05

- 继续按付费用户严苛审计陪伴资产体验：“重置陪伴数据”不再弹出 Windows 系统确认框，改为暖色面板确认。
- 确认文案明确只重置等级、经验、连续陪伴天数和互动次数，不删除聊天、待办或提醒，避免纪念型桌宠用户误判风险。
- 重置完成后显示面板 Toast，并保留蛋黄气泡反馈；陪伴 JSON 数据结构和初始字段不变。
- 已补回归测试和 QA 证据：`qa/tk-ui-0.11.59-companion-reset-confirm-20260705/companion-reset-confirm-evidence.json`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-182622.zip`，ZIP SHA256 `6F3AA198F61F3B3851E39CEFF6C45644A98F977E1C84ADA13BAD204EDB5C4804`，EXE SHA256 `E6B0DCD3F1949C4EF2C43B0785F28B1BADF26F83B5C33535D2CFC530EEBD6694`。

## 0.11.58-tk-reminder-delete-confirm-polish - 2026-07-05

- 继续按付费用户严苛审计提醒体验：删除待办不再弹出 Windows 系统确认框，提醒页和待办编辑弹层统一使用暖色面板确认。
- 新增 `show_panel_confirm()` 通用确认 helper；本批先接入提醒删除，后续可逐步替换其他高频危险操作。
- `delete_todo()` 收敛为已确认后的软删除执行逻辑，继续保留提醒时间轴删除记录，不改变待办 JSON 契约。
- 面板 Toast 增加 `warning` 色板，未选中提醒、提醒不存在等轻警告从普通信息状态中区分出来。
- 已补提醒删除确认 QA 证据：`qa/tk-ui-0.11.58-reminder-delete-confirm-20260705/reminder-delete-confirm-evidence.json`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-181739.zip`，ZIP SHA256 `186AB2BF1CB3B67952EEF9563CC5CF28CEF561CA136BD8C8F0EADF95EDF7A23B`，EXE SHA256 `288475A83940ED67899FE29ED679E1CB13F52510CEC3127E02BC4F0C9BF84FC2`。

## 0.11.57-tk-reminder-feedback-trust-fix - 2026-07-05

- 继续按付费用户严苛审计提醒体验：提醒页待办操作不再静默失败，未选中待办时会用面板 Toast 提示先选择一条提醒。
- “稍后提醒”反馈文案改为普通用户可理解的时间表达，明天不再显示成“1440 分钟后”。
- 新增 `snooze_delay_label()` 回归测试，确认 legacy、当前运行镜像的人类可读延后文案一致。
- 已补提醒反馈 QA 证据和 exe 桌面烟测截图：`qa/tk-ui-0.11.57-reminder-feedback-20260705/reminder-feedback-evidence.json`、`qa/tk-ui-0.11.57-reminder-feedback-20260705/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-180455.zip`，ZIP SHA256 `547BC2327D3A92E00134BC045A24696E9C5FF841F029A48DB31880F2DE2127C0`，EXE SHA256 `DD5854AD54A56B149FED96DE6B45315EBC0C776FB780653C3FC5334146CE42C6`。

## 0.11.56-tk-initial-roam-trust-fix - 2026-07-05

- 继续按付费用户严苛审计桌宠本体体验：修复默认日常模式虽然写着 120 秒低频巡游，但首次启动后 2-4 秒就可能自动移动的打扰问题。
- 新增 `next_roam_timestamp()` 作为首次和后续自动巡游的统一调度入口；右键“巡逻一下”仍保持用户主动触发时立即执行。
- 新增回归测试，确认 legacy、当前运行镜像的日常模式首次自动巡游延迟为 84-162 秒，并确认旧的 `random.uniform(2.0, 4.0)` 启动逻辑已移除。
- 已补运动调度 QA 证据和 exe 桌面烟测截图：`qa/tk-ui-0.11.56-motion-20260705/initial-roam-schedule.json`、`qa/tk-ui-0.11.56-motion-20260705/exe-smoke-desktop.png`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-174959.zip`，ZIP SHA256 `3D44E5CD842EF16F51FC7B8B39D0CD048579370A9E52F472BCAAC3430B9E5EFB`，EXE SHA256 `BA1E6AFC7D1657276EBEC8FE9B2624150BF6CF4D311C05BC0D496C973A065DD7`。

## 0.11.55-tk-paid-chat-copy-and-input-visibility - 2026-07-05

- 继续按付费用户严苛审计收口：包内使用说明、聊天发送提示、连接测试 Toast、资料查询状态和陪聊失败状态统一使用“云端陪聊 / 陪聊服务”口径。
- 修复聊天窗口 560x680 场景下角色 Skill 区过高、底部输入区容易被挤出可见范围的问题；角色详细说明默认移出首屏，聊天历史区设置更小初始高度。
- 已补最终发行包截图：`qa/tk-ui-0.11.55-paid-copy-20260705/chat-composer-copy-final-scaled.png`，确认输入框、发送按钮和“当前云端陪聊/本地陪伴”提示可见。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-173901.zip`，ZIP SHA256 `8DFA38BC2A5A6E38D3908058C4648E63C8345D2A1AB13DAAC85FE3A845D74816`，EXE SHA256 `385ADD30621F437DD901155006BFAB32D3C68154BDF4015EDA1A5E8F22D03BD6`。

## 0.11.54-tk-paid-language-unification - 2026-07-05

- 继续按付费用户严苛审计收口：控制面板内部仍保留 `AI` 页面 key，但侧栏、页面标题和失败提示展示为“陪聊设置”，避免入口叫陪聊、落地页又变成工程化 `AI`。
- 新增“陪聊设置 / 云端陪聊”页面别名，刷新当前页或从展示名恢复页面时仍能回到原 AI Provider 配置页。
- README 当前功能说明同步为高级模式显示“陪聊设置”，用户手册不再回退到工程命名。
- 已补最终发行包截图：`qa/tk-ui-0.11.54-paid-language-20260705/ai-page-label.png`，确认发行包页面标题显示“陪聊设置”。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-172236.zip`，ZIP SHA256 `667C7513B33113AF31660AA42E1BB50B95C911BF339A34AA2B213956FC4C8632`，EXE SHA256 `DAB8003C2B01ED838D530722A525BEF22ABCFBBB0DFB925E162C68429B090B13`。

## 0.11.53-tk-paid-trust-ai-safety-copy - 2026-07-05

- 继续按付费用户严苛审计收口：对话页、首页、操作页、导出弹窗和包内说明把普通入口统一为“陪聊设置/云端陪聊”，降低 API 调试台感。
- AI 页连接状态改为 Key 感知：无 Key 时显示“云端陪聊 / 待配置”，有 Key 时显示“已配置”，不再出现 Key 未配置但“AI 对话已开启”的自相矛盾状态。
- 安全页本地数据位置改为“当前安装目录 / exports”等友好标签，完整路径通过按钮打开，不再把开发机绝对路径直接铺在首屏。
- 包内使用说明同步为普通用户口径，导出数据文案改为“陪聊服务配置”，真实 API Key 仍不导出。
- 已补最终发行包截图：`qa/tk-ui-0.11.53-paid-trust-20260705/` 覆盖对话、AI、安全三页，确认“待配置”和“当前安装目录”文案生效。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-170551.zip`，ZIP SHA256 `63FCF47D18D6672148E560F2658666EE2E3CE73D1D1596B47661629CC5A0C163`，EXE SHA256 `CFE0E33D88C1EAFFC058EC0742622481E9BA3B8CD3DBED71468657A758A20237`。

## 0.11.52-tk-right-menu-small-screen-scroll - 2026-07-05

- 右键菜单新增屏幕高度自适应：布局 token 增加 `max_height_ratio=0.78/min_scroll_body_height=180`，低矮屏幕或远程桌面下会把按钮区压到安全高度并启用鼠标滚轮滚动。
- “窗口”分组前移到常用入口后面，确保小屏初始视图里能直接看到“暂停活动 / 隐藏气泡 / 退出”，不再需要先滚到底部。
- 右键入口“AI 配置”改为“陪聊设置”，页面仍指向 AI 设置，但首屏文案更接近普通用户语义。
- 主程序 fallback 同步扩展动作可见上限为 3，并保留无 modular 目录时的右键高度计算，避免 PyInstaller 发行包与开发镜像行为不一致。
- modular UI 测试新增右键 viewport clamp 覆盖；当前运行镜像和发行包 `validate_phase3.py` 均输出 `sections=common/window/activity_modes/base_actions/extension_actions`，`warnings` 为空。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-164939.zip`，ZIP SHA256 `AB7F239C26CE8870B51F4105EF6272B552D570D6590E969F208E28CAD52EF771`，EXE SHA256 `F682083513F0DCE788C7FEB2D8B848575635C6F73C40983A4209832A04915C44`。

## 0.11.51-tk-right-menu-compact-single-pet - 2026-07-05

- 右键快捷菜单改为 3 列紧凑布局，布局 token 调整为 `columns=3/min_width=540/max_width=620/button_min_height=32`，降低 720p/768p 或远程桌面窗口下底部操作不可见的风险。
- 扩展动作主菜单只展示前 3 个，其余进入“更多动作”，避免多宠/多扩展动作时右键菜单越堆越高。
- 公开单宠包不再显示“切换形象”空入口；只有存在多个 ready 宠物时才在右键菜单展示切换入口。
- 包内使用说明按导出宠物数量生成：单宠版说明为“形象页查看/管理资料”，多宠包才提示右键切换形象。
- modular UI 测试覆盖单宠隐藏切换入口和新右键布局契约；当前运行镜像 `validate_phase3.py` 已输出 `columns=3/min_width=540/max_width=620`。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-162937.zip`，ZIP SHA256 `B4096078FACECCBD74A8E5AFE72F85A48E1BBC571ACF613AFA1E86FAF4932E01`。

## 0.11.50-tk-settings-trust-hardening - 2026-07-05

- 修复旧设置缺失或无效 `activity_mode` 时的迁移问题：升级后会真正应用“日常”低打扰参数，避免 UI 显示日常但仍保留旧的频繁说话、多屏巡游和进屏幕中心倾向。
- 设置页从开发者表单改为普通用户优先的本地文件夹卡片；当前桌宠目录内路径用“当前桌宠目录”别名展示，减少工程路径暴露。
- GitHub macOS 构建配置改为“开发者构建工具”并默认折叠；保存配置和写入 workflow 改为面板 Toast 反馈。
- modular settings store 增加旧设置迁移测试，当前运行镜像 `validate_phase3.py` 已能证明巡游间隔、多屏和中心策略回到日常边界。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-160513.zip`，ZIP SHA256 `FD20E7C4B34965B2FCA36B8AC302590108C795AB5329649CAF82BDA5CC71C4B2`。

## 0.11.49-tk-activity-mode-hardening - 2026-07-05

- 新增共享“陪伴模式”模型，安静、日常、活跃三档统一控制自动说话、巡游开关、巡游间隔、速度、范围、置顶和屏幕中心策略。
- 首页新增“陪伴模式”卡片；行为页旧开发者参数预设改为同一套模式入口，避免“安静”仍频繁说话、“日常”过于活跃。
- 右键快捷菜单新增“陪伴模式”分组，可直接切换安静/日常/活跃；“暂停活动/恢复日常”改为复用同一套模式逻辑。
- 右键菜单布局 token 加宽到 `min_width=460/max_width=540`，修复新增模式分组后两列按钮被裁切的问题。
- 安静模式关闭自动说话和自动巡游；日常模式保持低频沿边陪伴；活跃模式提高互动频率但仍默认不置顶、不跑进屏幕中心。
- 干净发行默认体型缩放从 0.50 收敛到 0.46，降低首次启动占屏和遮挡感。
- 已生成并验证 Windows 免 Python 包：`packages/danhuang-desktop-pet-windows-20260705-131843.zip`，ZIP SHA256 `8936698700EAF4F93ED5698BFBA7E2A2CEF0BC69F7448396649FEA836D3FED5F`。

## 0.11.48-tk-paid-beta-trust-hardening - 2026-07-05

- 发行默认值改为低打扰：默认不置顶、边缘活动、低频说话和低速巡逻；公开包清洗层不再继承本机跨屏、快捷动作、路径和 GitHub 配置。
- 右键快捷菜单新增“安静一下”和“暂停活动/恢复日常”，用于临时或持久降低打扰。
- 控制面板默认导航收口为首页、对话、提醒、形象、动作、安全；AI、档案、故事、行为、操作、设置、巡逻、外观保留在高级模式或指定入口。
- 提醒页快速记录默认按生活事项处理，时间格式和添加失败改为页内状态 + 暖色 Toast，不再弹系统错误框。
- 安全页新增本地数据位置卡片，可打开数据目录和导出目录；README 和包内安装说明改为普通用户可理解的免 Python 安装路径，并明确不写开机自启。
- 公开包宠物配置改为蛋黄单宠版，清空 `identity_image` 和 `reference_images`，避免用户上传源图、现实照片或身份参考图进入发行包。
- 已生成 Windows 免 Python exe 包：`packages/danhuang-desktop-pet-windows-20260705-122408/` 和 `packages/danhuang-desktop-pet-windows-20260705-122408.zip`，zip SHA256：`791D9F5409CF79CC45A0E2C594C473043FFB16EADC6F9E7886AAF0DE9B859EF8`。

## 0.11.47-tk-panel-grid-hardening - 2026-07-05

- 在当前 `DanhuangProduct-tk` 根目录重建 `data-dev/current-runtime/danhuang/` 运行镜像，主程序以 `tk/main` 的 legacy monolith 为准，资源来自本机既有 Tk 运行资产。
- 控制面板继续复用 `panel_button_grid()`，将首页/陪伴操作、行为页预设与屏幕策略、提示词操作、提醒页常用时间与待办操作、安全页备份/导出操作和底部操作条改为固定列网格，降低窄窗口按钮挤压和横向溢出风险。
- AI 页 Provider 操作和测试结果操作改为网格布局，Key 为空、Key 保存失败和测试前保存失败改为面板 Toast + 状态行反馈，不再弹出割裂的系统消息框。
- 本次不改 Vue/Tauri，不改宠物资源、动作 ID、AI Provider 数据契约或 DPAPI/Key 存储逻辑。

## 0.11.45-tk-pet-category-action-prompts - 2026-07-03

- Tk 分类预设新增动作画像：`identity_focus`、`motion_rules`、`avoid_rules`、`quality_rules`，用于统一 UI 摘要和 AI 生图提示词。
- 基础动作、单行动作修复和扩展动作提示词改为按分类读取动作细节，鸟类按跳步/拍翅，水生按游动/摆鳍，人物按两足走路/招手，机器人按滑行/机械臂，物件和植物按挪动/摆动处理。
- 右键快捷动作和动作页基础动作栏开始使用当前宠物分类的短标签，例如水生为“游一小段”、人物为“走一小段”、机器人为“滑一小段”。
- 模块化核心补充 `pet_category_action_profile()`，并增加测试覆盖非猫狗分类不再套用猫狗动作语义。
- 产品文档补充分类动作画像、提示词规则和验收标准；本次仍不改宠物 ID、动作槽位和现有 spritesheet 顺序。
- 已生成 Windows 免 Python exe 包：`packages/danhuang-desktop-pet-windows-20260703-165013/` 和 `packages/danhuang-desktop-pet-windows-20260703-165013-exe.zip`，zip SHA256：`3F45FB0E588DD761F0C9CFC47CE68C0D8A6E7D7FAE3D1175E9A748A62BB11AA5`。
- `packages/` 已清理旧包，只保留最新 `20260703-165013` 文件夹和 zip。

## 0.11.44-tk-pet-category-taxonomy - 2026-07-03

- Tk 宠物分类从扁平 `dog/cat/human/robot/other` 升级为「一级大类 / 二级类型 / 三级细分 / 细节描述」。
- 新增字段契约：`category_group`、`category`、`category_subtype`、`category_detail`；现有 5 个宠物已迁移到明确细分分类。
- 新增三层分类选择 UI，导入宠物和编辑资料共用同一控件，避免所有分类按钮挤在一行或一块。
- 形象页当前宠物卡片新增体态、动作和基础动作摘要。
- AI 生图提示词带入分类、体态、动作语义和推荐扩展动作，人物、鸟类、水生、机器人、物件不再默认套用猫狗动作。
- 新增产品技术文档：`docs/product/蛋黄-Tk宠物分类体系-技术文档-v1.md`。
- 已生成 Windows 免 Python exe 包：`packages/danhuang-desktop-pet-windows-20260703-161901/` 和 `packages/danhuang-desktop-pet-windows-20260703-161901-exe.zip`，zip SHA256：`5FF6EB2A763D494A831476C346C381FB2545CE92F89B7717DBBF626AC4F4B5A1`。
- `packages/` 已清理旧包，只保留最新 `20260703-161901` 文件夹和 zip。

## 2026-07-03-tk-only-project-route

- 当前产品主线收敛为 Python/Tk，WPF Spike/技术验证目录已移除，不再作为后续同步目标。
- 新增当前项目梳理文档：`docs/product/蛋黄Tk当前项目梳理_20260703.md`，明确 Tk 代码基线、E 盘运行镜像、模块化阶段、非主线目录和下一步优先级。
- 更新 README、架构、路线图、目录治理、UI 设计规格和执行追踪，移除当前路线中的 WPF 运行/同步要求。
- 固化 Tk 打包规则：每次完成 Tk 功能优化、UI 优化或运行逻辑修复后，都必须同步 E 盘运行镜像，并重新生成 Windows 可执行 exe 包到 `packages/`。
- 基于当前 Tk `0.11.43` 生成 Windows 免 Python exe 包：`packages/danhuang-desktop-pet-windows-20260703-142158/` 和 `packages/danhuang-desktop-pet-windows-20260703-142158-exe.zip`，zip SHA256：`1ADAEF3205322C35ECBD447E769B4562EAA2F54F1E0DB6963359C7ED91F69814`。
- 清理旧 Tk Windows 打包记录，只保留最新 `20260703-142158` 文件夹和 zip，释放约 723 MB；后续新包验证通过后默认删除旧包。

## 0.11.43-prototype-bubble-renderer-module - 2026-06-18

- 新增 `src-prototype/modular/ui/tk_bubble_render.py`，把 soft、rounded、cloud、thought、note、caption 六种气泡的 Pillow 图片绘制从单文件中抽成独立 renderer。
- E 盘 Tk 单文件运行镜像和 legacy monolith 的 `render_bubble_image()` 现在优先调用 modular renderer；模块不可用或渲染失败时保留旧单文件绘制函数回退。
- `validate_phase3.py` 的 bubble 摘要新增 `renderer_styles`，用于验证六种气泡样式均可在无 GUI 条件下输出 RGBA 图片。
- Phase 3 UI 单元测试补充气泡 renderer 样式覆盖；运行集成测试更新到 `APP_VERSION=0.11.43` 并检查运行入口已加载 modular renderer。
- 未修改 C 盘当前运行版主程序，因此不需要重启 C 盘桌宠。

## 0.11.42-prototype-right-menu-style-position-model - 2026-06-18

- 新增 right-menu style tokens 和 `compute_menu_position()`，把右键主面板的宽度约束、列数、按钮最小高度、屏幕边距、与宠物避让间距和按钮/弹层颜色 token 抽成纯模型。
- E 盘 Tk 单文件运行镜像和 legacy monolith 已开始消费 right-menu style/layout：主面板 shell/header/body、按钮 variant、禁用态、宠物切换弹层行选中态和更多动作弹层 footer 均优先读取 model；模块不可用时保留旧颜色和定位逻辑。
- 右键主面板定位现在优先使用 modular 坐标模型：右侧优先、左侧/下方/上方候选避让宠物，最后才回退到点击点附近。
- `validate_phase3.py` 的 right_menu 摘要新增 `layout` 和 `style_variants`，便于设计工具和 WPF 后续承接右键面板尺寸、状态和颜色 token。
- README 和 WPF 技术验证说明补充 WPF Spike 运行命令，当前可用 `dotnet run --project ...` 查看透明置顶窗口效果。
- WPF Spike 增加 `ShowActivated`、任务栏显示、启动后主动激活和非关闭按钮早期关闭保护；用于避免从自动化 shell 启动时窗口闪退或被后台清理导致看不到效果。
- Phase 3 UI 单元测试补充主面板定位避让和样式 token 隔离；运行集成测试更新到 `APP_VERSION=0.11.42`。
- 未修改 C 盘当前运行版主程序，因此不需要重启 C 盘桌宠。

## 0.11.41-prototype-right-menu-popup-position-model - 2026-06-18

- 新增 right-menu popup layout 和 `compute_popup_position()`，把右键子弹层的间距、屏幕边距、关闭延迟、更多动作展示上限和左右侧放置策略抽成纯模型。
- E 盘 Tk 单文件运行镜像和 legacy monolith 已让“切换形象”和“更多动作”两个弹层共用同一个 `place_quick_menu_popup()`，优先消费 modular 坐标模型；模块不可用时回退旧定位逻辑。
- “更多动作”弹层的最大可见动作数量开始读取 popup layout，不再在单文件里硬编码为 10。
- `validate_phase3.py` 的 `pet_switcher` 摘要新增 `popup_layout`，便于设计工具和 WPF 后续承接弹层间距、边距和关闭时序。
- Phase 3 UI 单元测试补充弹层右侧优先、右侧溢出翻左、屏幕内夹取等定位规则；运行集成测试更新到 `APP_VERSION=0.11.41`。
- 未修改 C 盘当前运行版主程序，因此不需要重启 C 盘桌宠。

## 0.11.40-prototype-pet-switcher-model - 2026-06-18

- 新增 `build_pet_switcher_model()`，把右键“切换形象”弹层的标题、当前宠物排序、最多展示数量、隐藏数量、空态和管理入口抽成纯 view model。
- E 盘 Tk 单文件运行镜像和 legacy monolith 已新增 `pet_switcher_view_model()`，切换形象弹层优先消费 model 的 `items/footer/empty/title`，照片仍由 Tk 渲染层按 `pet_id` 读取。
- `build_pet_switcher_model()` 同时兼容运行期 `id` 和资产 manifest `pet_id`，避免 runtime family 与 Phase 3 asset manifest 字段漂移。
- `validate_phase3.py` 现在会输出 `pet_switcher` 摘要，便于设计工具和后续验证看到可切换形象数量、当前宠物和管理入口。
- Phase 3 UI 单元测试补充 pet switcher 当前态排序、展示上限、隐藏数量、footer 和 `pet_id` 兼容性；运行集成测试更新到 `APP_VERSION=0.11.40`。
- 未修改 C 盘当前运行版主程序，因此不需要重启 C 盘桌宠。

## 0.11.39-prototype-right-menu-model-rendering - 2026-06-18

- E 盘 Tk 单文件右键快捷面板继续接入 `ui/tk_right_menu.py` 的完整 `sections/items/footer/layout/header` 合同。
- 右键面板标题、副标题、自动关闭时间和外部点击检测延迟开始读取 right-menu layout/header model。
- 常用入口、基础动作、扩展动作、更多动作入口、管理动作和窗口命令现在优先按 model item 的 `command/page/variant/enabled/action_id/loops` 渲染；模型不可用时仍保留旧硬编码分组兜底。
- “更多动作”弹层现在优先消费 `hidden_extension_buttons`，文案、可用态和播放循环数与右键主面板使用同一模型来源。
- Phase 3 UI 单元测试补充 right-menu 可渲染命令合同；运行集成测试更新到 `APP_VERSION=0.11.39`。
- 未修改 C 盘当前运行版主程序，因此不需要重启 C 盘桌宠。

## 0.11.38-prototype-bubble-window-model-runtime - 2026-06-18

- E 盘 Tk 单文件运行镜像和 legacy monolith 继续接入 Phase 3 UI 状态模型。
- `say()` 现在会优先读取 `ui/tk_bubble.py` 的气泡 view model，托管样式规范化、文字颜色、文本宽度和显示时长；Canvas 实测排版和图片绘制路径继续保留。
- `position_bubble()` 现在会优先读取 `ui/tk_bubble.py` 的屏幕内定位模型；模块不可用或计算失败时自动回退旧定位逻辑。
- `base_pet_size()` 现在会优先读取 `ui/tk_pet_window.py` 的基础窗口尺寸模型；真实渲染尺寸和当前图片尺寸链路仍保留旧逻辑。
- 新增 Phase 3 运行集成测试，覆盖两份 E 盘单文件能否加载 modular 的右键菜单、气泡和窗口模型。
- 未修改 C 盘当前运行版主程序，因此不需要重启 C 盘桌宠。

## 0.11.37-wpf-spike-and-right-menu-model-runtime - 2026-06-18

- 安装并验证 .NET 9 SDK 9.0.315，本机已可构建 WPF 技术验证工程。
- 在 `src-windows-wpf/` 生成 `Danhuang.WpfSpike` 和 `DanhuangProduct.sln`，并把空白模板改为暖色透明置顶窗口 Spike，覆盖拖动、置顶切换、右键面板和气泡验证占位。
- WPF Spike 已通过 `dotnet build .\DanhuangProduct.sln`，0 警告、0 错误。
- E 盘 Tk 单文件运行镜像和 legacy monolith 已接入 `ui/tk_right_menu.py` 的右键菜单 view model：模型可用时使用 modular 输出的基础动作、可见扩展动作和隐藏扩展动作；模块不可用时自动回退旧逻辑。
- 更新设计说明、路线图、目标架构、WPF 技术验证规格和执行追踪，移除“dotnet 缺失阻塞”的旧状态。
- 未修改 C 盘当前运行版主程序，因此不需要重启 C 盘桌宠。

## 0.11.36-prototype-phase3-ui-models - 2026-06-18

- 落地 Tk 原型模块化 Phase 3 第二批：右键菜单、气泡和桌宠窗口 UI 状态模型。
- 新增 `src-prototype/modular/ui/tk_right_menu.py`，把右键快捷面板拆成常用、基础动作、扩展动作和窗口命令的纯 view model，并保留“更多动作 +N”边界。
- 新增 `src-prototype/modular/ui/tk_bubble.py`，负责气泡样式、颜色、尺寸估算、阴影色和屏幕内位置计算。
- 新增 `src-prototype/modular/ui/tk_pet_window.py`，负责桌宠窗口尺寸、默认位置、屏幕夹取、置顶透明度和巡逻策略摘要。
- `validate_phase3.py` 现在会同时输出当前宠物右键菜单、气泡和窗口行为摘要，仍然只读 E 盘运行镜像。
- 未修改 C 盘当前运行版主程序，因此不需要重启桌宠。

## 0.11.35-prototype-phase3-assets-and-ui-brief - 2026-06-18

- 落地 Tk 原型模块化 Phase 3 第一批：动作资产和 manifest 纯逻辑。
- 新增 `src-prototype/modular/assets/atlas.py`，负责 spritesheet 网格、标准动作行、扩展动作条尺寸、帧数和时长校验。
- 新增 `src-prototype/modular/assets/manifest.py`，负责宠物动作 manifest、动作标签、复合跑动、右键动作选择和 family 级动作摘要。
- 新增 `src-prototype/modular/validate_phase3.py` 和资产单元测试，可只读 E 盘运行镜像输出 5 个宠物、54 个可播放动作和 11 个扩展动作摘要。
- 新增 `docs/product/蛋黄桌宠总体UI设计说明.md`，用于交给外部设计工具生成总体 UI 方案，覆盖控制面板、右键面板、聊天窗、提醒页、动作页、形象页和安全页。
- 未修改 C 盘当前运行版主程序，因此不需要重启桌宠。

## 0.11.34-prototype-phase2-core - 2026-06-18

- 落地 Tk 原型模块化 Phase 2：AI Provider、待办和提醒历史三类核心逻辑。
- 新增 `src-prototype/modular/core/ai_providers.py`，负责 Provider 默认配置、规范化、当前 Provider、连接端点和公开摘要脱敏，真实加密 Key 不进入导出视图。
- 新增 `src-prototype/modular/core/todos.py`，负责待办 CRUD、聊天新增意图、查询意图区分、重复待办、稍后提醒、到期待办筛选和本地查询回复。
- 新增 `src-prototype/modular/core/reminder_history.py`，负责提醒事件规范化、时间轴摘要和最近事件截断。
- 新增 `src-prototype/modular/validate_phase2.py` 和 Phase 2 单元测试，验证 E 盘运行镜像可读、Provider 摘要不泄漏密钥、待办查询不会误判为新增。
- 未修改 C 盘当前运行版主程序，因此不需要重启桌宠。

## 0.11.33-tk-chat-role-skill-detail - 2026-06-17

- 聊天角色 Skill 从 6 个扩展到 8 个，新增“知识博主”和“短视频编导”两类泛化达人风格。
- 每个角色 Skill 补齐适用场景和角色边界，并写入 AI prompt；角色只改变表达方式，不覆盖宠物身份、主人关系和真实故事边界。
- 聊天窗角色区改为 4 列两行按钮 + 当前角色说明卡，说明卡按窗口宽度动态换行，避免角色按钮或长说明挤压成竖排、重叠或横向溢出。
- 聊天窗顶层改为固定底部输入区的网格布局：聊天历史区负责伸缩，快捷按钮和输入框始终保留在窗口内。
- 最小窗口高度调整为 520x660，并补充全窗截图验收，避免只验角色区时漏掉底部输入框消失的问题。
- 泛化达人风格只借表达方法，不模仿具体真人达人、口头禅、个人经历或具体平台人设。
- WPF 重构时需要保留角色库元数据、当前角色说明卡、非真人模仿边界、固定底部输入区和全窗窄窗口截图验收。

## 0.11.32-tk-search-source-upgrade - 2026-06-17

- 联网资料查询新增中文维基摘要补强：非实时知识类问题会先尝试拿百科摘要，再合并网页搜索结果。
- 搜索层从 DuckDuckGo Lite + 中文维基 OpenSearch 扩展为 DuckDuckGo Lite、Bing HTML 兜底、中文维基摘要和中文维基 OpenSearch 多来源合并。
- 本地无 AI 兜底回复会显示来源类型和 URL，减少“查到了但不知道来源”的情况。
- 查询词清洗补充“什么是 / 谁是 / 是什么 / 是谁 / 什么意思”，让普通知识问句更容易命中实体摘要。
- WPF 重构时需要保留“实体词清洗 + 多来源搜索 + 来源标注 + 实时问题不强行走百科”的检索策略。

## 0.11.31-tk-family-list-layout-fix - 2026-06-17

- 修复形象页“家人形象列表”右侧操作列过窄导致“切换/编辑资料”按钮文字被挤成竖排的问题。
- 列表行取消窄操作列，操作按钮移入卡片内容区并使用稳定像素宽度，分类/照片/动作信息过长时截断显示。
- 移除默认宠物代码中的历史本机图片路径，公开 exe 包继续保持无本机路径、无 API Key、无聊天/待办/提醒历史。
- 新增形象页截图验收：`qa/tk-family-list-actions-inline-900-20260617.png` 和 `qa/tk-family-list-actions-inline-900-scrolled-20260617.png`。
- UI 验收规则补充：后续页面改动必须检查按钮文字、状态 chip、长说明在常规宽度下不重叠、不竖排、不横向溢出。

## 0.11.30-tk-pet-category-actions - 2026-06-17

- 新增宠物和编辑资料接入细分类模型，覆盖犬类、猫类、兔类、小型哺乳、大型哺乳、鸟类、爬行动物、水生生物、昆虫/节肢、人物、幻想生物、机器人、拟物/物件和其他。
- 形象页展示当前宠物分类，新宠物导入和资料编辑使用分类 chip，避免后续人物、幻想生物或拟物角色仍被硬套猫狗动作。
- 五个基础动作槽位继续兼容旧 atlas，但 UI 文案和生图提示词按分类解释动作语义，例如人物是站立/走路/招手，鸟类是跳步/拍翅，水生生物是漂浮/游动。
- AI 宠物上下文和生图提示词补入分类、示例和动作方向；WPF 重构时需要保留分类数据字段、分类选择入口和分类化动作标签。

## 0.11.29-tk-chat-role-skills - 2026-06-17

- 聊天窗新增“角色 Skill”选择区，内置蛋黄本色、技术导师、产品拆解、研究助手、直说教练、运营写手六种表达风格。
- 角色 Skill 会保存到本机设置，后续 AI 回复自动带入当前角色风格；蛋黄的家人身份和主人关系仍是底层约束。
- 角色 preset 使用能力风格，不冒充具体真人达人；适合后续继续接入本地 skill 或用户自定义角色。
- WPF 重构时需要保留“宠物身份 + 可选角色 Skill”的双层提示词模型，以及聊天窗内的角色选择入口。

## 0.11.28-tk-chat-general-qa - 2026-06-17

- AI 聊天新增通用知识问题识别：`什么是 / 谁是 / 为什么 / 怎么 / 如何 / 多少 / 哪里 / 哪年 / 有哪些` 等提问会自动进入资料查询链路。
- AI 可用时会先检索网页资料再交给模型组织回复；AI 未配置时也会给本地网页摘要，减少“问很多问题回答不了”的情况。
- 搜索层在 DuckDuckGo Lite 之外补充中文维基百科 OpenSearch 作为知识类问题备用来源，并对多来源结果做去重合并。
- 保留陪伴语境排除：`你是谁 / 你叫什么 / 想你 / 陪我 / 摸摸` 等仍走宠物陪伴回复，不会误触发网页查询。
- WPF 重构时需要保留显式查询词和通用知识问题两级触发，并保留陪伴语境排除。

## 0.11.27-tk-chat-quick-grid - 2026-06-17

- 聊天窗快捷入口从单行按钮改为 4 列自适应网格，两行稳定展示“累了、难过、想你、休息、时间、待办、查资料、背景”。
- 继续保留时间、待办和联网查询入口，但避免后续新增工具按钮时横向撑爆聊天窗。
- WPF 重构时聊天窗快捷工具区应使用 WrapPanel/UniformGrid 这类可换行布局，而不是固定单行工具栏。

## 0.11.26-tk-chat-todo-lookup - 2026-06-17

- 聊天新增本地待办查询工具，问“今天有什么安排 / 待办有哪些 / 查看一下今天待办”时直接读取本地待办摘要。
- 待办查询优先于新增待办，但“提醒我明天 9 点开会”“帮我记一下后天发材料”等创建意图仍会正常新增提醒。
- 本地待办查询回复包含标题、提醒时间、分类、优先级和总览统计；AI 未配置时也能回答日程类问题。
- 聊天窗快捷区新增“待办”入口，并压缩快捷按钮宽度避免横向溢出。
- WPF 重构时需要保留“查询待办”和“新增待办”的意图区分，不能把日程查询误写成新待办。

## 0.11.25-tk-chat-capability-status - 2026-06-17

- 聊天窗新增能力状态条，显式展示云端、时间、资料、待办和兜底五类当前能力状态。
- 云端状态会按 AI 开关和 Key 配置显示“已连 / 待配置 Key / 已关闭”；资料查询状态区分“查后给 AI”和“本地摘要”。
- 待办状态条展示未完成和今日待办数量，聊天创建待办后会刷新，减少用户猜测当前上下文是否被读取。
- 聊天窗关闭时清理状态条控件引用，避免反复打开后残留旧窗口控件。
- WPF 重构时需要保留同一能力状态模型，可落地为聊天窗顶部 InfoBar/StatusPill 组合。

## 0.11.24-tk-ai-chat-tools-and-exe - 2026-06-17

- 聊天链路新增本地工具层：问“现在几点/今天几号”时直接用本机时间回复，不再绕 AI。
- 联网查询触发词扩展到上网查、联网查、实时、最近、天气、股价、汇率等；AI 未连接时也会返回本地网页摘要兜底。
- AI 快速回复提示词补入当前时间和本地待办摘要，让日常安排、待办和实时资料回答更顺滑。
- 聊天窗快捷区新增“时间”“查资料”入口；AI 页资料查询说明补充本机时间和无 AI 时的联网摘要兜底。
- 控制面板底部“保存”后显示暖色 Toast，明确设置已写入 E 盘运行配置。
- 同步准备当前 E 盘运行版 Windows exe 打包，公开包继续清空聊天、待办、提醒历史、陪伴状态和 API Key，并把应用图标写入 PyInstaller exe。

## 0.11.23-tk-ai-provider-test-toast - 2026-06-14

- 新增控制面板暖色 Toast 反馈组件，挂在当前控制面板右上角，自动关闭并保留手动“关闭”入口。
- AI Provider 连接测试成功时显示“AI 测试成功”Toast，展示厂商和接口返回摘要；“测试并启用”成功后提示已设为当前。
- AI Provider 连接测试失败时显示“AI 测试失败”Toast，展示恢复用错误说明；页面内状态卡和测试结果文本继续保留。
- Toast 只用于本地 UI 反馈，不写入 Provider 配置、聊天记录、日志或公开导出包。
- 同步 Tk UI 优化清单，后续 WPF AI Provider 页需要保留“状态卡 + 测试中禁用 + 成功/失败 Toast 或 InfoBar”的反馈组合。

## 0.11.22-tk-chat-window-feedback - 2026-06-14

- 聊天窗底部输入区升级为暖色输入卡，新增标题、状态提示、输入框描边和主发送按钮。
- 空输入改为聊天窗内联错误提示，不再静默清空；发送后显示等待回复状态。
- AI 回复等待期间“发送”按钮切换为“发送中...”并禁用，避免同一聊天窗重复提交。
- AI 状态栏按云端可用、本地兜底、失败或未连接展示不同文字颜色，但状态仍保留明确文本，不只靠颜色表达。
- AI 失败时保留原本本地兜底逻辑，同时在输入区提示“AI 没接上”；后续 WPF 聊天窗需要保留输入反馈、发送中禁用和失败可恢复状态。

## 0.11.21-tk-ai-provider-key-confirm - 2026-06-14

- AI Provider 页“替换 Key”从系统确认框升级为暖色本地确认弹窗，说明新 Key 会覆盖旧 Key，旧 Key 不会显示。
- 替换 Key 和清除 Key 共用 AI 页内部确认弹窗样式，统一标题、说明卡、取消、确认和 Escape 关闭路径。
- 替换成功后继续沿用原本 DPAPI 本机加密保存逻辑；真实 Key 不写入日志、聊天记录或公开导出包。
- 取消替换或取消清除时改为页内状态反馈，避免系统弹窗风格割裂。
- 同步 Tk UI 优化清单，后续 WPF AI Provider 页需要保留“本地 Key 替换确认 + 清除确认 + Key 隐私边界”的结构。

## 0.11.20-tk-ai-provider-feedback - 2026-06-14

- AI Provider 页新增连接测试运行中状态锁：当前厂商测试时“测试并启用”按钮切换为“测试中...”并禁用，避免重复发起连接测试。
- AI 测试开始和结束后只在 AI 页可见时刷新当前页，让状态卡、底部测试结果和按钮禁用态保持同步；刷新后保留用户最后选中的厂商，成功后继续沿用原有自动设为当前逻辑。
- “清除 Key”从系统确认框升级为暖色本地确认弹窗，说明只清除本机加密 Key，不修改环境变量、不删除聊天记忆。
- 未保存 Key 时点击“清除 Key”改为页内状态反馈，不再弹出无意义确认；真实 Key 仍不显示、不导出。
- 同步 Tk UI 优化清单，后续 WPF AI Provider 页需要保留“测试中禁用 + 本地确认弹窗 + Key 隐私边界”的结构。

## 0.11.19-tk-reminder-history-window - 2026-06-14

- 提醒时间轴窗口从纯文本 `Text` 升级为暖色卡片式浏览窗口，顶部说明用途，摘要卡显示总记录、本次显示和最近更新时间。
- 最近 80 条提醒历史改为倒序事件卡，事件类型、时间、标题、分类、优先级、到期时间、重复和稍后分钟数分层展示。
- 新增空状态和底部说明，避免无记录时出现空白窗口；关闭按钮和 Escape 作为明确退出路径。
- 数据读取继续只使用本机 `reminder_history.events`，不改变提醒日志、完成、删除、稍后提醒和重复生成逻辑。
- 同步 Tk UI 优化清单，后续 WPF 提醒时间轴需要保留“摘要卡 + 事件卡 + 状态 chip + 空状态 + 明确关闭”的结构。

## 0.11.18-tk-reminder-due-popup - 2026-06-14

- 到点提醒弹窗从旧式小按钮窗口升级为暖色提醒卡，顶部说明当前状态，主体展示待办标题、状态 chip、分类、优先级、时间和提醒次数。
- 长备注在弹窗中截断预览，避免撑坏固定窗口；完整内容可通过“打开提醒页”查看。
- 弹窗操作改为主操作、打开详情和稍后提醒两层：完成为主按钮，打开提醒页为次按钮，15 分钟、1 小时、明天作为稍后提醒分组。
- 新增“关闭”和 Escape 关闭路径，不改变待办状态；完成和稍后提醒继续复用原有本地待办逻辑。
- 同步 Tk UI 优化清单，后续 WPF 到点提醒弹窗需要保留“状态摘要 + 待办卡片 + 分层操作 + 关闭不改状态”的结构。

## 0.11.17-tk-reminder-editor-panel - 2026-06-14

- 待办“详细/编辑”弹层从旧式单列表单升级为暖色分区面板，拆分为当前状态、事项和时间、提醒规则、备注和底部动作区。
- 编辑弹层新增当前状态 chip，显示新待办、已完成、已到点、今日、稍后或待办状态，以及提醒次数摘要。
- 标题为空和时间格式错误改为弹层内状态提示，减少系统错误弹窗打断输入。
- 保存后保持当前待办选中；新增待办保存后自动回到列表并选中刚创建的条目。
- 同步 Tk UI 优化清单，后续 WPF 提醒编辑弹层需要保留“状态摘要 + 分区表单 + 内联校验 + 分层动作”的结构。

## 0.11.16-tk-reminder-card-list - 2026-06-14

- 提醒页待办列表从原生 `Listbox` 升级为固定高度滚动卡片区，避免标题、时间、分类和状态挤在一行。
- 待办卡片新增显式选中态，当前项用“当前”状态 chip 标记；筛选后会保留当前项，失效时自动选中第一条可见待办。
- 列表卡片显示提醒时间、分类、优先级、置顶、重复、稍后和持续提醒信息，备注过长时在卡片内截断。
- 点击卡片查看详情，双击卡片进入详细编辑；原有完成/重开、编辑、置顶、时间轴、稍后提醒和删除动作保持不变。
- 同步 Tk UI 优化清单，后续 WPF 提醒页需要保留“固定高度列表 + 显式当前项 + 详情面板 + 分层操作”的结构。

## 0.11.15-tk-export-progress-status - 2026-06-14

- 安全页“安装包导出”新增“导出状态和路径”卡片，显示默认导出目录、结果路径说明和失败日志位置。
- 导出弹窗新增暖色状态卡，覆盖就绪、导出中、成功和失败四类状态。
- Windows 本地导出和 macOS 源码包导出改为后台线程执行，导出期间禁用底部按钮，避免面板卡住或重复点击。
- 导出成功后弹窗保留压缩包路径、入口脚本路径和导出目录；失败时显示 `desktop-pet-error.log` 路径和恢复建议。
- 同步 Tk UI 优化清单，后续 WPF 安全页需要保留“进度状态 + 结果路径 + 失败恢复建议”的导出反馈结构。

## 0.11.14-tk-appearance-bubble-color - 2026-06-14

- 外观页新增“外观总览”，集中展示体型、透明度、窗口置顶状态和当前气泡配色。
- “窗口”调整为“窗口行为”，保留体型、透明度、屏幕限制、置顶和多屏尺寸锁定设置。
- 对话框颜色从小色块升级为可点击预设卡，卡片直接展示气泡效果并标记当前配色。
- 新增当前颜色预览区、颜色值状态和“预览气泡”按钮，自定义背景/描边/文字颜色后立即刷新预览。
- 同步 Tk UI 优化清单，后续 WPF 外观页需要保留“总览 + 窗口行为 + 气泡预设卡 + 自定义颜色”的结构。

## 0.11.13-tk-dialog-bubble-preview - 2026-06-14

- 对话页新增“对话总览”，把快速试聊、AI 状态、记忆条数和当前气泡样式放到首屏。
- 快速试聊区补充空输入提示和发送状态，保留 Enter/发送按钮以及完整聊天窗入口。
- AI 与记忆区改为状态卡表达云端可用、本地兜底、待配置或已关闭，AI 未配置时不再只呈现错误感。
- 气泡外观区新增样式预览卡，点击预览即可切换样式，并保留跳转外观页调整颜色。
- 同步 Tk UI 优化清单，后续 WPF 对话页需要保留“快速试聊 + AI/记忆 + 气泡预览”的信息架构。

## 0.11.12-tk-archive-memory-density - 2026-06-14

- 档案页新增“长期记忆摘要”卡片，集中展示摘要更新次数、主要情绪、宠物级数据隔离和记忆条目。
- 最近聊天从逐条长文本改为按日折叠的摘要行，显示时间、说话双方、情绪和记忆更新状态。
- 每条聊天新增“查看详情”暖色阅读器，用于查看完整主人消息、宠物回复和记忆更新。
- 同步 Tk UI 优化清单，后续 WPF 档案页需要保留“陪伴指标 + 长期记忆 + 聊天详情”的信息层级。

## 0.11.11-tk-story-list-reader - 2026-06-14

- 故事页列表新增条目状态 chip，显式展示故事/日记/思念类型、时间和图片数量。
- 故事条目新增“查看全文”阅读器，用统一暖色窗口查看完整正文和图片缩略图。
- 删除操作从编辑/阅读操作中拆出，放入右侧危险区，降低误触。
- 同步 Tk UI 优化清单，后续 WPF 故事页需要保留宠物筛选、时间分组、全文阅读器和危险操作分区。

## 0.11.10-tk-safety-export-boundary - 2026-06-14

- 安全页新增“分发安全边界”首屏卡片，区分默认排除、弹窗可选和永不导出的数据。
- “配置安全”调整为“个人备份”，明确配置导出用于本人迁移，不应当作公开安装包分发。
- 安装包导出区新增公开分发规则，强调目标电脑首次启动默认空待办、空聊天、空 Key。
- 同步 Tk UI 优化清单，后续 WPF 安全页必须保留个人备份和公开分发的边界表达。

## 0.11.9-tk-action-preview-status - 2026-06-14

- 动作页“动作”卡片改为“动作预览”，每个动作显示可播放帧数、素材来源和右键栏状态。
- 预览区继续使用浅色播放按钮，避免把“能播放”和“已加入右键”混为同一种选中态。
- 右键动作列表保持独立配置区域，基础动作固定、扩展动作可加入或移出。
- 同步 Tk UI 优化清单，后续 WPF 动作页需要保留“动作预览状态”和“右键动作栏配置”分离。

## 0.11.8-tk-pet-assets-list - 2026-06-14

- 形象页拆出“家人形象列表”独立区域，不再把宠物列表继续塞在家庭宠物概览卡片里。
- 宠物列表行新增状态、动作包、照片/动作数量 chip，长说明只在中间区域换行。
- 每个宠物行右侧固定为纵向操作区，切换、当前、待生成和编辑资料按钮不再被描述文本挤压。
- 同步 Tk UI 优化清单，后续 WPF 宠物资产页需要沿用“概览 + 当前主形象 + 固定操作列表 + 现实照片”的结构。

## 0.11.7-tk-ai-provider-status - 2026-06-14

- AI 页新增选中厂商状态卡，明确未配置、已保存 Key、测试中、可用和失败状态，并给出恢复建议。
- AI 连接设置拆出模型选择、连接配置、本机 Key 和测试结果分段，高级连接参数继续默认收起。
- 替换已保存 Key 前增加确认；保存成功后的状态文案提示继续测试启用。
- 同步 Tk UI 优化清单，后续 WPF AI Provider 页需要保留同等状态机、恢复建议和 Key 隐私边界。

## 0.11.6-tk-reminder-density - 2026-06-14

- 提醒页快速新增区降密度：只保留事项、时间、重要程度和添加按钮；分类、重复、持续提醒和备注进入详细编辑。
- 待办筛选拆成搜索行与分类/焦点/完成状态筛选行，减少横向拥挤。
- 待办操作拆成主操作与稍后提醒/删除两层，删除远离主要动作。
- 同步 Tk UI 优化清单，后续 WPF 提醒页需要沿用“快速新增 + 筛选栏 + 列表 + 详情编辑”的信息架构。

## 0.11.5-tk-quick-menu-more-actions - 2026-06-14

- 右键快捷面板的扩展动作超过 4 个时显示“更多动作 +N”，点击后打开轻量弹层直接播放隐藏动作。
- “管理动作”保留为动作页入口，不再承担隐藏动作提示职责。
- 右键快捷面板补齐“窗口”分组，将“隐藏气泡”和“退出”从扩展动作区域拆出。
- 同步 Tk UI 优化清单，后续 WPF 托盘/右键入口需要保留同等更多动作弹层。

## 0.11.4-tk-quick-menu - 2026-06-14

- 右键快捷面板的“切换形象”改为点击后打开宠物选择弹层，不再依赖悬停触发。
- 宠物选择弹层新增“管理形象”入口，可跳转到控制面板形象页。
- 同步内置分发说明和 Tk UI 优化清单，后续 WPF 右键/托盘入口需要保留同等显式切换交互。

## 0.11.3-e-drive-runtime-and-tk-shell - 2026-06-14

- 将 C 盘历史运行版同步到 `data-dev/current-runtime/danhuang/`，并同步主程序、启动脚本和运行版 changelog 到 `src-prototype/legacy-monolith/`。
- 后续新增功能、UI 优化和试运行默认只在 E 盘产品目录进行，C 盘不再作为开发源。
- E 盘启动脚本会停止旧 C 盘蛋黄进程，避免新旧路径同时运行。
- 完成第一批 Tk 控制面板外壳优化：默认 920x640、左侧导航分组、`陪伴` 旧入口映射为 `首页`、首页危险操作下沉。

## 0.11.2-ui-backlog-doc - 2026-06-14

- 新增当前 Tk 桌宠 UI 优化清单，明确短期继续 Tk、自绘控件和截图验收，中期只做 `CustomTkinter` / `ttkbootstrap` spike，WPF 仍是 Windows 产品版主线。
- 将“当前版本 UI 优化也是产品资产，后续 WPF 必须同步实现”写入路线图和执行追踪。
- 未修改 C 盘当前运行版主程序，因此不需要重启桌宠。

## 0.11.1-prototype-modular-core - 2026-06-14

- 落地 Tk 原型模块化 Phase 1：宠物注册表、设置存储、陪伴状态三类纯逻辑。
- 新增 `src-prototype/modular/validate_phase1.py`，可对原型副本或冻结归档做只读验证。
- 新增 Phase 1 单元测试，覆盖设置夹取、右键动作过滤、宠物注册表去重、陪伴等级规范化和分发空状态。
- 同步执行追踪和拆分计划，下一步进入 AI Provider、待办和提醒历史拆分。
- 未修改 C 盘当前运行版主程序，因此不需要重启桌宠。

## 0.11.0-product-foundation - 2026-06-14

- 建立早期产品化工程根目录：`E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct`；当前 Tk 主线根已收敛为 `E:\ProgrammingAlgorithm\VSCodeProjects\DanhuangProduct-tk`。
- 将当前原型完整归档到 `archives/DanhuangPrototype-20260614-121543`，并设为只读。
- 复制当前 Tk 单文件原型到 `src-prototype/legacy-monolith/`。
- 生成原型审计：文件清单、隐私清单、宠物家庭清单、代码结构清单。
- 新增产品文档：PRD、路线图、目标架构、UI 重构、目录治理、隐私商业化、WPF 技术验证。
- 新增工程约束：`AGENTS.md`、`.editorconfig`、`.gitignore`。
- 当前未修改 C 盘运行版主程序，因此不需要重启桌宠。
