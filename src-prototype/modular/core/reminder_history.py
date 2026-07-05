"""Reminder history timeline helpers."""

from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

REMINDER_HISTORY_FILE = "danhuang-reminder-history.json"
REMINDER_HISTORY_DEFAULT: dict[str, Any] = {
    "version": 1,
    "events": [],
}
MAX_REMINDER_EVENTS = 500

EVENT_LABELS = {
    "add": "新增",
    "edit": "编辑",
    "complete": "完成",
    "delete": "删除",
    "snooze": "稍后",
    "pin": "置顶",
    "unpin": "取消置顶",
    "reopen": "重新打开",
    "remind": "提醒",
    "repeat_create": "生成重复",
}


def reminder_history_path(pet_dir_or_file: str | Path) -> Path:
    path = Path(pet_dir_or_file)
    return path if path.name == REMINDER_HISTORY_FILE else path / REMINDER_HISTORY_FILE


def default_reminder_history() -> dict[str, Any]:
    return copy.deepcopy(REMINDER_HISTORY_DEFAULT)


def normalize_reminder_event(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "time": str(event.get("time", "") or ""),
        "type": str(event.get("type", "remind") or "remind"),
        "todo_id": str(event.get("todo_id", "") or ""),
        "title": str(event.get("title", "") or ""),
        "category": str(event.get("category", "") or ""),
        "priority": str(event.get("priority", "") or ""),
        "due_at": str(event.get("due_at", "") or ""),
        "repeat": str(event.get("repeat", "") or ""),
        **{str(k): v for k, v in event.items() if str(k) not in {"time", "type", "todo_id", "title", "category", "priority", "due_at", "repeat"}},
    }


def normalize_reminder_history(raw: Mapping[str, Any] | None) -> dict[str, Any]:
    state = default_reminder_history()
    if isinstance(raw, Mapping):
        state.update(raw)
    try:
        state["version"] = int(state.get("version") or 1)
    except (TypeError, ValueError):
        state["version"] = 1
    events = state.get("events") if isinstance(state.get("events"), list) else []
    state["events"] = [
        normalize_reminder_event(event)
        for event in events[-MAX_REMINDER_EVENTS:]
        if isinstance(event, Mapping)
    ]
    return state


def load_reminder_history(pet_dir_or_file: str | Path) -> dict[str, Any]:
    path = reminder_history_path(pet_dir_or_file)
    if not path.exists():
        return normalize_reminder_history(None)
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        saved = None
    return normalize_reminder_history(saved if isinstance(saved, Mapping) else None)


def save_reminder_history(pet_dir_or_file: str | Path, history: Mapping[str, Any]) -> dict[str, Any]:
    clean = normalize_reminder_history(history)
    clean["updated_at"] = datetime.now().isoformat(timespec="seconds")
    path = reminder_history_path(pet_dir_or_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    return clean


def log_todo_event(
    history: Mapping[str, Any],
    todo: Mapping[str, Any],
    event_type: str = "remind",
    extra: Mapping[str, Any] | None = None,
    now: datetime | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    state = normalize_reminder_history(history)
    payload: dict[str, Any] = {
        "time": (now or datetime.now()).isoformat(timespec="seconds"),
        "type": str(event_type or "remind"),
        "todo_id": todo.get("id"),
        "title": todo.get("title"),
        "category": todo.get("category"),
        "priority": todo.get("priority"),
        "due_at": todo.get("due_at"),
        "repeat": todo.get("repeat"),
    }
    if extra:
        payload.update(dict(extra))
    state.setdefault("events", []).append(normalize_reminder_event(payload))
    state["events"] = state["events"][-MAX_REMINDER_EVENTS:]
    return state, payload


def timeline_text(history: Mapping[str, Any], limit: int = 6) -> str:
    events = normalize_reminder_history(history).get("events", [])[-max(0, int(limit)) :]
    if not events:
        return "还没有时间轴记录。"
    lines: list[str] = []
    for event in reversed(events):
        when = str(event.get("time", ""))[5:16].replace("T", " ")
        label = EVENT_LABELS.get(event.get("type"), str(event.get("type", "记录")))
        lines.append(f"{when}  {label}  {event.get('title', '')}")
    return "\n".join(lines)


def fresh_distribution_reminder_history() -> dict[str, Any]:
    return {"version": 1, "events": [], "updated_at": ""}
