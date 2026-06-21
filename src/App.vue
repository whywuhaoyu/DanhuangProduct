<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import { currentMonitor, cursorPosition, getCurrentWindow, PhysicalPosition, PhysicalSize } from "@tauri-apps/api/window";
import {
  Bell,
  BookOpen,
  Bot,
  Brush,
  ArrowDown,
  ArrowUp,
  CalendarClock,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Clock3,
  CloudSun,
  Download,
  Eye,
  Filter,
  FolderHeart,
  Heart,
  Home,
  Image,
  KeyRound,
  Layers3,
  LayoutGrid,
  ListChecks,
  Map,
  MessageCircle,
  Moon,
  PackageCheck,
  Palette,
  PanelRightOpen,
  Play,
  Plus,
  RefreshCw,
  Save,
  ShieldCheck,
  Sparkles,
  Timer,
  Upload,
  X,
  Zap,
} from "@lucide/vue";
import { runtimeApi } from "./api/runtime";
import { MetricCard, StatusPill } from "./components";
import type {
  ChatMessageSummary,
  PetActionSummary,
  PetStateSummary,
  PetSummary,
  RuntimeAsset,
  RuntimeSummary,
  SafeSettingsSummary,
  TodoSummary,
  UploadPetActionStripInput,
  UploadPetImageInput,
  UpdateAiProviderStateInput,
  UpdateAiProviderKeyInput,
  UpdatePetProfileInput,
  UpdateQuickMenuActionsInput,
  UpdateSettingsInput,
} from "./types/runtime";

const params = new URLSearchParams(window.location.search);
const viewMode = params.get("window") === "pet" ? "pet" : "panel";
const requestedPanelPage = params.get("page") ?? "";
document.documentElement.dataset.window = viewMode;
const PANEL_PAGE_KEY = "danhuang-panel-page";
const THEME_KEY = "danhuang-panel-theme";
const PET_REFRESH_KEY = "danhuang-runtime-refresh";
const REMINDER_SIGNAL_KEY = "danhuang-reminder-signal";
const CHAT_SIGNAL_KEY = "danhuang-chat-signal";
const PET_BUBBLE_SIGNAL_KEY = "danhuang-pet-bubble-signal";
const REMINDER_CHECK_INTERVAL_MS = 30_000;
const PET_ROAM_INTERVAL_MS = 180;
const PET_ROAM_PAUSE_MS = 2_200;
const PET_ROAM_EDGE_PADDING = 12;
const PET_DRAG_DIRECTION_THRESHOLD = 6;
const PET_DRAG_FEEDBACK_INTERVAL_MS = 16;
const PET_DRAG_IDLE_RESET_MS = 650;
const PET_DRAG_SAFETY_MS = 8_000;
const AUTO_TALK_MIN_MS = 90_000;
const AUTO_TALK_MAX_MS = 180_000;

type PanelThemeId = "studio" | "garden" | "daylight" | "soft-blue";
type ReminderTone = "sage" | "info" | "danger-soft" | "warn";
type ReminderFilter = "全部" | "今日" | "重要" | "已完成";
type ProviderState = "待配置 Key" | "可接入" | "测试中" | "已启用" | "当前" | "连接失败" | "高级";

interface ThemeOption {
  id: PanelThemeId;
  label: string;
  caption: string;
  swatches: string[];
}

interface BubblePaletteOption {
  id: string;
  label: string;
  caption: string;
  fill: string;
  outline: string;
  text: string;
}

interface ReminderItem {
  id: string;
  title: string;
  note: string;
  due: string;
  category: string;
  priority: "普通" | "重要" | "安全";
  repeat: string;
  repeatRaw: string;
  pinned: boolean;
  done: boolean;
  tone: ReminderTone;
  importantIntervalMinutes: number;
  snoozeUntil: string;
  createdAt: string;
  lastRemindedAt: string;
  updatedAt: string;
  remindCount: number;
}

interface ReminderDetailDraft {
  title: string;
  due: string;
  category: string;
  priority: ReminderItem["priority"];
  repeat: string;
  note: string;
  importantIntervalMinutes: number;
}

interface ReminderSignal {
  id: string;
  title: string;
  due: string;
  priority: string;
  time: string;
}

interface ChatSignal {
  reply: string;
  mood: string;
  source: string;
  time: string;
}

interface PetBubbleSignal {
  message: string;
  action_id: string;
  source: string;
  time: string;
}

interface ProviderCard {
  id: string;
  name: string;
  model: string;
  state: ProviderState;
  note: string;
  enabled: boolean;
  active: boolean;
  hasSavedKey: boolean;
}

const runtime = ref<RuntimeSummary | null>(null);
const currentAsset = ref("");
const referenceAssets = ref<string[]>([]);
const petSpriteAsset = ref("");
const assetError = ref("");
const referenceAssetError = ref("");
const petSpriteError = ref("");
const loading = ref(true);
const activePage = ref("overview");
const toast = ref("");
const petPinned = ref(true);
const quickMenuOpen = ref(false);
const petSwitcherOpen = ref(false);
const quickMenuPos = ref({ x: 44, y: 44 });
const activePetActionId = ref("idle");
const spriteFrame = ref(0);
let spriteFrameTimer: number | undefined;
let petBubbleTimer: number | undefined;
let reminderCheckTimer: number | undefined;
let petRoamTimer: number | undefined;
let autoTalkTimer: number | undefined;
let petRoamTargetX: number | null = null;
let petRoamTargetY: number | null = null;
let petRoamDirection: "left" | "right" = "right";
let petRoamBusy = false;
let petWindowSizeBusy = false;
let petRoamPausedUntil = 0;
let petDragActive = false;
let petDragFeedbackBusy = false;
let petDragFeedbackTimer: number | undefined;
let petDragIdleTimer: number | undefined;
let petDragSafetyTimer: number | undefined;
let petDragStartCursor: { x: number; y: number } | null = null;
let petDragStartWindow: { x: number; y: number } | null = null;
let petDragLastCursorX: number | null = null;
let petDragLastClientX = 0;
let petDragDirection: "left" | "right" | "idle" = "idle";
let spriteLoadVersion = 0;
let unlistenRuntimeChanged: UnlistenFn | undefined;
let unlistenReminderTriggered: UnlistenFn | undefined;
let unlistenChatReply: UnlistenFn | undefined;
let lastHandledReminderSignal = "";
let lastHandledChatSignal = "";
let lastHandledPetBubbleSignal = "";
const SPRITE_CELL_WIDTH = 192;
const SPRITE_CELL_HEIGHT = 208;
const themeOptions: ThemeOption[] = [
  {
    id: "studio",
    label: "清透工作台",
    caption: "中性纸面、青绿色状态、低饱和陪伴感。",
    swatches: ["#f7f5ef", "#2f807c", "#d48142", "#6e7d5d"],
  },
  {
    id: "garden",
    label: "窗边绿意",
    caption: "更柔和的绿与米白，适合长期挂着。",
    swatches: ["#f2f7ef", "#5f8d65", "#b7793a", "#d7e6d3"],
  },
  {
    id: "daylight",
    label: "晨光浅暖",
    caption: "保留一点蛋黄暖色，但降低橙色占比。",
    swatches: ["#fbf6ed", "#b86f35", "#6f8f72", "#e8d3b7"],
  },
  {
    id: "soft-blue",
    label: "浅蓝便签",
    caption: "更清爽的蓝灰背景，减少米黄色面积。",
    swatches: ["#f3f7fb", "#3d7f93", "#7a8f66", "#d7e5ec"],
  },
];
const bubbleStyleOptions = [
  { id: "thought", label: "思考泡", caption: "当前运行镜像默认，轻盈、有陪伴感。" },
  { id: "cloud", label: "云朵", caption: "更柔软，适合主动陪伴短句。" },
  { id: "rounded", label: "圆角", caption: "克制、清晰，适合工作时常开。" },
  { id: "comic", label: "漫画", caption: "边框更明确，适合互动反馈。" },
  { id: "minimal", label: "极简", caption: "低打扰，只保留文字和轻背景。" },
  { id: "pixel", label: "像素", caption: "更接近桌宠精灵图的玩具感。" },
];
const bubblePaletteOptions: BubblePaletteOption[] = [
  { id: "warm", label: "暖白便签", caption: "接近 Tk 默认气泡，温和不抢屏。", fill: "#fffaf0", outline: "#d8a760", text: "#3b3024" },
  { id: "mint", label: "薄荷轻声", caption: "降低橙色占比，适合长期挂桌面。", fill: "#f1fbf6", outline: "#74a98b", text: "#24453a" },
  { id: "blue", label: "浅蓝便签", caption: "和浅蓝页面背景搭配更清爽。", fill: "#f3f8ff", outline: "#79a8c6", text: "#233846" },
  { id: "paper", label: "漫画纸面", caption: "边框更明确，适合动作反馈。", fill: "#fffdf8", outline: "#2f807c", text: "#262b28" },
];
const storedTheme = localStorage.getItem(THEME_KEY);
const activeThemeId = ref<PanelThemeId>(
  themeOptions.some((theme) => theme.id === storedTheme) ? (storedTheme as PanelThemeId) : "studio",
);
const reminderFilters: ReminderFilter[] = ["全部", "今日", "重要", "已完成"];
const reminderPriorityOptions: ReminderItem["priority"][] = ["普通", "重要", "安全"];
const reminderRepeatOptions = [
  { value: "none", label: "单次" },
  { value: "daily", label: "每天" },
  { value: "weekly", label: "每周" },
  { value: "monthly", label: "每月" },
];

const navGroups = [
  {
    label: "日常",
    items: [
      { id: "overview", label: "首页", icon: Home },
      { id: "chat", label: "对话", icon: MessageCircle },
      { id: "reminders", label: "提醒", icon: Bell },
      { id: "actions", label: "操作", icon: Play },
    ],
  },
  {
    label: "宠物资产",
    items: [
      { id: "identity", label: "形象", icon: Image },
      { id: "profile", label: "档案", icon: FolderHeart },
      { id: "story", label: "故事", icon: BookOpen },
      { id: "motion", label: "动作", icon: LayoutGrid },
    ],
  },
  {
    label: "智能",
    items: [{ id: "ai", label: "AI", icon: Bot }],
  },
  {
    label: "设置与安全",
    items: [
      { id: "appearance", label: "外观", icon: Palette },
      { id: "behavior", label: "行为", icon: Map },
      { id: "security", label: "安全", icon: ShieldCheck },
    ],
  },
];

const quickTools = [
  { label: "摸摸", caption: "给它一个轻反馈", icon: Heart },
  { label: "说句话", caption: "低频陪伴短句", icon: MessageCircle },
  { label: "加提醒", caption: "本地待办", icon: Bell },
  { label: "查资料", caption: "资料检索", icon: CloudSun },
  { label: "切形象", caption: "家人列表", icon: Image },
  { label: "动作页", caption: "预览动作", icon: Play },
];

const baseActionIds = ["idle", "running-right", "running-left", "waving", "jumping"];

const roleStyles = [
  "蛋黄本色",
  "技术导师",
  "产品拆解",
  "知识博主",
  "短视频编导",
  "研究助手",
  "直说教练",
  "运营写手",
];

function providerCard(id: string, name: string, model: string, state: ProviderState, note: string): ProviderCard {
  return {
    id,
    name,
    model,
    state,
    note,
    enabled: state === "当前" || state === "已启用",
    active: state === "当前",
    hasSavedKey: state === "当前" || state === "已启用" || state === "可接入",
  };
}

const providerCards = ref<ProviderCard[]>([
  providerCard("openai", "OpenAI", "Responses API", "待配置 Key", "适合完整云端对话，Key 走本机安全存储。"),
  providerCard("deepseek", "DeepSeek", "OpenAI Compatible", "当前", "兼容接口，适合低成本日常陪伴。"),
  providerCard("kimi", "Kimi", "Moonshot", "可接入", "适合长上下文资料整理。"),
  providerCard("zhipu", "智谱 GLM", "GLM", "可接入", "中文能力和工具调用预留。"),
  providerCard("xiaomi_mimo", "小米 MiMo", "MiMo", "可接入", "国产厂商预设入口，后续接配置。"),
  providerCard("gemini", "Gemini", "Gemini", "可接入", "跨模态能力预留，不回传本地隐私。"),
  providerCard("qwen", "Qwen", "通义千问", "可接入", "中文和工具场景预设入口。"),
  providerCard("openrouter", "OpenRouter", "Router", "高级", "多模型路由，适合高级用户。"),
  providerCard("mistral", "Mistral", "OpenAI Compatible", "可接入", "轻量模型预设入口。"),
  providerCard("groq", "Groq", "OpenAI Compatible", "可接入", "快速回复场景预留。"),
  providerCard("custom", "自定义中转", "兼容接口", "高级", "支持 Base URL、模型名和兼容模式。"),
]);
const selectedProvider = ref("deepseek");
const providerTestLog = ref("选择厂商后可测试连接；真实 Key 不回显、不写日志。");
const providerSavingId = ref("");
const providerKeyModalMode = ref<"" | "replace" | "clear">("");
const providerKeyDraft = ref("");
const providerKeyConfirm = ref("");
const providerKeySaving = ref(false);

const chatMessages = ref<ChatMessageSummary[]>([]);
const chatLoading = ref(false);
const chatSending = ref(false);
const chatDraft = ref("");
const selectedRoleStyle = ref("蛋黄本色");
const petState = ref<PetStateSummary | null>(null);
const petStateLoading = ref(false);
const storySaving = ref(false);
const selectedStoryId = ref("");
const storyDraft = ref({
  title: "",
  content: "",
  entry_type: "story",
});
const reminders = ref<ReminderItem[]>([]);
const remindersLoading = ref(false);
const reminderDraft = ref({ title: "", due: "今天 18:30" });
const reminderFilter = ref<ReminderFilter>("全部");
const selectedReminderId = ref("");
const reminderDetailSaving = ref(false);
const dueReminderRecordingId = ref("");
const activeDueReminder = ref<ReminderItem | null>(null);
const reminderDetailDraft = ref<ReminderDetailDraft>({
  title: "",
  due: "",
  category: "本地",
  priority: "普通",
  repeat: "none",
  note: "",
  importantIntervalMinutes: 0,
});
const actionQueue = ref<string[]>([]);
const selectedBubbleStyle = ref("cloud");
const bubbleFill = ref("#fffaf0");
const bubbleOutline = ref("#d8a760");
const bubbleTextColor = ref("#3b3024");
const bubbleDuration = ref(6);
const petBubbleVisible = ref(true);
const petBubbleText = ref("我在这里，主人。");
const talkEnabled = ref(true);
const roamEnabled = ref(true);
const scaleValue = ref(0.46);
const animationSpeedValue = ref(0.5);
const dragSensitivityValue = ref(0.55);
const inertiaValue = ref(0.2);
const roamSpeedValue = ref(75);
const roamDistanceValue = ref(0.35);
const roamIntervalValue = ref(180);
const idleActionIntervalValue = ref(8);
const talkIntervalValue = ref(90);
const talkAfterInteractionDelayValue = ref(10);
const roamAllowCenter = ref(false);
const multiMonitorRoam = ref(false);
const primaryMonitorEdgeOnly = ref(true);
const secondaryMonitorFullRoam = ref(false);
const roamCurrentMonitorOnly = ref(false);
const keepOnScreen = ref(true);
const lockSizeAcrossMonitors = ref(true);
const settingsSaving = ref(false);
const petSwitchingId = ref("");
const petProfileSaving = ref(false);
const petImageUploading = ref<"" | "identity" | "reference">("");
const petActionUploading = ref(false);
const quickMenuSaving = ref(false);
const quickMenuDraft = ref<string[]>([]);
const petActionDraft = ref({
  action_id: "custom:petting",
  label: "摸摸头",
  frames: 4,
  durations: "220,180,180,260",
});
const editingPetId = ref("");
const petProfileDraft = ref({
  display_name: "",
  species: "",
  notes: "",
});

const stories = [
  { type: "故事", title: "第一次把胖久接入家人列表", time: "2026-06-17", detail: "记录主像素图、现实照片和基础动作包状态。" },
  { type: "日记", title: "今天的陪伴摘要", time: "2026-06-18", detail: "短句、待办、资料查询和本地兜底都保持低打扰。" },
  { type: "思念", title: "蛋黄一直在", time: "长期", detail: "纪念表达保持克制，保留家人感，不做夸张替代。" },
];

const currentPet = computed(() => runtime.value?.current_pet ?? null);
const readyPets = computed(() =>
  (runtime.value?.pets.filter((pet) => pet.status === "ready") ?? [])
    .slice()
    .sort((a, b) => Number(b.id === runtime.value?.current_pet_id) - Number(a.id === runtime.value?.current_pet_id)),
);
const navigationItems = computed(() => navGroups.flatMap((group) => group.items));
const activeTheme = computed(() => themeOptions.find((theme) => theme.id === activeThemeId.value) ?? themeOptions[0]);
const selectedProviderCard = computed(() => providerCards.value.find((provider) => provider.id === selectedProvider.value) ?? providerCards.value[0]);
const petMemorySummary = computed(() => petState.value?.memory ?? null);
const selectedStory = computed(() => petState.value?.stories.find((story) => story.id === selectedStoryId.value) ?? petState.value?.stories[0] ?? null);
const memoryTimelineItems = computed(() => {
  const memory = petMemorySummary.value;
  if (!memory) return [];
  return [
    ...memory.emotional_patterns,
    ...memory.common_questions.map((question) => `常见问题: ${question}`),
    ...memory.notes,
  ].slice(0, 8);
});
const visibleReminders = computed(() => {
  const today = new Date().toISOString().slice(0, 10);
  const items = reminders.value
    .slice()
    .sort((a, b) => Number(b.pinned) - Number(a.pinned) || Number(a.done) - Number(b.done));
  if (reminderFilter.value === "今日") return items.filter((item) => item.due.includes("今日") || item.due.includes("今天") || item.due.startsWith(today));
  if (reminderFilter.value === "重要") return items.filter((item) => item.priority !== "普通" || item.pinned);
  if (reminderFilter.value === "已完成") return items.filter((item) => item.done);
  return items;
});
const selectedReminder = computed(() => reminders.value.find((item) => item.id === selectedReminderId.value) ?? visibleReminders.value[0] ?? null);
const capabilityCards = computed(() => [
  {
    label: "云端",
    value: runtime.value?.features.saved_key_provider_count
      ? `${runtime.value.features.saved_key_provider_count} 个 Key`
      : runtime.value?.features.enabled_provider_count
        ? "待配置 Key"
        : "已关闭",
    tone: runtime.value?.features.saved_key_provider_count ? ("sage" as const) : ("warn" as const),
  },
  { label: "时间", value: "本机直答", tone: "sage" as const },
  { label: "资料", value: "网页摘要", tone: "sage" as const },
  {
    label: "待办",
    value: runtime.value ? `${runtime.value.features.todo_open_count} 未完成` : "本地读取",
    tone: "sage" as const,
  },
  { label: "兜底", value: "短句陪伴", tone: "sage" as const },
]);
const chatStatusSummary = computed(() => {
  const active = providerCards.value.find((provider) => provider.active) ?? selectedProviderCard.value;
  if (active?.hasSavedKey) return `${active.name} 云端回复 + 本地兜底`;
  if (active?.enabled) return `${active.name} 待配置 Key，本地兜底`;
  return "本地陪伴回复";
});
const providerKeyModalTitle = computed(() =>
  providerKeyModalMode.value === "clear"
    ? `清除 ${selectedProviderCard.value.name} Key`
    : `替换 ${selectedProviderCard.value.name} Key`,
);
const providerKeyActionDisabled = computed(() => {
  if (providerKeySaving.value || !providerKeyModalMode.value) return true;
  if (providerKeyModalMode.value === "clear") {
    return providerKeyConfirm.value.trim() !== selectedProviderCard.value.name;
  }
  return providerKeyDraft.value.trim().length < 8;
});
const pageTitle = computed(() => navigationItems.value.find((item) => item.id === activePage.value)?.label ?? "首页");
const pageCaption = computed(() => {
  const map: Record<string, string> = {
    overview: "看它现在怎么样，并快速进入高频操作。",
    chat: "固定能力状态条、角色 Skill 和底部输入区。",
    reminders: "本地待办、到点提醒、稍后提醒和时间轴。",
    actions: "日常摸摸、说话、基础动作和窗口命令。",
    identity: "当前主形象、现实照片和家人形象列表。",
    profile: "宠物级陪伴数据、长期记忆和最近聊天。",
    story: "故事、日记、思念记录，默认克制表达。",
    motion: "动作预览、右键动作栏和扩展动作上传。",
    ai: "Provider 状态、模型、Key 隐私和测试反馈。",
    appearance: "透明窗口、气泡样式、颜色预设和即时预览。",
    behavior: "移动速度、巡游策略、多屏和安静时段。",
    security: "个人备份、公开分发边界和安装包导出。",
  };
  return map[activePage.value] ?? "Tauri/Vue 产品版基础页面。";
});

function chatSourceLabel(source: string) {
  if (source.startsWith("ai-research:")) {
    const providerId = source.split(":")[1] ?? "";
    const provider = providerCards.value.find((item) => item.id === providerId);
    return provider ? `云端资料 · ${provider.name}` : "云端资料";
  }
  if (source.startsWith("ai:")) {
    const providerId = source.split(":")[1] ?? "";
    const provider = providerCards.value.find((item) => item.id === providerId);
    return provider ? `云端回复 · ${provider.name}` : "云端回复";
  }
  if (source.startsWith("research-fallback:")) return "资料摘要";
  if (source.startsWith("local-fallback:")) return "本地兜底";
  if (source.startsWith("local-time")) return "本机时间";
  if (source.startsWith("local")) return "本地短句";
  return source || "本地短句";
}

function chatSourceClass(source: string) {
  if (source.startsWith("ai-research:")) return "source-research";
  if (source.startsWith("ai:")) return "source-ai";
  if (source.startsWith("research-fallback:")) return "source-research";
  if (source.startsWith("local-fallback:")) return "source-fallback";
  return "source-local";
}

const petVisualLabel = computed(() => currentPet.value?.display_name?.slice(0, 2) || "蛋黄");
const petStatusText = computed(() => currentPet.value ? petStatusLabel(currentPet.value) : "等待运行镜像");
const playableActions = computed(() => currentPet.value?.actions ?? []);
const actionById = computed(() => new globalThis.Map(playableActions.value.map((action) => [action.id, action])));
const savedQuickMenuActionIds = computed(() => runtime.value?.settings.quick_menu_actions ?? []);
const activeQuickMenuActionItems = computed(() => {
  const items = savedQuickMenuActionIds.value
    .map((id) => actionById.value.get(id))
    .filter((action): action is PetActionSummary => Boolean(action));
  return items.length ? items : playableActions.value.slice(0, 8);
});
const quickMenuUnavailableCount = computed(
  () => savedQuickMenuActionIds.value.filter((id) => !actionById.value.has(id)).length,
);
const quickMenuDraftItems = computed(() =>
  quickMenuDraft.value
    .map((id) => actionById.value.get(id))
    .filter((action): action is PetActionSummary => Boolean(action)),
);
const quickMenuCandidateItems = computed(() =>
  playableActions.value.filter((action) => !quickMenuDraft.value.includes(action.id)),
);
const activePetAction = computed(
  () =>
    playableActions.value.find((action) => action.id === activePetActionId.value) ??
    playableActions.value.find((action) => action.id === "idle") ??
    playableActions.value[0] ??
    null,
);
const baseActionItems = computed(() =>
  baseActionIds
    .map((id) => playableActions.value.find((action) => action.id === id))
    .filter((action): action is PetActionSummary => Boolean(action)),
);
const extensionActionItems = computed(() => playableActions.value.filter((action) => !baseActionIds.includes(action.id)));
const petScale = computed(() => Math.min(Math.max(Number(scaleValue.value) || 0.46, 0.2), 1.2));
const petStageWidth = computed(() => Math.max(SPRITE_CELL_WIDTH, Math.round(SPRITE_CELL_WIDTH * petScale.value) + 20));
const petStageHeight = computed(() => Math.max(SPRITE_CELL_HEIGHT, Math.round(SPRITE_CELL_HEIGHT * petScale.value) + 34));
const petWindowWidth = computed(() => Math.max(260, Math.min(420, petStageWidth.value + 64)));
const petWindowHeight = computed(() => Math.max(260, Math.min(420, petStageHeight.value + 92)));
const petWindowSizeLabel = computed(() => `${petWindowWidth.value} x ${petWindowHeight.value}`);
const petStageStyle = computed(() => ({
  width: `${petStageWidth.value}px`,
  height: `${petStageHeight.value}px`,
}));
const petImageStyle = computed(() => ({
  width: `${Math.round(SPRITE_CELL_WIDTH * petScale.value)}px`,
  height: `${Math.round(SPRITE_CELL_HEIGHT * petScale.value)}px`,
}));
const petSpriteStyle = computed(() => {
  const action = activePetAction.value;
  if (!action || !petSpriteAsset.value) return {};
  const frameCount = Math.max(action.frames, 1);
  const frame = spriteFrame.value % frameCount;
  const row = action.source === "strip" ? 0 : action.row ?? 0;
  const style: Record<string, string> = {
    width: `${SPRITE_CELL_WIDTH}px`,
    height: `${SPRITE_CELL_HEIGHT}px`,
    backgroundImage: `url("${petSpriteAsset.value}")`,
    backgroundPosition: `-${frame * SPRITE_CELL_WIDTH}px -${row * SPRITE_CELL_HEIGHT}px`,
    transform: `scale(${petScale.value})`,
    transformOrigin: "center bottom",
  };
  if (action.source === "strip") {
    style.backgroundSize = `${frameCount * SPRITE_CELL_WIDTH}px ${SPRITE_CELL_HEIGHT}px`;
  }
  return style;
});
const quickMenuStyle = computed(() => ({
  left: `${Math.min(Math.max(quickMenuPos.value.x, 8), window.innerWidth - 328)}px`,
  top: `${Math.min(Math.max(quickMenuPos.value.y, 8), window.innerHeight - 420)}px`,
}));
const bubbleCssVars = computed<Record<string, string>>(() => ({
  "--bubble-fill": bubbleFill.value,
  "--bubble-outline": bubbleOutline.value,
  "--bubble-text": bubbleTextColor.value,
}));
const activeBubblePaletteId = computed(
  () =>
    bubblePaletteOptions.find(
      (palette) =>
        palette.fill.toLowerCase() === bubbleFill.value.toLowerCase() &&
        palette.outline.toLowerCase() === bubbleOutline.value.toLowerCase() &&
        palette.text.toLowerCase() === bubbleTextColor.value.toLowerCase(),
    )?.id ?? "",
);

function showToast(message: string) {
  toast.value = message;
  window.setTimeout(() => {
    if (toast.value === message) toast.value = "";
  }, 2800);
}

function clearPetBubbleTimer() {
  if (petBubbleTimer !== undefined) {
    window.clearTimeout(petBubbleTimer);
    petBubbleTimer = undefined;
  }
}

function showPetBubble(message = petBubbleText.value) {
  petBubbleText.value = message;
  petBubbleVisible.value = true;
  pausePetRoam(1_600);
  clearPetBubbleTimer();
  const duration = Math.min(Math.max(bubbleDuration.value || 6, 2), 20) * 1000;
  petBubbleTimer = window.setTimeout(() => {
    petBubbleVisible.value = false;
    petBubbleTimer = undefined;
  }, duration);
}

function autoTalkMessages() {
  const name = currentPet.value?.display_name || "蛋黄";
  return [
    "我在这里，主人。",
    "我趴着陪你一会儿。",
    "主人，喝口水再继续。",
    "我闻闻键盘旁边，今天也陪你。",
    `${name}摇了摇尾巴。`,
    "不用急，我在旁边等你。",
    "摸摸头也可以，主人。",
    "我安静待着，不打扰你。",
  ];
}

function pickAutoTalkMessage() {
  const messages = autoTalkMessages();
  const index = Math.floor(Math.random() * messages.length);
  return messages[index] ?? "我在这里，主人。";
}

function pickAutoTalkAction() {
  return (
    playableActions.value.find((action) => ["waving", "idle", "jumping"].includes(action.id)) ??
    playableActions.value.find((action) => action.label.includes("挥") || action.label.includes("待机")) ??
    actionForRoam("idle")
  );
}

function petBubbleSignalFromPayload(payload: unknown): PetBubbleSignal | null {
  if (!payload || typeof payload !== "object") return null;
  const record = payload as Record<string, unknown>;
  const message = String(record.message ?? "");
  if (!message) return null;
  return {
    message,
    action_id: String(record.action_id ?? ""),
    source: String(record.source ?? "local"),
    time: String(record.time ?? nowIso()),
  };
}

function petBubbleSignalKey(signal: PetBubbleSignal) {
  return `${signal.time}:${signal.source}:${signal.message.slice(0, 32)}`;
}

function showPetBubbleSignal(signal: PetBubbleSignal) {
  const key = petBubbleSignalKey(signal);
  if (lastHandledPetBubbleSignal === key) return;
  lastHandledPetBubbleSignal = key;
  showPetBubble(signal.message);
  const action =
    playableActions.value.find((item) => item.id === signal.action_id) ??
    (signal.source === "auto-talk" ? pickAutoTalkAction() : null);
  void setPetActionSilently(action);
}

function publishPetBubbleSignal(message: string, source = "manual-preview", actionId = "") {
  const signal: PetBubbleSignal = {
    message,
    action_id: actionId,
    source,
    time: nowIso(),
  };
  showPetBubbleSignal(signal);
  localStorage.setItem(PET_BUBBLE_SIGNAL_KEY, JSON.stringify({ ...signal, nonce: Date.now() }));
}

function previewAutoTalk() {
  publishPetBubbleSignal(pickAutoTalkMessage(), "manual-preview", pickAutoTalkAction()?.id ?? "");
  showToast("已发送一条自动说话预览到桌宠窗口");
}

function quickPetTalk() {
  quickMenuOpen.value = false;
  publishPetBubbleSignal(pickAutoTalkMessage(), "quick-menu", pickAutoTalkAction()?.id ?? "");
}

function quickPetTouch() {
  quickMenuOpen.value = false;
  const action =
    playableActions.value.find((item) => item.id === "waving") ??
    playableActions.value.find((item) => item.label.includes("挥")) ??
    actionForRoam("idle");
  publishPetBubbleSignal("摸摸头，蛋黄摇了摇尾巴。", "quick-menu", action?.id ?? "");
}

function clearAutoTalkTimer() {
  if (autoTalkTimer !== undefined) {
    window.clearTimeout(autoTalkTimer);
    autoTalkTimer = undefined;
  }
}

function nextAutoTalkDelay() {
  const base = Math.min(Math.max(Number(talkIntervalValue.value) || 90, 30), 600) * 1000;
  const max = Math.max(base, Math.min(Math.max(AUTO_TALK_MAX_MS, base), Math.round(base * 1.6)));
  const min = Math.max(30_000, Math.min(Math.round(base), AUTO_TALK_MIN_MS));
  return min + Math.round(Math.random() * Math.max(max - min, 1));
}

function scheduleAutoTalk(delayMs = nextAutoTalkDelay()) {
  if (viewMode !== "pet") return;
  clearAutoTalkTimer();
  if (!talkEnabled.value) return;
  autoTalkTimer = window.setTimeout(() => {
    if (!talkEnabled.value) return;
    if (quickMenuOpen.value || petBubbleVisible.value) {
      const delay = Math.min(Math.max(Number(talkAfterInteractionDelayValue.value) || 10, 2), 120) * 1000;
      scheduleAutoTalk(delay);
      return;
    }
    publishPetBubbleSignal(pickAutoTalkMessage(), "auto-talk", pickAutoTalkAction()?.id ?? "");
    scheduleAutoTalk();
  }, delayMs);
}

function pausePetRoam(durationMs = PET_ROAM_PAUSE_MS) {
  if (viewMode !== "pet") return;
  petRoamPausedUntil = Math.max(petRoamPausedUntil, Date.now() + durationMs);
}

function petRoamIntervalMs() {
  return Math.min(Math.max(Math.round(Number(roamIntervalValue.value) || PET_ROAM_INTERVAL_MS), 60), 1000);
}

function petDragDirectionThreshold() {
  const sensitivity = Math.min(Math.max(Number(dragSensitivityValue.value) || 1, 0.1), 2);
  return Math.min(Math.max(Math.round(PET_DRAG_DIRECTION_THRESHOLD / sensitivity), 3), 16);
}

function petDragIdleResetDelay() {
  const inertia = Math.min(Math.max(Number(inertiaValue.value) || 0, 0), 1);
  return Math.round(PET_DRAG_IDLE_RESET_MS + inertia * 550);
}

async function syncPetWindowSize() {
  if (viewMode !== "pet" || petWindowSizeBusy) return;
  petWindowSizeBusy = true;
  try {
    await getCurrentWindow().setSize(new PhysicalSize(petWindowWidth.value, petWindowHeight.value));
  } catch {
    // Browser preview and unsupported environments do not expose native window sizing.
  } finally {
    petWindowSizeBusy = false;
  }
}

function selectTheme(themeId: PanelThemeId) {
  activeThemeId.value = themeId;
  localStorage.setItem(THEME_KEY, themeId);
  showToast(`页面背景已切换为${activeTheme.value.label}`);
}

function selectBubblePalette(palette: BubblePaletteOption) {
  bubbleFill.value = palette.fill;
  bubbleOutline.value = palette.outline;
  bubbleTextColor.value = palette.text;
  showPetBubble("气泡颜色已预览。");
  showToast(`气泡配色已切换为${palette.label}`);
}

function providerTone(state: ProviderState): ReminderTone | "neutral" {
  if (state === "测试中" || state === "待配置 Key") return "warn";
  if (state === "连接失败") return "danger-soft";
  if (state === "当前") return "info";
  if (state === "已启用" || state === "可接入") return "sage";
  return "neutral";
}

function applySettings(settings: SafeSettingsSummary) {
  selectedBubbleStyle.value = settings.bubble_style ?? selectedBubbleStyle.value;
  bubbleFill.value = settings.bubble_fill ?? bubbleFill.value;
  bubbleOutline.value = settings.bubble_outline ?? bubbleOutline.value;
  bubbleTextColor.value = settings.bubble_text ?? bubbleTextColor.value;
  bubbleDuration.value = settings.bubble_duration ?? bubbleDuration.value;
  talkEnabled.value = settings.talk_enabled ?? talkEnabled.value;
  roamEnabled.value = settings.roam_enabled ?? roamEnabled.value;
  petPinned.value = settings.always_on_top ?? petPinned.value;
  scaleValue.value = settings.scale ?? scaleValue.value;
  animationSpeedValue.value = settings.animation_speed ?? animationSpeedValue.value;
  dragSensitivityValue.value = settings.drag_sensitivity ?? dragSensitivityValue.value;
  inertiaValue.value = settings.inertia ?? inertiaValue.value;
  roamSpeedValue.value = settings.roam_speed ?? roamSpeedValue.value;
  roamDistanceValue.value = settings.roam_distance ?? roamDistanceValue.value;
  roamIntervalValue.value = settings.roam_interval ?? roamIntervalValue.value;
  idleActionIntervalValue.value = settings.idle_action_interval ?? idleActionIntervalValue.value;
  talkIntervalValue.value = settings.talk_interval ?? talkIntervalValue.value;
  talkAfterInteractionDelayValue.value = settings.talk_after_interaction_delay ?? talkAfterInteractionDelayValue.value;
  roamAllowCenter.value = settings.roam_allow_center ?? roamAllowCenter.value;
  multiMonitorRoam.value = settings.multi_monitor_roam ?? multiMonitorRoam.value;
  primaryMonitorEdgeOnly.value = settings.primary_monitor_edge_only ?? primaryMonitorEdgeOnly.value;
  secondaryMonitorFullRoam.value = settings.secondary_monitor_full_roam ?? secondaryMonitorFullRoam.value;
  roamCurrentMonitorOnly.value = settings.roam_current_monitor_only ?? roamCurrentMonitorOnly.value;
  keepOnScreen.value = settings.keep_on_screen ?? keepOnScreen.value;
  lockSizeAcrossMonitors.value = settings.lock_size_across_monitors ?? lockSizeAcrossMonitors.value;
  void syncPetWindowSize();
}

function commitRuntimeSettings(settings: SafeSettingsSummary) {
  applySettings(settings);
  if (runtime.value) {
    runtime.value = {
      ...runtime.value,
      settings,
    };
  }
}

async function saveRuntimeSettings(input: UpdateSettingsInput, successMessage: string) {
  settingsSaving.value = true;
  try {
    const settings = await runtimeApi.updateSettings(input);
    commitRuntimeSettings(settings);
    showToast(successMessage);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    settingsSaving.value = false;
  }
}

async function saveAppearanceSettings() {
  await saveRuntimeSettings(
    {
      bubble_style: selectedBubbleStyle.value,
      bubble_fill: bubbleFill.value,
      bubble_outline: bubbleOutline.value,
      bubble_text: bubbleTextColor.value,
      bubble_duration: bubbleDuration.value,
      always_on_top: petPinned.value,
    },
    "外观偏好已写入 E 盘运行镜像",
  );
}

async function saveBehaviorSettings() {
  await saveRuntimeSettings(
    {
      scale: scaleValue.value,
      animation_speed: animationSpeedValue.value,
      talk_enabled: talkEnabled.value,
      roam_enabled: roamEnabled.value,
      drag_sensitivity: dragSensitivityValue.value,
      inertia: inertiaValue.value,
      roam_speed: roamSpeedValue.value,
      roam_distance: roamDistanceValue.value,
      roam_interval: roamIntervalValue.value,
      idle_action_interval: idleActionIntervalValue.value,
      talk_interval: talkIntervalValue.value,
      talk_after_interaction_delay: talkAfterInteractionDelayValue.value,
      roam_allow_center: roamAllowCenter.value,
      multi_monitor_roam: multiMonitorRoam.value,
      primary_monitor_edge_only: primaryMonitorEdgeOnly.value,
      secondary_monitor_full_roam: secondaryMonitorFullRoam.value,
      roam_current_monitor_only: roamCurrentMonitorOnly.value,
      keep_on_screen: keepOnScreen.value,
      lock_size_across_monitors: lockSizeAcrossMonitors.value,
      always_on_top: petPinned.value,
    },
    "行为设置已写入 E 盘运行镜像",
  );
}

function nowIso() {
  return new Date().toISOString();
}

function parseClockParts(raw: string) {
  const match = raw.match(/(\d{1,2}):(\d{2})/);
  if (!match) return null;
  const hours = Number(match[1]);
  const minutes = Number(match[2]);
  if (!Number.isInteger(hours) || !Number.isInteger(minutes) || hours > 23 || minutes > 59) return null;
  return { hours, minutes };
}

function dateWithClock(base: Date, clock: { hours: number; minutes: number }) {
  return new Date(base.getFullYear(), base.getMonth(), base.getDate(), clock.hours, clock.minutes, 0, 0);
}

function parseReminderDate(raw: string, now = new Date()) {
  const value = raw.trim();
  if (!value || value === "稍后" || value === "本周") return null;

  if (/^\d{4}-\d{2}-\d{2}/.test(value)) {
    const normalized = value.includes("T") ? value : value.replace(" ", "T");
    const parsed = new Date(normalized);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  const clock = parseClockParts(value);
  if (!clock) return null;
  if (value.includes("今天") || value.includes("今日")) return dateWithClock(now, clock);
  if (value.includes("明天")) {
    const tomorrow = new Date(now);
    tomorrow.setDate(now.getDate() + 1);
    return dateWithClock(tomorrow, clock);
  }

  return null;
}

function parseStoredDate(raw: string) {
  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function reminderThrottleMinutes(reminder: ReminderItem) {
  return reminder.importantIntervalMinutes > 0 ? reminder.importantIntervalMinutes : 5;
}

function isReminderReadyToSignal(reminder: ReminderItem, now = new Date()) {
  if (reminder.done) return false;

  const snoozeUntil = parseStoredDate(reminder.snoozeUntil);
  if (snoozeUntil && snoozeUntil.getTime() > now.getTime()) return false;

  const dueAt = parseReminderDate(reminder.due, now);
  if (!dueAt || dueAt.getTime() > now.getTime()) return false;

  const lastRemindedAt = parseStoredDate(reminder.lastRemindedAt);
  if (!lastRemindedAt) return true;

  return now.getTime() - lastRemindedAt.getTime() >= reminderThrottleMinutes(reminder) * 60_000;
}

function normalizeReminderPriority(priority: string): ReminderItem["priority"] {
  if (priority === "安全" || priority.toLowerCase() === "security") return "安全";
  if (priority === "重要" || priority.toLowerCase() === "important") return "重要";
  return "普通";
}

function reminderTone(priority: ReminderItem["priority"], done: boolean): ReminderTone {
  if (done) return "sage";
  if (priority === "安全") return "danger-soft";
  if (priority === "重要") return "info";
  return "sage";
}

function repeatLabel(repeat: string) {
  if (!repeat || repeat === "none") return "单次";
  if (repeat === "daily") return "每天";
  if (repeat === "weekly") return "每周";
  if (repeat === "monthly") return "每月";
  return repeat;
}

function mapTodoToReminder(todo: TodoSummary): ReminderItem {
  const priority = normalizeReminderPriority(todo.priority);
  const done = todo.status === "done";
  return {
    id: todo.id,
    title: todo.title || "未命名提醒",
    note: todo.note || "",
    due: todo.due_at || "稍后",
    category: todo.category || "本地",
    priority,
    repeat: repeatLabel(todo.repeat),
    repeatRaw: todo.repeat || "none",
    pinned: todo.pinned,
    done,
    tone: reminderTone(priority, done),
    importantIntervalMinutes: todo.important_interval_minutes ?? 0,
    snoozeUntil: todo.snooze_until,
    createdAt: todo.created_at,
    lastRemindedAt: todo.last_reminded_at,
    updatedAt: todo.updated_at,
    remindCount: todo.remind_count,
  };
}

function updateReminder(updated: ReminderItem) {
  reminders.value = reminders.value.map((item) => (item.id === updated.id ? updated : item));
  if (!reminders.value.some((item) => item.id === updated.id)) {
    reminders.value = [updated, ...reminders.value];
  }
  selectedReminderId.value = updated.id;
}

async function refreshChatMessages() {
  chatLoading.value = true;
  try {
    chatMessages.value = await runtimeApi.getChatMessages();
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    chatLoading.value = false;
  }
}

async function sendChatMessage() {
  const text = chatDraft.value.trim();
  if (!text) {
    showToast("先写一句要和它说的话");
    return;
  }

  chatSending.value = true;
  try {
    const message = await runtimeApi.sendChatMessage({
      text,
      role_style: selectedRoleStyle.value,
      now: nowIso(),
    });
    chatMessages.value = [...chatMessages.value, message].slice(-30);
    chatDraft.value = "";
    publishChatSignal(message);
    showToast(message.source.startsWith("ai") ? "云端对话已记录" : message.source.startsWith("research") ? "资料摘要已记录" : "本地对话已记录");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    chatSending.value = false;
  }
}

function chatSignalFromPayload(payload: unknown): ChatSignal | null {
  if (!payload || typeof payload !== "object") return null;
  const record = payload as Record<string, unknown>;
  const reply = String(record.reply ?? "");
  if (!reply) return null;
  return {
    reply,
    mood: String(record.mood ?? ""),
    source: String(record.source ?? "local"),
    time: String(record.time ?? nowIso()),
  };
}

function chatSignalKey(signal: ChatSignal) {
  return `${signal.time}:${signal.reply.slice(0, 32)}`;
}

function showChatFeedback(signal: ChatSignal) {
  const key = chatSignalKey(signal);
  if (lastHandledChatSignal === key) return;
  lastHandledChatSignal = key;
  showPetBubble(signal.reply);
  const action =
    playableActions.value.find((item) => item.id === "waving") ??
    playableActions.value.find((item) => item.id === "idle") ??
    pickAutoTalkAction();
  void setPetActionSilently(action);
}

function publishChatSignal(message: ChatMessageSummary) {
  const signal: ChatSignal = {
    reply: message.reply,
    mood: message.mood,
    source: message.source,
    time: message.time,
  };
  showChatFeedback(signal);
  localStorage.setItem(CHAT_SIGNAL_KEY, JSON.stringify({ ...signal, nonce: Date.now() }));
}

async function refreshPetState() {
  petStateLoading.value = true;
  try {
    const state = await runtimeApi.getPetState();
    petState.value = state;
    if (!state.stories.some((story) => story.id === selectedStoryId.value)) {
      selectedStoryId.value = state.stories[0]?.id ?? "";
    }
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    petStateLoading.value = false;
  }
}

async function createStory() {
  const title = storyDraft.value.title.trim();
  const content = storyDraft.value.content.trim();
  if (!title || !content) {
    showToast("故事标题和内容都不能为空");
    return;
  }

  storySaving.value = true;
  try {
    const state = await runtimeApi.createPetStory({
      title,
      content,
      entry_type: storyDraft.value.entry_type || "story",
      now: nowIso(),
    });
    petState.value = state;
    selectedStoryId.value = state.stories[0]?.id ?? "";
    storyDraft.value = { title: "", content: "", entry_type: "story" };
    await refreshRuntime();
    showToast("故事已保存到当前宠物档案");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    storySaving.value = false;
  }
}

function syncReminderDetailDraft(reminder: ReminderItem | null) {
  if (!reminder) {
    reminderDetailDraft.value = {
      title: "",
      due: "",
      category: "本地",
      priority: "普通",
      repeat: "none",
      note: "",
      importantIntervalMinutes: 0,
    };
    return;
  }

  reminderDetailDraft.value = {
    title: reminder.title,
    due: reminder.due,
    category: reminder.category,
    priority: reminder.priority,
    repeat: reminder.repeatRaw || "none",
    note: reminder.note,
    importantIntervalMinutes: reminder.importantIntervalMinutes,
  };
}

async function saveReminderDetail() {
  const selected = selectedReminder.value;
  if (!selected) {
    showToast("请先选择一个提醒");
    return;
  }

  const title = reminderDetailDraft.value.title.trim();
  if (!title) {
    showToast("提醒标题不能为空");
    return;
  }

  const interval = Number(reminderDetailDraft.value.importantIntervalMinutes);
  if (!Number.isFinite(interval) || interval < 0 || interval > 1440) {
    showToast("重要提醒间隔需在 0 到 1440 分钟之间");
    return;
  }

  reminderDetailSaving.value = true;
  try {
    const todo = await runtimeApi.updateTodoDetail({
      id: selected.id,
      title,
      due_at: reminderDetailDraft.value.due.trim() || "稍后",
      category: reminderDetailDraft.value.category.trim() || "本地",
      priority: reminderDetailDraft.value.priority,
      repeat: reminderDetailDraft.value.repeat || "none",
      note: reminderDetailDraft.value.note,
      important_interval_minutes: Math.round(interval),
      now: nowIso(),
    });
    updateReminder(mapTodoToReminder(todo));
    await refreshRuntime();
    showToast("提醒详情已保存到 E 盘运行镜像");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    reminderDetailSaving.value = false;
  }
}

async function updateAiProviderState(input: UpdateAiProviderStateInput, successMessage: string) {
  providerSavingId.value = input.provider_id;
  try {
    const summary = await runtimeApi.updateAiProviderState(input);
    await applyRuntimeSummary(summary, { refreshTodoList: false });
    showToast(successMessage);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    providerSavingId.value = "";
  }
}

async function activateProvider(provider = selectedProviderCard.value) {
  if (!provider) return;
  selectedProvider.value = provider.id;
  providerTestLog.value = `${provider.name} 将作为当前 AI 厂商；Key 仍只保存在本机安全配置中。`;
  await updateAiProviderState({ provider_id: provider.id, enabled: true, make_active: true }, `${provider.name} 已设为当前厂商`);
}

async function toggleProvider(provider = selectedProviderCard.value) {
  if (!provider) return;
  selectedProvider.value = provider.id;
  const nextEnabled = !provider.enabled;
  providerTestLog.value = nextEnabled
    ? `${provider.name} 已请求启用；如果没有保存 Key，仍会显示为待配置。`
    : `${provider.name} 已请求停用；如它是当前厂商，会自动切到下一个已启用厂商。`;
  await updateAiProviderState(
    { provider_id: provider.id, enabled: nextEnabled, make_active: false },
    nextEnabled ? `${provider.name} 已启用` : `${provider.name} 已停用`,
  );
}

function testProvider(providerId = selectedProvider.value) {
  selectedProvider.value = providerId;
  const provider = providerCards.value.find((item) => item.id === providerId);
  if (!provider) return;
  providerTestLog.value = provider.hasSavedKey
    ? `${provider.name} 本机已保存 Key；本轮只做安全状态检查，不发起联网测试。`
    : `${provider.name} 未保存 Key；后续接 Stronghold 或系统安全存储后再联网测试。`;
  showToast("已完成本地安全状态检查");
}

function openProviderKeyModal(mode: "replace" | "clear") {
  providerKeyModalMode.value = mode;
  providerKeyDraft.value = "";
  providerKeyConfirm.value = "";
}

function closeProviderKeyModal() {
  if (providerKeySaving.value) return;
  providerKeyModalMode.value = "";
  providerKeyDraft.value = "";
  providerKeyConfirm.value = "";
}

async function saveProviderKey() {
  if (!providerKeyModalMode.value || providerKeyActionDisabled.value) return;
  const provider = selectedProviderCard.value;
  const input: UpdateAiProviderKeyInput =
    providerKeyModalMode.value === "clear"
      ? { provider_id: provider.id, clear: true }
      : { provider_id: provider.id, api_key: providerKeyDraft.value.trim(), clear: false };

  providerKeySaving.value = true;
  providerSavingId.value = provider.id;
  try {
    const summary = await runtimeApi.updateAiProviderKey(input);
    await applyRuntimeSummary(summary, { refreshTodoList: false });
    providerTestLog.value =
      providerKeyModalMode.value === "clear"
        ? `${provider.name} 的本机 Key 已清除；历史聊天记录不会被修改。`
        : `${provider.name} 的 Key 已写入本机加密配置，真实值未返回前端。`;
    showToast(providerKeyModalMode.value === "clear" ? "Key 已清除" : "Key 已加密保存");
    providerKeyModalMode.value = "";
    providerKeyDraft.value = "";
    providerKeyConfirm.value = "";
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    providerKeySaving.value = false;
    providerSavingId.value = "";
  }
}

async function refreshTodos() {
  remindersLoading.value = true;
  try {
    const todos = await runtimeApi.getTodos();
    reminders.value = todos.map(mapTodoToReminder);
    if (!reminders.value.some((item) => item.id === selectedReminderId.value)) {
      selectedReminderId.value = visibleReminders.value[0]?.id ?? reminders.value[0]?.id ?? "";
    }
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    remindersLoading.value = false;
  }
}

async function addReminder() {
  const title = reminderDraft.value.title.trim();
  if (!title) {
    showToast("请先输入提醒标题");
    return;
  }
  try {
    const todo = await runtimeApi.createTodo({
      title,
      due_at: reminderDraft.value.due.trim() || "稍后",
      category: "本地",
      priority: "普通",
      now: nowIso(),
    });
    updateReminder(mapTodoToReminder(todo));
    reminderDraft.value.title = "";
    await refreshRuntime();
    void checkDueReminders({ silent: true });
    showToast("提醒已写入 E 盘运行镜像");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  }
}

async function toggleReminderDone(id: string) {
  const item = reminders.value.find((todo) => todo.id === id);
  if (!item) return;
  try {
    const todo = await runtimeApi.updateTodoState({ id, done: !item.done, now: nowIso() });
    updateReminder(mapTodoToReminder(todo));
    if (!item.done && activeDueReminder.value?.id === id) activeDueReminder.value = null;
    await refreshRuntime();
    showToast(item.done ? "提醒已重开" : "提醒已完成");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  }
}

async function toggleReminderPinned(id: string) {
  const item = reminders.value.find((todo) => todo.id === id);
  if (!item) return;
  try {
    const todo = await runtimeApi.updateTodoState({ id, pinned: !item.pinned, now: nowIso() });
    updateReminder(mapTodoToReminder(todo));
    await refreshRuntime();
    showToast(item.pinned ? "已取消置顶" : "提醒已置顶");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  }
}

async function snoozeReminder(id: string, minutes = 15) {
  const snoozeUntil = new Date(Date.now() + minutes * 60 * 1000).toISOString();
  try {
    const todo = await runtimeApi.updateTodoState({ id, snooze_until: snoozeUntil, now: nowIso() });
    updateReminder(mapTodoToReminder(todo));
    if (activeDueReminder.value?.id === id) activeDueReminder.value = null;
    await refreshRuntime();
    showToast(`已稍后 ${minutes} 分钟提醒`);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  }
}

function reminderSignalFromPayload(payload: unknown): ReminderSignal | null {
  if (!payload || typeof payload !== "object") return null;
  const record = payload as Record<string, unknown>;
  const id = String(record.id ?? "");
  const title = String(record.title ?? "");
  if (!id || !title) return null;
  return {
    id,
    title,
    due: String(record.due ?? record.due_at ?? ""),
    priority: String(record.priority ?? "普通"),
    time: String(record.time ?? nowIso()),
  };
}

function reminderSignalKey(signal: ReminderSignal) {
  return `${signal.id}:${signal.time.slice(0, 16)}`;
}

function pickReminderCueAction() {
  return (
    playableActions.value.find((action) => ["waving", "jumping", "tongue"].includes(action.id)) ??
    playableActions.value.find((action) => action.label.includes("挥") || action.label.includes("跳") || action.label.includes("说")) ??
    null
  );
}

async function playReminderCueAction() {
  const action = pickReminderCueAction();
  if (!action) return;
  activePetActionId.value = action.id;
  spriteFrame.value = 0;
  await loadPetSpriteForAction(action);
}

function showDueReminderFeedback(signal: ReminderSignal) {
  const key = reminderSignalKey(signal);
  if (lastHandledReminderSignal === key) return;
  lastHandledReminderSignal = key;

  const matched = reminders.value.find((item) => item.id === signal.id);
  if (matched) activeDueReminder.value = matched;

  const message = `${signal.title} 到点了。`;
  showPetBubble(message);
  void playReminderCueAction();
  if (viewMode === "panel") {
    showToast(`提醒到点：${signal.title}`);
  }
}

function publishReminderSignal(reminder: ReminderItem, time: string) {
  const signal: ReminderSignal = {
    id: reminder.id,
    title: reminder.title,
    due: reminder.due,
    priority: reminder.priority,
    time,
  };
  showDueReminderFeedback(signal);
  localStorage.setItem(REMINDER_SIGNAL_KEY, JSON.stringify({ ...signal, nonce: Date.now() }));
}

function nextDueReminder(now = new Date()) {
  return reminders.value
    .filter((reminder) => isReminderReadyToSignal(reminder, now))
    .sort((a, b) => {
      const aDue = parseReminderDate(a.due, now)?.getTime() ?? Number.MAX_SAFE_INTEGER;
      const bDue = parseReminderDate(b.due, now)?.getTime() ?? Number.MAX_SAFE_INTEGER;
      return Number(b.pinned) - Number(a.pinned) || aDue - bDue;
    })[0] ?? null;
}

async function checkDueReminders(options: { silent?: boolean } = {}) {
  if (dueReminderRecordingId.value) return;
  const due = nextDueReminder();
  if (!due) return;

  dueReminderRecordingId.value = due.id;
  const now = nowIso();
  try {
    const todo = await runtimeApi.recordTodoReminder({ id: due.id, now });
    const updated = mapTodoToReminder(todo);
    updateReminder(updated);
    activeDueReminder.value = updated;
    publishReminderSignal(updated, now);
    await refreshRuntime();
  } catch (error) {
    if (!options.silent) showToast(error instanceof Error ? error.message : String(error));
  } finally {
    dueReminderRecordingId.value = "";
  }
}

function clearReminderCheckTimer() {
  if (reminderCheckTimer !== undefined) {
    window.clearInterval(reminderCheckTimer);
    reminderCheckTimer = undefined;
  }
}

function startReminderCheckTimer() {
  clearReminderCheckTimer();
  reminderCheckTimer = window.setInterval(() => {
    void checkDueReminders({ silent: true });
  }, REMINDER_CHECK_INTERVAL_MS);
}

function pickPetAction(pet: PetSummary | null | undefined = currentPet.value, preferred = activePetActionId.value) {
  const actions = pet?.actions ?? [];
  return actions.find((action) => action.id === preferred) ?? actions.find((action) => action.id === "idle") ?? actions[0] ?? null;
}

function clearSpriteTimer() {
  if (spriteFrameTimer !== undefined) {
    window.clearTimeout(spriteFrameTimer);
    spriteFrameTimer = undefined;
  }
}

function spriteAssetPathForAction(action: PetActionSummary | null | undefined, pet: PetSummary | null | undefined = currentPet.value) {
  if (!action) return "";
  if (action.source === "strip" && action.asset) return action.asset;
  return pet?.spritesheet_asset ?? currentPet.value?.spritesheet_asset ?? "";
}

function scheduleSpriteFrame() {
  clearSpriteTimer();
  const action = activePetAction.value;
  if (!action || !petSpriteAsset.value) return;
  const frameCount = Math.max(action.frames, 1);
  const baseDuration = action.durations[spriteFrame.value % frameCount] ?? 180;
  const speed = Math.min(Math.max(animationSpeedValue.value || 1, 0.35), 1.5);
  const duration = Math.max(45, Math.round(baseDuration / speed));
  spriteFrameTimer = window.setTimeout(() => {
    spriteFrame.value = (spriteFrame.value + 1) % frameCount;
    scheduleSpriteFrame();
  }, duration);
}

async function loadPetSpriteForAction(action: PetActionSummary | null | undefined = activePetAction.value, pet: PetSummary | null | undefined = currentPet.value) {
  clearSpriteTimer();
  petSpriteAsset.value = "";
  petSpriteError.value = "";
  const assetPath = spriteAssetPathForAction(action, pet);
  if (!assetPath) {
    petSpriteError.value = "当前宠物没有可播放精灵图";
    return;
  }
  const loadVersion = ++spriteLoadVersion;
  try {
    const asset = await runtimeApi.getRuntimeAsset(assetPath);
    if (loadVersion !== spriteLoadVersion) return;
    petSpriteAsset.value = asset.data_url;
    spriteFrame.value = 0;
    scheduleSpriteFrame();
  } catch (error) {
    if (loadVersion !== spriteLoadVersion) return;
    petSpriteError.value = error instanceof Error ? error.message : String(error);
  }
}

async function setPetAction(action: PetActionSummary) {
  pausePetRoam(2_800);
  activePetActionId.value = action.id;
  spriteFrame.value = 0;
  await loadPetSpriteForAction(action);
  showPetBubble(`${action.label}，主人。`);
  showToast(`${action.label} 正在播放`);
}

function actionForRoam(direction: "left" | "right" | "idle") {
  if (direction === "right") {
    return (
      playableActions.value.find((action) => action.id === "running-right") ??
      playableActions.value.find((action) => action.label.includes("右") || action.label.includes("跑")) ??
      pickPetAction()
    );
  }
  if (direction === "left") {
    return (
      playableActions.value.find((action) => action.id === "running-left") ??
      playableActions.value.find((action) => action.label.includes("左") || action.label.includes("跑")) ??
      pickPetAction()
    );
  }
  return playableActions.value.find((action) => action.id === "idle") ?? pickPetAction();
}

async function setPetActionSilently(action: PetActionSummary | null | undefined) {
  if (!action || activePetActionId.value === action.id) return;
  activePetActionId.value = action.id;
  spriteFrame.value = 0;
  await loadPetSpriteForAction(action);
}

function clearPetDragIdleTimer() {
  if (petDragIdleTimer !== undefined) {
    window.clearTimeout(petDragIdleTimer);
    petDragIdleTimer = undefined;
  }
}

function clearPetDragFeedbackTimer() {
  if (petDragFeedbackTimer !== undefined) {
    window.clearInterval(petDragFeedbackTimer);
    petDragFeedbackTimer = undefined;
  }
}

function clearPetDragSafetyTimer() {
  if (petDragSafetyTimer !== undefined) {
    window.clearTimeout(petDragSafetyTimer);
    petDragSafetyTimer = undefined;
  }
}

function schedulePetDragIdleReset(delay = PET_DRAG_IDLE_RESET_MS) {
  clearPetDragIdleTimer();
  petDragIdleTimer = window.setTimeout(() => {
    petDragIdleTimer = undefined;
    petDragDirection = "idle";
    void settlePetRoamIdle();
  }, delay);
}

function updatePetDragAction(deltaX: number) {
  if (Math.abs(deltaX) < petDragDirectionThreshold()) return;
  const nextDirection = deltaX > 0 ? "right" : "left";
  if (nextDirection === petDragDirection) return;
  petDragDirection = nextDirection;
  void setPetActionSilently(actionForRoam(nextDirection));
}

async function pollPetDragCursor() {
  if (!petDragActive || petDragFeedbackBusy) return;
  petDragFeedbackBusy = true;
  try {
    const position = await cursorPosition();
    if (petDragStartCursor && petDragStartWindow) {
      await getCurrentWindow().setPosition(
        new PhysicalPosition(
          Math.round(petDragStartWindow.x + position.x - petDragStartCursor.x),
          Math.round(petDragStartWindow.y + position.y - petDragStartCursor.y),
        ),
      );
    }
    if (petDragLastCursorX !== null) {
      updatePetDragAction(position.x - petDragLastCursorX);
    }
    petDragLastCursorX = position.x;
  } catch {
    clearPetDragFeedbackTimer();
  } finally {
    petDragFeedbackBusy = false;
  }
}

function handlePetDragMove(event: MouseEvent) {
  if (!petDragActive) return;
  updatePetDragAction(event.clientX - petDragLastClientX);
  petDragLastClientX = event.clientX;
}

function finishPetDragFeedback() {
  if (!petDragActive && petDragFeedbackTimer === undefined && petDragSafetyTimer === undefined) return;
  petDragActive = false;
  petDragFeedbackBusy = false;
  petDragStartCursor = null;
  petDragStartWindow = null;
  petDragLastCursorX = null;
  window.removeEventListener("mousemove", handlePetDragMove);
  window.removeEventListener("mouseup", finishPetDragFeedback);
  window.removeEventListener("mouseleave", finishPetDragFeedback);
  window.removeEventListener("blur", finishPetDragFeedback);
  clearPetDragFeedbackTimer();
  clearPetDragSafetyTimer();
  pausePetRoam(1_500);
  schedulePetDragIdleReset(petDragIdleResetDelay());
}

async function beginPetDragFeedback(event: MouseEvent) {
  petDragActive = true;
  petDragDirection = "idle";
  petDragLastClientX = event.clientX;
  petDragLastCursorX = null;
  petDragStartCursor = null;
  petDragStartWindow = null;
  clearPetDragIdleTimer();
  clearPetDragFeedbackTimer();
  clearPetDragSafetyTimer();
  pausePetRoam(4_000);
  const [position, windowPosition] = await Promise.all([cursorPosition(), getCurrentWindow().outerPosition()]);
  petDragStartCursor = { x: position.x, y: position.y };
  petDragStartWindow = { x: windowPosition.x, y: windowPosition.y };
  petDragLastCursorX = position.x;
  window.addEventListener("mousemove", handlePetDragMove);
  window.addEventListener("mouseup", finishPetDragFeedback);
  window.addEventListener("mouseleave", finishPetDragFeedback);
  window.addEventListener("blur", finishPetDragFeedback);
  petDragFeedbackTimer = window.setInterval(() => {
    void pollPetDragCursor();
  }, PET_DRAG_FEEDBACK_INTERVAL_MS);
  petDragSafetyTimer = window.setTimeout(finishPetDragFeedback, PET_DRAG_SAFETY_MS);
}

function clearPetRoamTimer() {
  if (petRoamTimer !== undefined) {
    window.clearInterval(petRoamTimer);
    petRoamTimer = undefined;
  }
}

function resetPetRoamTarget() {
  petRoamTargetX = null;
  petRoamTargetY = null;
}

async function settlePetRoamIdle() {
  resetPetRoamTarget();
  await setPetActionSilently(actionForRoam("idle"));
}

async function tickPetRoam() {
  if (viewMode !== "pet" || petRoamBusy) return;
  if (petDragActive) return;
  if (!roamEnabled.value || quickMenuOpen.value || Date.now() < petRoamPausedUntil) {
    await settlePetRoamIdle();
    return;
  }

  petRoamBusy = true;
  try {
    const windowRef = getCurrentWindow();
    const [position, size, monitor] = await Promise.all([
      windowRef.outerPosition(),
      windowRef.outerSize(),
      currentMonitor(),
    ]);
    const workArea = monitor?.workArea;
    if (!workArea) return;

    const minX = workArea.position.x + PET_ROAM_EDGE_PADDING;
    const maxX = workArea.position.x + workArea.size.width - size.width - PET_ROAM_EDGE_PADDING;
    const minY = workArea.position.y + PET_ROAM_EDGE_PADDING;
    const maxY = workArea.position.y + workArea.size.height - size.height - PET_ROAM_EDGE_PADDING;
    if (maxX <= minX || maxY <= minY) return;

    const currentX = Math.min(Math.max(position.x, minX), maxX);
    const currentY = Math.min(Math.max(position.y, minY), maxY);
    if (petRoamTargetX === null || Math.abs(petRoamTargetX - currentX) < 8) {
      const usableWidth = Math.max(maxX - minX, 1);
      const distanceRatio = Math.min(Math.max(Number(roamDistanceValue.value) || 0.35, 0.05), 1);
      const distance = Math.max(80, Math.round(usableWidth * distanceRatio));
      petRoamDirection = currentX <= minX + 24 ? "right" : currentX >= maxX - 24 ? "left" : petRoamDirection === "right" ? "left" : "right";
      petRoamTargetX =
        petRoamDirection === "right"
          ? Math.min(currentX + distance, maxX)
          : Math.max(currentX - distance, minX);
      if (Math.abs(petRoamTargetX - currentX) < 24) {
        petRoamTargetX = petRoamDirection === "right" ? maxX : minX;
      }
      petRoamTargetY = roamAllowCenter.value
        ? Math.round(minY + Math.random() * Math.max(maxY - minY, 1))
        : currentY;
    }

    const nextDirection = petRoamTargetX >= currentX ? "right" : "left";
    petRoamDirection = nextDirection;
    const intervalSeconds = petRoamIntervalMs() / 1000;
    const step = Math.min(Math.max(Math.round((Number(roamSpeedValue.value) || 75) * intervalSeconds), 4), 32);
    const nextX =
      nextDirection === "right"
        ? Math.min(currentX + step, petRoamTargetX)
        : Math.max(currentX - step, petRoamTargetX);
    const targetY = petRoamTargetY ?? currentY;
    const nextY =
      Math.abs(targetY - currentY) <= step
        ? targetY
        : targetY > currentY
          ? currentY + step
          : currentY - step;

    await setPetActionSilently(actionForRoam(nextDirection));
    await windowRef.setPosition(new PhysicalPosition(Math.round(nextX), Math.round(nextY)));

    if (Math.abs(nextX - petRoamTargetX) < 2 && Math.abs(nextY - targetY) < 2) {
      petRoamTargetX = null;
      petRoamTargetY = null;
      petRoamPausedUntil = Date.now() + 1_200;
      await setPetActionSilently(actionForRoam("idle"));
    }
  } catch {
    clearPetRoamTimer();
  } finally {
    petRoamBusy = false;
  }
}

function startPetRoamTimer() {
  if (viewMode !== "pet") return;
  clearPetRoamTimer();
  petRoamTimer = window.setInterval(() => {
    void tickPetRoam();
  }, petRoamIntervalMs());
  void tickPetRoam();
}

function resolveAction(action: string | PetActionSummary) {
  if (typeof action !== "string") return action;
  return playableActions.value.find((item) => item.id === action || item.label === action) ?? null;
}

function queueAction(action: string | PetActionSummary) {
  const item = resolveAction(action);
  const label = item?.label ?? String(action);
  actionQueue.value = [label, ...actionQueue.value.filter((queued) => queued !== label)].slice(0, 5);
  if (item) {
    void setPetAction(item);
  } else {
    showToast(`${label} 已加入播放队列`);
  }
}

function syncRuntimeFeatures(summary: RuntimeSummary) {
  const safeProviders = summary.features.providers;
  if (safeProviders.length) {
    providerCards.value = safeProviders.map((provider) => {
      const active = provider.id === summary.features.active_provider;
      const enabled = provider.enabled;
      return {
        id: provider.id,
        name: provider.display_name,
        model: provider.model || "默认模型",
        enabled,
        active,
        hasSavedKey: provider.has_saved_key,
        state: active ? "当前" : enabled ? "已启用" : provider.has_saved_key ? "可接入" : "待配置 Key",
        note: provider.has_saved_key ? "本机已保存 Key，但不会回显真实值。" : "未保存 Key，可先使用本地兜底。",
      };
    });
    selectedProvider.value = summary.features.active_provider || providerCards.value[0]?.id || selectedProvider.value;
    providerTestLog.value = summary.features.saved_key_provider_count
      ? `运行镜像中有 ${summary.features.saved_key_provider_count} 个厂商保存了本机 Key，真实值未返回前端。`
      : "运行镜像未返回已保存 Key，前端只展示安全状态。";
  }
}

function syncQuickMenuDraft(summary: RuntimeSummary) {
  const available = new Set((summary.current_pet?.actions ?? []).map((action) => action.id));
  const configured = summary.settings.quick_menu_actions.filter((id, index, source) => available.has(id) && source.indexOf(id) === index);
  quickMenuDraft.value = configured.length
    ? configured
    : (summary.current_pet?.actions ?? []).slice(0, 8).map((action) => action.id);
}

async function loadAsset(path: string) {
  currentAsset.value = "";
  assetError.value = "";
  if (!path) {
    assetError.value = "当前宠物没有可预览主图";
    return;
  }
  try {
    const asset = await runtimeApi.getRuntimeAsset(path);
    currentAsset.value = asset.data_url;
  } catch (error) {
    assetError.value = error instanceof Error ? error.message : String(error);
  }
}

async function loadReferenceAssets(pet: PetSummary | null | undefined) {
  referenceAssets.value = [];
  referenceAssetError.value = "";
  const paths = (pet?.reference_assets ?? []).slice(0, 4);
  if (!paths.length) return;

  const results = await Promise.allSettled(paths.map((path) => runtimeApi.getRuntimeAsset(path)));
  referenceAssets.value = results
    .filter((result): result is PromiseFulfilledResult<RuntimeAsset> => result.status === "fulfilled")
    .map((result) => result.value.data_url);
  const failedCount = results.filter((result) => result.status === "rejected").length;
  if (failedCount) {
    referenceAssetError.value = `${failedCount} 张参考图暂时无法预览`;
  }
}

async function applyRuntimeSummary(summary: RuntimeSummary, options: { refreshTodoList?: boolean } = {}) {
  runtime.value = summary;
  syncRuntimeFeatures(summary);
  syncQuickMenuDraft(summary);
  applySettings(summary.settings);
  const action = pickPetAction(summary.current_pet);
  activePetActionId.value = action?.id ?? "idle";
  const tasks: Promise<unknown>[] = [
    loadAsset(summary.current_pet?.identity_asset ?? summary.current_pet?.spritesheet_asset ?? ""),
    loadReferenceAssets(summary.current_pet),
    loadPetSpriteForAction(action, summary.current_pet),
  ];
  if (options.refreshTodoList) {
    tasks.push(refreshTodos());
  }
  await Promise.all(tasks);
}

async function refreshRuntime() {
  loading.value = true;
  try {
    const summary = await runtimeApi.getRuntimeSummary();
    await applyRuntimeSummary(summary, { refreshTodoList: true });
  } finally {
    loading.value = false;
  }
}

async function showPetWindow() {
  await runtimeApi.showPet();
  showToast("桌宠窗口已显示");
}

async function hidePetWindow() {
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  await runtimeApi.hidePet();
  showToast("桌宠窗口已隐藏");
}

async function setPinned(enabled: boolean) {
  try {
    petPinned.value = enabled;
    await runtimeApi.setPetAlwaysOnTop(enabled);
    await saveRuntimeSettings({ always_on_top: enabled }, enabled ? "桌宠窗口已置顶并保存" : "桌宠窗口已取消置顶并保存");
  } catch (error) {
    petPinned.value = !enabled;
    showToast(error instanceof Error ? error.message : String(error));
  }
}

async function startPetDrag(event: MouseEvent) {
  if (event.button !== 0 || quickMenuOpen.value) return;
  event.preventDefault();
  pausePetRoam(4_000);
  try {
    await beginPetDragFeedback(event);
  } catch {
    finishPetDragFeedback();
    try {
      await getCurrentWindow().startDragging();
    } catch {
      // Browser preview and unsupported environments can ignore this.
    }
  }
}

function openQuickMenu(event: MouseEvent) {
  pausePetRoam(4_000);
  quickMenuPos.value = { x: event.clientX, y: event.clientY };
  petSwitcherOpen.value = false;
  quickMenuOpen.value = true;
}

function isKnownPage(page: string) {
  return navGroups.some((group) => group.items.some((item) => item.id === page));
}

function switchPage(page: string) {
  if (!isKnownPage(page)) return;
  activePage.value = page;
  if (page === "chat") {
    void refreshChatMessages();
  }
  if (page === "profile" || page === "story") {
    void refreshPetState();
  }
  if (viewMode === "panel") {
    localStorage.setItem(PANEL_PAGE_KEY, page);
  }
}

function openPanelPage(page: string) {
  if (isKnownPage(page)) {
    localStorage.setItem(PANEL_PAGE_KEY, page);
    activePage.value = page;
    if (page === "chat") {
      void refreshChatMessages();
    }
    if (page === "profile" || page === "story") {
      void refreshPetState();
    }
    showToast(`已请求打开${navigationItems.value.find((item) => item.id === page)?.label ?? "控制面板"}`);
  }
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  void runtimeApi.showPanel();
}

function petStatusLabel(pet: PetSummary) {
  return `${pet.supported_action_count} 动作 / ${pet.extension_action_count} 扩展`;
}

function petInitial(pet: PetSummary) {
  return pet.display_name.slice(0, 1) || "宠";
}

function openPetProfileEditor(pet: PetSummary) {
  editingPetId.value = pet.id;
  petProfileDraft.value = {
    display_name: pet.display_name,
    species: pet.species,
    notes: pet.notes,
  };
}

function closePetProfileEditor() {
  if (petProfileSaving.value) return;
  editingPetId.value = "";
}

async function savePetProfile() {
  if (!editingPetId.value) return;
  const input: UpdatePetProfileInput = {
    pet_id: editingPetId.value,
    display_name: petProfileDraft.value.display_name,
    species: petProfileDraft.value.species,
    notes: petProfileDraft.value.notes,
  };
  petProfileSaving.value = true;
  try {
    const summary = await runtimeApi.updatePetProfile(input);
    await applyRuntimeSummary(summary, { refreshTodoList: false });
    localStorage.setItem(PET_REFRESH_KEY, `${Date.now()}:profile:${editingPetId.value}`);
    showToast("宠物资料已保存");
    editingPetId.value = "";
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    petProfileSaving.value = false;
  }
}

function readFileAsDataUrl(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ""));
    reader.onerror = () => reject(reader.error ?? new Error("读取图片失败"));
    reader.readAsDataURL(file);
  });
}

async function uploadPetImage(kind: UploadPetImageInput["kind"], event: Event) {
  const inputEl = event.target as HTMLInputElement;
  const file = inputEl.files?.[0];
  inputEl.value = "";
  if (!file || !currentPet.value) return;
  if (file.size > 10 * 1024 * 1024) {
    showToast("图片超过 10MB，先压缩后再导入");
    return;
  }

  petImageUploading.value = kind;
  try {
    const dataUrl = await readFileAsDataUrl(file);
    const payload: UploadPetImageInput = {
      pet_id: currentPet.value.id,
      kind,
      file_name: file.name,
      mime_type: file.type,
      data_base64: dataUrl.split(",")[1] ?? dataUrl,
    };
    const summary = await runtimeApi.uploadPetImage(payload);
    await applyRuntimeSummary(summary, { refreshTodoList: false });
    localStorage.setItem(PET_REFRESH_KEY, `${Date.now()}:image:${kind}:${currentPet.value.id}`);
    showToast(kind === "identity" ? "主形象图已导入" : "现实参考图已导入");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    petImageUploading.value = "";
  }
}

function parseDurations(raw: string, frames: number) {
  const values = raw
    .split(/[,\s]+/)
    .map((item) => Number.parseInt(item, 10))
    .filter((item) => Number.isFinite(item))
    .map((item) => Math.min(Math.max(item, 60), 900));
  return Array.from({ length: frames }, (_, index) => values[index] ?? 180);
}

async function uploadPetActionStrip(event: Event) {
  const inputEl = event.target as HTMLInputElement;
  const file = inputEl.files?.[0];
  inputEl.value = "";
  if (!file || !currentPet.value) return;
  const frames = Math.min(Math.max(Math.round(Number(petActionDraft.value.frames) || 1), 1), 8);
  const actionId = petActionDraft.value.action_id.trim().toLowerCase();
  const label = petActionDraft.value.label.trim();
  if (!actionId.startsWith("custom:")) {
    showToast("新增动作 ID 请使用 custom: 前缀");
    return;
  }
  if (!label) {
    showToast("请先填写动作名称");
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showToast("动作条超过 10MB，先压缩后再导入");
    return;
  }

  petActionUploading.value = true;
  try {
    const dataUrl = await readFileAsDataUrl(file);
    const payload: UploadPetActionStripInput = {
      pet_id: currentPet.value.id,
      action_id: actionId,
      label,
      frames,
      durations: parseDurations(petActionDraft.value.durations, frames),
      file_name: file.name,
      mime_type: file.type,
      data_base64: dataUrl.split(",")[1] ?? dataUrl,
    };
    const summary = await runtimeApi.uploadPetActionStrip(payload);
    await applyRuntimeSummary(summary, { refreshTodoList: false });
    activePetActionId.value = actionId;
    const action = playableActions.value.find((item) => item.id === actionId);
    if (action) await loadPetSpriteForAction(action);
    localStorage.setItem(PET_REFRESH_KEY, `${Date.now()}:action:${currentPet.value.id}:${actionId}`);
    showToast(`${label} 动作条已导入`);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    petActionUploading.value = false;
  }
}

function addQuickMenuAction(actionId: string) {
  if (quickMenuDraft.value.includes(actionId)) return;
  if (quickMenuDraft.value.length >= 16) {
    showToast("右键动作栏最多保留 16 个动作");
    return;
  }
  quickMenuDraft.value = [...quickMenuDraft.value, actionId];
}

function removeQuickMenuAction(actionId: string) {
  if (quickMenuDraft.value.length <= 1) {
    showToast("右键动作栏至少保留 1 个动作");
    return;
  }
  quickMenuDraft.value = quickMenuDraft.value.filter((id) => id !== actionId);
}

function moveQuickMenuAction(actionId: string, direction: -1 | 1) {
  const index = quickMenuDraft.value.indexOf(actionId);
  const nextIndex = index + direction;
  if (index < 0 || nextIndex < 0 || nextIndex >= quickMenuDraft.value.length) return;
  const next = quickMenuDraft.value.slice();
  [next[index], next[nextIndex]] = [next[nextIndex], next[index]];
  quickMenuDraft.value = next;
}

function resetQuickMenuDraft() {
  if (!runtime.value) return;
  syncQuickMenuDraft(runtime.value);
  showToast("右键动作草稿已恢复为已保存配置");
}

async function saveQuickMenuActions() {
  if (!currentPet.value) return;
  const input: UpdateQuickMenuActionsInput = {
    pet_id: currentPet.value.id,
    action_ids: quickMenuDraft.value,
  };
  quickMenuSaving.value = true;
  try {
    const summary = await runtimeApi.updateQuickMenuActions(input);
    await applyRuntimeSummary(summary, { refreshTodoList: false });
    localStorage.setItem(PET_REFRESH_KEY, `${Date.now()}:quick-menu:${currentPet.value.id}`);
    showToast("右键动作栏已保存");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    quickMenuSaving.value = false;
  }
}

async function switchCurrentPet(pet: PetSummary) {
  if (pet.id === runtime.value?.current_pet_id || petSwitchingId.value) return;
  petSwitchingId.value = pet.id;
  try {
    const summary = await runtimeApi.switchPet({ pet_id: pet.id });
    await applyRuntimeSummary(summary, { refreshTodoList: true });
    if (activePage.value === "profile" || activePage.value === "story") {
      await refreshPetState();
    }
    localStorage.setItem(PET_REFRESH_KEY, `${Date.now()}:${pet.id}`);
    showPetBubble(`已切换为${pet.display_name}。`);
    showToast(`已切换为 ${pet.display_name}`);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    petSwitchingId.value = "";
  }
}

async function switchPetFromQuickMenu(pet: PetSummary) {
  await switchCurrentPet(pet);
  if (pet.id !== runtime.value?.current_pet_id) return;
  petSwitcherOpen.value = false;
  quickMenuOpen.value = false;
}

function handleStorage(event: StorageEvent) {
  if (event.key === PANEL_PAGE_KEY && event.newValue && viewMode === "panel") {
    switchPage(event.newValue);
  }
  if (event.key === PET_REFRESH_KEY && event.newValue) {
    void refreshRuntime();
  }
  if (event.key === REMINDER_SIGNAL_KEY && event.newValue) {
    try {
      const signal = reminderSignalFromPayload(JSON.parse(event.newValue));
      if (signal) showDueReminderFeedback(signal);
    } catch {
      // Ignore malformed reminder signals from stale previews.
    }
  }
  if (event.key === CHAT_SIGNAL_KEY && event.newValue) {
    try {
      const signal = chatSignalFromPayload(JSON.parse(event.newValue));
      if (signal) showChatFeedback(signal);
    } catch {
      // Ignore malformed chat signals from stale previews.
    }
  }
  if (event.key === PET_BUBBLE_SIGNAL_KEY && event.newValue) {
    try {
      const signal = petBubbleSignalFromPayload(JSON.parse(event.newValue));
      if (signal) showPetBubbleSignal(signal);
    } catch {
      // Ignore malformed pet bubble signals from stale previews.
    }
  }
}

onMounted(() => {
  if (viewMode === "panel") {
    const storedPage = localStorage.getItem(PANEL_PAGE_KEY);
    if (requestedPanelPage && isKnownPage(requestedPanelPage)) {
      switchPage(requestedPanelPage);
    } else if (storedPage) {
      switchPage(storedPage);
    }
  }
  window.addEventListener("storage", handleStorage);
  void listen("danhuang-runtime-changed", () => {
    void refreshRuntime();
  })
    .then((unlisten) => {
      unlistenRuntimeChanged = unlisten;
    })
    .catch(() => {
      // Browser preview does not expose Tauri's event bus.
    });
  void listen<unknown>("danhuang-reminder-triggered", (event) => {
    const signal = reminderSignalFromPayload(event.payload);
    if (signal) showDueReminderFeedback(signal);
  })
    .then((unlisten) => {
      unlistenReminderTriggered = unlisten;
    })
    .catch(() => {
      // Browser preview uses localStorage reminder signals.
    });
  void listen<unknown>("danhuang-chat-reply", (event) => {
    const signal = chatSignalFromPayload(event.payload);
    if (signal) showChatFeedback(signal);
  })
    .then((unlisten) => {
      unlistenChatReply = unlisten;
    })
    .catch(() => {
      // Browser preview directly shows the local reply in sendChatMessage().
  });
  startReminderCheckTimer();
  startPetRoamTimer();
  if (viewMode === "pet") {
    showPetBubble(petBubbleText.value);
    scheduleAutoTalk(45_000);
  }
  void refreshRuntime().then(() => {
    void checkDueReminders({ silent: true });
    if (activePage.value === "chat") {
      void refreshChatMessages();
    }
    if (activePage.value === "profile" || activePage.value === "story") {
      void refreshPetState();
    }
  });
});

watch(animationSpeedValue, () => {
  scheduleSpriteFrame();
});

watch(scaleValue, () => {
  void syncPetWindowSize();
});

watch(roamEnabled, (enabled) => {
  if (viewMode !== "pet") return;
  if (enabled) {
    startPetRoamTimer();
  } else {
    clearPetRoamTimer();
    void settlePetRoamIdle();
  }
});

watch([roamSpeedValue, roamDistanceValue, roamIntervalValue, roamAllowCenter], () => {
  if (viewMode !== "pet" || !roamEnabled.value) return;
  resetPetRoamTarget();
  startPetRoamTimer();
});

watch(talkEnabled, (enabled) => {
  if (viewMode !== "pet") return;
  if (enabled) {
    scheduleAutoTalk(45_000);
  } else {
    clearAutoTalkTimer();
  }
});

watch(
  selectedReminder,
  (reminder) => {
    syncReminderDetailDraft(reminder);
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  clearSpriteTimer();
  clearPetBubbleTimer();
  clearReminderCheckTimer();
  clearPetRoamTimer();
  clearAutoTalkTimer();
  finishPetDragFeedback();
  clearPetDragIdleTimer();
  if (unlistenRuntimeChanged) {
    unlistenRuntimeChanged();
    unlistenRuntimeChanged = undefined;
  }
  if (unlistenReminderTriggered) {
    unlistenReminderTriggered();
    unlistenReminderTriggered = undefined;
  }
  if (unlistenChatReply) {
    unlistenChatReply();
    unlistenChatReply = undefined;
  }
  window.removeEventListener("storage", handleStorage);
});
</script>

<template>
  <div
    v-if="viewMode === 'pet'"
    class="pet-window"
    @mousedown="startPetDrag"
    @contextmenu.prevent="openQuickMenu"
    @dblclick="showPetBubble('摸摸头，蛋黄摇了摇尾巴。')"
  >
    <div
      v-if="petBubbleVisible"
      class="pet-bubble"
      :class="`pet-bubble--${selectedBubbleStyle}`"
      :style="bubbleCssVars"
      aria-live="polite"
    >
      <span>{{ petBubbleText }}</span>
    </div>
    <div class="pet-stage" :class="{ 'pet-stage--fallback': !petSpriteAsset && !currentAsset }" :style="petStageStyle">
      <div
        v-if="petSpriteAsset && activePetAction"
        class="sprite-player"
        :style="petSpriteStyle"
        :aria-label="`${currentPet?.display_name ?? '当前宠物'}：${activePetAction.label}`"
      />
      <img v-else-if="currentAsset" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" :style="petImageStyle" />
      <div v-else class="pet-fallback">
        <Heart :size="54" />
        <strong>{{ petVisualLabel }}</strong>
      </div>
      <span v-if="activePetAction" class="pet-action-badge">{{ activePetAction.label }}</span>
      <span v-if="petSpriteError && !petSpriteAsset" class="pet-action-hint">{{ petSpriteError }}</span>
    </div>

    <section v-if="quickMenuOpen" class="quick-menu" :style="quickMenuStyle" @mousedown.stop>
      <header class="quick-menu__header">
        <div class="mini-avatar">{{ petVisualLabel }}</div>
        <div>
          <strong>{{ currentPet?.display_name ?? "当前宠物" }}</strong>
          <span>{{ petStatusText }}</span>
        </div>
        <button class="icon-button compact" type="button" title="关闭" @click="quickMenuOpen = false">
          <X :size="15" />
        </button>
      </header>
      <div class="quick-menu__section">
        <p>常用</p>
        <div class="quick-menu__grid">
          <button type="button" @click="quickPetTalk">说句话</button>
          <button type="button" @click="quickPetTouch">摸摸</button>
          <button type="button" @click="openPanelPage('chat')">对话</button>
          <button type="button" @click="openPanelPage('reminders')">提醒</button>
          <button type="button" :class="{ active: petSwitcherOpen }" @click="petSwitcherOpen = !petSwitcherOpen">切换形象</button>
          <button type="button" @click="openPanelPage('overview')">控制面板</button>
        </div>
      </div>
      <div v-if="petSwitcherOpen" class="quick-menu__pet-switcher">
        <p>家人形象</p>
        <button
          v-for="pet in readyPets"
          :key="pet.id"
          type="button"
          class="quick-menu__pet-row"
          :class="{ current: pet.id === runtime?.current_pet_id }"
          :disabled="petSwitchingId === pet.id"
          @click="switchPetFromQuickMenu(pet)"
        >
          <span class="quick-menu__pet-avatar">{{ petInitial(pet) }}</span>
          <span>
            <strong>{{ pet.display_name }}</strong>
            <small>{{ pet.species || "未标注种类" }} · {{ pet.action_pack_level || "basic" }}</small>
          </span>
          <StatusPill :label="pet.id === runtime?.current_pet_id ? '当前' : petSwitchingId === pet.id ? '切换中' : '切换'" :tone="pet.id === runtime?.current_pet_id ? 'info' : 'sage'" />
        </button>
        <button class="quick-menu__manage-link" type="button" @click="openPanelPage('identity')">管理全部形象</button>
      </div>
      <div class="quick-menu__section">
        <p>右键动作</p>
        <div class="quick-menu__grid">
          <button v-for="item in activeQuickMenuActionItems.slice(0, 8)" :key="item.id" type="button" @click="queueAction(item)">
            {{ item.label }}
          </button>
          <button v-if="!activeQuickMenuActionItems.length" type="button" disabled>暂无可用动作</button>
          <button v-if="activeQuickMenuActionItems.length > 8" type="button" @click="openPanelPage('motion')">
            更多/管理 +{{ Math.max(activeQuickMenuActionItems.length - 8, 0) }}
          </button>
        </div>
      </div>
      <footer class="quick-menu__footer">
        <button class="button ghost" type="button" @click="setPinned(!petPinned)">{{ petPinned ? "取消置顶" : "窗口置顶" }}</button>
        <button class="button ghost" type="button" @click="hidePetWindow">隐藏</button>
      </footer>
    </section>

    <button class="pet-close" type="button" title="隐藏桌宠" @click.stop="hidePetWindow">
      <X :size="16" />
    </button>
    <div v-if="toast" class="toast pet-toast">{{ toast }}</div>
  </div>

  <main v-else class="app-shell" :data-theme="activeThemeId">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">
          <img v-if="currentAsset" :src="currentAsset" alt="" />
          <Heart v-else :size="22" />
        </div>
        <div>
          <strong>蛋黄桌宠</strong>
          <span>暖色陪伴控制台</span>
        </div>
      </div>

      <nav class="nav" aria-label="主导航">
        <section v-for="group in navGroups" :key="group.label" class="nav-group">
          <p>{{ group.label }}</p>
          <button
            v-for="item in group.items"
            :key="item.id"
            type="button"
            :class="{ active: activePage === item.id }"
            @click="switchPage(item.id)"
          >
            <component :is="item.icon" :size="17" />
            <span>{{ item.label }}</span>
          </button>
        </section>
      </nav>

      <div class="sidebar-card">
        <div class="sidebar-card__title">
          <StatusPill :label="runtime?.runtime_available ? 'E 盘镜像' : '浏览器预览'" tone="sage" />
          <button class="icon-button compact" type="button" title="刷新数据" @click="refreshRuntime">
            <RefreshCw :size="15" />
          </button>
        </div>
        <p>{{ currentPet?.display_name ?? "等待数据" }} · {{ runtime?.ready_pet_count ?? 0 }} 个 ready 形象</p>
      </div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <span class="eyebrow">Tauri/Vue 产品版</span>
          <h1>{{ pageTitle }}</h1>
          <p>{{ pageCaption }}</p>
        </div>
        <div class="topbar-actions">
          <div class="theme-switcher" aria-label="页面背景">
            <button
              v-for="theme in themeOptions"
              :key="theme.id"
              type="button"
              :class="{ active: activeThemeId === theme.id }"
              :title="theme.caption"
              @click="selectTheme(theme.id)"
            >
              <span class="theme-dot" :style="{ background: theme.swatches[1] }" />
              {{ theme.label }}
            </button>
          </div>
          <button class="button ghost" type="button" @click="refreshRuntime">
            <RefreshCw :size="16" />
            刷新数据
          </button>
          <button class="button ghost" type="button" @click="hidePetWindow">
            <X :size="16" />
            隐藏桌宠
          </button>
          <button class="button primary" type="button" @click="showPetWindow">
            <PanelRightOpen :size="16" />
            显示桌宠
          </button>
        </div>
      </header>

      <nav class="mobile-nav" aria-label="窄屏导航">
        <button
          v-for="item in navigationItems"
          :key="item.id"
          type="button"
          :class="{ active: activePage === item.id }"
          @click="switchPage(item.id)"
        >
          <component :is="item.icon" :size="16" />
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div v-if="loading" class="loading-panel">
        <Heart :size="28" />
        <span>正在读取 E 盘运行镜像...</span>
      </div>

      <div v-else class="page-scroll">
        <section v-if="activePage === 'overview'" class="dashboard-grid">
          <article class="panel hero-panel">
            <div class="hero-copy">
              <span class="eyebrow">当前陪伴</span>
              <h2>{{ currentPet?.display_name ?? "未读取到宠物" }}</h2>
              <p>桌面小窗口保持轻，控制面板承载形象、提醒、AI、动作和安全导出。所有状态跟随当前宠物刷新。</p>
              <div class="hero-actions">
                <button class="button primary" type="button" @click="switchPage('chat')">
                  <MessageCircle :size="16" />
                  和它说话
                </button>
                <button class="button ghost" type="button" @click="switchPage('identity')">
                  <Image :size="16" />
                  切换形象
                </button>
              </div>
            </div>
            <div class="hero-visual">
              <div class="pet-orbit">
                <img v-if="currentAsset" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" />
                <div v-else class="pet-preview-fallback">
                  <Heart :size="44" />
                  <span>{{ assetError || "浏览器预览使用占位图" }}</span>
                </div>
              </div>
              <div class="floating-note">我在 · 不打扰 · 可关闭</div>
            </div>
          </article>

          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">陪伴概览</span>
                <h2>今天的状态</h2>
              </div>
              <StatusPill :label="currentPet?.status ?? 'unknown'" tone="sage" />
            </div>
            <div class="metric-row">
              <MetricCard label="Ready 形象" :value="runtime?.ready_pet_count ?? 0" />
              <MetricCard label="可播放动作" :value="runtime?.total_supported_actions ?? 0" />
              <MetricCard label="扩展动作" :value="runtime?.total_extension_assets ?? 0" />
            </div>
            <div class="progress-block">
              <div><span>陪伴等级</span><strong>Lv. {{ runtime?.features.companion_level ?? 1 }}</strong></div>
              <div class="progress-track"><span style="width: 68%" /></div>
              <p>下一等级还需要 32 次轻互动。这里是产品 UI 示例，后续接宠物级 companion-state。</p>
            </div>
          </article>

          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">能力状态</span>
                <h2>本地优先</h2>
              </div>
              <ShieldCheck :size="22" />
            </div>
            <div class="capability-grid">
              <div v-for="item in capabilityCards" :key="item.label" class="capability-card">
                <StatusPill :label="item.label" :tone="item.tone" />
                <strong>{{ item.value }}</strong>
              </div>
            </div>
            <div class="privacy-list">
              <p v-for="note in runtime?.checks.notes" :key="note">
                <CircleDot :size="14" />
                {{ note }}
              </p>
            </div>
          </article>

          <article class="panel wide-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">快捷入口</span>
                <h2>常用操作不用进设置页</h2>
              </div>
              <Sparkles :size="22" />
            </div>
            <div class="quick-tool-grid">
              <button v-for="tool in quickTools" :key="tool.label" class="action-card" type="button" @click="showToast(`${tool.label} 已触发`)">
                <component :is="tool.icon" :size="18" />
                <span><strong>{{ tool.label }}</strong><small>{{ tool.caption }}</small></span>
                <ChevronRight :size="16" />
              </button>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'identity'" class="content-grid content-grid--identity">
          <article class="panel current-identity">
            <div class="panel-header">
              <div>
                <span class="eyebrow">当前主形象</span>
                <h2>{{ currentPet?.display_name ?? "未读取到宠物" }}</h2>
              </div>
              <div class="panel-header-actions">
                <StatusPill label="当前" tone="info" />
                <button v-if="currentPet" class="button ghost compact-action" type="button" @click="openPetProfileEditor(currentPet)">编辑资料</button>
              </div>
            </div>
            <div class="identity-preview">
              <img v-if="currentAsset" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" />
              <div v-else class="pet-preview-fallback"><Heart :size="40" /><span>等待图片</span></div>
            </div>
            <p class="identity-note">{{ currentPet?.notes || "还没有补充这个形象的说明。" }}</p>
            <div class="asset-upload-row">
              <label class="button ghost compact-action file-button" :class="{ disabled: petImageUploading === 'identity' || !currentPet }">
                <Upload :size="16" />
                {{ petImageUploading === "identity" ? "导入中" : "导入主形象" }}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  :disabled="petImageUploading !== '' || !currentPet"
                  @change="uploadPetImage('identity', $event)"
                />
              </label>
              <label class="button ghost compact-action file-button" :class="{ disabled: petImageUploading === 'reference' || !currentPet }">
                <Image :size="16" />
                {{ petImageUploading === "reference" ? "导入中" : "追加参考图" }}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  :disabled="petImageUploading !== '' || !currentPet"
                  @change="uploadPetImage('reference', $event)"
                />
              </label>
            </div>
            <div class="reference-strip">
              <div v-for="(asset, index) in referenceAssets" :key="`${asset}-${index}`" class="reference-thumb">
                <img :src="asset" :alt="`参考图 ${index + 1}`" />
              </div>
              <div v-if="!referenceAssets.length" class="reference-empty">
                <Image :size="22" />
                <span>现实参考图只保存在本机运行镜像内，不记录原始本机路径。</span>
              </div>
            </div>
            <small v-if="referenceAssetError" class="inline-warning">{{ referenceAssetError }}</small>
            <div class="metric-row">
              <MetricCard label="动作" :value="currentPet?.supported_action_count ?? 0" />
              <MetricCard label="扩展" :value="currentPet?.extension_action_count ?? 0" />
              <MetricCard label="参考图" :value="currentPet?.reference_assets.length ?? 0" />
              <MetricCard label="动作包" :value="currentPet?.action_pack_level ?? '-'" />
            </div>
          </article>

          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">家人形象列表</span>
                <h2>当前宠物排第一，操作不挤窄列</h2>
              </div>
              <Image :size="22" />
            </div>
            <div class="pet-list">
              <div v-for="pet in readyPets" :key="pet.id" class="pet-row" :class="{ current: pet.id === runtime?.current_pet_id }">
                <div class="pet-row__avatar">{{ petInitial(pet) }}</div>
                <div>
                  <strong>{{ pet.display_name }}</strong>
                  <span>{{ pet.species || "未标注种类" }} · {{ pet.action_pack_level || "basic" }} · 参考图 {{ pet.reference_assets.length }}</span>
                </div>
                <StatusPill :label="pet.id === runtime?.current_pet_id ? '当前' : pet.status" :tone="pet.id === runtime?.current_pet_id ? 'info' : 'sage'" />
                <span class="row-meta">{{ petStatusLabel(pet) }}</span>
                <div class="pet-row__actions">
                  <button class="button ghost compact-action" type="button" @click="openPetProfileEditor(pet)">编辑</button>
                  <button
                    class="button ghost compact-action"
                    type="button"
                    :disabled="pet.id === runtime?.current_pet_id || petSwitchingId === pet.id"
                    @click="switchCurrentPet(pet)"
                  >
                    {{ pet.id === runtime?.current_pet_id ? "当前形象" : petSwitchingId === pet.id ? "切换中" : "切换" }}
                  </button>
                </div>
              </div>
            </div>
          </article>

          <article class="panel wide-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">新增宠物向导</span>
                <h2>资料、主像素图、现实照片、五个基础动作</h2>
              </div>
              <Upload :size="22" />
            </div>
            <div class="wizard-steps">
              <div v-for="(step, index) in ['资料', '主像素图', '现实参考', '基础动作', '校验结果']" :key="step">
                <strong>0{{ index + 1 }}</strong>
                <span>{{ step }}</span>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'profile'" class="content-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">宠物档案</span>
                <h2>查看档案不等于切换当前桌宠</h2>
              </div>
              <FolderHeart :size="22" />
            </div>
            <div class="metric-row">
              <MetricCard label="等级" :value="`Lv. ${runtime?.features.companion_level ?? 1}`" />
              <MetricCard label="互动" :value="runtime?.features.companion_interactions ?? 0" />
              <MetricCard label="聊天" :value="runtime?.features.companion_talks ?? 0" />
            </div>
            <div class="memory-card">
              <StatusPill label="宠物级隔离" tone="sage" />
              <strong>长期记忆摘要</strong>
              <p v-if="petMemorySummary">
                {{ petMemorySummary.message_count }} 轮对话 · 最近情绪 {{ petMemorySummary.last_mood || "未记录" }} · {{ petMemorySummary.updated_at || "未更新时间" }}
              </p>
              <p v-else>{{ petStateLoading ? "正在读取当前宠物记忆摘要..." : "当前宠物暂未读取到长期记忆摘要。" }}</p>
              <div v-if="petMemorySummary" class="memory-chip-row">
                <StatusPill
                  v-for="[mood, count] in Object.entries(petMemorySummary.mood_counts).slice(0, 6)"
                  :key="mood"
                  :label="`${mood} · ${count}`"
                  tone="info"
                />
              </div>
            </div>
            <div v-if="petState?.prompt_summary" class="memory-card">
              <StatusPill label="角色摘要" tone="info" />
              <strong>当前宠物设定</strong>
              <p>{{ petState.prompt_summary }}</p>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">记忆线索</span>
                <h2>情绪模式、常见问题和备注</h2>
              </div>
              <MessageCircle :size="22" />
            </div>
            <div class="timeline-list">
              <div v-for="item in memoryTimelineItems" :key="item">
                <CircleDot :size="14" />
                <span>{{ item }}</span>
              </div>
              <div v-if="!petStateLoading && !petMemorySummary" class="empty-state compact">
                <CircleDot :size="18" />
                <span>当前宠物还没有可展示的记忆线索。</span>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'story'" class="content-grid">
          <article class="panel story-list">
            <div class="panel-header">
              <div>
                <span class="eyebrow">故事</span>
                <h2>按日期折叠，纪念表达保持克制</h2>
              </div>
              <StatusPill :label="`${petState?.stories.length ?? runtime?.features.story_count ?? stories.length} 条`" tone="info" />
            </div>
            <div v-if="petStateLoading" class="empty-state compact">
              <RefreshCw :size="22" />
              <span>正在读取当前宠物故事...</span>
            </div>
            <button
              v-for="story in petState?.stories ?? []"
              :key="story.id"
              class="story-card story-card-button"
              :class="{ selected: selectedStory?.id === story.id }"
              type="button"
              @click="selectedStoryId = story.id"
            >
              <StatusPill :label="story.entry_type" tone="info" />
              <div>
                <strong>{{ story.title }}</strong>
                <span>{{ story.created_at || story.updated_at || "未记录时间" }} · {{ story.image_count }} 张图</span>
                <p>{{ story.content_preview || story.content }}</p>
              </div>
              <span class="story-card__link">查看全文</span>
            </button>
            <div v-if="!petStateLoading && !(petState?.stories.length)" class="empty-state">
              <BookOpen :size="24" />
              <span>当前宠物还没有故事记录。</span>
            </div>
          </article>
          <article class="panel reader-panel">
            <span class="eyebrow">阅读器</span>
            <h2>{{ selectedStory?.title ?? "选择一条故事" }}</h2>
            <p>{{ selectedStory?.content ?? "故事页保留全文阅读器和新增入口。删除用户故事或照片前仍需明确确认。" }}</p>
            <div v-if="petState?.role_prompt" class="timeline-list">
              <div><BookOpen :size="14" /><span>角色 prompt 已保存 · {{ petState.summary_updated_at || "未记录更新时间" }}</span></div>
              <div><ShieldCheck :size="14" /><span>故事和纪念内容只保存在 E 盘运行镜像。</span></div>
            </div>
            <form class="form-stack story-form" @submit.prevent="createStory">
              <span class="eyebrow">新增故事</span>
              <input v-model="storyDraft.title" aria-label="故事标题" placeholder="故事标题" />
              <textarea v-model="storyDraft.content" aria-label="故事内容" placeholder="写一段只保存在本机的故事或日记。" />
              <div class="form-row">
                <select v-model="storyDraft.entry_type" aria-label="故事类型">
                  <option value="story">故事</option>
                  <option value="diary">日记</option>
                  <option value="memory">记忆</option>
                </select>
                <button class="button primary" type="submit" :disabled="storySaving">
                  <Save :size="16" />
                  {{ storySaving ? "保存中" : "保存故事" }}
                </button>
              </div>
            </form>
          </article>
        </section>

        <section v-else-if="activePage === 'actions'" class="content-grid">
          <article class="panel wide-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">操作</span>
                <h2>常用、基础动作、扩展动作、窗口操作分组</h2>
              </div>
              <Play :size="22" />
            </div>
            <div class="operation-section">
              <h3>常用操作</h3>
              <div class="quick-tool-grid compact-grid">
                <button v-for="tool in quickTools.slice(0, 4)" :key="tool.label" class="action-card" type="button" @click="showToast(`${tool.label} 已触发`)">
                  <component :is="tool.icon" :size="18" />
                  <span><strong>{{ tool.label }}</strong><small>{{ tool.caption }}</small></span>
                </button>
              </div>
            </div>
            <div class="operation-section">
              <h3>基础动作</h3>
              <div class="chip-grid">
                <button v-for="item in baseActionItems" :key="item.id" type="button" @click="queueAction(item)">
                  {{ item.label }}
                </button>
                <small v-if="!baseActionItems.length">当前宠物还没有可播放基础动作。</small>
              </div>
            </div>
            <div class="operation-section">
              <h3>扩展动作</h3>
              <div class="chip-grid">
                <button v-for="item in extensionActionItems" :key="item.id" type="button" @click="queueAction(item)">
                  {{ item.label }}
                </button>
                <small v-if="!extensionActionItems.length">扩展动作条还未接入，后续可上传动作 strip。</small>
              </div>
            </div>
            <div class="operation-section">
              <h3>当前播放队列</h3>
              <div class="queue-strip">
                <span v-for="item in actionQueue" :key="item">{{ item }}</span>
                <small v-if="!actionQueue.length">还没有动作，点击基础动作或右键面板加入。</small>
              </div>
            </div>
            <div class="operation-section">
              <h3>窗口操作</h3>
              <div class="button-row">
                <button class="button ghost" type="button" @click="showPetWindow">显示桌宠</button>
                <button class="button ghost" type="button" @click="setPinned(!petPinned)">{{ petPinned ? "取消置顶" : "窗口置顶" }}</button>
                <button class="button danger" type="button" @click="hidePetWindow">隐藏桌宠</button>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'motion'" class="content-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">动作概览</span>
                <h2>能播放和已加入右键分开表达</h2>
              </div>
              <LayoutGrid :size="22" />
            </div>
            <div class="metric-row">
              <MetricCard label="可播放动作" :value="playableActions.length" />
              <MetricCard label="扩展动作条" :value="runtime?.total_extension_assets ?? 0" />
              <MetricCard label="右键动作" :value="activeQuickMenuActionItems.length" />
            </div>
            <div class="action-preview-list">
              <button
                v-for="item in playableActions"
                :key="item.id"
                class="action-preview-card"
                :class="{ selected: activePetActionId === item.id }"
                type="button"
                @click="queueAction(item)"
              >
                <Play :size="18" />
                <div>
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.source === "strip" ? "扩展动作条" : "主 atlas" }} · {{ item.frames }} 帧</span>
                </div>
                <StatusPill :label="activePetActionId === item.id ? '播放中' : '可播放'" :tone="activePetActionId === item.id ? 'info' : 'sage'" />
              </button>
              <small v-if="!playableActions.length">当前宠物还没有可播放动作元数据。</small>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">扩展动作导入</span>
                <h2>上传 192x208 cell 的 PNG/WebP strip</h2>
              </div>
              <Upload :size="22" />
            </div>
            <div class="action-upload-form">
              <label>
                <span>动作 ID</span>
                <input v-model.trim="petActionDraft.action_id" placeholder="custom:petting" />
              </label>
              <label>
                <span>名称</span>
                <input v-model.trim="petActionDraft.label" maxlength="24" placeholder="摸摸头" />
              </label>
              <label>
                <span>帧数</span>
                <input v-model.number="petActionDraft.frames" type="number" min="1" max="8" />
              </label>
              <label>
                <span>帧时长 ms</span>
                <input v-model.trim="petActionDraft.durations" placeholder="220,180,180,260" />
              </label>
              <label class="button primary file-button action-upload-button" :class="{ disabled: petActionUploading || !currentPet }">
                <Upload :size="16" />
                {{ petActionUploading ? "导入中" : "选择动作条并导入" }}
                <input
                  type="file"
                  accept="image/png,image/webp"
                  :disabled="petActionUploading || !currentPet"
                  @change="uploadPetActionStrip"
                />
              </label>
            </div>
            <div class="qa-list">
              <div><StatusPill label="尺寸" tone="sage" /><span>Rust 校验宽度等于 192 x 帧数，高度 208。</span></div>
              <div><StatusPill label="格式" tone="sage" /><span>动作条只接受透明友好的 PNG/WebP。</span></div>
              <div><StatusPill label="语义" tone="warn" /><span>方向、身份一致性仍需人工确认。</span></div>
            </div>
          </article>
          <article class="panel wide-panel action-manager-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">右键动作栏</span>
                <h2>决定透明桌宠右键面板里出现哪些动作</h2>
              </div>
              <StatusPill :label="`${quickMenuDraftItems.length}/16`" tone="info" />
            </div>
            <div class="action-manager-layout">
              <section class="managed-actions">
                <div class="section-title-row">
                  <strong>当前顺序</strong>
                  <span v-if="quickMenuUnavailableCount">已过滤 {{ quickMenuUnavailableCount }} 个当前宠物不适配动作</span>
                </div>
                <div class="managed-action-list">
                  <div v-for="item in quickMenuDraftItems" :key="item.id" class="managed-action-row">
                    <Play :size="16" />
                    <div>
                      <strong>{{ item.label }}</strong>
                      <span>{{ item.id }} · {{ item.source === "strip" ? "扩展动作条" : "主 atlas" }}</span>
                    </div>
                    <div class="managed-action-controls">
                      <button class="icon-button compact" type="button" title="上移" @click="moveQuickMenuAction(item.id, -1)">
                        <ArrowUp :size="15" />
                      </button>
                      <button class="icon-button compact" type="button" title="下移" @click="moveQuickMenuAction(item.id, 1)">
                        <ArrowDown :size="15" />
                      </button>
                      <button class="icon-button compact" type="button" title="移除" @click="removeQuickMenuAction(item.id)">
                        <X :size="15" />
                      </button>
                    </div>
                  </div>
                  <div v-if="!quickMenuDraftItems.length" class="empty-state compact">
                    <Play :size="20" />
                    <span>还没有右键动作。</span>
                  </div>
                </div>
              </section>
              <section class="available-actions">
                <div class="section-title-row">
                  <strong>可加入动作</strong>
                  <span>{{ quickMenuCandidateItems.length }} 个</span>
                </div>
                <div class="available-action-grid">
                  <button v-for="item in quickMenuCandidateItems" :key="item.id" type="button" @click="addQuickMenuAction(item.id)">
                    <Plus :size="15" />
                    <span>{{ item.label }}</span>
                  </button>
                  <small v-if="!quickMenuCandidateItems.length">当前可播放动作已全部加入右键栏。</small>
                </div>
              </section>
            </div>
            <div class="button-row panel-actions">
              <button class="button primary" type="button" :disabled="quickMenuSaving || !quickMenuDraftItems.length" @click="saveQuickMenuActions">
                <Save :size="16" />
                {{ quickMenuSaving ? "保存中" : "保存右键动作栏" }}
              </button>
              <button class="button ghost" type="button" :disabled="quickMenuSaving" @click="resetQuickMenuDraft">恢复已保存</button>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'chat'" class="content-grid content-grid--chat">
          <article class="panel chat-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">聊天窗</span>
                <h2>{{ chatStatusSummary }}</h2>
              </div>
              <MessageCircle :size="22" />
            </div>
            <div class="chat-shell">
              <div class="chat-capabilities">
                <StatusPill v-for="item in capabilityCards" :key="item.label" :label="`${item.label} · ${item.value}`" :tone="item.tone" />
              </div>
              <div class="role-grid">
                <button v-for="role in roleStyles" :key="role" type="button" :class="{ selected: selectedRoleStyle === role }" @click="selectedRoleStyle = role">{{ role }}</button>
              </div>
              <div class="message-list">
                <div v-if="chatLoading" class="empty-state compact">
                  <RefreshCw :size="22" />
                  <span>正在读取本地聊天记录...</span>
                </div>
                <template v-for="item in chatMessages" :key="item.id">
                  <p class="message owner">{{ item.user }}</p>
                  <p class="message pet">
                    {{ item.reply }}
                    <small>
                      <span class="message-source" :class="chatSourceClass(item.source)">{{ chatSourceLabel(item.source) }}</span>
                      {{ item.mood }} · {{ item.time }}
                    </small>
                  </p>
                </template>
                <div v-if="!chatLoading && !chatMessages.length" class="empty-state compact">
                  <MessageCircle :size="22" />
                  <span>还没有本地聊天记录。</span>
                </div>
              </div>
              <div class="composer">
                <input v-model="chatDraft" aria-label="聊天输入" placeholder="和它说一句..." :disabled="chatSending" @keydown.enter="sendChatMessage" />
                <button class="button primary" type="button" :disabled="chatSending" @click="sendChatMessage">
                  <MessageCircle :size="16" />
                  {{ chatSending ? "发送中" : "发送" }}
                </button>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'ai'" class="content-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">AI Provider</span>
                <h2>真实 Key 永不显示</h2>
              </div>
              <Bot :size="22" />
            </div>
            <div class="provider-grid">
              <button
                v-for="provider in providerCards"
                :key="provider.id"
                class="provider-card"
                :class="{ selected: selectedProvider === provider.id }"
                type="button"
                @click="selectedProvider = provider.id"
              >
                <StatusPill :label="provider.state" :tone="providerTone(provider.state)" />
                <strong>{{ provider.name }}</strong>
                <span>{{ provider.model }}</span>
                <small>{{ provider.note }}</small>
              </button>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">本机 Key</span>
                <h2>{{ selectedProviderCard.name }} · 替换和清除都走确认弹窗</h2>
              </div>
              <KeyRound :size="22" />
            </div>
            <div class="security-grid">
              <div><strong>当前状态</strong><p>{{ selectedProviderCard.active ? "当前厂商" : selectedProviderCard.enabled ? "已启用" : "未启用" }}</p></div>
              <div><strong>Key 状态</strong><p>{{ selectedProviderCard.hasSavedKey ? "已保存本机加密 Key" : "未保存 Key" }}</p></div>
              <div><strong>测试反馈</strong><p>{{ providerTestLog }}</p></div>
            </div>
            <div class="button-row panel-actions">
              <button
                class="button primary"
                type="button"
                @click="activateProvider()"
                :disabled="providerSavingId === selectedProviderCard.id || selectedProviderCard.active"
              >
                <Check :size="16" />
                {{ selectedProviderCard.active ? "当前厂商" : providerSavingId === selectedProviderCard.id ? "保存中..." : "设为当前" }}
              </button>
              <button class="button ghost" type="button" @click="toggleProvider()" :disabled="providerSavingId === selectedProviderCard.id">
                {{ selectedProviderCard.enabled ? "停用" : "启用" }}
              </button>
              <button class="button ghost" type="button" @click="testProvider()">本地状态检查</button>
              <button class="button ghost" type="button" @click="openProviderKeyModal('replace')">替换 Key</button>
              <button class="button danger" type="button" :disabled="!selectedProviderCard.hasSavedKey" @click="openProviderKeyModal('clear')">清除 Key</button>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'reminders'" class="content-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">快速新增</span>
                <h2>写入本地运行镜像</h2>
              </div>
              <CalendarClock :size="22" />
            </div>
            <div class="quick-add">
              <input v-model="reminderDraft.title" aria-label="提醒标题" placeholder="提醒标题" @keydown.enter="addReminder" />
              <input v-model="reminderDraft.due" aria-label="提醒时间" placeholder="今天 18:30" @keydown.enter="addReminder" />
              <button class="button primary" type="button" @click="addReminder">
                <Plus :size="16" />
                添加
              </button>
            </div>
            <div v-if="activeDueReminder" class="due-alert-card" role="status" aria-live="polite">
              <div class="due-alert-card__icon">
                <Bell :size="20" />
              </div>
              <div class="due-alert-card__body">
                <span class="eyebrow">到点提醒</span>
                <strong>{{ activeDueReminder.title }}</strong>
                <small>{{ activeDueReminder.due }} · {{ activeDueReminder.category }} · 已提醒 {{ activeDueReminder.remindCount }} 次</small>
              </div>
              <div class="due-alert-card__actions">
                <button class="button primary" type="button" @click="toggleReminderDone(activeDueReminder.id)">
                  <Check :size="16" />
                  完成
                </button>
                <button class="button ghost" type="button" @click="snoozeReminder(activeDueReminder.id)">稍后</button>
                <button class="button ghost" type="button" @click="selectedReminderId = activeDueReminder.id">详情</button>
              </div>
            </div>
            <div class="filter-row" aria-label="提醒筛选">
              <button
                v-for="filter in reminderFilters"
                :key="filter"
                type="button"
                :class="{ selected: reminderFilter === filter }"
                @click="reminderFilter = filter"
              >
                <Filter :size="15" />
                {{ filter }}
              </button>
            </div>
            <div class="todo-list">
              <div v-if="remindersLoading" class="empty-state compact">
                <RefreshCw :size="22" />
                <span>正在同步 E 盘待办镜像...</span>
              </div>
              <button
                v-for="todo in visibleReminders"
                :key="todo.id"
                class="todo-card"
                :class="{ selected: selectedReminder?.id === todo.id, done: todo.done }"
                type="button"
                @click="selectedReminderId = todo.id"
              >
                <StatusPill :label="todo.priority" :tone="todo.tone" />
                <strong>{{ todo.title }}</strong>
                <span>
                  {{ todo.due }} · {{ todo.category }} · {{ todo.repeat }}{{ todo.pinned ? ' · 置顶' : '' }}{{ todo.snoozeUntil ? ' · 已稍后' : '' }}
                </span>
              </button>
              <div v-if="!remindersLoading && !visibleReminders.length" class="empty-state">
                <ListChecks :size="24" />
                <span>当前筛选没有提醒。</span>
              </div>
            </div>
          </article>
          <article class="panel due-panel reminder-editor">
            <div class="panel-header">
              <div>
                <span class="eyebrow">提醒详情</span>
                <h2>{{ selectedReminder?.title ?? "没有选中的提醒" }}</h2>
              </div>
              <Timer :size="22" />
            </div>

            <form class="form-stack reminder-detail-form" @submit.prevent="saveReminderDetail">
              <label>
                标题
                <input v-model="reminderDetailDraft.title" :disabled="!selectedReminder" aria-label="编辑提醒标题" placeholder="提醒标题" />
              </label>
              <label>
                提醒时间
                <input v-model="reminderDetailDraft.due" :disabled="!selectedReminder" aria-label="编辑提醒时间" placeholder="2026-06-19T18:30 或 今天 18:30" />
              </label>
              <div class="form-row">
                <label>
                  分类
                  <input v-model="reminderDetailDraft.category" :disabled="!selectedReminder" aria-label="编辑提醒分类" placeholder="工作 / 生活 / 安全" />
                </label>
                <label>
                  重要间隔
                  <input
                    v-model.number="reminderDetailDraft.importantIntervalMinutes"
                    :disabled="!selectedReminder"
                    type="number"
                    min="0"
                    max="1440"
                    step="5"
                    aria-label="编辑重要提醒间隔"
                  />
                </label>
              </div>
              <div class="form-row">
                <label>
                  优先级
                  <select v-model="reminderDetailDraft.priority" :disabled="!selectedReminder" aria-label="编辑提醒优先级">
                    <option v-for="priority in reminderPriorityOptions" :key="priority" :value="priority">{{ priority }}</option>
                  </select>
                </label>
                <label>
                  重复
                  <select v-model="reminderDetailDraft.repeat" :disabled="!selectedReminder" aria-label="编辑提醒重复规则">
                    <option v-for="option in reminderRepeatOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
                  </select>
                </label>
              </div>
              <label>
                备注
                <textarea v-model="reminderDetailDraft.note" :disabled="!selectedReminder" aria-label="编辑提醒备注" placeholder="补充提醒背景，默认只保存在本机运行镜像。" />
              </label>
              <div class="button-row">
                <button class="button primary" type="submit" :disabled="!selectedReminder || reminderDetailSaving">
                  <Save :size="16" />
                  {{ reminderDetailSaving ? "保存中..." : "保存详情" }}
                </button>
                <button class="button ghost" type="button" :disabled="!selectedReminder" @click="selectedReminder && toggleReminderDone(selectedReminder.id)">
                  <Check :size="16" />
                  {{ selectedReminder?.done ? "重开" : "完成" }}
                </button>
                <button class="button ghost" type="button" :disabled="!selectedReminder" @click="selectedReminder && toggleReminderPinned(selectedReminder.id)">
                  {{ selectedReminder?.pinned ? "取消置顶" : "置顶" }}
                </button>
                <button class="button ghost" type="button" :disabled="!selectedReminder" @click="selectedReminder && snoozeReminder(selectedReminder.id)">
                  <Timer :size="16" />
                  稍后 15 分钟
                </button>
              </div>
            </form>

            <div class="timeline-list reminder-timeline">
              <div><Clock3 :size="14" /><span>创建 · {{ selectedReminder?.createdAt || "等待同步" }}</span></div>
              <div><Bell :size="14" /><span>上次提醒 · {{ selectedReminder?.lastRemindedAt || "未触发" }}</span></div>
              <div><CircleDot :size="14" /><span>累计提醒 · {{ selectedReminder?.remindCount ?? 0 }} 次</span></div>
              <div><Timer :size="14" /><span>稍后 · {{ selectedReminder?.snoozeUntil || "未设置" }}</span></div>
              <div><CheckCircle2 :size="14" /><span>完成/重开/置顶/编辑会写入本地时间轴</span></div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'appearance'" class="content-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">外观总览</span>
                <h2>页面背景、窗口行为和气泡样式同屏预览</h2>
              </div>
              <Palette :size="22" />
            </div>
            <div class="metric-row">
              <MetricCard label="透明度" value="100%" />
              <MetricCard label="气泡" :value="selectedBubbleStyle" />
              <MetricCard label="时长" :value="`${bubbleDuration.toFixed(0)} 秒`" />
              <MetricCard label="背景" :value="activeTheme.label" />
            </div>
            <div class="bubble-preview" :class="`bubble-preview--${selectedBubbleStyle}`" :style="bubbleCssVars">
              <span>我会轻轻说话，不挡住你。</span>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">背景主题</span>
                <h2>可随时切换前端页面背景</h2>
              </div>
              <Brush :size="22" />
            </div>
            <div class="theme-card-grid">
              <button
                v-for="theme in themeOptions"
                :key="theme.id"
                class="theme-card"
                :class="{ selected: activeThemeId === theme.id }"
                type="button"
                @click="selectTheme(theme.id)"
              >
                <span class="theme-card__preview">
                  <i v-for="color in theme.swatches" :key="color" :style="{ background: color }" />
                </span>
                <strong>{{ theme.label }}</strong>
                <small>{{ theme.caption }}</small>
              </button>
            </div>
          </article>
          <article class="panel wide-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">气泡样式</span>
                <h2>运行镜像气泡样式预览和保存</h2>
              </div>
              <Eye :size="22" />
            </div>
            <div class="bubble-style-grid">
              <button
                v-for="style in bubbleStyleOptions"
                :key="style.id"
                type="button"
                :class="{ selected: selectedBubbleStyle === style.id }"
                @click="selectedBubbleStyle = style.id; showPetBubble(`气泡样式已切换为${style.label}。`); showToast(`气泡样式预览切换为 ${style.label}`)"
              >
                <span>{{ style.label }}</span>
                <strong>{{ style.id }}</strong>
                <small>{{ style.caption }}</small>
              </button>
            </div>
            <div class="bubble-config-section">
              <div class="section-title-row">
                <strong>气泡配色</strong>
                <span>写入运行镜像，不影响页面背景主题</span>
              </div>
              <div class="bubble-palette-grid">
                <button
                  v-for="palette in bubblePaletteOptions"
                  :key="palette.id"
                  type="button"
                  :class="{ selected: activeBubblePaletteId === palette.id }"
                  @click="selectBubblePalette(palette)"
                >
                  <span class="bubble-palette-preview" :style="{ background: palette.fill, borderColor: palette.outline, color: palette.text }">Aa</span>
                  <strong>{{ palette.label }}</strong>
                  <small>{{ palette.caption }}</small>
                </button>
              </div>
              <div class="bubble-control-grid">
                <label>
                  <span>背景</span>
                  <input v-model="bubbleFill" type="color" aria-label="气泡背景色" @input="showPetBubble('气泡背景已预览。')" />
                </label>
                <label>
                  <span>描边</span>
                  <input v-model="bubbleOutline" type="color" aria-label="气泡描边色" @input="showPetBubble('气泡描边已预览。')" />
                </label>
                <label>
                  <span>文字</span>
                  <input v-model="bubbleTextColor" type="color" aria-label="气泡文字色" @input="showPetBubble('气泡文字已预览。')" />
                </label>
                <label class="bubble-duration-control">
                  <span>显示时长 <strong>{{ bubbleDuration.toFixed(0) }} 秒</strong></span>
                  <input v-model.number="bubbleDuration" type="range" min="2" max="20" step="1" @input="showPetBubble('显示时长已预览。')" />
                </label>
              </div>
            </div>
            <div class="button-row panel-actions">
              <button class="button primary" type="button" :disabled="settingsSaving" @click="saveAppearanceSettings">
                <Save :size="16" />
                {{ settingsSaving ? "保存中" : "保存外观偏好" }}
              </button>
              <button class="button ghost" type="button" @click="showPetBubble('这是保存前的气泡预览。')">预览桌宠气泡</button>
              <button class="button ghost" type="button" @click="selectTheme('studio')">恢复清透工作台</button>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'behavior'" class="content-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">行为</span>
                <h2>巡游、拖动、多屏和安静时段</h2>
              </div>
              <Map :size="22" />
            </div>
            <div class="mode-grid">
              <button type="button" :class="{ selected: primaryMonitorEdgeOnly && !roamAllowCenter }" @click="primaryMonitorEdgeOnly = true; roamAllowCenter = false">
                <Moon :size="20" />
                <strong>边缘安静</strong>
                <span>主屏四边，不挡工作内容。</span>
              </button>
              <button type="button" :class="{ selected: roamAllowCenter }" @click="roamAllowCenter = !roamAllowCenter">
                <Zap :size="20" />
                <strong>当前屏自由</strong>
                <span>允许跑到当前屏幕中间。</span>
              </button>
              <button type="button" :class="{ selected: multiMonitorRoam }" @click="multiMonitorRoam = !multiMonitorRoam; secondaryMonitorFullRoam = multiMonitorRoam">
                <Layers3 :size="20" />
                <strong>多屏巡游</strong>
                <span>保留副屏自由活动策略。</span>
              </button>
            </div>
          </article>
          <article class="panel">
            <span class="eyebrow">窗口状态</span>
            <h2>当前配置摘要</h2>
            <div class="settings-control-grid">
              <button class="switch-card" :class="{ selected: talkEnabled }" type="button" @click="talkEnabled = !talkEnabled">
                <MessageCircle :size="19" />
                <strong>自动说话</strong>
                <span>{{ talkEnabled ? "开启，低频陪伴短句" : "关闭，只保留主动互动" }}</span>
              </button>
              <button class="switch-card" :class="{ selected: roamEnabled }" type="button" @click="roamEnabled = !roamEnabled">
                <Map :size="19" />
                <strong>自由巡游</strong>
                <span>{{ roamEnabled ? "开启，按运行镜像策略移动" : "关闭，停留在当前位置" }}</span>
              </button>
            </div>
            <div class="movement-summary">
              <div>
                <StatusPill :label="talkEnabled ? '低频开启' : '已关闭'" :tone="talkEnabled ? 'sage' : 'warn'" />
                <strong>自动说话会真实触发</strong>
                <span>透明桌宠窗口会每隔一段时间轻声冒泡；右键菜单打开或已有气泡时会延后，不主动打扰。</span>
              </div>
              <div>
                <StatusPill :label="roamEnabled ? '巡游生效' : '巡游暂停'" :tone="roamEnabled ? 'sage' : 'warn'" />
                <strong>透明桌宠窗口会自己移动</strong>
                <span>保存后在桌宠窗口沿当前屏幕工作区水平巡游；打开右键菜单、拖动窗口或显示气泡时会短暂停住。</span>
              </div>
              <div>
                <StatusPill label="动作联动" tone="info" />
                <strong>方向自动切换</strong>
                <span>向右移动播放“向右跑”，向左移动播放“向左跑”，到达边界回到待机。</span>
              </div>
              <div>
                <StatusPill label="尺寸同步" tone="sage" />
                <strong>大小比例会真实生效</strong>
                <span>保存或拖动滑杆后，透明桌宠窗口和精灵图会按当前比例同步调整。</span>
              </div>
              <div>
                <StatusPill label="Tk 设置接入" tone="sage" />
                <strong>拖动、巡游和说话间隔会写回</strong>
                <span>灵敏度、惯性、巡游速度、活动范围和自动说话间隔来自 E 盘运行镜像 settings。</span>
              </div>
            </div>
            <div class="slider-stack">
              <label>
                <span>大小比例 <strong>{{ scaleValue.toFixed(2) }}</strong></span>
                <input v-model.number="scaleValue" type="range" min="0.2" max="1.2" step="0.01" />
              </label>
              <label>
                <span>动画速度 <strong>{{ animationSpeedValue.toFixed(2) }}</strong></span>
                <input v-model.number="animationSpeedValue" type="range" min="0.1" max="2" step="0.05" />
              </label>
              <label>
                <span>拖动灵敏度 <strong>{{ dragSensitivityValue.toFixed(2) }}</strong></span>
                <input v-model.number="dragSensitivityValue" type="range" min="0.1" max="2" step="0.05" />
              </label>
              <label>
                <span>拖动惯性 <strong>{{ inertiaValue.toFixed(2) }}</strong></span>
                <input v-model.number="inertiaValue" type="range" min="0" max="1" step="0.05" />
              </label>
              <label>
                <span>巡游速度 <strong>{{ roamSpeedValue.toFixed(0) }} px/s</strong></span>
                <input v-model.number="roamSpeedValue" type="range" min="20" max="240" step="5" />
              </label>
              <label>
                <span>巡游距离 <strong>{{ Math.round(roamDistanceValue * 100) }}%</strong></span>
                <input v-model.number="roamDistanceValue" type="range" min="0.05" max="1" step="0.05" />
              </label>
              <label>
                <span>自动说话间隔 <strong>{{ talkIntervalValue.toFixed(0) }} 秒</strong></span>
                <input v-model.number="talkIntervalValue" type="range" min="30" max="600" step="10" />
              </label>
              <label>
                <span>互动后延迟 <strong>{{ talkAfterInteractionDelayValue.toFixed(0) }} 秒</strong></span>
                <input v-model.number="talkAfterInteractionDelayValue" type="range" min="2" max="120" step="2" />
              </label>
            </div>
            <div class="settings-control-grid">
              <button class="switch-card" :class="{ selected: roamAllowCenter }" type="button" @click="roamAllowCenter = !roamAllowCenter">
                <Zap :size="19" />
                <strong>允许屏幕中活动</strong>
                <span>{{ roamAllowCenter ? "开启，巡游会带少量纵向移动" : "关闭，尽量沿当前边缘移动" }}</span>
              </button>
              <button class="switch-card" :class="{ selected: multiMonitorRoam }" type="button" @click="multiMonitorRoam = !multiMonitorRoam">
                <Layers3 :size="19" />
                <strong>多屏活动策略</strong>
                <span>{{ multiMonitorRoam ? "已保存多屏策略" : "只按当前屏策略巡游" }}</span>
              </button>
              <button class="switch-card" :class="{ selected: secondaryMonitorFullRoam }" type="button" @click="secondaryMonitorFullRoam = !secondaryMonitorFullRoam">
                <PanelRightOpen :size="19" />
                <strong>副屏自由活动</strong>
                <span>{{ secondaryMonitorFullRoam ? "副屏可使用更大活动范围" : "副屏也按安静范围处理" }}</span>
              </button>
              <button class="switch-card" :class="{ selected: keepOnScreen }" type="button" @click="keepOnScreen = !keepOnScreen">
                <ShieldCheck :size="19" />
                <strong>保持在屏幕内</strong>
                <span>{{ keepOnScreen ? "开启，自动巡游不跑出工作区" : "关闭，仅保存偏好，仍建议谨慎" }}</span>
              </button>
            </div>
            <div class="setting-list">
              <div><span>大小比例</span><strong>{{ scaleValue.toFixed(2) }}</strong></div>
              <div><span>桌宠窗口</span><strong>{{ petWindowSizeLabel }}</strong></div>
              <div><span>动画速度</span><strong>{{ animationSpeedValue.toFixed(2) }}</strong></div>
              <div><span>拖动灵敏度</span><strong>{{ dragSensitivityValue.toFixed(2) }}</strong></div>
              <div><span>拖动惯性</span><strong>{{ inertiaValue.toFixed(2) }}</strong></div>
              <div><span>巡游速度</span><strong>{{ roamSpeedValue.toFixed(0) }} px/s</strong></div>
              <div><span>巡游距离</span><strong>{{ Math.round(roamDistanceValue * 100) }}%</strong></div>
              <div><span>自动说话间隔</span><strong>{{ talkIntervalValue.toFixed(0) }} 秒</strong></div>
              <div><span>自动说话</span><strong>{{ talkEnabled ? "开启" : "关闭" }}</strong></div>
              <div><span>自由巡游</span><strong>{{ roamEnabled ? "开启" : "关闭" }}</strong></div>
              <div><span>屏幕中活动</span><strong>{{ roamAllowCenter ? "允许" : "关闭" }}</strong></div>
              <div><span>多屏策略</span><strong>{{ multiMonitorRoam ? "开启" : "关闭" }}</strong></div>
              <div><span>置顶</span><strong>{{ petPinned ? "开启" : "关闭" }}</strong></div>
            </div>
            <div class="button-row panel-actions">
              <button class="button primary" type="button" :disabled="settingsSaving" @click="saveBehaviorSettings">
                <Save :size="16" />
                {{ settingsSaving ? "保存中" : "保存行为设置" }}
              </button>
              <button class="button ghost" type="button" @click="previewAutoTalk">预览自动说话</button>
              <button class="button ghost" type="button" @click="setPinned(!petPinned)">{{ petPinned ? "取消置顶" : "窗口置顶" }}</button>
            </div>
          </article>
        </section>

        <section v-else class="content-grid">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">安全</span>
                <h2>公开分发边界清楚可见</h2>
              </div>
              <ShieldCheck :size="22" />
            </div>
            <div class="privacy-matrix">
              <div><StatusPill label="默认排除" tone="sage" /><p>聊天、待办、提醒历史、陪伴状态、日志。</p></div>
              <div><StatusPill label="永不导出" tone="danger-soft" /><p>API Key、Token、DPAPI、本机绝对路径。</p></div>
              <div><StatusPill label="可选导出" tone="info" /><p>默认形象、动作素材、公开说明和新用户模板。</p></div>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">安装包</span>
                <h2>NSIS 调试包已通过，商业包另做清洁验收</h2>
              </div>
              <PackageCheck :size="22" />
            </div>
            <div class="export-card">
              <Download :size="22" />
              <div>
                <strong>公开包必须从干净模板生成</strong>
                <p>导出只作用于副本，不修改本机真实数据。开机启动默认关闭。</p>
              </div>
            </div>
          </article>
        </section>
      </div>
    </section>

    <section v-if="providerKeyModalMode" class="modal-backdrop" @mousedown.self="closeProviderKeyModal">
      <form class="profile-modal" @submit.prevent="saveProviderKey">
        <header class="modal-header">
          <div>
            <span class="eyebrow">本机安全配置</span>
            <h2>{{ providerKeyModalTitle }}</h2>
          </div>
          <button class="icon-button compact" type="button" title="关闭" :disabled="providerKeySaving" @click="closeProviderKeyModal">
            <X :size="16" />
          </button>
        </header>
        <div class="form-stack">
          <div class="privacy-matrix">
            <div><StatusPill label="只写本机" tone="sage" /><p>Key 只传给 Rust，写入 DPAPI 加密字段。</p></div>
            <div><StatusPill label="不回显" tone="info" /><p>保存后前端只刷新“已保存”状态，不读取真实值。</p></div>
            <div><StatusPill label="不进仓库" tone="danger-soft" /><p>运行镜像、DPAPI 和 Key 文件默认被 Git 排除。</p></div>
          </div>
          <label v-if="providerKeyModalMode === 'replace'">
            <span>新的 API Key</span>
            <input v-model="providerKeyDraft" type="password" autocomplete="off" placeholder="粘贴新的 Key，保存后不会显示" />
          </label>
          <label v-else>
            <span>输入厂商名确认清除：{{ selectedProviderCard.name }}</span>
            <input v-model.trim="providerKeyConfirm" autocomplete="off" :placeholder="selectedProviderCard.name" />
          </label>
        </div>
        <footer class="modal-actions">
          <button class="button ghost" type="button" :disabled="providerKeySaving" @click="closeProviderKeyModal">取消</button>
          <button class="button" :class="providerKeyModalMode === 'clear' ? 'danger' : 'primary'" type="submit" :disabled="providerKeyActionDisabled">
            <KeyRound :size="16" />
            {{ providerKeySaving ? "处理中" : providerKeyModalMode === "clear" ? "确认清除" : "加密保存" }}
          </button>
        </footer>
      </form>
    </section>

    <section v-if="editingPetId" class="modal-backdrop" @mousedown.self="closePetProfileEditor">
      <form class="profile-modal" @submit.prevent="savePetProfile">
        <header class="modal-header">
          <div>
            <span class="eyebrow">形象资料</span>
            <h2>编辑宠物基础资料</h2>
          </div>
          <button class="icon-button compact" type="button" title="关闭" :disabled="petProfileSaving" @click="closePetProfileEditor">
            <X :size="16" />
          </button>
        </header>
        <div class="form-stack">
          <label>
            <span>名称</span>
            <input v-model.trim="petProfileDraft.display_name" maxlength="24" required placeholder="宠物名称" />
          </label>
          <label>
            <span>种类</span>
            <input v-model.trim="petProfileDraft.species" maxlength="24" placeholder="例如 dog、cat、松狮" />
          </label>
          <label>
            <span>说明</span>
            <textarea v-model.trim="petProfileDraft.notes" maxlength="420" rows="5" placeholder="外观特征、性格和当前动作包说明" />
          </label>
        </div>
        <footer class="modal-actions">
          <button class="button ghost" type="button" :disabled="petProfileSaving" @click="closePetProfileEditor">取消</button>
          <button class="button primary" type="submit" :disabled="petProfileSaving">
            <Save :size="16" />
            {{ petProfileSaving ? "保存中" : "保存资料" }}
          </button>
        </footer>
      </form>
    </section>

    <div v-if="toast" class="toast">{{ toast }}</div>
  </main>
</template>
