use base64::engine::general_purpose::STANDARD as BASE64;
use base64::Engine;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs;
use std::path::{Component, Path, PathBuf};
use tauri::menu::{Menu, MenuItem};
use tauri::tray::TrayIconBuilder;
use tauri::{AppHandle, Manager};

const RUNTIME_DIR: &str = "data-dev/current-runtime/danhuang";
const FAMILY_PATH: &str = "data-dev/current-runtime/danhuang/danhuang-failed-identity-backup-20260521-140133/pet-family.json";
const SETTINGS_PATH: &str = "data-dev/current-runtime/danhuang/desktop-pet-settings.json";
const MAX_ASSET_BYTES: u64 = 15 * 1024 * 1024;

#[derive(Debug, Deserialize)]
struct PetFamilyFile {
    #[serde(default)]
    current_pet_id: String,
    #[serde(default)]
    pets: Vec<PetEntryFile>,
}

#[derive(Debug, Deserialize)]
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
    action_pack_level: String,
    #[serde(default)]
    supported_actions: Vec<String>,
    #[serde(default)]
    extension_assets: Vec<ExtensionAssetFile>,
}

#[derive(Debug, Deserialize)]
struct ExtensionAssetFile {
    #[serde(default)]
    id: String,
}

#[derive(Debug, Deserialize)]
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
    talk_enabled: Option<bool>,
    #[serde(default)]
    roam_enabled: Option<bool>,
    #[serde(default)]
    quick_menu_actions: Vec<String>,
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
    checks: RuntimeChecks,
}

#[derive(Debug, Clone, Serialize)]
struct PetSummary {
    id: String,
    display_name: String,
    species: String,
    status: String,
    action_pack_level: String,
    supported_action_count: usize,
    extension_action_count: usize,
    identity_asset: Option<String>,
    spritesheet_asset: Option<String>,
    identity_available: bool,
    spritesheet_available: bool,
}

#[derive(Debug, Serialize)]
struct SafeSettingsSummary {
    scale: Option<f64>,
    animation_speed: Option<f64>,
    always_on_top: Option<bool>,
    bubble_style: Option<String>,
    talk_enabled: Option<bool>,
    roam_enabled: Option<bool>,
    quick_menu_action_count: usize,
}

#[derive(Debug, Serialize)]
struct RuntimeChecks {
    settings_loaded: bool,
    family_loaded: bool,
    sensitive_fields_returned: bool,
    notes: Vec<String>,
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
    let raw = fs::read_to_string(path).map_err(|err| format!("读取失败 {}: {}", path.display(), err))?;
    serde_json::from_str(&raw).map_err(|err| format!("JSON 解析失败 {}: {}", path.display(), err))
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
    if path
        .components()
        .any(|part| matches!(part, Component::ParentDir | Component::RootDir | Component::Prefix(_)))
    {
        return Err("资源路径不能包含上级目录或绝对路径".to_string());
    }

    let filename = path
        .file_name()
        .and_then(|name| name.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();
    let extension = path
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();

    let allowed_extension = matches!(extension.as_str(), "png" | "jpg" | "jpeg" | "webp");
    let allowed_name = filename == "identity-base.png"
        || filename == "spritesheet.webp"
        || filename.starts_with("extension-");
    let allowed_root_sprite = normalized == "spritesheet.webp";
    let blocked_private_area = normalized.contains("/uploads/") || normalized.starts_with("family-references/");

    if !allowed_extension || (!allowed_name && !allowed_root_sprite) || blocked_private_area {
        return Err("该资源不在前端预览白名单内".to_string());
    }

    Ok(normalized)
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

fn to_pet_summary(root: &Path, pet: &PetEntryFile) -> PetSummary {
    let identity_asset = safe_asset_path(&pet.identity_image).ok();
    let spritesheet_asset = safe_asset_path(&pet.spritesheet).ok();

    PetSummary {
        id: pet.id.clone(),
        display_name: pet.display_name.clone(),
        species: pet.species.clone(),
        status: pet.status.clone(),
        action_pack_level: pet.action_pack_level.clone(),
        supported_action_count: pet.supported_actions.len(),
        extension_action_count: pet
            .extension_assets
            .iter()
            .map(|item| item.id.as_str())
            .collect::<HashSet<_>>()
            .len(),
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

    let pets: Vec<PetSummary> = family.pets.iter().map(|pet| to_pet_summary(&root, pet)).collect();
    let current_pet = pets.iter().find(|pet| pet.id == current_pet_id).cloned();
    let ready_pet_count = pets.iter().filter(|pet| pet.status == "ready").count();
    let total_supported_actions = family.pets.iter().map(|pet| pet.supported_actions.len()).sum();
    let total_extension_assets = family.pets.iter().map(|pet| pet.extension_assets.len()).sum();

    let notes = vec![
        "只读取 E 盘 data-dev 运行镜像".to_string(),
        "未返回 API Key、Token、聊天、待办、提醒历史、本机导出路径".to_string(),
        "图片读取仅允许 identity、spritesheet 和 extension 动作条".to_string(),
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
        settings: SafeSettingsSummary {
            scale: settings.scale,
            animation_speed: settings.animation_speed,
            always_on_top: settings.always_on_top,
            bubble_style: settings.bubble_style,
            talk_enabled: settings.talk_enabled,
            roam_enabled: settings.roam_enabled,
            quick_menu_action_count: settings.quick_menu_actions.len(),
        },
        checks: RuntimeChecks {
            settings_loaded: settings_path.is_file(),
            family_loaded: family_path.is_file(),
            sensitive_fields_returned: false,
            notes,
        },
    })
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
    window.set_always_on_top(enabled).map_err(|err| err.to_string())
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
