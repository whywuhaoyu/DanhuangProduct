export interface PetSummary {
  id: string;
  display_name: string;
  species: string;
  status: string;
  action_pack_level: string;
  supported_action_count: number;
  extension_action_count: number;
  identity_asset: string | null;
  spritesheet_asset: string | null;
  identity_available: boolean;
  spritesheet_available: boolean;
}

export interface SafeSettingsSummary {
  scale: number | null;
  animation_speed: number | null;
  always_on_top: boolean | null;
  bubble_style: string | null;
  talk_enabled: boolean | null;
  roam_enabled: boolean | null;
  quick_menu_action_count: number;
}

export interface RuntimeChecks {
  settings_loaded: boolean;
  family_loaded: boolean;
  sensitive_fields_returned: boolean;
  notes: string[];
}

export interface RuntimeSummary {
  runtime_available: boolean;
  runtime_source: string;
  current_pet_id: string;
  pet_count: number;
  ready_pet_count: number;
  total_supported_actions: number;
  total_extension_assets: number;
  current_pet: PetSummary | null;
  pets: PetSummary[];
  settings: SafeSettingsSummary;
  checks: RuntimeChecks;
}

export interface RuntimeAsset {
  path: string;
  mime_type: string;
  data_url: string;
}

export interface RuntimeApi {
  getRuntimeSummary(): Promise<RuntimeSummary>;
  getRuntimeAsset(assetPath: string): Promise<RuntimeAsset>;
  showPanel(): Promise<void>;
  showPet(): Promise<void>;
  hidePet(): Promise<void>;
  setPetAlwaysOnTop(enabled: boolean): Promise<void>;
  quitApp(): Promise<void>;
}
