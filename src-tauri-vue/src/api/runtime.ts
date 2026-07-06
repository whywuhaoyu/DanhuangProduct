import { invoke } from "@tauri-apps/api/core";
import type {
  ChatMessageSummary,
  CreatePetStoryInput,
  CreateTodoInput,
  AiProviderTestResult,
  PetStateSummary,
  PetSummary,
  RecordTodoReminderInput,
  RuntimeApi,
  RuntimeAsset,
  RuntimeSummary,
  SafeSettingsSummary,
  SendChatMessageInput,
  SwitchPetInput,
  ClearPetActionStripInput,
  SecurityActionInput,
  SecurityActionResult,
  TodoSummary,
  UploadPetActionStripInput,
  UploadPetImageInput,
  UpdateAiProviderStateInput,
  UpdateAiProviderKeyInput,
  TestAiProviderInput,
  UpdatePetProfileInput,
  UpdateQuickMenuActionsInput,
  UpdateSettingsInput,
  UpdateTodoDetailInput,
  UpdateTodoInput,
} from "../types/runtime";

declare global {
  interface Window {
    __TAURI_INTERNALS__?: unknown;
  }
}

function atlasAction(id: string, label: string, row: number, frames: number, durations: number[]) {
  return { id, label, source: "atlas", row, frames, durations, asset: null };
}

function stripAction(id: string, label: string, asset: string, frames: number) {
  return {
    id,
    label,
    source: "strip",
    row: null,
    frames,
    durations: Array.from({ length: frames }, () => 160),
    asset,
  };
}

const demoCoreActions = [
  atlasAction("idle", "待机", 0, 6, [260, 150, 150, 170, 170, 320]),
  atlasAction("running-right", "向右跑", 1, 8, [58, 54, 50, 54, 58, 50, 54, 68]),
  atlasAction("running-left", "向左跑", 2, 8, [58, 54, 50, 54, 58, 50, 54, 68]),
  atlasAction("waving", "挥爪", 3, 4, [170, 120, 120, 220]),
  atlasAction("jumping", "跳一下", 4, 5, [80, 75, 90, 95, 140]),
];

const demoStandardActions = [
  ...demoCoreActions,
  atlasAction("failed", "委屈一下", 5, 8, [120, 100, 120, 140, 160, 180, 180, 260]),
  atlasAction("waiting", "等一下", 6, 6, [220, 180, 180, 220, 180, 260]),
  atlasAction("running", "跑一小段", 7, 6, [62, 58, 54, 58, 62, 74]),
  atlasAction("review", "陪我一会", 8, 6, [210, 190, 220, 190, 190, 260]),
];

const demoFullActions = [
  ...demoStandardActions,
  atlasAction("standing", "站一会", 9, 8, [240, 220, 260, 220, 280, 220, 240, 320]),
  atlasAction("tongue", "吐舌头", 10, 8, [140, 140, 150, 150, 150, 150, 160, 220]),
  atlasAction("lying", "卧倒", 11, 8, [190, 190, 230, 260, 260, 300, 300, 360]),
  atlasAction("stretching", "伸懒腰", 12, 8, [130, 140, 150, 170, 190, 180, 170, 230]),
  atlasAction("sleeping", "打个盹", 13, 8, [420, 480, 460, 520, 480, 540, 500, 560]),
  atlasAction("sniffing", "闻一闻", 14, 8, [130, 130, 140, 150, 170, 170, 160, 220]),
  atlasAction("rolling", "打个滚", 15, 8, [120, 110, 110, 115, 115, 110, 120, 180]),
  atlasAction("crying", "哭一下", 16, 8, [220, 200, 210, 230, 250, 230, 210, 300]),
  atlasAction("chase-butterfly", "追蝴蝶", 17, 8, [72, 66, 62, 66, 72, 66, 62, 88]),
  atlasAction("angry", "生气一下", 18, 8, [130, 110, 130, 110, 170, 140, 140, 240]),
];

const demoPets: PetSummary[] = [
  {
    id: "danhuang",
    display_name: "蛋黄",
    pet_type: "dog",
    pet_type_label: "狗狗",
    pet_tags: ["纪念陪伴", "完整动作"],
    species: "小狗",
    notes: "内置完整动作包，首次启动即可显示、对话、提醒和巡游。",
    status: "ready",
    action_pack_level: "full",
    supported_action_count: 19,
    extension_action_count: 0,
    identity_asset: null,
    reference_assets: ["family/danhuang/uploads/user-1-01.jpg"],
    spritesheet_asset: "spritesheet.webp",
    identity_available: false,
    spritesheet_available: true,
    actions: demoFullActions,
  },
  {
    id: "black_white_dog",
    display_name: "小墨",
    pet_type: "dog",
    pet_type_label: "狗狗",
    pet_tags: ["安静", "基础动作"],
    species: "小狗",
    notes: "黑白小狗形象，已内置基础动作，可直接切换到桌面。",
    status: "ready",
    action_pack_level: "basic",
    supported_action_count: 5,
    extension_action_count: 0,
    identity_asset: "family/xiao-mo/identity-base.png",
    reference_assets: ["family-references/black-white-dog.jpg"],
    spritesheet_asset: "family/xiao-mo/spritesheet.webp",
    identity_available: true,
    spritesheet_available: true,
    actions: demoCoreActions,
  },
  {
    id: "orange_cat",
    display_name: "橘宝",
    pet_type: "cat",
    pet_type_label: "猫咪",
    pet_tags: ["猫咪", "特色动作"],
    species: "小猫",
    notes: "橘猫形象，带舔爪、舔毛和洗脸三个特色动作。",
    status: "ready",
    action_pack_level: "basic",
    supported_action_count: 8,
    extension_action_count: 3,
    identity_asset: "family/ju-bao/identity-base.png",
    reference_assets: ["family-references/orange-cat-and-hugging-dog.jpg"],
    spritesheet_asset: "family/ju-bao/spritesheet.webp",
    identity_available: true,
    spritesheet_available: true,
    actions: [
      ...demoCoreActions,
      stripAction("custom:licking-paw", "舔爪", "family/ju-bao/extension-custom-licking-paw.webp", 4),
      stripAction("custom:licking-fur", "舔毛", "family/ju-bao/extension-custom-licking-fur.webp", 4),
      stripAction("custom:washing-face", "洗脸", "family/ju-bao/extension-custom-washing-face.webp", 4),
    ],
  },
  {
    id: "hugging_dog",
    display_name: "小白",
    pet_type: "dog",
    pet_type_label: "狗狗",
    pet_tags: ["温和", "基础动作"],
    species: "小狗",
    notes: "拥抱小狗形象，已内置基础动作，可直接切换到桌面。",
    status: "ready",
    action_pack_level: "basic",
    supported_action_count: 5,
    extension_action_count: 0,
    identity_asset: "family/xiao-bai/identity-base.png",
    reference_assets: ["family-references/orange-cat-and-hugging-dog.jpg"],
    spritesheet_asset: "family/xiao-bai/spritesheet.webp",
    identity_available: true,
    spritesheet_available: true,
    actions: demoCoreActions,
  },
  {
    id: "pet-20260520-112213",
    display_name: "胖久",
    pet_type: "dog",
    pet_type_label: "狗狗",
    pet_tags: ["松狮", "特色动作"],
    species: "松狮",
    notes: "奶油色松狮小狗，已内置基础动作和 8 个特色动作。",
    status: "ready",
    action_pack_level: "basic",
    supported_action_count: 13,
    extension_action_count: 8,
    identity_asset: "family/pet-20260520-112213/identity-base.png",
    reference_assets: [
      "family/pet-20260520-112213/uploads/user-1-01.jpg",
      "family/pet-20260520-112213/uploads/user-2-01.jpg",
    ],
    spritesheet_asset: "family/pet-20260520-112213/spritesheet.webp",
    identity_available: true,
    spritesheet_available: true,
    actions: [
      ...demoCoreActions,
      stripAction("custom:petting", "摸摸头", "family/pet-20260520-112213/extension-custom-petting.webp", 4),
      stripAction("custom:licking-paw", "舔爪", "family/pet-20260520-112213/extension-custom-licking-paw.webp", 4),
      stripAction("custom:yawning", "打哈欠", "family/pet-20260520-112213/extension-custom-yawning.webp", 4),
      stripAction("tongue", "吐舌头", "family/pet-20260520-112213/extension-tongue.webp", 6),
      stripAction("stretching", "伸懒腰", "family/pet-20260520-112213/extension-stretching.webp", 5),
      stripAction("sleeping", "打个盹", "family/pet-20260520-112213/extension-sleeping.webp", 6),
      stripAction("chase-butterfly", "追蝴蝶", "family/pet-20260520-112213/extension-chase-butterfly.webp", 8),
      stripAction("sniffing", "闻一闻", "family/pet-20260520-112213/extension-sniffing.webp", 8),
    ],
  },
  {
    id: "ikun_duck",
    display_name: "小坤",
    pet_type: "meme",
    pet_type_label: "梗系",
    pet_tags: ["唱跳Rap", "篮球", "特色动作"],
    species: "黄鸭",
    notes: "梗系黄鸭形象，灰色中分发型、黑色连帽衫和篮球是主要识别点，带打篮球、唱、跳、Rap、打招呼和认真工作六个特色动作。",
    status: "ready",
    action_pack_level: "basic",
    supported_action_count: 15,
    extension_action_count: 6,
    identity_asset: "family/ikun_duck/identity-base.png",
    reference_assets: ["family/ikun_duck/identity-base.png"],
    spritesheet_asset: "family/ikun_duck/spritesheet.webp",
    identity_available: true,
    spritesheet_available: true,
    actions: [
      ...demoStandardActions,
      stripAction("custom:basketball", "打篮球", "family/ikun_duck/extension-custom-basketball.webp", 8),
      stripAction("custom:sing", "唱", "family/ikun_duck/extension-custom-sing.webp", 4),
      stripAction("custom:dance", "跳", "family/ikun_duck/extension-custom-dance.webp", 6),
      stripAction("custom:rap", "Rap", "family/ikun_duck/extension-custom-rap.webp", 4),
      stripAction("custom:greeting", "打招呼", "family/ikun_duck/extension-custom-greeting.webp", 4),
      stripAction("custom:working", "认真工作", "family/ikun_duck/extension-custom-working.webp", 6),
    ],
  },
];

const mockRuntime: RuntimeSummary = {
  runtime_available: false,
  runtime_source: "体验预览",
  current_pet_id: "danhuang",
  pet_count: demoPets.length,
  ready_pet_count: demoPets.length,
  total_supported_actions: demoPets.reduce((total, pet) => total + pet.supported_action_count, 0),
  total_extension_assets: demoPets.reduce((total, pet) => total + pet.extension_action_count, 0),
  current_pet: demoPets[0],
  pets: demoPets,
  settings: {
    scale: 0.46,
    animation_speed: 0.5,
    always_on_top: true,
    bubble_style: "thought",
    bubble_fill: "#fffaf0",
    bubble_outline: "#d8a760",
    bubble_text: "#3b3024",
    bubble_duration: 6,
    talk_enabled: true,
    roam_enabled: true,
    drag_sensitivity: 0.55,
    inertia: 0.2,
    roam_speed: 75,
    roam_distance: 0.35,
    roam_interval: 100,
    idle_action_interval: 8,
    talk_interval: 90,
    talk_after_interaction_delay: 10,
    roam_allow_center: false,
    multi_monitor_roam: true,
    primary_monitor_edge_only: false,
    secondary_monitor_full_roam: true,
    roam_current_monitor_only: false,
    keep_on_screen: true,
    lock_size_across_monitors: true,
    click_through_enabled: false,
    quick_menu_action_count: 5,
    quick_menu_actions: [
      "idle",
      "running-right",
      "running-left",
      "waving",
      "jumping",
    ],
  },
  features: {
    providers: [
      { id: "openai", display_name: "OpenAI", model: "gpt-5", enabled: false, has_saved_key: false },
      { id: "deepseek", display_name: "DeepSeek", model: "deepseek-chat", enabled: true, has_saved_key: true },
      { id: "kimi", display_name: "Kimi", model: "moonshot-v1", enabled: false, has_saved_key: false },
    ],
    active_provider: "deepseek",
    enabled_provider_count: 1,
    saved_key_provider_count: 1,
    todo_total: 3,
    todo_open_count: 2,
    todo_done_count: 1,
    todo_pinned_count: 1,
    reminder_event_count: 8,
    story_count: 2,
    memory_summary_available: true,
    companion_level: 7,
    companion_xp: 1680,
    companion_interactions: 128,
    companion_talks: 42,
  },
  checks: {
    settings_loaded: false,
    family_loaded: false,
    sensitive_fields_returned: false,
    notes: ["体验预览使用 5 个内置宠物素材；桌面版会在本机数据目录初始化同一套宠物。"],
  },
};

function cloneMockRuntime() {
  return JSON.parse(JSON.stringify(mockRuntime)) as RuntimeSummary;
}

let mockTodos: TodoSummary[] = [
  {
    id: "ui-baseline",
    title: "把前端基础版 UI 跑通",
    note: "确认主题、面板和桌宠窗口基础交互。",
    due_at: "今日 18:30",
    category: "产品",
    priority: "重要",
    repeat: "none",
    status: "open",
    pinned: true,
    important_interval_minutes: 30,
    snooze_until: "",
    created_at: "体验演示",
    completed_at: "",
    last_reminded_at: "",
    updated_at: "体验演示",
    remind_count: 0,
  },
  {
    id: "screenshot",
    title: "确认桌宠第一眼可见",
    note: "检查小窗口、右键菜单和控制面板都能直接使用。",
    due_at: "明天",
    category: "QA",
    priority: "普通",
    repeat: "none",
    status: "open",
    pinned: false,
    important_interval_minutes: 0,
    snooze_until: "",
    created_at: "体验演示",
    completed_at: "",
    last_reminded_at: "",
    updated_at: "体验演示",
    remind_count: 0,
  },
  {
    id: "privacy",
    title: "检查公开包隐私排除清单",
    note: "公开包不得包含聊天、提醒历史、Key 和本机绝对路径。",
    due_at: "本周",
    category: "安全",
    priority: "安全",
    repeat: "每次导出",
    status: "open",
    pinned: true,
    important_interval_minutes: 60,
    snooze_until: "",
    created_at: "体验演示",
    completed_at: "",
    last_reminded_at: "",
    updated_at: "体验演示",
    remind_count: 0,
  },
];

let mockChatMessages: ChatMessageSummary[] = [
  {
    id: "browser-chat-1",
    time: "体验演示",
    user: "主人有点累了",
    mood: "tired",
    reply: "主人，先把肩膀放下来。我在这里陪你，慢慢做完这一点就好。",
    source: "ai:deepseek",
  },
  {
    id: "browser-chat-2",
    time: "体验演示",
    user: "明天记得提醒我买狗粮",
    mood: "question",
    reply: "好呀，主人可以在提醒页添加时间；我会在本机帮你记住，不会把提醒打进公开包。",
    source: "local",
  },
];

let mockPetState: PetStateSummary = {
  pet_id: "danhuang",
  stories: [
    {
      id: "browser-story-1",
      entry_type: "story",
      title: "我与胖久",
      content: "胖久从东北一路来到主人身边，慢慢建立起信任。它不爱洗澡，但很爱干净，也会在门口等主人回家。",
      content_preview: "胖久从东北一路来到主人身边，慢慢建立起信任。它不爱洗澡，但很爱干净，也会在门口等主人回家。",
      created_at: "体验演示",
      updated_at: "体验演示",
      pinned: false,
      image_count: 1,
    },
  ],
  prompt_summary: "胖久是一只奶油色松狮小狗，从东北远道而来，是主人家里安静、慢热又柔软的陪伴者。",
  role_prompt: "我叫胖久，是一只奶油色的松狮小狗，住在主人的电脑桌面右下角。",
  summary_updated_at: "体验演示",
  summary_source: "体验演示",
  memory: {
    message_count: 14,
    mood_counts: { ask_memory: 5, quiet: 3, thanks: 2 },
    owner_profile: "",
    emotional_patterns: ["ask_memory: 你还记得我们的故事吗", "stressed: 主人压力有点大"],
    preferences: [],
    important_memories: [],
    common_questions: ["你还记得我们的故事吗", "你还记得你的名字吗"],
    notes: [],
    last_mood: "ask_memory",
    updated_at: "体验演示",
  },
};

const isTauri = () => typeof window !== "undefined" && Boolean(window.__TAURI_INTERNALS__);

function classifyMockMood(text: string) {
  if (text.includes("想") || text.includes("蛋黄")) return "miss";
  if (text.includes("累") || text.includes("休息")) return "tired";
  if (text.includes("难过") || text.includes("哭")) return "sad";
  if (text.includes("开心") || text.includes("完成")) return "happy";
  return "quiet";
}

function mockReplyForMood(mood: string) {
  const replies: Record<string, string> = {
    miss: "你想我的时候，我就摇摇尾巴。",
    tired: "我趴着等你，先喝口水。",
    sad: "不用马上好起来，我陪你慢慢待着。",
    happy: "主人开心，我也开心。",
    quiet: "我在这里，轻轻陪你一会儿。",
  };
  return replies[mood] ?? replies.quiet;
}

function syncMockTodoCounts() {
  mockRuntime.features.todo_total = mockTodos.length;
  mockRuntime.features.todo_open_count = mockTodos.filter((todo) => todo.status !== "done" && todo.status !== "deleted").length;
  mockRuntime.features.todo_done_count = mockTodos.filter((todo) => todo.status === "done").length;
  mockRuntime.features.todo_pinned_count = mockTodos.filter((todo) => todo.pinned || todo.priority === "重要" || todo.priority === "安全").length;
}

export const runtimeApi: RuntimeApi = {
  async getRuntimeSummary() {
    if (!isTauri()) {
      syncMockTodoCounts();
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("get_runtime_summary");
  },

  async getRuntimeAsset(assetPath: string) {
    if (!isTauri()) {
      const normalized = assetPath.replace(/\\/g, "/").replace(/^\/+/, "").trim();
      if (!normalized || normalized.includes("..") || normalized.includes(":")) {
        throw new Error("素材路径不在体验预览范围内");
      }
      const extension = normalized.split(".").pop()?.toLowerCase();
      const mimeType =
        extension === "png" ? "image/png" : extension === "jpg" || extension === "jpeg" ? "image/jpeg" : "image/webp";
      return {
        path: normalized,
        mime_type: mimeType,
        data_url: `/src-tauri/builtin-runtime/danhuang/${normalized}`,
      };
    }
    return invoke<RuntimeAsset>("get_runtime_asset", { assetPath });
  },

  async updateSettings(input: UpdateSettingsInput) {
    if (!isTauri()) {
      mockRuntime.settings = {
        ...mockRuntime.settings,
        ...input,
      };
      return mockRuntime.settings as SafeSettingsSummary;
    }
    return invoke<SafeSettingsSummary>("update_settings", { input });
  },

  async updateQuickMenuActions(input: UpdateQuickMenuActionsInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("体验演示没有这个宠物资料");
      const available = new Set(target.actions.map((action) => action.id));
      const actionIds = input.action_ids.filter((id, index, source) => available.has(id) && source.indexOf(id) === index).slice(0, 16);
      if (!actionIds.length) throw new Error("右键动作栏至少保留 1 个动作");
      mockRuntime.settings.quick_menu_actions = actionIds;
      mockRuntime.settings.quick_menu_action_count = actionIds.length;
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("update_quick_menu_actions", { input });
  },

  async updateAiProviderState(input: UpdateAiProviderStateInput) {
    if (!isTauri()) {
      const providers = mockRuntime.features.providers.map((provider) => {
        if (provider.id !== input.provider_id) return provider;
        return {
          ...provider,
          enabled: input.make_active ? true : input.enabled ?? provider.enabled,
        };
      });
      let activeProvider = mockRuntime.features.active_provider;
      if (input.make_active) {
        activeProvider = input.provider_id;
      }
      const active = providers.find((provider) => provider.id === activeProvider);
      if (active && !active.enabled) {
        activeProvider = providers.find((provider) => provider.enabled)?.id ?? "";
      }
      mockRuntime.features.providers = providers;
      mockRuntime.features.active_provider = activeProvider;
      mockRuntime.features.enabled_provider_count = providers.filter((provider) => provider.enabled).length;
      mockRuntime.features.saved_key_provider_count = providers.filter((provider) => provider.has_saved_key).length;
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("update_ai_provider_state", { input });
  },

  async updateAiProviderKey(input: UpdateAiProviderKeyInput) {
    if (!isTauri()) {
      const providers = mockRuntime.features.providers.map((provider) =>
        provider.id === input.provider_id
          ? {
              ...provider,
              enabled: input.clear ? provider.enabled : true,
              has_saved_key: input.clear ? false : true,
            }
          : provider,
      );
      mockRuntime.features.providers = providers;
      mockRuntime.features.saved_key_provider_count = providers.filter((provider) => provider.has_saved_key).length;
      if (!input.clear) {
        mockRuntime.features.active_provider = input.provider_id;
      }
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("update_ai_provider_key", { input });
  },

  async testAiProviderConnection(input: TestAiProviderInput) {
    if (!isTauri()) {
      const provider = mockRuntime.features.providers.find((item) => item.id === input.provider_id);
      const providerName = provider?.display_name ?? input.provider_id;
      return {
        provider_id: input.provider_id,
        ok: Boolean(provider?.has_saved_key),
        title: provider?.has_saved_key ? "连接可用" : "缺少 Key",
        message: provider?.has_saved_key
          ? `${providerName} 的体验预览连接状态可用。桌面版会发送一条不落盘的真实测试请求。`
          : `${providerName} 还没有保存 Key。`,
        details: provider?.has_saved_key
          ? [`模型: ${provider.model || "默认模型"}`, "体验预览不会真实联网。"]
          : ["先保存 Key，再点测试连接。"],
      } satisfies AiProviderTestResult;
    }
    return invoke<AiProviderTestResult>("test_ai_provider_connection", { input });
  },

  async switchPet(input: SwitchPetInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id && pet.status === "ready");
      if (!target) throw new Error("体验演示没有这个可切换宠物");
      mockRuntime.current_pet_id = target.id;
      mockRuntime.current_pet = target;
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("switch_pet", { input });
  },

  async updatePetProfile(input: UpdatePetProfileInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("体验演示没有这个宠物资料");
      target.display_name = input.display_name;
      target.species = input.species ?? "";
      target.notes = input.notes ?? "";
      if (mockRuntime.current_pet_id === target.id) {
        mockRuntime.current_pet = target;
      }
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("update_pet_profile", { input });
  },

  async uploadPetImage(input: UploadPetImageInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("体验演示没有这个宠物资料");
      const mockPath =
        input.kind === "identity"
          ? `family/${input.pet_id}/identity-base.png`
          : `family/${input.pet_id}/uploads/user-demo.png`;
      if (input.kind === "identity") {
        target.identity_asset = mockPath;
        target.identity_available = true;
      } else {
        target.reference_assets = [mockPath, ...target.reference_assets.filter((path) => path !== mockPath)];
      }
      if (mockRuntime.current_pet_id === target.id) {
        mockRuntime.current_pet = target;
      }
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("upload_pet_image", { input });
  },

  async uploadPetActionStrip(input: UploadPetActionStripInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("体验演示没有这个宠物资料");
      const action = {
        id: input.action_id,
        label: input.label,
        source: "strip",
        row: null,
        frames: input.frames,
        durations: input.durations?.length ? input.durations : Array.from({ length: input.frames }, () => 180),
        asset: `family/${input.pet_id}/extension-${input.action_id.replace(/:/g, "-")}.webp`,
      };
      target.actions = [action, ...target.actions.filter((item) => item.id !== input.action_id)];
      target.supported_action_count = target.actions.length;
      target.extension_action_count = target.actions.filter((item) => item.source === "strip").length;
      mockRuntime.total_supported_actions = mockRuntime.pets.reduce((total, pet) => total + pet.supported_action_count, 0);
      mockRuntime.total_extension_assets = mockRuntime.pets.reduce((total, pet) => total + pet.extension_action_count, 0);
      if (mockRuntime.current_pet_id === target.id) {
        mockRuntime.current_pet = target;
      }
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("upload_pet_action_strip", { input });
  },

  async clearPetActionStrip(input: ClearPetActionStripInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("体验演示没有这个宠物资料");
      target.actions = target.actions.filter((item) => item.id !== input.action_id);
      target.supported_action_count = target.actions.length;
      target.extension_action_count = target.actions.filter((item) => item.source === "strip").length;
      mockRuntime.settings.quick_menu_actions = mockRuntime.settings.quick_menu_actions.filter((id) => id !== input.action_id);
      mockRuntime.settings.quick_menu_action_count = mockRuntime.settings.quick_menu_actions.length;
      mockRuntime.total_supported_actions = mockRuntime.pets.reduce((total, pet) => total + pet.supported_action_count, 0);
      mockRuntime.total_extension_assets = mockRuntime.pets.reduce((total, pet) => total + pet.extension_action_count, 0);
      if (mockRuntime.current_pet_id === target.id) {
        mockRuntime.current_pet = target;
      }
      return cloneMockRuntime();
    }
    return invoke<RuntimeSummary>("clear_pet_action_strip", { input });
  },

  async getTodos() {
    if (!isTauri()) return mockTodos;
    return invoke<TodoSummary[]>("get_todos");
  },

  async createTodo(input: CreateTodoInput) {
    if (!isTauri()) {
      const todo: TodoSummary = {
        id: `local-${Date.now()}`,
        title: input.title,
        note: "",
        due_at: input.due_at || "稍后",
        category: input.category ?? "本地",
        priority: input.priority ?? "普通",
        repeat: "none",
        status: "open",
        pinned: false,
        important_interval_minutes: 0,
        snooze_until: "",
        created_at: input.now,
        completed_at: "",
        last_reminded_at: "",
        updated_at: input.now,
        remind_count: 0,
      };
      mockTodos = [todo, ...mockTodos];
      syncMockTodoCounts();
      return todo;
    }
    return invoke<TodoSummary>("create_todo", { input });
  },

  async updateTodoState(input: UpdateTodoInput) {
    if (!isTauri()) {
      const updated = mockTodos.map((todo) => {
        if (todo.id !== input.id) return todo;
        return {
          ...todo,
          status: input.deleted ? "deleted" : input.done === undefined ? todo.status : input.done ? "done" : "open",
          completed_at: input.done ? input.now : input.done === false ? "" : todo.completed_at,
          pinned: input.pinned ?? todo.pinned,
          snooze_until: input.snooze_until ?? todo.snooze_until,
          updated_at: input.now,
        };
      });
      mockTodos = updated;
      syncMockTodoCounts();
      const todo = mockTodos.find((item) => item.id === input.id);
      if (!todo) throw new Error("未找到可更新的提醒");
      return todo;
    }
    return invoke<TodoSummary>("update_todo_state", { input });
  },

  async updateTodoDetail(input: UpdateTodoDetailInput) {
    if (!isTauri()) {
      mockTodos = mockTodos.map((todo) =>
        todo.id === input.id
          ? {
              ...todo,
              title: input.title,
              due_at: input.due_at,
              category: input.category,
              priority: input.priority,
              repeat: input.repeat,
              note: input.note,
              important_interval_minutes: input.important_interval_minutes,
              updated_at: input.now,
            }
          : todo,
      );
      syncMockTodoCounts();
      const todo = mockTodos.find((item) => item.id === input.id);
      if (!todo) throw new Error("未找到可编辑的提醒");
      return todo;
    }
    return invoke<TodoSummary>("update_todo_detail", { input });
  },

  async recordTodoReminder(input: RecordTodoReminderInput) {
    if (!isTauri()) {
      mockTodos = mockTodos.map((todo) =>
        todo.id === input.id
          ? {
              ...todo,
              last_reminded_at: input.now,
              remind_count: todo.remind_count + 1,
              snooze_until: "",
              updated_at: input.now,
            }
          : todo,
      );
      syncMockTodoCounts();
      const todo = mockTodos.find((item) => item.id === input.id);
      if (!todo) throw new Error("未找到可记录的提醒");
      return todo;
    }
    return invoke<TodoSummary>("record_todo_reminder", { input });
  },

  async getChatMessages() {
    if (!isTauri()) return mockChatMessages;
    return invoke<ChatMessageSummary[]>("get_chat_messages");
  },

  async sendChatMessage(input: SendChatMessageInput) {
    if (!isTauri()) {
      const mood = classifyMockMood(input.text);
      const isResearch = /查|搜索|资料|什么是|是什么|谁是|最新|新闻|天气|汇率|股价/.test(input.text);
      const item: ChatMessageSummary = {
        id: `browser-chat-${Date.now()}`,
        time: input.now,
        user: input.text,
        mood,
        reply: isResearch
          ? "主人，我先帮你查到这些：体验演示不会联网，桌面版会由本机后端受控查询资料摘要，再交给 AI 或本地兜底回答。"
          : mockReplyForMood(mood),
        source: isResearch ? "research-fallback:experience" : input.role_style ? `local:${input.role_style}` : "local",
      };
      mockChatMessages = [...mockChatMessages, item].slice(-30);
      return item;
    }
    return invoke<ChatMessageSummary>("send_chat_message", { input });
  },

  async getPetState() {
    if (!isTauri()) return mockPetState;
    return invoke<PetStateSummary>("get_pet_state");
  },

  async createPetStory(input: CreatePetStoryInput) {
    if (!isTauri()) {
      const content = input.content.trim();
      const story = {
        id: `browser-story-${Date.now()}`,
        entry_type: input.entry_type ?? "story",
        title: input.title.trim(),
        content,
        content_preview: content.slice(0, 120),
        created_at: input.now,
        updated_at: input.now,
        pinned: false,
        image_count: 0,
      };
      mockPetState = {
        ...mockPetState,
        stories: [story, ...mockPetState.stories],
        summary_updated_at: input.now,
        summary_source: "local_story",
      };
      return mockPetState;
    }
    return invoke<PetStateSummary>("create_pet_story", { input });
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

  async setPetClickThrough(enabled: boolean) {
    if (!isTauri()) {
      mockRuntime.settings.click_through_enabled = enabled;
      return;
    }
    await invoke("set_pet_click_through", { enabled });
  },

  async refreshPetWindow() {
    if (!isTauri()) return;
    await invoke("refresh_pet_window");
  },

  async runSecurityAction(input: SecurityActionInput) {
    if (!isTauri()) {
      const result: SecurityActionResult = {
        title:
          input.action === "personal-backup"
            ? "个人备份演示"
            : input.action === "open-data-dir"
              ? "数据目录演示"
              : input.action === "installer-status"
                ? "安装包状态演示"
                : "公开包检查演示",
        message: "体验演示不会读取或写入本机文件；桌面版会通过受控本地操作执行。",
        tone: "info",
        items: [
          "聊天、提醒、记忆、日志和 Key 不进入公开包。",
          "个人备份只写入本机数据目录副本。",
          "安装包默认不要求额外运行环境或手工复制文件。",
        ],
      };
      return result;
    }
    return invoke<SecurityActionResult>("run_security_action", { input });
  },

  async quitApp() {
    if (!isTauri()) return;
    await invoke("quit_app");
  },
};
