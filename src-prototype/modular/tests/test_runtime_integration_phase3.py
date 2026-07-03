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
                    self.assertEqual(module.APP_VERSION, "0.11.44")
                else:
                    self.assertTrue(hasattr(module, "APP_VERSION"))
                self.assertIsNotNone(module.MODULAR_BUILD_PET_ACTION_MANIFEST)
                self.assertIsNotNone(module.MODULAR_BUILD_PET_SWITCHER_MODEL)
                self.assertIsNotNone(module.MODULAR_BUILD_RIGHT_MENU_MODEL)
                self.assertIsNotNone(module.MODULAR_BUBBLE_PREVIEW_MODEL)
                self.assertIsNotNone(module.MODULAR_COMPUTE_BUBBLE_POSITION)
                self.assertIsNotNone(module.MODULAR_COMPUTE_RIGHT_MENU_POSITION)
                self.assertIsNotNone(module.MODULAR_COMPUTE_RIGHT_MENU_POPUP_POSITION)
                self.assertIsNotNone(module.MODULAR_PET_WINDOW_SIZE)
                self.assertIsNotNone(module.MODULAR_RIGHT_MENU_POPUP_LAYOUT)
                self.assertIsNotNone(module.MODULAR_RIGHT_MENU_STYLE_TOKENS)
                self.assertIsNotNone(module.MODULAR_RENDER_BUBBLE_IMAGE)
                self.assertIsNotNone(module.MODULAR_WINDOW_BEHAVIOR_MODEL)
                self.assertTrue(hasattr(module.DanhuangPet, "quick_menu_view_model"))
                self.assertTrue(hasattr(module.DanhuangPet, "pet_switcher_view_model"))
                self.assertTrue(hasattr(module.DanhuangPet, "bubble_view_model"))
                self.assertTrue(hasattr(module.DanhuangPet, "pet_window_view_model"))


if __name__ == "__main__":
    unittest.main()
