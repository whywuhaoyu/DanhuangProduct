from __future__ import annotations

import sys
import unittest
from pathlib import Path

MODULAR_ROOT = Path(__file__).resolve().parents[1]
if str(MODULAR_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULAR_ROOT))

from ui.tk_bubble import bubble_preview_model, compute_bubble_position, normalize_bubble_colors  # noqa: E402
from ui.tk_bubble_render import bubble_fold_color, render_bubble_image  # noqa: E402
from ui.tk_pet_window import clamp_pet_position, lock_edge_roam_position, monitor_allows_center_roam, window_behavior_model  # noqa: E402
from ui.tk_right_menu import (  # noqa: E402
    build_pet_switcher_model,
    build_right_menu_model,
    compute_menu_position,
    compute_menu_viewport_size,
    compute_popup_position,
    right_menu_action_buttons,
    right_menu_popup_layout,
    right_menu_style_tokens,
)


class Phase3UiTests(unittest.TestCase):
    def _pet_manifest(self) -> dict[str, object]:
        action_ids = [
            "waving",
            "running",
            "jumping",
            "waiting",
            "standing",
            "tongue",
            "lying",
            "sleeping",
            "custom:petting",
        ]
        return {
            "pet_id": "danhuang",
            "display_name": "蛋黄",
            "species": "dog",
            "status": "ready",
            "action_pack_level": "full",
            "summary": {"playable_count": len(action_ids), "extension_count": 5},
            "quick_menu": {
                "base": ["waving", "running", "jumping", "waiting"],
                "selected_extensions": ["standing", "tongue", "lying", "sleeping", "custom:petting"],
                "selected": action_ids,
            },
            "extension_assets": [{"id": "custom:petting", "label": "摸摸头"}],
            "actions": [
                {
                    "id": action_id,
                    "label": "跑一小段" if action_id == "running" else "",
                    "source": "extension" if action_id.startswith("custom:") else "atlas",
                    "frames": 4,
                    "playable": True,
                }
                for action_id in action_ids
            ],
        }

    def test_right_menu_model_keeps_sections_and_more_actions(self) -> None:
        model = build_right_menu_model(self._pet_manifest(), current_pet_id="danhuang")

        self.assertTrue(model["header"]["current"])
        self.assertEqual([section["id"] for section in model["sections"]], ["common", "window", "activity_modes", "base_actions", "extension_actions"])
        self.assertEqual(model["visible_extension_actions"], ["standing", "tongue", "lying"])
        self.assertEqual(model["hidden_extension_actions"], ["sleeping", "custom:petting"])
        self.assertTrue(model["can_show_more"])
        buttons = right_menu_action_buttons(model)
        self.assertEqual([button["action_id"] for button in buttons[:4]], ["waving", "running", "jumping", "waiting"])
        self.assertEqual(next(button for button in buttons if button["action_id"] == "running")["loops"], 1)

    def test_right_menu_model_exposes_renderable_commands(self) -> None:
        model = build_right_menu_model(self._pet_manifest(), current_pet_id="danhuang")
        sections = {section["id"]: section for section in model["sections"]}

        self.assertEqual([item["command"] for item in sections["common"]["items"]], [
            "open_chat",
            "open_control_panel",
            "open_control_panel",
            "open_control_panel",
            "quiet_mode",
            "open_pet_switcher",
            "say_random",
        ])
        self.assertEqual(sections["common"]["items"][2]["page"], "提醒")
        self.assertEqual(sections["common"]["items"][3]["page"], "AI")
        self.assertEqual(sections["common"]["items"][3]["label"], "陪聊设置")
        self.assertEqual(sections["common"]["items"][4]["label"], "安静一下")
        self.assertEqual([item["command"] for item in sections["activity_modes"]["items"]], ["set_activity_mode", "set_activity_mode", "set_activity_mode"])
        self.assertEqual([item["mode"] for item in sections["activity_modes"]["items"]], ["quiet", "daily", "active"])
        self.assertEqual(sections["activity_modes"]["items"][1]["variant"], "selected")
        self.assertEqual(sections["extension_actions"]["footer"][0]["command"], "open_more_actions")
        self.assertEqual(sections["extension_actions"]["footer"][0]["hidden_count"], 2)
        self.assertEqual(sections["extension_actions"]["footer"][1]["page"], "动作")
        self.assertEqual([item["command"] for item in sections["window"]["items"]], ["toggle_activity_pause", "hide_bubble", "close"])
        self.assertEqual(sections["window"]["items"][0]["label"], "暂停活动")
        self.assertEqual(model["layout"]["auto_close_ms"], 12000)
        self.assertEqual(model["layout"]["columns"], 3)
        self.assertEqual(model["layout"]["min_width"], 540)
        self.assertEqual(model["layout"]["min_scroll_body_height"], 180)
        self.assertIn("primary", model["style"]["button_variants"])
        self.assertEqual(model["style"]["button_variants"]["primary"]["fg"], "#ffffff")

    def test_right_menu_model_hides_switcher_for_single_pet_package(self) -> None:
        model = build_right_menu_model(
            self._pet_manifest(),
            current_pet_id="danhuang",
            can_switch_pet=False,
        )
        sections = {section["id"]: section for section in model["sections"]}

        self.assertFalse(model["header"]["can_switch_pet"])
        self.assertNotIn("open_pet_switcher", [item["command"] for item in sections["common"]["items"]])
        self.assertIn("say_random", [item["command"] for item in sections["common"]["items"]])

    def test_right_menu_model_marks_activity_mode(self) -> None:
        model = build_right_menu_model(self._pet_manifest(), current_pet_id="danhuang", activity_mode="quiet")
        sections = {section["id"]: section for section in model["sections"]}

        self.assertEqual(model["header"]["activity_mode"], "quiet")
        self.assertEqual(model["header"]["activity_mode_label"], "安静")
        self.assertEqual(sections["activity_modes"]["items"][0]["variant"], "selected")
        self.assertEqual(sections["activity_modes"]["items"][1]["variant"], "soft")

    def test_right_menu_model_marks_paused_activity(self) -> None:
        model = build_right_menu_model(self._pet_manifest(), current_pet_id="danhuang", paused=True)
        sections = {section["id"]: section for section in model["sections"]}

        self.assertTrue(model["header"]["paused"])
        self.assertEqual(sections["window"]["items"][0]["command"], "toggle_activity_pause")
        self.assertEqual(sections["window"]["items"][0]["label"], "恢复日常")

    def test_right_menu_style_tokens_are_isolated_copies(self) -> None:
        first = right_menu_style_tokens()
        first["button_variants"]["primary"]["bg"] = "#000000"
        second = right_menu_style_tokens()

        self.assertEqual(second["button_variants"]["primary"]["bg"], "#bf6f2a")

    def test_pet_switcher_model_sorts_current_and_limits_visible_items(self) -> None:
        pets = [
            {"id": f"pet-{index}", "display_name": f"宠物{index}", "status": "ready", "action_pack_level": "basic"}
            for index in range(10)
        ]
        model = build_pet_switcher_model(pets, current_pet_id="pet-7")

        self.assertEqual(model["title"], "选择形象")
        self.assertEqual(model["items"][0]["pet_id"], "pet-7")
        self.assertTrue(model["items"][0]["current"])
        self.assertEqual(model["items"][0]["variant"], "selected")
        self.assertEqual(len(model["items"]), 8)
        self.assertEqual(model["hidden_count"], 2)
        self.assertEqual(model["footer"][0]["command"], "open_control_panel")
        self.assertEqual(model["footer"][0]["page"], "形象")

    def test_pet_switcher_model_accepts_manifest_pet_id(self) -> None:
        model = build_pet_switcher_model(
            [
                {"pet_id": "danhuang", "display_name": "蛋黄", "status": "ready"},
                {"pet_id": "pangjiu", "display_name": "胖久", "status": "ready"},
            ],
            current_pet_id="pangjiu",
        )

        self.assertEqual(model["items"][0]["pet_id"], "pangjiu")
        self.assertEqual(model["items"][1]["pet_id"], "danhuang")

    def test_popup_position_prefers_right_and_flips_left_when_needed(self) -> None:
        layout = right_menu_popup_layout()
        right = compute_popup_position(
            {"x": 120, "y": 80, "width": 90, "height": 34},
            {"x": 40, "y": 40, "width": 260, "height": 360},
            {"width": 160, "height": 120},
            {"left": 0, "top": 0, "right": 640, "bottom": 480},
        )
        self.assertEqual(right["placement"], "right")
        self.assertEqual(right["x"], 120 + 90 + layout["gap"])
        self.assertEqual(right["y"], 80 - layout["gap"])

        left = compute_popup_position(
            {"x": 560, "y": 20, "width": 70, "height": 34},
            {"x": 360, "y": 40, "width": 260, "height": 360},
            {"width": 220, "height": 180},
            {"left": 0, "top": 0, "right": 640, "bottom": 480},
        )
        self.assertEqual(left["placement"], "left")
        self.assertLess(left["x"], 360)
        self.assertGreaterEqual(left["x"], layout["screen_margin"])
        self.assertGreaterEqual(left["y"], layout["screen_margin"])

    def test_menu_position_avoids_pet_and_uses_layout_margins(self) -> None:
        right = compute_menu_position(
            {"x": 20, "y": 40, "width": 96, "height": 112},
            {"width": 280, "height": 320},
            {"left": 0, "top": 0, "right": 640, "bottom": 480},
            anchor_point={"x": 30, "y": 52},
        )
        self.assertEqual(right["placement"], "right")
        self.assertEqual(right["x"], 20 + 96 + 12)
        self.assertEqual(right["y"], 40)

        left = compute_menu_position(
            {"x": 520, "y": 40, "width": 96, "height": 112},
            {"width": 280, "height": 320},
            {"left": 0, "top": 0, "right": 640, "bottom": 480},
            anchor_point={"x": 600, "y": 52},
        )
        self.assertEqual(left["placement"], "left")
        self.assertLess(left["x"] + 280, 520)
        self.assertGreaterEqual(left["x"], 8)

    def test_menu_viewport_size_clamps_tall_body_for_small_screens(self) -> None:
        compact = compute_menu_viewport_size(
            {"height": 620},
            {"height": 116},
            {"left": 0, "top": 0, "right": 1280, "bottom": 720},
        )

        self.assertTrue(compact["scrollable"])
        self.assertLessEqual(compact["panel_height"], compact["max_panel_height"])
        self.assertLess(compact["viewport_height"], 620)

        roomy = compute_menu_viewport_size(
            {"height": 420},
            {"height": 116},
            {"left": 0, "top": 0, "right": 1920, "bottom": 1080},
        )

        self.assertFalse(roomy["scrollable"])
        self.assertEqual(roomy["viewport_height"], 420)

    def test_bubble_model_normalizes_style_colors_and_position(self) -> None:
        model = bubble_preview_model(
            {"bubble_style": "unknown", "bubble_fill": "red", "bubble_outline": "#123456", "bubble_duration": 99},
            text="主人，我在这里。",
        )

        self.assertEqual(model["style"], "soft")
        self.assertEqual(model["colors"], {"fill": "#fffaf0", "outline": "#123456", "text": "#3b3024"})
        self.assertEqual(model["duration_seconds"], 12.0)
        self.assertEqual(normalize_bubble_colors({"bubble_text": "#abcdef"})["text"], "#abcdef")

        position = compute_bubble_position(
            {"x": 20, "y": 5, "width": 96, "height": 112},
            model["size"],
            {"left": 0, "top": 0, "right": 300, "bottom": 240},
        )
        self.assertEqual(position["placement"], "below")
        self.assertGreaterEqual(position["x"], 0)
        self.assertGreaterEqual(position["y"], 0)

    def test_bubble_renderer_outputs_images_for_all_styles(self) -> None:
        colors = {"fill": "#fffaf0", "outline": "#d8a760"}

        for style in ("soft", "rounded", "cloud", "thought", "note", "caption"):
            with self.subTest(style=style):
                image = render_bubble_image(style, 180, 82, 160, 58, 50, colors=colors)

                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.size, (180, 82))

        self.assertEqual(bubble_fold_color("not-a-color"), "#ffe29b")

    def test_pet_window_model_clamps_geometry_and_roam_flags(self) -> None:
        settings = {
            "scale": 0.5,
            "opacity": 0.2,
            "always_on_top": False,
            "roam_enabled": True,
            "primary_monitor_edge_only": True,
            "secondary_monitor_full_roam": True,
            "multi_monitor_roam": True,
        }
        model = window_behavior_model(settings, {"left": 0, "top": 0, "right": 320, "bottom": 240, "primary": True})

        self.assertEqual(model["size"], {"scale": 0.5, "width": 96, "height": 112})
        self.assertEqual(model["attributes"]["alpha"], 0.35)
        self.assertFalse(model["attributes"]["topmost"])
        self.assertFalse(model["roam"]["center_allowed"])
        self.assertEqual(clamp_pet_position(999, 999, settings, {"left": 0, "top": 0, "right": 320, "bottom": 240}), (224, 128))
        self.assertTrue(
            monitor_allows_center_roam(settings, {"left": 320, "top": 0, "right": 640, "bottom": 240, "primary": False})
        )

    def test_edge_roam_position_locks_fixed_axis(self) -> None:
        area = {"left": -120, "top": 10, "right": 620, "bottom": 420}

        self.assertEqual(lock_edge_roam_position(120, 34, "top", area), (120, 10))
        self.assertEqual(lock_edge_roam_position(612, 160, "right", area), (620, 160))
        self.assertEqual(lock_edge_roam_position(120, 384, "bottom", area), (120, 420))
        self.assertEqual(lock_edge_roam_position(-104, 160, "left", area), (-120, 160))
        self.assertEqual(lock_edge_roam_position(999, -99, None, area), (620, 10))


if __name__ == "__main__":
    unittest.main()
