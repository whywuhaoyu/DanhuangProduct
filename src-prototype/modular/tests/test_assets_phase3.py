from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

MODULAR_ROOT = Path(__file__).resolve().parents[1]
if str(MODULAR_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULAR_ROOT))

from assets.atlas import validate_atlas_image, validate_extension_strip_image  # noqa: E402
from assets.manifest import build_family_asset_manifest, build_pet_action_manifest  # noqa: E402
from core.pet_model import CELL_H, CELL_W, load_pet_family  # noqa: E402
from core.settings_store import normalize_settings  # noqa: E402


class Phase3AssetTests(unittest.TestCase):
    def _save_image(self, path: Path, size: tuple[int, int]) -> None:
        Image.new("RGBA", size, (0, 0, 0, 0)).save(path)

    def test_validate_standard_atlas_and_extension_strip(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            atlas = root / "spritesheet.webp"
            strip = root / "extension.webp"
            self._save_image(atlas, (CELL_W * 8, CELL_H * 9))
            self._save_image(strip, (CELL_W * 4, CELL_H))

            atlas_result = validate_atlas_image(atlas, required_actions=["idle", "running-right", "jumping"])
            strip_result = validate_extension_strip_image(strip, "custom:licking-paw")

        self.assertTrue(atlas_result["valid"])
        self.assertIn("idle", atlas_result["available_actions"])
        self.assertTrue(strip_result["valid"])
        self.assertEqual(strip_result["frames"], 4)
        self.assertEqual(strip_result["durations"], [180, 180, 180, 180])

    def test_pet_action_manifest_keeps_quick_menu_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._save_image(root / "spritesheet.webp", (CELL_W * 8, CELL_H * 5))
            self._save_image(root / "extension-custom-petting.webp", (CELL_W * 4, CELL_H))
            pet = {
                "id": "pet-a",
                "display_name": "测试宠物",
                "species": "dog",
                "status": "ready",
                "spritesheet": "spritesheet.webp",
                "action_pack_level": "basic",
                "supported_actions": ["idle", "running-right", "running-left", "waving", "jumping", "custom:petting"],
                "extension_assets": [
                    {
                        "id": "custom:petting",
                        "label": "摸摸头",
                        "strip": "extension-custom-petting.webp",
                        "frames": 4,
                        "durations": [220, 180, 180, 260],
                    }
                ],
            }
            settings = normalize_settings({"quick_menu_actions": ["custom:petting", "invalid", "waving"]})
            manifest = build_pet_action_manifest(root, pet, settings=settings)

        self.assertEqual(manifest["summary"]["extension_count"], 1)
        self.assertIn("custom:petting", manifest["quick_menu"]["selected_extensions"])
        self.assertIn("running", manifest["quick_menu"]["base"])
        running_action = next(item for item in manifest["actions"] if item["id"] == "running")
        self.assertTrue(running_action["playable"])
        self.assertNotIn("invalid", manifest["quick_menu"]["selected"])
        self.assertNotIn("waving", manifest["quick_menu"]["selected_extensions"])
        self.assertEqual(manifest["spritesheet_path"], "")
        self.assertNotIn("path", manifest["atlas"])
        action = next(item for item in manifest["actions"] if item["id"] == "custom:petting")
        self.assertTrue(action["playable"])
        self.assertEqual(action["label"], "摸摸头")

    def test_family_asset_manifest_summarizes_multiple_pets(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self._save_image(root / "spritesheet.webp", (CELL_W * 8, CELL_H * 19))
            family = {
                "version": 1,
                "current_pet_id": "danhuang",
                "pets": [
                    {
                        "id": "danhuang",
                        "display_name": "蛋黄",
                        "species": "dog",
                        "status": "ready",
                        "spritesheet": "spritesheet.webp",
                        "action_pack_level": "full",
                        "supported_actions": [],
                        "extension_assets": [],
                    }
                ],
            }
            (root / "pet-family.json").write_text(json.dumps(family, ensure_ascii=False), encoding="utf-8")
            loaded = load_pet_family(root)
            manifest = build_family_asset_manifest(root, loaded, settings={"quick_menu_actions": []})

        self.assertEqual(manifest["pet_count"], 1)
        self.assertEqual(manifest["current_pet_id"], "danhuang")
        self.assertGreaterEqual(manifest["totals"]["playable_actions"], 10)
        self.assertEqual(manifest["pets"][0]["display_name"], "蛋黄")


if __name__ == "__main__":
    unittest.main()
