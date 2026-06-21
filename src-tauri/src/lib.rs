use base64::engine::general_purpose::STANDARD as BASE64;
use base64::Engine;
use chrono::{Datelike, Local, Timelike};
use regex::Regex;
use reqwest::blocking::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet};
use std::env;
use std::fs;
use std::path::{Component, Path, PathBuf};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tauri::menu::{Menu, MenuItem};
use tauri::tray::TrayIconBuilder;
use tauri::{AppHandle, Emitter, Manager};

const RUNTIME_DIR: &str = "data-dev/current-runtime/danhuang";
const FAMILY_PATH: &str = "data-dev/current-runtime/danhuang/danhuang-failed-identity-backup-20260521-140133/pet-family.json";
const SETTINGS_PATH: &str = "data-dev/current-runtime/danhuang/desktop-pet-settings.json";
const AI_PROVIDERS_PATH: &str = "data-dev/current-runtime/danhuang/danhuang-ai-providers.json";
const TODOS_PATH: &str = "data-dev/current-runtime/danhuang/danhuang-todos.json";
const REMINDER_HISTORY_PATH: &str =
    "data-dev/current-runtime/danhuang/danhuang-reminder-history.json";
const CHAT_MEMORY_PATH: &str = "data-dev/current-runtime/danhuang/danhuang-chat-memory.json";
const DIALOGUE_LIBRARY_PATH: &str =
    "data-dev/current-runtime/danhuang/danhuang-dialogue-library.json";
const SOUL_PROFILE_PATH: &str = "data-dev/current-runtime/danhuang/danhuang-soul-profile.md";
const MAX_ASSET_BYTES: u64 = 15 * 1024 * 1024;
const MAX_UPLOAD_IMAGE_BYTES: usize = 10 * 1024 * 1024;
const MAX_QUICK_MENU_ACTIONS: usize = 16;
const MAX_CHAT_MESSAGES: usize = 200;

#[derive(Debug, Deserialize, Serialize)]
struct PetFamilyFile {
    #[serde(default)]
    current_pet_id: String,
    #[serde(default)]
    pets: Vec<PetEntryFile>,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Deserialize, Serialize)]
struct PetEntryFile {
    #[serde(default)]
    id: String,
    #[serde(default)]
    display_name: String,
    #[serde(default)]
    species: String,
    #[serde(default)]
    status: String,
    #[serde(default)]
    spritesheet: String,
    #[serde(default)]
    identity_image: String,
    #[serde(default)]
    reference_images: Vec<String>,
    #[serde(default)]
    notes: String,
    #[serde(default)]
    action_pack_level: String,
    #[serde(default)]
    supported_actions: Vec<String>,
    #[serde(default)]
    extension_assets: Vec<ExtensionAssetFile>,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Deserialize, Serialize)]
struct ExtensionAssetFile {
    #[serde(default)]
    id: String,
    #[serde(default)]
    label: String,
    #[serde(default)]
    strip: String,
    #[serde(default)]
    frames: usize,
    #[serde(default)]
    durations: Vec<u64>,
}

#[derive(Debug, Deserialize, Serialize)]
struct RuntimeSettingsFile {
    #[serde(default)]
    current_pet_id: String,
    #[serde(default)]
    scale: Option<f64>,
    #[serde(default)]
    animation_speed: Option<f64>,
    #[serde(default)]
    always_on_top: Option<bool>,
    #[serde(default)]
    bubble_style: Option<String>,
    #[serde(default)]
    bubble_fill: Option<String>,
    #[serde(default)]
    bubble_outline: Option<String>,
    #[serde(default)]
    bubble_text: Option<String>,
    #[serde(default)]
    bubble_duration: Option<f64>,
    #[serde(default)]
    talk_enabled: Option<bool>,
    #[serde(default)]
    ai_enabled: Option<bool>,
    #[serde(default)]
    ai_timeout: Option<f64>,
    #[serde(default)]
    roam_enabled: Option<bool>,
    #[serde(default)]
    drag_sensitivity: Option<f64>,
    #[serde(default)]
    inertia: Option<f64>,
    #[serde(default)]
    roam_speed: Option<f64>,
    #[serde(default)]
    roam_distance: Option<f64>,
    #[serde(default)]
    roam_interval: Option<f64>,
    #[serde(default)]
    idle_action_interval: Option<f64>,
    #[serde(default)]
    talk_interval: Option<f64>,
    #[serde(default)]
    talk_after_interaction_delay: Option<f64>,
    #[serde(default)]
    roam_allow_center: Option<bool>,
    #[serde(default)]
    multi_monitor_roam: Option<bool>,
    #[serde(default)]
    primary_monitor_edge_only: Option<bool>,
    #[serde(default)]
    secondary_monitor_full_roam: Option<bool>,
    #[serde(default)]
    roam_current_monitor_only: Option<bool>,
    #[serde(default)]
    keep_on_screen: Option<bool>,
    #[serde(default)]
    lock_size_across_monitors: Option<bool>,
    #[serde(default)]
    quick_menu_actions: Vec<String>,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Deserialize)]
struct UpdateSettingsInput {
    #[serde(default)]
    scale: Option<f64>,
    #[serde(default)]
    animation_speed: Option<f64>,
    #[serde(default)]
    always_on_top: Option<bool>,
    #[serde(default)]
    bubble_style: Option<String>,
    #[serde(default)]
    bubble_fill: Option<String>,
    #[serde(default)]
    bubble_outline: Option<String>,
    #[serde(default)]
    bubble_text: Option<String>,
    #[serde(default)]
    bubble_duration: Option<f64>,
    #[serde(default)]
    talk_enabled: Option<bool>,
    #[serde(default)]
    roam_enabled: Option<bool>,
    #[serde(default)]
    drag_sensitivity: Option<f64>,
    #[serde(default)]
    inertia: Option<f64>,
    #[serde(default)]
    roam_speed: Option<f64>,
    #[serde(default)]
    roam_distance: Option<f64>,
    #[serde(default)]
    roam_interval: Option<f64>,
    #[serde(default)]
    idle_action_interval: Option<f64>,
    #[serde(default)]
    talk_interval: Option<f64>,
    #[serde(default)]
    talk_after_interaction_delay: Option<f64>,
    #[serde(default)]
    roam_allow_center: Option<bool>,
    #[serde(default)]
    multi_monitor_roam: Option<bool>,
    #[serde(default)]
    primary_monitor_edge_only: Option<bool>,
    #[serde(default)]
    secondary_monitor_full_roam: Option<bool>,
    #[serde(default)]
    roam_current_monitor_only: Option<bool>,
    #[serde(default)]
    keep_on_screen: Option<bool>,
    #[serde(default)]
    lock_size_across_monitors: Option<bool>,
}

#[derive(Debug, Deserialize)]
struct SwitchPetInput {
    pet_id: String,
}

#[derive(Debug, Deserialize)]
struct UpdatePetProfileInput {
    pet_id: String,
    display_name: String,
    #[serde(default)]
    species: String,
    #[serde(default)]
    notes: String,
}

#[derive(Debug, Deserialize)]
struct UploadPetImageInput {
    pet_id: String,
    kind: String,
    #[serde(default)]
    file_name: String,
    #[serde(default)]
    mime_type: String,
    data_base64: String,
}

#[derive(Debug, Deserialize)]
struct UploadPetActionStripInput {
    pet_id: String,
    action_id: String,
    label: String,
    frames: usize,
    #[serde(default)]
    durations: Vec<u64>,
    #[serde(default)]
    file_name: String,
    #[serde(default)]
    mime_type: String,
    data_base64: String,
}

#[derive(Debug, Deserialize)]
struct UpdateQuickMenuActionsInput {
    pet_id: String,
    #[serde(default)]
    action_ids: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct UpdateAiProviderStateInput {
    provider_id: String,
    #[serde(default)]
    enabled: Option<bool>,
    #[serde(default)]
    make_active: bool,
}

#[derive(Debug, Deserialize, Serialize)]
struct AiProvidersFile {
    #[serde(default = "default_version")]
    version: u32,
    #[serde(default)]
    active_provider: String,
    #[serde(default)]
    providers: HashMap<String, AiProviderFile>,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct AiProviderFile {
    #[serde(default)]
    display_name: String,
    #[serde(default)]
    api_format: String,
    #[serde(default)]
    base_url: String,
    #[serde(default)]
    model: String,
    #[serde(default)]
    default_model: String,
    #[serde(default)]
    env_key: String,
    #[serde(default)]
    enabled: bool,
    #[serde(default)]
    encrypted_api_key: String,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Deserialize, Serialize)]
struct ChatMemoryFile {
    #[serde(default = "default_version")]
    version: u32,
    #[serde(default)]
    messages: Vec<ChatMessageFile>,
    #[serde(default)]
    mood_counts: HashMap<String, i64>,
    #[serde(default)]
    learned_phrases: Vec<String>,
    #[serde(default)]
    reply_count: i64,
    #[serde(default)]
    last_mood: String,
    #[serde(default)]
    updated_at: String,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

impl Default for ChatMemoryFile {
    fn default() -> Self {
        Self {
            version: default_version(),
            messages: Vec::new(),
            mood_counts: HashMap::new(),
            learned_phrases: Vec::new(),
            reply_count: 0,
            last_mood: String::new(),
            updated_at: String::new(),
            extra: HashMap::new(),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct ChatMessageFile {
    #[serde(default)]
    time: String,
    #[serde(default)]
    user: String,
    #[serde(default)]
    mood: String,
    #[serde(default)]
    reply: String,
    #[serde(default)]
    source: String,
    #[serde(default)]
    memory_update: String,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Deserialize)]
struct DialogueLibraryFile {
    #[serde(default)]
    base: Vec<String>,
    #[serde(default)]
    moods: HashMap<String, Vec<String>>,
    #[serde(default)]
    care: HashMap<String, Vec<String>>,
}

#[derive(Debug, Serialize)]
struct ChatMessageSummary {
    id: String,
    time: String,
    user: String,
    mood: String,
    reply: String,
    source: String,
}

#[derive(Debug, Deserialize)]
struct SendChatMessageInput {
    text: String,
    #[serde(default)]
    role_style: String,
    #[serde(default)]
    now: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct TodosFile {
    #[serde(default = "default_version")]
    version: u32,
    #[serde(default)]
    items: Vec<TodoItemFile>,
    #[serde(default)]
    updated_at: String,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct TodoItemFile {
    #[serde(default)]
    id: String,
    #[serde(default)]
    title: String,
    #[serde(default)]
    note: String,
    #[serde(default)]
    category: String,
    #[serde(default)]
    status: String,
    #[serde(default)]
    priority: String,
    #[serde(default)]
    due_at: String,
    #[serde(default)]
    repeat: String,
    #[serde(default)]
    pinned: bool,
    #[serde(default)]
    important_interval_minutes: i64,
    #[serde(default)]
    snooze_until: String,
    #[serde(default)]
    created_at: String,
    #[serde(default)]
    updated_at: String,
    #[serde(default)]
    completed_at: String,
    #[serde(default)]
    deleted_at: String,
    #[serde(default)]
    last_reminded_at: String,
    #[serde(default)]
    remind_count: i64,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Deserialize, Serialize)]
struct ReminderHistoryFile {
    #[serde(default = "default_version")]
    version: u32,
    #[serde(default)]
    events: Vec<Value>,
    #[serde(default)]
    updated_at: String,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Serialize)]
struct TodoSummary {
    id: String,
    title: String,
    note: String,
    due_at: String,
    category: String,
    priority: String,
    repeat: String,
    status: String,
    pinned: bool,
    important_interval_minutes: i64,
    snooze_until: String,
    created_at: String,
    completed_at: String,
    last_reminded_at: String,
    updated_at: String,
    remind_count: i64,
}

#[derive(Debug, Deserialize)]
struct CreateTodoInput {
    title: String,
    #[serde(default)]
    due_at: String,
    #[serde(default)]
    category: String,
    #[serde(default)]
    priority: String,
    #[serde(default)]
    now: String,
}

#[derive(Debug, Deserialize)]
struct UpdateTodoInput {
    id: String,
    #[serde(default)]
    done: Option<bool>,
    #[serde(default)]
    pinned: Option<bool>,
    #[serde(default)]
    snooze_until: Option<String>,
    #[serde(default)]
    now: String,
}

#[derive(Debug, Deserialize)]
struct UpdateTodoDetailInput {
    id: String,
    title: String,
    #[serde(default)]
    due_at: String,
    #[serde(default)]
    category: String,
    #[serde(default)]
    priority: String,
    #[serde(default)]
    repeat: String,
    #[serde(default)]
    note: String,
    #[serde(default)]
    important_interval_minutes: Option<i64>,
    #[serde(default)]
    now: String,
}

#[derive(Debug, Deserialize)]
struct RecordTodoReminderInput {
    id: String,
    #[serde(default)]
    now: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct StoryFile {
    #[serde(default = "default_version")]
    version: u32,
    #[serde(default)]
    entries: Vec<StoryEntryFile>,
    #[serde(default)]
    prompt_summary: String,
    #[serde(default)]
    role_prompt: String,
    #[serde(default)]
    role_prompt_updated_at: String,
    #[serde(default)]
    summary_updated_at: String,
    #[serde(default)]
    summary_source: String,
    #[serde(default)]
    updated_at: String,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

impl Default for StoryFile {
    fn default() -> Self {
        Self {
            version: default_version(),
            entries: Vec::new(),
            prompt_summary: String::new(),
            role_prompt: String::new(),
            role_prompt_updated_at: String::new(),
            summary_updated_at: String::new(),
            summary_source: String::new(),
            updated_at: String::new(),
            extra: HashMap::new(),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct StoryEntryFile {
    #[serde(default)]
    id: String,
    #[serde(default)]
    #[serde(rename = "type")]
    entry_type: String,
    #[serde(default)]
    title: String,
    #[serde(default)]
    content: String,
    #[serde(default)]
    image_refs: Vec<String>,
    #[serde(default)]
    created_at: String,
    #[serde(default)]
    updated_at: String,
    #[serde(default)]
    pinned: bool,
    #[serde(flatten)]
    extra: HashMap<String, Value>,
}

#[derive(Debug, Deserialize)]
struct MemorySummaryFile {
    #[serde(default)]
    message_count: i64,
    #[serde(default)]
    mood_counts: HashMap<String, i64>,
    #[serde(default)]
    owner_profile: String,
    #[serde(default)]
    emotional_patterns: Vec<String>,
    #[serde(default)]
    preferences: Vec<String>,
    #[serde(default)]
    important_memories: Vec<String>,
    #[serde(default)]
    common_questions: Vec<String>,
    #[serde(default)]
    notes: Vec<String>,
    #[serde(default)]
    last_mood: String,
    #[serde(default)]
    updated_at: String,
}

#[derive(Debug, Serialize)]
struct StoryEntrySummary {
    id: String,
    entry_type: String,
    title: String,
    content: String,
    content_preview: String,
    created_at: String,
    updated_at: String,
    pinned: bool,
    image_count: usize,
}

#[derive(Debug, Serialize)]
struct MemorySummary {
    message_count: i64,
    mood_counts: HashMap<String, i64>,
    owner_profile: String,
    emotional_patterns: Vec<String>,
    preferences: Vec<String>,
    important_memories: Vec<String>,
    common_questions: Vec<String>,
    notes: Vec<String>,
    last_mood: String,
    updated_at: String,
}

#[derive(Debug, Serialize)]
struct PetStateSummary {
    pet_id: String,
    stories: Vec<StoryEntrySummary>,
    prompt_summary: String,
    role_prompt: String,
    summary_updated_at: String,
    summary_source: String,
    memory: Option<MemorySummary>,
}

#[derive(Debug, Deserialize)]
struct CreatePetStoryInput {
    title: String,
    content: String,
    #[serde(default)]
    entry_type: String,
    #[serde(default)]
    now: String,
}

#[derive(Debug, Deserialize)]
struct CompanionStateFile {
    #[serde(default)]
    xp: i64,
    #[serde(default)]
    level: i64,
    #[serde(default)]
    interactions: i64,
    #[serde(default)]
    talks: i64,
}

#[derive(Debug, Serialize)]
struct RuntimeSummary {
    runtime_available: bool,
    runtime_source: String,
    current_pet_id: String,
    pet_count: usize,
    ready_pet_count: usize,
    total_supported_actions: usize,
    total_extension_assets: usize,
    current_pet: Option<PetSummary>,
    pets: Vec<PetSummary>,
    settings: SafeSettingsSummary,
    features: FeatureSummary,
    checks: RuntimeChecks,
}

#[derive(Debug, Clone, Serialize)]
struct PetSummary {
    id: String,
    display_name: String,
    species: String,
    notes: String,
    status: String,
    action_pack_level: String,
    supported_action_count: usize,
    extension_action_count: usize,
    identity_asset: Option<String>,
    reference_assets: Vec<String>,
    spritesheet_asset: Option<String>,
    identity_available: bool,
    spritesheet_available: bool,
    actions: Vec<PetActionSummary>,
}

#[derive(Debug, Clone, Serialize)]
struct PetActionSummary {
    id: String,
    label: String,
    source: String,
    row: Option<usize>,
    frames: usize,
    durations: Vec<u64>,
    asset: Option<String>,
}

#[derive(Debug, Serialize)]
struct SafeSettingsSummary {
    scale: Option<f64>,
    animation_speed: Option<f64>,
    always_on_top: Option<bool>,
    bubble_style: Option<String>,
    bubble_fill: Option<String>,
    bubble_outline: Option<String>,
    bubble_text: Option<String>,
    bubble_duration: Option<f64>,
    talk_enabled: Option<bool>,
    roam_enabled: Option<bool>,
    drag_sensitivity: Option<f64>,
    inertia: Option<f64>,
    roam_speed: Option<f64>,
    roam_distance: Option<f64>,
    roam_interval: Option<f64>,
    idle_action_interval: Option<f64>,
    talk_interval: Option<f64>,
    talk_after_interaction_delay: Option<f64>,
    roam_allow_center: Option<bool>,
    multi_monitor_roam: Option<bool>,
    primary_monitor_edge_only: Option<bool>,
    secondary_monitor_full_roam: Option<bool>,
    roam_current_monitor_only: Option<bool>,
    keep_on_screen: Option<bool>,
    lock_size_across_monitors: Option<bool>,
    quick_menu_action_count: usize,
    quick_menu_actions: Vec<String>,
}

#[derive(Debug, Serialize)]
struct RuntimeChecks {
    settings_loaded: bool,
    family_loaded: bool,
    sensitive_fields_returned: bool,
    notes: Vec<String>,
}

#[derive(Debug, Serialize)]
struct FeatureSummary {
    providers: Vec<SafeProviderSummary>,
    active_provider: String,
    enabled_provider_count: usize,
    saved_key_provider_count: usize,
    todo_total: usize,
    todo_open_count: usize,
    todo_done_count: usize,
    todo_pinned_count: usize,
    reminder_event_count: usize,
    story_count: usize,
    memory_summary_available: bool,
    companion_level: Option<i64>,
    companion_xp: Option<i64>,
    companion_interactions: Option<i64>,
    companion_talks: Option<i64>,
}

#[derive(Debug, Serialize)]
struct SafeProviderSummary {
    id: String,
    display_name: String,
    model: String,
    enabled: bool,
    has_saved_key: bool,
}

#[derive(Debug, Serialize)]
struct RuntimeAsset {
    path: String,
    mime_type: String,
    data_url: String,
}

fn product_root() -> Result<PathBuf, String> {
    let mut candidates = Vec::new();

    if let Ok(current_dir) = std::env::current_dir() {
        candidates.push(current_dir);
    }

    if let Ok(manifest_dir) = std::env::var("CARGO_MANIFEST_DIR") {
        candidates.push(PathBuf::from(manifest_dir));
    }

    for candidate in candidates {
        let mut cursor = candidate.as_path();
        for _ in 0..8 {
            if cursor.join(RUNTIME_DIR).is_dir() {
                return Ok(cursor.to_path_buf());
            }
            match cursor.parent() {
                Some(parent) => cursor = parent,
                None => break,
            }
        }
    }

    Err("未找到 DanhuangProduct 产品根目录".to_string())
}

fn read_json_file<T: for<'de> Deserialize<'de>>(path: &Path) -> Result<T, String> {
    let raw =
        fs::read_to_string(path).map_err(|err| format!("读取失败 {}: {}", path.display(), err))?;
    serde_json::from_str(&raw).map_err(|err| format!("JSON 解析失败 {}: {}", path.display(), err))
}

fn read_optional_json_file<T: for<'de> Deserialize<'de>>(path: &Path) -> Option<T> {
    fs::read_to_string(path)
        .ok()
        .and_then(|raw| serde_json::from_str(&raw).ok())
}

fn write_json_file<T: Serialize>(path: &Path, value: &T) -> Result<(), String> {
    let raw = serde_json::to_string_pretty(value)
        .map_err(|err| format!("JSON 序列化失败 {}: {}", path.display(), err))?;
    fs::write(path, format!("{}\n", raw))
        .map_err(|err| format!("写入失败 {}: {}", path.display(), err))
}

fn default_version() -> u32 {
    1
}

impl Default for TodosFile {
    fn default() -> Self {
        Self {
            version: default_version(),
            items: Vec::new(),
            updated_at: String::new(),
            extra: HashMap::new(),
        }
    }
}

impl Default for ReminderHistoryFile {
    fn default() -> Self {
        Self {
            version: default_version(),
            events: Vec::new(),
            updated_at: String::new(),
            extra: HashMap::new(),
        }
    }
}

fn current_millis() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_millis())
        .unwrap_or(0)
}

fn runtime_file_path(root: &Path, relative_path: &str) -> Result<PathBuf, String> {
    let runtime_root = root
        .join(RUNTIME_DIR)
        .canonicalize()
        .map_err(|err| format!("运行镜像目录不可用: {}", err))?;
    let path = root.join(relative_path);
    let parent = path
        .parent()
        .ok_or_else(|| format!("文件路径无父目录: {}", path.display()))?;
    let parent_canonical = parent
        .canonicalize()
        .map_err(|err| format!("运行镜像文件目录不可用 {}: {}", parent.display(), err))?;

    if !parent_canonical.starts_with(&runtime_root) {
        return Err("文件路径越过运行镜像边界".to_string());
    }

    Ok(path)
}

fn current_pet_id_from_settings(root: &Path) -> Result<String, String> {
    let settings_path = runtime_file_path(root, SETTINGS_PATH)?;
    let settings: RuntimeSettingsFile = read_json_file(&settings_path)?;
    normalized_pet_id(&settings.current_pet_id)
}

fn pet_state_dir(root: &Path, pet_id: &str) -> Result<PathBuf, String> {
    let safe_pet_id = normalized_pet_id(pet_id)?;
    let runtime_root = root
        .join(RUNTIME_DIR)
        .canonicalize()
        .map_err(|err| format!("运行镜像目录不可用: {}", err))?;
    let state_root = runtime_root.join("pet-state");
    if !state_root.exists() {
        fs::create_dir_all(&state_root).map_err(|err| format!("无法创建宠物状态目录: {}", err))?;
    }
    let dir = state_root.join(safe_pet_id);
    if !dir.starts_with(&runtime_root) {
        return Err("宠物状态路径越过运行镜像边界".to_string());
    }
    Ok(dir)
}

fn read_todos_file(path: &Path) -> Result<TodosFile, String> {
    if !path.is_file() {
        return Ok(TodosFile::default());
    }
    read_json_file(path)
}

fn read_chat_memory_file(path: &Path) -> Result<ChatMemoryFile, String> {
    if !path.is_file() {
        return Ok(ChatMemoryFile::default());
    }
    read_json_file(path)
}

fn read_story_file(path: &Path) -> Result<StoryFile, String> {
    if !path.is_file() {
        return Ok(StoryFile::default());
    }
    read_json_file(path)
}

fn safe_settings_summary(settings: &RuntimeSettingsFile) -> SafeSettingsSummary {
    SafeSettingsSummary {
        scale: settings.scale,
        animation_speed: settings.animation_speed,
        always_on_top: settings.always_on_top,
        bubble_style: settings.bubble_style.clone(),
        bubble_fill: settings.bubble_fill.clone(),
        bubble_outline: settings.bubble_outline.clone(),
        bubble_text: settings.bubble_text.clone(),
        bubble_duration: settings.bubble_duration,
        talk_enabled: settings.talk_enabled,
        roam_enabled: settings.roam_enabled,
        drag_sensitivity: settings.drag_sensitivity,
        inertia: settings.inertia,
        roam_speed: settings.roam_speed,
        roam_distance: settings.roam_distance,
        roam_interval: settings.roam_interval,
        idle_action_interval: settings.idle_action_interval,
        talk_interval: settings.talk_interval,
        talk_after_interaction_delay: settings.talk_after_interaction_delay,
        roam_allow_center: settings.roam_allow_center,
        multi_monitor_roam: settings.multi_monitor_roam,
        primary_monitor_edge_only: settings.primary_monitor_edge_only,
        secondary_monitor_full_roam: settings.secondary_monitor_full_roam,
        roam_current_monitor_only: settings.roam_current_monitor_only,
        keep_on_screen: settings.keep_on_screen,
        lock_size_across_monitors: settings.lock_size_across_monitors,
        quick_menu_action_count: settings.quick_menu_actions.len(),
        quick_menu_actions: settings.quick_menu_actions.clone(),
    }
}

fn normalized_f64(value: f64, min: f64, max: f64, label: &str) -> Result<f64, String> {
    if !value.is_finite() {
        return Err(format!("{} 必须是有效数字", label));
    }
    Ok(value.max(min).min(max))
}

fn normalize_bubble_style(raw: &str) -> Result<String, String> {
    let value = raw.trim().to_ascii_lowercase();
    let allowed = [
        "cloud", "rounded", "comic", "minimal", "pixel", "thought", "note", "caption",
    ];

    if allowed.contains(&value.as_str()) {
        Ok(value)
    } else {
        Err("气泡样式不在白名单内".to_string())
    }
}

fn normalize_hex_color(raw: &str, label: &str) -> Result<String, String> {
    let value = raw.trim();
    if value.len() != 7 || !value.starts_with('#') {
        return Err(format!("{} 必须是 #RRGGBB 颜色值", label));
    }
    if !value[1..].chars().all(|ch| ch.is_ascii_hexdigit()) {
        return Err(format!("{} 包含非法颜色字符", label));
    }
    Ok(format!("#{}", value[1..].to_ascii_lowercase()))
}

fn normalized_pet_id(raw: &str) -> Result<String, String> {
    let value = raw.trim();
    if value.is_empty() {
        return Err("宠物 ID 不能为空".to_string());
    }
    if value.len() > 96 {
        return Err("宠物 ID 过长".to_string());
    }
    if !value
        .chars()
        .all(|ch| ch.is_ascii_alphanumeric() || ch == '-' || ch == '_')
    {
        return Err("宠物 ID 只能包含字母、数字、短横线和下划线".to_string());
    }
    Ok(value.to_string())
}

fn normalize_text(raw: &str, fallback: &str, max_chars: usize) -> String {
    let collapsed = raw.split_whitespace().collect::<Vec<_>>().join(" ");
    let value = if collapsed.is_empty() {
        fallback.to_string()
    } else {
        collapsed
    };
    value.chars().take(max_chars).collect()
}

fn normalize_multiline_text(raw: &str, max_chars: usize) -> String {
    raw.replace("\r\n", "\n")
        .replace('\r', "\n")
        .trim()
        .chars()
        .take(max_chars)
        .collect()
}

fn normalize_timestamp(raw: &str) -> String {
    let value = normalize_text(raw, "", 48);
    if value.is_empty() {
        current_millis().to_string()
    } else {
        value
    }
}

fn same_timestamp_minute(left: &str, right: &str) -> bool {
    let left_minute: String = left.chars().take(16).collect();
    let right_minute: String = right.chars().take(16).collect();
    !left_minute.is_empty() && left_minute == right_minute
}

fn normalize_priority(raw: &str) -> String {
    let trimmed = raw.trim();
    match trimmed {
        "重要" | "安全" | "普通" => trimmed.to_string(),
        _ => match trimmed.to_ascii_lowercase().as_str() {
            "important" => "重要".to_string(),
            "security" => "安全".to_string(),
            _ => "普通".to_string(),
        },
    }
}

fn normalize_repeat(raw: &str) -> String {
    let trimmed = raw.trim();
    match trimmed {
        "" | "none" | "单次" => "none".to_string(),
        "daily" | "每天" => "daily".to_string(),
        "weekly" | "每周" => "weekly".to_string(),
        "monthly" | "每月" => "monthly".to_string(),
        _ => normalize_text(trimmed, "none", 24),
    }
}

fn normalize_interval_minutes(value: Option<i64>) -> i64 {
    value.unwrap_or(0).clamp(0, 1440)
}

fn is_important_priority(priority: &str) -> bool {
    matches!(priority, "important" | "重要" | "security" | "安全")
}

fn todo_to_summary(item: &TodoItemFile) -> TodoSummary {
    TodoSummary {
        id: item.id.clone(),
        title: item.title.clone(),
        note: item.note.clone(),
        due_at: item.due_at.clone(),
        category: item.category.clone(),
        priority: item.priority.clone(),
        repeat: item.repeat.clone(),
        status: item.status.clone(),
        pinned: item.pinned,
        important_interval_minutes: item.important_interval_minutes,
        snooze_until: item.snooze_until.clone(),
        created_at: item.created_at.clone(),
        completed_at: item.completed_at.clone(),
        last_reminded_at: item.last_reminded_at.clone(),
        updated_at: item.updated_at.clone(),
        remind_count: item.remind_count,
    }
}

fn visible_todos(file: &TodosFile) -> Vec<TodoSummary> {
    file.items
        .iter()
        .filter(|item| item.status != "deleted" && item.deleted_at.is_empty())
        .map(todo_to_summary)
        .collect()
}

fn chat_to_summary(item: &ChatMessageFile, index: usize) -> ChatMessageSummary {
    ChatMessageSummary {
        id: format!("chat-{}-{}", item.time, index),
        time: item.time.clone(),
        user: item.user.clone(),
        mood: item.mood.clone(),
        reply: item.reply.clone(),
        source: if item.source.is_empty() {
            "local".to_string()
        } else {
            item.source.clone()
        },
    }
}

fn recent_chat_summaries(file: &ChatMemoryFile) -> Vec<ChatMessageSummary> {
    let start = file.messages.len().saturating_sub(30);
    file.messages
        .iter()
        .enumerate()
        .skip(start)
        .map(|(index, item)| chat_to_summary(item, index))
        .collect()
}

fn story_entry_to_summary(item: &StoryEntryFile) -> StoryEntrySummary {
    let content_preview = item.content.chars().take(120).collect::<String>();

    StoryEntrySummary {
        id: item.id.clone(),
        entry_type: if item.entry_type.is_empty() {
            "story".to_string()
        } else {
            item.entry_type.clone()
        },
        title: if item.title.is_empty() {
            "未命名故事".to_string()
        } else {
            item.title.clone()
        },
        content: item.content.clone(),
        content_preview,
        created_at: item.created_at.clone(),
        updated_at: item.updated_at.clone(),
        pinned: item.pinned,
        image_count: item.image_refs.len(),
    }
}

fn memory_summary_to_safe(file: MemorySummaryFile) -> MemorySummary {
    MemorySummary {
        message_count: file.message_count,
        mood_counts: file.mood_counts,
        owner_profile: file.owner_profile,
        emotional_patterns: file.emotional_patterns,
        preferences: file.preferences,
        important_memories: file.important_memories,
        common_questions: file.common_questions,
        notes: file.notes,
        last_mood: file.last_mood,
        updated_at: file.updated_at,
    }
}

fn classify_chat_mood(text: &str) -> String {
    let value = text.trim();
    if value.contains("想") || value.contains("思念") || value.contains("蛋黄") {
        return "miss".to_string();
    }
    if value.contains("累")
        || value.contains("困")
        || value.contains("休息")
        || value.contains("肩")
        || value.contains("眼睛")
    {
        return "tired".to_string();
    }
    if value.contains("难过")
        || value.contains("哭")
        || value.contains("伤心")
        || value.contains("疼")
    {
        return "sad".to_string();
    }
    if value.contains("急")
        || value.contains("压力")
        || value.contains("焦虑")
        || value.contains("烦")
    {
        return "stressed".to_string();
    }
    if value.contains("开心")
        || value.contains("完成")
        || value.contains("好耶")
        || value.contains("不错")
    {
        return "happy".to_string();
    }
    if value.contains("?") || value.contains("？") || value.contains("吗") {
        return "question".to_string();
    }
    "quiet".to_string()
}

fn local_chat_reply(root: &Path, mood: &str, reply_count: i64) -> String {
    let dialogue_path = root.join(DIALOGUE_LIBRARY_PATH);
    let library = read_optional_json_file::<DialogueLibraryFile>(&dialogue_path);
    let index = reply_count.max(0) as usize;

    if let Some(file) = library {
        if let Some(pool) = file.moods.get(mood) {
            if !pool.is_empty() {
                return pool[index % pool.len()].clone();
            }
        }

        if mood == "tired" {
            if let Some(pool) = file.care.get("rest") {
                if !pool.is_empty() {
                    return pool[index % pool.len()].clone();
                }
            }
        }

        if !file.base.is_empty() {
            return file.base[index % file.base.len()].clone();
        }
    }

    "我在这里，轻轻陪你一会儿。".to_string()
}

#[derive(Debug, Clone)]
struct ResearchItem {
    title: String,
    url: String,
    snippet: String,
    source: String,
}

#[derive(Debug, Clone)]
struct ResearchBundle {
    triggered: bool,
    query: String,
    context: String,
    local_reply: String,
}

fn contains_any(value: &str, terms: &[&str]) -> bool {
    terms.iter().any(|term| value.contains(term))
}

fn is_general_knowledge_query(text: &str) -> bool {
    let raw = text.trim();
    if raw.is_empty() {
        return false;
    }
    let normalized = raw.to_lowercase();
    let companion_terms = [
        "陪我",
        "想你",
        "摸摸",
        "抱抱",
        "安慰我",
        "我难过",
        "我累了",
        "压力大",
        "你是谁",
        "你叫什么",
        "你的名字",
        "你记得我吗",
    ];
    if contains_any(raw, &companion_terms) && raw.chars().count() <= 18 {
        return false;
    }

    let knowledge_terms = [
        "什么是",
        "是什么",
        "是谁",
        "谁是",
        "什么意思",
        "含义",
        "解释一下",
        "介绍一下",
        "为什么",
        "为啥",
        "原因",
        "原理",
        "怎么",
        "如何",
        "怎么办",
        "怎么做",
        "多少",
        "多少钱",
        "哪年",
        "什么时候",
        "哪里",
        "在哪",
        "哪个",
        "哪些",
        "有哪些",
        "区别",
        "差异",
        "对比",
        "排名",
        "榜单",
        "教程",
        "攻略",
    ];
    if contains_any(raw, &knowledge_terms) {
        return true;
    }
    if ["what ", "who ", "why ", "how ", "where ", "when ", "which "]
        .iter()
        .any(|prefix| normalized.starts_with(prefix))
    {
        return true;
    }
    (raw.ends_with('？') || raw.ends_with('?')) && raw.chars().count() >= 6
}

fn is_research_query(text: &str) -> bool {
    let raw = text.trim();
    if raw.is_empty() {
        return false;
    }
    let lowered = raw.to_lowercase();
    let terms = [
        "帮我查",
        "查一下",
        "查下",
        "查查",
        "查询",
        "搜索",
        "搜一下",
        "搜下",
        "搜搜",
        "上网查",
        "联网查",
        "网上查",
        "网页",
        "百度",
        "谷歌",
        "google",
        "找资料",
        "查资料",
        "资料",
        "实时",
        "最近",
        "最新",
        "新闻",
        "资讯",
        "热搜",
        "天气",
        "股价",
        "汇率",
        "今日",
        "今天发生",
        "往年今日",
        "历史上的今天",
        "百科",
        "来源",
        "依据",
        "latest",
        "news",
    ];
    contains_any(&lowered, &terms)
        || Regex::new(r"(20\d{2}|19\d{2}).*(发生|事件|新闻|资料)")
            .map(|re| re.is_match(raw))
            .unwrap_or(false)
        || is_general_knowledge_query(raw)
}

fn is_recency_research_query(text: &str) -> bool {
    let raw = text.trim().to_lowercase();
    if raw.is_empty() {
        return false;
    }
    contains_any(
        &raw,
        &[
            "实时",
            "最近",
            "最新",
            "新闻",
            "资讯",
            "热搜",
            "今天",
            "今日",
            "现在",
            "天气",
            "股价",
            "汇率",
            "价格",
            "多少钱",
            "2026",
            "2025",
            "this week",
            "today",
            "latest",
            "news",
        ],
    )
}

fn is_time_query(text: &str) -> bool {
    let raw = text.trim();
    if raw.is_empty() {
        return false;
    }
    let patterns = [
        r"(现在|当前|此刻).*(几点|时间)",
        r"(今天|现在|当前).*(几号|日期|星期几|周几)",
        r"(几点了|几点钟|获取时间|报个时|看下时间|看一下时间)",
        r"^(时间|日期|今天几号|星期几|周几)$",
    ];
    patterns.iter().any(|pattern| {
        Regex::new(pattern)
            .map(|re| re.is_match(raw))
            .unwrap_or(false)
    })
}

fn local_time_reply(text: &str) -> String {
    if !is_time_query(text) {
        return String::new();
    }
    let now = Local::now();
    let weekdays = ["一", "二", "三", "四", "五", "六", "日"];
    let weekday = weekdays
        .get(now.weekday().num_days_from_monday() as usize)
        .copied()
        .unwrap_or("");
    let date_text = format!("{}年{:02}月{:02}日", now.year(), now.month(), now.day());
    let time_text = format!("{:02}:{:02}", now.hour(), now.minute());
    if contains_any(text, &["几点", "时间", "报个时", "几点钟"]) {
        format!(
            "主人，现在是 {} {}，星期{}。我在旁边陪着你。",
            date_text, time_text, weekday
        )
    } else {
        format!("主人，今天是 {}，星期{}。", date_text, weekday)
    }
}

fn regex_replace_all(input: &str, pattern: &str, replacement: &str) -> String {
    Regex::new(pattern)
        .map(|re| re.replace_all(input, replacement).to_string())
        .unwrap_or_else(|_| input.to_string())
}

fn research_query_from_user_text(text: &str) -> String {
    let raw = text.split_whitespace().collect::<Vec<_>>().join(" ");
    if raw.is_empty() {
        return raw;
    }
    if contains_any(
        &raw,
        &[
            "往年今日",
            "历史上的今天",
            "今日的事件",
            "今天发生过",
            "今天发生的事件",
        ],
    ) {
        return "历史上的今天 事件".to_string();
    }

    let mut query = raw.clone();
    query = regex_replace_all(
        &query,
        r"^(主人)?(你可以|可以|能不能|能|帮我|麻烦你|请你|请)?",
        "",
    )
    .trim()
    .to_string();
    query = regex_replace_all(
        &query,
        r"^(你知道|知道|告诉我|给我讲讲|讲讲|解释一下|介绍一下|说说|请问)",
        "",
    )
    .trim()
    .to_string();
    query = regex_replace_all(&query, r"^(什么是|什么叫|啥是|谁是|哪位是)", "")
        .trim()
        .to_string();
    query = regex_replace_all(
        &query,
        r"(.+?)(是什么|是谁|什么意思|是什么东西)[吗嘛呢？?。！!]*$",
        "$1",
    )
    .trim()
    .to_string();
    query = regex_replace_all(
        &query,
        r"(帮我)?(上网查一下|上网查|联网查一下|联网查|网上查一下|网上查|查一下|查下|查查|查询|搜索|搜一下|搜下|搜搜|找一下|找找|查资料)",
        "",
    )
    .trim()
    .to_string();
    query = regex_replace_all(&query, r"[吗嘛呢？?。！!]+$", "")
        .trim()
        .to_string();
    if query.is_empty() {
        raw
    } else {
        query
    }
}

fn percent_encode_query(value: &str) -> String {
    let mut output = String::new();
    for byte in value.as_bytes() {
        match *byte {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                output.push(*byte as char)
            }
            b' ' => output.push('+'),
            _ => output.push_str(&format!("%{:02X}", byte)),
        }
    }
    output
}

fn percent_decode(value: &str) -> String {
    let mut output = Vec::new();
    let bytes = value.as_bytes();
    let mut index = 0;
    while index < bytes.len() {
        if bytes[index] == b'%' && index + 2 < bytes.len() {
            if let Ok(hex) = u8::from_str_radix(&value[index + 1..index + 3], 16) {
                output.push(hex);
                index += 3;
                continue;
            }
        }
        output.push(if bytes[index] == b'+' {
            b' '
        } else {
            bytes[index]
        });
        index += 1;
    }
    String::from_utf8_lossy(&output).to_string()
}

fn html_unescape_basic(value: &str) -> String {
    value
        .replace("&amp;", "&")
        .replace("&quot;", "\"")
        .replace("&#39;", "'")
        .replace("&apos;", "'")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&nbsp;", " ")
}

fn clean_web_text(text: &str, max_chars: usize) -> String {
    let mut value = html_unescape_basic(text);
    value = regex_replace_all(&value, r"(?is)<script[\s\S]*?</script>", " ");
    value = regex_replace_all(&value, r"(?is)<style[\s\S]*?</style>", " ");
    value = regex_replace_all(&value, r"(?is)<[^>]+>", " ");
    value = value.split_whitespace().collect::<Vec<_>>().join(" ");
    let mut trimmed = value.chars().take(max_chars).collect::<String>();
    if value.chars().count() > max_chars {
        trimmed.push_str("...");
    }
    trimmed
}

fn unwrap_duckduckgo_url(url: &str) -> String {
    let mut value = html_unescape_basic(url.trim());
    if value.starts_with("//") {
        value = format!("https:{}", value);
    }
    if value.contains("duckduckgo.com/l/") || value.starts_with("/l/") {
        if let Some(query) = value.split('?').nth(1) {
            for pair in query.split('&') {
                if let Some(encoded) = pair.strip_prefix("uddg=") {
                    return percent_decode(encoded);
                }
            }
        }
    }
    value
}

fn web_request_text(url: &str, timeout_secs: f64) -> Result<String, String> {
    let client = Client::builder()
        .timeout(Duration::from_secs_f64(timeout_secs.clamp(4.0, 18.0)))
        .user_agent("Mozilla/5.0 DanhuangDesktopPet/1.0")
        .build()
        .map_err(|_| "资料查询 HTTP 客户端初始化失败".to_string())?;
    let response = client
        .get(url)
        .header("Accept", "text/html,application/json;q=0.9,*/*;q=0.8")
        .header("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.6")
        .send()
        .map_err(|err| format!("资料查询请求失败: {}", err))?;
    let status = response.status();
    if !status.is_success() {
        return Err(format!("资料查询 HTTP {}", status.as_u16()));
    }
    response
        .text()
        .map_err(|_| "资料查询响应读取失败".to_string())
}

fn duckduckgo_search_results(query: &str, limit: usize) -> Vec<ResearchItem> {
    let url = format!(
        "https://lite.duckduckgo.com/lite/?q={}",
        percent_encode_query(query)
    );
    let Ok(body) = web_request_text(&url, 14.0) else {
        return Vec::new();
    };
    let link_re = match Regex::new(
        r#"(?is)<a[^>]*class=['"]result-link['"][^>]*href=['"]([^'"]+)['"][^>]*>(.*?)</a>"#,
    ) {
        Ok(re) => re,
        Err(_) => return Vec::new(),
    };
    let snippet_re =
        Regex::new(r#"(?is)<td[^>]*class=['"]result-snippet['"][^>]*>(.*?)</td>"#).ok();
    let mut results = Vec::new();
    for mat in link_re.captures_iter(&body) {
        let href = mat.get(1).map(|item| item.as_str()).unwrap_or_default();
        let title = clean_web_text(
            mat.get(2).map(|item| item.as_str()).unwrap_or_default(),
            120,
        );
        let tail = &body[mat.get(0).map(|item| item.end()).unwrap_or(0)..];
        let snippet = snippet_re
            .as_ref()
            .and_then(|re| re.captures(tail))
            .and_then(|cap| cap.get(1))
            .map(|item| clean_web_text(item.as_str(), 260))
            .unwrap_or_default();
        let url = unwrap_duckduckgo_url(href);
        if !title.is_empty() && !url.is_empty() {
            results.push(ResearchItem {
                title,
                url,
                snippet,
                source: "DuckDuckGo".to_string(),
            });
        }
        if results.len() >= limit {
            break;
        }
    }
    results
}

fn wikipedia_search_results(query: &str, limit: usize) -> Vec<ResearchItem> {
    let url = format!(
        "https://zh.wikipedia.org/w/api.php?action=opensearch&namespace=0&format=json&limit={}&search={}",
        limit.clamp(1, 5),
        percent_encode_query(query)
    );
    let Ok(body) = web_request_text(&url, 10.0) else {
        return Vec::new();
    };
    let Ok(value) = serde_json::from_str::<Value>(&body) else {
        return Vec::new();
    };
    let Some(items) = value.as_array() else {
        return Vec::new();
    };
    if items.len() < 4 {
        return Vec::new();
    }
    let titles = items
        .get(1)
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    let snippets = items
        .get(2)
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    let urls = items
        .get(3)
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    let mut results = Vec::new();
    for (index, title_value) in titles.iter().enumerate() {
        let title = title_value.as_str().unwrap_or_default().trim().to_string();
        let url = urls
            .get(index)
            .and_then(Value::as_str)
            .unwrap_or_default()
            .trim()
            .to_string();
        let snippet = clean_web_text(
            snippets
                .get(index)
                .and_then(Value::as_str)
                .unwrap_or_default(),
            260,
        );
        if !title.is_empty() && !url.is_empty() {
            results.push(ResearchItem {
                title,
                url,
                snippet,
                source: "中文维基百科".to_string(),
            });
        }
        if results.len() >= limit {
            break;
        }
    }
    results
}

fn wikipedia_summary_result(query: &str) -> Option<ResearchItem> {
    let mut candidates = vec![query.trim().to_string()];
    for item in wikipedia_search_results(query, 1) {
        if !item.title.trim().is_empty() && !candidates.contains(&item.title) {
            candidates.push(item.title);
        }
    }

    for title in candidates {
        if title.trim().is_empty() {
            continue;
        }
        let url = format!(
            "https://zh.wikipedia.org/api/rest_v1/page/summary/{}",
            percent_encode_query(&title.replace(' ', "_")).replace('+', "%20")
        );
        let Ok(body) = web_request_text(&url, 10.0) else {
            continue;
        };
        let Ok(value) = serde_json::from_str::<Value>(&body) else {
            continue;
        };
        if value.get("type").and_then(Value::as_str) == Some("disambiguation") {
            continue;
        }
        let snippet = clean_web_text(
            value
                .get("extract")
                .and_then(Value::as_str)
                .unwrap_or_default(),
            420,
        );
        let page_url = value
            .get("content_urls")
            .and_then(|urls| urls.get("desktop"))
            .and_then(|desktop| desktop.get("page"))
            .and_then(Value::as_str)
            .or_else(|| {
                value
                    .get("content_urls")
                    .and_then(|urls| urls.get("mobile"))
                    .and_then(|mobile| mobile.get("page"))
                    .and_then(Value::as_str)
            })
            .unwrap_or_default()
            .trim()
            .to_string();
        let title = value
            .get("title")
            .and_then(Value::as_str)
            .unwrap_or(&title)
            .trim()
            .to_string();
        if !title.is_empty() && !page_url.is_empty() && !snippet.is_empty() {
            return Some(ResearchItem {
                title,
                url: page_url,
                snippet,
                source: "中文维基摘要".to_string(),
            });
        }
    }
    None
}

fn merge_research_results(groups: Vec<Vec<ResearchItem>>, limit: usize) -> Vec<ResearchItem> {
    let mut merged = Vec::new();
    let mut seen = HashSet::new();
    for group in groups {
        for item in group {
            let key = if item.url.trim().is_empty() {
                item.title.to_lowercase()
            } else {
                item.url
                    .trim()
                    .trim_end_matches('/')
                    .to_lowercase()
                    .split('?')
                    .next()
                    .unwrap_or_default()
                    .to_string()
            };
            if key.is_empty() || seen.contains(&key) {
                continue;
            }
            seen.insert(key);
            merged.push(item);
            if merged.len() >= limit {
                return merged;
            }
        }
    }
    merged
}

fn web_search_results(query: &str, limit: usize) -> Vec<ResearchItem> {
    let mut wiki_summary = Vec::new();
    if !is_recency_research_query(query) {
        if let Some(summary) = wikipedia_summary_result(query) {
            wiki_summary.push(summary);
        }
    }
    let duckduckgo = duckduckgo_search_results(query, limit);
    let wiki = if is_general_knowledge_query(query) || duckduckgo.len() < limit.min(3) {
        wikipedia_search_results(query, 3)
    } else {
        Vec::new()
    };
    merge_research_results(vec![wiki_summary, duckduckgo, wiki], limit)
}

fn build_research_bundle(user_text: &str) -> ResearchBundle {
    if !is_research_query(user_text) {
        return ResearchBundle {
            triggered: false,
            query: String::new(),
            context: String::new(),
            local_reply: String::new(),
        };
    }

    let query = research_query_from_user_text(user_text);
    let results = web_search_results(&query, 5);
    if results.is_empty() {
        return ResearchBundle {
            triggered: true,
            query: query.clone(),
            context: format!(
                "【联网查询资料】\n搜索词：{}\n没有查到可用网页资料。请明确告诉主人没有查到，不要编造。",
                query
            ),
            local_reply: format!(
                "主人，我刚刚查了“{}”，但没拿到可用摘要。你换个更具体的说法，我再帮你查。",
                query
            ),
        };
    }

    let mut context_lines = vec![format!("【联网查询资料】\n搜索词：{}", query)];
    let mut reply_lines = vec![format!("主人，我先帮你查到这些：\n搜索词：{}", query)];
    for (index, item) in results.iter().enumerate() {
        context_lines.push(format!(
            "{}. [{}] {} | {}\n摘要：{}",
            index + 1,
            item.source,
            item.title,
            item.url,
            item.snippet
        ));
        if index < 3 {
            let detail = if item.snippet.trim().is_empty() {
                item.url.as_str()
            } else {
                item.snippet.as_str()
            };
            reply_lines.push(format!(
                "{}. [{}] {}：{}\n   {}",
                index + 1,
                item.source,
                item.title,
                detail,
                item.url
            ));
        }
    }
    reply_lines.push("资料来自网页摘要，重要结论我们再点来源确认一下。".to_string());

    ResearchBundle {
        triggered: true,
        query,
        context: compact_lines(context_lines, 5200),
        local_reply: compact_lines(reply_lines, 1100),
    }
}

fn ai_reply_refuses_research(reply: &str) -> bool {
    if reply.trim().is_empty() {
        return false;
    }
    let refusal_terms = [
        "不能查询",
        "无法查询",
        "不能搜索",
        "无法搜索",
        "不能联网",
        "无法联网",
        "不能访问互联网",
        "无法访问互联网",
        "不能浏览网页",
        "无法浏览网页",
        "没有实时",
        "无法实时",
        "不能实时",
        "我不能查",
        "我无法查",
    ];
    let source_terms = [
        "根据资料",
        "资料显示",
        "搜索结果",
        "查到",
        "来源",
        "网页",
        "结果里",
    ];
    contains_any(reply, &refusal_terms) && !contains_any(reply, &source_terms)
}

fn strip_code_fence(raw: &str) -> String {
    let mut value = raw.trim().to_string();
    if value.starts_with("```") {
        value = value
            .trim_start_matches("```json")
            .trim_start_matches("```")
            .trim()
            .to_string();
        if value.ends_with("```") {
            value = value.trim_end_matches("```").trim().to_string();
        }
    }
    value
}

fn normalize_visible_ai_reply(raw: &str, mood: &str) -> String {
    let mut value = strip_code_fence(raw)
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ");
    if value.is_empty() {
        value = local_default_reply(mood);
    }

    let banned = ["作为AI", "作为 AI", "语言模型", "AI模型", "我是程序"];
    if banned.iter().any(|term| value.contains(term)) {
        value = "主人，我在。你慢慢说，我听着。".to_string();
    }

    let mut trimmed = value.chars().take(260).collect::<String>();
    if !trimmed
        .chars()
        .take(24)
        .collect::<String>()
        .contains("主人")
        && trimmed.chars().count() <= 90
    {
        trimmed = format!("主人，{}", trimmed);
    }
    trimmed
}

fn local_default_reply(mood: &str) -> String {
    match mood {
        "miss" => "主人，我在这里，轻轻陪你一会儿。".to_string(),
        "tired" => "主人，先放松一下肩膀，我在旁边陪你。".to_string(),
        "sad" => "主人，难过也可以慢慢说，我听着。".to_string(),
        "stressed" => "主人，我们先把呼吸放慢一点，一件一件来。".to_string(),
        "happy" => "主人，做得好。我摇摇尾巴陪你高兴一下。".to_string(),
        _ => "主人，我在。你慢慢说。".to_string(),
    }
}

fn provider_model_name(provider: &AiProviderFile) -> String {
    let model = provider.model.trim();
    if !model.is_empty() {
        model.to_string()
    } else if !provider.default_model.trim().is_empty() {
        provider.default_model.trim().to_string()
    } else {
        "gpt-4.1-mini".to_string()
    }
}

fn provider_api_format(provider: &AiProviderFile) -> String {
    let value = provider.api_format.trim();
    if value == "responses" {
        "responses".to_string()
    } else {
        "chat_completions".to_string()
    }
}

fn provider_endpoint_url(provider: &AiProviderFile) -> Result<String, String> {
    let raw = provider.base_url.trim().trim_end_matches('/');
    if raw.is_empty() {
        return Err("当前 AI Provider 未配置 Base URL".to_string());
    }
    if provider_api_format(provider) == "responses" {
        Ok(raw.to_string())
    } else if raw.ends_with("/chat/completions") {
        Ok(raw.to_string())
    } else {
        Ok(format!("{}/chat/completions", raw))
    }
}

#[cfg(windows)]
fn dpapi_decrypt_text(value: &str) -> Result<String, String> {
    let value = value.trim();
    if value.is_empty() || !value.starts_with("dpapi:") {
        return Ok(String::new());
    }

    use std::ptr::null_mut;
    use std::slice;
    use winapi::um::dpapi::CryptUnprotectData;
    use winapi::um::winbase::LocalFree;
    use winapi::um::wincrypt::DATA_BLOB;

    let mut encrypted = BASE64
        .decode(value.trim_start_matches("dpapi:"))
        .map_err(|_| "DPAPI Key 数据不是合法 base64".to_string())?;
    let mut blob_in = DATA_BLOB {
        cbData: encrypted.len() as u32,
        pbData: encrypted.as_mut_ptr(),
    };
    let mut blob_out = DATA_BLOB {
        cbData: 0,
        pbData: null_mut(),
    };

    let ok = unsafe {
        CryptUnprotectData(
            &mut blob_in,
            null_mut(),
            null_mut(),
            null_mut(),
            null_mut(),
            0,
            &mut blob_out,
        )
    };
    if ok == 0 {
        return Err("Windows DPAPI 解密失败".to_string());
    }

    let bytes =
        unsafe { slice::from_raw_parts(blob_out.pbData, blob_out.cbData as usize).to_vec() };
    unsafe {
        LocalFree(blob_out.pbData.cast());
    }
    String::from_utf8(bytes).map_err(|_| "DPAPI Key 解密后不是 UTF-8".to_string())
}

#[cfg(not(windows))]
fn dpapi_decrypt_text(_value: &str) -> Result<String, String> {
    Ok(String::new())
}

fn provider_api_key(provider: &AiProviderFile) -> String {
    if let Ok(saved) = dpapi_decrypt_text(&provider.encrypted_api_key) {
        if !saved.trim().is_empty() {
            return saved.trim().to_string();
        }
    }

    let env_key = provider.env_key.trim();
    if env_key.is_empty() {
        String::new()
    } else {
        env::var(env_key).unwrap_or_default().trim().to_string()
    }
}

fn active_ai_provider(file: &AiProvidersFile) -> Option<(String, AiProviderFile)> {
    if let Some(provider) = file.providers.get(&file.active_provider) {
        return Some((file.active_provider.clone(), provider.clone()));
    }

    file.providers
        .iter()
        .find(|(_, provider)| provider.enabled)
        .map(|(id, provider)| (id.clone(), provider.clone()))
        .or_else(|| {
            file.providers
                .iter()
                .next()
                .map(|(id, provider)| (id.clone(), provider.clone()))
        })
}

fn current_pet_entry(root: &Path, pet_id: &str) -> Option<PetEntryFile> {
    let family_path = root.join(FAMILY_PATH);
    let family = read_optional_json_file::<PetFamilyFile>(&family_path)?;
    family.pets.into_iter().find(|pet| pet.id == pet_id)
}

fn compact_lines(lines: Vec<String>, max_chars: usize) -> String {
    let mut output = String::new();
    for line in lines {
        if line.trim().is_empty() {
            continue;
        }
        if output.len() + line.len() + 1 > max_chars {
            break;
        }
        if !output.is_empty() {
            output.push('\n');
        }
        output.push_str(line.trim());
    }
    output
}

fn todo_context_for_ai(root: &Path, limit: usize) -> String {
    let path = match runtime_file_path(root, TODOS_PATH) {
        Ok(path) => path,
        Err(_) => return "待办摘要不可用。".to_string(),
    };
    let file = read_todos_file(&path).unwrap_or_default();
    let visible = visible_todos(&file);
    let open = visible
        .iter()
        .filter(|todo| todo.status != "done" && todo.completed_at.is_empty())
        .collect::<Vec<_>>();
    let important = open
        .iter()
        .filter(|todo| is_important_priority(&todo.priority))
        .count();

    let mut lines = vec![format!("未完成 {} 项，重要 {} 项。", open.len(), important)];
    for todo in open.into_iter().take(limit) {
        let due = if todo.snooze_until.trim().is_empty() {
            todo.due_at.as_str()
        } else {
            todo.snooze_until.as_str()
        };
        let due = if due.trim().is_empty() {
            "无提醒"
        } else {
            due
        };
        lines.push(format!(
            "- {} | {} | {} | {}",
            todo.title, todo.category, todo.priority, due
        ));
    }
    compact_lines(lines, 900)
}

fn pet_story_context_for_ai(root: &Path, pet_id: &str, max_chars: usize) -> String {
    let state_dir = match pet_state_dir(root, pet_id) {
        Ok(dir) => dir,
        Err(_) => return String::new(),
    };
    let story_path = state_dir.join("pet-stories.json");
    let story_file = match read_story_file(&story_path) {
        Ok(file) => file,
        Err(_) => return String::new(),
    };

    if !story_file.prompt_summary.trim().is_empty() {
        return story_file
            .prompt_summary
            .chars()
            .take(max_chars)
            .collect::<String>();
    }

    let mut lines = Vec::new();
    for story in story_file.entries.iter().take(5) {
        let title = if story.title.trim().is_empty() {
            "未命名故事"
        } else {
            story.title.trim()
        };
        let content = story
            .content
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ");
        lines.push(format!("- {}：{}", title, content));
    }
    compact_lines(lines, max_chars)
}

fn memory_context_for_ai(root: &Path, pet_id: &str) -> String {
    let state_dir = match pet_state_dir(root, pet_id) {
        Ok(dir) => dir,
        Err(_) => return "暂无长期记忆摘要。".to_string(),
    };
    let memory_path = state_dir.join("memory-summary.json");
    let Some(memory) = read_optional_json_file::<MemorySummaryFile>(&memory_path) else {
        return "暂无长期记忆摘要。".to_string();
    };

    let value = json!({
        "message_count": memory.message_count,
        "last_mood": memory.last_mood,
        "owner_profile": memory.owner_profile,
        "emotional_patterns": memory.emotional_patterns.into_iter().take(8).collect::<Vec<_>>(),
        "preferences": memory.preferences.into_iter().take(8).collect::<Vec<_>>(),
        "important_memories": memory.important_memories.into_iter().take(10).collect::<Vec<_>>(),
        "common_questions": memory.common_questions.into_iter().take(8).collect::<Vec<_>>(),
        "notes": memory.notes.into_iter().take(8).collect::<Vec<_>>(),
        "mood_counts": memory.mood_counts,
    });
    serde_json::to_string(&value).unwrap_or_else(|_| "暂无长期记忆摘要。".to_string())
}

fn recent_conversation_for_ai(file: &ChatMemoryFile) -> String {
    let mut lines = Vec::new();
    let start = file.messages.len().saturating_sub(12);
    for item in file.messages.iter().skip(start) {
        if !item.user.trim().is_empty() {
            lines.push(format!("主人：{}", item.user.trim()));
        }
        if !item.reply.trim().is_empty() {
            lines.push(format!("桌宠：{}", item.reply.trim()));
        }
    }
    if lines.is_empty() {
        "暂无".to_string()
    } else {
        compact_lines(lines, 1800)
    }
}

fn build_ai_system_prompt(root: &Path, pet: Option<&PetEntryFile>) -> String {
    let pet_name = pet
        .map(|item| item.display_name.trim())
        .filter(|name| !name.is_empty())
        .unwrap_or("蛋黄");
    let soul_profile = fs::read_to_string(root.join(SOUL_PROFILE_PATH))
        .unwrap_or_else(|_| "你是安静、亲近、真诚的桌宠，称呼用户为主人。".to_string());

    format!(
        "你是桌宠“{}”，不是普通 AI 助手。\n\n【最高优先级身份】\n{}\n\n【角色边界】\n- 称呼用户为“主人”。\n- 回复默认短一点、亲近一点、真诚一点。\n- 不要说“作为 AI”“我是语言模型”“我只是程序”。\n- 不要假装真实复活，不要说自己真正拥有身体或现实感知。\n- 主人表达想念、难过、累、内疚时，优先陪伴和安慰。\n- 主人问今天安排、接下来做什么、有什么没做时，要结合本地待办摘要回答。\n\n只输出要给主人的自然中文回复，不要 JSON，不要 Markdown 代码块。",
        pet_name,
        soul_profile.trim()
    )
}

fn build_ai_user_prompt(
    root: &Path,
    pet_id: &str,
    pet: Option<&PetEntryFile>,
    file: &ChatMemoryFile,
    user_text: &str,
    mood: &str,
    research_context: &str,
) -> String {
    let pet_name = pet
        .map(|item| item.display_name.trim())
        .filter(|name| !name.is_empty())
        .unwrap_or("蛋黄");
    let pet_profile = pet
        .map(|item| {
            format!(
                "名字：{}\n种类：{}\n说明：{}",
                item.display_name, item.species, item.notes
            )
        })
        .unwrap_or_else(|| "暂无当前宠物档案。".to_string());

    format!(
        "【当前时间】\n{}\n\n【本地待办摘要】\n{}\n\n【联网查询资料】\n{}\n\n【当前宠物档案】\n{}\n\n【主人与{}的真实故事】\n{}\n\n【长期记忆摘要】\n{}\n\n【最近对话】\n{}\n\n【本地初判】mood={}\n【主人刚刚说】{}\n\n请以{}的身份自然回复给主人。只输出回复正文。主人问共同故事或回忆时，只能基于真实故事和长期记忆，不要编造。主人问资料时，如果上面有搜索资料，必须基于资料回答，不要说自己不能查询；资料不足就直说没查到。",
        current_millis(),
        todo_context_for_ai(root, 6),
        if research_context.trim().is_empty() {
            "本轮没有触发资料查询。"
        } else {
            research_context
        },
        pet_profile,
        pet_name,
        pet_story_context_for_ai(root, pet_id, 1600),
        memory_context_for_ai(root, pet_id),
        recent_conversation_for_ai(file),
        mood,
        user_text,
        pet_name
    )
}

fn extract_chat_completion_text(response: &Value) -> String {
    response
        .get("choices")
        .and_then(Value::as_array)
        .and_then(|choices| choices.first())
        .and_then(|choice| choice.get("message"))
        .and_then(|message| message.get("content"))
        .map(|content| {
            if let Some(text) = content.as_str() {
                text.to_string()
            } else if let Some(parts) = content.as_array() {
                parts
                    .iter()
                    .filter_map(|item| item.get("text").and_then(Value::as_str))
                    .collect::<Vec<_>>()
                    .join("\n")
            } else {
                String::new()
            }
        })
        .unwrap_or_default()
        .trim()
        .to_string()
}

fn extract_responses_text(response: &Value) -> String {
    if let Some(text) = response.get("output_text").and_then(Value::as_str) {
        if !text.trim().is_empty() {
            return text.trim().to_string();
        }
    }

    let mut parts = Vec::new();
    if let Some(output) = response.get("output").and_then(Value::as_array) {
        for item in output {
            if let Some(content) = item.get("content").and_then(Value::as_array) {
                for part in content {
                    if let Some(text) = part
                        .get("text")
                        .or_else(|| part.get("output_text"))
                        .and_then(Value::as_str)
                    {
                        parts.push(text);
                    }
                }
            }
        }
    }
    parts.join("\n").trim().to_string()
}

fn call_ai_reply(
    root: &Path,
    settings: &RuntimeSettingsFile,
    chat_file: &ChatMemoryFile,
    user_text: &str,
    mood: &str,
    research_context: &str,
) -> Result<(String, String), String> {
    if settings.ai_enabled == Some(false) {
        return Err("AI 已关闭".to_string());
    }

    let ai_path = runtime_file_path(root, AI_PROVIDERS_PATH)?;
    let ai_file: AiProvidersFile = read_json_file(&ai_path)?;
    let (provider_id, provider) =
        active_ai_provider(&ai_file).ok_or_else(|| "没有可用 AI Provider".to_string())?;
    if !provider.enabled {
        return Err(format!("{} 未启用", provider_id));
    }

    let api_key = provider_api_key(&provider);
    if api_key.is_empty() {
        return Err(format!("{} 未配置 API Key", provider_id));
    }

    let pet_id = current_pet_id_from_settings(root).unwrap_or_else(|_| "danhuang".to_string());
    let pet = current_pet_entry(root, &pet_id);
    let api_format = provider_api_format(&provider);
    let endpoint = provider_endpoint_url(&provider)?;
    let model = provider_model_name(&provider);
    let system_prompt = build_ai_system_prompt(root, pet.as_ref());
    let user_prompt = build_ai_user_prompt(
        root,
        &pet_id,
        pet.as_ref(),
        chat_file,
        user_text,
        mood,
        research_context,
    );
    let payload = if api_format == "responses" {
        json!({
            "model": model,
            "instructions": system_prompt,
            "input": user_prompt,
            "max_output_tokens": 900,
            "store": false
        })
    } else {
        json!({
            "model": model,
            "messages": [
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": user_prompt }
            ],
            "temperature": 0.55,
            "max_tokens": 900,
            "stream": false
        })
    };

    let timeout_seconds = settings.ai_timeout.unwrap_or(90.0).clamp(8.0, 180.0);
    let client = Client::builder()
        .timeout(Duration::from_secs_f64(timeout_seconds))
        .build()
        .map_err(|_| "AI HTTP 客户端初始化失败".to_string())?;
    let response = client
        .post(endpoint)
        .bearer_auth(api_key)
        .header("Content-Type", "application/json")
        .json(&payload)
        .send()
        .map_err(|err| format!("AI 请求失败: {}", err))?;
    let status = response.status();
    let body = response.text().map_err(|_| "AI 响应读取失败".to_string())?;
    if !status.is_success() {
        let detail: String = body.chars().take(160).collect();
        return Err(format!("AI HTTP {}: {}", status.as_u16(), detail));
    }

    let value: Value =
        serde_json::from_str(&body).map_err(|_| "AI 响应不是合法 JSON".to_string())?;
    let raw = if api_format == "responses" {
        extract_responses_text(&value)
    } else {
        extract_chat_completion_text(&value)
    };
    if raw.trim().is_empty() {
        return Err("AI 回复为空".to_string());
    }
    let visible = normalize_visible_ai_reply(&raw, mood);
    if !research_context.trim().is_empty() && ai_reply_refuses_research(&visible) {
        return Err("AI 未使用已检索资料".to_string());
    }

    Ok((
        visible,
        if research_context.trim().is_empty() {
            format!("ai:{}", provider_id)
        } else {
            format!("ai-research:{}", provider_id)
        },
    ))
}

fn append_reminder_event(
    root: &Path,
    event_type: &str,
    item: &TodoItemFile,
    now: &str,
) -> Result<(), String> {
    let path = runtime_file_path(root, REMINDER_HISTORY_PATH)?;
    let mut history = if path.is_file() {
        read_json_file::<ReminderHistoryFile>(&path)?
    } else {
        ReminderHistoryFile::default()
    };

    history.events.push(json!({
        "time": now,
        "type": event_type,
        "todo_id": item.id,
        "title": item.title,
        "category": item.category,
        "priority": item.priority,
        "due_at": item.due_at,
        "repeat": item.repeat,
    }));
    history.updated_at = now.to_string();
    write_json_file(&path, &history)
}

fn feature_summary(root: &Path, current_pet_id: &str) -> FeatureSummary {
    let ai_path = root.join(AI_PROVIDERS_PATH);
    let todos_path = root.join(TODOS_PATH);
    let reminder_path = root.join(REMINDER_HISTORY_PATH);
    let pet_state_root = root
        .join(RUNTIME_DIR)
        .join("pet-state")
        .join(current_pet_id);
    let story_path = pet_state_root.join("pet-stories.json");
    let memory_summary_path = pet_state_root.join("memory-summary.json");
    let companion_state_path = pet_state_root.join("companion-state.json");

    let ai = read_optional_json_file::<AiProvidersFile>(&ai_path);
    let mut providers = ai
        .as_ref()
        .map(|file| {
            let mut items: Vec<SafeProviderSummary> = file
                .providers
                .iter()
                .map(|(id, provider)| SafeProviderSummary {
                    id: id.clone(),
                    display_name: if provider.display_name.is_empty() {
                        id.clone()
                    } else {
                        provider.display_name.clone()
                    },
                    model: if provider.model.is_empty() {
                        provider.default_model.clone()
                    } else {
                        provider.model.clone()
                    },
                    enabled: provider.enabled,
                    has_saved_key: !provider.encrypted_api_key.is_empty(),
                })
                .collect();
            items.sort_by(|a, b| a.id.cmp(&b.id));
            items
        })
        .unwrap_or_default();

    let active_provider = ai
        .as_ref()
        .map(|file| file.active_provider.clone())
        .unwrap_or_default();
    let enabled_provider_count = providers.iter().filter(|provider| provider.enabled).count();
    let saved_key_provider_count = providers
        .iter()
        .filter(|provider| provider.has_saved_key)
        .count();

    let todos = read_optional_json_file::<TodosFile>(&todos_path);
    let todo_total = todos.as_ref().map(|file| file.items.len()).unwrap_or(0);
    let todo_open_count = todos
        .as_ref()
        .map(|file| {
            file.items
                .iter()
                .filter(|item| item.status != "done" && item.status != "deleted")
                .count()
        })
        .unwrap_or(0);
    let todo_done_count = todos
        .as_ref()
        .map(|file| {
            file.items
                .iter()
                .filter(|item| item.status == "done")
                .count()
        })
        .unwrap_or(0);
    let todo_pinned_count = todos
        .as_ref()
        .map(|file| {
            file.items
                .iter()
                .filter(|item| item.pinned || is_important_priority(&item.priority))
                .count()
        })
        .unwrap_or(0);

    let reminder_event_count = read_optional_json_file::<ReminderHistoryFile>(&reminder_path)
        .map(|file| file.events.len())
        .unwrap_or(0);
    let story_count = read_optional_json_file::<StoryFile>(&story_path)
        .map(|file| file.entries.len())
        .unwrap_or(0);
    let companion = read_optional_json_file::<CompanionStateFile>(&companion_state_path);

    if providers.is_empty() {
        providers = Vec::new();
    }

    FeatureSummary {
        providers,
        active_provider,
        enabled_provider_count,
        saved_key_provider_count,
        todo_total,
        todo_open_count,
        todo_done_count,
        todo_pinned_count,
        reminder_event_count,
        story_count,
        memory_summary_available: memory_summary_path.is_file(),
        companion_level: companion.as_ref().map(|state| state.level),
        companion_xp: companion.as_ref().map(|state| state.xp),
        companion_interactions: companion.as_ref().map(|state| state.interactions),
        companion_talks: companion.as_ref().map(|state| state.talks),
    }
}

fn safe_asset_path(asset_path: &str) -> Result<String, String> {
    let normalized = asset_path.replace('\\', "/").trim().to_string();
    if normalized.is_empty() {
        return Err("资源路径为空".to_string());
    }
    if normalized.contains(':') || normalized.starts_with('/') || normalized.starts_with('~') {
        return Err("只允许运行镜像内的相对资源路径".to_string());
    }

    let path = Path::new(&normalized);
    if path.components().any(|part| {
        matches!(
            part,
            Component::ParentDir | Component::RootDir | Component::Prefix(_)
        )
    }) {
        return Err("资源路径不能包含上级目录或绝对路径".to_string());
    }

    let filename = path
        .file_name()
        .and_then(|name| name.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();
    let stem = path
        .file_stem()
        .and_then(|name| name.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();
    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();

    let allowed_extension = matches!(extension.as_str(), "png" | "jpg" | "jpeg" | "webp");
    let allowed_name = stem == "identity-base"
        || filename == "spritesheet.webp"
        || filename.starts_with("extension-");
    let allowed_root_sprite = normalized == "spritesheet.webp";
    let allowed_user_upload = normalized.starts_with("family/")
        && normalized.contains("/uploads/")
        && filename.starts_with("user-");
    let allowed_family_reference = normalized.starts_with("family-references/");

    if !allowed_extension
        || (!allowed_name
            && !allowed_root_sprite
            && !allowed_user_upload
            && !allowed_family_reference)
    {
        return Err("该资源不在前端预览白名单内".to_string());
    }

    Ok(normalized)
}

fn runtime_asset_write_path(root: &Path, asset_path: &str) -> Result<PathBuf, String> {
    let safe_path = safe_asset_path(asset_path)?;
    let runtime_root = root
        .join(RUNTIME_DIR)
        .canonicalize()
        .map_err(|err| format!("运行镜像目录不可用: {}", err))?;
    let target = runtime_root.join(&safe_path);
    let parent = target
        .parent()
        .ok_or_else(|| format!("资源路径无父目录: {}", target.display()))?;

    fs::create_dir_all(parent)
        .map_err(|err| format!("创建资源目录失败 {}: {}", parent.display(), err))?;
    let parent_canonical = parent
        .canonicalize()
        .map_err(|err| format!("资源目录不可用 {}: {}", parent.display(), err))?;
    if !parent_canonical.starts_with(&runtime_root) {
        return Err("资源路径越过运行镜像边界".to_string());
    }

    Ok(target)
}

fn normalize_upload_kind(raw: &str) -> Result<&'static str, String> {
    match raw.trim().to_ascii_lowercase().as_str() {
        "identity" => Ok("identity"),
        "reference" => Ok("reference"),
        _ => Err("上传类型只能是主形象或现实参考图".to_string()),
    }
}

fn strip_data_url(raw: &str) -> &str {
    let trimmed = raw.trim();
    if trimmed.starts_with("data:") {
        trimmed
            .split_once(',')
            .map(|(_, data)| data)
            .unwrap_or(trimmed)
    } else {
        trimmed
    }
}

fn image_extension_from_magic(bytes: &[u8]) -> Option<&'static str> {
    if bytes.starts_with(&[0x89, b'P', b'N', b'G', 0x0d, 0x0a, 0x1a, 0x0a]) {
        return Some("png");
    }
    if bytes.starts_with(&[0xff, 0xd8, 0xff]) {
        return Some("jpg");
    }
    if bytes.len() >= 12 && &bytes[0..4] == b"RIFF" && &bytes[8..12] == b"WEBP" {
        return Some("webp");
    }
    None
}

fn validate_upload_image(input: &UploadPetImageInput) -> Result<(Vec<u8>, &'static str), String> {
    let filename_extension = Path::new(&input.file_name)
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();
    if !filename_extension.is_empty()
        && !matches!(filename_extension.as_str(), "png" | "jpg" | "jpeg" | "webp")
    {
        return Err("只支持 PNG、JPG 和 WebP 图片".to_string());
    }

    let mime = input.mime_type.trim().to_ascii_lowercase();
    if !mime.is_empty()
        && !matches!(
            mime.as_str(),
            "image/png" | "image/jpeg" | "image/jpg" | "image/webp"
        )
    {
        return Err("图片 MIME 类型不在白名单内".to_string());
    }

    let bytes = BASE64
        .decode(strip_data_url(&input.data_base64))
        .map_err(|_| "图片数据不是有效 base64".to_string())?;
    if bytes.is_empty() {
        return Err("图片数据为空".to_string());
    }
    if bytes.len() > MAX_UPLOAD_IMAGE_BYTES {
        return Err("图片超过 10MB，先压缩后再导入".to_string());
    }
    let extension = image_extension_from_magic(&bytes)
        .ok_or_else(|| "图片文件头不是 PNG、JPG 或 WebP".to_string())?;

    Ok((bytes, extension))
}

fn normalized_custom_action_id(raw: &str) -> Result<String, String> {
    let value = raw.trim().to_ascii_lowercase();
    if value.is_empty() {
        return Err("动作 ID 不能为空，例如 custom:petting".to_string());
    }
    if value.len() > 64 {
        return Err("动作 ID 过长".to_string());
    }
    if !value
        .chars()
        .all(|ch| ch.is_ascii_alphanumeric() || matches!(ch, ':' | '-' | '_'))
    {
        return Err("动作 ID 只能包含小写字母、数字、冒号、短横线和下划线".to_string());
    }
    if !value.starts_with("custom:") && action_row_metadata(&value).is_none() {
        return Err("新增动作 ID 建议使用 custom: 前缀，避免覆盖基础动作".to_string());
    }
    Ok(value)
}

fn action_asset_slug(action_id: &str) -> String {
    action_id.replace(':', "-").replace('_', "-")
}

fn read_u24_le(bytes: &[u8], offset: usize) -> Option<u32> {
    let b0 = *bytes.get(offset)? as u32;
    let b1 = *bytes.get(offset + 1)? as u32;
    let b2 = *bytes.get(offset + 2)? as u32;
    Some(b0 | (b1 << 8) | (b2 << 16))
}

fn png_dimensions(bytes: &[u8]) -> Option<(u32, u32)> {
    if !bytes.starts_with(&[0x89, b'P', b'N', b'G', 0x0d, 0x0a, 0x1a, 0x0a]) || bytes.len() < 24 {
        return None;
    }
    let width = u32::from_be_bytes(bytes.get(16..20)?.try_into().ok()?);
    let height = u32::from_be_bytes(bytes.get(20..24)?.try_into().ok()?);
    Some((width, height))
}

fn webp_dimensions(bytes: &[u8]) -> Option<(u32, u32)> {
    if bytes.len() < 30 || &bytes[0..4] != b"RIFF" || &bytes[8..12] != b"WEBP" {
        return None;
    }
    match &bytes[12..16] {
        b"VP8X" => {
            let width = read_u24_le(bytes, 24)? + 1;
            let height = read_u24_le(bytes, 27)? + 1;
            Some((width, height))
        }
        b"VP8L" => {
            if *bytes.get(20)? != 0x2f {
                return None;
            }
            let b0 = *bytes.get(21)? as u32;
            let b1 = *bytes.get(22)? as u32;
            let b2 = *bytes.get(23)? as u32;
            let b3 = *bytes.get(24)? as u32;
            let width = 1 + (((b1 & 0x3f) << 8) | b0);
            let height = 1 + (((b3 & 0x0f) << 10) | (b2 << 2) | ((b1 & 0xc0) >> 6));
            Some((width, height))
        }
        b"VP8 " => {
            if bytes.len() < 30 || bytes.get(23..26)? != [0x9d, 0x01, 0x2a] {
                return None;
            }
            let width = u16::from_le_bytes(bytes.get(26..28)?.try_into().ok()?) as u32 & 0x3fff;
            let height = u16::from_le_bytes(bytes.get(28..30)?.try_into().ok()?) as u32 & 0x3fff;
            Some((width, height))
        }
        _ => None,
    }
}

fn image_dimensions(bytes: &[u8], extension: &str) -> Option<(u32, u32)> {
    match extension {
        "png" => png_dimensions(bytes),
        "webp" => webp_dimensions(bytes),
        _ => None,
    }
}

fn validate_upload_action_strip(
    input: &UploadPetActionStripInput,
) -> Result<(Vec<u8>, &'static str, Vec<u64>), String> {
    let image_input = UploadPetImageInput {
        pet_id: input.pet_id.clone(),
        kind: "reference".to_string(),
        file_name: input.file_name.clone(),
        mime_type: input.mime_type.clone(),
        data_base64: input.data_base64.clone(),
    };
    let (bytes, extension) = validate_upload_image(&image_input)?;
    if extension == "jpg" {
        return Err("动作条需要透明背景，请使用 PNG 或 WebP".to_string());
    }
    let frames = input.frames.clamp(1, 8);
    let (width, height) =
        image_dimensions(&bytes, extension).ok_or_else(|| "无法读取动作条尺寸".to_string())?;
    let expected_width = 192 * frames as u32;
    if width != expected_width || height != 208 {
        return Err(format!(
            "动作条尺寸应为 {}x208，当前为 {}x{}",
            expected_width, width, height
        ));
    }

    let durations = (0..frames)
        .map(|index| {
            input
                .durations
                .get(index)
                .copied()
                .unwrap_or(180)
                .clamp(60, 900)
        })
        .collect::<Vec<_>>();

    Ok((bytes, extension, durations))
}

fn normalized_action_ref(raw: &str) -> Result<String, String> {
    let value = raw.trim().to_ascii_lowercase();
    if value.is_empty() {
        return Err("动作 ID 不能为空".to_string());
    }
    if value.len() > 64 {
        return Err("动作 ID 过长".to_string());
    }
    if !value
        .chars()
        .all(|ch| ch.is_ascii_alphanumeric() || matches!(ch, ':' | '-' | '_'))
    {
        return Err("动作 ID 只能包含小写字母、数字、冒号、短横线和下划线".to_string());
    }
    Ok(value)
}

fn mime_type(path: &str) -> &'static str {
    match Path::new(path)
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase()
        .as_str()
    {
        "png" => "image/png",
        "jpg" | "jpeg" => "image/jpeg",
        "webp" => "image/webp",
        _ => "application/octet-stream",
    }
}

fn asset_exists(root: &Path, asset_path: &str) -> bool {
    safe_asset_path(asset_path)
        .ok()
        .map(|path| root.join(RUNTIME_DIR).join(path).is_file())
        .unwrap_or(false)
}

fn action_row_metadata(action_id: &str) -> Option<(usize, usize, Vec<u64>, &'static str)> {
    match action_id {
        "idle" => Some((0, 6, vec![260, 150, 150, 170, 170, 320], "待机")),
        "running-right" => Some((1, 8, vec![58, 54, 50, 54, 58, 50, 54, 68], "向右跑")),
        "running-left" => Some((2, 8, vec![58, 54, 50, 54, 58, 50, 54, 68], "向左跑")),
        "waving" => Some((3, 4, vec![170, 120, 120, 220], "挥爪")),
        "jumping" => Some((4, 5, vec![80, 75, 90, 95, 140], "跳一下")),
        "failed" => Some((
            5,
            8,
            vec![120, 100, 120, 140, 160, 180, 180, 260],
            "委屈一下",
        )),
        "waiting" => Some((6, 6, vec![220, 180, 180, 220, 180, 260], "等一下")),
        "running" => Some((7, 6, vec![62, 58, 54, 58, 62, 74], "跑一小段")),
        "review" => Some((8, 6, vec![210, 190, 220, 190, 190, 260], "陪我一会")),
        "standing" => Some((9, 8, vec![240, 220, 260, 220, 280, 220, 240, 320], "站一会")),
        "tongue" => Some((
            10,
            8,
            vec![140, 140, 150, 150, 150, 150, 160, 220],
            "吐舌头",
        )),
        "lying" => Some((11, 8, vec![190, 190, 230, 260, 260, 300, 300, 360], "卧倒")),
        "stretching" => Some((
            12,
            8,
            vec![130, 140, 150, 170, 190, 180, 170, 230],
            "伸懒腰",
        )),
        "sleeping" => Some((
            13,
            8,
            vec![420, 480, 460, 520, 480, 540, 500, 560],
            "打个盹",
        )),
        "sniffing" => Some((
            14,
            8,
            vec![130, 130, 140, 150, 170, 170, 160, 220],
            "闻一闻",
        )),
        "rolling" => Some((
            15,
            8,
            vec![120, 110, 110, 115, 115, 110, 120, 180],
            "打个滚",
        )),
        "crying" => Some((
            16,
            8,
            vec![220, 200, 210, 230, 250, 230, 210, 300],
            "哭一下",
        )),
        "chase-butterfly" => Some((17, 8, vec![72, 66, 62, 66, 72, 66, 62, 88], "追蝴蝶")),
        "angry" => Some((
            18,
            8,
            vec![130, 110, 130, 110, 170, 140, 140, 240],
            "生气一下",
        )),
        _ => None,
    }
}

fn normalized_action_durations(source: &[u64], frames: usize, fallback: &[u64]) -> Vec<u64> {
    (0..frames)
        .map(|index| {
            source
                .get(index)
                .or_else(|| fallback.get(index))
                .copied()
                .unwrap_or(180)
                .clamp(60, 900)
        })
        .collect()
}

fn pet_action_summaries(pet: &PetEntryFile) -> Vec<PetActionSummary> {
    let extension_by_id: HashMap<&str, &ExtensionAssetFile> = pet
        .extension_assets
        .iter()
        .filter(|asset| !asset.id.is_empty())
        .map(|asset| (asset.id.as_str(), asset))
        .collect();

    let mut seen = HashSet::new();
    let mut ordered_actions = pet.supported_actions.clone();
    for asset in &pet.extension_assets {
        if !asset.id.is_empty() {
            ordered_actions.push(asset.id.clone());
        }
    }

    ordered_actions
        .into_iter()
        .filter_map(|action_id| {
            if action_id.is_empty() || !seen.insert(action_id.clone()) {
                return None;
            }

            let row_meta = action_row_metadata(&action_id);
            let extension = extension_by_id.get(action_id.as_str()).copied();
            let extension_asset = extension
                .and_then(|asset| safe_asset_path(&asset.strip).ok())
                .filter(|path| !path.is_empty());

            if let Some(asset) = extension {
                if extension_asset.is_some() {
                    let fallback = row_meta
                        .as_ref()
                        .map(|(_, _, durations, _)| durations.as_slice())
                        .unwrap_or(&[]);
                    let frames = if asset.frames > 0 {
                        asset.frames.min(8)
                    } else {
                        row_meta
                            .as_ref()
                            .map(|(_, frames, _, _)| *frames)
                            .unwrap_or(1)
                    };
                    let label = if asset.label.is_empty() {
                        row_meta
                            .as_ref()
                            .map(|(_, _, _, label)| (*label).to_string())
                            .unwrap_or_else(|| action_id.replace("custom:", ""))
                    } else {
                        asset.label.clone()
                    };

                    return Some(PetActionSummary {
                        id: action_id,
                        label,
                        source: "strip".to_string(),
                        row: None,
                        frames,
                        durations: normalized_action_durations(&asset.durations, frames, fallback),
                        asset: extension_asset,
                    });
                }
            }

            row_meta.map(|(row, frames, durations, label)| PetActionSummary {
                id: action_id,
                label: label.to_string(),
                source: "atlas".to_string(),
                row: Some(row),
                frames,
                durations: durations.clone(),
                asset: None,
            })
        })
        .collect()
}

fn to_pet_summary(root: &Path, pet: &PetEntryFile) -> PetSummary {
    let identity_asset = safe_asset_path(&pet.identity_image).ok();
    let spritesheet_asset = safe_asset_path(&pet.spritesheet).ok();
    let reference_assets = pet
        .reference_images
        .iter()
        .filter_map(|path| safe_asset_path(path).ok())
        .collect::<Vec<_>>();
    let actions = pet_action_summaries(pet);

    PetSummary {
        id: pet.id.clone(),
        display_name: pet.display_name.clone(),
        species: pet.species.clone(),
        notes: pet.notes.clone(),
        status: pet.status.clone(),
        action_pack_level: pet.action_pack_level.clone(),
        supported_action_count: pet.supported_actions.len(),
        extension_action_count: pet
            .extension_assets
            .iter()
            .map(|item| item.id.as_str())
            .collect::<HashSet<_>>()
            .len(),
        reference_assets,
        identity_available: identity_asset
            .as_deref()
            .map(|path| asset_exists(root, path))
            .unwrap_or(false),
        spritesheet_available: spritesheet_asset
            .as_deref()
            .map(|path| asset_exists(root, path))
            .unwrap_or(false),
        identity_asset,
        spritesheet_asset,
        actions,
    }
}

fn show_window(app: &AppHandle, label: &str, focus: bool) -> Result<(), String> {
    let window = app
        .get_webview_window(label)
        .ok_or_else(|| format!("窗口不存在: {}", label))?;
    window.show().map_err(|err| err.to_string())?;
    if focus {
        window.set_focus().map_err(|err| err.to_string())?;
    }
    Ok(())
}

#[tauri::command]
fn get_runtime_summary() -> Result<RuntimeSummary, String> {
    let root = product_root()?;
    let family_path = root.join(FAMILY_PATH);
    let settings_path = root.join(SETTINGS_PATH);
    let family: PetFamilyFile = read_json_file(&family_path)?;
    let settings: RuntimeSettingsFile = read_json_file(&settings_path)?;
    let current_pet_id = if settings.current_pet_id.is_empty() {
        family.current_pet_id.clone()
    } else {
        settings.current_pet_id.clone()
    };

    let pets: Vec<PetSummary> = family
        .pets
        .iter()
        .map(|pet| to_pet_summary(&root, pet))
        .collect();
    let current_pet = pets.iter().find(|pet| pet.id == current_pet_id).cloned();
    let ready_pet_count = pets.iter().filter(|pet| pet.status == "ready").count();
    let total_supported_actions = family
        .pets
        .iter()
        .map(|pet| pet.supported_actions.len())
        .sum();
    let total_extension_assets = family
        .pets
        .iter()
        .map(|pet| pet.extension_assets.len())
        .sum();
    let features = feature_summary(&root, &current_pet_id);

    let notes = vec![
        "只通过白名单命令读写 E 盘 data-dev 运行镜像".to_string(),
        "未返回 API Key、Token、聊天、待办、提醒历史、本机导出路径".to_string(),
        "图片读取仅允许注册表中的 identity、reference、spritesheet 和 extension 动作条".to_string(),
    ];

    Ok(RuntimeSummary {
        runtime_available: root.join(RUNTIME_DIR).is_dir(),
        runtime_source: RUNTIME_DIR.to_string(),
        current_pet_id,
        pet_count: pets.len(),
        ready_pet_count,
        total_supported_actions,
        total_extension_assets,
        current_pet,
        pets,
        settings: safe_settings_summary(&settings),
        features,
        checks: RuntimeChecks {
            settings_loaded: settings_path.is_file(),
            family_loaded: family_path.is_file(),
            sensitive_fields_returned: false,
            notes,
        },
    })
}

#[tauri::command]
fn update_settings(input: UpdateSettingsInput) -> Result<SafeSettingsSummary, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, SETTINGS_PATH)?;
    let mut settings: RuntimeSettingsFile = read_json_file(&path)?;

    if let Some(scale) = input.scale {
        settings.scale = Some(normalized_f64(scale, 0.2, 1.2, "大小比例")?);
    }
    if let Some(animation_speed) = input.animation_speed {
        settings.animation_speed = Some(normalized_f64(animation_speed, 0.1, 2.0, "动画速度")?);
    }
    if let Some(always_on_top) = input.always_on_top {
        settings.always_on_top = Some(always_on_top);
    }
    if let Some(bubble_style) = input.bubble_style {
        settings.bubble_style = Some(normalize_bubble_style(&bubble_style)?);
    }
    if let Some(bubble_fill) = input.bubble_fill {
        settings.bubble_fill = Some(normalize_hex_color(&bubble_fill, "气泡背景色")?);
    }
    if let Some(bubble_outline) = input.bubble_outline {
        settings.bubble_outline = Some(normalize_hex_color(&bubble_outline, "气泡描边色")?);
    }
    if let Some(bubble_text) = input.bubble_text {
        settings.bubble_text = Some(normalize_hex_color(&bubble_text, "气泡文字色")?);
    }
    if let Some(bubble_duration) = input.bubble_duration {
        settings.bubble_duration =
            Some(normalized_f64(bubble_duration, 2.0, 20.0, "气泡显示时长")?);
    }
    if let Some(talk_enabled) = input.talk_enabled {
        settings.talk_enabled = Some(talk_enabled);
    }
    if let Some(roam_enabled) = input.roam_enabled {
        settings.roam_enabled = Some(roam_enabled);
    }
    if let Some(drag_sensitivity) = input.drag_sensitivity {
        settings.drag_sensitivity = Some(normalized_f64(drag_sensitivity, 0.1, 2.0, "拖动灵敏度")?);
    }
    if let Some(inertia) = input.inertia {
        settings.inertia = Some(normalized_f64(inertia, 0.0, 1.0, "拖动惯性")?);
    }
    if let Some(roam_speed) = input.roam_speed {
        settings.roam_speed = Some(normalized_f64(roam_speed, 20.0, 240.0, "巡游速度")?);
    }
    if let Some(roam_distance) = input.roam_distance {
        settings.roam_distance = Some(normalized_f64(roam_distance, 0.05, 1.0, "巡游距离")?);
    }
    if let Some(roam_interval) = input.roam_interval {
        settings.roam_interval = Some(normalized_f64(roam_interval, 60.0, 1000.0, "巡游刷新间隔")?);
    }
    if let Some(idle_action_interval) = input.idle_action_interval {
        settings.idle_action_interval = Some(normalized_f64(
            idle_action_interval,
            4.0,
            120.0,
            "待机动作间隔",
        )?);
    }
    if let Some(talk_interval) = input.talk_interval {
        settings.talk_interval = Some(normalized_f64(talk_interval, 30.0, 600.0, "自动说话间隔")?);
    }
    if let Some(talk_after_interaction_delay) = input.talk_after_interaction_delay {
        settings.talk_after_interaction_delay = Some(normalized_f64(
            talk_after_interaction_delay,
            2.0,
            120.0,
            "互动后说话延迟",
        )?);
    }
    if let Some(roam_allow_center) = input.roam_allow_center {
        settings.roam_allow_center = Some(roam_allow_center);
    }
    if let Some(multi_monitor_roam) = input.multi_monitor_roam {
        settings.multi_monitor_roam = Some(multi_monitor_roam);
    }
    if let Some(primary_monitor_edge_only) = input.primary_monitor_edge_only {
        settings.primary_monitor_edge_only = Some(primary_monitor_edge_only);
    }
    if let Some(secondary_monitor_full_roam) = input.secondary_monitor_full_roam {
        settings.secondary_monitor_full_roam = Some(secondary_monitor_full_roam);
    }
    if let Some(roam_current_monitor_only) = input.roam_current_monitor_only {
        settings.roam_current_monitor_only = Some(roam_current_monitor_only);
    }
    if let Some(keep_on_screen) = input.keep_on_screen {
        settings.keep_on_screen = Some(keep_on_screen);
    }
    if let Some(lock_size_across_monitors) = input.lock_size_across_monitors {
        settings.lock_size_across_monitors = Some(lock_size_across_monitors);
    }

    write_json_file(&path, &settings)?;
    Ok(safe_settings_summary(&settings))
}

#[tauri::command]
fn update_quick_menu_actions(
    app: AppHandle,
    input: UpdateQuickMenuActionsInput,
) -> Result<RuntimeSummary, String> {
    let root = product_root()?;
    let family_path = root.join(FAMILY_PATH);
    let settings_path = runtime_file_path(&root, SETTINGS_PATH)?;
    let family: PetFamilyFile = read_json_file(&family_path)?;
    let pet_id = normalized_pet_id(&input.pet_id)?;
    let target = family
        .pets
        .iter()
        .find(|pet| pet.id == pet_id)
        .ok_or_else(|| "没有在宠物注册表中找到这个形象".to_string())?;

    let available_actions = pet_action_summaries(target)
        .into_iter()
        .map(|action| action.id)
        .collect::<HashSet<_>>();
    let mut normalized_actions = Vec::new();
    let mut seen = HashSet::new();

    for raw_action_id in input.action_ids.iter().take(MAX_QUICK_MENU_ACTIONS) {
        let action_id = normalized_action_ref(raw_action_id)?;
        if !available_actions.contains(&action_id) {
            return Err(format!("当前宠物不支持动作: {}", action_id));
        }
        if seen.insert(action_id.clone()) {
            normalized_actions.push(action_id);
        }
    }

    if normalized_actions.is_empty() {
        return Err("右键动作栏至少保留 1 个动作".to_string());
    }

    let mut settings: RuntimeSettingsFile = read_json_file(&settings_path)?;
    settings.quick_menu_actions = normalized_actions.clone();
    write_json_file(&settings_path, &settings)?;

    let summary = get_runtime_summary()?;
    let _ = app.emit(
        "danhuang-runtime-changed",
        json!({ "quick_menu_actions_updated": pet_id, "action_count": normalized_actions.len() }),
    );
    Ok(summary)
}

#[tauri::command]
fn update_ai_provider_state(
    app: AppHandle,
    input: UpdateAiProviderStateInput,
) -> Result<RuntimeSummary, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, AI_PROVIDERS_PATH)?;
    let mut file: AiProvidersFile = read_json_file(&path)?;
    let provider_id = normalized_pet_id(&input.provider_id)?;

    if !file.providers.contains_key(&provider_id) {
        return Err("未找到这个 AI Provider".to_string());
    }

    if let Some(provider) = file.providers.get_mut(&provider_id) {
        if let Some(enabled) = input.enabled {
            provider.enabled = enabled;
        }
        if input.make_active {
            provider.enabled = true;
            file.active_provider = provider_id.clone();
        }
    }

    if file.active_provider == provider_id {
        let active_enabled = file
            .providers
            .get(&provider_id)
            .map(|provider| provider.enabled)
            .unwrap_or(false);
        if !active_enabled {
            file.active_provider = file
                .providers
                .iter()
                .filter(|(_, provider)| provider.enabled)
                .map(|(id, _)| id.clone())
                .min()
                .unwrap_or_default();
        }
    }

    write_json_file(&path, &file)?;

    let summary = get_runtime_summary()?;
    let _ = app.emit(
        "danhuang-runtime-changed",
        json!({ "ai_provider_updated": provider_id, "active_provider": summary.features.active_provider }),
    );
    Ok(summary)
}

#[tauri::command]
fn switch_pet(app: AppHandle, input: SwitchPetInput) -> Result<RuntimeSummary, String> {
    let root = product_root()?;
    let family_path = root.join(FAMILY_PATH);
    let settings_path = runtime_file_path(&root, SETTINGS_PATH)?;
    let family: PetFamilyFile = read_json_file(&family_path)?;
    let pet_id = normalized_pet_id(&input.pet_id)?;
    let target = family
        .pets
        .iter()
        .find(|pet| pet.id == pet_id)
        .ok_or_else(|| "没有在宠物注册表中找到这个形象".to_string())?;

    if target.status != "ready" {
        return Err("这个形象还没有准备好，不能切换为当前桌宠".to_string());
    }
    if !asset_exists(&root, &target.spritesheet) {
        return Err("这个形象缺少可播放 spritesheet，暂不能切换".to_string());
    }

    let mut settings: RuntimeSettingsFile = read_json_file(&settings_path)?;
    settings.current_pet_id = pet_id.clone();
    write_json_file(&settings_path, &settings)?;

    let summary = get_runtime_summary()?;
    let _ = app.emit(
        "danhuang-runtime-changed",
        json!({ "current_pet_id": pet_id }),
    );
    Ok(summary)
}

#[tauri::command]
fn update_pet_profile(
    app: AppHandle,
    input: UpdatePetProfileInput,
) -> Result<RuntimeSummary, String> {
    let root = product_root()?;
    let family_path = runtime_file_path(&root, FAMILY_PATH)?;
    let mut family: PetFamilyFile = read_json_file(&family_path)?;
    let pet_id = normalized_pet_id(&input.pet_id)?;
    let display_name = normalize_text(&input.display_name, "", 24);
    let species = normalize_text(&input.species, "", 24);
    let notes = normalize_text(&input.notes, "", 420);

    if display_name.is_empty() {
        return Err("宠物名称不能为空".to_string());
    }

    let target = family
        .pets
        .iter_mut()
        .find(|pet| pet.id == pet_id)
        .ok_or_else(|| "没有在宠物注册表中找到这个形象".to_string())?;

    target.display_name = display_name;
    target.species = species;
    target.notes = notes;
    write_json_file(&family_path, &family)?;

    let summary = get_runtime_summary()?;
    let _ = app.emit(
        "danhuang-runtime-changed",
        json!({ "pet_profile_updated": pet_id }),
    );
    Ok(summary)
}

#[tauri::command]
fn upload_pet_image(app: AppHandle, input: UploadPetImageInput) -> Result<RuntimeSummary, String> {
    let root = product_root()?;
    let family_path = runtime_file_path(&root, FAMILY_PATH)?;
    let mut family: PetFamilyFile = read_json_file(&family_path)?;
    let pet_id = normalized_pet_id(&input.pet_id)?;
    let kind = normalize_upload_kind(&input.kind)?;
    let (bytes, extension) = validate_upload_image(&input)?;

    let target = family
        .pets
        .iter_mut()
        .find(|pet| pet.id == pet_id)
        .ok_or_else(|| "没有在宠物注册表中找到这个形象".to_string())?;

    let asset_path = if kind == "identity" {
        format!("family/{}/identity-base.{}", pet_id, extension)
    } else {
        format!(
            "family/{}/uploads/user-{}.{}",
            pet_id,
            current_millis(),
            extension
        )
    };
    let target_path = runtime_asset_write_path(&root, &asset_path)?;
    fs::write(&target_path, &bytes)
        .map_err(|err| format!("写入图片失败 {}: {}", target_path.display(), err))?;

    if kind == "identity" {
        target.identity_image = asset_path.clone();
    } else if !target
        .reference_images
        .iter()
        .any(|path| path == &asset_path)
    {
        target.reference_images.push(asset_path.clone());
    }

    write_json_file(&family_path, &family)?;

    let summary = get_runtime_summary()?;
    let _ = app.emit(
        "danhuang-runtime-changed",
        json!({ "pet_image_uploaded": pet_id, "kind": kind, "asset": asset_path }),
    );
    Ok(summary)
}

#[tauri::command]
fn upload_pet_action_strip(
    app: AppHandle,
    input: UploadPetActionStripInput,
) -> Result<RuntimeSummary, String> {
    let root = product_root()?;
    let family_path = runtime_file_path(&root, FAMILY_PATH)?;
    let mut family: PetFamilyFile = read_json_file(&family_path)?;
    let pet_id = normalized_pet_id(&input.pet_id)?;
    let action_id = normalized_custom_action_id(&input.action_id)?;
    let label = normalize_text(&input.label, "", 24);
    if label.is_empty() {
        return Err("动作名称不能为空".to_string());
    }
    let frames = input.frames.clamp(1, 8);
    let (bytes, extension, durations) = validate_upload_action_strip(&input)?;

    let target = family
        .pets
        .iter_mut()
        .find(|pet| pet.id == pet_id)
        .ok_or_else(|| "没有在宠物注册表中找到这个形象".to_string())?;

    let asset_path = format!(
        "family/{}/extension-{}.{}",
        pet_id,
        action_asset_slug(&action_id),
        extension
    );
    let target_path = runtime_asset_write_path(&root, &asset_path)?;
    fs::write(&target_path, &bytes)
        .map_err(|err| format!("写入动作条失败 {}: {}", target_path.display(), err))?;

    if !target.supported_actions.iter().any(|id| id == &action_id) {
        target.supported_actions.push(action_id.clone());
    }

    if let Some(asset) = target
        .extension_assets
        .iter_mut()
        .find(|asset| asset.id == action_id)
    {
        asset.label = label.clone();
        asset.strip = asset_path.clone();
        asset.frames = frames;
        asset.durations = durations.clone();
    } else {
        target.extension_assets.push(ExtensionAssetFile {
            id: action_id.clone(),
            label: label.clone(),
            strip: asset_path.clone(),
            frames,
            durations,
        });
    }

    write_json_file(&family_path, &family)?;

    let summary = get_runtime_summary()?;
    let _ = app.emit(
        "danhuang-runtime-changed",
        json!({ "pet_action_uploaded": pet_id, "action_id": action_id, "asset": asset_path }),
    );
    Ok(summary)
}

#[tauri::command]
fn get_todos() -> Result<Vec<TodoSummary>, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, TODOS_PATH)?;
    let file = read_todos_file(&path)?;
    Ok(visible_todos(&file))
}

#[tauri::command]
fn create_todo(input: CreateTodoInput) -> Result<TodoSummary, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, TODOS_PATH)?;
    let mut file = read_todos_file(&path)?;
    let now = normalize_timestamp(&input.now);
    let title = normalize_text(&input.title, "", 120);

    if title.is_empty() {
        return Err("提醒标题不能为空".to_string());
    }

    let item = TodoItemFile {
        id: format!("todo-{}-{}", current_millis(), file.items.len() + 1),
        title,
        note: String::new(),
        category: normalize_text(&input.category, "本地", 32),
        priority: normalize_priority(&input.priority),
        due_at: normalize_text(&input.due_at, "稍后", 80),
        repeat: "none".to_string(),
        status: "open".to_string(),
        pinned: false,
        important_interval_minutes: 0,
        snooze_until: String::new(),
        created_at: now.clone(),
        updated_at: now.clone(),
        completed_at: String::new(),
        deleted_at: String::new(),
        last_reminded_at: String::new(),
        remind_count: 0,
        extra: HashMap::new(),
    };
    let summary = todo_to_summary(&item);
    file.items.insert(0, item.clone());
    file.updated_at = now.clone();
    write_json_file(&path, &file)?;
    let _ = append_reminder_event(&root, "created", &item, &now);
    Ok(summary)
}

#[tauri::command]
fn update_todo_state(input: UpdateTodoInput) -> Result<TodoSummary, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, TODOS_PATH)?;
    let mut file = read_todos_file(&path)?;
    let now = normalize_timestamp(&input.now);
    let todo_id = normalize_text(&input.id, "", 96);

    if todo_id.is_empty() {
        return Err("提醒 ID 不能为空".to_string());
    }

    let index = file
        .items
        .iter()
        .position(|item| {
            item.id == todo_id && item.status != "deleted" && item.deleted_at.is_empty()
        })
        .ok_or_else(|| "未找到可更新的提醒".to_string())?;
    let mut event_type = "updated";

    {
        let item = &mut file.items[index];
        if let Some(done) = input.done {
            if done {
                item.status = "done".to_string();
                item.completed_at = now.clone();
                event_type = "completed";
            } else {
                item.status = "open".to_string();
                item.completed_at.clear();
                event_type = "reopened";
            }
        }

        if let Some(pinned) = input.pinned {
            item.pinned = pinned;
            event_type = if pinned { "pinned" } else { "unpinned" };
        }

        if let Some(snooze_until) = input.snooze_until {
            let normalized = normalize_text(&snooze_until, "", 80);
            if !normalized.is_empty() {
                item.snooze_until = normalized;
                item.last_reminded_at = now.clone();
                event_type = "snoozed";
            }
        }

        item.updated_at = now.clone();
    }

    file.updated_at = now.clone();
    let updated_item = file.items[index].clone();
    let summary = todo_to_summary(&updated_item);
    write_json_file(&path, &file)?;
    let _ = append_reminder_event(&root, event_type, &updated_item, &now);
    Ok(summary)
}

#[tauri::command]
fn update_todo_detail(input: UpdateTodoDetailInput) -> Result<TodoSummary, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, TODOS_PATH)?;
    let mut file = read_todos_file(&path)?;
    let now = normalize_timestamp(&input.now);
    let todo_id = normalize_text(&input.id, "", 96);
    let title = normalize_text(&input.title, "", 120);

    if todo_id.is_empty() {
        return Err("提醒 ID 不能为空".to_string());
    }
    if title.is_empty() {
        return Err("提醒标题不能为空".to_string());
    }

    let index = file
        .items
        .iter()
        .position(|item| {
            item.id == todo_id && item.status != "deleted" && item.deleted_at.is_empty()
        })
        .ok_or_else(|| "未找到可编辑的提醒".to_string())?;

    {
        let item = &mut file.items[index];
        item.title = title;
        item.due_at = normalize_text(&input.due_at, "稍后", 80);
        item.category = normalize_text(&input.category, "本地", 32);
        item.priority = normalize_priority(&input.priority);
        item.repeat = normalize_repeat(&input.repeat);
        item.note = normalize_multiline_text(&input.note, 800);
        item.important_interval_minutes =
            normalize_interval_minutes(input.important_interval_minutes);
        item.updated_at = now.clone();
    }

    file.updated_at = now.clone();
    let updated_item = file.items[index].clone();
    let summary = todo_to_summary(&updated_item);
    write_json_file(&path, &file)?;
    let _ = append_reminder_event(&root, "edited", &updated_item, &now);
    Ok(summary)
}

#[tauri::command]
fn record_todo_reminder(
    app: AppHandle,
    input: RecordTodoReminderInput,
) -> Result<TodoSummary, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, TODOS_PATH)?;
    let mut file = read_todos_file(&path)?;
    let now = normalize_timestamp(&input.now);
    let todo_id = normalize_text(&input.id, "", 96);

    if todo_id.is_empty() {
        return Err("提醒 ID 不能为空".to_string());
    }

    let index = file
        .items
        .iter()
        .position(|item| {
            item.id == todo_id && item.status != "deleted" && item.deleted_at.is_empty()
        })
        .ok_or_else(|| "未找到可记录的提醒".to_string())?;

    if same_timestamp_minute(&file.items[index].last_reminded_at, &now) {
        return Ok(todo_to_summary(&file.items[index]));
    }

    {
        let item = &mut file.items[index];
        item.last_reminded_at = now.clone();
        item.remind_count = item.remind_count.saturating_add(1);
        item.snooze_until.clear();
        item.updated_at = now.clone();
    }

    file.updated_at = now.clone();
    let updated_item = file.items[index].clone();
    let summary = todo_to_summary(&updated_item);
    write_json_file(&path, &file)?;
    let _ = append_reminder_event(&root, "remind", &updated_item, &now);
    let _ = app.emit(
        "danhuang-reminder-triggered",
        json!({
            "id": summary.id,
            "title": summary.title,
            "due_at": summary.due_at,
            "priority": summary.priority,
            "remind_count": summary.remind_count,
            "time": now,
        }),
    );
    Ok(summary)
}

#[tauri::command]
fn get_chat_messages() -> Result<Vec<ChatMessageSummary>, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, CHAT_MEMORY_PATH)?;
    let file = read_chat_memory_file(&path)?;
    Ok(recent_chat_summaries(&file))
}

#[tauri::command]
fn send_chat_message(
    app: AppHandle,
    input: SendChatMessageInput,
) -> Result<ChatMessageSummary, String> {
    let root = product_root()?;
    let path = runtime_file_path(&root, CHAT_MEMORY_PATH)?;
    let mut file = read_chat_memory_file(&path)?;
    let settings_path = runtime_file_path(&root, SETTINGS_PATH)?;
    let settings: RuntimeSettingsFile = read_json_file(&settings_path)?;
    let now = normalize_timestamp(&input.now);
    let text = normalize_multiline_text(&input.text, 400);

    if text.is_empty() {
        return Err("聊天内容不能为空".to_string());
    }

    let mood = classify_chat_mood(&text);
    let role_style = normalize_text(&input.role_style, "蛋黄本色", 32);
    let time_reply = local_time_reply(&text);
    let (reply, mut source) = if !time_reply.trim().is_empty() {
        (time_reply, "local-time".to_string())
    } else {
        let research = build_research_bundle(&text);
        match call_ai_reply(&root, &settings, &file, &text, &mood, &research.context) {
            Ok((reply, source)) => (reply, source),
            Err(error) => {
                let local_reply = if research.triggered && !research.local_reply.trim().is_empty() {
                    normalize_multiline_text(&research.local_reply, 1200)
                } else {
                    normalize_multiline_text(&local_chat_reply(&root, &mood, file.reply_count), 180)
                };
                let fallback_source = normalize_text(&error, "local", 48)
                    .replace(':', "_")
                    .replace('\n', " ");
                let prefix = if research.triggered {
                    format!(
                        "research-fallback:{}:",
                        normalize_text(&research.query, "资料", 40)
                    )
                } else {
                    "local-fallback:".to_string()
                };
                (local_reply, format!("{}{}", prefix, fallback_source))
            }
        }
    };
    if role_style != "蛋黄本色" {
        source = format!("{}:{}", source, role_style);
    }

    let item = ChatMessageFile {
        time: now.clone(),
        user: text,
        mood: mood.clone(),
        reply,
        source,
        memory_update: String::new(),
        extra: HashMap::new(),
    };

    file.messages.push(item.clone());
    if file.messages.len() > MAX_CHAT_MESSAGES {
        let overflow = file.messages.len() - MAX_CHAT_MESSAGES;
        file.messages.drain(0..overflow);
    }
    *file.mood_counts.entry(mood.clone()).or_insert(0) += 1;
    file.reply_count = file.reply_count.saturating_add(1);
    file.last_mood = mood;
    file.updated_at = now;

    let summary = chat_to_summary(&item, file.messages.len().saturating_sub(1));
    write_json_file(&path, &file)?;
    let _ = app.emit(
        "danhuang-chat-reply",
        json!({
            "time": summary.time,
            "mood": summary.mood,
            "reply": summary.reply,
            "source": summary.source,
        }),
    );
    Ok(summary)
}

#[tauri::command]
fn get_pet_state() -> Result<PetStateSummary, String> {
    let root = product_root()?;
    let pet_id = current_pet_id_from_settings(&root)?;
    let state_dir = pet_state_dir(&root, &pet_id)?;
    let story_path = state_dir.join("pet-stories.json");
    let memory_path = state_dir.join("memory-summary.json");
    let story_file = read_story_file(&story_path)?;
    let memory =
        read_optional_json_file::<MemorySummaryFile>(&memory_path).map(memory_summary_to_safe);

    let mut stories: Vec<StoryEntrySummary> = story_file
        .entries
        .iter()
        .map(story_entry_to_summary)
        .collect();
    stories.sort_by(|a, b| {
        b.pinned
            .cmp(&a.pinned)
            .then_with(|| b.created_at.cmp(&a.created_at))
    });

    Ok(PetStateSummary {
        pet_id,
        stories,
        prompt_summary: story_file.prompt_summary,
        role_prompt: story_file.role_prompt,
        summary_updated_at: story_file.summary_updated_at,
        summary_source: story_file.summary_source,
        memory,
    })
}

#[tauri::command]
fn create_pet_story(app: AppHandle, input: CreatePetStoryInput) -> Result<PetStateSummary, String> {
    let root = product_root()?;
    let pet_id = current_pet_id_from_settings(&root)?;
    let state_dir = pet_state_dir(&root, &pet_id)?;
    fs::create_dir_all(&state_dir).map_err(|err| format!("无法创建宠物状态目录: {}", err))?;
    let story_path = state_dir.join("pet-stories.json");
    let mut story_file = read_story_file(&story_path)?;
    let now = normalize_timestamp(&input.now);
    let title = normalize_text(&input.title, "", 80);
    let content = normalize_multiline_text(&input.content, 4000);

    if title.is_empty() {
        return Err("故事标题不能为空".to_string());
    }
    if content.is_empty() {
        return Err("故事内容不能为空".to_string());
    }

    let entry_type = normalize_text(&input.entry_type, "story", 24);
    let entry = StoryEntryFile {
        id: format!(
            "story-{}-{}",
            current_millis(),
            story_file.entries.len() + 1
        ),
        entry_type,
        title,
        content,
        image_refs: Vec::new(),
        created_at: now.clone(),
        updated_at: now.clone(),
        pinned: false,
        extra: HashMap::new(),
    };

    story_file.entries.insert(0, entry);
    story_file.updated_at = now.clone();
    if story_file.summary_updated_at.is_empty() {
        story_file.summary_updated_at = now.clone();
        story_file.summary_source = "local_story".to_string();
    }
    write_json_file(&story_path, &story_file)?;
    let _ = app.emit(
        "danhuang-runtime-changed",
        json!({ "pet_story_created": pet_id }),
    );
    get_pet_state()
}

#[tauri::command]
fn get_runtime_asset(asset_path: String) -> Result<RuntimeAsset, String> {
    let root = product_root()?;
    let safe_path = safe_asset_path(&asset_path)?;
    let runtime_root = root
        .join(RUNTIME_DIR)
        .canonicalize()
        .map_err(|err| format!("运行镜像目录不可用: {}", err))?;
    let asset = runtime_root.join(&safe_path);
    let asset_canonical = asset
        .canonicalize()
        .map_err(|err| format!("资源不存在 {}: {}", safe_path, err))?;

    if !asset_canonical.starts_with(&runtime_root) {
        return Err("资源越过运行镜像边界".to_string());
    }

    let metadata = fs::metadata(&asset_canonical).map_err(|err| err.to_string())?;
    if metadata.len() > MAX_ASSET_BYTES {
        return Err("资源过大，不适合前端预览".to_string());
    }

    let bytes = fs::read(&asset_canonical).map_err(|err| err.to_string())?;
    let mime = mime_type(&safe_path).to_string();
    let encoded = BASE64.encode(bytes);

    Ok(RuntimeAsset {
        path: safe_path,
        mime_type: mime.clone(),
        data_url: format!("data:{};base64,{}", mime, encoded),
    })
}

#[tauri::command]
fn show_panel(app: AppHandle) -> Result<(), String> {
    show_window(&app, "main", true)
}

#[tauri::command]
fn show_pet(app: AppHandle) -> Result<(), String> {
    show_window(&app, "pet", false)
}

#[tauri::command]
fn hide_pet(app: AppHandle) -> Result<(), String> {
    let window = app
        .get_webview_window("pet")
        .ok_or_else(|| "窗口不存在: pet".to_string())?;
    window.hide().map_err(|err| err.to_string())
}

#[tauri::command]
fn set_pet_always_on_top(app: AppHandle, enabled: bool) -> Result<(), String> {
    let window = app
        .get_webview_window("pet")
        .ok_or_else(|| "窗口不存在: pet".to_string())?;
    window
        .set_always_on_top(enabled)
        .map_err(|err| err.to_string())
}

#[tauri::command]
fn quit_app(app: AppHandle) {
    app.exit(0);
}

fn build_tray(app: &tauri::App) -> tauri::Result<()> {
    let show_panel = MenuItem::with_id(app, "show-panel", "打开控制面板", true, None::<&str>)?;
    let show_pet = MenuItem::with_id(app, "show-pet", "显示桌宠", true, None::<&str>)?;
    let hide_pet = MenuItem::with_id(app, "hide-pet", "隐藏桌宠", true, None::<&str>)?;
    let quit = MenuItem::with_id(app, "quit", "退出蛋黄桌宠", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&show_panel, &show_pet, &hide_pet, &quit])?;
    let icon = app.default_window_icon().cloned();

    let mut builder = TrayIconBuilder::new()
        .tooltip("蛋黄桌宠")
        .menu(&menu)
        .show_menu_on_left_click(true)
        .on_menu_event(|app, event| match event.id.as_ref() {
            "show-panel" => {
                let _ = show_window(app, "main", true);
            }
            "show-pet" => {
                let _ = show_window(app, "pet", false);
            }
            "hide-pet" => {
                if let Some(window) = app.get_webview_window("pet") {
                    let _ = window.hide();
                }
            }
            "quit" => {
                app.exit(0);
            }
            _ => {}
        });

    if let Some(icon) = icon {
        builder = builder.icon(icon);
    }

    builder.build(app)?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            build_tray(app)?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_runtime_summary,
            update_settings,
            update_quick_menu_actions,
            update_ai_provider_state,
            switch_pet,
            update_pet_profile,
            upload_pet_image,
            upload_pet_action_strip,
            get_todos,
            create_todo,
            update_todo_state,
            update_todo_detail,
            record_todo_reminder,
            get_chat_messages,
            send_chat_message,
            get_pet_state,
            create_pet_story,
            get_runtime_asset,
            show_panel,
            show_pet,
            hide_pet,
            set_pet_always_on_top,
            quit_app
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn research_detection_skips_companion_chat() {
        assert!(!is_general_knowledge_query("你是谁？"));
        assert!(!is_research_query("我累了，陪我一下"));
    }

    #[test]
    fn research_detection_catches_tool_queries() {
        assert!(is_research_query("查一下 Tauri 是什么"));
        assert!(is_research_query("最新汇率是多少？"));
        assert!(is_general_knowledge_query("什么是透明窗口？"));
    }

    #[test]
    fn research_query_cleanup_keeps_core_terms() {
        assert_eq!(
            research_query_from_user_text("帮我查一下 Tauri 是什么？"),
            "Tauri"
        );
        assert_eq!(research_query_from_user_text("什么是 Live2D？"), "Live2D");
    }

    #[test]
    fn local_time_query_is_direct_reply() {
        assert!(is_time_query("现在几点了？"));
        assert!(local_time_reply("今天几号？").contains("主人，今天是"));
        assert!(local_time_reply("现在几点了？").contains("现在是"));
    }
}
