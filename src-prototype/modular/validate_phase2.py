"""Read-only validation for Phase 2 AI provider, todo, and reminder modules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.ai_providers import active_ai_provider, load_ai_providers, provider_public_summary
from core.reminder_history import load_reminder_history, timeline_text
from core.todos import build_local_todo_lookup_reply, is_todo_lookup_query, load_todos, todo_stats


def default_pet_dir() -> Path:
    product_root = Path(__file__).resolve().parents[2]
    runtime = product_root / "data-dev" / "current-runtime" / "danhuang"
    if runtime.exists():
        return runtime
    return Path(__file__).resolve().parents[1] / "legacy-monolith"


def build_report(pet_dir: Path) -> dict[str, object]:
    providers = load_ai_providers(pet_dir)
    active_id, active_provider = active_ai_provider(providers)
    provider_summaries = [
        provider_public_summary(provider_id, provider)
        for provider_id, provider in providers.get("providers", {}).items()
    ]
    todos = load_todos(pet_dir)
    history = load_reminder_history(pet_dir)
    lookup_probe = "提醒我今天待办有哪些"
    return {
        "pet_dir": str(pet_dir),
        "ai": {
            "active_provider": active_id,
            "active_display_name": active_provider.get("display_name"),
            "provider_count": len(provider_summaries),
            "saved_key_count": sum(1 for item in provider_summaries if item["has_saved_key"]),
            "providers": provider_summaries,
        },
        "todos": {
            "item_count": len(todos.get("items", [])),
            "stats": todo_stats(todos),
            "lookup_probe_is_query": is_todo_lookup_query(lookup_probe),
            "lookup_probe_reply": build_local_todo_lookup_reply(todos, lookup_probe, limit=3),
        },
        "reminder_history": {
            "event_count": len(history.get("events", [])),
            "timeline_preview": timeline_text(history, limit=3),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Danhuang modular Phase 2 core loaders.")
    parser.add_argument("--pet-dir", type=Path, default=default_pet_dir(), help="Prototype/runtime data directory.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    report = build_report(args.pet_dir)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Phase 2 modular core validation passed.")
        print(f"pet_dir: {report['pet_dir']}")
        print(f"ai: {report['ai']['provider_count']} providers, active {report['ai']['active_provider']}")
        print(f"todos: {report['todos']['item_count']} items, stats {report['todos']['stats']}")
        print(f"reminder_history: {report['reminder_history']['event_count']} events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
