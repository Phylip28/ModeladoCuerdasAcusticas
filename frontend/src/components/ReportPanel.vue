<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1 class="panel-title">REPORTE</h1>
        <p class="panel-sub">
          Generación de PDF técnico para entrega académica
        </p>
      </div>
    </header>

    <div v-if="!store.hasTrainResults" class="warn-banner">
      ← Entrena los modelos primero en la pestaña <strong>Modelos</strong>
    </div>

    <div class="report-layout">
      <!-- Preview of PDF contents -->
      <div class="card preview-card">
        <div class="card-section-title">Contenido del reporte</div>

        <div class="toc-list">
          <div class="toc-item">
            <span class="toc-num">01</span>
            <div>
              <div class="toc-title">Portada y datos del experimento</div>
              <div class="toc-desc">
                Integrantes, instrumento, dataset utilizado
              </div>
            </div>
            <span class="toc-status ok">✓</span>
          </div>

          <div class="toc-item" :class="{ inactive: !store.hasTrainResults }">
            <span class="toc-num">02</span>
            <div>
              <div class="toc-title">Tabla comparativa de métricas</div>
              <div class="toc-desc">R², MSE, MAE por cada modelo entrenado</div>
            </div>
            <span
              class="toc-status"
              :class="store.hasTrainResults ? 'ok' : 'pending'"
            >
              {{ store.hasTrainResults ? "✓" : "○" }}
            </span>
          </div>

          <div class="toc-item" :class="{ inactive: !hasPolynomial }">
            <span class="toc-num">03</span>
            <div>
              <div class="toc-title">Ecuación del modelo polinomial</div>
              <div class="toc-desc">f(L) = a·Lⁿ + … coeficientes completos</div>
            </div>
            <span class="toc-status" :class="hasPolynomial ? 'ok' : 'pending'">
              {{ hasPolynomial ? "✓" : "○" }}
            </span>
          </div>

          <div class="toc-item">
            <span class="toc-num">04</span>
            <div>
              <div class="toc-title">
                Gráfico de dispersión + curvas de ajuste
              </div>
              <div class="toc-desc">Imagen exportada con matplotlib</div>
            </div>
            <span
              class="toc-status"
              :class="store.hasTrainResults ? 'ok' : 'pending'"
            >
              {{ store.hasTrainResults ? "✓" : "○" }}
            </span>
          </div>

          <div class="toc-item">
            <span class="toc-num">05</span>
            <div>
              <div class="toc-title">Gráfico de residuos</div>
              <div class="toc-desc">Análisis de errores por punto</div>
            </div>
            <span
              class="toc-status"
              :class="store.hasTrainResults ? 'ok' : 'pending'"
            >
              {{ store.hasTrainResults ? "✓" : "○" }}
            </span>
          </div>

          <div class="toc-item" :class="{ inactive: !hasMlp }">
            <span class="toc-num">06</span>
            <div>
              <div class="toc-title">Curva de pérdida MLP</div>
              <div class="toc-desc">
                Convergencia del entrenamiento neuronal
              </div>
            </div>
            <span class="toc-status" :class="hasMlp ? 'ok' : 'pending'">
              {{ hasMlp ? "✓" : "○" }}
            </span>
          </div>
        </div>
      </div>

      <!-- Generate -->
      <div class="card generate-card">
        <div class="card-section-title">Configuración de exportación</div>

        <div class="gen-info">
          <div class="gen-row">
            <span class="gen-label">Columna usada</span>
            <span class="gen-val mono">{{ store.selectedColumn || "—" }}</span>
          </div>
          <div class="gen-row">
            <span class="gen-label">Modelos incluidos</span>
            <div class="gen-badges">
              <span
                v-for="m in store.selectedModels"
                :key="m"
                class="badge"
                :class="modelBadge(m)"
                >{{ m }}</span
              >
            </div>
          </div>
          <div
            class="gen-row"
            v-if="store.selectedModels.includes('polinomial')"
          >
            <span class="gen-label">Grado polinomial</span>
            <span class="gen-val mono">{{ store.polyGrado }}</span>
          </div>
          <div class="gen-row" v-if="store.bestModel">
            <span class="gen-label">Mejor modelo</span>
            <span class="gen-val text-teal">{{
              store.bestModel.etiqueta
            }}</span>
          </div>
        </div>

        <div class="divider" />

        <div v-if="store.reportError" class="error-banner">
          ⚠ {{ store.reportError }}
        </div>

        <button
          class="btn btn-primary btn-big"
          :disabled="!store.hasTrainResults || store.loadingReport"
          @click="store.downloadReport()"
        >
          <div
            v-if="store.loadingReport"
            class="spinner"
            style="width: 14px; height: 14px"
          />
          <span v-else class="btn-icon">⊡</span>
          {{ store.loadingReport ? "Generando PDF…" : "Descargar Reporte PDF" }}
        </button>

        <p class="pdf-hint">
          El PDF incluye ecuaciones, métricas y gráficos listos para entregar al
          docente.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useLabStore } from "@/stores/labStore";

const store = useLabStore();

const hasPolynomial = computed(
  () => store.selectedModels.includes("polinomial") && store.hasTrainResults,
);
const hasMlp = computed(
  () => store.selectedModels.includes("mlp") && store.hasTrainResults,
);

function modelBadge(name) {
  return (
    { polinomial: "badge-gold", svr: "badge-teal", mlp: "badge-violet" }[
      name
    ] ?? ""
  );
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

.report-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 16px;
  align-items: start;
}

.card-section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* TOC */
.toc-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.toc-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  transition: opacity var(--transition);
}

.toc-item:last-child {
  border-bottom: none;
}

.toc-item.inactive {
  opacity: 0.4;
}

.toc-num {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  flex-shrink: 0;
  width: 22px;
}

.toc-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.toc-desc {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.toc-status {
  margin-left: auto;
  font-size: 14px;
  flex-shrink: 0;
}
.toc-status.ok {
  color: var(--teal);
}
.toc-status.pending {
  color: var(--text-muted);
}

/* Generate card */
.generate-card {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.gen-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.gen-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}

.gen-label {
  color: var(--text-muted);
}

.gen-val {
  color: var(--text-primary);
  font-size: 12px;
}

.gen-badges {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.error-banner {
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: var(--coral);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: 12px;
  margin-bottom: 14px;
}

.btn-big {
  width: 100%;
  justify-content: center;
  padding: 12px;
  font-size: 14px;
  letter-spacing: 0.03em;
}

.btn-icon {
  font-size: 16px;
}

.pdf-hint {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
  margin-top: 10px;
  line-height: 1.5;
}
</style>
