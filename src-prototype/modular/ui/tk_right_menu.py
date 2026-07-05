"""Pure right-menu view models for the Tk prototype split."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from assets.manifest import action_label

QUICK_MENU_MAX_VISIBLE_EXTRA_ACTIONS = 4

RIGHT_MENU_LAYOUT = {
    "columns": 2,
    "min_width": 280,
    "max_width": 340,
    "button_min_height": 34,
    "panel_gap": 12,
    "screen_margin": 8,
    "pet_overlap_margin": 4,
    "outside_click_delay_ms": 180,
    "auto_close_ms": 12000,
}

PET_SWITCHER_LAYOUT = {
    "max_visible_pets": 8,
    "row_min_height": 38,
    "thumbnail_size": 28,
}

RIGHT_MENU_POPUP_LAYOUT = {
    "gap": 8,
    "screen_margin": 8,
    "close_delay_ms": 260,
    "max_visible_actions": 10,
}

RIGHT_MENU_STYLE = {
    "panel": {
        "shell_bg": "#fff8ec",
        "shell_border": "#d8b98d",
        "header_bg": "#f3d6ae",
        "name_fg": "#3a2a1c",
        "subtitle_fg": "#6d5138",
        "body_bg": "#fff8ec",
        "section_fg": "#8a6642",
        "disabled_fg": "#9a8978",
    },
    "button_variants": {
        "primary": {"bg": "#bf6f2a", "active": "#96511e", "fg": "#ffffff"},
        "soft": {"bg": "#f7e3c4", "active": "#ecd0a4", "fg": "#3a2a1c"},
        "danger": {"bg": "#f3d3c9", "active": "#e8b8aa", "fg": "#4b2723"},
        "neutral": {"bg": "#fffdf7", "active": "#f2e5d1", "fg": "#3a2a1c"},
        "ghost": {"bg": "#fff8ec", "active": "#f3e2c9", "fg": "#6c5239"},
        "selected": {"bg": "#c8732b", "active": "#8f4d22", "fg": "#ffffff"},
    },
    "popup": {
        "shell_bg": "#fffdf7",
        "shell_border": "#d8b98d",
        "title_fg": "#6d5138",
        "hint_fg": "#8a6642",
        "row_bg": "#fff7e9",
        "row_fg": "#3a2a1c",
        "row_selected_bg": "#c8732b",
        "row_selected_fg": "#ffffff",
        "current_fg": "#8f4d22",
        "current_selected_fg": "#fff4d8",
        "footer_button_bg": "#f7e3c4",
        "footer_button_active": "#ecd0a4",
        "footer_button_fg": "#3a2a1c",
    },
}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp_int(value: int | float, lower: int, upper: int) -> int:
    if upper < lower:
        upper = lower
    return int(max(lower, min(upper, value)))


def right_menu_popup_layout() -> dict[str, int]:
    return dict(RIGHT_MENU_POPUP_LAYOUT)


def right_menu_style_tokens() -> dict[str, Any]:
    return deepcopy(RIGHT_MENU_STYLE)


def _action_map(pet_manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    actions = _list(pet_manifest.get("actions"))
    return {
        str(action.get("id")): action
        for action in actions
        if isinstance(action, Mapping) and action.get("id")
    }


def _command(
    command_id: str,
    label: str,
    command: str,
    *,
    page: str = "",
    variant: str = "neutral",
    enabled: bool = True,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": command_id,
        "label": label,
        "command": command,
        "page": page,
        "variant": variant,
        "enabled": bool(enabled),
    }
    if meta:
        data.update(dict(meta))
    return data


def _action_button(
    action_id: str,
    pet_manifest: Mapping[str, Any],
    actions: Mapping[str, Mapping[str, Any]],
    *,
    fixed: bool,
    visible: bool = True,
) -> dict[str, Any]:
    entry = actions.get(action_id, {})
    playable = bool(entry.get("playable", True))
    loops = 2 if action_id in {"rolling", "chase-butterfly"} else 1
    return _command(
        f"action:{action_id}",
        str(entry.get("label") or action_label(action_id, pet_manifest)),
        "play_action",
        variant="neutral",
        enabled=playable,
        meta={
            "action_id": action_id,
            "fixed": fixed,
            "visible": visible,
            "source": str(entry.get("source") or ""),
            "frames": int(entry.get("frames") or 0),
            "loops": loops,
        },
    )


def build_right_menu_model(
    pet_manifest: Mapping[str, Any],
    *,
    current_pet_id: str = "",
    pinned: bool = False,
    max_visible_extensions: int = QUICK_MENU_MAX_VISIBLE_EXTRA_ACTIONS,
) -> dict[str, Any]:
    """Build a serializable model for the desktop right-click menu.

    The result mirrors the current Tk panel grouping while keeping the
    renderer-independent facts testable before the monolith is wired to it.
    """

    actions = _action_map(pet_manifest)
    quick_menu = pet_manifest.get("quick_menu") if isinstance(pet_manifest.get("quick_menu"), Mapping) else {}
    base_actions = [str(action) for action in _list(quick_menu.get("base"))]
    selected_extensions = [str(action) for action in _list(quick_menu.get("selected_extensions"))]
    visible_count = max(0, int(max_visible_extensions))
    visible_extensions = selected_extensions[:visible_count]
    hidden_extensions = selected_extensions[visible_count:]
    pet_id = str(pet_manifest.get("pet_id") or "")
    display_name = str(pet_manifest.get("display_name") or pet_id or "宠物")
    summary = pet_manifest.get("summary") if isinstance(pet_manifest.get("summary"), Mapping) else {}

    common = [
        _command("chat", f"和{display_name}聊", "open_chat", variant="primary"),
        _command("control_panel", "桌宠面板", "open_control_panel", variant="soft"),
        _command("reminders", "待办提醒", "open_control_panel", page="提醒", variant="soft"),
        _command("ai", "AI 配置", "open_control_panel", page="AI", variant="soft"),
        _command("switch_pet", "切换形象", "open_pet_switcher", variant="soft"),
        _command("pet_touch", "摸摸它", "say_random", variant="neutral"),
    ]
    base_buttons = [
        _action_button(action_id, pet_manifest, actions, fixed=True)
        for action_id in base_actions
    ]
    visible_extension_buttons = [
        _action_button(action_id, pet_manifest, actions, fixed=False)
        for action_id in visible_extensions
    ]
    hidden_extension_buttons = [
        _action_button(action_id, pet_manifest, actions, fixed=False, visible=False)
        for action_id in hidden_extensions
    ]
    extension_footer = []
    if hidden_extensions:
        extension_footer.append(
            _command(
                "more_actions",
                f"更多动作 +{len(hidden_extensions)}",
                "open_more_actions",
                variant="soft",
                meta={"hidden_count": len(hidden_extensions)},
            )
        )
    extension_footer.append(_command("manage_actions", "管理动作", "open_control_panel", page="动作", variant="ghost" if hidden_extensions else "soft"))

    if not visible_extension_buttons:
        visible_extension_buttons.append(
            _command("add_extension_action", "添加扩展动作", "open_control_panel", page="动作", variant="soft")
        )

    window = [
        _command("hide_bubble", "隐藏气泡", "hide_bubble", variant="ghost"),
        _command("exit", "退出", "close", variant="danger"),
    ]
    sections = [
        {"id": "common", "title": "常用", "items": common},
        {"id": "base_actions", "title": "基础动作", "items": base_buttons},
        {
            "id": "extension_actions",
            "title": "扩展动作",
            "items": visible_extension_buttons,
            "footer": extension_footer,
        },
        {"id": "window", "title": "窗口", "items": window},
    ]
    return {
        "version": 1,
        "layout": dict(RIGHT_MENU_LAYOUT),
        "style": right_menu_style_tokens(),
        "header": {
            "pet_id": pet_id,
            "display_name": display_name,
            "species": str(pet_manifest.get("species") or ""),
            "status": str(pet_manifest.get("status") or ""),
            "action_pack_level": str(pet_manifest.get("action_pack_level") or ""),
            "current": bool(current_pet_id and pet_id == current_pet_id),
            "pinned": bool(pinned),
            "subtitle": "陪你说句话，或者做个基础动作",
            "playable_count": int(summary.get("playable_count") or 0),
            "extension_count": int(summary.get("extension_count") or 0),
        },
        "sections": sections,
        "base_actions": base_actions,
        "base_action_buttons": base_buttons,
        "visible_extension_actions": visible_extensions,
        "visible_extension_buttons": visible_extension_buttons,
        "hidden_extension_actions": hidden_extensions,
        "hidden_extension_buttons": hidden_extension_buttons,
        "can_show_more": bool(hidden_extensions),
    }


def right_menu_action_buttons(model: Mapping[str, Any]) -> list[dict[str, Any]]:
    buttons: list[dict[str, Any]] = []
    for section in _list(model.get("sections")):
        if not isinstance(section, Mapping):
            continue
        for item in _list(section.get("items")):
            if isinstance(item, Mapping) and str(item.get("command") or "") == "play_action":
                buttons.append(dict(item))
        for item in _list(section.get("footer")):
            if isinstance(item, Mapping) and str(item.get("command") or "") == "play_action":
                buttons.append(dict(item))
    return buttons


def build_pet_switcher_model(
    pets: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    *,
    current_pet_id: str = "",
    max_visible_pets: int = PET_SWITCHER_LAYOUT["max_visible_pets"],
) -> dict[str, Any]:
    """Build the serializable model for the quick-menu pet switcher popup."""

    current_id = str(current_pet_id or "")
    pet_items: list[dict[str, Any]] = []
    for pet in pets:
        if not isinstance(pet, Mapping):
            continue
        pet_id = str(pet.get("id") or pet.get("pet_id") or "")
        if not pet_id:
            continue
        display_name = str(pet.get("display_name") or pet_id)
        current = bool(current_id and pet_id == current_id)
        pet_items.append(
            _command(
                f"switch_pet:{pet_id}",
                display_name,
                "switch_pet",
                variant="selected" if current else "neutral",
                meta={
                    "pet_id": pet_id,
                    "current": current,
                    "species": str(pet.get("species") or pet.get("kind") or ""),
                    "status": str(pet.get("status") or ""),
                    "action_pack_level": str(pet.get("action_pack_level") or ""),
                },
            )
        )
    pet_items.sort(key=lambda item: (not bool(item.get("current")), str(item.get("label") or item.get("pet_id") or "")))
    visible_count = max(0, int(max_visible_pets))
    visible_items = pet_items[:visible_count]
    return {
        "version": 1,
        "title": "选择形象",
        "layout": {**PET_SWITCHER_LAYOUT, "max_visible_pets": visible_count},
        "style": {"popup": deepcopy(RIGHT_MENU_STYLE["popup"])},
        "items": visible_items,
        "hidden_count": max(0, len(pet_items) - len(visible_items)),
        "empty": {
            "title": "暂无可切换形象",
            "description": "到形象页添加或生成新的桌宠形象。",
        },
        "footer": [
            _command("manage_pets", "管理形象", "open_control_panel", page="形象", variant="soft"),
        ],
    }


def compute_menu_position(
    pet_rect: Mapping[str, Any],
    menu_size: Mapping[str, Any],
    screen_rect: Mapping[str, Any],
    *,
    anchor_point: Mapping[str, Any] | None = None,
    gap: int = RIGHT_MENU_LAYOUT["panel_gap"],
    screen_margin: int = RIGHT_MENU_LAYOUT["screen_margin"],
    pet_overlap_margin: int = RIGHT_MENU_LAYOUT["pet_overlap_margin"],
) -> dict[str, Any]:
    """Place the right-menu panel near the pet while avoiding direct overlap."""

    pet_left = _int(pet_rect.get("left", pet_rect.get("x", 0)))
    pet_top = _int(pet_rect.get("top", pet_rect.get("y", 0)))
    pet_width = _int(pet_rect.get("width", 0))
    pet_height = _int(pet_rect.get("height", 0))
    pet_right = _int(pet_rect.get("right", pet_left + pet_width))
    pet_bottom = _int(pet_rect.get("bottom", pet_top + pet_height))
    menu_w = _int(menu_size.get("width", 0))
    menu_h = _int(menu_size.get("height", 0))
    screen_left = _int(screen_rect.get("left", 0))
    screen_top = _int(screen_rect.get("top", 0))
    screen_right = _int(screen_rect.get("right", 1920))
    screen_bottom = _int(screen_rect.get("bottom", 1080))
    anchor = anchor_point or {}
    anchor_x = _int(anchor.get("x", pet_right + int(gap)))
    anchor_y = _int(anchor.get("y", pet_top))
    margin = int(screen_margin)
    overlap_margin = int(pet_overlap_margin)

    candidates = [
        ("right", pet_right + int(gap), pet_top),
        ("left", pet_left - menu_w - int(gap), pet_top),
        ("below", pet_left, pet_bottom + int(gap)),
        ("above", pet_left, pet_top - menu_h - int(gap)),
        ("anchor", anchor_x, anchor_y),
    ]
    max_x = screen_right - menu_w - margin
    max_y = screen_bottom - menu_h - margin
    for placement, candidate_x, candidate_y in candidates:
        x = _clamp_int(candidate_x, screen_left + margin, max_x)
        y = _clamp_int(candidate_y, screen_top + margin, max_y)
        overlaps_pet = not (
            x + menu_w < pet_left - overlap_margin
            or x > pet_right + overlap_margin
            or y + menu_h < pet_top - overlap_margin
            or y > pet_bottom + overlap_margin
        )
        if not overlaps_pet:
            return {
                "x": x,
                "y": y,
                "placement": placement,
                "gap": int(gap),
                "screen_margin": margin,
                "pet_overlap_margin": overlap_margin,
            }

    return {
        "x": _clamp_int(anchor_x + int(gap), screen_left + margin, max_x),
        "y": _clamp_int(anchor_y + int(gap), screen_top + margin, max_y),
        "placement": "fallback",
        "gap": int(gap),
        "screen_margin": margin,
        "pet_overlap_margin": overlap_margin,
    }


def compute_popup_position(
    anchor_rect: Mapping[str, Any],
    panel_rect: Mapping[str, Any],
    popup_size: Mapping[str, Any],
    screen_rect: Mapping[str, Any],
    *,
    gap: int = RIGHT_MENU_POPUP_LAYOUT["gap"],
    screen_margin: int = RIGHT_MENU_POPUP_LAYOUT["screen_margin"],
) -> dict[str, Any]:
    """Position a quick-menu child popup beside its anchor within a monitor."""

    anchor_x = _int(anchor_rect.get("x", anchor_rect.get("left", 0)))
    anchor_y = _int(anchor_rect.get("y", anchor_rect.get("top", 0)))
    anchor_w = _int(anchor_rect.get("width", 0))
    panel_x = _int(panel_rect.get("x", panel_rect.get("left", 0)))
    popup_w = _int(popup_size.get("width", 0))
    popup_h = _int(popup_size.get("height", 0))
    screen_left = _int(screen_rect.get("left", 0))
    screen_top = _int(screen_rect.get("top", 0))
    screen_right = _int(screen_rect.get("right", 1920))
    screen_bottom = _int(screen_rect.get("bottom", 1080))

    placement = "right"
    x = anchor_x + anchor_w + int(gap)
    y = anchor_y - int(gap)
    if x + popup_w > screen_right - int(screen_margin):
        placement = "left"
        x = panel_x - popup_w - int(gap)

    x = _clamp_int(x, screen_left + int(screen_margin), screen_right - popup_w - int(screen_margin))
    y = _clamp_int(y, screen_top + int(screen_margin), screen_bottom - popup_h - int(screen_margin))
    return {"x": x, "y": y, "placement": placement, "gap": int(gap), "screen_margin": int(screen_margin)}


def summarize_right_menu(model: Mapping[str, Any]) -> str:
    header = model.get("header") if isinstance(model.get("header"), Mapping) else {}
    sections = _list(model.get("sections"))
    item_count = 0
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        item_count += len(_list(section.get("items")))
        item_count += len(_list(section.get("footer")))
    return (
        f"{header.get('display_name', '宠物')} right menu: "
        f"{len(sections)} sections, {item_count} commands, "
        f"{len(_list(model.get('hidden_extension_actions')))} hidden extensions"
    )
