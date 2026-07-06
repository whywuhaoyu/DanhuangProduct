"""Pure pet-window behavior models for the Tk prototype split."""

from __future__ import annotations

from typing import Any, Mapping

from core.pet_model import CELL_H, CELL_W, clamp

BASE_DPI = 96
DEFAULT_SCREEN_RECT = {"left": 0, "top": 0, "right": 1920, "bottom": 1080, "primary": True}


def pet_window_size(settings: Mapping[str, Any] | None) -> dict[str, int | float]:
    source = settings or {}
    scale = round(clamp(source.get("scale", 0.5), 0.25, 1.0), 3)
    width = int(CELL_W * scale)
    height = int(CELL_H * scale) + 8
    return {"scale": scale, "width": width, "height": height}


def normalize_monitor_rect(monitor: Mapping[str, Any] | None) -> dict[str, int | bool]:
    source = monitor or DEFAULT_SCREEN_RECT
    left = int(source.get("left", 0))
    top = int(source.get("top", 0))
    right = int(source.get("right", DEFAULT_SCREEN_RECT["right"]))
    bottom = int(source.get("bottom", DEFAULT_SCREEN_RECT["bottom"]))
    if right < left:
        left, right = right, left
    if bottom < top:
        top, bottom = bottom, top
    return {
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom,
        "primary": bool(source.get("primary", False)),
    }


def monitor_area(
    monitor: Mapping[str, Any] | None,
    pet_size: Mapping[str, Any],
) -> dict[str, int]:
    rect = normalize_monitor_rect(monitor)
    width = int(pet_size.get("width") or 0)
    height = int(pet_size.get("height") or 0)
    return {
        "left": int(rect["left"]),
        "top": int(rect["top"]),
        "right": max(int(rect["left"]), int(rect["right"]) - width),
        "bottom": max(int(rect["top"]), int(rect["bottom"]) - height),
    }


def clamp_pet_position(
    x: int | float,
    y: int | float,
    settings: Mapping[str, Any] | None,
    monitor: Mapping[str, Any] | None = None,
) -> tuple[int, int]:
    source = settings or {}
    if not bool(source.get("keep_on_screen", True)):
        return int(x), int(y)
    size = pet_window_size(source)
    area = monitor_area(monitor, size)
    return int(clamp(x, area["left"], area["right"])), int(clamp(y, area["top"], area["bottom"]))


def default_pet_position(
    settings: Mapping[str, Any] | None,
    monitor: Mapping[str, Any] | None = None,
    *,
    margin: int = 28,
) -> dict[str, int]:
    size = pet_window_size(settings)
    area = monitor_area(monitor, size)
    x = int(area["right"]) - int(margin)
    y = int(area["bottom"]) - int(margin)
    x, y = clamp_pet_position(x, y, settings, monitor)
    return {"x": x, "y": y}


def lock_edge_roam_position(
    x: int | float,
    y: int | float,
    edge: str | None,
    area: Mapping[str, Any],
) -> tuple[int, int]:
    """Keep an edge-roam step attached to the chosen screen edge."""

    min_x = int(area.get("left", 0))
    min_y = int(area.get("top", 0))
    max_x = int(area.get("right", min_x))
    max_y = int(area.get("bottom", min_y))
    if max_x < min_x:
        min_x, max_x = max_x, min_x
    if max_y < min_y:
        min_y, max_y = max_y, min_y
    locked_x = int(clamp(x, min_x, max_x))
    locked_y = int(clamp(y, min_y, max_y))
    if edge == "top":
        return locked_x, min_y
    if edge == "right":
        return max_x, locked_y
    if edge == "bottom":
        return locked_x, max_y
    if edge == "left":
        return min_x, locked_y
    return locked_x, locked_y


def monitor_allows_center_roam(settings: Mapping[str, Any] | None, monitor: Mapping[str, Any] | None = None) -> bool:
    source = settings or {}
    rect = normalize_monitor_rect(monitor)
    if rect["primary"] and bool(source.get("primary_monitor_edge_only", True)):
        return False
    if (
        bool(source.get("multi_monitor_roam", True))
        and bool(source.get("secondary_monitor_full_roam", True))
        and not bool(rect["primary"])
    ):
        return True
    return bool(source.get("roam_allow_center", True))


def window_behavior_model(
    settings: Mapping[str, Any] | None,
    monitor: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = settings or {}
    size = pet_window_size(source)
    position = default_pet_position(source, monitor)
    return {
        "version": 1,
        "size": size,
        "position": position,
        "attributes": {
            "topmost": bool(source.get("always_on_top", True)),
            "alpha": round(clamp(source.get("opacity", 1.0), 0.35, 1.0), 3),
            "transparent_background": True,
            "lock_size_across_monitors": bool(source.get("lock_size_across_monitors", True)),
        },
        "roam": {
            "enabled": bool(source.get("roam_enabled", True)),
            "interval_seconds": round(clamp(source.get("roam_interval", 28.0), 8.0, 180.0), 3),
            "speed": round(clamp(source.get("roam_speed", 115.0), 45.0, 260.0), 3),
            "distance": round(clamp(source.get("roam_distance", 0.55), 0.20, 0.95), 3),
            "multi_monitor": bool(source.get("multi_monitor_roam", True)),
            "current_monitor_only": bool(source.get("roam_current_monitor_only", False)),
            "center_allowed": monitor_allows_center_roam(source, monitor),
        },
    }
