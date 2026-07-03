"""Settings loading and normalization for the Tk prototype."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping

from .pet_model import (
    BASE_ACTIONS,
    EXTENDED_ACTIONS,
    QUICK_MENU_BASE_ACTIONS,
    clamp,
    is_custom_action_id,
)

SETTINGS_FILE = "desktop-pet-settings.json"
BUBBLE_FILL = "#fffaf0"
BUBBLE_OUTLINE = "#d8a760"
BUBBLE_TEXT = "#3b3024"

BUBBLE_STYLES = {
    "soft": "柔和气泡",
    "rounded": "圆角气泡",
    "cloud": "小云朵",
    "thought": "思考泡泡",
    "note": "便签",
    "caption": "极简字幕",
}

DEFAULT_SETTINGS: dict[str, Any] = {
    "scale": 0.50,
    "animation_speed": 0.70,
    "drag_sensitivity": 0.70,
    "inertia": 0.55,
    "idle_action_interval": 9.0,
    "talk_enabled": True,
    "talk_interval": 45.0,
    "bubble_duration": 5.0,
    "bubble_style": "soft",
    "bubble_fill": BUBBLE_FILL,
    "bubble_outline": BUBBLE_OUTLINE,
    "bubble_text": BUBBLE_TEXT,
    "position_x": -1,
    "position_y": -1,
    "keep_on_screen": True,
    "always_on_top": True,
    "opacity": 1.0,
    "talk_after_interaction_delay": 18.0,
    "roam_enabled": True,
    "roam_interval": 28.0,
    "roam_speed": 115.0,
    "roam_distance": 0.55,
    "roam_allow_center": True,
    "multi_monitor_roam": True,
    "roam_current_monitor_only": False,
    "primary_monitor_edge_only": True,
    "secondary_monitor_full_roam": True,
    "lock_size_across_monitors": True,
    "panel_advanced": False,
    "panel_pinned": False,
    "ai_enabled": True,
    "ai_fallback_enabled": True,
    "ai_model": "",
    "ai_base_url": "",
    "ai_timeout": 90.0,
    "current_pet_id": "danhuang",
    "quick_menu_actions": [],
    "default_export_dir": "",
    "default_upload_dir": "",
    "default_image_dir": "",
    "github_repo": "",
    "github_branch": "main",
    "github_workflow": "build-macos-app.yml",
    "github_token_env_key": "DANHUANG_GITHUB_TOKEN",
    "encrypted_github_token": "",
}


def settings_path(pet_dir_or_file: str | Path) -> Path:
    path = Path(pet_dir_or_file)
    return path if path.name == SETTINGS_FILE else path / SETTINGS_FILE


def is_hex_color(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value) is not None


def default_settings() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_SETTINGS)


def normalize_quick_menu_setting(actions: Any) -> list[str]:
    valid = set(BASE_ACTIONS + EXTENDED_ACTIONS) - set(QUICK_MENU_BASE_ACTIONS)
    normalized: list[str] = []
    for action in actions if isinstance(actions, list) else []:
        action_id = str(action)
        if (action_id in valid or is_custom_action_id(action_id)) and action_id not in normalized:
            normalized.append(action_id)
    return normalized


def _coerce_setting(default: Any, value: Any) -> Any:
    if isinstance(default, bool):
        return bool(value)
    if isinstance(default, list):
        return list(value) if isinstance(value, list) else copy.deepcopy(default)
    if isinstance(default, str):
        return str(value)
    return float(value)


def normalize_settings(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    settings = default_settings()
    if isinstance(raw, Mapping):
        for key, default in DEFAULT_SETTINGS.items():
            if key not in raw:
                continue
            try:
                settings[key] = _coerce_setting(default, raw[key])
            except (TypeError, ValueError):
                settings[key] = copy.deepcopy(default)

    settings["scale"] = clamp(settings["scale"], 0.25, 1.00)
    settings["animation_speed"] = clamp(settings["animation_speed"], 0.35, 1.50)
    settings["drag_sensitivity"] = clamp(settings["drag_sensitivity"], 0.30, 1.40)
    settings["inertia"] = clamp(settings["inertia"], 0.0, 1.0)
    settings["idle_action_interval"] = clamp(settings["idle_action_interval"], 3.0, 30.0)
    settings["talk_interval"] = clamp(settings["talk_interval"], 15.0, 180.0)
    settings["bubble_duration"] = clamp(settings["bubble_duration"], 2.0, 12.0)
    settings["position_x"] = int(clamp(settings["position_x"], -200, 10000))
    settings["position_y"] = int(clamp(settings["position_y"], -200, 10000))
    settings["opacity"] = clamp(settings["opacity"], 0.35, 1.0)
    settings["talk_after_interaction_delay"] = clamp(settings["talk_after_interaction_delay"], 0.0, 120.0)
    settings["roam_interval"] = clamp(settings["roam_interval"], 8.0, 180.0)
    settings["roam_speed"] = clamp(settings["roam_speed"], 45.0, 260.0)
    settings["roam_distance"] = clamp(settings["roam_distance"], 0.20, 0.95)
    settings["ai_timeout"] = clamp(settings["ai_timeout"], 4.0, 120.0)

    if settings["bubble_style"] not in BUBBLE_STYLES:
        settings["bubble_style"] = DEFAULT_SETTINGS["bubble_style"]
    for key in ("bubble_fill", "bubble_outline", "bubble_text"):
        if not is_hex_color(settings[key]):
            settings[key] = DEFAULT_SETTINGS[key]
    settings["quick_menu_actions"] = normalize_quick_menu_setting(settings.get("quick_menu_actions"))
    return settings


def load_settings(pet_dir_or_file: str | Path) -> dict[str, Any]:
    path = settings_path(pet_dir_or_file)
    if not path.exists():
        return normalize_settings(None)
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        saved = None
    return normalize_settings(saved if isinstance(saved, Mapping) else None)


def save_settings(pet_dir_or_file: str | Path, settings: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_settings(settings)
    path = settings_path(pet_dir_or_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return normalized


def settings_dir_value(settings: Mapping[str, Any], key: str, fallback: str | Path) -> Path:
    value = str(settings.get(key, "") or "").strip()
    path = Path(value) if value else Path(fallback)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError:
        fallback_path = Path(fallback)
        fallback_path.mkdir(parents=True, exist_ok=True)
        return fallback_path


def remember_directory_setting(
    pet_dir_or_file: str | Path,
    settings: Mapping[str, Any],
    key: str,
    path: str | Path | None,
) -> dict[str, Any]:
    if not path:
        return normalize_settings(settings)
    directory = Path(path)
    if directory.suffix:
        directory = directory.parent
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        return normalize_settings(settings)
    updated = dict(settings)
    updated[key] = str(directory)
    return save_settings(pet_dir_or_file, updated)


def distribution_settings_snapshot(current_settings: Mapping[str, Any]) -> dict[str, Any]:
    current = normalize_settings(current_settings)
    settings = default_settings()
    for key in (
        "scale",
        "animation_speed",
        "drag_sensitivity",
        "inertia",
        "talk_enabled",
        "talk_interval",
        "bubble_style",
        "bubble_fill",
        "bubble_outline",
        "bubble_text",
        "roam_enabled",
        "roam_speed",
        "roam_distance",
        "multi_monitor_roam",
        "roam_current_monitor_only",
        "quick_menu_actions",
    ):
        if key in current:
            settings[key] = copy.deepcopy(current[key])

    settings["current_pet_id"] = "danhuang"
    settings["position_x"] = -1
    settings["position_y"] = -1
    settings["panel_pinned"] = False
    settings["panel_advanced"] = False
    settings["encrypted_github_token"] = ""
    return normalize_settings(settings)


def github_token_env_key(settings: Mapping[str, Any]) -> str:
    key = str(settings.get("github_token_env_key", "") or "").strip()
    return key if re.fullmatch(r"[A-Z_][A-Z0-9_]*", key) else "DANHUANG_GITHUB_TOKEN"
