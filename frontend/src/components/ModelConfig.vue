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
              v-for="g in [1, 2, 3, 4, 5]"
              :key="g"
              class="deg-btn"
              :class="{ active: store.polyGrado === g }"
              :disabled="!isSelected('polinomial')"
              @click="store.polyGrado = g"
            >
              {{ g }}
            </button>
          </div>
          <div class="hint" v-if="store.polyGrado === 1">
            ℹ Grado 1 → error alto esperado (f∝1/L no es lineal)
          </div>
          <div class="hint hint-good" v-else-if="store.polyGrado >= 2">
            ℹ Grado {{ store.polyGrado }} → buena aproximación de la hipérbola
            física
          </div>
        </div>
      </section>

      <!-- MLP config -->
      <section class="card" :class="{ 'card-disabled': !isSelected('mlp') }">
        <div class="card-title">
          Red Neuronal MLP
          <span class="badge badge-violet">Deep Learning</span>
        </div>
        <div class="field">
          <label>Capas ocultas (nodos por capa, separados por coma)</label>
          <input
            v-model="store.mlpCapas"
            type="text"
            placeholder="10,10"
            :disabled="!isSelected('mlp')"
          />
        </div>
        <div class="two-col">
          <div class="field">
            <label>Activación</label>
            <select
              v-model="store.mlpActivacion"
              :disabled="!isSelected('mlp')"
            >
              <option value="relu">ReLU</option>
              <option value="tanh">Tanh</option>
              <option value="logistic">Logistic</option>
            </select>
          </div>
          <div class="field">
            <label>Max iteraciones</label>
            <input
              v-model.number="store.mlpMaxIter"
              type="number"
              min="100"
              max="20000"
              step="100"
              :disabled="!isSelected('mlp')"
            />
          </div>
        </div>
      </section>

      <!-- SVR info -->
      <section class="card" :class="{ 'card-disabled': !isSelected('svr') }">
        <div class="card-title">
          SVR — Vector Support Regression
          <span class="badge badge-teal">ML</span>
        </div>
        <div class="svr-info">
          <p>Kernel <strong>RBF</strong> con C=100, γ=0.1, ε=0.1.</p>
          <p>Excelente para relaciones no lineales con pocos datos.</p>
          <p>No requiere configuración adicional para este dataset.</p>
        </div>
      </section>
    </div>

    <!-- Result summary -->
    <Transition name="slide-up">
      <div v-if="store.hasTrainResults" class="results-summary">
        <div class="results-label">
          <span
            class="status-dot ok"
            style="
              display: inline-block;
              width: 7px;
              height: 7px;
              border-radius: 50%;
              box-shadow: 0 0 6px var(--teal);
              background: var(--teal);
            "
          />
          Entrenamiento completado
        </div>
        <div class="results-chips">
          <div
            v-for="res in store.trainResult.resultados"
            :key="res.nombre"
            class="result-chip"
          >
            <span>{{ res.etiqueta }}</span>
            <span class="mono text-gold"
              >R²={{ res.metricas.r2?.toFixed(4) ?? "—" }}</span
            >
          </div>
        </div>
      </div>
    </Transition>
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
    badge: "badge-teal",
    tag: "ML",
  },
  {
    id: "mlp",
    name: "Red Neuronal",
    desc: "MLPRegressor multicapa",
    badge: "badge-violet",
    tag: "MLP",
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

.results-summary {
  background: rgba(0, 212, 170, 0.07);
  border: 1px solid rgba(0, 212, 170, 0.2);
  border-radius: var(--radius-md);
  padding: 12px 16px;
}

.results-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--teal);
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 8px;
}

.results-chips {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.result-chip {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 4px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 99px;
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
