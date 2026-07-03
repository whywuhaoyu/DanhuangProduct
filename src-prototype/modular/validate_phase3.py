"""Read-only validation for Phase 3 asset and action manifest modules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from assets.manifest import build_family_asset_manifest
from core.pet_model import load_pet_family
from core.settings_store import load_settings
from ui.tk_bubble import bubble_preview_model
from ui.tk_bubble_render import render_bubble_image
from ui.tk_pet_window import window_behavior_model
from ui.tk_right_menu import build_pet_switcher_model, build_right_menu_model, right_menu_popup_layout, summarize_right_menu


def default_pet_dir() -> Path:
    product_root = Path(__file__).resolve().parents[2]
    runtime = product_root / "data-dev" / "current-runtime" / "danhuang"
    if runtime.exists():
        return runtime
    return Path(__file__).resolve().parents[1] / "legacy-monolith"


def build_report(pet_dir: Path) -> dict[str, object]:
    settings = load_settings(pet_dir)
    family = load_pet_family(pet_dir)
    manifest = build_family_asset_manifest(pet_dir, family, settings=settings)
    pets = manifest.get("pets", []) if isinstance(manifest.get("pets"), list) else []
    current_pet = next(
        (pet for pet in pets if isinstance(pet, dict) and pet.get("pet_id") == manifest.get("current_pet_id")),
        pets[0] if pets else {},
    )
    right_menu = build_right_menu_model(
        current_pet if isinstance(current_pet, dict) else {},
        current_pet_id=str(manifest.get("current_pet_id") or ""),
        pinned=bool(settings.get("always_on_top")),
    )
    pet_switcher = build_pet_switcher_model(
        pets if isinstance(pets, list) else [],
        current_pet_id=str(manifest.get("current_pet_id") or ""),
    )
    bubble = bubble_preview_model(settings)
    bubble_renderer_styles = []
    for style in ("soft", "rounded", "cloud", "thought", "note", "caption"):
        image = render_bubble_image(
            style,
            bubble["size"]["canvas_width"],
            bubble["size"]["canvas_height"],
            bubble["size"]["body_width"],
            bubble["size"]["body_height"],
            bubble["size"]["tail_y"],
            colors=bubble["colors"],
        )
        bubble_renderer_styles.append({"style": style, "mode": image.mode, "size": list(image.size)})
    window = window_behavior_model(settings)
    warnings = []
    for pet in pets:
        atlas = pet.get("atlas", {}) if isinstance(pet, dict) else {}
        if isinstance(atlas, dict):
            for warning in atlas.get("warnings", []):
                warnings.append(f"{pet.get('display_name', pet.get('pet_id'))}: {warning}")
    return {
        "pet_dir": str(pet_dir),
        "current_pet_id": manifest["current_pet_id"],
        "pet_count": manifest["pet_count"],
        "totals": manifest["totals"],
        "pets": [
            {
                "pet_id": pet["pet_id"],
                "display_name": pet["display_name"],
                "status": pet["status"],
                "action_pack_level": pet["action_pack_level"],
                "spritesheet_exists": bool(pet.get("atlas", {}).get("exists")),
                "atlas_valid": bool(pet.get("atlas", {}).get("valid")),
                "playable_actions": pet["summary"]["playable_count"],
                "extension_assets": pet["summary"]["extension_count"],
                "quick_menu": pet["quick_menu"]["selected"],
            }
            for pet in pets
        ],
        "ui": {
            "right_menu": {
                "summary": summarize_right_menu(right_menu),
                "sections": [section["id"] for section in right_menu["sections"]],
                "layout": right_menu["layout"],
                "style_variants": sorted(right_menu.get("style", {}).get("button_variants", {}).keys()),
                "base_actions": right_menu["base_actions"],
                "visible_extension_actions": right_menu["visible_extension_actions"],
                "hidden_extension_count": len(right_menu["hidden_extension_actions"]),
                "can_show_more": right_menu["can_show_more"],
            },
            "pet_switcher": {
                "title": pet_switcher["title"],
                "visible_count": len(pet_switcher["items"]),
                "hidden_count": pet_switcher["hidden_count"],
                "current_pet_id": pet_switcher["items"][0]["pet_id"] if pet_switcher["items"] else "",
                "footer": [item["id"] for item in pet_switcher["footer"]],
                "popup_layout": right_menu_popup_layout(),
            },
            "bubble": {
                "style": bubble["style"],
                "style_label": bubble["style_label"],
                "duration_seconds": bubble["duration_seconds"],
                "colors": bubble["colors"],
                "size": bubble["size"],
                "renderer_styles": bubble_renderer_styles,
            },
            "window": {
                "size": window["size"],
                "attributes": window["attributes"],
                "roam": window["roam"],
            },
        },
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Danhuang modular Phase 3 asset manifest.")
    parser.add_argument("--pet-dir", type=Path, default=default_pet_dir(), help="Prototype/runtime data directory.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = build_report(args.pet_dir)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Phase 3 asset manifest validation passed.")
        print(f"pet_dir: {report['pet_dir']}")
        print(f"current_pet_id: {report['current_pet_id']}")
        print(f"pets: {report['pet_count']}, totals {report['totals']}")
        for pet in report["pets"]:
            print(
                f"- {pet['display_name']} ({pet['pet_id']}): "
                f"{pet['playable_actions']} playable, {pet['extension_assets']} extensions, "
                f"quick {pet['quick_menu']}"
            )
        ui = report["ui"]
        print(f"right_menu: {ui['right_menu']['summary']}")
        print(f"pet_switcher: {ui['pet_switcher']['visible_count']} visible, {ui['pet_switcher']['hidden_count']} hidden")
        print(f"bubble: {ui['bubble']['style_label']}, {ui['bubble']['duration_seconds']}s")
        print(f"bubble_renderer: {len(ui['bubble']['renderer_styles'])} styles")
        print(f"window: {ui['window']['size']}, roam {ui['window']['roam']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
