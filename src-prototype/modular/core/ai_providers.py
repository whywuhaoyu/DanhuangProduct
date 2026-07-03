"""AI provider configuration helpers for the Tk prototype split.

The module owns provider metadata, normalization, redaction, and endpoint
derivation. It deliberately does not decrypt or expose API keys.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping

AI_PROVIDERS_FILE = "danhuang-ai-providers.json"
PROTECTED_PROVIDER_FIELDS = {"encrypted_api_key"}

AI_PROVIDER_PRESETS: dict[str, dict[str, Any]] = {
    "openai": {
        "display_name": "OpenAI",
        "api_format": "responses",
        "base_url": "https://api.openai.com/v1/responses",
        "model": "gpt-5.4-mini",
        "default_model": "gpt-5.4-mini",
        "env_key": "OPENAI_API_KEY",
        "models": ["gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-4.1-mini", "gpt-4.1"],
        "provider_note": "通用办公、写作和轻量助手。",
        "model_recommendation": "日常陪聊和轻量办公推荐 gpt-5.4-mini；复杂写作或长文整理可选 gpt-5.4。",
        "diagnostic_hint": "OpenAI 使用 Responses API；Base URL 默认保持 /v1/responses，失败先检查 Key 和账户用量。",
        "quota_format": "console",
        "quota_console_url": "https://platform.openai.com/usage",
        "quota_note": "OpenAI 用量和余额需要到平台 Usage 页面查看。",
    },
    "deepseek": {
        "display_name": "DeepSeek",
        "api_format": "chat_completions",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-v4-flash",
        "default_model": "deepseek-v4-flash",
        "env_key": "DEEPSEEK_API_KEY",
        "models": ["deepseek-v4-flash", "deepseek-v4-pro", "deepseek-chat", "deepseek-reasoner"],
        "provider_note": "中文聊天、推理和代码问答。",
        "model_recommendation": "日常陪聊、办公和资料回答推荐 deepseek-v4-flash；复杂推理可切 deepseek-v4-pro。",
        "diagnostic_hint": "DeepSeek 走 OpenAI 兼容 Chat Completions；默认用 deepseek-v4-flash。",
        "quota_format": "deepseek_balance",
        "quota_console_url": "https://platform.deepseek.com/usage",
        "quota_note": "可通过官方余额接口查询账户余额。",
    },
    "kimi": {
        "display_name": "Kimi / Moonshot",
        "api_format": "chat_completions",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "kimi-k2.5",
        "default_model": "kimi-k2.5",
        "env_key": "MOONSHOT_API_KEY",
        "models": ["kimi-k2.5", "kimi-k2-turbo-preview", "kimi-k2-thinking-turbo", "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "provider_note": "长文本阅读、写作和资料整理。",
        "model_recommendation": "普通陪聊和办公推荐 kimi-k2.5；长文档整理可按上下文长度切 moonshot-v1-32k / 128k。",
        "diagnostic_hint": "Moonshot 使用 OpenAI 兼容接口；长上下文模型更慢，普通聊天优先 8k。",
        "quota_format": "console",
        "quota_console_url": "https://platform.moonshot.cn/console/account",
        "quota_note": "Moonshot 暂未接入通用余额接口，请到控制台查看。",
    },
    "zhipu": {
        "display_name": "智谱 GLM",
        "api_format": "chat_completions",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "default_model": "glm-4-flash",
        "env_key": "ZHIPU_API_KEY",
        "models": ["glm-4-flash", "glm-4-plus", "glm-4-air"],
        "provider_note": "中文办公、知识问答和轻量助手。",
        "model_recommendation": "轻量陪聊推荐 glm-4-flash；更复杂的中文办公和知识问答可选 glm-4-plus。",
        "diagnostic_hint": "智谱使用 OpenAI 兼容接口；失败先检查 base_url 是否保持到 /api/paas/v4。",
        "quota_format": "console",
        "quota_console_url": "https://bigmodel.cn/usercenter/proj-mgmt/apikeys",
        "quota_note": "智谱额度请到开放平台控制台查看。",
    },
    "xiaomi_mimo": {
        "display_name": "小米 MiMo",
        "api_format": "chat_completions",
        "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "model": "mimo-v2-omni",
        "default_model": "mimo-v2-omni",
        "env_key": "XIAOMI_API_KEY",
        "models": ["mimo-v2-omni", "mimo-v2-pro", "mimo-v2.5-pro", "mimo-v2.5", "mimo-v2-flash"],
        "provider_note": "当前桌宠陪聊默认厂商，OpenAI 兼容接口。",
        "model_recommendation": "陪聊推荐 mimo-v2-omni；如果响应不完整或太慢，可切 mimo-v2-pro。",
        "diagnostic_hint": "小米 MiMo 的 Base URL 是 API 地址，不是网页控制台；控制台请用 plan-manage 地址。",
        "quota_format": "console",
        "quota_console_url": "https://platform.xiaomimimo.com/console/plan-manage",
        "quota_note": "小米 MiMo / Token Plan 暂未公开通用余额接口，请到控制台查看。",
    },
    "gemini": {
        "display_name": "Google Gemini",
        "api_format": "chat_completions",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash",
        "default_model": "gemini-2.5-flash",
        "env_key": "GEMINI_API_KEY",
        "models": ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest", "gemini-2.0-flash-lite"],
        "provider_note": "资料整理、多模态和办公辅助。",
        "model_recommendation": "资料整理和办公推荐 gemini-2.5-flash；复杂分析可选 gemini-2.5-pro。",
        "diagnostic_hint": "Gemini 通过 OpenAI 兼容入口调用；失败先检查 Google AI Studio Key 和项目权限。",
        "quota_format": "console",
        "quota_console_url": "https://aistudio.google.com/app/apikey",
        "quota_note": "Gemini 额度按 Google AI Studio / Cloud 项目查看。",
    },
    "qwen": {
        "display_name": "通义千问 Qwen",
        "api_format": "chat_completions",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "default_model": "qwen-plus",
        "env_key": "DASHSCOPE_API_KEY",
        "models": ["qwen3-max", "qwen3-max-preview", "qwen-max-latest", "qwen-plus", "qwen-plus-latest", "qwen-flash", "qwen-turbo", "qwen-long", "qwen3-coder-plus", "qwen3-coder-flash"],
        "provider_note": "中文办公、长文写作和代码辅助。",
        "model_recommendation": "中文办公推荐 qwen-plus 或 qwen-plus-latest；快速陪聊可选 qwen-flash。",
        "diagnostic_hint": "通义走百炼 OpenAI 兼容模式；Base URL 默认保持 compatible-mode/v1。",
        "quota_format": "console",
        "quota_console_url": "https://bailian.console.aliyun.com/",
        "quota_note": "DashScope 额度请到阿里云百炼控制台查看。",
    },
    "openrouter": {
        "display_name": "OpenRouter",
        "api_format": "chat_completions",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openrouter/auto",
        "default_model": "openrouter/auto",
        "env_key": "OPENROUTER_API_KEY",
        "models": ["openrouter/auto", "anthropic/claude-sonnet-4.5", "openai/gpt-5.1", "google/gemini-3-flash-preview", "deepseek/deepseek-v3.2"],
        "provider_note": "多模型路由，适合对比不同聊天模型。",
        "model_recommendation": "不确定模型时用 openrouter/auto；需要稳定质量时手动选择对应大模型。",
        "diagnostic_hint": "OpenRouter 需要模型 ID 带 provider 前缀；失败时先切 openrouter/auto 排查。",
        "quota_format": "openrouter_credits",
        "quota_console_url": "https://openrouter.ai/settings/credits",
        "quota_note": "可通过 OpenRouter credits 接口查询余额。",
    },
    "mistral": {
        "display_name": "Mistral",
        "api_format": "chat_completions",
        "base_url": "https://api.mistral.ai/v1",
        "model": "mistral-small-latest",
        "default_model": "mistral-small-latest",
        "env_key": "MISTRAL_API_KEY",
        "models": ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"],
        "provider_note": "英文/多语言办公和通用助手。",
        "model_recommendation": "日常聊天和轻量办公推荐 mistral-small-latest；复杂任务再切 medium / large。",
        "diagnostic_hint": "Mistral 使用 OpenAI 兼容 Chat Completions；普通陪聊优先 small。",
        "quota_format": "console",
        "quota_console_url": "https://console.mistral.ai/usage/",
        "quota_note": "Mistral 额度请到 Console 查看。",
    },
    "groq": {
        "display_name": "Groq",
        "api_format": "chat_completions",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "default_model": "llama-3.3-70b-versatile",
        "env_key": "GROQ_API_KEY",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "provider_note": "低延迟聊天和轻量办公辅助。",
        "model_recommendation": "低延迟陪聊推荐 llama-3.1-8b-instant；质量优先可选 llama-3.3-70b-versatile。",
        "diagnostic_hint": "Groq 适合低延迟，若模型不可用请在控制台确认当前可用模型 ID。",
        "quota_format": "console",
        "quota_console_url": "https://console.groq.com/settings/billing",
        "quota_note": "Groq 额度请到控制台 Billing 查看。",
    },
    "custom": {
        "display_name": "OpenAI-Compatible 中转站",
        "api_format": "chat_completions",
        "base_url": "",
        "model": "",
        "default_model": "",
        "env_key": "DANHUANG_AI_API_KEY",
        "models": [],
        "provider_note": "适合自建网关或第三方 OpenAI 兼容中转。",
        "model_recommendation": "自定义中转请填写平台支持的聊天模型 ID。",
        "diagnostic_hint": "自定义中转必须确认 Base URL、模型名和 Key 三者匹配。",
        "quota_format": "console",
        "quota_console_url": "",
        "quota_note": "自定义中转无法自动查询额度，请到对应平台查看。",
    },
}


def providers_path(pet_dir_or_file: str | Path) -> Path:
    path = Path(pet_dir_or_file)
    return path if path.name == AI_PROVIDERS_FILE else path / AI_PROVIDERS_FILE


def merge_unique_texts(*groups: Any) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        values = group if isinstance(group, list) else [group]
        for value in values:
            text = str(value or "").strip()
            if text and text not in seen:
                result.append(text)
                seen.add(text)
    return result


def clone_ai_provider_presets() -> dict[str, dict[str, Any]]:
    providers = copy.deepcopy(AI_PROVIDER_PRESETS)
    for provider in providers.values():
        provider.setdefault("model_notes", {})
        provider.setdefault("use_cases", [])
        provider.setdefault("model_catalog", [])
        provider.setdefault("recommended_model", str(provider.get("default_model") or provider.get("model") or ""))
        provider.setdefault("model_source_url", "")
        provider.setdefault("model_source_checked_at", "")
        provider.setdefault("model_status", "bundled")
        provider.setdefault("enabled", True)
        provider.setdefault("encrypted_api_key", "")
    return providers


def _base_provider(provider_id: str) -> dict[str, Any]:
    if provider_id in AI_PROVIDER_PRESETS:
        return copy.deepcopy(AI_PROVIDER_PRESETS[provider_id])
    base = copy.deepcopy(AI_PROVIDER_PRESETS["custom"])
    base["display_name"] = provider_id
    base["env_key"] = ""
    return base


def normalize_ai_provider(provider_id: str, provider: Mapping[str, Any] | None) -> dict[str, Any]:
    base = _base_provider(provider_id)
    preset = copy.deepcopy(base)
    if isinstance(provider, Mapping):
        preset.update(provider)
        preset["models"] = merge_unique_texts(base.get("models", []), provider.get("models", []), [provider.get("model", "")])

    if preset.get("api_format") not in {"responses", "chat_completions"}:
        preset["api_format"] = "chat_completions"
    for key in (
        "display_name",
        "base_url",
        "model",
        "default_model",
        "env_key",
        "encrypted_api_key",
        "provider_note",
        "model_recommendation",
        "recommended_model",
        "model_source_url",
        "model_source_checked_at",
        "model_status",
        "diagnostic_hint",
        "quota_format",
        "quota_console_url",
        "quota_note",
    ):
        preset[key] = str(preset.get(key, "") or "")

    if not preset["recommended_model"]:
        preset["recommended_model"] = preset.get("default_model") or preset.get("model") or ""
    if not preset["default_model"] and preset["recommended_model"]:
        preset["default_model"] = preset["recommended_model"]
    if preset["recommended_model"] and preset["recommended_model"] not in preset.get("models", []):
        preset.setdefault("models", []).insert(0, preset["recommended_model"])
    if preset["model"] and preset["model"] not in preset.get("models", []):
        preset.setdefault("models", []).append(preset["model"])

    if not isinstance(preset.get("model_notes"), dict):
        preset["model_notes"] = {}
    preset["model_notes"] = {
        str(key): str(value)
        for key, value in preset["model_notes"].items()
        if str(key).strip() and str(value).strip()
    }
    if not isinstance(preset.get("use_cases"), list):
        preset["use_cases"] = []
    preset["use_cases"] = [str(item) for item in preset["use_cases"] if str(item).strip()]
    if not isinstance(preset.get("models"), list):
        preset["models"] = []
    preset["models"] = [str(item) for item in preset["models"] if str(item).strip()]

    clean_catalog: list[dict[str, str]] = []
    for item in preset.get("model_catalog", []) if isinstance(preset.get("model_catalog"), list) else []:
        if not isinstance(item, Mapping):
            continue
        model_id = str(item.get("id", "") or "").strip()
        if not model_id:
            continue
        clean_catalog.append(
            {
                "id": model_id,
                "label": str(item.get("label", model_id) or model_id),
                "status": str(item.get("status", "") or ""),
                "best_for": str(item.get("best_for", "") or ""),
            }
        )
    preset["model_catalog"] = clean_catalog
    preset["enabled"] = bool(preset.get("enabled", True))

    if provider_id == "xiaomi_mimo" and (
        "token-plan-cn.xiaomimimo.com" in preset.get("quota_console_url", "")
        or preset.get("quota_console_url") == "https://platform.xiaomimimo.com/token-plan"
    ):
        preset["quota_console_url"] = "https://platform.xiaomimimo.com/console/plan-manage"
    return preset


def normalize_ai_providers_state(raw: Mapping[str, Any] | None, legacy_settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    state = {
        "version": 1,
        "active_provider": "openai",
        "providers": clone_ai_provider_presets(),
    }
    if isinstance(raw, Mapping):
        if isinstance(raw.get("active_provider"), str):
            state["active_provider"] = raw["active_provider"]
        saved_providers = raw.get("providers", {})
        if isinstance(saved_providers, Mapping):
            for provider_id, provider in saved_providers.items():
                if isinstance(provider, Mapping):
                    base = state["providers"].get(str(provider_id), _base_provider(str(provider_id)))
                    base.update(provider)
                    state["providers"][str(provider_id)] = base
    elif isinstance(legacy_settings, Mapping):
        model = str(legacy_settings.get("ai_model", "") or "").strip()
        base_url = str(legacy_settings.get("ai_base_url", "") or "").strip()
        if model:
            state["providers"]["openai"]["model"] = model
        if base_url:
            state["providers"]["openai"]["base_url"] = base_url

    for provider_id in list(state["providers"]):
        state["providers"][provider_id] = normalize_ai_provider(provider_id, state["providers"][provider_id])
    if state["active_provider"] not in state["providers"]:
        state["active_provider"] = "openai"
    return state


def load_ai_providers(pet_dir_or_file: str | Path, legacy_settings: Mapping[str, Any] | None = None) -> dict[str, Any]:
    path = providers_path(pet_dir_or_file)
    raw: Mapping[str, Any] | None = None
    if path.exists():
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
            raw = saved if isinstance(saved, Mapping) else None
        except (OSError, ValueError, TypeError):
            raw = None
    return normalize_ai_providers_state(raw, legacy_settings=legacy_settings)


def save_ai_providers(pet_dir_or_file: str | Path, state: Mapping[str, Any]) -> dict[str, Any]:
    clean = normalize_ai_providers_state(state)
    path = providers_path(pet_dir_or_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    return clean


def active_provider_id(state: Mapping[str, Any]) -> str:
    provider_id = str(state.get("active_provider", "openai") or "openai")
    providers = state.get("providers") if isinstance(state.get("providers"), Mapping) else {}
    return provider_id if provider_id in providers else "openai"


def active_ai_provider(state: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    provider_id = active_provider_id(state)
    providers = state.get("providers") if isinstance(state.get("providers"), Mapping) else {}
    return provider_id, normalize_ai_provider(provider_id, providers.get(provider_id, {}))


def set_active_ai_provider(state: Mapping[str, Any], provider_id: str) -> dict[str, Any]:
    clean = normalize_ai_providers_state(state)
    if provider_id in clean.get("providers", {}):
        clean["active_provider"] = provider_id
    return clean


def update_ai_provider_field(state: Mapping[str, Any], provider_id: str, key: str, value: Any) -> dict[str, Any]:
    clean = normalize_ai_providers_state(state)
    if key in PROTECTED_PROVIDER_FIELDS:
        return clean
    provider = clean["providers"].get(provider_id)
    if provider is None:
        return clean
    provider[key] = str(value or "").strip()
    clean["providers"][provider_id] = normalize_ai_provider(provider_id, provider)
    return clean


def provider_model_name(provider: Mapping[str, Any]) -> str:
    models = provider.get("models", []) if isinstance(provider.get("models"), list) else []
    return str(provider.get("model") or provider.get("default_model") or provider.get("recommended_model") or (models[0] if models else "") or "")


def ai_endpoint_url(provider: Mapping[str, Any]) -> str:
    base_url = str(provider.get("base_url", "") or "").strip()
    if not base_url:
        return ""
    url = base_url.rstrip("/")
    if provider.get("api_format") == "responses":
        return url if url.endswith("/responses") else url + "/responses"
    return url if url.endswith("/chat/completions") else url + "/chat/completions"


def provider_has_saved_key(provider: Mapping[str, Any]) -> bool:
    return bool(str(provider.get("encrypted_api_key", "") or "").strip())


def provider_public_summary(provider_id: str, provider: Mapping[str, Any]) -> dict[str, Any]:
    clean = normalize_ai_provider(provider_id, provider)
    return {
        "id": provider_id,
        "display_name": clean["display_name"],
        "enabled": clean["enabled"],
        "api_format": clean["api_format"],
        "base_url": clean["base_url"],
        "model": provider_model_name(clean),
        "env_key": clean["env_key"],
        "has_saved_key": provider_has_saved_key(clean),
        "quota_format": clean["quota_format"],
    }


def safe_ai_provider_export_config(state: Mapping[str, Any]) -> dict[str, Any]:
    clean = normalize_ai_providers_state(state)
    providers = clean.get("providers", {})
    for provider_id, provider in list(providers.items()):
        normalized = normalize_ai_provider(provider_id, provider)
        normalized["encrypted_api_key"] = ""
        env_key = str(normalized.get("env_key", "") or "")
        if env_key and not re.fullmatch(r"[A-Z_][A-Z0-9_]*", env_key):
            normalized["env_key"] = AI_PROVIDER_PRESETS.get(provider_id, {}).get("env_key", "")
        providers[provider_id] = normalized
    active = str(clean.get("active_provider", "") or "openai")
    if active not in providers:
        active = "openai"
    return {"version": 1, "active_provider": active, "providers": providers}


def provider_quota_endpoint(provider_id: str, provider: Mapping[str, Any]) -> str:
    quota_format = str(provider.get("quota_format", "") or "")
    if quota_format == "deepseek_balance":
        base_url = str(provider.get("base_url", "") or "https://api.deepseek.com").strip().rstrip("/")
        base_url = re.sub(r"/v\d+$", "", base_url)
        return base_url + "/user/balance"
    if quota_format == "openrouter_credits":
        return "https://openrouter.ai/api/v1/credits"
    return ""


def format_provider_quota_response(provider_id: str, provider: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    quota_format = str(provider.get("quota_format", "") or "")
    if quota_format == "deepseek_balance":
        infos = data.get("balance_infos", []) if isinstance(data, Mapping) else []
        if isinstance(infos, list) and infos:
            parts: list[str] = []
            for item in infos:
                if not isinstance(item, Mapping):
                    continue
                currency = str(item.get("currency", "") or "").strip()
                total = item.get("total_balance", "")
                segment = f"{currency} {total}".strip()
                if segment:
                    parts.append(segment)
            if parts:
                return "额度：" + "；".join(parts)
    if quota_format == "openrouter_credits":
        payload = data.get("data", data) if isinstance(data, Mapping) else {}
        if isinstance(payload, Mapping):
            total = payload.get("total_credits", payload.get("credits"))
            usage = payload.get("total_usage", payload.get("usage"))
            if total is not None and usage is not None:
                try:
                    remain = float(total) - float(usage)
                    return f"额度：剩余 ${remain:.4f}，总额 ${float(total):.4f}，已用 ${float(usage):.4f}"
                except (TypeError, ValueError):
                    return f"额度：总额 {total}，已用 {usage}"
            if total is not None:
                return f"额度：{total}"
    return "额度接口已返回，但格式不在当前识别范围内。"
