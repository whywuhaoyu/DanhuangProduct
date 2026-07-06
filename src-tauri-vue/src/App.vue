<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { listen, type UnlistenFn } from "@tauri-apps/api/event";
import {
  availableMonitors,
  currentMonitor,
  cursorPosition,
  getCurrentWindow,
  LogicalSize,
  PhysicalPosition,
  PhysicalSize,
  primaryMonitor,
  type Monitor,
} from "@tauri-apps/api/window";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
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
  FolderOpen,
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
  Trash2,
  Upload,
  X,
  Zap,
} from "@lucide/vue";
import { runtimeApi } from "./api/runtime";
import { MetricCard, StatusPill } from "./components";
import type {
  AiProviderTestResult,
  ChatMessageSummary,
  SecurityActionInput,
  SecurityActionResult,
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
const pageScrollRef = ref<HTMLElement | null>(null);
const THEME_KEY = "danhuang-panel-theme";
const PET_REFRESH_KEY = "danhuang-runtime-refresh";
const REMINDER_SIGNAL_KEY = "danhuang-reminder-signal";
const CHAT_SIGNAL_KEY = "danhuang-chat-signal";
const PET_BUBBLE_SIGNAL_KEY = "danhuang-pet-bubble-signal";
const PET_COMMAND_SIGNAL_KEY = "danhuang-pet-command-signal";
const REMINDER_CHECK_INTERVAL_MS = 30_000;
const PET_ROAM_INTERVAL_MS = 180;
const PET_ROAM_PAUSE_MS = 2_200;
const PET_ROAM_EDGE_PADDING = 12;
const PET_ROAM_MONITOR_SWITCH_CHANCE = 0.24;
const PET_DRAG_DIRECTION_THRESHOLD = 6;
const PET_DRAG_FEEDBACK_INTERVAL_MS = 16;
const PET_DRAG_IDLE_RESET_MS = 650;
const PET_DRAG_SAFETY_MS = 8_000;
const PET_DRAG_HINT_MS = 1_000;
const PET_DRAG_DIRECTION_SCORE_DECAY = 0.62;
const PET_DRAG_DIRECTION_TRIGGER_MULTIPLIER = 1.55;
const PET_DRAG_QUIET_MS = 180;
const PET_CLICK_MOVE_TOLERANCE = 8;
const PET_TOUCH_COOLDOWN_MS = 620;
const PET_TOUCH_EFFECT_MS = 920;
const PET_WINDOW_MIN_POSITION_DELTA = 1;
const PET_CURSOR_FOLLOW_INTERVAL_MS = 120;
const PET_CURSOR_FOLLOW_DURATION_MS = 12_000;
const PET_CURSOR_FOLLOW_STOP_DISTANCE = 46;
const PET_CURSOR_FOLLOW_POINTER_OFFSET_Y = 34;
const PET_RECALL_POINTER_OFFSET_X = 34;
const PET_RECALL_POINTER_OFFSET_Y = 42;
const PET_SETTLE_PAUSE_MS = 180_000;
const PET_TEMP_CLICK_THROUGH_MS = 30_000;
const AUTO_TALK_MIN_MS = 90_000;
const AUTO_TALK_MAX_MS = 180_000;
const PET_BUBBLE_TYPE_INTERVAL_MS = 28;
const PET_BUBBLE_MAX_QUEUE = 8;
const PET_BUBBLE_RECENT_SIGNAL_MS = 120_000;
const PET_COMMAND_RECENT_SIGNAL_MS = 20_000;
const PET_ATLAS_COLUMNS = 8;

type PanelThemeId = "studio" | "garden" | "daylight" | "soft-blue";
type ReminderTone = "sage" | "info" | "danger-soft" | "warn";
type ToastTone = "success" | "info" | "warn" | "danger-soft";
type ReminderFilter = "全部" | "今日" | "重要" | "已完成";
type ProviderState = "待配置 Key" | "可接入" | "测试中" | "已启用" | "当前" | "连接失败" | "高级";
type PresencePresetId = "companion" | "focus" | "playful" | "edge";
type PetTypeId = "all" | "dog" | "cat" | "meme" | "custom" | "other";
type PetCommandId =
  | "quick-talk"
  | "quick-chat"
  | "pet-touch"
  | "follow-cursor"
  | "stop-follow"
  | "recall-near-cursor"
  | "settle-near-edge"
  | "play-action"
  | "clear-bubbles";
type QuickToolAction = "pet-touch" | "pet-talk" | "recall-pet" | "settle-pet" | "reminder" | "chat" | "identity" | "motion";

interface ThemeOption {
  id: PanelThemeId;
  label: string;
  caption: string;
  swatches: string[];
}

interface PetTypeOption {
  id: PetTypeId;
  label: string;
}

interface BubblePaletteOption {
  id: string;
  label: string;
  caption: string;
  fill: string;
  outline: string;
  text: string;
}

interface PresencePreset {
  id: PresencePresetId;
  label: string;
  caption: string;
  icon: typeof Heart;
  settings: UpdateSettingsInput;
  bubble: string;
  status: string;
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

interface PetCommandSignal {
  command: PetCommandId;
  action_id: string;
  source: string;
  time: string;
  nonce: number;
}

interface PetBubbleQueueItem {
  id: string;
  message: string;
  actionId: string;
  source: string;
  priority: number;
  time: string;
}

interface PetTouchEffect {
  id: string;
  x: number;
  y: number;
  size: number;
  drift: number;
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

interface QuickTool {
  action: QuickToolAction;
  label: string;
  caption: string;
  icon: typeof Heart;
}

interface BuyerTask {
  id: string;
  label: string;
  caption: string;
  icon: typeof Heart;
  action: () => void | Promise<void>;
  status: string;
  tone: ReminderTone;
}

interface SecurityActionCard {
  action: SecurityActionInput["action"];
  label: string;
  caption: string;
  icon: typeof Heart;
  tone: ReminderTone;
}

interface RuntimeHealthItem {
  label: string;
  value: string;
  tone: ReminderTone;
}

interface QuickToolCard extends QuickTool {
  status: string;
  tone: ReminderTone;
}

interface PetRoamArea {
  monitor: Monitor;
  monitorKey: string;
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  allowCenter: boolean;
  clampCurrentPosition: boolean;
}

const petCommandIds: PetCommandId[] = [
  "quick-talk",
  "quick-chat",
  "pet-touch",
  "follow-cursor",
  "stop-follow",
  "recall-near-cursor",
  "settle-near-edge",
  "play-action",
  "clear-bubbles",
];

const petTypeOptions: PetTypeOption[] = [
  { id: "all", label: "全部" },
  { id: "dog", label: "狗狗" },
  { id: "cat", label: "猫咪" },
  { id: "meme", label: "梗系" },
  { id: "custom", label: "自定义" },
  { id: "other", label: "其他" },
];

const runtime = ref<RuntimeSummary | null>(null);
const currentAsset = ref("");
const currentAssetPath = ref("");
const referenceAssets = ref<string[]>([]);
const petSpriteAsset = ref("");
const petSpriteAssetPath = ref("");
const assetError = ref("");
const referenceAssetError = ref("");
const petSpriteError = ref("");
const actionDropActive = ref(false);
const lastActionImportResult = ref("");
const reminderSearch = ref("");
const reminderDeleteBusyId = ref("");
const securityActionBusy = ref<SecurityActionInput["action"] | "">("");
const securityActionResult = ref<SecurityActionResult | null>(null);
const loading = ref(true);
const activePage = ref("overview");
const toast = ref("");
const toastTone = ref<ToastTone>("info");
const petPinned = ref(true);
const quickMenuOpen = ref(false);
const quickMenuMoreOpen = ref(false);
const petSwitcherOpen = ref(false);
const identityPetTypeFilter = ref<PetTypeId>("all");
const quickMenuPetTypeFilter = ref<PetTypeId>("all");
const quickMenuPos = ref({ x: 44, y: 44 });
const activePetActionId = ref("idle");
const spriteFrame = ref(0);
let spriteFrameTimer: number | undefined;
let petBubbleTimer: number | undefined;
let petBubbleTypingTimer: number | undefined;
let reminderCheckTimer: number | undefined;
let petRoamTimer: number | undefined;
let autoTalkTimer: number | undefined;
let petRoamTargetX: number | null = null;
let petRoamTargetY: number | null = null;
let petRoamTargetMonitorKey: string | null = null;
let petRoamDirection: "left" | "right" = "right";
let petRoamBusy = false;
let petWindowSizeBusy = false;
let petRoamPausedUntil = 0;
let petActionHoldUntil = 0;
let petDragActive = false;
let petDragFeedbackBusy = false;
let petDragFeedbackTimer: number | undefined;
let petDragIdleTimer: number | undefined;
let petDragSafetyTimer: number | undefined;
let petDragStartCursor: { x: number; y: number } | null = null;
let petDragStartWindow: { x: number; y: number } | null = null;
let petDragLastCursorX: number | null = null;
let petDragDirection: "left" | "right" | "idle" = "idle";
let petDragDirectionScore = 0;
let petDragLastMoveAt = 0;
let petDragLastWindowX: number | null = null;
let petDragLastWindowY: number | null = null;
let petDragMoved = false;
let petDragHintShown = false;
let petDragHintTimer: number | undefined;
let suppressNextPetClick = false;
let lastPetTouchAt = 0;
let cursorFollowTimer: number | undefined;
let cursorFollowEndsAt = 0;
let cursorFollowBusy = false;
let temporaryClickThroughTimer: number | undefined;
let spriteLoadVersion = 0;
let unlistenRuntimeChanged: UnlistenFn | undefined;
let unlistenReminderTriggered: UnlistenFn | undefined;
let unlistenChatReply: UnlistenFn | undefined;
let lastHandledReminderSignal = "";
let lastHandledChatSignal = "";
let lastHandledPetBubbleSignal = "";
let lastHandledPetCommandSignal = "";
const activePetBubbleId = ref("");
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
  {
    id: "thought",
    label: "思考泡",
    caption: "当前本机默认，轻盈、有陪伴感。",
  },
  { id: "cloud", label: "云朵", caption: "更柔软，适合主动陪伴短句。" },
  { id: "rounded", label: "圆角", caption: "克制、清晰，适合工作时常开。" },
  { id: "comic", label: "漫画", caption: "边框更明确，适合互动反馈。" },
  { id: "minimal", label: "极简", caption: "低打扰，只保留文字和轻背景。" },
  { id: "pixel", label: "像素", caption: "更接近桌宠精灵图的玩具感。" },
];
const bubblePaletteOptions: BubblePaletteOption[] = [
  {
    id: "warm",
    label: "暖白便签",
    caption: "接近 Tk 默认气泡，温和不抢屏。",
    fill: "#fffaf0",
    outline: "#d8a760",
    text: "#3b3024",
  },
  {
    id: "mint",
    label: "薄荷轻声",
    caption: "降低橙色占比，适合长期挂桌面。",
    fill: "#f1fbf6",
    outline: "#74a98b",
    text: "#24453a",
  },
  {
    id: "blue",
    label: "浅蓝便签",
    caption: "和浅蓝页面背景搭配更清爽。",
    fill: "#f3f8ff",
    outline: "#79a8c6",
    text: "#233846",
  },
  {
    id: "paper",
    label: "漫画纸面",
    caption: "边框更明确，适合动作反馈。",
    fill: "#fffdf8",
    outline: "#2f807c",
    text: "#262b28",
  },
];
const presencePresets: PresencePreset[] = [
  {
    id: "companion",
    label: "陪伴模式",
    caption: "低频说话、贴边巡游，适合日常一直挂着。",
    icon: Heart,
    status: "低打扰",
    bubble: "我会安静陪着你，主人。",
    settings: {
      talk_enabled: true,
      roam_enabled: true,
      roam_allow_center: false,
      multi_monitor_roam: false,
      primary_monitor_edge_only: true,
      secondary_monitor_full_roam: false,
      click_through_enabled: false,
      roam_speed: 70,
      roam_distance: 0.35,
      talk_interval: 180,
      talk_after_interaction_delay: 18,
    },
  },
  {
    id: "focus",
    label: "专注勿扰",
    caption: "停止巡游和自动说话，保留右键和拖动恢复入口。",
    icon: Moon,
    status: "不打扰",
    bubble: "我先趴好，不打扰你。",
    settings: {
      talk_enabled: false,
      roam_enabled: false,
      roam_allow_center: false,
      multi_monitor_roam: false,
      primary_monitor_edge_only: true,
      secondary_monitor_full_roam: false,
      click_through_enabled: false,
      roam_speed: 55,
      roam_distance: 0.2,
      talk_interval: 300,
      talk_after_interaction_delay: 45,
    },
  },
  {
    id: "playful",
    label: "活跃互动",
    caption: "更积极地跑动、冒泡和响应摸摸。",
    icon: Zap,
    status: "更活泼",
    bubble: "主人，我跑一会儿给你看。",
    settings: {
      talk_enabled: true,
      roam_enabled: true,
      roam_allow_center: true,
      multi_monitor_roam: true,
      primary_monitor_edge_only: false,
      secondary_monitor_full_roam: true,
      click_through_enabled: false,
      roam_speed: 120,
      roam_distance: 0.78,
      talk_interval: 70,
      talk_after_interaction_delay: 6,
    },
  },
  {
    id: "edge",
    label: "桌边巡游",
    caption: "只沿当前屏边缘活动，保留手动互动。",
    icon: Map,
    status: "贴边",
    bubble: "我贴着桌边慢慢走。",
    settings: {
      talk_enabled: true,
      roam_enabled: true,
      roam_allow_center: false,
      multi_monitor_roam: true,
      primary_monitor_edge_only: true,
      secondary_monitor_full_roam: false,
      click_through_enabled: false,
      roam_speed: 60,
      roam_distance: 0.28,
      talk_interval: 220,
      talk_after_interaction_delay: 22,
    },
  },
];
const storedTheme = localStorage.getItem(THEME_KEY);
const activeThemeId = ref<PanelThemeId>(themeOptions.some((theme) => theme.id === storedTheme) ? (storedTheme as PanelThemeId) : "studio");
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

const quickTools: QuickTool[] = [
  { action: "pet-touch", label: "摸摸", caption: "给它一个轻反馈", icon: Heart },
  { action: "pet-talk", label: "说句话", caption: "低频陪伴短句", icon: MessageCircle },
  { action: "recall-pet", label: "召回", caption: "拉到鼠标旁边", icon: PanelRightOpen },
  { action: "settle-pet", label: "靠边", caption: "安静停在底边", icon: Moon },
  { action: "reminder", label: "加提醒", caption: "本地待办", icon: Bell },
  { action: "chat", label: "查资料", caption: "问答和资料检索", icon: CloudSun },
  { action: "identity", label: "切形象", caption: "家人列表", icon: Image },
  { action: "motion", label: "动作页", caption: "预览动作", icon: Play },
];

const securityActionCards: SecurityActionCard[] = [
  { action: "personal-backup", label: "个人备份", caption: "备份本机配置、提醒、聊天和加密 Key 配置副本。", icon: Save, tone: "sage" },
  { action: "public-export-check", label: "公开包检查", caption: "列出公开分发前必须排除的私人数据。", icon: ShieldCheck, tone: "warn" },
  { action: "open-data-dir", label: "打开数据目录", caption: "打开本机数据目录，方便核对真实记录。", icon: FolderOpen, tone: "info" },
  { action: "installer-status", label: "安装包状态", caption: "检查安装包是否已生成，并确认无需额外运行环境。", icon: PackageCheck, tone: "info" },
];

const baseActionIds = [
  "idle",
  "running-right",
  "running-left",
  "waving",
  "jumping",
  "failed",
  "waiting",
  "running",
  "review",
];

const roleStyles = ["蛋黄本色", "技术导师", "产品拆解", "知识博主", "短视频编导", "研究助手", "直说教练", "运营写手"];

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
const providerTestResult = ref<AiProviderTestResult | null>(null);
const providerSavingId = ref("");
const providerKeyModalMode = ref<"" | "replace" | "clear">("");
const providerKeyDraft = ref("");
const providerKeyConfirm = ref("");
const providerKeySaving = ref(false);

const chatMessages = ref<ChatMessageSummary[]>([]);
const chatLoading = ref(false);
const chatSending = ref(false);
const chatDraft = ref("");
const petInlineChatOpen = ref(false);
const petInlineChatDraft = ref("");
const petInlineChatInputRef = ref<HTMLInputElement | null>(null);
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
const petBubbleVisible = ref(false);
const petBubbleText = ref("我在这里，主人。");
const petBubbleFullText = ref("我在这里，主人。");
const petBubbleQueue = ref<PetBubbleQueueItem[]>([]);
const petTouchEffects = ref<PetTouchEffect[]>([]);
const petDragHintVisible = ref(false);
const petDragHintText = ref("我跟着你移动。");
const cursorFollowActive = ref(false);
const cursorFollowRemainingSeconds = ref(0);
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
const clickThroughEnabled = ref(false);
const clickThroughBusy = ref(false);
const settingsSaving = ref(false);
const petSwitchingId = ref("");
const petProfileSaving = ref(false);
const petImageUploading = ref<"" | "identity" | "reference">("");
const petActionUploading = ref(false);
const quickMenuSaving = ref(false);
const quickMenuDraft = ref<string[]>([]);
function nextCustomActionId() {
  return `custom:action-${Date.now().toString(36)}`;
}

const petActionDraft = ref({
  action_id: nextCustomActionId(),
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
  {
    type: "故事",
    title: "第一次把胖久接入家人列表",
    time: "2026-06-17",
    detail: "记录主像素图、现实照片和基础动作包状态。",
  },
  {
    type: "日记",
    title: "今天的陪伴摘要",
    time: "2026-06-18",
    detail: "短句、待办、资料查询和本地兜底都保持低打扰。",
  },
  {
    type: "思念",
    title: "蛋黄一直在",
    time: "长期",
    detail: "纪念表达保持克制，保留家人感，不做夸张替代。",
  },
];

const currentPet = computed(() => runtime.value?.current_pet ?? null);
const readyPets = computed(() =>
  (runtime.value?.pets.filter((pet) => pet.status === "ready") ?? [])
    .slice()
    .sort((a, b) => Number(b.id === runtime.value?.current_pet_id) - Number(a.id === runtime.value?.current_pet_id)),
);
const filteredReadyPets = computed(() => readyPets.value.filter((pet) => petMatchesType(pet, identityPetTypeFilter.value)));
const quickMenuReadyPets = computed(() => readyPets.value.filter((pet) => petMatchesType(pet, quickMenuPetTypeFilter.value)));
const navigationItems = computed(() => navGroups.flatMap((group) => group.items));
const activeTheme = computed(() => themeOptions.find((theme) => theme.id === activeThemeId.value) ?? themeOptions[0]);
const selectedProviderCard = computed(() => providerCards.value.find((provider) => provider.id === selectedProvider.value) ?? providerCards.value[0]);
const petMemorySummary = computed(() => petState.value?.memory ?? null);
const selectedStory = computed(() => petState.value?.stories.find((story) => story.id === selectedStoryId.value) ?? petState.value?.stories[0] ?? null);
const memoryTimelineItems = computed(() => {
  const memory = petMemorySummary.value;
  if (!memory) return [];
  return [...memory.emotional_patterns, ...memory.common_questions.map((question) => `常见问题: ${question}`), ...memory.notes].slice(0, 8);
});
const visibleReminders = computed(() => {
  const today = new Date().toISOString().slice(0, 10);
  const keyword = reminderSearch.value.trim().toLowerCase();
  let items = reminders.value.slice().sort((a, b) => Number(b.pinned) - Number(a.pinned) || Number(a.done) - Number(b.done));
  if (reminderFilter.value === "今日") items = items.filter((item) => item.due.includes("今日") || item.due.includes("今天") || item.due.startsWith(today));
  if (reminderFilter.value === "重要") items = items.filter((item) => item.priority !== "普通" || item.pinned);
  if (reminderFilter.value === "已完成") items = items.filter((item) => item.done);
  if (keyword) {
    items = items.filter((item) =>
      [item.title, item.note, item.due, item.category, item.priority, item.repeat]
        .join(" ")
        .toLowerCase()
        .includes(keyword),
    );
  }
  return items;
});
const selectedReminder = computed(() => reminders.value.find((item) => item.id === selectedReminderId.value) ?? visibleReminders.value[0] ?? null);
const reminderPreviewText = computed(() => {
  const title = reminderDraft.value.title.trim();
  const due = reminderDraft.value.due.trim() || "稍后";
  if (!title) return "输入标题后会先显示本地解析预览。";
  return `将创建提醒: ${title} / ${due} / 本地分类 / 普通优先级。`;
});
const companionLevel = computed(() => Math.max(1, Math.round(Number(runtime.value?.features.companion_level ?? 1) || 1)));
const companionXp = computed(() => Math.max(0, Math.round(Number(runtime.value?.features.companion_xp ?? 0) || 0)));
const companionInteractions = computed(() => Math.max(0, Math.round(Number(runtime.value?.features.companion_interactions ?? 0) || 0)));
const companionTalks = computed(() => Math.max(0, Math.round(Number(runtime.value?.features.companion_talks ?? 0) || 0)));
const companionLevelSpan = computed(() => Math.max(240, (companionLevel.value + 1) * 240));
const companionProgressXp = computed(() => companionXp.value % companionLevelSpan.value);
const companionXpToNext = computed(() => companionLevelSpan.value - companionProgressXp.value);
const companionProgressPercent = computed(() => clamp(Math.round((companionProgressXp.value / companionLevelSpan.value) * 100), 4, 100));
const companionProgressText = computed(() => {
  const prefix = runtime.value?.runtime_available ? "当前宠物真实陪伴状态" : "体验演示状态";
  return `${prefix}: ${companionXp.value} XP、互动 ${companionInteractions.value} 次、对话 ${companionTalks.value} 轮；按当前等级进度估算，距离下一阶段约 ${companionXpToNext.value} XP。`;
});
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
  { label: "工具", value: "时间/天气/汇率/资料", tone: "sage" as const },
  {
    label: "待办",
    value: runtime.value ? `${runtime.value.features.todo_open_count} 未完成` : "本地读取",
    tone: "sage" as const,
  },
  { label: "兜底", value: "短句陪伴", tone: "sage" as const },
]);
const runtimeHealthItems = computed<RuntimeHealthItem[]>(() => [
  {
    label: "数据状态",
    value: runtime.value?.runtime_available ? "已就绪" : "预览模式",
    tone: runtime.value?.runtime_available ? "sage" : "warn",
  },
  {
    label: "当前形象",
    value: currentPet.value?.display_name ?? "未读取",
    tone: currentPet.value ? "sage" : "warn",
  },
  {
    label: "提醒",
    value: runtime.value ? `${runtime.value.features.todo_open_count} 未完成` : "未读取",
    tone: runtime.value?.features.todo_pinned_count ? "warn" : "info",
  },
  {
    label: "AI",
    value: runtime.value?.features.saved_key_provider_count ? `${runtime.value.features.saved_key_provider_count} Key` : "本地兜底",
    tone: runtime.value?.features.saved_key_provider_count ? "sage" : "warn",
  },
  {
    label: "动作",
    value: runtime.value ? `${runtime.value.total_supported_actions} 个` : "未读取",
    tone: runtime.value?.total_supported_actions ? "sage" : "warn",
  },
]);
const quickToolCards = computed<QuickToolCard[]>(() =>
  quickTools.map((tool) => {
    if (tool.action === "chat") {
      return {
        ...tool,
        status: selectedProviderCard.value.hasSavedKey ? "云端可用" : "本地兜底",
        tone: selectedProviderCard.value.hasSavedKey ? "sage" : "warn",
      };
    }
    if (tool.action === "reminder") {
      return {
        ...tool,
        status: runtime.value ? `${runtime.value.features.todo_open_count} 未完成` : "本地读取",
        tone: runtime.value?.features.todo_pinned_count ? "warn" : "info",
      };
    }
    if (tool.action === "identity") {
      return {
        ...tool,
        status: runtime.value ? `${runtime.value.ready_pet_count} 可用` : "演示",
        tone: runtime.value?.ready_pet_count ? "sage" : "warn",
      };
    }
    if (tool.action === "motion") {
      return {
        ...tool,
        status: runtime.value ? `${runtime.value.total_supported_actions} 动作` : "演示",
        tone: runtime.value?.total_supported_actions ? "sage" : "warn",
      };
    }
    if (tool.action === "recall-pet" || tool.action === "settle-pet") {
      return {
        ...tool,
        status: runtime.value?.runtime_available ? "桌面可用" : "演示提示",
        tone: runtime.value?.runtime_available ? "sage" : "warn",
      };
    }
    return { ...tool, status: "立即可用", tone: "sage" };
  }),
);
const buyerTasks = computed<BuyerTask[]>(() => [
  {
    id: "show-pet",
    label: "显示桌宠",
    caption: petSpriteAsset.value || currentAsset.value ? "把它放回桌面，确认形象可见。" : "先显示桌宠；如素材缺失会引导修复形象。",
    icon: PanelRightOpen,
    action: showPetWindow,
    status: petSpriteAsset.value || currentAsset.value ? "形象可见" : "需修复",
    tone: petSpriteAsset.value || currentAsset.value ? "sage" : "warn",
  },
  {
    id: "chat",
    label: "和它说话",
    caption: "打开对话页，测试本地兜底或云端回复。",
    icon: MessageCircle,
    action: () => switchPage("chat"),
    status: selectedProviderCard.value.hasSavedKey ? "云端可用" : "本地兜底",
    tone: selectedProviderCard.value.hasSavedKey ? "sage" : "info",
  },
  {
    id: "reminder",
    label: "创建提醒",
    caption: "进入本地待办，添加第一条提醒。",
    icon: Bell,
    action: () => switchPage("reminders"),
    status: runtime.value ? `${runtime.value.features.todo_open_count} 未完成` : "待读取",
    tone: runtime.value?.features.todo_pinned_count ? "warn" : "sage",
  },
  {
    id: "privacy",
    label: "隐私与数据",
    caption: "检查备份、公开包排除项和安装包状态。",
    icon: ShieldCheck,
    action: () => switchPage("security"),
    status: "本机优先",
    tone: "sage",
  },
]);
const chatStatusSummary = computed(() => {
  const active = providerCards.value.find((provider) => provider.active) ?? selectedProviderCard.value;
  if (active?.hasSavedKey) return `${active.name} 云端回复 + 本地兜底`;
  if (active?.enabled) return `${active.name} 待配置 Key，本地兜底`;
  return "本地陪伴回复";
});
const providerKeyModalTitle = computed(() =>
  providerKeyModalMode.value === "clear" ? `清除 ${selectedProviderCard.value.name} Key` : `替换 ${selectedProviderCard.value.name} Key`,
);
const providerKeyActionDisabled = computed(() => {
  if (providerKeySaving.value || !providerKeyModalMode.value) return true;
  if (providerKeyModalMode.value === "clear") {
    return providerKeyConfirm.value.trim() !== selectedProviderCard.value.name;
  }
  return providerKeyDraft.value.trim().length < 8;
});
const selectedProviderTestResult = computed(() =>
  providerTestResult.value?.provider_id === selectedProvider.value ? providerTestResult.value : null,
);
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
    motion: "动作预览、右键动作栏和特色动作上传。",
    ai: "AI 厂商、模型、Key 隐私和测试反馈。",
    appearance: "透明窗口、气泡样式、颜色预设和即时预览。",
    behavior: "移动速度、巡游策略、多屏和安静时段。",
    security: "个人备份、公开分发边界和安装包导出。",
  };
  return map[activePage.value] ?? "桌面陪伴版页面。";
});
const activePresencePresetId = computed(() => presencePresets.find((preset) => presencePresetMatches(preset))?.id ?? "");

function numberSettingMatches(expected: number | undefined, actual: number, tolerance = 0.01) {
  if (expected === undefined) return true;
  return Math.abs(expected - actual) <= tolerance;
}

function presencePresetMatches(preset: PresencePreset) {
  const settings = preset.settings;
  return (
    (settings.talk_enabled === undefined || settings.talk_enabled === talkEnabled.value) &&
    (settings.roam_enabled === undefined || settings.roam_enabled === roamEnabled.value) &&
    (settings.roam_allow_center === undefined || settings.roam_allow_center === roamAllowCenter.value) &&
    (settings.multi_monitor_roam === undefined || settings.multi_monitor_roam === multiMonitorRoam.value) &&
    (settings.primary_monitor_edge_only === undefined || settings.primary_monitor_edge_only === primaryMonitorEdgeOnly.value) &&
    (settings.secondary_monitor_full_roam === undefined || settings.secondary_monitor_full_roam === secondaryMonitorFullRoam.value) &&
    (settings.click_through_enabled === undefined || settings.click_through_enabled === clickThroughEnabled.value) &&
    numberSettingMatches(settings.roam_speed, roamSpeedValue.value) &&
    numberSettingMatches(settings.roam_distance, roamDistanceValue.value) &&
    numberSettingMatches(settings.talk_interval, talkIntervalValue.value) &&
    numberSettingMatches(settings.talk_after_interaction_delay, talkAfterInteractionDelayValue.value)
  );
}

function chatSourceLabel(source: string) {
  if (source.startsWith("ai-research:")) {
    const providerId = source.split(":")[1] ?? "";
    const provider = providerCards.value.find((item) => item.id === providerId);
    return provider ? `云端资料 · ${provider.name}` : "云端资料";
  }
  if (source.startsWith("ai-weather:")) {
    const providerId = source.split(":")[1] ?? "";
    const provider = providerCards.value.find((item) => item.id === providerId);
    return provider ? `云端天气 · ${provider.name}` : "云端天气";
  }
  if (source.startsWith("ai-exchange:")) {
    const providerId = source.split(":")[1] ?? "";
    const provider = providerCards.value.find((item) => item.id === providerId);
    return provider ? `云端汇率 · ${provider.name}` : "云端汇率";
  }
  if (source.startsWith("ai-history:")) {
    const providerId = source.split(":")[1] ?? "";
    const provider = providerCards.value.find((item) => item.id === providerId);
    return provider ? `云端历史 · ${provider.name}` : "云端历史";
  }
  if (source.startsWith("ai:")) {
    const providerId = source.split(":")[1] ?? "";
    const provider = providerCards.value.find((item) => item.id === providerId);
    return provider ? `云端回复 · ${provider.name}` : "云端回复";
  }
  if (source.startsWith("weather-fallback:")) return "天气";
  if (source.startsWith("exchange-fallback:")) return "汇率";
  if (source.startsWith("history-fallback:")) return "历史资料";
  if (source.startsWith("research-fallback:")) return "资料摘要";
  if (source.startsWith("local-fallback:")) return "本地兜底";
  if (source.startsWith("local-time")) return "本机时间";
  if (source.startsWith("local")) return "本地短句";
  return source || "本地短句";
}

function chatSourceClass(source: string) {
  if (source.startsWith("ai-research:")) return "source-research";
  if (source.startsWith("ai-weather:")) return "source-weather";
  if (source.startsWith("ai-exchange:")) return "source-exchange";
  if (source.startsWith("ai-history:")) return "source-history";
  if (source.startsWith("ai:")) return "source-ai";
  if (source.startsWith("weather-fallback:")) return "source-weather";
  if (source.startsWith("exchange-fallback:")) return "source-exchange";
  if (source.startsWith("history-fallback:")) return "source-history";
  if (source.startsWith("research-fallback:")) return "source-research";
  if (source.startsWith("local-fallback:")) return "source-fallback";
  return "source-local";
}

const petVisualLabel = computed(() => currentPet.value?.display_name?.slice(0, 2) || "蛋黄");
const petStatusText = computed(() => (currentPet.value ? petStatusLabel(currentPet.value) : "等待本机数据"));
const playableActions = computed(() => currentPet.value?.actions ?? []);
const actionById = computed(() => new globalThis.Map(playableActions.value.map((action) => [action.id, action])));
const savedQuickMenuActionIds = computed(() => runtime.value?.settings.quick_menu_actions ?? []);
const activeQuickMenuActionItems = computed(() => {
  const items = savedQuickMenuActionIds.value.map((id) => actionById.value.get(id)).filter((action): action is PetActionSummary => Boolean(action));
  return items.length ? items : playableActions.value.slice(0, 8);
});
const quickMenuUnavailableCount = computed(() => savedQuickMenuActionIds.value.filter((id) => !actionById.value.has(id)).length);
const quickMenuDraftItems = computed(() =>
  quickMenuDraft.value.map((id) => actionById.value.get(id)).filter((action): action is PetActionSummary => Boolean(action)),
);
const quickMenuCandidateItems = computed(() => playableActions.value.filter((action) => !quickMenuDraft.value.includes(action.id)));
const activePetAction = computed(
  () =>
    playableActions.value.find((action) => action.id === activePetActionId.value) ??
    playableActions.value.find((action) => action.id === "idle") ??
    playableActions.value[0] ??
    null,
);
const baseActionItems = computed(() =>
  baseActionIds.map((id) => playableActions.value.find((action) => action.id === id)).filter((action): action is PetActionSummary => Boolean(action)),
);
const extensionActionItems = computed(() => playableActions.value.filter((action) => !baseActionIds.includes(action.id)));
const petScale = computed(() => Math.min(Math.max(Number(scaleValue.value) || 0.46, 0.2), 1.2));
const petStageWidth = computed(() => Math.max(SPRITE_CELL_WIDTH, Math.round(SPRITE_CELL_WIDTH * petScale.value) + 20));
const petStageHeight = computed(() => Math.max(SPRITE_CELL_HEIGHT, Math.round(SPRITE_CELL_HEIGHT * petScale.value) + 34));
const petWindowWidth = computed(() => Math.max(320, Math.min(420, petStageWidth.value + 96)));
const petWindowHeight = computed(() => Math.max(300, Math.min(420, petStageHeight.value + 84)));
const petWindowSizeLabel = computed(() => `${petWindowWidth.value} x ${petWindowHeight.value}`);
const roamPolicyLabel = computed(() => {
  if (roamCurrentMonitorOnly.value) return "当前屏限制";
  if (multiMonitorRoam.value) return secondaryMonitorFullRoam.value ? "多屏 + 副屏自由" : "多屏候选";
  return primaryMonitorEdgeOnly.value ? "主屏边缘" : "单屏巡游";
});
const roamPolicyCaption = computed(() => {
  if (roamCurrentMonitorOnly.value) return "自动巡游只跟随当前所在显示器；拖到另一块屏幕后，那块屏幕会成为新的活动范围。";
  if (multiMonitorRoam.value) return "自动巡游会从系统显示器列表中选择目标工作区，支持负坐标副屏。";
  if (primaryMonitorEdgeOnly.value && !roamAllowCenter.value) return "主屏优先贴近上下边缘水平移动，减少遮挡工作区。";
  return "自动巡游限制在当前显示器工作区内。";
});
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
  const row = action.source === "strip" ? 0 : (action.row ?? 0);
  const scale = Math.min(Math.max(petScale.value || 1, 0.2), 2.5);
  const columns = action.source === "strip" ? frameCount : PET_ATLAS_COLUMNS;
  return {
    width: `${Math.round(SPRITE_CELL_WIDTH * scale)}px`,
    height: `${Math.round(SPRITE_CELL_HEIGHT * scale)}px`,
    backgroundImage: `url("${petSpriteAsset.value}")`,
    backgroundPosition: `-${Math.round(frame * SPRITE_CELL_WIDTH * scale)}px -${Math.round(row * SPRITE_CELL_HEIGHT * scale)}px`,
    backgroundSize: `${Math.round(columns * SPRITE_CELL_WIDTH * scale)}px auto`,
  };
});
const petFallbackClasses = computed<Record<string, boolean>>(() => {
  const actionId = activePetAction.value?.id ?? "idle";
  return {
    "pet-fallback--idle": actionId === "idle",
    "pet-fallback--run": actionId === "running-right" || actionId === "running-left",
    "pet-fallback--run-left": actionId === "running-left",
    "pet-fallback--wave": actionId === "waving",
    "pet-fallback--jump": actionId === "jumping",
  };
});
const currentAssetIsSpritesheet = computed(
  () => Boolean(currentAsset.value && currentAssetPath.value && currentPet.value?.spritesheet_asset === currentAssetPath.value),
);
const panelSpritePreviewStyle = computed(() => {
  const action = activePetAction.value ?? playableActions.value.find((item) => item.id === "idle") ?? playableActions.value[0] ?? null;
  if (!action || !petSpriteAsset.value) return {};
  const frameCount = Math.max(action.frames, 1);
  const frame = spriteFrame.value % frameCount;
  const row = action.source === "strip" ? 0 : action.row ?? 0;
  const style: Record<string, string> = {
    width: `${SPRITE_CELL_WIDTH}px`,
    height: `${SPRITE_CELL_HEIGHT}px`,
    backgroundImage: `url("${petSpriteAsset.value}")`,
    backgroundPosition: `-${frame * SPRITE_CELL_WIDTH}px -${row * SPRITE_CELL_HEIGHT}px`,
  };
  if (action.source === "strip") {
    style.backgroundSize = `${frameCount * SPRITE_CELL_WIDTH}px ${SPRITE_CELL_HEIGHT}px`;
  }
  return style;
});

const quickMenuStyle = computed(() => {
  return {
    top: "10px",
    right: "auto",
    left: "24px",
    width: "210px",
    maxWidth: "calc(100vw - 48px)",
    maxHeight: "calc(100vh - 20px)",
  };
});
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
const petBubbleQueueCount = computed(() => petBubbleQueue.value.length + (activePetBubbleId.value ? 1 : 0));
const petBubblePriorityLabel = computed(() => {
  const top = petBubbleQueue.value.slice().sort((a, b) => b.priority - a.priority)[0];
  if (!top && activePetBubbleId.value) return "当前播放";
  if (!top) return "空闲";
  if (top.priority >= 90) return "提醒优先";
  if (top.priority >= 76) return "对话优先";
  if (top.priority >= 68) return "互动优先";
  if (top.priority <= 20) return "自动说话";
  return "普通";
});
const toastTitle = computed(() => {
  if (toastTone.value === "success") return "已完成";
  if (toastTone.value === "warn") return "需要处理";
  if (toastTone.value === "danger-soft") return "操作失败";
  return "状态更新";
});
const toastRole = computed(() => (toastTone.value === "danger-soft" || toastTone.value === "warn" ? "alert" : "status"));

function inferToastTone(message: string): ToastTone {
  if (/(失败|错误|异常|无法|不能|不可|超过|未支持)/.test(message)) return "danger-soft";
  if (/(请先|需要|等待|暂无|未读取|未配置)/.test(message)) return "warn";
  if (/(已|成功|保存|完成|开启|恢复|导入|切换|加入|写入|显示|隐藏)/.test(message)) return "success";
  return "info";
}

function showToast(message: string, tone: ToastTone = inferToastTone(message)) {
  toast.value = message;
  toastTone.value = tone;
  window.setTimeout(() => {
    if (toast.value === message) toast.value = "";
  }, 2800);
}

function dismissToast() {
  toast.value = "";
}

function publishRuntimeRefresh(reason: string) {
  localStorage.setItem(PET_REFRESH_KEY, `${Date.now()}:${reason}`);
}

function clearPetBubbleTimer() {
  if (petBubbleTimer !== undefined) {
    window.clearTimeout(petBubbleTimer);
    petBubbleTimer = undefined;
  }
}

function clearPetBubbleTypingTimer() {
  if (petBubbleTypingTimer !== undefined) {
    window.clearInterval(petBubbleTypingTimer);
    petBubbleTypingTimer = undefined;
  }
}

function clearPetBubbleLifecycle() {
  clearPetBubbleTimer();
  clearPetBubbleTypingTimer();
  activePetBubbleId.value = "";
}

function normalizeBubbleMessage(message: string) {
  return message.split(/\s+/).join(" ").trim().slice(0, 240);
}

function petBubblePriority(source = "local-preview") {
  const normalizedSource = source.toLowerCase();
  if (source === "reminder") return 90;
  if (
    source === "chat" ||
    source === "cloud" ||
    source === "local" ||
    source === "tool" ||
    normalizedSource.includes("chat") ||
    normalizedSource.includes("reply") ||
    normalizedSource.includes("fallback") ||
    normalizedSource.includes("weather") ||
    normalizedSource.includes("exchange") ||
    normalizedSource.includes("research")
  )
    return 76;
  if (source === "quick-menu" || source === "manual-preview" || source === "touch" || source === "action") return 68;
  if (source === "appearance") return 58;
  if (source === "auto-talk") return 20;
  return 50;
}

function trimPetBubbleQueueForIncoming(priority: number) {
  if (petBubbleQueue.value.length < PET_BUBBLE_MAX_QUEUE) return;
  const lowerPriorityIndex = petBubbleQueue.value.findIndex((item) => item.priority < priority);
  if (lowerPriorityIndex >= 0) {
    petBubbleQueue.value.splice(lowerPriorityIndex, 1);
    return;
  }
  const autoIndex = petBubbleQueue.value.findIndex((item) => item.source === "auto-talk");
  if (autoIndex >= 0) {
    petBubbleQueue.value.splice(autoIndex, 1);
    return;
  }
  petBubbleQueue.value.shift();
}

function enqueuePetBubble(item: PetBubbleQueueItem) {
  const insertIndex = petBubbleQueue.value.findIndex((queued) => queued.priority < item.priority);
  if (insertIndex >= 0) {
    petBubbleQueue.value.splice(insertIndex, 0, item);
  } else {
    petBubbleQueue.value.push(item);
  }
}

function finishActivePetBubble() {
  clearPetBubbleTimer();
  clearPetBubbleTypingTimer();
  petBubbleVisible.value = false;
  activePetBubbleId.value = "";
  window.setTimeout(() => {
    startNextPetBubble();
  }, 180);
}

function dismissCurrentPetBubble() {
  if (!petBubbleVisible.value && !activePetBubbleId.value) return;
  finishActivePetBubble();
}

function clearAllPetBubbles() {
  clearPetBubbleLifecycle();
  petBubbleQueue.value = [];
  petBubbleVisible.value = false;
  petBubbleText.value = "";
  activePetBubbleId.value = "";
}

function quickClearPetBubbles() {
  quickMenuOpen.value = false;
  clearAllPetBubbles();
}

function schedulePetBubbleHide(fullText: string) {
  clearPetBubbleTimer();
  const baseDuration = Math.min(Math.max(bubbleDuration.value || 6, 2), 20) * 1000;
  const readingBonus = Math.min(Math.max(fullText.length * 18, 0), 2600);
  petBubbleTimer = window.setTimeout(finishActivePetBubble, baseDuration + readingBonus);
}

function startNextPetBubble() {
  if (activePetBubbleId.value || !petBubbleQueue.value.length) return;
  const next = petBubbleQueue.value.shift();
  if (!next) return;

  activePetBubbleId.value = next.id;
  petBubbleFullText.value = next.message;
  petBubbleText.value = "";
  petBubbleVisible.value = true;
  pausePetRoam(1_600);

  if (next.actionId) {
    const action = playableActions.value.find((item) => item.id === next.actionId);
    holdPetAction();
    void setPetActionSilently(action);
  }

  const chars = Array.from(next.message);
  let index = 0;
  const reveal = () => {
    index += 1;
    petBubbleText.value = chars.slice(0, index).join("");
    if (index >= chars.length) {
      clearPetBubbleTypingTimer();
      schedulePetBubbleHide(next.message);
    }
  };

  reveal();
  if (chars.length > 1) {
    petBubbleTypingTimer = window.setInterval(reveal, PET_BUBBLE_TYPE_INTERVAL_MS);
  }
}

function showPetBubble(message = petBubbleFullText.value || petBubbleText.value, options: { source?: string; actionId?: string; replace?: boolean } = {}) {
  const normalized = normalizeBubbleMessage(message);
  if (!normalized) return;
  const source = options.source ?? "local-preview";
  const priority = petBubblePriority(source);

  if (options.replace) {
    clearPetBubbleLifecycle();
    petBubbleQueue.value = [];
    petBubbleVisible.value = false;
  }

  trimPetBubbleQueueForIncoming(priority);

  enqueuePetBubble({
    id: `${Date.now()}:${Math.random().toString(36).slice(2)}`,
    message: normalized,
    actionId: options.actionId ?? "",
    source,
    priority,
    time: nowIso(),
  });
  startNextPetBubble();
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
  showPetBubble(signal.message, {
    source: signal.source,
    actionId: signal.action_id || (signal.source === "auto-talk" ? pickAutoTalkAction()?.id : ""),
  });
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

function isPetCommandId(value: string): value is PetCommandId {
  return petCommandIds.includes(value as PetCommandId);
}

function petCommandSignalFromPayload(payload: unknown): PetCommandSignal | null {
  if (!payload || typeof payload !== "object") return null;
  const record = payload as Record<string, unknown>;
  const command = String(record.command ?? "");
  if (!isPetCommandId(command)) return null;
  const nonce = Number(record.nonce ?? Date.now());
  return {
    command,
    action_id: String(record.action_id ?? ""),
    source: String(record.source ?? "panel"),
    time: String(record.time ?? nowIso()),
    nonce: Number.isFinite(nonce) ? nonce : Date.now(),
  };
}

function petCommandSignalKey(signal: PetCommandSignal) {
  return `${signal.time}:${signal.source}:${signal.command}:${signal.action_id}:${signal.nonce}`;
}

async function handlePetCommandSignal(signal: PetCommandSignal) {
  if (viewMode !== "pet") return;
  const key = petCommandSignalKey(signal);
  if (lastHandledPetCommandSignal === key) return;
  lastHandledPetCommandSignal = key;

  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  switch (signal.command) {
    case "quick-talk":
      quickPetTalk();
      break;
    case "quick-chat":
      await quickPetChat();
      break;
    case "pet-touch":
      triggerPetTouch(undefined, signal.source || "panel-command");
      break;
    case "follow-cursor":
      startCursorFollow();
      break;
    case "stop-follow":
      stopCursorFollow();
      break;
    case "recall-near-cursor":
      await recallPetNearCursor(signal.source || "panel-recall");
      break;
    case "settle-near-edge":
      await settlePetNearEdge(signal.source || "panel-settle");
      break;
    case "play-action":
      if (signal.action_id) {
        queueAction(signal.action_id);
      }
      break;
    case "clear-bubbles":
      clearAllPetBubbles();
      break;
  }
}

function publishPetCommandSignal(command: PetCommandId, options: { actionId?: string; source?: string } = {}) {
  const signal: PetCommandSignal = {
    command,
    action_id: options.actionId ?? "",
    source: options.source ?? (viewMode === "panel" ? "panel" : "pet"),
    time: nowIso(),
    nonce: Date.now(),
  };
  localStorage.setItem(PET_COMMAND_SIGNAL_KEY, JSON.stringify(signal));
  if (viewMode === "pet") {
    void handlePetCommandSignal(signal);
  }
}

async function sendPetCommand(command: PetCommandId, options: { actionId?: string; source?: string; toast?: string } = {}) {
  try {
    if (viewMode === "panel") {
      await runtimeApi.showPet();
    }
    publishPetCommandSignal(command, options);
    if (options.toast) {
      showToast(options.toast);
    }
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  }
}

function runQuickTool(tool: QuickTool) {
  switch (tool.action) {
    case "pet-touch":
      void sendPetCommand("pet-touch", { source: "quick-tool:touch", toast: "已让桌宠做摸摸反馈" });
      break;
    case "pet-talk":
      void sendPetCommand("quick-talk", { source: "quick-tool:talk", toast: "已让桌宠说一句" });
      break;
    case "recall-pet":
      void sendPetCommand("recall-near-cursor", { source: "quick-tool:recall", toast: "已把桌宠召回到鼠标附近" });
      break;
    case "settle-pet":
      void sendPetCommand("settle-near-edge", { source: "quick-tool:settle", toast: "已让桌宠靠边休息" });
      break;
    case "reminder":
      switchPage("reminders");
      showToast("已打开提醒页");
      break;
    case "chat":
      switchPage("chat");
      showToast("已打开对话页，可继续问资料");
      break;
    case "identity":
      switchPage("identity");
      showToast("已打开形象页");
      break;
    case "motion":
      switchPage("motion");
      showToast("已打开动作页");
      break;
  }
}

function previewAutoTalk() {
  publishPetBubbleSignal(pickAutoTalkMessage(), "manual-preview", pickAutoTalkAction()?.id ?? "");
  showToast("已发送一条自动说话预览到桌宠窗口");
}

function quickPetTalk() {
  quickMenuOpen.value = false;
  publishPetBubbleSignal(pickAutoTalkMessage(), "quick-menu", pickAutoTalkAction()?.id ?? "");
}

async function quickPetChat() {
  if (chatSending.value) return;
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  chatSending.value = true;
  showPetBubble("我想想，马上回你。", {
    replace: true,
    source: "quick-chat",
    actionId: pickAutoTalkAction()?.id ?? "",
  });
  try {
    const message = await runtimeApi.sendChatMessage({
      text: "和我打个招呼，短短陪我一句。",
      role_style: selectedRoleStyle.value,
      now: nowIso(),
    });
    chatMessages.value = [...chatMessages.value, message].slice(-30);
    publishChatSignal(message, { replace: true });
    showToast("桌宠已回复一句聊天");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    chatSending.value = false;
  }
}

function openPetInlineChat() {
  if (viewMode !== "pet") {
    openPanelPage("chat");
    return;
  }
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  clearAllPetBubbles();
  petInlineChatOpen.value = true;
  pausePetRoam(4_000);
  void nextTick(() => {
    petInlineChatInputRef.value?.focus({ preventScroll: true });
  });
}

function closePetInlineChat() {
  petInlineChatOpen.value = false;
}

async function sendPetInlineChat() {
  const text = petInlineChatDraft.value.trim();
  if (!text) {
    showPetBubble("主人，先和我说一句吧。", {
      replace: true,
      source: "pet-inline-chat-empty",
      actionId: pickAutoTalkAction()?.id ?? "",
    });
    return;
  }
  if (chatSending.value) return;

  petInlineChatOpen.value = false;
  chatSending.value = true;
  showPetBubble("我听到了，想一想。", {
    replace: true,
    source: "pet-inline-chat",
    actionId: pickAutoTalkAction()?.id ?? "",
  });
  try {
    const message = await runtimeApi.sendChatMessage({
      text,
      role_style: selectedRoleStyle.value,
      now: nowIso(),
    });
    chatMessages.value = [...chatMessages.value, message].slice(-30);
    petInlineChatDraft.value = "";
    publishChatSignal(message, { replace: true });
    pausePetRoam(2_600);
  } catch (error) {
    showPetBubble("我刚刚没听清，再和我说一次好吗。", {
      replace: true,
      source: "pet-inline-chat-error",
      actionId: pickAutoTalkAction()?.id ?? "",
    });
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    chatSending.value = false;
  }
}

function petTouchMessage() {
  const name = currentPet.value?.display_name || "蛋黄";
  return `摸摸头，${name}摇了摇尾巴。`;
}

function pickPetTouchAction() {
  const action =
    playableActions.value.find((item) => item.id === "waving") ?? playableActions.value.find((item) => item.label.includes("挥")) ?? actionForRoam("idle");
  return action;
}

function addPetTouchEffect(x = window.innerWidth / 2, y = window.innerHeight / 2) {
  const effect: PetTouchEffect = {
    id: `${Date.now()}:${Math.random().toString(36).slice(2)}`,
    x,
    y,
    size: 16 + Math.round(Math.random() * 5),
    drift: Math.round((Math.random() - 0.5) * 24),
  };
  petTouchEffects.value = [...petTouchEffects.value, effect].slice(-6);
  window.setTimeout(() => {
    petTouchEffects.value = petTouchEffects.value.filter((item) => item.id !== effect.id);
  }, PET_TOUCH_EFFECT_MS);
}

function triggerPetTouch(event?: MouseEvent, source = "touch") {
  const now = Date.now();
  if (now - lastPetTouchAt < PET_TOUCH_COOLDOWN_MS) return;
  lastPetTouchAt = now;
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  pausePetRoam(2_400);
  const action = pickPetTouchAction();
  addPetTouchEffect(event?.clientX ?? window.innerWidth / 2, event?.clientY ?? window.innerHeight / 2);
  showPetBubble(petTouchMessage(), {
    replace: true,
    source,
    actionId: action?.id ?? "",
  });
}

function quickPetTouch() {
  triggerPetTouch(undefined, "quick-menu");
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
    if (quickMenuOpen.value || petBubbleVisible.value || petBubbleQueue.value.length) {
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

function holdPetAction(durationMs = 1_600) {
  if (viewMode !== "pet") return;
  petActionHoldUntil = Math.max(petActionHoldUntil, Date.now() + durationMs);
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

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function shouldMoveWindow(nextX: number, nextY: number, lastX: number | null, lastY: number | null, minDelta = PET_WINDOW_MIN_POSITION_DELTA) {
  return lastX === null || lastY === null || Math.abs(nextX - lastX) >= minDelta || Math.abs(nextY - lastY) >= minDelta;
}

function monitorKey(monitor: Monitor) {
  return [monitor.name ?? "monitor", monitor.position.x, monitor.position.y, monitor.size.width, monitor.size.height, monitor.scaleFactor].join(":");
}

function sameMonitor(left: Monitor | null | undefined, right: Monitor | null | undefined) {
  return Boolean(left && right && monitorKey(left) === monitorKey(right));
}

function isPrimaryRoamMonitor(monitor: Monitor, primary: Monitor | null) {
  return !primary || sameMonitor(monitor, primary);
}

function monitorDistanceFromCurrent(monitor: Monitor, current: Monitor | null) {
  if (!current) return 0;
  const monitorCenterX = monitor.workArea.position.x + monitor.workArea.size.width / 2;
  const monitorCenterY = monitor.workArea.position.y + monitor.workArea.size.height / 2;
  const currentCenterX = current.workArea.position.x + current.workArea.size.width / 2;
  const currentCenterY = current.workArea.position.y + current.workArea.size.height / 2;
  return Math.hypot(monitorCenterX - currentCenterX, monitorCenterY - currentCenterY);
}

function shouldRoamInMonitorCenter(monitor: Monitor, primary: Monitor | null) {
  const primaryLike = isPrimaryRoamMonitor(monitor, primary);
  if (!primaryLike && secondaryMonitorFullRoam.value) return true;
  if (primaryLike && primaryMonitorEdgeOnly.value && !roamAllowCenter.value) return false;
  return roamAllowCenter.value;
}

function chooseRoamMonitor(monitors: Monitor[], current: Monitor | null, primary: Monitor | null) {
  const fallback = current ?? monitors[0] ?? null;
  if (!fallback) return null;
  if (roamCurrentMonitorOnly.value || !multiMonitorRoam.value || monitors.length <= 1) return fallback;

  if (petRoamTargetMonitorKey) {
    const existing = monitors.find((monitor) => monitorKey(monitor) === petRoamTargetMonitorKey);
    if (existing) return existing;
  }

  const otherMonitors = monitors
    .filter((monitor) => !sameMonitor(monitor, current))
    .sort((left, right) => {
      if (secondaryMonitorFullRoam.value) {
        const primaryOrder = Number(isPrimaryRoamMonitor(left, primary)) - Number(isPrimaryRoamMonitor(right, primary));
        if (primaryOrder !== 0) return primaryOrder;
      }
      return monitorDistanceFromCurrent(left, current) - monitorDistanceFromCurrent(right, current);
    });
  if (!otherMonitors.length || Math.random() > PET_ROAM_MONITOR_SWITCH_CHANCE) return fallback;
  return otherMonitors[0];
}

function nearestEdgeY(value: number, minY: number, maxY: number) {
  if (value <= minY) return minY;
  if (value >= maxY) return maxY;
  return value - minY < maxY - value ? minY : maxY;
}

async function resolvePetRoamArea(windowSize: PhysicalSize): Promise<PetRoamArea | null> {
  const [current, monitors, primary] = await Promise.all([currentMonitor(), availableMonitors(), primaryMonitor().catch(() => null)]);
  const available = monitors.length ? monitors : current ? [current] : [];
  const monitor = chooseRoamMonitor(available, current, primary);
  if (!monitor) return null;

  const workArea = monitor.workArea;
  const minX = workArea.position.x + PET_ROAM_EDGE_PADDING;
  const maxX = workArea.position.x + workArea.size.width - windowSize.width - PET_ROAM_EDGE_PADDING;
  const minY = workArea.position.y + PET_ROAM_EDGE_PADDING;
  const maxY = workArea.position.y + workArea.size.height - windowSize.height - PET_ROAM_EDGE_PADDING;
  if (maxX <= minX || maxY <= minY) return null;

  petRoamTargetMonitorKey = monitorKey(monitor);
  return {
    monitor,
    monitorKey: petRoamTargetMonitorKey,
    minX,
    maxX,
    minY,
    maxY,
    allowCenter: shouldRoamInMonitorCenter(monitor, primary),
    clampCurrentPosition: keepOnScreen.value && sameMonitor(monitor, current),
  };
}

async function syncPetWindowSize() {
  if (viewMode !== "pet" || petWindowSizeBusy) return;
  petWindowSizeBusy = true;
  try {
    await getCurrentWindow().setSize(new LogicalSize(petWindowWidth.value, petWindowHeight.value));
    resetPetRoamTarget();
  } catch {
    // Browser preview and unsupported environments do not expose native window sizing.
  } finally {
    petWindowSizeBusy = false;
  }
}

async function syncPetWindowChrome() {
  if (viewMode !== "pet") return;
  try {
    const windowRef = getCurrentWindow();
    await Promise.allSettled([
      windowRef.setDecorations(false),
      windowRef.setShadow(false),
      windowRef.setBackgroundColor([0, 0, 0, 0]),
      getCurrentWebviewWindow().setBackgroundColor([0, 0, 0, 0]),
    ]);
    await runtimeApi.refreshPetWindow();
  } catch {
    // Browser preview and older WebView hosts can ignore native chrome cleanup.
  }
}

function schedulePetWindowChromeRefresh() {
  if (viewMode !== "pet") return;
  window.setTimeout(() => {
    void syncPetWindowChrome();
  }, 120);
  window.setTimeout(() => {
    void syncPetWindowChrome();
  }, 480);
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
  showPetBubble("气泡颜色已预览。", {
    replace: true,
    source: "appearance-preview",
  });
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
  clickThroughEnabled.value = viewMode === "pet" ? false : settings.click_through_enabled ?? clickThroughEnabled.value;
  void syncPetWindowSize();
  if (viewMode === "pet") {
    void syncPetClickThrough(false);
  }
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

function applySettingsInputLocally(input: UpdateSettingsInput) {
  if (input.scale !== undefined) scaleValue.value = input.scale;
  if (input.animation_speed !== undefined) animationSpeedValue.value = input.animation_speed;
  if (input.always_on_top !== undefined) petPinned.value = input.always_on_top;
  if (input.bubble_style !== undefined) selectedBubbleStyle.value = input.bubble_style;
  if (input.bubble_fill !== undefined) bubbleFill.value = input.bubble_fill;
  if (input.bubble_outline !== undefined) bubbleOutline.value = input.bubble_outline;
  if (input.bubble_text !== undefined) bubbleTextColor.value = input.bubble_text;
  if (input.bubble_duration !== undefined) bubbleDuration.value = input.bubble_duration;
  if (input.talk_enabled !== undefined) talkEnabled.value = input.talk_enabled;
  if (input.roam_enabled !== undefined) roamEnabled.value = input.roam_enabled;
  if (input.drag_sensitivity !== undefined) dragSensitivityValue.value = input.drag_sensitivity;
  if (input.inertia !== undefined) inertiaValue.value = input.inertia;
  if (input.roam_speed !== undefined) roamSpeedValue.value = input.roam_speed;
  if (input.roam_distance !== undefined) roamDistanceValue.value = input.roam_distance;
  if (input.roam_interval !== undefined) roamIntervalValue.value = input.roam_interval;
  if (input.idle_action_interval !== undefined) idleActionIntervalValue.value = input.idle_action_interval;
  if (input.talk_interval !== undefined) talkIntervalValue.value = input.talk_interval;
  if (input.talk_after_interaction_delay !== undefined) talkAfterInteractionDelayValue.value = input.talk_after_interaction_delay;
  if (input.roam_allow_center !== undefined) roamAllowCenter.value = input.roam_allow_center;
  if (input.multi_monitor_roam !== undefined) multiMonitorRoam.value = input.multi_monitor_roam;
  if (input.primary_monitor_edge_only !== undefined) primaryMonitorEdgeOnly.value = input.primary_monitor_edge_only;
  if (input.secondary_monitor_full_roam !== undefined) secondaryMonitorFullRoam.value = input.secondary_monitor_full_roam;
  if (input.roam_current_monitor_only !== undefined) roamCurrentMonitorOnly.value = input.roam_current_monitor_only;
  if (input.keep_on_screen !== undefined) keepOnScreen.value = input.keep_on_screen;
  if (input.lock_size_across_monitors !== undefined) lockSizeAcrossMonitors.value = input.lock_size_across_monitors;
  if (input.click_through_enabled !== undefined) clickThroughEnabled.value = input.click_through_enabled;
}

async function saveRuntimeSettings(input: UpdateSettingsInput, successMessage: string) {
  settingsSaving.value = true;
  try {
    const settings = await runtimeApi.updateSettings(input);
    commitRuntimeSettings(settings);
    publishRuntimeRefresh("settings");
    showToast(successMessage);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    settingsSaving.value = false;
  }
}

async function applyPresencePreset(preset: PresencePreset) {
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  applySettingsInputLocally(preset.settings);
  settingsSaving.value = true;
  if (preset.settings.click_through_enabled !== undefined) clickThroughBusy.value = true;
  try {
    const settings = await runtimeApi.updateSettings(preset.settings);
    commitRuntimeSettings(settings);
    if (preset.settings.click_through_enabled !== undefined) {
      await runtimeApi.setPetClickThrough(preset.settings.click_through_enabled);
    }
    publishRuntimeRefresh(`settings:presence:${preset.id}`);
    publishPetBubbleSignal(preset.bubble, `presence:${preset.id}`, pickAutoTalkAction()?.id ?? "");
    showToast(`${preset.label} 已保存并应用`);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    settingsSaving.value = false;
    clickThroughBusy.value = false;
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
    "外观偏好已保存到本机",
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
    "行为设置已保存到本机",
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
    showToast(
      message.source.startsWith("ai")
        ? "云端对话已记录"
        : message.source.startsWith("weather")
          ? "天气摘要已记录"
          : message.source.startsWith("exchange")
            ? "汇率摘要已记录"
            : message.source.startsWith("history") || message.source.startsWith("research")
              ? "资料摘要已记录"
              : "本地对话已记录",
    );
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

function showChatFeedback(signal: ChatSignal, options: { replace?: boolean } = {}) {
  const key = chatSignalKey(signal);
  if (lastHandledChatSignal === key) return;
  lastHandledChatSignal = key;
  const action = playableActions.value.find((item) => item.id === "waving") ?? playableActions.value.find((item) => item.id === "idle") ?? pickAutoTalkAction();
  showPetBubble(signal.reply, {
    source: signal.source || "chat",
    actionId: action?.id ?? "",
    replace: options.replace,
  });
}

function publishChatSignal(message: ChatMessageSummary, options: { replace?: boolean } = {}) {
  const signal: ChatSignal = {
    reply: message.reply,
    mood: message.mood,
    source: message.source,
    time: message.time,
  };
  showChatFeedback(signal, options);
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
    showToast("提醒详情已保存到本机");
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

async function testProvider(providerId = selectedProvider.value) {
  selectedProvider.value = providerId;
  const provider = providerCards.value.find((item) => item.id === providerId);
  if (!provider) return;
  providerSavingId.value = providerId;
  providerTestLog.value = `${provider.name} 正在发送一条不落盘的连接测试请求...`;
  providerTestResult.value = null;
  try {
    const result = await runtimeApi.testAiProviderConnection({ provider_id: providerId });
    providerTestResult.value = result;
    providerTestLog.value = result.message;
    const target = providerCards.value.find((item) => item.id === providerId);
    if (target) {
      target.state = result.ok ? (target.active ? "当前" : "可接入") : "连接失败";
      target.note = result.message;
    }
    showToast(result.title, result.ok ? "success" : "warn");
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    providerTestResult.value = {
      provider_id: providerId,
      ok: false,
      title: "测试失败",
      message,
      details: ["检查网络、Base URL、模型名和 Key 权限。"],
    };
    providerTestLog.value = message;
    const target = providerCards.value.find((item) => item.id === providerId);
    if (target) target.state = "连接失败";
    showToast(message, "warn");
  } finally {
    providerSavingId.value = "";
  }
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
      : {
          provider_id: provider.id,
          api_key: providerKeyDraft.value.trim(),
          clear: false,
        };

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
    showToast("提醒已保存到本机");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  }
}

async function toggleReminderDone(id: string) {
  const item = reminders.value.find((todo) => todo.id === id);
  if (!item) return;
  try {
    const todo = await runtimeApi.updateTodoState({
      id,
      done: !item.done,
      now: nowIso(),
    });
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
    const todo = await runtimeApi.updateTodoState({
      id,
      pinned: !item.pinned,
      now: nowIso(),
    });
    updateReminder(mapTodoToReminder(todo));
    await refreshRuntime();
    showToast(item.pinned ? "已取消置顶" : "提醒已置顶");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  }
}

async function deleteReminder(id: string) {
  const item = reminders.value.find((todo) => todo.id === id);
  if (!item || reminderDeleteBusyId.value) return;
  const confirmed = window.confirm(`确认删除提醒“${item.title}”？\n\n会从列表隐藏，但保留本机时间轴记录。`);
  if (!confirmed) return;
  reminderDeleteBusyId.value = id;
  try {
    await runtimeApi.updateTodoState({
      id,
      deleted: true,
      now: nowIso(),
    });
    reminders.value = reminders.value.filter((todo) => todo.id !== id);
    if (selectedReminderId.value === id) selectedReminderId.value = visibleReminders.value[0]?.id ?? "";
    if (activeDueReminder.value?.id === id) activeDueReminder.value = null;
    await refreshRuntime();
    showToast("提醒已软删除，时间轴仍保留记录");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    reminderDeleteBusyId.value = "";
  }
}

async function snoozeReminder(id: string, minutes = 15) {
  const snoozeUntil = new Date(Date.now() + minutes * 60 * 1000).toISOString();
  try {
    const todo = await runtimeApi.updateTodoState({
      id,
      snooze_until: snoozeUntil,
      now: nowIso(),
    });
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
  showPetBubble(message, {
    source: "reminder",
    actionId: pickReminderCueAction()?.id ?? "",
  });
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
  return (
    reminders.value
      .filter((reminder) => isReminderReadyToSignal(reminder, now))
      .sort((a, b) => {
        const aDue = parseReminderDate(a.due, now)?.getTime() ?? Number.MAX_SAFE_INTEGER;
        const bDue = parseReminderDate(b.due, now)?.getTime() ?? Number.MAX_SAFE_INTEGER;
        return Number(b.pinned) - Number(a.pinned) || aDue - bDue;
      })[0] ?? null
  );
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

async function loadPetSpriteForAction(
  action: PetActionSummary | null | undefined = activePetAction.value,
  pet: PetSummary | null | undefined = currentPet.value,
) {
  clearSpriteTimer();
  petSpriteError.value = "";
  const assetPath = spriteAssetPathForAction(action, pet);
  if (!assetPath) {
    petSpriteAsset.value = "";
    petSpriteAssetPath.value = "";
    petSpriteError.value = "正在使用内置默认形象，可导入精灵图升级动作";
    return;
  }
  if (petSpriteAsset.value && petSpriteAssetPath.value === assetPath) {
    spriteFrame.value = 0;
    scheduleSpriteFrame();
    return;
  }
  const loadVersion = ++spriteLoadVersion;
  try {
    const asset = await runtimeApi.getRuntimeAsset(assetPath);
    if (loadVersion !== spriteLoadVersion) return;
    petSpriteAsset.value = asset.data_url;
    petSpriteAssetPath.value = assetPath;
    spriteFrame.value = 0;
    scheduleSpriteFrame();
  } catch (error) {
    if (loadVersion !== spriteLoadVersion) return;
    if (!petSpriteAsset.value) petSpriteAssetPath.value = "";
    petSpriteError.value = error instanceof Error ? error.message : String(error);
  }
}

async function setPetAction(action: PetActionSummary) {
  stopCursorFollow(false);
  pausePetRoam(2_800);
  holdPetAction(1_800);
  activePetActionId.value = action.id;
  spriteFrame.value = 0;
  await loadPetSpriteForAction(action);
  showPetBubble(`${action.label}，主人。`, {
    replace: true,
    source: "action",
    actionId: action.id,
  });
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

function clearCursorFollowTimer() {
  if (cursorFollowTimer !== undefined) {
    window.clearInterval(cursorFollowTimer);
    cursorFollowTimer = undefined;
  }
}

function clearTemporaryClickThroughTimer() {
  if (temporaryClickThroughTimer !== undefined) {
    window.clearTimeout(temporaryClickThroughTimer);
    temporaryClickThroughTimer = undefined;
  }
}

function stopCursorFollow(showFeedback = true) {
  const wasActive = cursorFollowActive.value;
  clearCursorFollowTimer();
  cursorFollowActive.value = false;
  cursorFollowRemainingSeconds.value = 0;
  cursorFollowEndsAt = 0;
  cursorFollowBusy = false;
  if (wasActive) {
    if (showFeedback) {
      showPetBubble("我先停下来，主人。", {
        replace: true,
        source: "cursor-follow",
        actionId: actionForRoam("idle")?.id ?? "",
      });
    }
    void setPetActionSilently(actionForRoam("idle"));
  }
}

function cursorInsideMonitor(point: { x: number; y: number }, monitor: Monitor) {
  const area = monitor.workArea;
  return (
    point.x >= area.position.x &&
    point.x <= area.position.x + area.size.width &&
    point.y >= area.position.y &&
    point.y <= area.position.y + area.size.height
  );
}

async function resolveCursorFollowArea(cursor: { x: number; y: number }, windowSize: PhysicalSize) {
  const [current, monitors] = await Promise.all([currentMonitor().catch(() => null), availableMonitors().catch(() => [] as Monitor[])]);
  const monitor = monitors.find((item) => cursorInsideMonitor(cursor, item)) ?? current ?? monitors[0] ?? null;
  if (!monitor) return null;

  const workArea = monitor.workArea;
  const minX = workArea.position.x + PET_ROAM_EDGE_PADDING;
  const maxX = workArea.position.x + workArea.size.width - windowSize.width - PET_ROAM_EDGE_PADDING;
  const minY = workArea.position.y + PET_ROAM_EDGE_PADDING;
  const maxY = workArea.position.y + workArea.size.height - windowSize.height - PET_ROAM_EDGE_PADDING;
  if (maxX <= minX || maxY <= minY) return null;
  return { minX, maxX, minY, maxY };
}

async function resolveRecallMonitor(cursor: { x: number; y: number }) {
  const [current, primary, monitors] = await Promise.all([
    currentMonitor().catch(() => null),
    primaryMonitor().catch(() => null),
    availableMonitors().catch(() => [] as Monitor[]),
  ]);
  return monitors.find((monitor) => cursorInsideMonitor(cursor, monitor)) ?? current ?? primary ?? monitors[0] ?? null;
}

async function recallPetNearCursor(source = "panel-recall") {
  if (viewMode !== "pet") {
    showToast("召回桌宠请从控制面板触发");
    return;
  }
  stopCursorFollow(false);
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  pausePetRoam(2_800);

  try {
    const windowRef = getCurrentWindow();
    const [cursor, size] = await Promise.all([cursorPosition(), windowRef.outerSize()]);
    const monitor = await resolveRecallMonitor({ x: cursor.x, y: cursor.y });
    if (!monitor) throw new Error("未获取到屏幕区域");

    const workArea = monitor.workArea;
    const minX = workArea.position.x + PET_ROAM_EDGE_PADDING;
    const maxX = workArea.position.x + workArea.size.width - size.width - PET_ROAM_EDGE_PADDING;
    const minY = workArea.position.y + PET_ROAM_EDGE_PADDING;
    const maxY = workArea.position.y + workArea.size.height - size.height - PET_ROAM_EDGE_PADDING;
    const nextX = clamp(cursor.x + PET_RECALL_POINTER_OFFSET_X, Math.min(minX, maxX), Math.max(minX, maxX));
    const nextY = clamp(cursor.y + PET_RECALL_POINTER_OFFSET_Y, Math.min(minY, maxY), Math.max(minY, maxY));
    await windowRef.setPosition(new PhysicalPosition(Math.round(nextX), Math.round(nextY)));
    await setPetActionSilently(actionForRoam("idle"));
    addPetTouchEffect(window.innerWidth / 2, window.innerHeight / 2);
    showPetBubble("我回到你旁边了，主人。", {
      replace: true,
      source,
      actionId: actionForRoam("idle")?.id ?? "",
    });
  } catch {
    showPetBubble("我在这里，主人。", {
      replace: true,
      source,
      actionId: actionForRoam("idle")?.id ?? "",
    });
    showToast("当前环境无法移动桌宠，打包桌面版可用");
  }
}

async function settlePetNearEdge(source = "panel-settle") {
  if (viewMode !== "pet") {
    showToast("靠边休息请从控制面板触发");
    return;
  }
  stopCursorFollow(false);
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  pausePetRoam(PET_SETTLE_PAUSE_MS);

  try {
    const windowRef = getCurrentWindow();
    const [cursor, size] = await Promise.all([cursorPosition(), windowRef.outerSize()]);
    const monitor = await resolveRecallMonitor({ x: cursor.x, y: cursor.y });
    if (!monitor) throw new Error("未获取到屏幕区域");

    const workArea = monitor.workArea;
    const minX = workArea.position.x + PET_ROAM_EDGE_PADDING;
    const maxX = workArea.position.x + workArea.size.width - size.width - PET_ROAM_EDGE_PADDING;
    const minY = workArea.position.y + PET_ROAM_EDGE_PADDING;
    const maxY = workArea.position.y + workArea.size.height - size.height - PET_ROAM_EDGE_PADDING;
    const targetX = clamp(cursor.x - size.width * 0.5, Math.min(minX, maxX), Math.max(minX, maxX));
    const targetY = Math.max(minY, maxY);
    await windowRef.setPosition(new PhysicalPosition(Math.round(targetX), Math.round(targetY)));
    await setPetActionSilently(actionForRoam("idle"));
    addPetTouchEffect(window.innerWidth / 2, window.innerHeight / 2);
    showPetBubble("我靠边趴一会儿，安静陪你。", {
      replace: true,
      source,
      actionId: actionForRoam("idle")?.id ?? "",
    });
  } catch {
    showPetBubble("我先安静待着，主人。", {
      replace: true,
      source,
      actionId: actionForRoam("idle")?.id ?? "",
    });
    showToast("当前环境无法移动桌宠，打包桌面版可用");
  }
}

function cursorFollowStepPx() {
  const intervalSeconds = PET_CURSOR_FOLLOW_INTERVAL_MS / 1000;
  const speed = Math.min(Math.max(Number(roamSpeedValue.value) || 90, 40), 260);
  return Math.min(Math.max(Math.round(speed * intervalSeconds * 1.45), 8), 42);
}

async function tickCursorFollow() {
  if (!cursorFollowActive.value || cursorFollowBusy) return;
  if (viewMode !== "pet" || petDragActive || quickMenuOpen.value || clickThroughEnabled.value) {
    stopCursorFollow(false);
    return;
  }

  const remainingMs = cursorFollowEndsAt - Date.now();
  cursorFollowRemainingSeconds.value = Math.max(0, Math.ceil(remainingMs / 1000));
  if (remainingMs <= 0) {
    stopCursorFollow(false);
    return;
  }

  cursorFollowBusy = true;
  try {
    const windowRef = getCurrentWindow();
    const [cursor, position, size] = await Promise.all([cursorPosition(), windowRef.outerPosition(), windowRef.outerSize()]);
    const targetX = cursor.x - size.width * 0.5;
    const targetY = cursor.y + PET_CURSOR_FOLLOW_POINTER_OFFSET_Y - size.height * 0.45;
    const deltaX = targetX - position.x;
    const deltaY = targetY - position.y;
    const distance = Math.hypot(deltaX, deltaY);

    if (distance < PET_CURSOR_FOLLOW_STOP_DISTANCE) {
      await setPetActionSilently(actionForRoam("idle"));
      return;
    }

    const step = Math.min(cursorFollowStepPx(), distance);
    let nextX = position.x + (deltaX / distance) * step;
    let nextY = position.y + (deltaY / distance) * step;
    if (keepOnScreen.value) {
      const area = await resolveCursorFollowArea({ x: cursor.x, y: cursor.y }, size);
      if (area) {
        nextX = clamp(nextX, area.minX, area.maxX);
        nextY = clamp(nextY, area.minY, area.maxY);
      }
    }

    const direction = deltaX >= 0 ? "right" : "left";
    await setPetActionSilently(actionForRoam(direction));
    const roundedNextX = Math.round(nextX);
    const roundedNextY = Math.round(nextY);
    if (shouldMoveWindow(roundedNextX, roundedNextY, Math.round(position.x), Math.round(position.y))) {
      await windowRef.setPosition(new PhysicalPosition(roundedNextX, roundedNextY));
    }
  } catch {
    stopCursorFollow(false);
    showToast("当前环境不支持跟随光标，打包桌面版可用");
  } finally {
    cursorFollowBusy = false;
  }
}

function startCursorFollow(durationMs = PET_CURSOR_FOLLOW_DURATION_MS) {
  if (viewMode !== "pet") {
    showToast("跟随光标请在桌宠窗口右键使用");
    return;
  }
  if (clickThroughEnabled.value) {
    showToast("鼠标穿透开启时不能跟随光标，请先恢复桌宠交互");
    return;
  }

  clearCursorFollowTimer();
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  resetPetRoamTarget();
  cursorFollowActive.value = true;
  cursorFollowEndsAt = Date.now() + durationMs;
  cursorFollowRemainingSeconds.value = Math.ceil(durationMs / 1000);
  pausePetRoam(durationMs + 1_200);
  addPetTouchEffect(window.innerWidth / 2, window.innerHeight / 2);
  showPetBubble("我跟着鼠标走一小会儿。", {
    replace: true,
    source: "cursor-follow",
    actionId: actionForRoam("right")?.id ?? "",
  });
  cursorFollowTimer = window.setInterval(() => {
    void tickCursorFollow();
  }, PET_CURSOR_FOLLOW_INTERVAL_MS);
  void tickCursorFollow();
}

function toggleCursorFollow() {
  if (cursorFollowActive.value) {
    stopCursorFollow();
    return;
  }
  startCursorFollow();
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

function clearPetDragHintTimer() {
  if (petDragHintTimer !== undefined) {
    window.clearTimeout(petDragHintTimer);
    petDragHintTimer = undefined;
  }
}

function hidePetDragHint() {
  clearPetDragHintTimer();
  petDragHintVisible.value = false;
}

function showPetDragHint(text = "我跟着你移动。") {
  petDragHintText.value = text;
  petDragHintVisible.value = true;
  clearPetDragHintTimer();
  petDragHintTimer = window.setTimeout(() => {
    petDragHintTimer = undefined;
    petDragHintVisible.value = false;
  }, PET_DRAG_HINT_MS);
}

function schedulePetDragIdleReset(delay = PET_DRAG_IDLE_RESET_MS) {
  clearPetDragIdleTimer();
  petDragIdleTimer = window.setTimeout(() => {
    petDragIdleTimer = undefined;
    petDragDirection = "idle";
    petDragDirectionScore = 0;
    void settlePetRoamIdle();
  }, delay);
}

function updatePetDragAction(deltaX: number) {
  const threshold = petDragDirectionThreshold();
  const quietDelta = Math.max(1, threshold * 0.42);
  const now = Date.now();
  if (Math.abs(deltaX) < quietDelta) {
    petDragDirectionScore *= PET_DRAG_DIRECTION_SCORE_DECAY;
    if (Math.abs(petDragDirectionScore) < 1 && now - petDragLastMoveAt > PET_DRAG_QUIET_MS && petDragDirection !== "idle") {
      petDragDirection = "idle";
      void setPetActionSilently(actionForRoam("idle"));
    }
    return;
  }

  petDragLastMoveAt = now;
  petDragDirectionScore = clamp(petDragDirectionScore * PET_DRAG_DIRECTION_SCORE_DECAY + deltaX, -threshold * 3, threshold * 3);
  if (Math.abs(petDragDirectionScore) < threshold * PET_DRAG_DIRECTION_TRIGGER_MULTIPLIER) return;

  const nextDirection = petDragDirectionScore > 0 ? "right" : "left";
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
      if (Math.abs(position.x - petDragStartCursor.x) > PET_CLICK_MOVE_TOLERANCE || Math.abs(position.y - petDragStartCursor.y) > PET_CLICK_MOVE_TOLERANCE) {
        petDragMoved = true;
        if (!petDragHintShown) {
          petDragHintShown = true;
          showPetDragHint("我跟着你移动。");
        }
      }
      const nextX = Math.round(petDragStartWindow.x + position.x - petDragStartCursor.x);
      const nextY = Math.round(petDragStartWindow.y + position.y - petDragStartCursor.y);
      if (shouldMoveWindow(nextX, nextY, petDragLastWindowX, petDragLastWindowY)) {
        await getCurrentWindow().setPosition(new PhysicalPosition(nextX, nextY));
        petDragLastWindowX = nextX;
        petDragLastWindowY = nextY;
      }
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

function finishPetDragFeedback() {
  if (!petDragActive && petDragFeedbackTimer === undefined && petDragSafetyTimer === undefined) return;
  const moved = petDragMoved;
  petDragActive = false;
  petDragFeedbackBusy = false;
  petDragStartCursor = null;
  petDragStartWindow = null;
  petDragLastCursorX = null;
  petDragDirectionScore = 0;
  petDragLastMoveAt = 0;
  petDragLastWindowX = null;
  petDragLastWindowY = null;
  petDragHintShown = false;
  suppressNextPetClick = moved;
  petDragMoved = false;
  window.removeEventListener("mouseup", finishPetDragFeedback);
  window.removeEventListener("blur", finishPetDragFeedback);
  clearPetDragFeedbackTimer();
  clearPetDragSafetyTimer();
  hidePetDragHint();
  pausePetRoam(1_500);
  schedulePetDragIdleReset(petDragIdleResetDelay());
  if (moved && viewMode === "pet") {
    showPetBubble("我就在这里陪你，主人。", {
      replace: true,
      source: "drag-release",
      actionId: actionForRoam("idle")?.id ?? "",
    });
  }
}

async function beginPetDragFeedback(_event: MouseEvent) {
  petDragActive = true;
  petDragDirection = "idle";
  petDragLastCursorX = null;
  petDragDirectionScore = 0;
  petDragLastMoveAt = Date.now();
  petDragLastWindowX = null;
  petDragLastWindowY = null;
  petDragMoved = false;
  petDragHintShown = false;
  suppressNextPetClick = false;
  petDragStartCursor = null;
  petDragStartWindow = null;
  hidePetDragHint();
  clearPetDragIdleTimer();
  clearPetDragFeedbackTimer();
  clearPetDragSafetyTimer();
  pausePetRoam(4_000);
  const [position, windowPosition] = await Promise.all([cursorPosition(), getCurrentWindow().outerPosition()]);
  petDragStartCursor = { x: position.x, y: position.y };
  petDragStartWindow = { x: windowPosition.x, y: windowPosition.y };
  petDragLastCursorX = position.x;
  petDragLastWindowX = windowPosition.x;
  petDragLastWindowY = windowPosition.y;
  window.addEventListener("mouseup", finishPetDragFeedback);
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
  petRoamTargetMonitorKey = null;
}

async function settlePetRoamIdle() {
  resetPetRoamTarget();
  await setPetActionSilently(actionForRoam("idle"));
}

async function tickPetRoam() {
  if (viewMode !== "pet" || petRoamBusy) return;
  if (petDragActive) return;
  if (cursorFollowActive.value) return;
  if (!roamEnabled.value || quickMenuOpen.value || Date.now() < petRoamPausedUntil) {
    if (Date.now() >= petActionHoldUntil) {
      await settlePetRoamIdle();
    }
    return;
  }

  petRoamBusy = true;
  try {
    const windowRef = getCurrentWindow();
    const [position, size] = await Promise.all([windowRef.outerPosition(), windowRef.outerSize()]);
    const roamArea = await resolvePetRoamArea(size);
    if (!roamArea) return;

    const currentX = roamArea.clampCurrentPosition ? clamp(position.x, roamArea.minX, roamArea.maxX) : position.x;
    const currentY = roamArea.clampCurrentPosition ? clamp(position.y, roamArea.minY, roamArea.maxY) : position.y;
    if (roamArea.clampCurrentPosition && (currentX !== position.x || currentY !== position.y)) {
      const clampedCurrentX = Math.round(currentX);
      const clampedCurrentY = Math.round(currentY);
      if (shouldMoveWindow(clampedCurrentX, clampedCurrentY, Math.round(position.x), Math.round(position.y))) {
        await windowRef.setPosition(new PhysicalPosition(clampedCurrentX, clampedCurrentY));
      }
    }

    if (petRoamTargetX === null || Math.abs(petRoamTargetX - currentX) < 8) {
      const usableWidth = Math.max(roamArea.maxX - roamArea.minX, 1);
      const distanceRatio = Math.min(Math.max(Number(roamDistanceValue.value) || 0.35, 0.05), 1);
      const distance = Math.max(80, Math.round(usableWidth * distanceRatio));
      petRoamDirection =
        currentX < roamArea.minX - 24
          ? "right"
          : currentX > roamArea.maxX + 24
            ? "left"
            : currentX <= roamArea.minX + 24
              ? "right"
              : currentX >= roamArea.maxX - 24
                ? "left"
                : petRoamDirection === "right"
                  ? "left"
                  : "right";
      petRoamTargetX =
        petRoamDirection === "right"
          ? Math.min(Math.max(currentX + distance, roamArea.minX), roamArea.maxX)
          : Math.max(Math.min(currentX - distance, roamArea.maxX), roamArea.minX);
      if (Math.abs(petRoamTargetX - currentX) < 24) {
        petRoamTargetX = petRoamDirection === "right" ? roamArea.maxX : roamArea.minX;
      }
      petRoamTargetY = roamArea.allowCenter
        ? Math.round(roamArea.minY + Math.random() * Math.max(roamArea.maxY - roamArea.minY, 1))
        : nearestEdgeY(currentY, roamArea.minY, roamArea.maxY);
    }

    const nextDirection = petRoamTargetX >= currentX ? "right" : "left";
    petRoamDirection = nextDirection;
    const intervalSeconds = petRoamIntervalMs() / 1000;
    const step = Math.min(Math.max(Math.round((Number(roamSpeedValue.value) || 75) * intervalSeconds), 4), 32);
    const nextX = nextDirection === "right" ? Math.min(currentX + step, petRoamTargetX) : Math.max(currentX - step, petRoamTargetX);
    const targetY = petRoamTargetY ?? currentY;
    const nextY = Math.abs(targetY - currentY) <= step ? targetY : targetY > currentY ? currentY + step : currentY - step;

    await setPetActionSilently(actionForRoam(nextDirection));
    const nextInsideTarget = nextX >= roamArea.minX && nextX <= roamArea.maxX && nextY >= roamArea.minY && nextY <= roamArea.maxY;
    const shouldClampNext = keepOnScreen.value && (roamArea.clampCurrentPosition || nextInsideTarget);
    const clampedNextX = shouldClampNext ? clamp(nextX, roamArea.minX, roamArea.maxX) : nextX;
    const clampedNextY = shouldClampNext ? clamp(nextY, roamArea.minY, roamArea.maxY) : nextY;
    const roundedNextX = Math.round(clampedNextX);
    const roundedNextY = Math.round(clampedNextY);
    if (shouldMoveWindow(roundedNextX, roundedNextY, Math.round(currentX), Math.round(currentY))) {
      await windowRef.setPosition(new PhysicalPosition(roundedNextX, roundedNextY));
    }

    if (Math.abs(clampedNextX - petRoamTargetX) < 2 && Math.abs(clampedNextY - targetY) < 2) {
      petRoamTargetX = null;
      petRoamTargetY = null;
      petRoamTargetMonitorKey = null;
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
    if (viewMode === "panel") {
      activePetActionId.value = item.id;
      spriteFrame.value = 0;
      void loadPetSpriteForAction(item);
      void sendPetCommand("play-action", {
        actionId: item.id,
        source: "panel-action",
        toast: `已让桌宠播放${item.label}`,
      });
    } else {
      quickMenuOpen.value = false;
      quickMenuMoreOpen.value = false;
      void setPetAction(item);
    }
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
      ? `本机数据中有 ${summary.features.saved_key_provider_count} 个厂商保存了加密 Key，真实值不会返回前端。`
      : "本机数据未返回已保存 Key，前端只展示安全状态。";
  }
}

function syncQuickMenuDraft(summary: RuntimeSummary) {
  const available = new Set((summary.current_pet?.actions ?? []).map((action) => action.id));
  const configured = summary.settings.quick_menu_actions.filter((id, index, source) => available.has(id) && source.indexOf(id) === index);
  quickMenuDraft.value = configured.length ? configured : (summary.current_pet?.actions ?? []).slice(0, 8).map((action) => action.id);
}

async function loadAsset(path: string) {
  currentAsset.value = "";
  currentAssetPath.value = path;
  assetError.value = "";
  if (!path) {
    currentAssetPath.value = "";
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
  await runtimeApi.refreshPetWindow();
  if (clickThroughEnabled.value) {
    await setClickThrough(false, { persist: true });
  }
  showToast("桌宠窗口已显示");
}

async function hidePetWindow() {
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  petInlineChatOpen.value = false;
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

async function syncPetClickThrough(enabled = clickThroughEnabled.value) {
  if (clickThroughBusy.value) return;
  try {
    await runtimeApi.setPetClickThrough(enabled);
  } catch {
    // The panel can be previewed without native window control; explicit user toggles still report errors.
  }
}

async function setClickThrough(enabled: boolean, options: { persist?: boolean } = {}) {
  if (!enabled) {
    clearTemporaryClickThroughTimer();
  }
  const previous = clickThroughEnabled.value;
  clickThroughBusy.value = true;
  try {
    clickThroughEnabled.value = enabled;
    if (enabled) {
      stopCursorFollow(false);
      quickMenuOpen.value = false;
      petSwitcherOpen.value = false;
    }
    await runtimeApi.setPetClickThrough(enabled);
    if (options.persist) {
      await saveRuntimeSettings({ click_through_enabled: enabled }, enabled ? "鼠标穿透已开启并保存" : "鼠标穿透已关闭并保存");
    } else {
      showToast(enabled ? "短时穿透已开启，约 30 秒后自动恢复" : "桌宠交互已恢复");
    }
  } catch (error) {
    clickThroughEnabled.value = previous;
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    clickThroughBusy.value = false;
  }
}

async function enableTemporaryClickThrough(durationMs = PET_TEMP_CLICK_THROUGH_MS) {
  clearTemporaryClickThroughTimer();
  if (viewMode === "pet") {
    showPetBubble("我先不挡鼠标，半分钟后回来。", {
      replace: true,
      source: "quick-menu",
      actionId: pickAutoTalkAction()?.id ?? "",
    });
  }
  await setClickThrough(true);
  temporaryClickThroughTimer = window.setTimeout(() => {
    void setClickThrough(false);
  }, durationMs);
}

async function startPetDrag(event: MouseEvent) {
  if (event.button !== 0 || quickMenuOpen.value) return;
  const target = event.target instanceof HTMLElement ? event.target : null;
  if (target?.closest("button, input, textarea, select, a, .quick-menu, .pet-bubble, .pet-inline-chat")) return;
  event.preventDefault();
  stopCursorFollow(false);
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

function handlePetWindowClick(event: MouseEvent) {
  if (viewMode !== "pet") return;
  const target = event.target instanceof HTMLElement ? event.target : null;
  if (target?.closest("button, input, textarea, select, a, .quick-menu, .pet-bubble, .pet-inline-chat")) return;
  if (quickMenuOpen.value) {
    quickMenuOpen.value = false;
    return;
  }
  if (suppressNextPetClick) {
    suppressNextPetClick = false;
    return;
  }
  triggerPetTouch(event, "touch");
}

function openQuickMenu(event: MouseEvent) {
  event.stopPropagation();
  stopCursorFollow(false);
  pausePetRoam(4_000);
  quickMenuPos.value = { x: event.clientX, y: event.clientY };
  quickMenuMoreOpen.value = false;
  petSwitcherOpen.value = false;
  petInlineChatOpen.value = false;
  quickMenuOpen.value = true;
}

function isKnownPage(page: string) {
  return navGroups.some((group) => group.items.some((item) => item.id === page));
}

function resetPageScroll() {
  if (viewMode !== "panel") return;
  void nextTick(() => {
    const scroller = pageScrollRef.value;
    if (!scroller) return;
    scroller.scrollTo({ top: 0, left: 0 });
  });
}

function isVerticallyScrollableElement(element: HTMLElement) {
  const style = window.getComputedStyle(element);
  if (!/(auto|scroll|overlay)/.test(style.overflowY)) return false;
  return element.scrollHeight > element.clientHeight + 1;
}

function findPanelScrollableElement(target: EventTarget | null, boundary: HTMLElement) {
  let element = target instanceof HTMLElement ? target : null;
  while (element && element !== boundary) {
    if (isVerticallyScrollableElement(element)) return element;
    element = element.parentElement;
  }
  return null;
}

function canScrollElementInDirection(element: HTMLElement, deltaY: number) {
  if (deltaY < 0) return element.scrollTop > 1;
  if (deltaY > 0) return element.scrollTop + element.clientHeight < element.scrollHeight - 1;
  return false;
}

function scrollPageBy(delta: number) {
  const scroller = pageScrollRef.value;
  if (!scroller || !delta || scroller.scrollHeight <= scroller.clientHeight + 1) return false;
  const nextTop = clamp(scroller.scrollTop + delta, 0, scroller.scrollHeight - scroller.clientHeight);
  if (Math.abs(nextTop - scroller.scrollTop) < 1) return false;
  scroller.scrollTop = nextTop;
  return true;
}

function handleWorkspaceWheel(event: WheelEvent) {
  if (viewMode !== "panel" || !event.deltaY) return;
  const scroller = pageScrollRef.value;
  if (!scroller) return;
  const target = event.target instanceof HTMLElement ? event.target : null;
  const localScroller = findPanelScrollableElement(target, scroller.parentElement ?? scroller);
  if (localScroller && localScroller !== scroller && canScrollElementInDirection(localScroller, event.deltaY)) return;

  const deltaUnit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? scroller.clientHeight : 1;
  if (scrollPageBy(event.deltaY * deltaUnit)) event.preventDefault();
}

function handlePageScrollKeydown(event: KeyboardEvent) {
  if (viewMode !== "panel") return;
  const target = event.target instanceof HTMLElement ? event.target : null;
  if (target?.closest("input, textarea, select, button, [contenteditable='true']")) return;
  const scroller = pageScrollRef.value;
  if (!scroller) return;
  const line = 54;
  let handled = false;
  if (event.key === "ArrowDown") handled = scrollPageBy(line);
  if (event.key === "ArrowUp") handled = scrollPageBy(-line);
  if (event.key === "PageDown" || event.key === " ") handled = scrollPageBy(scroller.clientHeight * 0.86);
  if (event.key === "PageUp") handled = scrollPageBy(-scroller.clientHeight * 0.86);
  if (event.key === "Home") {
    handled = scroller.scrollTop > 0;
    scroller.scrollTop = 0;
  }
  if (event.key === "End") {
    const maxTop = scroller.scrollHeight - scroller.clientHeight;
    handled = scroller.scrollTop < maxTop - 1;
    scroller.scrollTop = maxTop;
  }
  if (handled) event.preventDefault();
}

function switchPage(page: string) {
  if (!isKnownPage(page)) return;
  activePage.value = page;
  resetPageScroll();
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
    if (viewMode === "panel") {
      activePage.value = page;
      resetPageScroll();
      if (page === "chat") {
        void refreshChatMessages();
      }
      if (page === "profile" || page === "story") {
        void refreshPetState();
      }
    }
    showToast(`已请求打开${navigationItems.value.find((item) => item.id === page)?.label ?? "控制面板"}`);
  }
  quickMenuOpen.value = false;
  petSwitcherOpen.value = false;
  void runtimeApi.showPanel();
}

function petStatusLabel(pet: PetSummary) {
  return `${pet.supported_action_count} 个动作，${pet.extension_action_count} 个特色动作`;
}

function petActionPackLabel(pet: PetSummary | null | undefined) {
  if (!pet) return "等待资料";
  if (pet.action_pack_level === "full") return "完整动作";
  if (pet.action_pack_level === "basic") return "基础动作";
  if (pet.action_pack_level === "builtin") return "内置动作";
  return "自定义动作";
}

function actionKindLabel(action: PetActionSummary) {
  return action.source === "strip" ? "特色动作" : "内置动作";
}

function normalizedPetTypeId(pet: PetSummary | null | undefined): PetTypeId {
  const typeId = pet?.pet_type?.trim();
  if (typeId === "dog" || typeId === "cat" || typeId === "meme" || typeId === "custom" || typeId === "other") return typeId;
  const species = pet?.species?.toLowerCase() ?? "";
  if (species.includes("dog") || species.includes("狗") || species.includes("犬") || species.includes("松狮")) return "dog";
  if (species.includes("cat") || species.includes("猫")) return "cat";
  if (species.includes("duck") || species.includes("鸭") || species.includes("梗")) return "meme";
  return species ? "other" : "custom";
}

function petTypeLabel(pet: PetSummary | null | undefined) {
  return pet?.pet_type_label?.trim() || petTypeOptions.find((item) => item.id === normalizedPetTypeId(pet))?.label || "自定义";
}

function petSpeciesLabel(pet: PetSummary | null | undefined) {
  return pet?.species?.trim() || "未标注物种";
}

function petMetaLabel(pet: PetSummary) {
  return `${petTypeLabel(pet)} · ${petSpeciesLabel(pet)} · ${petActionPackLabel(pet)}`;
}

function petMatchesType(pet: PetSummary, typeId: PetTypeId) {
  return typeId === "all" || normalizedPetTypeId(pet) === typeId;
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

function resetActionUploadDraft() {
  petActionDraft.value = {
    action_id: nextCustomActionId(),
    label: "摸摸头",
    frames: 4,
    durations: "220,180,180,260",
  };
  lastActionImportResult.value = "";
  showToast("动作上传表单已清空");
}

async function uploadPetActionStripFile(file: File | undefined) {
  if (!file || !currentPet.value) return;
  const frames = Math.min(Math.max(Math.round(Number(petActionDraft.value.frames) || 1), 1), 8);
  const actionId = petActionDraft.value.action_id.trim().toLowerCase().startsWith("custom:")
    ? petActionDraft.value.action_id.trim().toLowerCase()
    : nextCustomActionId();
  const label = petActionDraft.value.label.trim();
  if (!label) {
    showToast("请先填写动作名称");
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    showToast("动作文件超过 10MB，先压缩后再导入");
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
    lastActionImportResult.value = `${label} 已导入，${frames} 帧，已加入当前宠物动作清单；仍需人工确认身份、方向和透明边缘。`;
    petActionDraft.value.action_id = nextCustomActionId();
    showToast(`${label} 特色动作已导入`);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    petActionUploading.value = false;
    actionDropActive.value = false;
  }
}

async function uploadPetActionStrip(event: Event) {
  const inputEl = event.target as HTMLInputElement;
  const file = inputEl.files?.[0];
  inputEl.value = "";
  await uploadPetActionStripFile(file);
}

async function handleActionStripDrop(event: DragEvent) {
  actionDropActive.value = false;
  const file = event.dataTransfer?.files?.[0];
  await uploadPetActionStripFile(file);
}

async function clearPetActionStrip(action: PetActionSummary) {
  if (!currentPet.value || action.source !== "strip") return;
  const confirmed = window.confirm(`确认从动作清单移除“${action.label}”？\n\n不会删除磁盘上的原始动作文件，只会从当前宠物和右键栏移除。`);
  if (!confirmed) return;
  try {
    const summary = await runtimeApi.clearPetActionStrip({
      pet_id: currentPet.value.id,
      action_id: action.id,
    });
    await applyRuntimeSummary(summary, { refreshTodoList: false });
    localStorage.setItem(PET_REFRESH_KEY, `${Date.now()}:action-clear:${currentPet.value.id}:${action.id}`);
    lastActionImportResult.value = `${action.label} 已从动作清单移除，素材文件未物理删除。`;
    showToast("特色动作已从清单移除");
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
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

async function runSecurityAction(action: SecurityActionInput["action"]) {
  securityActionBusy.value = action;
  try {
    const result = await runtimeApi.runSecurityAction({ action });
    securityActionResult.value = result;
    showToast(result.message, result.tone);
  } catch (error) {
    showToast(error instanceof Error ? error.message : String(error));
  } finally {
    securityActionBusy.value = "";
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
    showPetBubble(`已切换为${pet.display_name}。`, {
      replace: true,
      source: "pet-switch",
    });
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
  if (event.key === PET_COMMAND_SIGNAL_KEY && event.newValue) {
    try {
      const signal = petCommandSignalFromPayload(JSON.parse(event.newValue));
      if (signal) void handlePetCommandSignal(signal);
    } catch {
      // Ignore malformed pet command signals from stale previews.
    }
  }
}

function isRecentSignalTime(raw: string, maxAgeMs = PET_BUBBLE_RECENT_SIGNAL_MS) {
  const time = new Date(raw).getTime();
  return Number.isFinite(time) && Date.now() - time <= maxAgeMs;
}

function readStoredSignal<T>(key: string, parse: (payload: unknown) => T | null) {
  const raw = localStorage.getItem(key);
  if (!raw) return null;
  try {
    return parse(JSON.parse(raw));
  } catch {
    return null;
  }
}

function hydrateRecentPetSignals() {
  if (viewMode !== "pet") return;

  const petSignal = readStoredSignal(PET_BUBBLE_SIGNAL_KEY, petBubbleSignalFromPayload);
  if (petSignal && isRecentSignalTime(petSignal.time)) {
    showPetBubbleSignal(petSignal);
  }

  const chatSignal = readStoredSignal(CHAT_SIGNAL_KEY, chatSignalFromPayload);
  if (chatSignal && isRecentSignalTime(chatSignal.time)) {
    showChatFeedback(chatSignal);
  }

  const reminderSignal = readStoredSignal(REMINDER_SIGNAL_KEY, reminderSignalFromPayload);
  if (reminderSignal && isRecentSignalTime(reminderSignal.time)) {
    showDueReminderFeedback(reminderSignal);
  }

  const commandSignal = readStoredSignal(PET_COMMAND_SIGNAL_KEY, petCommandSignalFromPayload);
  if (commandSignal && isRecentSignalTime(commandSignal.time, PET_COMMAND_RECENT_SIGNAL_MS)) {
    void handlePetCommandSignal(commandSignal);
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
      // 体验模式没有桌面事件总线。
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
    void syncPetWindowChrome();
    schedulePetWindowChromeRefresh();
    showPetBubble(petBubbleFullText.value || petBubbleText.value, {
      replace: true,
      source: "startup",
    });
    hydrateRecentPetSignals();
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
    resetPageScroll();
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

watch(
  [
    roamSpeedValue,
    roamDistanceValue,
    roamIntervalValue,
    roamAllowCenter,
    multiMonitorRoam,
    primaryMonitorEdgeOnly,
    secondaryMonitorFullRoam,
    roamCurrentMonitorOnly,
    keepOnScreen,
  ],
  () => {
    if (viewMode !== "pet" || !roamEnabled.value) return;
    resetPetRoamTarget();
    startPetRoamTimer();
  },
);

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
  clearPetBubbleTypingTimer();
  clearReminderCheckTimer();
  clearPetRoamTimer();
  clearCursorFollowTimer();
  clearTemporaryClickThroughTimer();
  clearAutoTalkTimer();
  finishPetDragFeedback();
  clearPetDragIdleTimer();
  hidePetDragHint();
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
    @click="handlePetWindowClick"
    @contextmenu.prevent="openQuickMenu"
  >
    <div v-if="petBubbleVisible" class="pet-bubble" :class="`pet-bubble--${selectedBubbleStyle}`" :style="bubbleCssVars" aria-live="polite">
      <span>{{ petBubbleText }}</span>
      <button class="pet-bubble__close" type="button" title="关闭气泡" @mousedown.stop @mouseup.stop @click.stop="clearAllPetBubbles">
        <X :size="13" />
      </button>
    </div>
    <div v-if="petDragHintVisible" class="pet-drag-hint" aria-live="polite">{{ petDragHintText }}</div>
    <section
      v-if="petInlineChatOpen"
      class="pet-inline-chat"
      aria-label="桌宠迷你对话"
      @mousedown.stop
      @click.stop
      @contextmenu.stop
    >
      <header>
        <span>和{{ currentPet?.display_name ?? "蛋黄" }}说话</span>
        <button class="icon-button compact" type="button" title="关闭对话" @click="closePetInlineChat">
          <X :size="14" />
        </button>
      </header>
      <div class="pet-inline-chat__row">
        <input
          ref="petInlineChatInputRef"
          v-model="petInlineChatDraft"
          aria-label="桌宠聊天输入"
          placeholder="说一句..."
          :disabled="chatSending"
          @keydown.enter.prevent="sendPetInlineChat"
          @keydown.esc.prevent="closePetInlineChat"
        />
        <button class="button primary" type="button" :disabled="chatSending" @click="sendPetInlineChat">
          {{ chatSending ? "想着" : "发送" }}
        </button>
      </div>
    </section>
    <div class="pet-stage" :class="{ 'pet-stage--fallback': !petSpriteAsset && !currentAsset }" :style="petStageStyle">
      <div
        v-if="petSpriteAsset && activePetAction"
        class="sprite-player"
        :style="petSpriteStyle"
        :aria-label="`${currentPet?.display_name ?? '当前宠物'}：${activePetAction.label}`"
      />
      <img v-else-if="currentAsset && !currentAssetIsSpritesheet" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" :style="petImageStyle" />
      <div
        v-else
        class="pet-fallback"
        :class="petFallbackClasses"
        :data-action="activePetAction?.id ?? 'idle'"
        role="img"
        :aria-label="`${currentPet?.display_name ?? '桌宠'}默认形象`"
      >
        <span class="pet-fallback__dog">
          <span class="pet-fallback__ear pet-fallback__ear--left" />
          <span class="pet-fallback__ear pet-fallback__ear--right" />
          <span class="pet-fallback__tail" />
          <span class="pet-fallback__face">
            <span class="pet-fallback__eye pet-fallback__eye--left" />
            <span class="pet-fallback__eye pet-fallback__eye--right" />
            <span class="pet-fallback__nose" />
          </span>
        </span>
        <strong>{{ petVisualLabel }}</strong>
        <button class="pet-repair-button" type="button" @mousedown.stop @click.stop="openPanelPage('identity')">导入形象</button>
      </div>
      <span v-if="activePetAction" class="pet-action-badge">{{ activePetAction.label }}</span>
      <span v-if="petSpriteError && !petSpriteAsset" class="pet-action-hint">{{ petSpriteError }}</span>
    </div>
    <span
      v-for="effect in petTouchEffects"
      :key="effect.id"
      class="pet-touch-effect"
      :style="{ left: `${effect.x}px`, top: `${effect.y}px`, '--touch-drift': `${effect.drift}px` }"
      aria-hidden="true"
    >
      <Heart :size="effect.size" />
    </span>

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
        <div class="quick-menu__grid quick-menu__grid--list">
          <button type="button" @click="quickPetTalk">说句话</button>
          <button type="button" @click="quickPetTouch">摸摸</button>
          <button type="button" @click="openPetInlineChat">直接对话</button>
          <button type="button" @click="openPanelPage('reminders')">提醒</button>
          <button type="button" @click="openPanelPage('overview')">控制面板</button>
          <button type="button" @click="hidePetWindow">隐藏</button>
        </div>
      </div>
      <button class="quick-menu__more-toggle" type="button" :aria-expanded="quickMenuMoreOpen" @click="quickMenuMoreOpen = !quickMenuMoreOpen">
        {{ quickMenuMoreOpen ? "收起更多" : "更多动作与设置" }}
      </button>
      <template v-if="quickMenuMoreOpen">
        <div class="quick-menu__section">
          <p>更多</p>
          <div class="quick-menu__grid quick-menu__grid--list">
            <button type="button" :disabled="chatSending" @click="quickPetChat">{{ chatSending ? "思考中" : "聊一句" }}</button>
            <button type="button" @click="openPanelPage('chat')">打开对话页</button>
            <button type="button" :class="{ active: cursorFollowActive }" @click="toggleCursorFollow">
              {{ cursorFollowActive ? `停止跟随 ${cursorFollowRemainingSeconds}s` : "跟随光标" }}
            </button>
            <button type="button" @click="settlePetNearEdge('quick-menu')">靠边休息</button>
            <button type="button" @click="quickClearPetBubbles">清空气泡</button>
            <button type="button" :class="{ active: petSwitcherOpen }" @click="petSwitcherOpen = !petSwitcherOpen">切换形象</button>
          </div>
        </div>
        <div class="quick-menu__section">
          <p>陪伴模式</p>
          <div class="quick-menu__grid quick-menu__grid--list quick-menu__grid--presence">
            <button
              v-for="preset in presencePresets"
              :key="preset.id"
              type="button"
              :class="{ active: activePresencePresetId === preset.id }"
              :disabled="settingsSaving || clickThroughBusy"
              @click="applyPresencePreset(preset)"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>
        <div v-if="petSwitcherOpen" class="quick-menu__pet-switcher">
          <p>家人形象</p>
          <div class="quick-menu__type-filter" aria-label="宠物类型筛选">
            <button
              v-for="type in petTypeOptions"
              :key="type.id"
              type="button"
              :class="{ active: quickMenuPetTypeFilter === type.id }"
              @click.stop="quickMenuPetTypeFilter = type.id"
            >
              {{ type.label }}
            </button>
          </div>
          <button
            v-for="pet in quickMenuReadyPets"
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
              <small>{{ petMetaLabel(pet) }}</small>
            </span>
            <StatusPill
              :label="pet.id === runtime?.current_pet_id ? '当前' : petSwitchingId === pet.id ? '切换中' : '切换'"
              :tone="pet.id === runtime?.current_pet_id ? 'info' : 'sage'"
            />
          </button>
          <small v-if="!quickMenuReadyPets.length" class="quick-menu__empty">这个类型下暂时没有可切换形象。</small>
          <button class="quick-menu__manage-link" type="button" @click="openPanelPage('identity')">管理全部形象</button>
        </div>
        <div class="quick-menu__section">
          <p>右键动作</p>
          <div class="quick-menu__grid quick-menu__grid--actions">
            <button v-for="item in activeQuickMenuActionItems.slice(0, 5)" :key="item.id" type="button" @click="queueAction(item)">
              {{ item.label }}
            </button>
            <button v-if="!activeQuickMenuActionItems.length" type="button" disabled>暂无可用动作</button>
            <button v-if="activeQuickMenuActionItems.length > 5" type="button" @click="openPanelPage('motion')">
              更多/管理 +{{ Math.max(activeQuickMenuActionItems.length - 5, 0) }}
            </button>
          </div>
        </div>
      </template>
      <footer v-if="quickMenuMoreOpen" class="quick-menu__footer">
        <button class="button ghost" type="button" @click="setPinned(!petPinned)">
          {{ petPinned ? "取消置顶" : "窗口置顶" }}
        </button>
        <button class="button ghost" type="button" :disabled="clickThroughBusy" @click="enableTemporaryClickThrough()">短时穿透</button>
      </footer>
    </section>

    <button class="pet-close" type="button" title="隐藏桌宠" @click.stop="hidePetWindow">
      <X :size="16" />
    </button>
    <div v-if="toast" class="toast pet-toast" :class="`toast--${toastTone}`" :role="toastRole" aria-live="polite">
      <div>
        <strong>{{ toastTitle }}</strong>
        <span>{{ toast }}</span>
      </div>
      <button class="toast__close" type="button" aria-label="关闭提示" @click="dismissToast">
        <X :size="14" />
      </button>
    </div>
  </div>

  <main v-else class="app-shell" :data-theme="activeThemeId">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">
          <img v-if="currentAsset && !currentAssetIsSpritesheet" :src="currentAsset" alt="" />
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
          <button v-for="item in group.items" :key="item.id" type="button" :class="{ active: activePage === item.id }" @click="switchPage(item.id)">
            <component :is="item.icon" :size="17" />
            <span>{{ item.label }}</span>
          </button>
        </section>
      </nav>

      <div class="sidebar-card">
        <div class="sidebar-card__title">
          <StatusPill :label="runtime?.runtime_available ? '数据就绪' : '预览模式'" tone="sage" />
          <button class="icon-button compact" type="button" title="刷新数据" @click="refreshRuntime">
            <RefreshCw :size="15" />
          </button>
        </div>
        <p>{{ currentPet?.display_name ?? "等待数据" }} · {{ runtime?.ready_pet_count ?? 0 }} 个可用形象</p>
      </div>
    </aside>

    <section class="workspace" @wheel="handleWorkspaceWheel">
      <header class="topbar">
        <div>
          <span class="eyebrow">桌面陪伴版</span>
          <h1>{{ pageTitle }}</h1>
          <p>{{ pageCaption }}</p>
          <div class="runtime-strip" aria-label="运行状态摘要">
            <div v-for="item in runtimeHealthItems" :key="item.label">
              <StatusPill :label="item.label" :tone="item.tone" />
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </div>
        <div class="topbar-actions">
          <div v-if="activePage === 'appearance'" class="theme-switcher" aria-label="页面背景">
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
          <button class="button ghost" type="button" @click="sendPetCommand('recall-near-cursor', { source: 'topbar-recall', toast: '已把桌宠召回到鼠标附近' })">
            <PanelRightOpen :size="16" />
            召回桌宠
          </button>
          <button class="button primary" type="button" @click="showPetWindow">
            <PanelRightOpen :size="16" />
            显示桌宠
          </button>
        </div>
      </header>

      <nav class="mobile-nav" aria-label="窄屏导航">
        <button v-for="item in navigationItems" :key="item.id" type="button" :class="{ active: activePage === item.id }" @click="switchPage(item.id)">
          <component :is="item.icon" :size="16" />
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div v-if="loading" class="loading-panel">
        <Heart :size="28" />
        <span>正在读取本机数据...</span>
      </div>

      <div v-else ref="pageScrollRef" class="page-scroll" tabindex="0" aria-label="页面内容" @keydown="handlePageScrollKeydown">
        <section v-if="activePage === 'overview'" class="dashboard-grid">
          <article class="panel hero-panel">
            <div class="hero-copy">
              <span class="eyebrow">当前陪伴</span>
              <h2>{{ currentPet?.display_name ?? "未读取到宠物" }}</h2>
              <p>买来第一分钟要能看到桌宠、说上话、记一条提醒，并确认隐私数据不会被误打包。</p>
              <div class="hero-actions">
                <button class="button primary" type="button" @click="showPetWindow">
                  <PanelRightOpen :size="16" />
                  显示桌宠
                </button>
                <button class="button ghost" type="button" @click="switchPage('security')">
                  <ShieldCheck :size="16" />
                  隐私与数据
                </button>
              </div>
            </div>
            <div class="hero-visual">
              <div class="pet-orbit">
                <div v-if="petSpriteAsset" class="panel-sprite-preview" :style="panelSpritePreviewStyle" :aria-label="currentPet?.display_name ?? '当前宠物'" />
                <img v-else-if="currentAsset && !currentAssetIsSpritesheet" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" />
                <div v-else class="pet-preview-fallback">
                  <Heart :size="44" />
                  <span>{{ assetError || "形象素材需要修复" }}</span>
                  <button class="button ghost compact-action" type="button" @click="switchPage('identity')">修复形象</button>
                </div>
              </div>
              <div class="floating-note">我在 · 不打扰 · 可关闭</div>
            </div>
          </article>

          <article class="panel wide-panel buyer-start-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">首次使用</span>
                <h2>买来先做这四件事</h2>
              </div>
              <CheckCircle2 :size="22" />
            </div>
            <div class="buyer-task-grid">
              <button v-for="task in buyerTasks" :key="task.id" class="action-card" type="button" @click="task.action()">
                <component :is="task.icon" :size="18" />
                <span class="action-card__body">
                  <strong>{{ task.label }}</strong>
                  <small>{{ task.caption }}</small>
                </span>
                <StatusPill :label="task.status" :tone="task.tone" />
                <ChevronRight class="action-card__arrow" :size="16" />
              </button>
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
              <MetricCard label="可用形象" :value="runtime?.ready_pet_count ?? 0" />
              <MetricCard label="可播放动作" :value="runtime?.total_supported_actions ?? 0" />
              <MetricCard label="特色动作" :value="runtime?.total_extension_assets ?? 0" />
            </div>
            <div class="progress-block">
              <div>
                <span>陪伴等级</span><strong>Lv. {{ companionLevel }}</strong>
              </div>
              <div class="progress-track"><span :style="{ width: `${companionProgressPercent}%` }" /></div>
              <p>{{ companionProgressText }}</p>
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
              <button v-for="tool in quickToolCards" :key="tool.label" class="action-card" type="button" @click="runQuickTool(tool)">
                <component :is="tool.icon" :size="18" />
                <span class="action-card__body">
                  <strong>{{ tool.label }}</strong>
                  <small>{{ tool.caption }}</small>
                </span>
                <StatusPill :label="tool.status" :tone="tool.tone" />
                <ChevronRight class="action-card__arrow" :size="16" />
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
              <div v-if="petSpriteAsset" class="panel-sprite-preview panel-sprite-preview--large" :style="panelSpritePreviewStyle" :aria-label="currentPet?.display_name ?? '当前宠物'" />
              <img v-else-if="currentAsset && !currentAssetIsSpritesheet" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" />
              <div v-else class="pet-preview-fallback"><Heart :size="40" /><span>等待图片</span></div>
            </div>
            <p class="identity-note">
              {{ currentPet?.notes || "还没有补充这个形象的说明。" }}
            </p>
            <div class="asset-upload-row">
              <label
                class="button ghost compact-action file-button"
                :class="{
                  disabled: petImageUploading === 'identity' || !currentPet,
                }"
              >
                <Upload :size="16" />
                {{ petImageUploading === "identity" ? "导入中" : "导入主形象" }}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  :disabled="petImageUploading !== '' || !currentPet"
                  @change="uploadPetImage('identity', $event)"
                />
              </label>
              <label
                class="button ghost compact-action file-button"
                :class="{
                  disabled: petImageUploading === 'reference' || !currentPet,
                }"
              >
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
                <span>现实参考图只保存在本机数据内，不记录原始本机路径。</span>
              </div>
            </div>
            <small v-if="referenceAssetError" class="inline-warning">{{ referenceAssetError }}</small>
            <div class="metric-row">
              <MetricCard label="动作" :value="currentPet?.supported_action_count ?? 0" />
              <MetricCard label="特色动作" :value="currentPet?.extension_action_count ?? 0" />
              <MetricCard label="参考图" :value="currentPet?.reference_assets.length ?? 0" />
              <MetricCard label="动作表现" :value="petActionPackLabel(currentPet)" />
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
            <div class="filter-row pet-type-filter" aria-label="宠物类型筛选">
              <button
                v-for="type in petTypeOptions"
                :key="type.id"
                type="button"
                :class="{ selected: identityPetTypeFilter === type.id }"
                @click="identityPetTypeFilter = type.id"
              >
                {{ type.label }}
              </button>
            </div>
            <div class="pet-list">
              <div v-for="pet in filteredReadyPets" :key="pet.id" class="pet-row" :class="{ current: pet.id === runtime?.current_pet_id }">
                <div class="pet-row__avatar">{{ petInitial(pet) }}</div>
                <div>
                  <strong>{{ pet.display_name }}</strong>
                  <span>{{ petMetaLabel(pet) }} · 参考图 {{ pet.reference_assets.length }}</span>
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
              <div v-if="!filteredReadyPets.length" class="empty-state compact">
                <Image :size="20" />
                <span>这个类型下暂时没有可用形象。</span>
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
              <MetricCard label="等级" :value="`Lv. ${companionLevel}`" />
              <MetricCard label="互动" :value="companionInteractions" />
              <MetricCard label="聊天" :value="companionTalks" />
            </div>
            <div class="memory-card">
              <StatusPill label="宠物级隔离" tone="sage" />
              <strong>长期记忆摘要</strong>
              <p v-if="petMemorySummary">
                {{ petMemorySummary.message_count }} 轮对话 · 最近情绪 {{ petMemorySummary.last_mood || "未记录" }} ·
                {{ petMemorySummary.updated_at || "未更新时间" }}
              </p>
              <p v-else>
                {{ petStateLoading ? "正在读取当前宠物记忆摘要..." : "当前宠物暂未读取到长期记忆摘要。" }}
              </p>
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
            <div v-if="!petStateLoading && !petState?.stories.length" class="empty-state">
              <BookOpen :size="24" />
              <span>当前宠物还没有故事记录。</span>
            </div>
          </article>
          <article class="panel reader-panel">
            <span class="eyebrow">阅读器</span>
            <h2>{{ selectedStory?.title ?? "选择一条故事" }}</h2>
            <p>
              {{ selectedStory?.content ?? "故事页保留全文阅读器和新增入口。删除用户故事或照片前仍需明确确认。" }}
            </p>
            <div v-if="petState?.role_prompt" class="timeline-list">
              <div>
                <BookOpen :size="14" /><span>角色 prompt 已保存 · {{ petState.summary_updated_at || "未记录更新时间" }}</span>
              </div>
              <div><ShieldCheck :size="14" /><span>故事和纪念内容只保存在本机数据里。</span></div>
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
                <h2>常用、基础动作、特色动作、窗口操作分组</h2>
              </div>
              <Play :size="22" />
            </div>
            <div class="operation-section">
              <h3>常用操作</h3>
              <div class="quick-tool-grid compact-grid">
                <button v-for="tool in quickToolCards.slice(0, 4)" :key="tool.label" class="action-card" type="button" @click="runQuickTool(tool)">
                  <component :is="tool.icon" :size="18" />
                  <span class="action-card__body">
                    <strong>{{ tool.label }}</strong>
                    <small>{{ tool.caption }}</small>
                  </span>
                  <StatusPill :label="tool.status" :tone="tool.tone" />
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
              <h3>特色动作</h3>
              <div class="chip-grid">
                <button v-for="item in extensionActionItems" :key="item.id" type="button" @click="queueAction(item)">
                  {{ item.label }}
                </button>
                <small v-if="!extensionActionItems.length">特色动作还未接入，后续可上传特色动作素材。</small>
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
                <button class="button ghost" type="button" @click="sendPetCommand('recall-near-cursor', { source: 'actions-panel', toast: '已把桌宠召回到鼠标附近' })">召回桌宠</button>
                <button class="button ghost" type="button" @click="sendPetCommand('settle-near-edge', { source: 'actions-panel', toast: '已让桌宠靠边休息' })">靠边休息</button>
                <button class="button ghost" type="button" @click="sendPetCommand('follow-cursor', { source: 'actions-panel', toast: '已让桌宠跟随光标 12 秒' })">跟随光标</button>
                <button class="button ghost" type="button" :disabled="chatSending" @click="sendPetCommand('quick-chat', { source: 'actions-panel', toast: '已让桌宠聊一句' })">
                  {{ chatSending ? "思考中" : "聊一句" }}
                </button>
                <button class="button ghost" type="button" @click="sendPetCommand('pet-touch', { source: 'actions-panel', toast: '已让桌宠做摸摸反馈' })">摸摸反馈</button>
                <button class="button ghost" type="button" @click="setPinned(!petPinned)">
                  {{ petPinned ? "取消置顶" : "窗口置顶" }}
                </button>
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
              <MetricCard label="特色动作" :value="runtime?.total_extension_assets ?? 0" />
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
                  <span>{{ actionKindLabel(item) }} · {{ item.frames }} 帧</span>
                </div>
                <div class="action-preview-card__meta">
                  <StatusPill :label="activePetActionId === item.id ? '播放中' : '可播放'" :tone="activePetActionId === item.id ? 'info' : 'sage'" />
                  <button
                    v-if="item.source === 'strip'"
                    class="icon-button compact"
                    type="button"
                    title="从动作清单移除"
                    @click.stop="clearPetActionStrip(item)"
                  >
                    <Trash2 :size="15" />
                  </button>
                </div>
              </button>
              <small v-if="!playableActions.length">当前宠物还没有可播放动作元数据。</small>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">特色动作导入</span>
                <h2>上传透明 PNG/WebP 特色动作</h2>
              </div>
              <Upload :size="22" />
            </div>
            <div
              class="action-drop-zone"
              :class="{ active: actionDropActive, disabled: petActionUploading || !currentPet }"
              @dragover.prevent="actionDropActive = true"
              @dragleave.prevent="actionDropActive = false"
              @drop.prevent="handleActionStripDrop"
            >
              <Upload :size="24" />
              <strong>{{ petActionUploading ? "正在导入特色动作" : "拖入 PNG/WebP 动作素材" }}</strong>
                <span>也可以先填名称和帧数，再用下方按钮选择文件。动作编号会自动生成。</span>
            </div>
            <div class="action-upload-form">
              <label>
                <span>显示名称</span>
                <input v-model.trim="petActionDraft.label" maxlength="24" placeholder="摸摸头" />
              </label>
              <label>
                <span>帧数</span>
                <input v-model.number="petActionDraft.frames" type="number" min="1" max="8" />
              </label>
              <label>
                <span>每帧时长 ms</span>
                <input v-model.trim="petActionDraft.durations" placeholder="220,180,180,260" />
              </label>
              <div class="button-row action-upload-actions">
                <label class="button primary file-button action-upload-button" :class="{ disabled: petActionUploading || !currentPet }">
                  <Upload :size="16" />
                  {{ petActionUploading ? "导入中" : "选择文件并导入" }}
                  <input type="file" accept="image/png,image/webp" :disabled="petActionUploading || !currentPet" @change="uploadPetActionStrip" />
                </label>
                <button class="button ghost" type="button" :disabled="petActionUploading" @click="resetActionUploadDraft">清空表单</button>
              </div>
            </div>
            <div v-if="lastActionImportResult" class="qa-result-card">
              <CheckCircle2 :size="18" />
              <span>{{ lastActionImportResult }}</span>
            </div>
            <div class="qa-list">
              <div><StatusPill label="尺寸" tone="sage" /><span>Rust 校验宽度等于 192 x 帧数，高度 208。</span></div>
              <div><StatusPill label="格式" tone="sage" /><span>动作素材只接受透明友好的 PNG/WebP。</span></div>
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
                      <span>{{ actionKindLabel(item) }} · {{ item.frames }} 帧</span>
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
                <button
                  v-for="role in roleStyles"
                  :key="role"
                  type="button"
                  :class="{ selected: selectedRoleStyle === role }"
                  @click="selectedRoleStyle = role"
                >
                  {{ role }}
                </button>
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
                <span class="eyebrow">AI 厂商</span>
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
              <div>
                <strong>当前状态</strong>
                <p>
                  {{ selectedProviderCard.active ? "当前厂商" : selectedProviderCard.enabled ? "已启用" : "未启用" }}
                </p>
              </div>
              <div>
                <strong>Key 状态</strong>
                <p>
                  {{ selectedProviderCard.hasSavedKey ? "已保存本机加密 Key" : "未保存 Key" }}
                </p>
              </div>
              <div>
                <strong>连接反馈</strong>
                <p>{{ providerTestLog }}</p>
                <div v-if="selectedProviderTestResult" class="qa-list compact-qa-list">
                  <div v-for="detail in selectedProviderTestResult.details" :key="detail">
                    <StatusPill :label="selectedProviderTestResult.ok ? '通过' : '待修复'" :tone="selectedProviderTestResult.ok ? 'sage' : 'warn'" />
                    <span>{{ detail }}</span>
                  </div>
                </div>
              </div>
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
              <button class="button ghost" type="button" :disabled="providerSavingId === selectedProviderCard.id" @click="testProvider()">
                {{ providerSavingId === selectedProviderCard.id ? "测试中..." : "测试连接" }}
              </button>
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
                <h2>添加本机提醒</h2>
              </div>
              <CalendarClock :size="22" />
            </div>
            <div class="quick-add">
              <input v-model="reminderDraft.title" aria-label="提醒标题" placeholder="提醒标题" @keydown.enter="addReminder" />
              <input v-model="reminderDraft.due" aria-label="提醒时间" placeholder="今天 18:30" @keydown.enter="addReminder" />
              <button class="button primary" type="button" @click="addReminder">
                <Plus :size="16" />
                添加提醒
              </button>
            </div>
            <p class="inline-helper">{{ reminderPreviewText }}</p>
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
              <input v-model="reminderSearch" aria-label="搜索提醒" placeholder="搜索标题、分类、备注" />
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
                <span>正在同步本机提醒...</span>
              </div>
              <button
                v-for="todo in visibleReminders"
                :key="todo.id"
                class="todo-card"
                :class="{
                  selected: selectedReminder?.id === todo.id,
                  done: todo.done,
                }"
                type="button"
                @click="selectedReminderId = todo.id"
              >
                <StatusPill :label="todo.priority" :tone="todo.tone" />
                <strong>{{ todo.title }}</strong>
                <span>
                  {{ todo.due }} · {{ todo.category }} · {{ todo.repeat }}{{ todo.pinned ? " · 置顶" : "" }}{{ todo.snoozeUntil ? " · 已稍后" : "" }}
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
                    <option v-for="priority in reminderPriorityOptions" :key="priority" :value="priority">
                      {{ priority }}
                    </option>
                  </select>
                </label>
                <label>
                  重复
                  <select v-model="reminderDetailDraft.repeat" :disabled="!selectedReminder" aria-label="编辑提醒重复规则">
                    <option v-for="option in reminderRepeatOptions" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                </label>
              </div>
              <label>
                备注
                <textarea
                  v-model="reminderDetailDraft.note"
                  :disabled="!selectedReminder"
                  aria-label="编辑提醒备注"
                  placeholder="补充提醒背景，默认只保存在本机。"
                />
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
                <button
                  class="button danger"
                  type="button"
                  :disabled="!selectedReminder || reminderDeleteBusyId === selectedReminder.id"
                  @click="selectedReminder && deleteReminder(selectedReminder.id)"
                >
                  <Trash2 :size="16" />
                  {{ reminderDeleteBusyId === selectedReminder?.id ? "删除中" : "删除" }}
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
              <div>
                <Clock3 :size="14" /><span>创建 · {{ selectedReminder?.createdAt || "等待同步" }}</span>
              </div>
              <div>
                <Bell :size="14" /><span>上次提醒 · {{ selectedReminder?.lastRemindedAt || "未触发" }}</span>
              </div>
              <div>
                <CircleDot :size="14" /><span>累计提醒 · {{ selectedReminder?.remindCount ?? 0 }} 次</span>
              </div>
              <div>
                <Timer :size="14" /><span>稍后 · {{ selectedReminder?.snoozeUntil || "未设置" }}</span>
              </div>
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
              <MetricCard label="队列" :value="`${petBubbleQueueCount} 条`" />
              <MetricCard label="优先级" :value="petBubblePriorityLabel" />
              <MetricCard label="背景" :value="activeTheme.label" />
            </div>
            <div class="button-row">
              <button class="button ghost" type="button" @click="previewAutoTalk">
                <MessageCircle :size="16" />
                发一条预览
              </button>
              <button class="button ghost" type="button" :disabled="!petBubbleVisible" @click="dismissCurrentPetBubble">
                <X :size="16" />
                跳过当前
              </button>
              <button class="button ghost" type="button" :disabled="!petBubbleVisible && !petBubbleQueue.length" @click="clearAllPetBubbles">
                清空队列
              </button>
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
                <h2>本机气泡样式预览和保存</h2>
              </div>
              <Eye :size="22" />
            </div>
            <div class="bubble-style-grid">
              <button
                v-for="style in bubbleStyleOptions"
                :key="style.id"
                type="button"
                :class="{ selected: selectedBubbleStyle === style.id }"
                @click="
                  selectedBubbleStyle = style.id;
                  showPetBubble(`气泡样式已切换为${style.label}。`, {
                    replace: true,
                    source: 'appearance-preview',
                  });
                  showToast(`气泡样式预览切换为 ${style.label}`);
                "
              >
                <span>{{ style.label }}</span>
                <strong>{{ style.id }}</strong>
                <small>{{ style.caption }}</small>
              </button>
            </div>
            <div class="bubble-config-section">
              <div class="section-title-row">
                <strong>气泡配色</strong>
                <span>保存到本机，不影响页面背景主题</span>
              </div>
              <div class="bubble-palette-grid">
                <button
                  v-for="palette in bubblePaletteOptions"
                  :key="palette.id"
                  type="button"
                  :class="{ selected: activeBubblePaletteId === palette.id }"
                  @click="selectBubblePalette(palette)"
                >
                  <span
                    class="bubble-palette-preview"
                    :style="{
                      background: palette.fill,
                      borderColor: palette.outline,
                      color: palette.text,
                    }"
                    >Aa</span
                  >
                  <strong>{{ palette.label }}</strong>
                  <small>{{ palette.caption }}</small>
                </button>
              </div>
              <div class="bubble-control-grid">
                <label>
                  <span>背景</span>
                  <input
                    v-model="bubbleFill"
                    type="color"
                    aria-label="气泡背景色"
                    @input="
                      showPetBubble('气泡背景已预览。', {
                        replace: true,
                        source: 'appearance-preview',
                      })
                    "
                  />
                </label>
                <label>
                  <span>描边</span>
                  <input
                    v-model="bubbleOutline"
                    type="color"
                    aria-label="气泡描边色"
                    @input="
                      showPetBubble('气泡描边已预览。', {
                        replace: true,
                        source: 'appearance-preview',
                      })
                    "
                  />
                </label>
                <label>
                  <span>文字</span>
                  <input
                    v-model="bubbleTextColor"
                    type="color"
                    aria-label="气泡文字色"
                    @input="
                      showPetBubble('气泡文字已预览。', {
                        replace: true,
                        source: 'appearance-preview',
                      })
                    "
                  />
                </label>
                <label class="bubble-duration-control">
                  <span
                    >显示时长 <strong>{{ bubbleDuration.toFixed(0) }} 秒</strong></span
                  >
                  <input
                    v-model.number="bubbleDuration"
                    type="range"
                    min="2"
                    max="20"
                    step="1"
                    @input="
                      showPetBubble('显示时长已预览。', {
                        replace: true,
                        source: 'appearance-preview',
                      })
                    "
                  />
                </label>
              </div>
            </div>
            <div class="button-row panel-actions">
              <button class="button primary" type="button" :disabled="settingsSaving" @click="saveAppearanceSettings">
                <Save :size="16" />
                {{ settingsSaving ? "保存中" : "保存外观偏好" }}
              </button>
              <button
                class="button ghost"
                type="button"
                @click="
                  showPetBubble('这是保存前的气泡预览。', {
                    replace: true,
                    source: 'appearance-preview',
                  })
                "
              >
                预览桌宠气泡
              </button>
              <button class="button ghost" type="button" @click="selectTheme('studio')">恢复清透工作台</button>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'behavior'" class="content-grid">
          <article class="panel wide-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">陪伴场景</span>
                <h2>把复杂参数收成可直接使用的桌宠模式</h2>
              </div>
              <Sparkles :size="22" />
            </div>
            <div class="presence-preset-grid">
              <button
                v-for="preset in presencePresets"
                :key="preset.id"
                class="presence-preset-card"
                type="button"
                :class="{ selected: activePresencePresetId === preset.id }"
                :disabled="settingsSaving || clickThroughBusy"
                @click="applyPresencePreset(preset)"
              >
                <component :is="preset.icon" :size="20" />
                <span>
                  <strong>{{ preset.label }}</strong>
                  <small>{{ preset.caption }}</small>
                </span>
                <StatusPill :label="activePresencePresetId === preset.id ? '当前' : preset.status" :tone="activePresencePresetId === preset.id ? 'info' : 'sage'" />
              </button>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">行为</span>
                <h2>巡游、拖动、多屏和安静时段</h2>
              </div>
              <Map :size="22" />
            </div>
            <div class="mode-grid">
              <button
                type="button"
                :class="{
                  selected: primaryMonitorEdgeOnly && !roamAllowCenter,
                }"
                @click="
                  primaryMonitorEdgeOnly = true;
                  roamAllowCenter = false;
                "
              >
                <Moon :size="20" />
                <strong>边缘安静</strong>
                <span>主屏四边，不挡工作内容。</span>
              </button>
              <button type="button" :class="{ selected: roamAllowCenter }" @click="roamAllowCenter = !roamAllowCenter">
                <Zap :size="20" />
                <strong>当前屏自由</strong>
                <span>允许跑到当前屏幕中间。</span>
              </button>
              <button
                type="button"
                :class="{ selected: multiMonitorRoam }"
                @click="
                  multiMonitorRoam = !multiMonitorRoam;
                  secondaryMonitorFullRoam = multiMonitorRoam;
                "
              >
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
                <span>{{ roamEnabled ? "开启，按本机策略移动" : "关闭，停留在当前位置" }}</span>
              </button>
              <button
                class="switch-card"
                :class="{ selected: clickThroughEnabled }"
                type="button"
                :disabled="clickThroughBusy"
                @click="clickThroughEnabled ? setClickThrough(false) : enableTemporaryClickThrough()"
              >
                <ShieldCheck :size="19" />
                <strong>短时穿透</strong>
                <span>{{ clickThroughEnabled ? "短时开启，会自动恢复；也可立即恢复" : "关闭，可拖动和右键互动" }}</span>
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
                <StatusPill :label="roamPolicyLabel" tone="info" />
                <strong>活动范围会真实影响移动</strong>
                <span>{{ roamPolicyCaption }}</span>
              </div>
              <div>
                <StatusPill label="尺寸同步" tone="sage" />
                <strong>大小比例会真实生效</strong>
                <span>保存或拖动滑杆后，透明桌宠窗口和精灵图会按当前比例同步调整。</span>
              </div>
              <div>
                <StatusPill :label="clickThroughEnabled ? '短时穿透' : '可交互'" :tone="clickThroughEnabled ? 'info' : 'sage'" />
                <strong>短时穿透防锁死</strong>
                <span>{{
                  clickThroughEnabled ? "桌宠暂时不挡下面的软件，约半分钟后自动恢复交互。" : "桌宠可拖动、右键打开快捷菜单，也能响应摸摸和说句话。"
                }}</span>
              </div>
              <div>
                <StatusPill label="本机设置" tone="sage" />
                <strong>拖动、巡游和说话间隔会写回</strong>
                <span>灵敏度、惯性、巡游速度、活动范围和自动说话间隔都会保存在本机设置里。</span>
              </div>
            </div>
            <div class="slider-stack">
              <label>
                <span
                  >大小比例 <strong>{{ scaleValue.toFixed(2) }}</strong></span
                >
                <input v-model.number="scaleValue" type="range" min="0.2" max="1.2" step="0.01" />
              </label>
              <label>
                <span
                  >动画速度 <strong>{{ animationSpeedValue.toFixed(2) }}</strong></span
                >
                <input v-model.number="animationSpeedValue" type="range" min="0.1" max="2" step="0.05" />
              </label>
              <label>
                <span
                  >拖动灵敏度 <strong>{{ dragSensitivityValue.toFixed(2) }}</strong></span
                >
                <input v-model.number="dragSensitivityValue" type="range" min="0.1" max="2" step="0.05" />
              </label>
              <label>
                <span
                  >拖动惯性 <strong>{{ inertiaValue.toFixed(2) }}</strong></span
                >
                <input v-model.number="inertiaValue" type="range" min="0" max="1" step="0.05" />
              </label>
              <label>
                <span
                  >巡游速度 <strong>{{ roamSpeedValue.toFixed(0) }} px/s</strong></span
                >
                <input v-model.number="roamSpeedValue" type="range" min="20" max="240" step="5" />
              </label>
              <label>
                <span
                  >巡游距离 <strong>{{ Math.round(roamDistanceValue * 100) }}%</strong></span
                >
                <input v-model.number="roamDistanceValue" type="range" min="0.05" max="1" step="0.05" />
              </label>
              <label>
                <span
                  >自动说话间隔 <strong>{{ talkIntervalValue.toFixed(0) }} 秒</strong></span
                >
                <input v-model.number="talkIntervalValue" type="range" min="30" max="600" step="10" />
              </label>
              <label>
                <span
                  >互动后延迟 <strong>{{ talkAfterInteractionDelayValue.toFixed(0) }} 秒</strong></span
                >
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
              <button
                class="switch-card"
                :class="{ selected: secondaryMonitorFullRoam }"
                type="button"
                @click="secondaryMonitorFullRoam = !secondaryMonitorFullRoam"
              >
                <PanelRightOpen :size="19" />
                <strong>副屏自由活动</strong>
                <span>{{ secondaryMonitorFullRoam ? "副屏可使用更大活动范围" : "副屏也按安静范围处理" }}</span>
              </button>
              <button class="switch-card" :class="{ selected: keepOnScreen }" type="button" @click="keepOnScreen = !keepOnScreen">
                <ShieldCheck :size="19" />
                <strong>保持在屏幕内</strong>
                <span>{{ keepOnScreen ? "开启，自动巡游不跑出工作区" : "关闭，仅保存偏好，仍建议谨慎" }}</span>
              </button>
              <button class="switch-card" :class="{ selected: roamCurrentMonitorOnly }" type="button" @click="roamCurrentMonitorOnly = !roamCurrentMonitorOnly">
                <CircleDot :size="19" />
                <strong>只在当前屏</strong>
                <span>{{ roamCurrentMonitorOnly ? "拖到哪块屏，自动巡游就留在哪块屏" : "允许按多屏策略选择活动范围" }}</span>
              </button>
              <button class="switch-card" :class="{ selected: lockSizeAcrossMonitors }" type="button" @click="lockSizeAcrossMonitors = !lockSizeAcrossMonitors">
                <LayoutGrid :size="19" />
                <strong>跨屏尺寸锁定</strong>
                <span>{{ lockSizeAcrossMonitors ? "保持同一物理尺寸，降低 DPI 跳变" : "只保存偏好，后续按平台差异处理" }}</span>
              </button>
            </div>
            <div class="setting-list">
              <div>
                <span>大小比例</span><strong>{{ scaleValue.toFixed(2) }}</strong>
              </div>
              <div>
                <span>桌宠窗口</span><strong>{{ petWindowSizeLabel }}</strong>
              </div>
              <div>
                <span>动画速度</span><strong>{{ animationSpeedValue.toFixed(2) }}</strong>
              </div>
              <div>
                <span>拖动灵敏度</span><strong>{{ dragSensitivityValue.toFixed(2) }}</strong>
              </div>
              <div>
                <span>拖动惯性</span><strong>{{ inertiaValue.toFixed(2) }}</strong>
              </div>
              <div>
                <span>巡游速度</span><strong>{{ roamSpeedValue.toFixed(0) }} px/s</strong>
              </div>
              <div>
                <span>巡游距离</span><strong>{{ Math.round(roamDistanceValue * 100) }}%</strong>
              </div>
              <div>
                <span>自动说话间隔</span><strong>{{ talkIntervalValue.toFixed(0) }} 秒</strong>
              </div>
              <div>
                <span>自动说话</span><strong>{{ talkEnabled ? "开启" : "关闭" }}</strong>
              </div>
              <div>
                <span>自由巡游</span><strong>{{ roamEnabled ? "开启" : "关闭" }}</strong>
              </div>
              <div>
                <span>鼠标穿透</span><strong>{{ clickThroughEnabled ? "开启" : "关闭" }}</strong>
              </div>
              <div>
                <span>屏幕中活动</span><strong>{{ roamAllowCenter ? "允许" : "关闭" }}</strong>
              </div>
              <div>
                <span>多屏策略</span><strong>{{ multiMonitorRoam ? "开启" : "关闭" }}</strong>
              </div>
              <div>
                <span>当前屏限制</span><strong>{{ roamCurrentMonitorOnly ? "开启" : "关闭" }}</strong>
              </div>
              <div>
                <span>副屏自由</span><strong>{{ secondaryMonitorFullRoam ? "开启" : "关闭" }}</strong>
              </div>
              <div>
                <span>跨屏尺寸锁定</span><strong>{{ lockSizeAcrossMonitors ? "开启" : "关闭" }}</strong>
              </div>
              <div>
                <span>置顶</span><strong>{{ petPinned ? "开启" : "关闭" }}</strong>
              </div>
            </div>
            <div class="button-row panel-actions">
              <button class="button primary" type="button" :disabled="settingsSaving" @click="saveBehaviorSettings">
                <Save :size="16" />
                {{ settingsSaving ? "保存中" : "保存行为设置" }}
              </button>
              <button class="button ghost" type="button" @click="sendPetCommand('recall-near-cursor', { source: 'behavior-panel', toast: '已把桌宠召回到鼠标附近' })">召回桌宠</button>
              <button class="button ghost" type="button" @click="sendPetCommand('settle-near-edge', { source: 'behavior-panel', toast: '已让桌宠靠边休息' })">让桌宠靠边休息</button>
              <button class="button ghost" type="button" @click="sendPetCommand('follow-cursor', { source: 'behavior-panel', toast: '已让桌宠跟随光标 12 秒' })">让桌宠跟随光标</button>
              <button class="button ghost" type="button" :disabled="chatSending" @click="sendPetCommand('quick-chat', { source: 'behavior-panel', toast: '已让桌宠聊一句' })">
                {{ chatSending ? "思考中" : "让桌宠聊一句" }}
              </button>
              <button class="button ghost" type="button" @click="sendPetCommand('pet-touch', { source: 'behavior-panel', toast: '已让桌宠做摸摸反馈' })">摸摸桌宠</button>
              <button class="button ghost" type="button" @click="previewAutoTalk">预览自动说话</button>
              <button class="button ghost" type="button" :disabled="clickThroughBusy" @click="clickThroughEnabled ? setClickThrough(false) : enableTemporaryClickThrough()">
                {{ clickThroughEnabled ? "立即恢复桌宠交互" : "短时穿透 30 秒" }}
              </button>
              <button class="button ghost" type="button" @click="setPinned(!petPinned)">
                {{ petPinned ? "取消置顶" : "窗口置顶" }}
              </button>
            </div>
          </article>
        </section>

        <section v-else class="content-grid">
          <article class="panel wide-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">安全</span>
                <h2>隐私、备份和公开包检查</h2>
              </div>
              <ShieldCheck :size="22" />
            </div>
            <div class="security-action-grid">
              <button
                v-for="item in securityActionCards"
                :key="item.action"
                class="action-card"
                type="button"
                :disabled="Boolean(securityActionBusy)"
                @click="runSecurityAction(item.action)"
              >
                <component :is="item.icon" :size="18" />
                <span class="action-card__body">
                  <strong>{{ item.label }}</strong>
                  <small>{{ item.caption }}</small>
                </span>
                <StatusPill :label="securityActionBusy === item.action ? '执行中' : '可执行'" :tone="securityActionBusy === item.action ? 'info' : item.tone" />
                <ChevronRight class="action-card__arrow" :size="16" />
              </button>
            </div>
            <div v-if="securityActionResult" class="security-result-card" :class="`security-result-card--${securityActionResult.tone}`">
              <div>
                <strong>{{ securityActionResult.title }}</strong>
                <p>{{ securityActionResult.message }}</p>
                <small v-if="securityActionResult.path">{{ securityActionResult.path }}</small>
              </div>
              <ul>
                <li v-for="item in securityActionResult.items" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="privacy-matrix">
              <div>
                <StatusPill label="默认排除" tone="sage" />
                <p>聊天、待办、提醒历史、陪伴状态、日志。</p>
              </div>
              <div>
                <StatusPill label="永不导出" tone="danger-soft" />
                <p>API Key、Token、本机加密材料、本机绝对路径。</p>
              </div>
              <div>
                <StatusPill label="可选导出" tone="info" />
                <p>默认形象、动作素材、公开说明和新用户模板。</p>
              </div>
            </div>
          </article>
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">安装包</span>
                <h2>买家无需额外环境</h2>
              </div>
              <PackageCheck :size="22" />
            </div>
            <div class="export-card">
              <Download :size="22" />
              <div>
                <strong>公开包必须从干净模板生成</strong>
                <p>导出只作用于副本，不修改本机真实数据。开机启动默认关闭，发版前必须跑公开包检查。</p>
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
            <div>
              <StatusPill label="只写本机" tone="sage" />
              <p>Key 只传给本机后端，写入系统加密字段。</p>
            </div>
            <div>
              <StatusPill label="不回显" tone="info" />
              <p>保存后前端只刷新“已保存”状态，不读取真实值。</p>
            </div>
            <div>
              <StatusPill label="不进仓库" tone="danger-soft" />
              <p>本机数据、加密材料和 Key 文件默认被 Git 排除。</p>
            </div>
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

    <div v-if="toast" class="toast" :class="`toast--${toastTone}`" :role="toastRole" aria-live="polite">
      <div>
        <strong>{{ toastTitle }}</strong>
        <span>{{ toast }}</span>
      </div>
      <button class="toast__close" type="button" aria-label="关闭提示" @click="dismissToast">
        <X :size="14" />
      </button>
    </div>
  </main>
</template>
