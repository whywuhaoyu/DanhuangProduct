"""Pure speech-bubble models for the Tk prototype split."""

from __future__ import annotations

from typing import Any, Mapping

from core.pet_model import clamp
from core.settings_store import BUBBLE_FILL, BUBBLE_OUTLINE, BUBBLE_STYLES, BUBBLE_TEXT, is_hex_color

DEFAULT_BUBBLE_TEXT = "我在。"
DEFAULT_SCREEN_RECT = {"left": 0, "top": 0, "right": 1920, "bottom": 1080}


def normalize_bubble_style(value: Any) -> str:
    style = str(value or "")
    return style if style in BUBBLE_STYLES else "soft"


def normalize_bubble_colors(settings: Mapping[str, Any] | None) -> dict[str, str]:
    source = settings or {}
    fill = source.get("bubble_fill")
    outline = source.get("bubble_outline")
    text = source.get("bubble_text")
    return {
        "fill": str(fill) if is_hex_color(fill) else BUBBLE_FILL,
        "outline": str(outline) if is_hex_color(outline) else BUBBLE_OUTLINE,
        "text": str(text) if is_hex_color(text) else BUBBLE_TEXT,
    }


def bubble_shadow_color(fill: str) -> str:
    value = str(fill or "").lstrip("#")
    try:
        red = int(value[0:2], 16)
        green = int(value[2:4], 16)
        blue = int(value[4:6], 16)
    except (TypeError, ValueError):
        return "#ffe29b"
    return f"#{int(red * 0.88):02x}{int(green * 0.84):02x}{int(blue * 0.74):02x}"


def estimate_bubble_size(text: str, style: str = "soft") -> dict[str, int]:
    normalized_style = normalize_bubble_style(style)
    content = str(text or DEFAULT_BUBBLE_TEXT)
    max_chars = 18 if normalized_style != "caption" else 22
    raw_lines = content.splitlines() or [content]
    lines = sum(max(1, (len(line) + max_chars - 1) // max_chars) for line in raw_lines)
    longest = min(max_chars, max((len(line) for line in raw_lines), default=len(content)))
    width = max(132, min(270, longest * 11 + 44))
    height = max(48, min(150, lines * 22 + 34))
    if normalized_style == "caption":
        width = max(140, min(284, longest * 10 + 34))
        height = max(38, min(120, lines * 20 + 22))
    return {
        "body_width": int(width),
        "body_height": int(height),
        "canvas_width": int(width + 20),
        "canvas_height": int(height + 24),
        "tail_y": int(height - 8),
    }


def clamp_rect_position(
    x: int | float,
    y: int | float,
    width: int | float,
    height: int | float,
    screen_rect: Mapping[str, Any] | None = None,
) -> tuple[int, int]:
    screen = screen_rect or DEFAULT_SCREEN_RECT
    left = int(screen.get("left", 0))
    top = int(screen.get("top", 0))
    right = int(screen.get("right", 1920))
    bottom = int(screen.get("bottom", 1080))
    max_x = max(left, right - int(width))
    max_y = max(top, bottom - int(height))
    return int(clamp(x, left, max_x)), int(clamp(y, top, max_y))


def compute_bubble_position(
    pet_rect: Mapping[str, Any],
    bubble_size: Mapping[str, Any],
    screen_rect: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    pet_x = int(pet_rect.get("x", 0))
    pet_y = int(pet_rect.get("y", 0))
    pet_w = int(pet_rect.get("width", 0))
    pet_h = int(pet_rect.get("height", 0))
    bubble_w = int(bubble_size.get("canvas_width") or bubble_size.get("width") or 0)
    bubble_h = int(bubble_size.get("canvas_height") or bubble_size.get("height") or 0)
    screen = screen_rect or DEFAULT_SCREEN_RECT
    placement = "above"
    x = pet_x - 18
    y = pet_y - bubble_h - 8
    if y < int(screen.get("top", 0)):
        placement = "below"
        y = pet_y + pet_h + 8
    x, y = clamp_rect_position(x, y, bubble_w, bubble_h, screen)
    return {"x": x, "y": y, "placement": placement, "width": bubble_w, "height": bubble_h}


def bubble_preview_model(
    settings: Mapping[str, Any] | None,
    text: str = DEFAULT_BUBBLE_TEXT,
) -> dict[str, Any]:
    source = settings or {}
    style = normalize_bubble_style(source.get("bubble_style"))
    colors = normalize_bubble_colors(source)
    duration = clamp(source.get("bubble_duration", 5.0), 2.0, 12.0)
    size = estimate_bubble_size(text, style)
    return {
        "version": 1,
        "text": str(text or DEFAULT_BUBBLE_TEXT),
        "style": style,
        "style_label": BUBBLE_STYLES[style],
        "colors": colors,
        "shadow": bubble_shadow_color(colors["fill"]),
        "duration_seconds": duration,
        "size": size,
        "text_width": 236 if style != "caption" else 250,
        "font": {"family": "Microsoft YaHei UI", "size": 10},
    }
