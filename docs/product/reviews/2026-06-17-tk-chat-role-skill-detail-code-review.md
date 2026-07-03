# Tk 聊天角色 Skill 详情代码审查

时间：2026-06-17

范围：

- `src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- `CHANGELOG.md`
- `src-prototype/legacy-monolith/CHANGELOG.md`
- `docs/product/CURRENT_TK_UI_OPTIMIZATION_BACKLOG.md`
- `docs/product/UI_REDESIGN_SPEC.md`
- `docs/product/wpf-tech-spike/WPF_TECH_SPIKE_SPEC.md`

## 结论

通过。

本次改动把聊天角色 Skill 从 6 个扩展到 8 个泛化风格，并在聊天窗增加当前角色说明卡。改动范围只影响角色 preset、聊天提示词和聊天窗角色选择布局，不改变 AI Provider 配置、联网检索、本地待办、聊天记忆或公开包隐私边界。

## 审查要点

- 正确性：每个角色 preset 都有 `label`、`short`、`best_for`、`boundary` 和 `prompt`；`chat_role_skill_prompt()` 会把适用场景和角色边界写入提示词。
- 身份边界：知识博主和短视频编导均为泛化表达风格，不模仿具体真人达人、口头禅、个人经历或具体平台人设。
- UI 稳定性：角色按钮使用 4 列网格，当前角色说明卡使用标题和说明上下结构，并按窗口宽度动态调整换行；520px 最小宽度下未出现竖排、重叠或横向溢出。
- 可维护性：WPF 重构可以直接复用角色库元数据，迁移为角色列表、当前角色说明卡和提示词组装器。

## 验证

- `python -m py_compile src-prototype/legacy-monolith/run-danhuang-desktop-pet.py`
- `python -m py_compile data-dev/current-runtime/danhuang/run-danhuang-desktop-pet.py`
- 角色库函数级断言：版本 `0.11.33`、8 个角色、知识博主/短视频编导存在、全部角色具备适用场景和角色边界。
- 截图验收：`qa/tk-chat-role-skill-detail-620-20260617.png`、`qa/tk-chat-role-skill-detail-520-20260617.png`。

## 剩余风险

- 这次只验证了聊天窗角色 Skill 区；整套控制面板页面截图基线仍需继续补齐。
