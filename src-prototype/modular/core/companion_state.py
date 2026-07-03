"""Companion state loading and level calculation for each pet."""

from __future__ import annotations

import copy
import json
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping

from .pet_model import sanitize_pet_slug

COMPANION_FILE = "companion-state.json"
CHAT_MEMORY_FILE = "chat-memory.json"
MEMORY_SUMMARY_FILE = "memory-summary.json"
PET_STATE_DIR = "pet-state"

COMPANION_DEFAULT: dict[str, Any] = {
    "xp": 0,
    "level": 1,
    "created_date": "",
    "last_active_date": "",
    "streak_days": 0,
    "total_seconds": 0,
    "interactions": 0,
    "talks": 0,
    "roams": 0,
    "manual_actions": 0,
    "daily_bonus_dates": [],
    "last_saved_at": "",
}

LEVELS = [
    (1, "回到身边", 0),
    (2, "认得气味", 30),
    (3, "桌边趴着", 80),
    (4, "等你回头", 150),
    (5, "小尾巴跟着", 250),
    (6, "守着主人", 400),
    (7, "安静陪伴", 600),
    (8, "家里的位置", 850),
    (9, "一直都在", 1150),
    (10, "家人", 1500),
]

XP_RULES = {
    "interaction": 2,
    "talk": 1,
    "roam": 1,
    "manual_action": 2,
    "daily_start": 10,
    "streak_3": 10,
    "streak_7": 25,
}


def companion_default() -> dict[str, Any]:
    return copy.deepcopy(COMPANION_DEFAULT)


def level_for_xp(xp: Any) -> tuple[int, str, int]:
    try:
        amount = int(xp)
    except (TypeError, ValueError):
        amount = 0
    amount = max(0, amount)
    current = LEVELS[0]
    for level in LEVELS:
        if amount >= level[2]:
            current = level
        else:
            break
    return current


def normalize_companion_state(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    state = companion_default()
    if isinstance(raw, Mapping):
        state.update(raw)

    for key in ("xp", "total_seconds", "interactions", "talks", "roams", "manual_actions", "streak_days"):
        try:
            state[key] = max(0, int(state.get(key, 0) or 0))
        except (TypeError, ValueError):
            state[key] = 0

    state["level"] = level_for_xp(state["xp"])[0]
    for key in ("created_date", "last_active_date", "last_saved_at"):
        state[key] = str(state.get(key) or "")
    if not isinstance(state.get("daily_bonus_dates"), list):
        state["daily_bonus_dates"] = []
    else:
        state["daily_bonus_dates"] = [str(item) for item in state["daily_bonus_dates"]]
    return state


def load_json_object(path: str | Path, default: Mapping[str, Any]) -> dict[str, Any]:
    state = copy.deepcopy(dict(default))
    file_path = Path(path)
    if file_path.exists():
        try:
            saved = json.loads(file_path.read_text(encoding="utf-8"))
            if isinstance(saved, Mapping):
                state.update(saved)
        except (OSError, ValueError, TypeError):
            pass
    return state


def pet_state_dir(pet_dir: str | Path, pet_id: str, create: bool = False) -> Path:
    path = Path(pet_dir) / PET_STATE_DIR / sanitize_pet_slug(pet_id or "danhuang")
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def pet_state_file(pet_dir: str | Path, pet_id: str, filename: str) -> Path:
    return pet_state_dir(pet_dir, pet_id) / filename


def legacy_companion_path(pet_dir: str | Path) -> Path:
    return Path(pet_dir) / COMPANION_FILE


def migrate_legacy_pet_state(pet_dir: str | Path, pet_id: str = "danhuang") -> list[Path]:
    if sanitize_pet_slug(pet_id) != "danhuang":
        return []
    root = Path(pet_dir)
    state_dir = pet_state_dir(root, pet_id, create=True)
    pairs = [
        (root / COMPANION_FILE, state_dir / COMPANION_FILE),
        (root / "danhuang-chat-memory.json", state_dir / CHAT_MEMORY_FILE),
        (root / "danhuang-memory-summary.json", state_dir / MEMORY_SUMMARY_FILE),
    ]
    migrated: list[Path] = []
    for source, target in pairs:
        if source.exists() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            migrated.append(target)
    return migrated


def load_companion_state(
    pet_dir: str | Path,
    pet_id: str = "danhuang",
    migrate_legacy: bool = False,
) -> dict[str, Any]:
    if migrate_legacy:
        migrate_legacy_pet_state(pet_dir, pet_id)
    path = pet_state_file(pet_dir, pet_id, COMPANION_FILE)
    if not path.exists() and sanitize_pet_slug(pet_id) == "danhuang":
        path = legacy_companion_path(pet_dir)
    return normalize_companion_state(load_json_object(path, COMPANION_DEFAULT))


def save_companion_state(pet_dir: str | Path, pet_id: str, state: Mapping[str, Any]) -> dict[str, Any]:
    clean = normalize_companion_state(state)
    clean["last_saved_at"] = datetime.now().isoformat(timespec="seconds")
    path = pet_state_file(pet_dir, pet_id, COMPANION_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    return clean


def reset_companion_state(today: date | None = None) -> dict[str, Any]:
    current_day = (today or date.today()).isoformat()
    state = companion_default()
    state["created_date"] = current_day
    state["last_active_date"] = current_day
    state["streak_days"] = 1
    state["last_saved_at"] = datetime.now().isoformat(timespec="seconds")
    return state


def fresh_distribution_companion_state(today: date | None = None) -> dict[str, Any]:
    current_day = (today or date.today()).isoformat()
    state = companion_default()
    state["created_date"] = current_day
    state["last_active_date"] = current_day
    state["last_saved_at"] = datetime.now().isoformat(timespec="seconds")
    return state


def companion_hours(state: Mapping[str, Any]) -> float:
    try:
        seconds = int(state.get("total_seconds", 0) or 0)
    except (TypeError, ValueError):
        seconds = 0
    return round(max(0, seconds) / 3600, 1)


def companion_summary(state: Mapping[str, Any]) -> dict[str, Any]:
    clean = normalize_companion_state(state)
    level, title, current_xp = level_for_xp(clean["xp"])
    next_levels = [item for item in LEVELS if item[0] > level]
    next_xp = next_levels[0][2] if next_levels else current_xp
    return {
        "level": level,
        "title": title,
        "xp": clean["xp"],
        "current_level_xp": current_xp,
        "next_level_xp": next_xp,
        "hours": companion_hours(clean),
        "streak_days": clean["streak_days"],
        "interactions": clean["interactions"],
        "talks": clean["talks"],
        "roams": clean["roams"],
    }
