<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1 class="panel-title">MODELOS</h1>
        <p class="panel-sub">Configura y entrena los algoritmos de regresión</p>
      </div>
      <button
        class="btn btn-primary"
        :disabled="!canTrain || store.loadingTrain"
        @click="store.trainModels()"
      >
        <div
          v-if="store.loadingTrain"
          class="spinner"
          style="width: 13px; height: 13px"
        />
        <span v-else>▶</span>
        {{ store.loadingTrain ? "Entrenando…" : "Entrenar" }}
      </button>
    </header>

    <div v-if="!store.dataset" class="warn-banner">
      ← Carga datos primero en la pestaña <strong>Datos</strong>
    </div>

    <div v-if="store.trainError" class="error-banner">
      ⚠ {{ store.trainError }}
    </div>

    <div class="config-grid">
      <!-- Column selection -->
      <section class="card">
        <div class="card-title">Columna de frecuencia</div>
        <div class="field">
          <label>Sensor / app de medición</label>
          <select v-model="store.selectedColumn">
            <option v-for="col in store.columnOptions" :key="col" :value="col">
              {{ col }}
            </option>
          </select>
        </div>
      </section>

      <!-- Model selectors -->
      <section class="card">
        <div class="card-title">Algoritmos a comparar</div>
        <div class="model-list">
          <label
            v-for="m in modelOptions"
            :key="m.id"
            class="model-row"
            :class="{ selected: isSelected(m.id) }"
          >
            <div class="checkbox-row" @click.prevent="toggleModel(m.id)">
              <div
                class="checkbox-box"
                :class="{ checked: isSelected(m.id) }"
              />
              <div class="model-info">
                <span class="model-name">{{ m.name }}</span>
                <span class="model-desc">{{ m.desc }}</span>
              </div>
              <span class="badge" :class="m.badge">{{ m.tag }}</span>
            </div>
          </label>
        </div>
      </section>

      <!-- Polynomial config -->
      <section
        class="card"
        :class="{ 'card-disabled': !isSelected('polinomial') }"
      >
        <div class="card-title">
          Polinomial
          <span class="badge badge-gold">Clásico</span>
        </div>
        <div class="field">
          <label>Grado del polinomio</label>
          <div class="degree-row">
            <button
              v-for="g in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
              :key="g"
              class="deg-btn"
              :class="{ active: store.polyGrado === g }"
              :disabled="!isSelected('polinomial')"
              @click="store.polyGrado = g"
            >
              {{ g }}
            </button>
          </div>
        </div>
      </section>

      <!-- MLP config -->
      <section class="card" :class="{ 'card-disabled': !isSelected('mlp') }">
        <div class="card-title">
          Red Neuronal
          <span class="badge badge-violet">Deep Learning</span>
        </div>
        <div class="two-col">
          <div class="field">
            <label>Épocas</label>
            <input
              v-model.number="store.mlpEpocas"
              type="number"
              min="10" max="3000" step="10"
              :disabled="!isSelected('mlp')"
            />
          </div>
          <div class="field">
            <label>Neuronas (capa oculta)</label>
            <input
              v-model.number="store.mlpUnidades"
              type="number"
              min="1" max="200" step="1"
              :disabled="!isSelected('mlp')"
            />
          </div>
        </div>
        <div class="two-col">
          <div class="field">
            <label>Tasa de aprendizaje</label>
            <select
              v-model="store.mlpLearningRate"
              :disabled="!isSelected('mlp')"
            >
              <option value="0.001">0.001 (lenta)</option>
              <option value="0.01">0.01 (normal)</option>
              <option value="0.1">0.1 (rápida)</option>
              <option value="0.5">0.5 (agresiva)</option>
            </select>
          </div>
          <div class="field">
            <label>Activación</label>
            <select
              v-model="store.mlpActivacion"
              :disabled="!isSelected('mlp')"
            >
              <option value="sigmoid">Sigmoid σ(z)</option>
              <option value="relu">ReLU</option>
              <option value="linear">Linear (identidad)</option>
            </select>
          </div>
        </div>
      </section>

      <!-- SVR config -->
      <section class="card" :class="{ 'card-disabled': !isSelected('svr') }">
        <div class="card-title">
          SVR — Support Vector Regression
          <span class="badge badge-violet">ML</span>
        </div>
        <div class="field">
          <label>Kernel</label>
          <select v-model="store.svrKernel" :disabled="!isSelected('svr')">
            <option value="rbf">RBF (no lineal)</option>
            <option value="linear">Linear</option>
            <option value="poly">Polinomial</option>
          </select>
        </div>
        <div class="two-col">
          <div class="field">
            <label>C (regularización)</label>
            <input
              v-model.number="store.svrC"
              type="number"
              min="0.01" max="1000" step="0.1"
              :disabled="!isSelected('svr')"
            />
          </div>
          <div class="field">
            <label>Epsilon (ε)</label>
            <input
              v-model.number="store.svrEpsilon"
              type="number"
              min="0" max="10" step="0.01"
              :disabled="!isSelected('svr')"
            />
          </div>
        </div>
      </section>

      <!-- KNN config -->
      <section class="card" :class="{ 'card-disabled': !isSelected('knn') }">
        <div class="card-title">
          KNN
          <span class="badge badge-violet">ML</span>
        </div>
        <div class="field">
          <label>Número de vecinos (k)</label>
          <div class="knn-row">
            <input
              v-model.number="store.knnK"
              type="range"
              min="1" max="20"
              :disabled="!isSelected('knn')"
              class="knn-slider"
            />
            <span class="mono text-gold knn-val">{{ store.knnK }}</span>
          </div>
          <div class="hint hint-good">k={{ store.knnK }} → promedia los {{ store.knnK }} puntos más cercanos</div>
        </div>
      </section>

      <!-- Árbol Decisión config -->
      <section class="card" :class="{ 'card-disabled': !isSelected('arbol') }">
        <div class="card-title">
          Árbol de Decisión
          <span class="badge badge-violet">ML</span>
        </div>
        <div class="field">
          <label>Profundidad máxima (vaciar = sin límite)</label>
          <input
            v-model.number="store.arbolProfundidad"
            type="number"
            min="1" max="50" placeholder="sin límite"
            :disabled="!isSelected('arbol')"
          />
          <div class="hint hint-good">Profundidad: {{ store.arbolProfundidad ?? 'sin límite' }}</div>
        </div>
      </section>

      <!-- Random Forest config -->
      <section class="card" :class="{ 'card-disabled': !isSelected('bosque') }">
        <div class="card-title">
          Random Forest
          <span class="badge badge-violet">ML</span>
        </div>
        <div class="two-col">
          <div class="field">
            <label>Nº árboles</label>
            <input
              v-model.number="store.bosqueEstimadores"
              type="number"
              min="10" max="500" step="10"
              :disabled="!isSelected('bosque')"
            />
          </div>
          <div class="field">
            <label>Profundidad máx.</label>
            <input
              v-model.number="store.bosqueProfundidad"
              type="number"
              min="1" max="50" placeholder="sin límite"
              :disabled="!isSelected('bosque')"
            />
          </div>
        </div>
      </section>
    </div>

    <!-- Training history -->
    <div v-if="store.hasTrainResults" class="history-section">
      <div class="history-header">
        <span class="history-title">HISTORIAL DE ENTRENAMIENTOS</span>
        <span class="history-count">{{ store.trainHistory.length }} sesión(es)</span>
      </div>
      <div class="history-list">
        <div
          v-for="session in [...store.trainHistory].reverse()"
          :key="session.session_id"
          class="history-item"
        >
          <div class="history-item-header">
            <div class="history-meta">
              <span class="history-id mono">#{{ session.session_id }}</span>
              <span class="history-col">{{ session.columna_frecuencia }}</span>
              <span class="history-time mono">{{ session.timestamp }}</span>
            </div>
            <button class="btn-delete" @click="store.deleteSession(session.session_id)" title="Eliminar sesión">✕</button>
          </div>
          <div class="history-chips">
            <div
              v-for="res in session.resultados"
              :key="res.nombre"
              class="result-chip"
            >
              <span class="chip-label">{{ res.etiqueta }}</span>
              <span class="mono text-gold">R²={{ res.metricas.r2?.toFixed(4) ?? '—' }}</span>
              <span class="mono text-muted">MSE={{ res.metricas.mse?.toFixed(2) ?? '—' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useLabStore } from "@/stores/labStore";

const store = useLabStore();

const modelOptions = [
  {
    id: "polinomial",
    name: "Polinomial",
    desc: "numpy + scikit-learn",
    badge: "badge-gold",
    tag: "Clásico",
  },
  {
    id: "svr",
    name: "SVR",
    desc: "Support Vector Regression (RBF)",
    badge: "badge-violet",
    tag: "ML",
  },
  {
    id: "mlp",
    name: "Red Neuronal",
    desc: "Gradiente descendente con épocas",
    badge: "badge-violet",
    tag: "Deep Learning",
  },
  {
    id: "knn",
    name: "KNN",
    desc: "K-Nearest Neighbors Regressor",
    badge: "badge-violet",
    tag: "ML",
  },
  {
    id: "arbol",
    name: "Árbol Decisión",
    desc: "Decision Tree Regressor",
    badge: "badge-violet",
    tag: "ML",
  },
  {
    id: "bosque",
    name: "Random Forest",
    desc: "Ensemble de árboles de decisión",
    badge: "badge-violet",
    tag: "ML",
  },
];

const canTrain = computed(
  () =>
    store.dataset && store.selectedColumn && store.selectedModels.length > 0,
);

function isSelected(id) {
  return store.selectedModels.includes(id);
}

function toggleModel(id) {
  const idx = store.selectedModels.indexOf(id);
  if (idx > -1) {
    if (store.selectedModels.length > 1) store.selectedModels.splice(idx, 1);
  } else {
    store.selectedModels.push(id);
  }
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

.error-banner,
.warn-banner {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 13px;
  flex-shrink: 0;
}
.error-banner {
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: var(--coral);
}
.warn-banner {
  background: rgba(245, 200, 66, 0.07);
  border: 1px solid rgba(245, 200, 66, 0.2);
  color: var(--gold-dim);
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.card-title {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-disabled {
  opacity: 0.45;
  pointer-events: none;
}

.model-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-row {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  cursor: pointer;
  transition: all var(--transition);
}

.model-row.selected {
  border-color: rgba(245, 200, 66, 0.35);
  background: rgba(245, 200, 66, 0.05);
}

.model-info {
  flex: 1;
}

.model-name {
  display: block;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
}

.model-desc {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 1px;
}

.degree-row {
  display: flex;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.deg-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 15px;
  cursor: pointer;
  transition: all var(--transition);
}

.deg-btn:hover {
  border-color: var(--border-bright);
  color: var(--text-primary);
}
.deg-btn.active {
  background: var(--gold);
  color: #0d0b00;
  border-color: var(--gold);
}

.hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 6px;
  padding: 6px 10px;
  background: rgba(255, 107, 107, 0.07);
  border-left: 2px solid var(--coral);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.hint-good {
  background: rgba(0, 212, 170, 0.07);
  border-color: var(--teal);
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.svr-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.svr-info strong {
  color: var(--teal);
}

/* KNN slider row */
.knn-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.knn-slider {
  flex: 1;
  accent-color: var(--coral);
  cursor: pointer;
}
.knn-val {
  min-width: 24px;
  text-align: center;
}

/* Training history */
.history-section {
  background: rgba(245, 200, 66, 0.04);
  border: 1px solid rgba(245, 200, 66, 0.18);
  border-radius: var(--radius-md);
  overflow: hidden;
  flex-shrink: 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 14px;
  background: rgba(245, 200, 66, 0.07);
  border-bottom: 1px solid rgba(245, 200, 66, 0.15);
}

.history-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--gold-dim);
  text-transform: uppercase;
}

.history-count {
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.history-list {
  max-height: 280px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.history-item {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.history-item:last-child { border-bottom: none; }

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 7px;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-id {
  font-size: 10px;
  color: var(--gold-dim);
}

.history-col {
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--bg-card);
  padding: 1px 7px;
  border-radius: 4px;
  border: 1px solid var(--border);
}

.history-time {
  font-size: 10px;
  color: var(--text-muted);
}

.btn-delete {
  background: none;
  border: 1px solid rgba(255,107,107,0.25);
  color: rgba(255,107,107,0.6);
  border-radius: 4px;
  width: 22px;
  height: 22px;
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}
.btn-delete:hover {
  background: rgba(255,107,107,0.12);
  color: var(--coral);
  border-color: var(--coral);
}

.history-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.result-chip {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 3px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 99px;
  font-size: 11px;
  color: var(--text-secondary);
}

.chip-label {
  color: var(--text-primary);
  font-size: 11px;
}

.text-muted {
  color: var(--text-muted);
}
</style>
