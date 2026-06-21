export interface PetSummary {
  id: string;
  display_name: string;
  species: string;
  notes: string;
  status: string;
  action_pack_level: string;
  supported_action_count: number;
  extension_action_count: number;
  identity_asset: string | null;
  reference_assets: string[];
  spritesheet_asset: string | null;
  identity_available: boolean;
  spritesheet_available: boolean;
  actions: PetActionSummary[];
}

export interface PetActionSummary {
  id: string;
  label: string;
  source: "atlas" | "strip" | string;
  row: number | null;
  frames: number;
  durations: number[];
  asset: string | null;
}

export interface SafeSettingsSummary {
  scale: number | null;
  animation_speed: number | null;
  always_on_top: boolean | null;
  bubble_style: string | null;
  bubble_fill: string | null;
  bubble_outline: string | null;
  bubble_text: string | null;
  bubble_duration: number | null;
  talk_enabled: boolean | null;
  roam_enabled: boolean | null;
  drag_sensitivity: number | null;
  inertia: number | null;
  roam_speed: number | null;
  roam_distance: number | null;
  roam_interval: number | null;
  idle_action_interval: number | null;
  talk_interval: number | null;
  talk_after_interaction_delay: number | null;
  roam_allow_center: boolean | null;
  multi_monitor_roam: boolean | null;
  primary_monitor_edge_only: boolean | null;
  secondary_monitor_full_roam: boolean | null;
  roam_current_monitor_only: boolean | null;
  keep_on_screen: boolean | null;
  lock_size_across_monitors: boolean | null;
  quick_menu_action_count: number;
  quick_menu_actions: string[];
}

export interface RuntimeChecks {
  settings_loaded: boolean;
  family_loaded: boolean;
  sensitive_fields_returned: boolean;
  notes: string[];
}

export interface SafeProviderSummary {
  id: string;
  display_name: string;
  model: string;
  enabled: boolean;
  has_saved_key: boolean;
}

export interface FeatureSummary {
  providers: SafeProviderSummary[];
  active_provider: string;
  enabled_provider_count: number;
  saved_key_provider_count: number;
  todo_total: number;
  todo_open_count: number;
  todo_done_count: number;
  todo_pinned_count: number;
  reminder_event_count: number;
  story_count: number;
  memory_summary_available: boolean;
  companion_level: number | null;
  companion_xp: number | null;
  companion_interactions: number | null;
  companion_talks: number | null;
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
  features: FeatureSummary;
  checks: RuntimeChecks;
}

export interface RuntimeAsset {
  path: string;
  mime_type: string;
  data_url: string;
}

export interface TodoSummary {
  id: string;
  title: string;
  note: string;
  due_at: string;
  category: string;
  priority: string;
  repeat: string;
  status: string;
  pinned: boolean;
  important_interval_minutes: number;
  snooze_until: string;
  created_at: string;
  completed_at: string;
  last_reminded_at: string;
  updated_at: string;
  remind_count: number;
}

export interface CreateTodoInput {
  title: string;
  due_at: string;
  category?: string;
  priority?: string;
  now: string;
}

export interface UpdateTodoInput {
  id: string;
  done?: boolean;
  pinned?: boolean;
  snooze_until?: string;
  now: string;
}

export interface UpdateTodoDetailInput {
  id: string;
  title: string;
  due_at: string;
  category: string;
  priority: string;
  repeat: string;
  note: string;
  important_interval_minutes: number;
  now: string;
}

export interface RecordTodoReminderInput {
  id: string;
  now: string;
}

export interface ChatMessageSummary {
  id: string;
  time: string;
  user: string;
  mood: string;
  reply: string;
  source: string;
}

export interface SendChatMessageInput {
  text: string;
  role_style?: string;
  now: string;
}

export interface StoryEntrySummary {
  id: string;
  entry_type: string;
  title: string;
  content: string;
  content_preview: string;
  created_at: string;
  updated_at: string;
  pinned: boolean;
  image_count: number;
}

export interface MemorySummary {
  message_count: number;
  mood_counts: Record<string, number>;
  owner_profile: string;
  emotional_patterns: string[];
  preferences: string[];
  important_memories: string[];
  common_questions: string[];
  notes: string[];
  last_mood: string;
  updated_at: string;
}

export interface PetStateSummary {
  pet_id: string;
  stories: StoryEntrySummary[];
  prompt_summary: string;
  role_prompt: string;
  summary_updated_at: string;
  summary_source: string;
  memory: MemorySummary | null;
}

export interface CreatePetStoryInput {
  title: string;
  content: string;
  entry_type?: string;
  now: string;
}

export interface UpdateSettingsInput {
  scale?: number;
  animation_speed?: number;
  always_on_top?: boolean;
  bubble_style?: string;
  bubble_fill?: string;
  bubble_outline?: string;
  bubble_text?: string;
  bubble_duration?: number;
  talk_enabled?: boolean;
  roam_enabled?: boolean;
  drag_sensitivity?: number;
  inertia?: number;
  roam_speed?: number;
  roam_distance?: number;
  roam_interval?: number;
  idle_action_interval?: number;
  talk_interval?: number;
  talk_after_interaction_delay?: number;
  roam_allow_center?: boolean;
  multi_monitor_roam?: boolean;
  primary_monitor_edge_only?: boolean;
  secondary_monitor_full_roam?: boolean;
  roam_current_monitor_only?: boolean;
  keep_on_screen?: boolean;
  lock_size_across_monitors?: boolean;
}

export interface SwitchPetInput {
  pet_id: string;
}

export interface UpdatePetProfileInput {
  pet_id: string;
  display_name: string;
  species?: string;
  notes?: string;
}

export interface UploadPetImageInput {
  pet_id: string;
  kind: "identity" | "reference";
  file_name?: string;
  mime_type?: string;
  data_base64: string;
}

export interface UploadPetActionStripInput {
  pet_id: string;
  action_id: string;
  label: string;
  frames: number;
  durations?: number[];
  file_name?: string;
  mime_type?: string;
  data_base64: string;
}

export interface UpdateQuickMenuActionsInput {
  pet_id: string;
  action_ids: string[];
}

export interface UpdateAiProviderStateInput {
  provider_id: string;
  enabled?: boolean;
  make_active?: boolean;
}

export interface RuntimeApi {
  getRuntimeSummary(): Promise<RuntimeSummary>;
  getRuntimeAsset(assetPath: string): Promise<RuntimeAsset>;
  updateSettings(input: UpdateSettingsInput): Promise<SafeSettingsSummary>;
  updateQuickMenuActions(input: UpdateQuickMenuActionsInput): Promise<RuntimeSummary>;
  updateAiProviderState(input: UpdateAiProviderStateInput): Promise<RuntimeSummary>;
  switchPet(input: SwitchPetInput): Promise<RuntimeSummary>;
  updatePetProfile(input: UpdatePetProfileInput): Promise<RuntimeSummary>;
  uploadPetImage(input: UploadPetImageInput): Promise<RuntimeSummary>;
  uploadPetActionStrip(input: UploadPetActionStripInput): Promise<RuntimeSummary>;
  getTodos(): Promise<TodoSummary[]>;
  createTodo(input: CreateTodoInput): Promise<TodoSummary>;
  updateTodoState(input: UpdateTodoInput): Promise<TodoSummary>;
  updateTodoDetail(input: UpdateTodoDetailInput): Promise<TodoSummary>;
  recordTodoReminder(input: RecordTodoReminderInput): Promise<TodoSummary>;
  getChatMessages(): Promise<ChatMessageSummary[]>;
  sendChatMessage(input: SendChatMessageInput): Promise<ChatMessageSummary>;
  getPetState(): Promise<PetStateSummary>;
  createPetStory(input: CreatePetStoryInput): Promise<PetStateSummary>;
  showPanel(): Promise<void>;
  showPet(): Promise<void>;
  hidePet(): Promise<void>;
  setPetAlwaysOnTop(enabled: boolean): Promise<void>;
  quitApp(): Promise<void>;
}
