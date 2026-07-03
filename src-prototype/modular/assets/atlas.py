"""Atlas and sprite-strip inspection helpers for the Tk prototype split."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from PIL import Image

from core.pet_model import CELL_H, CELL_W, CUSTOM_ACTION_MAX_FRAMES, ROWS, clamp


def image_info(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    info: dict[str, Any] = {
        "path": str(target),
        "exists": target.exists(),
        "width": 0,
        "height": 0,
        "mode": "",
        "error": "",
    }
    if not target.exists():
        info["error"] = "missing"
        return info
    try:
        with Image.open(target) as image:
            info.update({"width": int(image.width), "height": int(image.height), "mode": str(image.mode)})
    except OSError as exc:
        info["error"] = str(exc)
    return info


def atlas_grid_info(path: str | Path) -> dict[str, Any]:
    info = image_info(path)
    width = int(info.get("width") or 0)
    height = int(info.get("height") or 0)
    columns = width // CELL_W if width > 0 else 0
    rows = height // CELL_H if height > 0 else 0
    return {
        **info,
        "cell_width": CELL_W,
        "cell_height": CELL_H,
        "columns": columns,
        "rows": rows,
        "complete_cell_grid": width > 0 and height > 0 and width % CELL_W == 0 and height % CELL_H == 0,
    }


def action_frame_spec(action_id: str) -> dict[str, Any] | None:
    if action_id not in ROWS:
        return None
    row, frame_count, durations = ROWS[action_id]
    return {
        "id": action_id,
        "row": int(row),
        "frames": int(frame_count),
        "durations": [int(item) for item in durations],
    }


def available_atlas_actions(path: str | Path) -> list[str]:
    grid = atlas_grid_info(path)
    rows = int(grid.get("rows") or 0)
    columns = int(grid.get("columns") or 0)
    actions: list[str] = []
    for action_id, (row, frame_count, _durations) in ROWS.items():
        if row < rows and frame_count <= columns:
            actions.append(action_id)
    return actions


def validate_atlas_image(path: str | Path, required_actions: Iterable[str] | None = None) -> dict[str, Any]:
    grid = atlas_grid_info(path)
    errors: list[str] = []
    warnings: list[str] = []
    if not grid["exists"]:
        errors.append("spritesheet 不存在。")
    elif grid.get("error"):
        errors.append(f"spritesheet 无法读取：{grid['error']}")
    else:
        if int(grid["width"]) < CELL_W or int(grid["height"]) < CELL_H:
            errors.append(f"spritesheet 必须至少包含一个 {CELL_W}x{CELL_H} 单元格。")
        if not grid["complete_cell_grid"]:
            warnings.append(f"spritesheet 尺寸不是 {CELL_W}x{CELL_H} 的整数倍，运行时会按单元格裁切。")
    available = set(available_atlas_actions(path)) if not errors else set()
    missing_required = [
        str(action)
        for action in required_actions or []
        if str(action) in ROWS and str(action) not in available
    ]
    if missing_required:
        errors.append("缺少必需动作行：" + "、".join(missing_required))
    return {
        **grid,
        "available_actions": sorted(available, key=lambda action: ROWS[action][0]),
        "missing_required_actions": missing_required,
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def strip_frame_durations(action_id: str, frame_count: int, provided: list[Any] | None = None) -> list[int]:
    source = provided if isinstance(provided, list) else []
    durations: list[int] = []
    for index in range(max(0, int(frame_count))):
        try:
            duration = int(source[index])
        except (IndexError, TypeError, ValueError):
            if action_id in ROWS and index < len(ROWS[action_id][2]):
                duration = int(ROWS[action_id][2][index])
            else:
                duration = 180
        durations.append(int(clamp(duration, 60, 900)))
    return durations


def validate_extension_strip_image(
    path: str | Path,
    target_state: str | None = None,
    durations: list[Any] | None = None,
) -> dict[str, Any]:
    info = image_info(path)
    errors: list[str] = []
    warnings: list[str] = []
    frame_count = 0
    if not info["exists"]:
        errors.append("动作条不存在。")
    elif info.get("error"):
        errors.append(f"动作条无法读取：{info['error']}")
    else:
        width = int(info["width"])
        height = int(info["height"])
        if height != CELL_H or width < CELL_W or width % CELL_W != 0:
            errors.append(f"动作条必须是横向 sprite strip，每帧 {CELL_W}x{CELL_H}，当前是 {width}x{height}。")
        else:
            frame_count = width // CELL_W
            if frame_count > CUSTOM_ACTION_MAX_FRAMES:
                warnings.append(f"动作条共有 {frame_count} 帧，当前运行最多使用前 {CUSTOM_ACTION_MAX_FRAMES} 帧。")
                frame_count = CUSTOM_ACTION_MAX_FRAMES
    action_id = str(target_state or "")
    return {
        **info,
        "cell_width": CELL_W,
        "cell_height": CELL_H,
        "frames": frame_count,
        "durations": strip_frame_durations(action_id, frame_count, durations),
        "errors": errors,
        "warnings": warnings,
        "valid": not errors,
    }


def extension_asset_frame_info(pet_dir: str | Path, asset: Mapping[str, Any]) -> dict[str, Any]:
    strip = str(asset.get("strip") or "")
    path = Path(strip)
    target = path if path.is_absolute() else Path(pet_dir) / strip
    result = validate_extension_strip_image(target, str(asset.get("id") or ""), asset.get("durations"))
    return {
        "id": str(asset.get("id") or ""),
        "label": str(asset.get("label") or ""),
        "strip": strip,
        "exists": result["exists"],
        "frames": result["frames"],
        "durations": result["durations"],
        "valid": result["valid"],
        "errors": result["errors"],
        "warnings": result["warnings"],
    }
