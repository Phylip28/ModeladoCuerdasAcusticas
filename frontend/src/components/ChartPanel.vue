<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1 class="panel-title">ANÁLISIS</h1>
        <p class="panel-sub">
          Comparativa visual de modelos — ajuste y residuos
        </p>
      </div>
      <div class="header-actions" v-if="store.hasTrainResults">
        <div class="session-selector">
          <label class="session-label">Sesión</label>
          <select v-model="selectedSessionId" class="session-select">
            <option
              v-for="(s, i) in [...store.trainHistory].reverse()"
              :key="s.session_id"
              :value="s.session_id"
            >
              #{{ s.session_id }} — {{ s.columna_frecuencia }} — {{ s.timestamp }}
              {{ i === 0 ? '(última)' : '' }}
            </option>
          </select>
        </div>
        <div class="best-model-chip">
          <span class="bm-label">Mejor R²</span>
          <span class="bm-val">{{ activeBestModel?.etiqueta }}</span>
          <span class="bm-r2 mono">{{ activeBestModel?.metricas.r2?.toFixed(5) }}</span>
        </div>
      </div>
    </header>

    <div v-if="!store.hasTrainResults" class="empty-state">
      <div class="empty-icon">◈</div>
      <p>Entrena los modelos primero</p>
      <p class="text-muted">
        Ve a <strong>Modelos</strong> y presiona Entrenar
      </p>
    </div>

    <template v-else>
      <!-- Metrics row -->
      <div class="metrics-row">
        <div
          v-for="res in activeSession.resultados"
          :key="res.nombre"
          class="metric-card"
          :style="{ '--accent': modelColor(res.nombre) }"
        >
          <div class="mc-top">
            <span class="mc-name">{{ res.etiqueta }}</span>
            <span v-if="res.ecuacion" class="mc-eq mono">{{
              res.ecuacion
            }}</span>
          </div>
          <div class="mc-metrics">
            <div class="mc-m">
              <span class="mc-v mono">{{
                res.metricas.r2?.toFixed(4) ?? "—"
              }}</span>
              <span class="mc-k">R²</span>
            </div>
            <div class="mc-m">
              <span class="mc-v mono">{{ res.metricas.rmse.toFixed(2) }}</span>
              <span class="mc-k">RMSE</span>
            </div>
            <div class="mc-m">
              <span class="mc-v mono">{{ res.metricas.mse.toFixed(2) }}</span>
              <span class="mc-k">MSE</span>
            </div>
            <div class="mc-m">
              <span class="mc-v mono">{{ res.metricas.mae.toFixed(2) }}</span>
              <span class="mc-k">MAE</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts 2-col -->
      <div class="charts-grid">
        <!-- Raw data scatter (no models) -->
        <div class="chart-card chart-full">
          <div class="chart-title">
            Dispersión — Datos Reales
            <span class="chart-sub">sin modelos &mdash; {{ activeSession.longitudes_originales?.length ?? 0 }} puntos</span>
          </div>
          <div class="chart-wrap chart-wrap-sm">
            <Scatter :data="rawScatterData" :options="rawScatterOptions" />
          </div>
        </div>

        <!-- Scatter + fit curves -->
        <div class="chart-card">
          <div class="chart-title">Dispersión + Curvas de Ajuste</div>
          <div class="chart-wrap">
            <Scatter :data="scatterData" :options="scatterOptions" />
          </div>
        </div>

        <!-- Residuals -->
        <div class="chart-card">
          <div class="chart-title">Residuos por Modelo</div>
          <div class="chart-wrap">
            <Bar :data="residualData" :options="residualOptions" />
          </div>
        </div>

        <!-- Loss curve (MLP only) -->
        <div v-if="hasMlpLoss" class="chart-card chart-full">
          <div class="chart-title">Curva de Pérdida (MLP)</div>
          <div class="chart-wrap chart-wrap-sm">
            <Line :data="lossData" :options="lossOptions" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Scatter, Bar, Line } from "vue-chartjs";
import { useLabStore } from "@/stores/labStore";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
);

const store = useLabStore();

// ── Session selector ──
const selectedSessionId = ref(store.trainResult?.session_id ?? null);

// Keep selector pointing to latest when a new training completes
watch(
  () => store.trainHistory.length,
  () => {
    selectedSessionId.value = store.trainResult?.session_id ?? null;
  },
);

// Also initialise if store already has sessions when panel mounts
if (!selectedSessionId.value && store.trainResult) {
  selectedSessionId.value = store.trainResult.session_id;
}

const activeSession = computed(
  () =>
    store.trainHistory.find((s) => s.session_id === selectedSessionId.value) ??
    store.trainResult,
);

const activeBestModel = computed(() => {
  if (!activeSession.value) return null;
  return activeSession.value.resultados.reduce((best, cur) =>
    cur.metricas.mse < best.metricas.mse ? cur : best,
    activeSession.value.resultados[0],
  );
});

const MODEL_COLORS = {
  polinomial: "#F5C842",
  svr: "#00D4AA",
  mlp: "#A78BFA",
};

const MODEL_COLORS_DIM = {
  polinomial: "rgba(245,200,66,0.2)",
  svr: "rgba(0,212,170,0.2)",
  mlp: "rgba(167,139,250,0.2)",
};

function modelColor(nombre) {
  return MODEL_COLORS[nombre] ?? "#8899CC";
}

const baseChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 600 },
  plugins: {
    legend: {
      labels: {
        color: "#8899CC",
        font: { family: "Space Mono", size: 11 },
        boxWidth: 12,
      },
    },
    tooltip: {
      backgroundColor: "#111A35",
      borderColor: "rgba(100,126,200,0.3)",
      borderWidth: 1,
      titleColor: "#E8EDF8",
      bodyColor: "#8899CC",
      titleFont: { family: "Space Mono", size: 11 },
    },
  },
  scales: {
    x: {
      grid: { color: "rgba(100,126,200,0.08)" },
      ticks: { color: "#4A5578", font: { family: "Space Mono", size: 10 } },
    },
    y: {
      grid: { color: "rgba(100,126,200,0.08)" },
      ticks: { color: "#4A5578", font: { family: "Space Mono", size: 10 } },
    },
  },
};

// ── Raw data scatter (points only, no model curves) ──
 const rawScatterData = computed(() => {
  if (!activeSession.value) return { datasets: [] };
  const { longitudes_originales: Xs, frecuencias_originales: ys } = activeSession.value;
  return {
    datasets: [
      {
        label: "Datos reales",
        data: Xs.map((x, i) => ({ x, y: ys[i] })),
        backgroundColor: "rgba(245,200,66,0.75)",
        borderColor: "rgba(245,200,66,0.4)",
        borderWidth: 1,
        pointRadius: 5,
        pointHoverRadius: 8,
      },
    ],
  };
});

const rawScatterOptions = computed(() => ({
  ...baseChartOptions,
  plugins: {
    ...baseChartOptions.plugins,
    legend: { display: false },
    tooltip: {
      ...baseChartOptions.plugins.tooltip,
      callbacks: {
        label: (ctx) => ` L=${ctx.parsed.x.toFixed(1)} cm  f=${ctx.parsed.y.toFixed(1)} Hz`,
      },
    },
  },
  scales: {
    x: {
      ...baseChartOptions.scales.x,
      type: "linear",
      title: {
        display: true,
        text: "Longitud L (cm)",
        color: "#4A5578",
        font: { family: "Space Mono", size: 11 },
      },
    },
    y: {
      ...baseChartOptions.scales.y,
      title: {
        display: true,
        text: "Frecuencia (Hz)",
        color: "#4A5578",
        font: { family: "Space Mono", size: 11 },
      },
    },
  },
}));

// ── Scatter data ──
const scatterData = computed(() => {
  if (!activeSession.value) return { datasets: [] };
  const {
    longitudes_originales: Xs,
    frecuencias_originales: ys,
    resultados,
  } = activeSession.value;

  const scatterPoints = Xs.map((x, i) => ({ x, y: ys[i] }));

  const datasets = [
    {
      type: "scatter",
      label: "Datos reales",
      data: scatterPoints,
      backgroundColor: "rgba(232, 237, 248, 0.7)",
      pointRadius: 5,
      pointHoverRadius: 7,
      order: 10,
    },
    ...resultados.map((res) => ({
      type: "line",
      label: res.etiqueta,
      data: res.curva_ajuste.longitudes.map((x, i) => ({
        x,
        y: res.curva_ajuste.frecuencias_pred[i],
      })),
      borderColor: MODEL_COLORS[res.nombre] ?? "#8899CC",
      backgroundColor: "transparent",
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.3,
      order: 1,
    })),
  ];

  return { datasets };
});

const scatterOptions = computed(() => ({
  ...baseChartOptions,
  plugins: {
    ...baseChartOptions.plugins,
    title: {
      display: false,
    },
  },
  scales: {
    x: {
      ...baseChartOptions.scales.x,
      title: {
        display: true,
        text: "Longitud L (cm)",
        color: "#4A5578",
        font: { family: "Space Mono", size: 11 },
      },
      type: "linear",
    },
    y: {
      ...baseChartOptions.scales.y,
      title: {
        display: true,
        text: "Frecuencia f (Hz)",
        color: "#4A5578",
        font: { family: "Space Mono", size: 11 },
      },
    },
  },
}));

// ── Residual data ──
const residualData = computed(() => {
  if (!activeSession.value) return { labels: [], datasets: [] };
  const { longitudes_originales: Xs, resultados } = activeSession.value;
  const labels = Xs.map((x) => x.toFixed(1));

  const datasets = resultados.map((res) => ({
    label: res.etiqueta,
    data: res.residuos,
    backgroundColor: MODEL_COLORS_DIM[res.nombre] ?? "rgba(136,153,204,0.2)",
    borderColor: MODEL_COLORS[res.nombre] ?? "#8899CC",
    borderWidth: 1,
  }));

  return { labels, datasets };
});

const residualOptions = computed(() => ({
  ...baseChartOptions,
  scales: {
    ...baseChartOptions.scales,
    x: {
      ...baseChartOptions.scales.x,
      title: {
        display: true,
        text: "L (cm)",
        color: "#4A5578",
        font: { family: "Space Mono", size: 10 },
      },
    },
    y: {
      ...baseChartOptions.scales.y,
      title: {
        display: true,
        text: "Residuo (Hz)",
        color: "#4A5578",
        font: { family: "Space Mono", size: 10 },
      },
    },
  },
}));

// ── Loss curve ──
const hasMlpLoss = computed(() => {
  const mlp = activeSession.value?.resultados.find((r) => r.nombre === "mlp");
  return mlp?.loss_curve && mlp.loss_curve.length > 0;
});

const lossData = computed(() => {
  const mlp = activeSession.value?.resultados.find((r) => r.nombre === "mlp");
  if (!mlp?.loss_curve) return { labels: [], datasets: [] };
  const labels = mlp.loss_curve.map((_, i) => i + 1);
  return {
    labels,
    datasets: [
      {
        label: "Pérdida (MSE)",
        data: mlp.loss_curve,
        borderColor: "#A78BFA",
        backgroundColor: "rgba(167,139,250,0.08)",
        borderWidth: 1.5,
        pointRadius: 0,
        fill: true,
        tension: 0.3,
      },
    ],
  };
});

const lossOptions = computed(() => ({
  ...baseChartOptions,
  scales: {
    ...baseChartOptions.scales,
    x: {
      ...baseChartOptions.scales.x,
      title: {
        display: true,
        text: "Iteración",
        color: "#4A5578",
        font: { family: "Space Mono", size: 10 },
      },
    },
    y: {
      ...baseChartOptions.scales.y,
      title: {
        display: true,
        text: "Pérdida",
        color: "#4A5578",
        font: { family: "Space Mono", size: 10 },
      },
    },
  },
}));
</script>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  padding: 24px 28px;
  gap: 16px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-shrink: 0;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 28px;
  letter-spacing: 0.12em;
  color: var(--text-primary);
  line-height: 1;
}

.panel-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 3px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.session-selector {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 5px 10px;
}

.session-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  white-space: nowrap;
}

.session-select {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  outline: none;
  max-width: 280px;
}

.session-select option {
  background: var(--bg-deep);
  color: var(--text-primary);
}

.best-model-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 212, 170, 0.08);
  border: 1px solid rgba(0, 212, 170, 0.2);
  border-radius: 99px;
  padding: 6px 14px;
  font-size: 12px;
}

.bm-label {
  color: var(--text-muted);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.bm-val {
  color: var(--teal);
  font-weight: 500;
}
.bm-r2 {
  color: var(--gold);
  font-size: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex: 1;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 52px;
  opacity: 0.2;
}

/* Metrics row */
.metrics-row {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.metric-card {
  flex: 1;
  min-width: 180px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-top: 2px solid var(--accent, var(--gold));
  border-radius: var(--radius-md);
  padding: 12px 14px;
}

.mc-top {
  margin-bottom: 10px;
}

.mc-name {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--accent, var(--gold));
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.mc-eq {
  display: block;
  font-size: 9.5px;
  color: var(--text-muted);
  margin-top: 3px;
  word-break: break-all;
}

.mc-metrics {
  display: flex;
  gap: 14px;
}

.mc-m {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.mc-v {
  font-size: 16px;
  color: var(--text-primary);
}

.mc-k {
  font-size: 9px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* Charts */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  flex: 1;
  min-height: 0;
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px;
  display: flex;
  flex-direction: column;
  min-height: 280px;
}

.chart-full {
  grid-column: 1 / -1;
}

.chart-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 10px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-sub {
  font-size: 10px;
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
  color: var(--text-muted);
  opacity: 0.6;
}

.chart-wrap {
  flex: 1;
  position: relative;
  min-height: 220px;
}

.chart-wrap-sm {
  min-height: 140px;
}
</style>
