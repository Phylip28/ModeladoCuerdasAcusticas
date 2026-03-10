<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1 class="panel-title">PREDICCIÓN</h1>
        <p class="panel-sub">
          Simulador — ingresa L y predice la frecuencia en todos los modelos
        </p>
      </div>
    </header>

    <!-- Prediction history selector -->
    <div v-if="store.predictHistory.length > 0" class="pred-history-bar">
      <div class="pred-selector">
        <span class="pred-selector-label">PREDICCIÓN</span>
        <select
          v-model="selectedPredictId"
          class="pred-select"
        >
          <option
            v-for="(p, idx) in [...store.predictHistory].reverse()"
            :key="p.predict_id"
            :value="p.predict_id"
          >
            #{{ p.predict_id }} — {{ p.longitud_cm }} cm — {{ p.timestamp }}{{ idx === 0 ? ' (última)' : '' }}
          </option>
        </select>
      </div>
      <div class="pred-history-actions">
        <button
          class="btn btn-outline btn-sm"
          :disabled="store.loadingReport"
          @click="store.downloadReport()"
          title="Genera un reporte PDF con los modelos actuales"
        >
          <span v-if="store.loadingReport">⏳</span>
          <span v-else>📄</span>
          {{ store.loadingReport ? 'Generando…' : 'Reporte PDF' }}
        </button>
        <button
          class="btn btn-ghost btn-sm"
          :disabled="!selectedPredictId"
          @click="store.deletePrediction(selectedPredictId)"
          title="Eliminar esta predicción del historial"
        >
          ✕ Eliminar
        </button>
      </div>
    </div>

    <div v-if="!store.hasTrainResults" class="warn-banner">
      ← Entrena los modelos primero en la pestaña <strong>Modelos</strong>
    </div>

    <div class="predict-layout">
      <!-- Input card -->
      <div class="input-card card">
        <div class="input-card-title">Longitud de cuerda</div>

        <div class="slider-area">
          <input
            v-model.number="store.predictLength"
            type="range"
            min="20"
            max="70"
            step="0.1"
            class="length-slider"
            :disabled="!store.hasTrainResults"
          />
          <div class="slider-labels">
            <span class="mono">20 cm</span>
            <span class="mono">70 cm</span>
          </div>
        </div>

        <div class="length-display">
          <input
            v-model.number="store.predictLength"
            type="number"
            min="1"
            max="200"
            step="0.1"
            style="text-align: center; font-size: 32px; width: 120px"
            :disabled="!store.hasTrainResults"
          />
          <span class="unit">cm</span>
        </div>

        <div class="physics-note">
          <span class="pn-label">f ∝ 1/L</span>
          <span class="pn-desc">relación física esperada</span>
        </div>

        <button
          class="btn btn-primary"
          style="width: 100%; justify-content: center"
          :disabled="!store.hasTrainResults || store.loadingPredict"
          @click="store.runPredict()"
        >
          <div
            v-if="store.loadingPredict"
            class="spinner"
            style="width: 13px; height: 13px"
          />
          <span v-else>◉</span>
          {{ store.loadingPredict ? "Calculando…" : "Predecir frecuencia" }}
        </button>
      </div>

      <!-- Results -->
      <div class="results-area">
        <Transition name="fade">
          <div
            v-if="!activePrediction && store.hasTrainResults"
            class="results-empty"
          >
            <p class="text-muted">
              Ajusta la longitud y presiona <strong>Predecir</strong>
            </p>
          </div>

          <div v-else-if="activePrediction" class="results-list">
            <div
              v-for="pred in activePrediction.predicciones"
              :key="pred.nombre"
              class="pred-card"
              :class="{
                'pred-best': pred.nombre === activePrediction.mejor_modelo,
              }"
              :style="{ '--mc': modelColor(pred.nombre) }"
            >
              <div class="pred-top">
                <span class="pred-name">{{ pred.etiqueta }}</span>
                <span
                  v-if="pred.nombre === activePrediction.mejor_modelo"
                  class="badge badge-teal"
                  >Mejor R²</span
                >
              </div>
              <div class="pred-freq">
                <span class="pred-hz mono">{{
                  pred.frecuencia_hz.toFixed(2)
                }}</span>
                <span class="pred-unit">Hz</span>
              </div>
              <div class="pred-bar-wrap">
                <div
                  class="pred-bar"
                  :style="{ width: barWidth(pred.frecuencia_hz) + '%' }"
                />
              </div>
              <div v-if="pred.confianza" class="pred-err">
                {{ pred.confianza }}
              </div>
            </div>

            <!-- Note about physics -->
            <div class="physics-card">
              <div class="phys-title">Relación física f(L) = k / L</div>
              <div class="phys-body">
                Para L =
                <strong class="mono text-gold"
                  >{{ activePrediction.longitud_cm }} cm</strong
                >, la física predice f ≈
                <strong class="mono text-teal"
                  >{{ physicsEstimate.toFixed(1) }} Hz</strong
                >
                (estimación con k calibrada del dataset)
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useLabStore } from "@/stores/labStore";

const store = useLabStore();

const MODEL_COLORS = {
  polinomial: "#F5C842",
  svr: "#00D4AA",
  mlp: "#A78BFA",
  knn: "#FF6B6B",
  arbol: "#4ADE80",
  bosque: "#FB923C",
};

function modelColor(nombre) {
  return MODEL_COLORS[nombre] ?? "#8899CC";
}

// ── Prediction history selector ───────────────────────────────────────────
const selectedPredictId = ref(null);

watch(
  () => store.predictHistory.at(-1)?.predict_id,
  (newId) => {
    if (newId) selectedPredictId.value = newId;
  }
);

const activePrediction = computed(() =>
  store.predictHistory.find((p) => p.predict_id === selectedPredictId.value) ??
  store.predictResult
);

// f ∝ 1/L → f = k/L, calibrar k con el promedio del dataset
const physicsEstimate = computed(() => {
  const ap = activePrediction.value;
  if (!ap) return 0;
  const Xs = ap.longitudes_originales;
  const ys = ap.frecuencias_originales;
  if (!Xs?.length) return 0;
  const k = Xs.reduce((sum, x, i) => sum + x * ys[i], 0) / Xs.length;
  return k / ap.longitud_cm;
});

const maxFreq = computed(() => {
  if (!activePrediction.value) return 500;
  return (
    Math.max(...activePrediction.value.predicciones.map((p) => p.frecuencia_hz)) *
    1.1
  );
});

function barWidth(hz) {
  return Math.min(100, (hz / maxFreq.value) * 100);
}

function formatPredLabel(p, idx, arr) {
  const rev = [...arr].reverse();
  const i = rev.indexOf(p);
  return `#${p.predict_id} — ${p.longitud_cm} cm — ${p.timestamp}${i === 0 ? " (última)" : ""}`;
}
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

.warn-banner {
  background: rgba(245, 200, 66, 0.07);
  border: 1px solid rgba(245, 200, 66, 0.2);
  color: var(--gold-dim);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 13px;
  flex-shrink: 0;
}

.predict-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 16px;
  flex: 1;
}

/* Input card */
.input-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-self: start;
}

.input-card-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

.slider-area {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.length-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 99px;
  background: linear-gradient(
    90deg,
    var(--gold) var(--pct, 50%),
    var(--border) var(--pct, 50%)
  );
  outline: none;
  cursor: pointer;
}

.length-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--gold);
  box-shadow: 0 0 8px rgba(245, 200, 66, 0.5);
  cursor: pointer;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-muted);
}

.length-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  padding: 8px 0;
}

.unit {
  font-family: var(--font-mono);
  font-size: 18px;
  color: var(--text-muted);
}

.physics-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(245, 200, 66, 0.06);
  border: 1px solid rgba(245, 200, 66, 0.15);
  border-radius: var(--radius-sm);
}

.pn-label {
  font-family: var(--font-mono);
  color: var(--gold);
  font-size: 13px;
}

.pn-desc {
  font-size: 11px;
  color: var(--text-muted);
}

/* Results */
.results-area {
  display: flex;
  flex-direction: column;
}

.results-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  font-size: 14px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pred-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--mc, var(--border));
  border-radius: var(--radius-md);
  padding: 14px 16px;
  transition: all var(--transition);
}

.pred-best {
  border-color: var(--mc, var(--teal));
  background: var(--bg-card-hover);
  box-shadow: 0 0 20px rgba(0, 212, 170, 0.05);
}

.pred-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.pred-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--mc, var(--text-secondary));
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.pred-freq {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 8px;
}

.pred-hz {
  font-size: 36px;
  color: var(--text-primary);
  line-height: 1;
}

.pred-unit {
  font-size: 14px;
  color: var(--text-muted);
}

.pred-bar-wrap {
  height: 3px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
}

.pred-bar {
  height: 100%;
  background: var(--mc, var(--gold));
  border-radius: 99px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 6px var(--mc, var(--gold));
}

.pred-err {
  font-size: 11px;
  color: var(--coral);
  margin-top: 6px;
}

.physics-card {
  background: rgba(245, 200, 66, 0.05);
  border: 1px solid rgba(245, 200, 66, 0.15);
  border-radius: var(--radius-md);
  padding: 14px 16px;
}

.phys-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--gold-dim);
  margin-bottom: 6px;
}

.phys-body {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* ── Prediction history bar ─────────────────────────────────────────── */
.pred-history-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  flex-shrink: 0;
}

.pred-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 6px 10px;
}

.pred-selector-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  white-space: nowrap;
}

.pred-select {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  outline: none;
  cursor: pointer;
  max-width: 320px;
}

.pred-select option {
  background: var(--bg-panel);
  color: var(--text-primary);
}

.pred-history-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-sm {
  padding: 5px 11px;
  font-size: 12px;
  gap: 5px;
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--teal);
  color: var(--teal);
}

.btn-outline:hover:not(:disabled) {
  background: rgba(0, 212, 170, 0.08);
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
}

.btn-ghost:hover:not(:disabled) {
  border-color: var(--coral);
  color: var(--coral);
}
</style>
