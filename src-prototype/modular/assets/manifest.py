"""Action and asset manifest helpers for the Tk prototype split."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from assets.atlas import (
    action_frame_spec,
    atlas_grid_info,
    available_atlas_actions,
    extension_asset_frame_info,
    validate_atlas_image,
)
from core.pet_model import (
    ACTION_LABELS,
    BASE_ACTIONS,
    BASIC_ATLAS_ACTIONS,
    BASE_INTERNAL_ACTIONS,
    EXTENDED_ACTIONS,
    FULL_SUPPORTED_ACTIONS,
    QUICK_MENU_BASE_ACTIONS,
    ROWS,
    is_custom_action_id,
    normalize_extension_assets,
    pet_asset_path,
)
from core.settings_store import normalize_quick_menu_setting


def extension_asset_for_action(pet: Mapping[str, Any], action_id: str) -> dict[str, Any] | None:
    assets = pet.get("extension_assets") if isinstance(pet.get("extension_assets"), list) else []
    for asset in assets:
        if isinstance(asset, Mapping) and asset.get("id") == action_id:
            return dict(asset)
    return None


def action_label(action_id: str, pet: Mapping[str, Any] | None = None) -> str:
    asset = extension_asset_for_action(pet or {}, action_id)
    if asset and asset.get("label"):
        return str(asset["label"])
    return ACTION_LABELS.get(action_id, action_id)


def pet_supported_actions(pet: Mapping[str, Any]) -> set[str]:
    actions = pet.get("supported_actions") if isinstance(pet.get("supported_actions"), list) else []
    return {str(action) for action in actions}


def action_supported(pet: Mapping[str, Any], action_id: str) -> bool:
    if action_id in {"idle", "stepping"}:
        return True
    if action_id == "running":
        supported = pet_supported_actions(pet)
        return "running-right" in supported and "running-left" in supported
    if action_id == "chase-butterfly-left":
        action_id = "running-left"
    return action_id in pet_supported_actions(pet)


def fallback_action_for_state(pet: Mapping[str, Any], action_id: str) -> str:
    preferred = {
        "standing": "waiting",
        "tongue": "waving",
        "lying": "waiting",
        "stretching": "jumping",
        "sleeping": "waiting",
        "sniffing": "review",
        "rolling": "waving",
        "crying": "failed",
        "chase-butterfly": "running",
        "angry": "failed",
    }.get(action_id, action_id)
    for candidate in (preferred, "waiting", "review", "waving", "failed", "running", "jumping", "idle"):
        if action_supported(pet, candidate):
            return candidate
    return "idle"


def _action_has_frames(action_id: str, atlas_actions: set[str], extension_ids: set[str]) -> bool:
    if action_id == "running":
        return "running-right" in atlas_actions and "running-left" in atlas_actions
    return action_id in atlas_actions or action_id in extension_ids


def quick_menu_available_actions(pet: Mapping[str, Any], frame_actions: set[str]) -> list[str]:
    extension_ids = {
        str(asset.get("id"))
        for asset in pet.get("extension_assets", []) if isinstance(asset, Mapping)
    }
    standard = [
        action
        for action in [*BASE_ACTIONS, *EXTENDED_ACTIONS]
        if action_supported(pet, action) and _action_has_frames(action, frame_actions, extension_ids)
    ]
    custom = [
        action
        for action in extension_ids
        if is_custom_action_id(action) and action_supported(pet, action)
    ]
    return list(dict.fromkeys([*standard, *custom]))


def selected_quick_menu_actions(
    pet: Mapping[str, Any],
    settings: Mapping[str, Any] | None,
    frame_actions: set[str],
) -> dict[str, list[str]]:
    available = quick_menu_available_actions(pet, frame_actions)
    base = [action for action in QUICK_MENU_BASE_ACTIONS if action in available]
    extensions = [action for action in available if action not in set(QUICK_MENU_BASE_ACTIONS)]
    selected_raw = normalize_quick_menu_setting((settings or {}).get("quick_menu_actions"))
    selected_extensions = [action for action in selected_raw if action in extensions]
    return {
        "base": base,
        "available_extensions": extensions,
        "selected_extensions": selected_extensions,
        "selected": [*base, *selected_extensions],
    }


def build_action_entry(
    pet: Mapping[str, Any],
    action_id: str,
    atlas_actions: set[str],
    extension_frame_map: Mapping[str, Mapping[str, Any]],
    selected_quick_actions: set[str],
) -> dict[str, Any]:
    extension = extension_frame_map.get(action_id)
    spec = action_frame_spec(action_id)
    supported = action_supported(pet, action_id)
    has_frames = action_id in atlas_actions or extension is not None or (action_id == "running" and _action_has_frames(action_id, atlas_actions, set(extension_frame_map)))
    if extension is not None:
        source = "extension"
        frames = int(extension.get("frames") or 0)
        durations = extension.get("durations") if isinstance(extension.get("durations"), list) else []
        valid = bool(extension.get("valid"))
    elif spec is not None:
        source = "atlas"
        frames = int(spec["frames"])
        durations = list(spec["durations"])
        valid = _action_has_frames(action_id, atlas_actions, set(extension_frame_map)) if action_id == "running" else action_id in atlas_actions
    else:
        source = "custom"
        frames = 0
        durations = []
        valid = False
    return {
        "id": action_id,
        "label": action_label(action_id, pet),
        "source": source,
        "row": spec.get("row") if spec else None,
        "frames": frames,
        "durations": durations,
        "supported": supported,
        "has_frames": has_frames,
        "playable": supported and has_frames and valid,
        "quick_menu_fixed": action_id in QUICK_MENU_BASE_ACTIONS,
        "quick_menu_selected": action_id in selected_quick_actions,
        "fallback": fallback_action_for_state(pet, action_id) if not supported else "",
    }


def build_pet_action_manifest(
    pet_dir: str | Path,
    pet: Mapping[str, Any],
    settings: Mapping[str, Any] | None = None,
    include_private_paths: bool = False,
) -> dict[str, Any]:
    root = Path(pet_dir)
    sprite_path = pet_asset_path(root, pet.get("spritesheet"))
    atlas_actions = set(available_atlas_actions(sprite_path)) if sprite_path else set()
    extension_assets = normalize_extension_assets(pet.get("extension_assets"))
    extension_infos = [extension_asset_frame_info(root, asset) for asset in extension_assets]
    extension_map = {item["id"]: item for item in extension_infos if item.get("id")}
    quick_menu = selected_quick_menu_actions(pet, settings, atlas_actions | set(extension_map))
    selected_quick = set(quick_menu["selected"])
    configured_actions = pet.get("supported_actions") if isinstance(pet.get("supported_actions"), list) else []
    action_ids = list(dict.fromkeys([*FULL_SUPPORTED_ACTIONS, *configured_actions, *extension_map.keys()]))
    entries = [
        build_action_entry(pet, str(action_id), atlas_actions, extension_map, selected_quick)
        for action_id in action_ids
        if str(action_id) in ROWS or str(action_id) == "running" or is_custom_action_id(str(action_id))
    ]
    atlas = validate_atlas_image(sprite_path, BASIC_ATLAS_ACTIONS) if sprite_path else {"valid": False, "errors": ["spritesheet 未配置。"], "warnings": []}
    atlas_grid = atlas_grid_info(sprite_path) if sprite_path else {}
    if not include_private_paths:
        atlas.pop("path", None)
        atlas_grid.pop("path", None)
    return {
        "pet_id": str(pet.get("id") or ""),
        "display_name": str(pet.get("display_name") or pet.get("id") or ""),
        "species": str(pet.get("species") or ""),
        "status": str(pet.get("status") or ""),
        "action_pack_level": str(pet.get("action_pack_level") or ""),
        "spritesheet": str(pet.get("spritesheet") or ""),
        "spritesheet_path": str(sprite_path) if include_private_paths and sprite_path else "",
        "atlas": atlas,
        "atlas_grid": atlas_grid,
        "extension_assets": extension_infos,
        "actions": entries,
        "quick_menu": quick_menu,
        "summary": {
            "supported_count": len(pet_supported_actions(pet)),
            "playable_count": len([entry for entry in entries if entry["playable"]]),
            "extension_count": len(extension_infos),
            "selected_quick_count": len(quick_menu["selected"]),
        },
    }


def build_family_asset_manifest(
    pet_dir: str | Path,
    family: Mapping[str, Any],
    settings: Mapping[str, Any] | None = None,
    include_private_paths: bool = False,
) -> dict[str, Any]:
    pets = family.get("pets") if isinstance(family.get("pets"), list) else []
    pet_manifests = [
        build_pet_action_manifest(pet_dir, pet, settings=settings, include_private_paths=include_private_paths)
        for pet in pets
        if isinstance(pet, Mapping)
    ]
    return {
        "version": 1,
        "current_pet_id": str(family.get("current_pet_id") or ""),
        "pet_count": len(pet_manifests),
        "pets": pet_manifests,
        "totals": {
            "playable_actions": sum(item["summary"]["playable_count"] for item in pet_manifests),
            "extension_assets": sum(item["summary"]["extension_count"] for item in pet_manifests),
            "ready_pets": len([item for item in pet_manifests if item["status"] == "ready"]),
        },
    }
