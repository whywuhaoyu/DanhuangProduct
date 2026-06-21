import { invoke } from "@tauri-apps/api/core";
import type {
  ChatMessageSummary,
  CreatePetStoryInput,
  CreateTodoInput,
  PetStateSummary,
  RecordTodoReminderInput,
  RuntimeApi,
  RuntimeAsset,
  RuntimeSummary,
  SafeSettingsSummary,
  SendChatMessageInput,
  SwitchPetInput,
  TodoSummary,
  UploadPetActionStripInput,
  UploadPetImageInput,
  UpdateAiProviderStateInput,
  UpdateAiProviderKeyInput,
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
    notes: "奶油色松狮小狗，圆脸厚毛、粉棕鼻、灰色胸背带。",
    status: "ready",
    action_pack_level: "basic",
    supported_action_count: 11,
    extension_action_count: 6,
    identity_asset: null,
    reference_assets: [],
    spritesheet_asset: null,
    identity_available: false,
    spritesheet_available: false,
    actions: [
      { id: "idle", label: "待机", source: "atlas", row: 0, frames: 6, durations: [260, 150, 150, 170, 170, 320], asset: null },
      { id: "running-right", label: "向右跑", source: "atlas", row: 1, frames: 8, durations: [58, 54, 50, 54, 58, 50, 54, 68], asset: null },
      { id: "running-left", label: "向左跑", source: "atlas", row: 2, frames: 8, durations: [58, 54, 50, 54, 58, 50, 54, 68], asset: null },
      { id: "waving", label: "挥爪", source: "atlas", row: 3, frames: 4, durations: [170, 120, 120, 220], asset: null },
      { id: "jumping", label: "跳一下", source: "atlas", row: 4, frames: 5, durations: [80, 75, 90, 95, 140], asset: null },
    ],
  },
  pets: [
    {
      id: "danhuang",
      display_name: "蛋黄",
      species: "dog",
      notes: "暖黄短腿小狗，深棕下垂耳，温柔略委屈的眼神。",
      status: "ready",
      action_pack_level: "full",
      supported_action_count: 19,
      extension_action_count: 0,
      identity_asset: null,
      reference_assets: [],
      spritesheet_asset: null,
      identity_available: false,
      spritesheet_available: false,
      actions: [
        { id: "idle", label: "待机", source: "atlas", row: 0, frames: 6, durations: [260, 150, 150, 170, 170, 320], asset: null },
        { id: "running-right", label: "向右跑", source: "atlas", row: 1, frames: 8, durations: [58, 54, 50, 54, 58, 50, 54, 68], asset: null },
        { id: "running-left", label: "向左跑", source: "atlas", row: 2, frames: 8, durations: [58, 54, 50, 54, 58, 50, 54, 68], asset: null },
        { id: "waving", label: "挥爪", source: "atlas", row: 3, frames: 4, durations: [170, 120, 120, 220], asset: null },
        { id: "jumping", label: "跳一下", source: "atlas", row: 4, frames: 5, durations: [80, 75, 90, 95, 140], asset: null },
      ],
    },
    {
      id: "pet-20260520-112213",
      display_name: "胖久",
      species: "松狮",
      notes: "奶油色松狮小狗，圆脸厚毛、粉棕鼻、灰色胸背带。",
      status: "ready",
      action_pack_level: "basic",
      supported_action_count: 11,
      extension_action_count: 6,
      identity_asset: null,
      reference_assets: [],
      spritesheet_asset: null,
      identity_available: false,
      spritesheet_available: false,
      actions: [
        { id: "idle", label: "待机", source: "atlas", row: 0, frames: 6, durations: [260, 150, 150, 170, 170, 320], asset: null },
        { id: "running-right", label: "向右跑", source: "atlas", row: 1, frames: 8, durations: [58, 54, 50, 54, 58, 50, 54, 68], asset: null },
        { id: "running-left", label: "向左跑", source: "atlas", row: 2, frames: 8, durations: [58, 54, 50, 54, 58, 50, 54, 68], asset: null },
        { id: "waving", label: "挥爪", source: "atlas", row: 3, frames: 4, durations: [170, 120, 120, 220], asset: null },
        { id: "jumping", label: "跳一下", source: "atlas", row: 4, frames: 5, durations: [80, 75, 90, 95, 140], asset: null },
      ],
    },
  ],
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
    notes: ["浏览器预览使用 mock 数据；Tauri 运行时读取 E 盘 data-dev 镜像。"],
  },
};

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
    created_at: "browser-preview",
    completed_at: "",
    last_reminded_at: "",
    updated_at: "browser-preview",
    remind_count: 0,
  },
  {
    id: "screenshot",
    title: "补 Tauri/Vue 页面截图基线",
    note: "覆盖窄屏和桌面宽度。",
    due_at: "明天",
    category: "QA",
    priority: "普通",
    repeat: "none",
    status: "open",
    pinned: false,
    important_interval_minutes: 0,
    snooze_until: "",
    created_at: "browser-preview",
    completed_at: "",
    last_reminded_at: "",
    updated_at: "browser-preview",
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
    created_at: "browser-preview",
    completed_at: "",
    last_reminded_at: "",
    updated_at: "browser-preview",
    remind_count: 0,
  },
];

let mockChatMessages: ChatMessageSummary[] = [
  {
    id: "browser-chat-1",
    time: "browser-preview",
    user: "主人有点累了",
    mood: "tired",
    reply: "主人，先把肩膀放下来。我在这里陪你，慢慢做完这一点就好。",
    source: "ai:deepseek",
  },
  {
    id: "browser-chat-2",
    time: "browser-preview",
    user: "查一下 Tauri 是什么",
    mood: "question",
    reply: "主人，我先帮你查到这些：Tauri 是桌面应用框架，常用 Web 前端做界面、Rust 做系统能力。浏览器预览只展示资料摘要样式，真实桌面版会由 Rust 执行受控网页摘要查询。",
    source: "research-fallback:Tauri:browser-preview",
  },
];

let mockPetState: PetStateSummary = {
  pet_id: "pet-20260520-112213",
  stories: [
    {
      id: "browser-story-1",
      entry_type: "story",
      title: "我与胖久",
      content: "胖久从东北一路来到主人身边，慢慢建立起信任。它不爱洗澡，但很爱干净，也会在门口等主人回家。",
      content_preview: "胖久从东北一路来到主人身边，慢慢建立起信任。它不爱洗澡，但很爱干净，也会在门口等主人回家。",
      created_at: "browser-preview",
      updated_at: "browser-preview",
      pinned: false,
      image_count: 1,
    },
  ],
  prompt_summary: "胖久是一只奶油色松狮小狗，从东北远道而来，是主人家里安静、慢热又柔软的陪伴者。",
  role_prompt: "我叫胖久，是一只奶油色的松狮小狗，住在主人的电脑桌面右下角。",
  summary_updated_at: "browser-preview",
  summary_source: "mock",
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
    updated_at: "browser-preview",
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
      return mockRuntime;
    }
    return invoke<RuntimeSummary>("get_runtime_summary");
  },

  async getRuntimeAsset(assetPath: string) {
    if (!isTauri()) {
      throw new Error("浏览器预览不读取本机运行镜像图片");
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
      if (!target) throw new Error("浏览器预览没有这个宠物资料");
      const available = new Set(target.actions.map((action) => action.id));
      const actionIds = input.action_ids.filter((id, index, source) => available.has(id) && source.indexOf(id) === index).slice(0, 16);
      if (!actionIds.length) throw new Error("右键动作栏至少保留 1 个动作");
      mockRuntime.settings.quick_menu_actions = actionIds;
      mockRuntime.settings.quick_menu_action_count = actionIds.length;
      return mockRuntime;
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
      return mockRuntime;
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
      return mockRuntime;
    }
    return invoke<RuntimeSummary>("update_ai_provider_key", { input });
  },

  async switchPet(input: SwitchPetInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id && pet.status === "ready");
      if (!target) throw new Error("浏览器预览没有这个可切换宠物");
      mockRuntime.current_pet_id = target.id;
      mockRuntime.current_pet = target;
      return mockRuntime;
    }
    return invoke<RuntimeSummary>("switch_pet", { input });
  },

  async updatePetProfile(input: UpdatePetProfileInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("浏览器预览没有这个宠物资料");
      target.display_name = input.display_name;
      target.species = input.species ?? "";
      target.notes = input.notes ?? "";
      if (mockRuntime.current_pet_id === target.id) {
        mockRuntime.current_pet = target;
      }
      return mockRuntime;
    }
    return invoke<RuntimeSummary>("update_pet_profile", { input });
  },

  async uploadPetImage(input: UploadPetImageInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("浏览器预览没有这个宠物资料");
      const mockPath =
        input.kind === "identity"
          ? `family/${input.pet_id}/identity-base.png`
          : `family/${input.pet_id}/uploads/user-browser-preview.png`;
      if (input.kind === "identity") {
        target.identity_asset = mockPath;
        target.identity_available = true;
      } else {
        target.reference_assets = [mockPath, ...target.reference_assets.filter((path) => path !== mockPath)];
      }
      if (mockRuntime.current_pet_id === target.id) {
        mockRuntime.current_pet = target;
      }
      return mockRuntime;
    }
    return invoke<RuntimeSummary>("upload_pet_image", { input });
  },

  async uploadPetActionStrip(input: UploadPetActionStripInput) {
    if (!isTauri()) {
      const target = mockRuntime.pets.find((pet) => pet.id === input.pet_id);
      if (!target) throw new Error("浏览器预览没有这个宠物资料");
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
      return mockRuntime;
    }
    return invoke<RuntimeSummary>("upload_pet_action_strip", { input });
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
          status: input.done === undefined ? todo.status : input.done ? "done" : "open",
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
          ? "主人，我先帮你查到这些：浏览器预览不会联网，真实桌面版会由 Rust 受控查询中文维基和网页摘要，再交给 AI 或本地兜底回答。"
          : mockReplyForMood(mood),
        source: isResearch ? "research-fallback:browser-preview" : input.role_style ? `local:${input.role_style}` : "local",
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

  async quitApp() {
    if (!isTauri()) return;
    await invoke("quit_app");
  },
};
