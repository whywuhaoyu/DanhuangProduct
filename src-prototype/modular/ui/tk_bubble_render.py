"""Pillow speech-bubble renderer for the Tk prototype split."""

from __future__ import annotations

from typing import Any, Mapping

from PIL import Image, ImageDraw, ImageFilter

from core.settings_store import BUBBLE_FILL, BUBBLE_OUTLINE, is_hex_color
from ui.tk_bubble import bubble_shadow_color, normalize_bubble_style

DEFAULT_BACKGROUND = "#f7f7f2"
DEFAULT_FOLD = "#ffe29b"


def normalize_render_colors(colors: Mapping[str, Any] | None = None) -> dict[str, str]:
    source = colors or {}
    fill = source.get("fill", source.get("bubble_fill"))
    outline = source.get("outline", source.get("bubble_outline"))
    return {
        "fill": str(fill) if is_hex_color(fill) else BUBBLE_FILL,
        "outline": str(outline) if is_hex_color(outline) else BUBBLE_OUTLINE,
    }


def bubble_fold_color(fill: str) -> str:
    value = str(fill or "").lstrip("#")
    try:
        red = min(255, int(int(value[0:2], 16) * 1.02))
        green = max(0, int(int(value[2:4], 16) * 0.94))
        blue = max(0, int(int(value[4:6], 16) * 0.78))
    except (TypeError, ValueError):
        return DEFAULT_FOLD
    return f"#{red:02x}{green:02x}{blue:02x}"


def render_bubble_image(
    style: str,
    canvas_w: int,
    canvas_h: int,
    width: int,
    height: int,
    tail_y: int,
    colors: Mapping[str, Any] | None = None,
    background: str = DEFAULT_BACKGROUND,
) -> Image.Image:
    normalized_style = normalize_bubble_style(style)
    render_colors = normalize_render_colors(colors)
    if normalized_style == "caption":
        return _render_caption_bubble(canvas_w, canvas_h, width, height, render_colors, background)
    if normalized_style == "note":
        return _render_note_bubble(canvas_w, canvas_h, width, height, render_colors, background)
    if normalized_style == "soft":
        return _render_soft_bubble(canvas_w, canvas_h, width, height, tail_y, render_colors, background)
    if normalized_style == "cloud":
        return _render_cloud_bubble(canvas_w, canvas_h, width, height, tail_y, render_colors, background)
    if normalized_style == "thought":
        return _render_thought_bubble(canvas_w, canvas_h, width, height, render_colors, background)
    return _render_rounded_bubble(canvas_w, canvas_h, width, height, tail_y, render_colors, background)


def _resize(image: Image.Image, canvas_w: int, canvas_h: int) -> Image.Image:
    return image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)


def _render_masked_shape(
    canvas_w: int,
    canvas_h: int,
    draw_mask,
    colors: Mapping[str, str],
    background: str,
) -> Image.Image:
    scale = 3
    mask = Image.new("L", (canvas_w * scale, canvas_h * scale), 0)
    mask_draw = ImageDraw.Draw(mask)
    draw_mask(mask_draw, scale)

    image = Image.new("RGBA", mask.size, background)
    shadow_mask = Image.new("L", mask.size, 0)
    shadow_mask.paste(mask, (2 * scale, 3 * scale))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(int(1.4 * scale)))
    image.paste(bubble_shadow_color(colors["fill"]), (0, 0), shadow_mask)

    outline = mask.filter(ImageFilter.MaxFilter(scale + 2))
    image.paste(colors["outline"], (0, 0), outline)
    image.paste(colors["fill"], (0, 0), mask)
    return _resize(image, canvas_w, canvas_h)


def _render_soft_bubble(
    canvas_w: int,
    canvas_h: int,
    width: int,
    height: int,
    tail_y: int,
    colors: Mapping[str, str],
    background: str,
) -> Image.Image:
    del tail_y
    scale = 3
    image = Image.new("RGBA", (canvas_w * scale, canvas_h * scale), background)
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    x = 7 * scale
    y = 6 * scale
    w = width * scale
    h = height * scale
    radius = 18 * scale

    mask = Image.new("L", image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=255)
    tail_points = [
        (x + int(w * 0.66), y + h - 3 * scale),
        (x + int(w * 0.76), y + h + 12 * scale),
        (x + int(w * 0.72), y + h - 4 * scale),
    ]
    mask_draw.polygon(tail_points, fill=255)

    shadow_mask = Image.new("L", image.size, 0)
    shadow_mask.paste(mask, (2 * scale, 3 * scale))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(2 * scale))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle((0, 0, image.size[0], image.size[1]), fill=bubble_shadow_color(colors["fill"]))
    image = Image.composite(shadow, image, shadow_mask)

    body = Image.new("RGBA", image.size, colors["fill"])
    image = Image.composite(body, image, mask)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, outline=colors["outline"], width=max(2, scale))
    draw.line(tail_points, fill=colors["outline"], width=max(2, scale), joint="curve")
    draw.arc((x + 8 * scale, y + 7 * scale, x + 58 * scale, y + 34 * scale), 190, 250, fill="#ffffff", width=scale)
    return _resize(image, canvas_w, canvas_h)


def _render_rounded_bubble(
    canvas_w: int,
    canvas_h: int,
    width: int,
    height: int,
    tail_y: int,
    colors: Mapping[str, str],
    background: str,
) -> Image.Image:
    def draw_mask(draw, scale):
        x = 5 * scale
        y = 5 * scale
        w = width * scale
        h = height * scale
        radius = 14 * scale
        draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=255)
        draw.polygon(
            [
                (int(width * 0.66 * scale), int((tail_y - 1) * scale)),
                (int(width * 0.78 * scale), int((tail_y + 13) * scale)),
                (int(width * 0.73 * scale), int((tail_y - 2) * scale)),
            ],
            fill=255,
        )

    return _render_masked_shape(canvas_w, canvas_h, draw_mask, colors, background)


def _render_cloud_bubble(
    canvas_w: int,
    canvas_h: int,
    width: int,
    height: int,
    tail_y: int,
    colors: Mapping[str, str],
    background: str,
) -> Image.Image:
    def draw_mask(draw, scale):
        x = 7 * scale
        y = 7 * scale
        w = max(40, width - 4) * scale
        h = max(30, height - 4) * scale
        draw.rounded_rectangle((x + 8 * scale, y + 8 * scale, x + w - 8 * scale, y + h), radius=20 * scale, fill=255)
        for oval in [
            (x, y + h * 0.36, x + 34 * scale, y + h * 0.88),
            (x + 12 * scale, y + 2 * scale, x + 56 * scale, y + 38 * scale),
            (x + w * 0.30, y, x + w * 0.70, y + 34 * scale),
            (x + w - 58 * scale, y + 4 * scale, x + w - 12 * scale, y + 40 * scale),
            (x + w - 34 * scale, y + h * 0.36, x + w, y + h * 0.88),
        ]:
            draw.ellipse(tuple(int(value) for value in oval), fill=255)
        draw.polygon(
            [
                (int(width * 0.62 * scale), int(tail_y * scale)),
                (int(width * 0.75 * scale), int((tail_y + 12) * scale)),
                (int(width * 0.70 * scale), int((tail_y - 1) * scale)),
            ],
            fill=255,
        )

    return _render_masked_shape(canvas_w, canvas_h, draw_mask, colors, background)


def _render_thought_bubble(
    canvas_w: int,
    canvas_h: int,
    width: int,
    height: int,
    colors: Mapping[str, str],
    background: str,
) -> Image.Image:
    def draw_mask(draw, scale):
        x = 7 * scale
        y = 7 * scale
        w = width * scale
        h = height * scale
        draw.rounded_rectangle((x, y, x + w, y + h), radius=22 * scale, fill=255)
        draw.ellipse((x + w * 0.66, y + h + 2 * scale, x + w * 0.80, y + h + 15 * scale), fill=255)
        draw.ellipse((x + w * 0.82, y + h + 13 * scale, x + w * 0.91, y + h + 22 * scale), fill=255)

    return _render_masked_shape(canvas_w, canvas_h, draw_mask, colors, background)


def _render_note_bubble(
    canvas_w: int,
    canvas_h: int,
    width: int,
    height: int,
    colors: Mapping[str, str],
    background: str,
) -> Image.Image:
    scale = 3
    image = Image.new("RGBA", (canvas_w * scale, canvas_h * scale), background)
    draw = ImageDraw.Draw(image)
    x = 6 * scale
    y = 6 * scale
    w = width * scale
    h = height * scale
    draw.rounded_rectangle(
        (x + 3 * scale, y + 3 * scale, x + w + 3 * scale, y + h + 3 * scale),
        radius=6 * scale,
        fill=bubble_shadow_color(colors["fill"]),
    )
    draw.rounded_rectangle((x, y, x + w, y + h), radius=6 * scale, fill=colors["fill"], outline=colors["outline"], width=scale)
    fold = 14 * scale
    draw.polygon((x + w - fold, y, x + w, y, x + w, y + fold), fill=bubble_fold_color(colors["fill"]), outline=colors["outline"])
    return _resize(image, canvas_w, canvas_h)


def _render_caption_bubble(
    canvas_w: int,
    canvas_h: int,
    width: int,
    height: int,
    colors: Mapping[str, str],
    background: str,
) -> Image.Image:
    scale = 3
    image = Image.new("RGBA", (canvas_w * scale, canvas_h * scale), background)
    draw = ImageDraw.Draw(image)
    x = 6 * scale
    y = 6 * scale
    w = width * scale
    h = height * scale
    draw.rounded_rectangle(
        (x, y, x + w, y + h),
        radius=10 * scale,
        fill=colors["fill"],
        outline=colors["outline"],
        width=scale,
    )
    return _resize(image, canvas_w, canvas_h)
