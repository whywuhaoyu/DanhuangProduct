"""Todo and local reminder business logic for the Tk prototype split."""

from __future__ import annotations

import calendar
import copy
import json
import random
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Mapping

TODO_FILE = "danhuang-todos.json"
TODO_DEFAULT: dict[str, Any] = {
    "version": 1,
    "items": [],
}

TODO_CATEGORIES = ["工作", "生活", "学习", "内容", "灵感", "纪念", "其他"]
TODO_PRIORITIES = ["普通", "重要", "紧急"]
TODO_REPEAT_LABELS = {
    "不重复": "none",
    "每天": "daily",
    "每周": "weekly",
    "每月": "monthly",
    "每年": "yearly",
}
TODO_IMPORTANT_INTERVAL_LABELS = {
    "不持续提醒": 0,
    "每10分钟": 10,
    "每30分钟": 30,
    "每1小时": 60,
    "每天一次": 1440,
}


def todos_path(pet_dir_or_file: str | Path) -> Path:
    path = Path(pet_dir_or_file)
    return path if path.name == TODO_FILE else path / TODO_FILE


def default_todos() -> dict[str, Any]:
    return copy.deepcopy(TODO_DEFAULT)


def _non_negative_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return default


def parse_iso_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def normalize_due_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text.replace("：", ":"))
    day_prefix = ""
    for prefix in ("今天", "明天", "后天"):
        if text.startswith(prefix):
            day_prefix = prefix
            text = text.replace(prefix, "", 1).strip()
            break
    point_half = re.fullmatch(r"(\d{1,2})点半", text)
    if point_half:
        text = f"{int(point_half.group(1)):02d}:30"
    else:
        point_minute = re.fullmatch(r"(\d{1,2})点(\d{1,2})分?", text)
        if point_minute:
            text = f"{int(point_minute.group(1)):02d}:{int(point_minute.group(2)):02d}"
        else:
            point_hour = re.fullmatch(r"(\d{1,2})点", text)
            if point_hour:
                text = f"{int(point_hour.group(1)):02d}:00"
    return f"{day_prefix} {text}".strip() if day_prefix else text


def _replace_time(base: datetime, hour: int, minute: int) -> datetime | None:
    try:
        return base.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except ValueError:
        return None


def parse_local_datetime(value: Any, now: datetime | None = None) -> datetime | None:
    text = normalize_due_text(value)
    if not text:
        return None
    now = now or datetime.now()
    compact = text.replace(" ", "")
    relative = re.fullmatch(r"(\d+)(分钟|分|小时|天)后", compact)
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2)
        if unit in {"分钟", "分"}:
            return now + timedelta(minutes=amount)
        if unit == "小时":
            return now + timedelta(hours=amount)
        if unit == "天":
            return now + timedelta(days=amount)
    if re.fullmatch(r"\d{1,2}:\d{2}", text):
        hour, minute = [int(part) for part in text.split(":")]
        target = _replace_time(now, hour, minute)
        if target is None:
            return None
        return target if target > now else target + timedelta(days=1)
    for prefix, days, default_time in (("今天", 0, "18:00"), ("明天", 1, "09:00"), ("后天", 2, "09:00")):
        if text.startswith(prefix):
            rest = text.replace(prefix, "", 1).strip() or default_time
            if re.fullmatch(r"\d{1,2}:\d{2}", rest):
                hour, minute = [int(part) for part in rest.split(":")]
                target = _replace_time(now + timedelta(days=days), hour, minute)
                if target is None:
                    return None
                if prefix == "今天" and target <= now:
                    return target + timedelta(days=1)
                return target
    for fmt in ("%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt)
            if fmt == "%Y-%m-%d":
                parsed = parsed.replace(hour=9, minute=0)
            return parsed
        except ValueError:
            pass
    return parse_iso_datetime(text)


def extract_due_text_from_sentence(text: Any, now: datetime | None = None) -> tuple[str, str]:
    source = normalize_due_text(text)
    patterns = [
        r"\d+\s*(?:分钟|分|小时|天)后",
        r"(?:今天|明天|后天)\s*\d{1,2}(?::\d{2}|点半|点\d{1,2}分?|点)?",
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:[ T]\d{1,2}:\d{2})?",
        r"\d{1,2}:\d{2}",
        r"\d{1,2}点半",
        r"\d{1,2}点\d{1,2}分?",
        r"\d{1,2}点",
    ]
    for pattern in patterns:
        match = re.search(pattern, source)
        if match:
            due_text = normalize_due_text(match.group(0))
            if parse_local_datetime(due_text, now=now) is not None:
                return due_text, match.group(0)
    return "", ""


def normalize_todo(
    item: Mapping[str, Any],
    now: datetime | None = None,
    id_factory: Callable[[], str] | None = None,
) -> dict[str, Any]:
    current = now or datetime.now()
    current_text = current.isoformat(timespec="seconds")
    todo_id = str(item.get("id") or (id_factory() if id_factory else f"todo-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"))
    todo = {
        "id": todo_id,
        "title": str(item.get("title", "")).strip(),
        "note": str(item.get("note", "")).strip(),
        "category": str(item.get("category", "工作") or "工作"),
        "priority": str(item.get("priority", "普通") or "普通"),
        "due_at": str(item.get("due_at", "") or ""),
        "repeat": str(item.get("repeat", "none") or "none"),
        "status": str(item.get("status", "open") or "open"),
        "pinned": bool(item.get("pinned", False)),
        "important_interval_minutes": _non_negative_int(item.get("important_interval_minutes", 0)),
        "snooze_until": str(item.get("snooze_until", "") or ""),
        "created_at": str(item.get("created_at", current_text) or current_text),
        "updated_at": str(item.get("updated_at", current_text) or current_text),
        "completed_at": str(item.get("completed_at", "") or ""),
        "deleted_at": str(item.get("deleted_at", "") or ""),
        "last_reminded_at": str(item.get("last_reminded_at", "") or ""),
        "remind_count": _non_negative_int(item.get("remind_count", 0)),
    }
    if todo["category"] not in TODO_CATEGORIES:
        todo["category"] = "其他"
    if todo["priority"] not in TODO_PRIORITIES:
        todo["priority"] = "普通"
    if todo["repeat"] not in set(TODO_REPEAT_LABELS.values()):
        todo["repeat"] = "none"
    if todo["status"] not in {"open", "done", "deleted"}:
        todo["status"] = "open"
    return todo


def normalize_todos_state(raw: Mapping[str, Any] | None, now: datetime | None = None) -> dict[str, Any]:
    state = default_todos()
    if isinstance(raw, Mapping):
        state.update(raw)
    try:
        state["version"] = int(state.get("version") or 1)
    except (TypeError, ValueError):
        state["version"] = 1
    items = state.get("items") if isinstance(state.get("items"), list) else []
    state["items"] = [normalize_todo(item, now=now) for item in items if isinstance(item, Mapping)]
    state["updated_at"] = str(state.get("updated_at", "") or "")
    return state


def load_todos(pet_dir_or_file: str | Path) -> dict[str, Any]:
    path = todos_path(pet_dir_or_file)
    if not path.exists():
        return normalize_todos_state(None)
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        saved = None
    return normalize_todos_state(saved if isinstance(saved, Mapping) else None)


def save_todos(pet_dir_or_file: str | Path, state: Mapping[str, Any]) -> dict[str, Any]:
    clean = normalize_todos_state(state)
    clean["updated_at"] = datetime.now().isoformat(timespec="seconds")
    path = todos_path(pet_dir_or_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    return clean


def infer_todo_category(text: Any) -> str:
    lowered = str(text or "").lower()
    if any(word in lowered for word in ["公众号", "文章", "视频", "素材", "选题", "脚本", "发布", "剪辑"]):
        return "内容"
    if any(word in lowered for word in ["代码", "开发", "bug", "需求", "项目", "结算", "接口", "测试", "上线"]):
        return "工作"
    if any(word in lowered for word in ["学习", "课程", "阅读", "复习", "笔记"]):
        return "学习"
    if any(word in lowered for word in ["买", "快递", "吃饭", "喝水", "运动", "睡觉", "休息"]):
        return "生活"
    if any(word in lowered for word in ["想法", "灵感", "点子"]):
        return "灵感"
    if any(word in lowered for word in ["蛋黄", "纪念", "照片"]):
        return "纪念"
    return "工作"


def infer_todo_priority(text: Any) -> str:
    lowered = str(text or "").lower()
    if any(word in lowered for word in ["紧急", "马上", "必须", "一定", "ddl", "deadline"]):
        return "紧急"
    if any(word in lowered for word in ["重要", "别忘", "记得"]):
        return "重要"
    return "普通"


def is_todo_lookup_query(text: Any, now: datetime | None = None) -> bool:
    raw = str(text or "").strip()
    if not raw:
        return False
    lowered = raw.lower()
    create_triggers = ("提醒我", "帮我记", "记一下", "记个待办", "添加待办", "加个待办")
    strong_lookup_terms = (
        "哪些", "有什么", "列表", "看一下", "看下", "查看", "多少", "几项",
        "接下来", "还剩", "没做", "未完成", "逾期", "到点", "重要", "安排", "清单",
    )
    create_trigger_lookup_terms = tuple(term for term in strong_lookup_terms if term != "安排")
    if any(trigger in raw for trigger in create_triggers):
        due_text, _due_raw = extract_due_text_from_sentence(raw, now=now)
        if due_text:
            return False
        if not any(term in raw for term in create_trigger_lookup_terms):
            return False
    target_terms = ("待办", "提醒", "安排", "事项", "任务", "清单", "todo")
    implicit_patterns = (
        "今天要做", "今日要做", "今天还有", "今日还有", "接下来做",
        "有什么没做", "还要做什么", "还没做什么", "今天安排",
    )
    has_target = any(term in lowered for term in target_terms) or any(term in raw for term in implicit_patterns)
    if not has_target:
        return False
    lookup_terms = (*strong_lookup_terms, "今天", "今日", "明天", "所有", "全部", "todo")
    return any(term in lowered for term in lookup_terms)


def todo_lookup_focus(text: Any) -> tuple[str, str]:
    raw = str(text or "")
    if any(term in raw for term in ("逾期", "超时", "过期", "到点")):
        return "逾期", "已到点"
    if any(term in raw for term in ("重要", "紧急")):
        return "重要", "重要"
    if any(term in raw for term in ("今天", "今日", "安排")):
        return "今日", "今天"
    return "全部", "未完成"


def extract_todo_request_from_chat(text: Any, now: datetime | None = None) -> dict[str, Any] | None:
    original = " ".join(str(text or "").strip().split())
    if not original:
        return None
    create_triggers = ["提醒我", "帮我记", "记一下", "记个待办", "添加待办", "加个待办"]
    has_create_trigger = any(trigger in original for trigger in create_triggers)
    if not has_create_trigger:
        if "待办" not in original:
            return None
        if any(word in original for word in ["哪些", "有什么", "列表", "看一下", "查看", "多少", "今天", "逾期"]):
            return None
    triggers = [*create_triggers, "待办"]
    if not any(trigger in original for trigger in triggers):
        return None
    due_text, due_raw = extract_due_text_from_sentence(original, now=now)
    lookup_terms = ["哪些", "有什么", "列表", "看一下", "看下", "查看", "多少", "今天", "今日", "逾期", "未完成", "重要", "安排", "清单"]
    if has_create_trigger and "待办" in original and any(word in original for word in lookup_terms) and not due_text:
        return None
    title = original
    for token in triggers:
        title = title.replace(token, " ")
    for token in ["请", "帮我", "一下", "到时候", "的时候", "记得", "提醒", "待办"]:
        title = title.replace(token, " ")
    for raw in {due_raw, due_raw.replace(" ", ""), due_text, due_text.replace(" ", "")}:
        if raw:
            title = title.replace(raw, " ")
    title = re.sub(r"(?:今天|明天|后天)\s*\d{1,2}(?::\d{2}|点半|点\d{1,2}分?|点)?", " ", title)
    title = re.sub(r"\d+\s*(?:分钟|分|小时|天)后", " ", title)
    title = re.sub(r"[，,。；;：:]+", " ", title)
    title = " ".join(title.split()) or "看一下这件事"
    repeat = "none"
    if any(word in original for word in ["每天", "每日"]):
        repeat = "daily"
    elif any(word in original for word in ["每周", "每星期"]):
        repeat = "weekly"
    elif "每月" in original:
        repeat = "monthly"
    elif "每年" in original:
        repeat = "yearly"
    priority = infer_todo_priority(original)
    interval = 0
    if any(word in original for word in ["持续提醒", "一直提醒", "反复提醒"]):
        interval = 10 if priority == "紧急" else 30
    return {
        "title": title[:80],
        "due_text": due_text,
        "category": infer_todo_category(original),
        "priority": priority,
        "repeat": repeat,
        "important_interval_minutes": interval,
    }


def add_todo(
    state: Mapping[str, Any],
    title: str,
    due_text: str = "",
    category: str = "工作",
    priority: str = "普通",
    repeat: str = "none",
    note: str = "",
    important_interval_minutes: int = 0,
    now: datetime | None = None,
    id_factory: Callable[[], str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    title = " ".join(str(title or "").strip().split())
    if not title:
        raise ValueError("待办标题不能为空")
    current = now or datetime.now()
    due = parse_local_datetime(due_text, now=current)
    todo = normalize_todo(
        {
            "id": id_factory() if id_factory else f"todo-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
            "title": title,
            "note": note,
            "category": category,
            "priority": priority,
            "due_at": due.isoformat(timespec="minutes") if due else "",
            "repeat": repeat,
            "important_interval_minutes": important_interval_minutes,
            "status": "open",
            "created_at": current.isoformat(timespec="seconds"),
            "updated_at": current.isoformat(timespec="seconds"),
        },
        now=current,
    )
    updated = normalize_todos_state(state, now=current)
    updated.setdefault("items", []).append(todo)
    return updated, todo


def create_todo_from_chat_if_needed(
    state: Mapping[str, Any],
    text: Any,
    now: datetime | None = None,
    id_factory: Callable[[], str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    payload = extract_todo_request_from_chat(text, now=now)
    if not payload:
        return normalize_todos_state(state, now=now), None
    return add_todo(
        state,
        payload["title"],
        payload["due_text"],
        payload["category"],
        payload["priority"],
        payload["repeat"],
        "",
        payload["important_interval_minutes"],
        now=now,
        id_factory=id_factory,
    )


def _todo_target_time(todo: Mapping[str, Any]) -> datetime | None:
    return parse_iso_datetime(todo.get("snooze_until")) or parse_iso_datetime(todo.get("due_at"))


def open_todos(
    state: Mapping[str, Any],
    include_done: bool = False,
    query: str = "",
    category: str = "全部",
    focus: str = "全部",
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    clean = normalize_todos_state(state, now=now)
    query = str(query or "").strip().lower()
    category = str(category or "全部")
    focus = str(focus or "全部")
    current = now or datetime.now()
    today = current.date()
    items: list[dict[str, Any]] = []
    for item in clean.get("items", []):
        status = item.get("status")
        if status == "deleted":
            continue
        if status == "done" and not include_done:
            continue
        if category != "全部" and item.get("category") != category:
            continue
        due = _todo_target_time(item)
        if focus == "今日" and (due is None or due.date() != today):
            continue
        if focus == "逾期" and (due is None or due > current or item.get("status") == "done"):
            continue
        if focus == "重要" and item.get("priority") not in {"重要", "紧急"}:
            continue
        haystack = " ".join([str(item.get("title", "")), str(item.get("note", "")), str(item.get("category", "")), str(item.get("priority", ""))]).lower()
        if query and query not in haystack:
            continue
        items.append(item)

    def sort_key(item: Mapping[str, Any]) -> tuple[Any, ...]:
        due = _todo_target_time(item)
        priority_rank = {"紧急": 0, "重要": 1, "普通": 2}
        status_rank = 1 if item.get("status") == "done" else 0
        pin_rank = 0 if item.get("pinned") else 1
        return (status_rank, pin_rank, due or datetime.max, priority_rank.get(item.get("priority", "普通"), 2), item.get("created_at", ""))

    return sorted(items, key=sort_key)


def todo_stats(state: Mapping[str, Any], now: datetime | None = None) -> dict[str, int]:
    current = now or datetime.now()
    today = current.date()
    stats = {"open": 0, "done": 0, "today": 0, "overdue": 0, "important": 0}
    for todo in normalize_todos_state(state, now=current).get("items", []):
        status = todo.get("status")
        if status == "deleted":
            continue
        if status == "done":
            stats["done"] += 1
            continue
        stats["open"] += 1
        if todo.get("priority") in {"重要", "紧急"}:
            stats["important"] += 1
        due = _todo_target_time(todo)
        if due is None:
            continue
        if due.date() == today:
            stats["today"] += 1
        if due <= current:
            stats["overdue"] += 1
    return stats


def todo_due_text(todo: Mapping[str, Any], now: datetime | None = None) -> str:
    due = _todo_target_time(todo)
    if due is None:
        return "无提醒时间"
    current = now or datetime.now()
    if due.date() == current.date():
        return "今天 " + due.strftime("%H:%M")
    if due.date() == (current + timedelta(days=1)).date():
        return "明天 " + due.strftime("%H:%M")
    return due.strftime("%m-%d %H:%M")


def todo_context_for_ai(state: Mapping[str, Any], limit: int = 8, now: datetime | None = None) -> str:
    stats = todo_stats(state, now=now)
    lines = [f"未完成 {stats['open']} 项，今日 {stats['today']} 项，已超时 {stats['overdue']} 项，重要 {stats['important']} 项。"]
    items = open_todos(state, include_done=False, now=now)[:limit]
    if not items:
        lines.append("暂无未完成待办。")
        return "\n".join(lines)
    current = now or datetime.now()
    for todo in items:
        due = _todo_target_time(todo)
        if due:
            if due <= current:
                due_text = "已到 " + due.strftime("%m-%d %H:%M")
            elif due.date() == current.date():
                due_text = "今天 " + due.strftime("%H:%M")
            else:
                due_text = due.strftime("%m-%d %H:%M")
        else:
            due_text = "无提醒"
        lines.append(f"- {todo.get('title', '')} | {todo.get('category', '')} | {todo.get('priority', '')} | {due_text}")
    return "\n".join(lines)


def build_local_todo_lookup_reply(state: Mapping[str, Any], text: Any, limit: int = 6, now: datetime | None = None) -> str:
    focus, scope_label = todo_lookup_focus(text)
    items = open_todos(state, include_done=False, focus=focus, now=now)
    stats = todo_stats(state, now=now)
    if not items:
        if focus == "全部":
            return "主人，我看了一下，现在没有未完成待办。你可以先安心做眼前这一件。"
        return f"主人，我看了一下，{scope_label}没有未完成待办。当前全部未完成还有 {stats['open']} 项。"
    lines: list[str] = []
    for index, todo in enumerate(items[:limit], 1):
        lines.append(f"{index}. {str(todo.get('title', '')).strip() or '未命名待办'}｜{todo_due_text(todo, now=now)}｜{todo.get('category', '工作')}｜{todo.get('priority', '普通')}")
    more = len(items) - limit
    more_text = f"\n还有 {more} 条在提醒页里。" if more > 0 else ""
    return (
        f"主人，我看了一下，{scope_label}有 {len(items)} 条未完成：\n"
        + "\n".join(lines)
        + more_text
        + f"\n总览：未完成 {stats['open']}，今天 {stats['today']}，已到点 {stats['overdue']}，重要 {stats['important']}。"
    )


def add_months(value: datetime, months: int) -> datetime:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def create_next_repeat_todo(state: Mapping[str, Any], todo: Mapping[str, Any], now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    repeat = todo.get("repeat", "none")
    if repeat == "none":
        return normalize_todos_state(state, now=now), None
    due = parse_iso_datetime(todo.get("due_at"))
    if due is None:
        return normalize_todos_state(state, now=now), None
    if repeat == "daily":
        next_due = due + timedelta(days=1)
    elif repeat == "weekly":
        next_due = due + timedelta(days=7)
    elif repeat == "monthly":
        next_due = add_months(due, 1)
    elif repeat == "yearly":
        next_due = add_months(due, 12)
    else:
        return normalize_todos_state(state, now=now), None
    current = now or datetime.now()
    next_todo = normalize_todo(
        {
            "title": todo.get("title", ""),
            "note": todo.get("note", ""),
            "category": todo.get("category", "工作"),
            "priority": todo.get("priority", "普通"),
            "due_at": next_due.isoformat(timespec="minutes"),
            "repeat": repeat,
            "important_interval_minutes": todo.get("important_interval_minutes", 0),
            "status": "open",
            "created_at": current.isoformat(timespec="seconds"),
        },
        now=current,
    )
    updated = normalize_todos_state(state, now=current)
    updated.setdefault("items", []).append(next_todo)
    return updated, next_todo


def complete_todo(state: Mapping[str, Any], todo_id: str, now: datetime | None = None, create_repeat: bool = True) -> tuple[dict[str, Any], dict[str, Any] | None]:
    current = now or datetime.now()
    updated = normalize_todos_state(state, now=current)
    completed: dict[str, Any] | None = None
    for todo in updated.get("items", []):
        if todo.get("id") != todo_id:
            continue
        todo["status"] = "done"
        todo["completed_at"] = current.isoformat(timespec="seconds")
        todo["updated_at"] = todo["completed_at"]
        completed = todo
        break
    if completed and create_repeat:
        updated, _next = create_next_repeat_todo(updated, completed, now=current)
    return updated, completed


def snooze_todo(state: Mapping[str, Any], todo_id: str, minutes: int, now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    current = now or datetime.now()
    until = current + timedelta(minutes=max(0, int(minutes)))
    updated = normalize_todos_state(state, now=current)
    changed = None
    for todo in updated.get("items", []):
        if todo.get("id") == todo_id:
            todo["snooze_until"] = until.isoformat(timespec="minutes")
            todo["updated_at"] = current.isoformat(timespec="seconds")
            changed = todo
            break
    return updated, changed


def due_todos(state: Mapping[str, Any], now: datetime | None = None) -> list[dict[str, Any]]:
    current = now or datetime.now()
    due: list[dict[str, Any]] = []
    for todo in open_todos(state, now=current):
        target = _todo_target_time(todo)
        if target is None or target > current:
            continue
        last = parse_iso_datetime(todo.get("last_reminded_at"))
        interval = _non_negative_int(todo.get("important_interval_minutes", 0))
        min_gap = timedelta(minutes=interval if interval > 0 else 5)
        if last is not None and current - last < min_gap:
            continue
        due.append(todo)
    return due


def mark_todo_reminded(state: Mapping[str, Any], todo_id: str, now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    current = now or datetime.now()
    updated = normalize_todos_state(state, now=current)
    changed = None
    for todo in updated.get("items", []):
        if todo.get("id") == todo_id:
            todo["last_reminded_at"] = current.isoformat(timespec="seconds")
            todo["remind_count"] = _non_negative_int(todo.get("remind_count", 0)) + 1
            todo["snooze_until"] = ""
            todo["updated_at"] = todo["last_reminded_at"]
            changed = todo
            break
    return updated, changed


def fresh_distribution_todos() -> dict[str, Any]:
    return {"version": 1, "items": [], "updated_at": ""}
