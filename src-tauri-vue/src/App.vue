<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { getCurrentWindow } from "@tauri-apps/api/window";
import {
  Bell,
  ChevronRight,
  CircleDot,
  Clock3,
  Heart,
  Home,
  Image,
  KeyRound,
  LayoutGrid,
  MessageCircle,
  Palette,
  PanelRightOpen,
  Play,
  RefreshCw,
  Settings2,
  ShieldCheck,
  Sparkles,
  X,
} from "@lucide/vue";
import { runtimeApi } from "./api/runtime";
import { MetricCard, StatusPill } from "./components";
import type { PetSummary, RuntimeSummary } from "./types/runtime";

const params = new URLSearchParams(window.location.search);
const viewMode = params.get("window") === "pet" ? "pet" : "panel";

const runtime = ref<RuntimeSummary | null>(null);
const currentAsset = ref("");
const assetError = ref("");
const loading = ref(true);
const activePage = ref("overview");
const toast = ref("");
const petPinned = ref(true);

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
      { id: "motion", label: "动作", icon: LayoutGrid },
    ],
  },
  {
    label: "设置与安全",
    items: [
      { id: "appearance", label: "外观", icon: Palette },
      { id: "security", label: "安全", icon: ShieldCheck },
      { id: "route", label: "路线", icon: Sparkles },
    ],
  },
];

const currentPet = computed(() => runtime.value?.current_pet ?? null);
const readyPets = computed(() => runtime.value?.pets.filter((pet) => pet.status === "ready") ?? []);
const pageTitle = computed(() => navGroups.flatMap((group) => group.items).find((item) => item.id === activePage.value)?.label ?? "首页");

function showToast(message: string) {
  toast.value = message;
  window.setTimeout(() => {
    if (toast.value === message) toast.value = "";
  }, 2600);
}

async function loadAsset(path: string) {
  currentAsset.value = "";
  assetError.value = "";
  if (!path) {
    assetError.value = "当前宠物没有可预览 identity 图";
    return;
  }
  try {
    const asset = await runtimeApi.getRuntimeAsset(path);
    currentAsset.value = asset.data_url;
  } catch (error) {
    assetError.value = error instanceof Error ? error.message : String(error);
  }
}

async function refreshRuntime() {
  loading.value = true;
  try {
    const summary = await runtimeApi.getRuntimeSummary();
    runtime.value = summary;
    petPinned.value = summary.settings.always_on_top ?? true;
    await loadAsset(summary.current_pet?.identity_asset ?? summary.current_pet?.spritesheet_asset ?? "");
  } finally {
    loading.value = false;
  }
}

async function showPetWindow() {
  await runtimeApi.showPet();
  showToast("桌宠窗口已显示");
}

async function hidePetWindow() {
  await runtimeApi.hidePet();
  showToast("桌宠窗口已隐藏");
}

async function setPinned(enabled: boolean) {
  petPinned.value = enabled;
  await runtimeApi.setPetAlwaysOnTop(enabled);
  showToast(enabled ? "桌宠窗口已置顶" : "桌宠窗口已取消置顶");
}

async function startPetDrag(event: MouseEvent) {
  if (event.button !== 0) return;
  try {
    await getCurrentWindow().startDragging();
  } catch {
    // Browser preview and unsupported environments can ignore this.
  }
}

function petStatusLabel(pet: PetSummary) {
  return `${pet.supported_action_count} 动作 / ${pet.extension_action_count} 扩展`;
}

onMounted(refreshRuntime);
</script>

<template>
  <div v-if="viewMode === 'pet'" class="pet-window" @mousedown="startPetDrag">
    <div class="pet-bubble" aria-live="polite">
      我在这里，主人。
    </div>
    <div class="pet-stage" :class="{ 'pet-stage--fallback': !currentAsset }">
      <img v-if="currentAsset" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" />
      <div v-else class="pet-fallback">
        <Heart :size="56" />
      </div>
    </div>
    <button class="pet-close" type="button" title="隐藏桌宠" @click.stop="hidePetWindow">
      <X :size="16" />
    </button>
  </div>

  <main v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark"><Heart :size="22" /></div>
        <div>
          <strong>蛋黄桌宠</strong>
          <span>Tauri + Vue 产品版</span>
        </div>
      </div>

      <nav class="nav">
        <section v-for="group in navGroups" :key="group.label" class="nav-group">
          <p>{{ group.label }}</p>
          <button
            v-for="item in group.items"
            :key="item.id"
            type="button"
            :class="{ active: activePage === item.id }"
            @click="activePage = item.id"
          >
            <component :is="item.icon" :size="17" />
            <span>{{ item.label }}</span>
          </button>
        </section>
      </nav>

      <div class="sidebar-status">
        <StatusPill :label="runtime?.runtime_available ? 'E 盘镜像' : '预览数据'" tone="sage" />
        <span>{{ runtime?.runtime_source ?? "加载中" }}</span>
      </div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <h1>{{ pageTitle }}</h1>
          <p>{{ currentPet?.display_name ?? "当前宠物" }} · {{ runtime?.ready_pet_count ?? 0 }} 个 ready 形象 · {{ runtime?.total_supported_actions ?? 0 }} 个动作</p>
        </div>
        <div class="topbar-actions">
          <button class="icon-button" type="button" title="刷新数据" @click="refreshRuntime">
            <RefreshCw :size="17" />
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

      <div v-if="loading" class="loading-panel">正在读取 E 盘运行镜像...</div>

      <template v-else>
        <section v-if="activePage === 'overview'" class="page-grid page-grid--overview">
          <article class="panel current-pet-panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">当前陪伴</span>
                <h2>{{ currentPet?.display_name ?? "未读取到宠物" }}</h2>
              </div>
              <StatusPill :label="currentPet?.status ?? 'unknown'" tone="sage" />
            </div>
            <div class="pet-preview">
              <img v-if="currentAsset" :src="currentAsset" :alt="currentPet?.display_name ?? '当前宠物'" />
              <div v-else class="pet-preview-fallback">
                <Heart :size="42" />
                <span>{{ assetError || "等待图片" }}</span>
              </div>
            </div>
            <div class="metric-row">
              <MetricCard label="动作" :value="currentPet?.supported_action_count ?? 0" />
              <MetricCard label="扩展" :value="currentPet?.extension_action_count ?? 0" />
              <MetricCard label="比例" :value="runtime?.settings.scale ?? '-'" />
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
            <div class="status-grid">
              <StatusPill label="云端可配置" tone="info" />
              <StatusPill label="本机时间" tone="sage" />
              <StatusPill label="资料查询" tone="info" />
              <StatusPill label="待办摘要" tone="sage" />
              <StatusPill label="本地兜底" tone="sage" />
              <StatusPill label="Key 不回显" tone="danger-soft" />
            </div>
            <div class="privacy-list">
              <p v-for="note in runtime?.checks.notes" :key="note">
                <CircleDot :size="14" />
                {{ note }}
              </p>
            </div>
          </article>

          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">快捷操作</span>
                <h2>桌面行为</h2>
              </div>
              <Settings2 :size="22" />
            </div>
            <div class="action-grid">
              <button class="action-card" type="button" @click="showPetWindow">
                <PanelRightOpen :size="18" />
                <span>显示桌宠</span>
                <ChevronRight :size="16" />
              </button>
              <button class="action-card" type="button" @click="setPinned(!petPinned)">
                <Settings2 :size="18" />
                <span>{{ petPinned ? "取消置顶" : "窗口置顶" }}</span>
                <ChevronRight :size="16" />
              </button>
              <button class="action-card" type="button" @click="activePage = 'chat'">
                <MessageCircle :size="18" />
                <span>打开对话</span>
                <ChevronRight :size="16" />
              </button>
              <button class="action-card" type="button" @click="activePage = 'reminders'">
                <Bell :size="18" />
                <span>查看提醒</span>
                <ChevronRight :size="16" />
              </button>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'identity'" class="page-stack">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">家人形象</span>
                <h2>5 个 ready 宠物从 manifest 读取</h2>
              </div>
              <Image :size="22" />
            </div>
            <div class="pet-list">
              <div v-for="pet in readyPets" :key="pet.id" class="pet-row" :class="{ current: pet.id === runtime?.current_pet_id }">
                <div>
                  <strong>{{ pet.display_name }}</strong>
                  <span>{{ pet.species }} · {{ pet.action_pack_level }}</span>
                </div>
                <StatusPill :label="pet.id === runtime?.current_pet_id ? '当前' : pet.status" :tone="pet.id === runtime?.current_pet_id ? 'info' : 'sage'" />
                <span class="row-meta">{{ petStatusLabel(pet) }}</span>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'actions' || activePage === 'motion'" class="page-stack">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">动作系统</span>
                <h2>v1 复用 spritesheet / atlas</h2>
              </div>
              <Play :size="22" />
            </div>
            <div class="split-grid">
              <MetricCard label="可播放动作" :value="runtime?.total_supported_actions ?? 0" />
              <MetricCard label="扩展动作条" :value="runtime?.total_extension_assets ?? 0" />
              <MetricCard label="右键动作" :value="runtime?.settings.quick_menu_action_count ?? 0" />
            </div>
            <div class="roadmap-strip">
              <StatusPill label="Sprite atlas" tone="sage" />
              <StatusPill label="气泡 renderer" tone="sage" />
              <StatusPill label="右键 model" tone="sage" />
              <StatusPill label="Live2D 预留" tone="info" />
              <StatusPill label="Lottie 预留" tone="info" />
              <StatusPill label="WebGL 预留" tone="info" />
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'chat'" class="page-stack">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">对话</span>
                <h2>能力状态条和固定输入区原型</h2>
              </div>
              <MessageCircle :size="22" />
            </div>
            <div class="chat-shell">
              <div class="chat-capabilities">
                <StatusPill label="云端" tone="info" />
                <StatusPill label="时间" tone="sage" />
                <StatusPill label="资料" tone="info" />
                <StatusPill label="待办" tone="sage" />
                <StatusPill label="本地兜底" tone="sage" />
              </div>
              <div class="message-list">
                <p class="message owner">今天还有什么要做？</p>
                <p class="message pet">我先陪你看一下本地待办，再短短说给主人听。</p>
              </div>
              <div class="composer">
                <input aria-label="聊天输入" placeholder="和它说一句..." />
                <button class="button primary" type="button">发送</button>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'reminders'" class="page-stack">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">提醒</span>
                <h2>快速新增 + 卡片列表 + 到点弹窗</h2>
              </div>
              <Clock3 :size="22" />
            </div>
            <div class="reminder-layout">
              <div class="quick-add">
                <input aria-label="提醒标题" placeholder="提醒标题" />
                <input aria-label="提醒时间" placeholder="今天 18:30" />
                <button class="button primary" type="button">添加</button>
              </div>
              <div class="todo-card">
                <StatusPill label="今日" tone="info" />
                <strong>把前端化 Spike 验收掉</strong>
                <span>重要 · 可稍后 · 有时间轴</span>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'appearance'" class="page-stack">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">外观</span>
                <h2>透明宠物窗和暖色气泡</h2>
              </div>
              <Palette :size="22" />
            </div>
            <div class="split-grid">
              <MetricCard label="透明度" :value="'100%'" />
              <MetricCard label="气泡" :value="runtime?.settings.bubble_style ?? '-'" />
              <MetricCard label="自动说话" :value="runtime?.settings.talk_enabled ? '开' : '关'" />
            </div>
          </article>
        </section>

        <section v-else-if="activePage === 'security'" class="page-stack">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">安全</span>
                <h2>Rust 命令边界</h2>
              </div>
              <KeyRound :size="22" />
            </div>
            <div class="security-grid">
              <div>
                <strong>默认不返回</strong>
                <p>API Key、Token、DPAPI、聊天、待办、提醒历史、日志、本机导出路径。</p>
              </div>
              <div>
                <strong>只读允许</strong>
                <p>宠物 manifest、settings 摘要、identity 图、spritesheet、extension 动作条。</p>
              </div>
            </div>
          </article>
        </section>

        <section v-else class="page-stack">
          <article class="panel">
            <div class="panel-header">
              <div>
                <span class="eyebrow">技术路线</span>
                <h2>Tauri 2 + Vue3 + TypeScript</h2>
              </div>
              <Sparkles :size="22" />
            </div>
            <div class="route-list">
              <div><strong>v1</strong><span>spritesheet / atlas、气泡、右键 model、双窗口和托盘。</span></div>
              <div><strong>v2</strong><span>Live2D、Lottie、WebGL、粒子和动作包平台。</span></div>
              <div><strong>Rust</strong><span>窗口、托盘、受控文件读取、加密和安装包。</span></div>
              <div><strong>Vue</strong><span>控制面板、聊天、提醒、形象、动作和安全页。</span></div>
            </div>
          </article>
        </section>
      </template>
    </section>

    <div v-if="toast" class="toast">{{ toast }}</div>
  </main>
</template>
