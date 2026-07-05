"""Validate Phase 1 modular data/config extraction against a prototype folder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.companion_state import companion_summary, load_companion_state
from core.pet_model import family_summary, load_pet_family, pet_by_id
from core.settings_store import load_settings


def build_report(pet_dir: Path) -> dict[str, object]:
    settings = load_settings(pet_dir)
    family = load_pet_family(pet_dir)
    companion = load_companion_state(pet_dir, str(settings.get("current_pet_id") or "danhuang"))
    current_pet = pet_by_id(family, str(settings.get("current_pet_id") or family.get("current_pet_id") or "danhuang"))
    return {
        "pet_dir": str(pet_dir),
        "settings": {
            "key_count": len(settings),
            "current_pet_id": settings.get("current_pet_id"),
            "scale": settings.get("scale"),
            "bubble_style": settings.get("bubble_style"),
            "quick_menu_actions": settings.get("quick_menu_actions"),
        },
        "family": family_summary(family),
        "current_pet": {
            "id": current_pet.get("id"),
            "display_name": current_pet.get("display_name"),
            "status": current_pet.get("status"),
            "action_pack_level": current_pet.get("action_pack_level"),
            "supported_action_count": len(current_pet.get("supported_actions", [])),
        },
        "companion": companion_summary(companion),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Danhuang modular Phase 1 core loaders.")
    parser.add_argument(
        "--pet-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "legacy-monolith",
        help="Prototype data directory. Defaults to src-prototype/legacy-monolith.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = build_report(args.pet_dir)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Phase 1 modular core validation passed.")
        print(f"pet_dir: {report['pet_dir']}")
        print(f"settings_keys: {report['settings']['key_count']}")
        print(f"pets: {report['family']['pet_count']} total, {report['family']['ready_count']} ready")
        print(
            "current_pet: "
            f"{report['current_pet']['display_name']} "
            f"({report['current_pet']['id']}, {report['current_pet']['action_pack_level']})"
        )
        print(
            "companion: "
            f"Lv{report['companion']['level']} {report['companion']['title']}, "
            f"{report['companion']['xp']} XP"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
