from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

MODULAR_ROOT = Path(__file__).resolve().parents[1]
if str(MODULAR_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULAR_ROOT))

from core.ai_providers import (  # noqa: E402
    active_ai_provider,
    ai_endpoint_url,
    load_ai_providers,
    safe_ai_provider_export_config,
    update_ai_provider_field,
)
from core.reminder_history import log_todo_event, timeline_text  # noqa: E402
from core.todos import (  # noqa: E402
    add_todo,
    build_local_todo_lookup_reply,
    complete_todo,
    create_todo_from_chat_if_needed,
    due_todos,
    extract_todo_request_from_chat,
    is_todo_lookup_query,
    normalize_todos_state,
    todo_stats,
)


class Phase2CoreTests(unittest.TestCase):
    def test_ai_provider_load_normalize_and_export_redacts_keys(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "danhuang-ai-providers.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "active_provider": "deepseek",
                        "providers": {
                            "deepseek": {
                                "display_name": "DeepSeek",
                                "api_format": "bad",
                                "base_url": "https://api.deepseek.com/v1",
                                "model": "deepseek-v4-flash",
                                "env_key": "bad key",
                                "encrypted_api_key": "local-placeholder",
                            }
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            state = load_ai_providers(root)

        provider_id, provider = active_ai_provider(state)
        self.assertEqual(provider_id, "deepseek")
        self.assertEqual(provider["api_format"], "chat_completions")
        self.assertTrue(provider["encrypted_api_key"])
        self.assertEqual(ai_endpoint_url(provider), "https://api.deepseek.com/v1/chat/completions")
        exported = safe_ai_provider_export_config(state)
        self.assertEqual(exported["providers"]["deepseek"]["encrypted_api_key"], "")
        self.assertEqual(exported["providers"]["deepseek"]["env_key"], "DEEPSEEK_API_KEY")

    def test_ai_provider_update_cannot_touch_encrypted_key(self) -> None:
        state = load_ai_providers(Path("missing-dir"))
        updated = update_ai_provider_field(state, "openai", "encrypted_api_key", "local-placeholder")
        self.assertEqual(updated["providers"]["openai"]["encrypted_api_key"], "")
        updated = update_ai_provider_field(updated, "openai", "model", "gpt-5.4")
        self.assertEqual(updated["providers"]["openai"]["model"], "gpt-5.4")

    def test_todo_lookup_query_is_not_misread_as_create(self) -> None:
        now = datetime(2026, 6, 18, 10, 0)
        self.assertTrue(is_todo_lookup_query("提醒我今天待办有哪些", now=now))
        self.assertIsNone(extract_todo_request_from_chat("提醒我今天待办有哪些", now=now))
        payload = extract_todo_request_from_chat("提醒我明天9点开会", now=now)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["title"], "开会")
        self.assertEqual(payload["due_text"], "明天 09:00")

    def test_todo_create_complete_repeat_and_due_filter(self) -> None:
        now = datetime(2026, 6, 18, 10, 0)
        state, todo = add_todo(
            normalize_todos_state(None),
            "写重构计划",
            "今天 11:00",
            "工作",
            "重要",
            "daily",
            now=now,
            id_factory=lambda: "todo-1",
        )
        self.assertEqual(todo["due_at"], "2026-06-18T11:00")
        self.assertEqual(todo_stats(state, now=now), {"open": 1, "done": 0, "today": 1, "overdue": 0, "important": 1})
        self.assertEqual(due_todos(state, now=now), [])
        self.assertEqual([item["id"] for item in due_todos(state, now=now + timedelta(hours=2))], ["todo-1"])
        completed_state, completed = complete_todo(state, "todo-1", now=now + timedelta(hours=2))
        self.assertIsNotNone(completed)
        self.assertEqual(todo_stats(completed_state, now=now + timedelta(hours=2))["done"], 1)
        self.assertEqual(len(completed_state["items"]), 2)
        self.assertEqual(completed_state["items"][1]["due_at"], "2026-06-19T11:00")

    def test_create_todo_from_chat_and_lookup_reply(self) -> None:
        now = datetime(2026, 6, 18, 10, 0)
        state, todo = create_todo_from_chat_if_needed(
            normalize_todos_state(None),
            "帮我记一下今天18点发布视频，重要",
            now=now,
            id_factory=lambda: "todo-chat",
        )
        self.assertIsNotNone(todo)
        self.assertEqual(todo["category"], "内容")
        self.assertEqual(todo["priority"], "重要")
        reply = build_local_todo_lookup_reply(state, "今天安排", now=now)
        self.assertIn("发布视频", reply)
        self.assertIn("总览", reply)

    def test_reminder_history_logs_caps_and_renders_timeline(self) -> None:
        history = {"version": "bad", "events": []}
        todo = {"id": "todo-1", "title": "写计划", "category": "工作", "priority": "普通", "due_at": "", "repeat": "none"}
        for index in range(505):
            history, _event = log_todo_event(history, todo, "remind", {"index": index}, now=datetime(2026, 6, 18, 10, 0) + timedelta(minutes=index))
        self.assertEqual(history["version"], 1)
        self.assertEqual(len(history["events"]), 500)
        text = timeline_text(history, limit=2)
        self.assertIn("提醒", text)
        self.assertIn("写计划", text)


if __name__ == "__main__":
    unittest.main()
