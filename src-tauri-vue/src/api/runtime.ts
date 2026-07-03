import { invoke } from "@tauri-apps/api/core";
import type { RuntimeApi, RuntimeAsset, RuntimeSummary } from "../types/runtime";

declare global {
  interface Window {
    __TAURI_INTERNALS__?: unknown;
  }
}

const mockRuntime: RuntimeSummary = {
  runtime_available: false,
  runtime_source: "browser-preview",
  current_pet_id: "pet-20260520-112213",
  pet_count: 5,
  ready_pet_count: 5,
  total_supported_actions: 54,
  total_extension_assets: 11,
  current_pet: {
    id: "pet-20260520-112213",
    display_name: "胖久",
    species: "松狮",
    status: "ready",
    action_pack_level: "basic",
    supported_action_count: 11,
    extension_action_count: 6,
    identity_asset: null,
    spritesheet_asset: null,
    identity_available: false,
    spritesheet_available: false,
  },
  pets: [
    {
      id: "danhuang",
      display_name: "蛋黄",
      species: "dog",
      status: "ready",
      action_pack_level: "full",
      supported_action_count: 19,
      extension_action_count: 0,
      identity_asset: null,
      spritesheet_asset: null,
      identity_available: false,
      spritesheet_available: false,
    },
    {
      id: "pet-20260520-112213",
      display_name: "胖久",
      species: "松狮",
      status: "ready",
      action_pack_level: "basic",
      supported_action_count: 11,
      extension_action_count: 6,
      identity_asset: null,
      spritesheet_asset: null,
      identity_available: false,
      spritesheet_available: false,
    },
  ],
  settings: {
    scale: 0.46,
    animation_speed: 0.5,
    always_on_top: true,
    bubble_style: "thought",
    talk_enabled: true,
    roam_enabled: true,
    quick_menu_action_count: 14,
  },
  checks: {
    settings_loaded: false,
    family_loaded: false,
    sensitive_fields_returned: false,
    notes: ["浏览器预览使用 mock 数据；Tauri 运行时读取 E 盘 data-dev 镜像。"],
  },
};

const isTauri = () => typeof window !== "undefined" && Boolean(window.__TAURI_INTERNALS__);

export const runtimeApi: RuntimeApi = {
  async getRuntimeSummary() {
    if (!isTauri()) return mockRuntime;
    return invoke<RuntimeSummary>("get_runtime_summary");
  },

  async getRuntimeAsset(assetPath: string) {
    if (!isTauri()) {
      throw new Error("浏览器预览不读取本机运行镜像图片");
    }
    return invoke<RuntimeAsset>("get_runtime_asset", { assetPath });
  },

  async showPanel() {
    if (!isTauri()) return;
    await invoke("show_panel");
  },

  async showPet() {
    if (!isTauri()) return;
    await invoke("show_pet");
  },

  async hidePet() {
    if (!isTauri()) return;
    await invoke("hide_pet");
  },

  async setPetAlwaysOnTop(enabled: boolean) {
    if (!isTauri()) return;
    await invoke("set_pet_always_on_top", { enabled });
  },

  async quitApp() {
    if (!isTauri()) return;
    await invoke("quit_app");
  },
};
