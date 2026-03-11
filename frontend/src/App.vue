<template>
  <div class="lab-shell">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-glyph">〜</span>
        <div>
          <div class="logo-title">LabAcústico</div>
          <div class="logo-sub">Modelado de Cuerdas</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="nav-item"
          :class="{ active: currentTab === tab.id }"
          @click="currentTab = tab.id"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span class="nav-label">{{ tab.label }}</span>
          <span
            v-if="tab.id === 'analisis' && store.hasTrainResults"
            class="nav-dot"
          />
        </button>
      </nav>

      <div class="sidebar-status">
        <div class="status-row">
          <span class="status-dot" :class="store.dataset ? 'ok' : 'idle'" />
          <span>{{
            store.dataset ? `${store.dataset.total} puntos` : "Sin datos"
          }}</span>
        </div>
        <div v-if="store.selectedColumn" class="status-col">
          {{ store.selectedColumn }}
        </div>
      </div>
    </aside>

    <!-- Main area -->
    <main class="main-content">
      <component :is="activePanel" :key="currentTab" />
    </main>
  </div>

  <!-- Loading overlay (initial + manual reload) -->
  <Transition name="loading-fade">
    <LoadingScreen v-if="store.showLoadingOverlay" />
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useLabStore } from "@/stores/labStore";
import DataPanel from "@/components/DataPanel.vue";
import ModelConfig from "@/components/ModelConfig.vue";
import ChartPanel from "@/components/ChartPanel.vue";
import PredictPanel from "@/components/PredictPanel.vue";
import ReportPanel from "@/components/ReportPanel.vue";
import LoadingScreen from "@/components/LoadingScreen.vue";

const store = useLabStore();
const currentTab = ref("datos");

const panelMap = {
  datos: DataPanel,
  modelos: ModelConfig,
  analisis: ChartPanel,
  prediccion: PredictPanel,
  reporte: ReportPanel,
};
const activePanel = computed(() => panelMap[currentTab.value]);

const tabs = [
  { id: "datos", icon: "⊞", label: "Datos" },
  { id: "modelos", icon: "⊛", label: "Modelos" },
  { id: "analisis", icon: "◈", label: "Análisis" },
  { id: "prediccion", icon: "◉", label: "Predicción" },
  { id: "reporte", icon: "⊡", label: "Reporte" },
];

onMounted(() => store.reload());
</script>

<style scoped>
.lab-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 210px;
  flex-shrink: 0;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 0;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 22px 20px 18px;
  border-bottom: 1px solid var(--border);
}

.logo-glyph {
  font-size: 26px;
  color: var(--gold);
  line-height: 1;
  filter: drop-shadow(0 0 8px rgba(245, 200, 66, 0.6));
}

.logo-title {
  font-family: var(--font-display);
  font-size: 18px;
  letter-spacing: 0.08em;
  color: var(--text-primary);
  line-height: 1;
}

.logo-sub {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 2px;
}

.sidebar-nav {
  flex: 1;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  background: none;
  border: none;
  border-radius: var(--radius-md);
  padding: 9px 12px;
  cursor: pointer;
  color: var(--text-secondary);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  transition: all var(--transition);
  position: relative;
  text-align: left;
}

.nav-item:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(245, 200, 66, 0.1);
  color: var(--gold);
  border: 1px solid rgba(245, 200, 66, 0.2);
}

.nav-icon {
  font-size: 14px;
  flex-shrink: 0;
  width: 18px;
  text-align: center;
}

.nav-dot {
  width: 6px;
  height: 6px;
  background: var(--teal);
  border-radius: 50%;
  margin-left: auto;
  box-shadow: 0 0 6px var(--teal);
}

.sidebar-status {
  padding: 14px 16px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--text-muted);
}

.status-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.ok {
  background: var(--teal);
  box-shadow: 0 0 5px var(--teal);
}
.status-dot.idle {
  background: var(--text-muted);
}

.status-col {
  margin-top: 4px;
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: var(--gold-dim);
  word-break: break-all;
}

/* ── Main ── */
.main-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Panel enter animation (replaces Vue Transition) */
.main-content > * {
  animation: panel-in 0.18s ease both;
}
@keyframes panel-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

/* ── Loading screen transition ── */
.loading-fade-enter-active,
.loading-fade-leave-active {
  transition: opacity 0.4s ease;
}
.loading-fade-enter-from,
.loading-fade-leave-to {
  opacity: 0;
}
</style>
