from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

MODULAR_ROOT = Path(__file__).resolve().parents[1]
if str(MODULAR_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULAR_ROOT))

from core.companion_state import (  # noqa: E402
    companion_summary,
    fresh_distribution_companion_state,
    load_companion_state,
)
from core.pet_model import infer_pet_category, load_pet_family, pet_category_action_profile  # noqa: E402
from core.settings_store import distribution_settings_snapshot, load_settings  # noqa: E402


class Phase1CoreTests(unittest.TestCase):
    def test_settings_are_typed_clamped_and_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "desktop-pet-settings.json").write_text(
                json.dumps(
                    {
                        "scale": 9,
                        "opacity": "0.1",
                        "bubble_style": "unknown",
                        "bubble_fill": "red",
                        "quick_menu_actions": ["standing", "waving", "standing", "custom:spin", "bad"],
                        "position_x": -999,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            settings = load_settings(root)

        self.assertEqual(settings["scale"], 1.0)
        self.assertEqual(settings["opacity"], 0.35)
        self.assertEqual(settings["bubble_style"], "soft")
        self.assertEqual(settings["bubble_fill"], "#fffaf0")
        self.assertEqual(settings["quick_menu_actions"], ["standing", "custom:spin"])
        self.assertEqual(settings["position_x"], -200)

    def test_distribution_snapshot_drops_local_runtime_state(self) -> None:
        snapshot = distribution_settings_snapshot(
            {
                "current_pet_id": "black_white_dog",
                "position_x": 500,
                "panel_pinned": True,
                "encrypted_github_token": "local-placeholder",
                "scale": 0.4,
            }
        )

        self.assertEqual(snapshot["current_pet_id"], "danhuang")
        self.assertEqual(snapshot["position_x"], -1)
        self.assertFalse(snapshot["panel_pinned"])
        self.assertEqual(snapshot["encrypted_github_token"], "")
        self.assertEqual(snapshot["scale"], 0.4)

    def test_pet_family_is_deduped_and_danhuang_is_restored(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "pet-family.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "current_pet_id": "missing",
                        "pets": [
                            {
                                "id": "custom_pet",
                                "display_name": "自定义",
                                "status": "ready",
                                "action_pack_level": "basic",
                                "supported_actions": ["idle", "running-right", "standing"],
                                "extension_assets": [
                                    {"id": "custom:spin", "label": "转圈", "strip": "spin.webp", "frames": 12}
                                ],
                            },
                            {"id": "custom_pet", "display_name": "重复"},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            family = load_pet_family(root)

        ids = [pet["id"] for pet in family["pets"]]
        self.assertEqual(ids.count("custom_pet"), 1)
        self.assertIn("danhuang", ids)
        self.assertEqual(family["current_pet_id"], "danhuang")
        custom = next(pet for pet in family["pets"] if pet["id"] == "custom_pet")
        self.assertIn("custom:spin", custom["supported_actions"])
        self.assertNotIn("standing", custom["supported_actions"])

    def test_pet_family_bad_version_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "pet-family.json").write_text(
                json.dumps({"version": "bad", "pets": []}, ensure_ascii=False),
                encoding="utf-8",
            )

            family = load_pet_family(root)

        self.assertEqual(family["version"], 1)
        self.assertEqual(family["pets"][0]["id"], "danhuang")

    def test_pet_category_action_profiles_avoid_cat_dog_motion_for_non_animals(self) -> None:
        aquatic = pet_category_action_profile(infer_pet_category({"species": "fish", "notes": "金鱼"}))
        human = pet_category_action_profile(infer_pet_category({"species": "human", "notes": "Q版产品经理"}))
        robot = pet_category_action_profile(infer_pet_category({"species": "robot", "notes": "盒子机器人"}))

        self.assertIn("不要画腿脚", aquatic["identity_focus"])
        self.assertIn("两足", human["motion_rules"])
        self.assertIn("机械臂", robot["identity_focus"])
        self.assertIn("不要画成四足动物", robot["avoid_rules"])

    def test_companion_state_is_loaded_from_pet_scope_and_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            state_dir = root / "pet-state" / "danhuang"
            state_dir.mkdir(parents=True)
            (state_dir / "companion-state.json").write_text(
                json.dumps({"xp": 85, "level": 99, "total_seconds": "7200", "daily_bonus_dates": "bad"}),
                encoding="utf-8",
            )

            state = load_companion_state(root, "danhuang")

        self.assertEqual(state["level"], 3)
        self.assertEqual(state["total_seconds"], 7200)
        self.assertEqual(state["daily_bonus_dates"], [])
        self.assertEqual(companion_summary(state)["hours"], 2.0)

    def test_fresh_distribution_companion_state_uses_today_without_history(self) -> None:
        state = fresh_distribution_companion_state(date(2026, 6, 14))

        self.assertEqual(state["created_date"], "2026-06-14")
        self.assertEqual(state["last_active_date"], "2026-06-14")
        self.assertEqual(state["xp"], 0)
        self.assertEqual(state["daily_bonus_dates"], [])


if __name__ == "__main__":
    unittest.main()
