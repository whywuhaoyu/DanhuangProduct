from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CURRENT_RUNTIME_FILE = PROJECT_ROOT / "data-dev" / "current-runtime" / "danhuang" / "run-danhuang-desktop-pet.py"
RUNTIME_FILES = [
    PROJECT_ROOT / "src-prototype" / "legacy-monolith" / "run-danhuang-desktop-pet.py",
    CURRENT_RUNTIME_FILE,
]


def load_runtime_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"danhuang_runtime_{abs(hash(path))}", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Cannot load runtime module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Phase3RuntimeIntegrationTests(unittest.TestCase):
    def test_runtime_files_import_modular_ui_models(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                module = load_runtime_module(path)

                if path == CURRENT_RUNTIME_FILE:
                    self.assertEqual(module.APP_VERSION, "0.11.73")
                else:
                    self.assertTrue(hasattr(module, "APP_VERSION"))
                self.assertIsNotNone(module.MODULAR_BUILD_PET_ACTION_MANIFEST)
                self.assertIsNotNone(module.MODULAR_BUILD_PET_SWITCHER_MODEL)
                self.assertIsNotNone(module.MODULAR_BUILD_RIGHT_MENU_MODEL)
                self.assertIsNotNone(module.MODULAR_BUBBLE_PREVIEW_MODEL)
                self.assertIsNotNone(module.MODULAR_COMPUTE_BUBBLE_POSITION)
                self.assertIsNotNone(module.MODULAR_COMPUTE_RIGHT_MENU_POSITION)
                self.assertIsNotNone(module.MODULAR_COMPUTE_RIGHT_MENU_POPUP_POSITION)
                self.assertIsNotNone(module.MODULAR_LOCK_EDGE_ROAM_POSITION)
                self.assertIsNotNone(module.MODULAR_PET_WINDOW_SIZE)
                self.assertIsNotNone(module.MODULAR_RIGHT_MENU_POPUP_LAYOUT)
                self.assertIsNotNone(module.MODULAR_RIGHT_MENU_STYLE_TOKENS)
                self.assertIsNotNone(module.MODULAR_RENDER_BUBBLE_IMAGE)
                self.assertIsNotNone(module.MODULAR_WINDOW_BEHAVIOR_MODEL)
                self.assertTrue(hasattr(module.DanhuangPet, "quick_menu_view_model"))
                self.assertTrue(hasattr(module.DanhuangPet, "pet_switcher_view_model"))
                self.assertTrue(hasattr(module.DanhuangPet, "bubble_view_model"))
                self.assertTrue(hasattr(module.DanhuangPet, "pet_window_view_model"))

    def test_initial_roam_schedule_respects_daily_interval(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                module = load_runtime_module(path)
                delay = module.next_roam_timestamp({"roam_interval": 120.0}, now=1000.0) - 1000.0
                source = path.read_text(encoding="utf-8")

                self.assertGreaterEqual(delay, 84.0)
                self.assertLessEqual(delay, 162.0)
                self.assertNotIn("random.uniform(2.0, 4.0)", source)

    def test_snooze_delay_label_uses_human_terms(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                module = load_runtime_module(path)

                self.assertEqual(module.snooze_delay_label(15), "15 分钟后")
                self.assertEqual(module.snooze_delay_label(60), "1 小时后")
                self.assertEqual(module.snooze_delay_label(24 * 60), "明天")
                self.assertEqual(module.snooze_delay_label(2 * 24 * 60), "2 天后")

    def test_todo_delete_uses_panel_confirm(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def show_panel_confirm(", source)
                self.assertIn("def confirm_delete_todo(", source)
                self.assertIn('self.show_panel_confirm(', source)
                self.assertNotIn('messagebox.askyesno("删除待办"', source)

    def test_companion_reset_uses_panel_confirm(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def reset_companion_state(", source)
                self.assertIn('self.show_panel_confirm(\n            "重置陪伴数据"', source)
                self.assertIn("不会删除聊天、待办或提醒", source)
                self.assertNotIn('messagebox.askyesno("重置陪伴数据"', source)

    def test_ai_memory_clear_uses_panel_confirm(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def clear_ai_memory(", source)
                self.assertIn('self.show_panel_confirm(\n            "清空陪聊记忆"', source)
                self.assertIn("不会删除 API Key、提醒、待办或陪伴等级", source)
                self.assertNotIn('messagebox.askyesno(f"清空{self.active_pet_name()}记忆"', source)

    def test_pet_asset_delete_uses_panel_confirm(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def clear_pet_identity_image(", source)
                self.assertIn("def remove_reference_image_from_pet(", source)
                self.assertIn('self.show_panel_confirm(\n            "删除主像素图"', source)
                self.assertIn("不会删除现实照片、参考图、动作精灵图或聊天记忆", source)
                self.assertNotIn('messagebox.askyesno("删除主像素图"', source)
                self.assertIn('self.show_panel_confirm(\n            "删除参考图"', source)
                self.assertIn("不会删除本机外部源文件", source)
                self.assertNotIn('messagebox.askyesno("删除参考图"', source)

    def test_extension_action_clear_uses_panel_confirm(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def remove_extension_action_asset(", source)
                self.assertIn('self.show_panel_confirm(\n            "清空动作精灵图"', source)
                self.assertIn("这个扩展动作会从动作页、右键动作栏和当前形象的可播放动作里移除", source)
                self.assertIn("不会删除基础动作、主像素图、现实照片、参考图或聊天记忆", source)
                self.assertNotIn('messagebox.askyesno("清空动作精灵图"', source)

    def test_story_page_feedback_uses_panel_components(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn('def show_panel_toast(self, title, message, tone="success", duration=4200, parent=None):', source)
                self.assertIn("def delete_story(pet_id, entry_id):", source)
                self.assertIn('self.show_panel_confirm(\n                    "删除故事"', source)
                self.assertIn("只移除当前宠物的一条故事记录", source)
                self.assertIn("不会删除图片文件、聊天记忆、提醒、陪伴等级或其他宠物故事", source)
                self.assertIn('self.show_panel_toast("故事已保存"', source)
                self.assertIn('self.show_panel_toast("已本地整理"', source)
                self.assertNotIn('messagebox.askyesno("删除故事"', source)
                self.assertNotIn('messagebox.showwarning("内容为空"', source)
                self.assertNotIn('messagebox.showinfo("需要先配置陪聊服务"', source)

    def test_safety_backup_feedback_uses_panel_toast(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def export_configuration(", source)
                self.assertIn("def restore_configuration(", source)
                self.assertIn("def backup_spritesheet(", source)
                self.assertIn('self.show_panel_toast("配置已导出"', source)
                self.assertIn('self.show_panel_toast("恢复失败"', source)
                self.assertIn('self.show_panel_toast("配置已恢复"', source)
                self.assertIn('self.show_panel_toast("备份失败"', source)
                self.assertIn('self.show_panel_toast("精灵图已备份"', source)
                self.assertNotIn('messagebox.showerror("恢复失败"', source)
                self.assertNotIn('messagebox.showerror("备份失败"', source)

    def test_installer_export_feedback_uses_panel_status_and_toast(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def open_installer_export_dialog(self, target_platform=\"windows\"):", source)
                self.assertIn("def set_export_status(title, body, tone=\"neutral\"):", source)
                self.assertIn('self.show_panel_toast("导出完成"', source)
                self.assertIn('self.show_panel_toast("导出失败"', source)
                self.assertIn('self.show_panel_toast("缺少 GitHub 仓库"', source)
                self.assertIn('self.show_panel_toast("缺少 GitHub Token"', source)
                self.assertIn('self.show_panel_toast("macOS 可运行包完成"', source)
                self.assertIn('self.show_panel_toast("macOS 构建失败"', source)
                self.assertNotIn('messagebox.showinfo("导出完成"', source)
                self.assertNotIn('messagebox.showerror("导出失败"', source)
                self.assertNotIn('messagebox.showwarning("缺少 GitHub 仓库"', source)
                self.assertNotIn('messagebox.showwarning("缺少 GitHub Token"', source)
                self.assertNotIn('messagebox.showinfo("macOS 可运行包完成"', source)
                self.assertNotIn('messagebox.showerror("macOS 构建失败"', source)

    def test_pet_motion_edge_lock_and_drag_reset_are_wired(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def lock_edge_roam_position(self, x, y, edge, area):", source)
                self.assertIn('self.roam_target.get("edge")', source)
                self.assertIn("nx, ny = self.lock_edge_roam_position(nx, ny, edge, area)", source)
                self.assertIn("def reset_drag_direction(self):", source)
                self.assertIn("self.reset_drag_direction()", source)

    def test_reminder_popup_grid_shortcuts_and_focus_are_wired(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def open_reminder_popup(self, todo):", source)
                self.assertIn('chip_row.grid_columnconfigure(column, weight=1, uniform="reminder_popup_chip")', source)
                self.assertIn('primary_row.grid_columnconfigure(column, weight=1, uniform="reminder_popup_primary")', source)
                self.assertIn('snooze_grid.grid_columnconfigure(column, weight=1, uniform="reminder_popup_snooze")', source)
                self.assertIn('popup.bind("<Control-Return>", complete_from_popup)', source)
                self.assertIn('popup.bind("<Key-1>", snooze_from_popup(15))', source)
                self.assertIn("def close_from_popup(_event=None):", source)
                self.assertIn('popup.bind("<Escape>", close_from_popup)', source)
                self.assertIn("popup.after(80, lambda: (popup.lift(), popup.focus_force(), complete_button.focus_set()))", source)
                self.assertIn("if self.reminder_popup is popup:", source)

    def test_chat_window_focus_and_background_feedback_are_wired(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def open_chat_panel(self):", source)
                self.assertIn("self.chat_panel.deiconify()", source)
                self.assertIn("self.chat_panel.after(80, entry.focus_set)", source)
                self.assertIn("def open_chat_background_dialog(self):", source)
                self.assertIn("def close_background_dialog(_event=None):", source)
                self.assertIn('self.show_panel_toast("背景设置失败"', source)
                self.assertIn('window.bind("<Escape>", close_background_dialog)', source)
                self.assertIn("window.after(80, lambda: (window.lift(), window.focus_force()))", source)
                self.assertNotIn('messagebox.showerror("背景失败"', source)

    def test_pet_identity_actions_use_button_grids(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("visual_actions = tk.Frame(visual_info", source)
                self.assertIn("panel_button_grid(\n                visual_actions,", source)
                self.assertIn('("更换主像素图", lambda pet_id=current_pet.get("id")', source)
                self.assertIn('("删除主像素图", lambda pet_id=current_pet.get("id")', source)
                self.assertIn("columns=3,\n                width=132,\n                height=28,", source)
                self.assertIn("refs_actions = tk.Frame(refs", source)
                self.assertIn("panel_button_grid(\n                refs_actions,", source)
                self.assertIn('("添加现实照片", lambda pet_id=current_pet.get("id")', source)
                self.assertIn('("新增宠物", lambda: self.import_basic_pet_assets', source)
                self.assertIn("columns=2,\n                width=132,\n                height=28,", source)
                self.assertNotIn('panel_button(visual_actions, "更换主像素图"', source)
                self.assertNotIn('panel_button(refs_actions, "添加现实照片"', source)

    def test_reference_image_dialog_feedback_uses_panel_toast(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def add_reference_paths_to_pet(self, pet_id, paths, on_done=None, feedback_parent=None):", source)
                self.assertIn('self.show_panel_toast("添加失败", str(exc)[:160], "error", parent=feedback_parent)', source)
                self.assertIn("def add_reference_images_to_pet(self, pet_id=None, on_done=None):", source)
                self.assertIn("def close_reference_window(_event=None):", source)
                self.assertIn('self.show_panel_toast("没有图片", "请先选择或拖入图片。", "warning", parent=window)', source)
                self.assertIn("self.add_reference_paths_to_pet(pet_id, staged, on_done, feedback_parent=window)", source)
                self.assertIn('window.bind("<Escape>", close_reference_window)', source)
                self.assertIn("window.after(80, lambda: (window.lift(), window.focus_force()))", source)
                self.assertNotIn('messagebox.showwarning("没有图片"', source)
                self.assertNotIn('messagebox.showerror("添加失败"', source)

    def test_pet_identity_image_feedback_uses_panel_toast(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn("def update_pet_identity_image(self, pet_id, source_path, on_done=None, feedback_parent=None):", source)
                self.assertIn('self.show_panel_toast("主像素图失败", "图片不存在。", "error", parent=feedback_parent)', source)
                self.assertIn('self.show_panel_toast("主像素图失败", f"无法读取图片：{exc}", "error", parent=feedback_parent)', source)
                self.assertIn("def choose_pet_identity_image(self, pet_id=None, on_done=None, feedback_parent=None):", source)
                self.assertIn("self.update_pet_identity_image(pet_id, path, on_done, feedback_parent=feedback_parent or self.panel)", source)
                self.assertNotIn('messagebox.showerror("主像素图失败"', source)

    def test_new_pet_import_feedback_uses_panel_toast(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn('def create_pet_from_assets(self, display_name, species="", category="", notes="", identity_path="", atlas_path="", reference_paths=None, activate=False, action_paths=None, category_detail="", feedback_parent=None):', source)
                self.assertIn('self.show_panel_toast("导入失败", "请先填写宠物名字。", "warning", parent=feedback_parent)', source)
                self.assertIn('self.show_panel_toast("导入失败", "至少选择一张主像素图或参考照片。", "warning", parent=feedback_parent)', source)
                self.assertIn('self.show_panel_toast("无法上传", "只支持拖入 png、webp、jpg、jpeg 图片。", "warning", parent=window)', source)
                self.assertIn('self.show_panel_toast("上传失败", "拖动上传时发生异常，已记录到错误日志。", "error", parent=window)', source)
                self.assertIn("feedback_parent=window", source)
                self.assertNotIn('messagebox.showerror("导入失败", "请先填写宠物名字。"', source)
                self.assertNotIn('messagebox.showerror("导入失败", "至少选择一张主像素图或参考照片。"', source)
                self.assertNotIn('messagebox.showwarning("无法上传"', source)
                self.assertNotIn('messagebox.showerror("上传失败"', source)

    def test_clipboard_copy_feedback_uses_panel_toast(self) -> None:
        for path in RUNTIME_FILES:
            with self.subTest(path=str(path.relative_to(PROJECT_ROOT))):
                source = path.read_text(encoding="utf-8")

                self.assertIn('def copy_text_to_clipboard(self, text, label="内容", parent=None):', source)
                self.assertIn('self.show_panel_toast("没有可复制内容", f"{label}为空。", "warning", parent=parent)', source)
                self.assertIn('self.show_panel_toast("已复制", f"{label}已经放进剪贴板。", "success", parent=parent)', source)
                self.assertIn('self.show_panel_toast("复制失败", str(exc)[:160], "error", parent=parent)', source)
                self.assertNotIn('messagebox.showwarning("没有可复制内容"', source)
                self.assertNotIn('messagebox.showerror("复制失败"', source)


if __name__ == "__main__":
    unittest.main()
