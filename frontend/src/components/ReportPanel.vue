<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1 class="panel-title">REPORTE</h1>
        <p class="panel-sub">
          Generación de PDF técnico para entrega académica
        </p>
      </div>
      <button class="btn reports-toggle-btn" @click="showReports = !showReports">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path
            d="M2 3h10M2 7h7M2 11h4"
            stroke="currentColor"
            stroke-width="1.4"
            stroke-linecap="round"
          />
        </svg>
        Vista previa
        <span v-if="store.generatedReports.length" class="reports-count-badge">{{
          store.generatedReports.length
        }}</span>
        <svg
          class="toggle-chevron"
          :class="{ rotated: !showReports }"
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
        >
          <path
            d="M3 8L6 5l3 3"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </header>

    <div v-if="!store.hasTrainResults" class="warn-banner">
      ← Entrena los modelos primero en la pestaña <strong>Modelos</strong>
    </div>

    <div class="report-layout">
      <!-- ── CENTER: Generated reports + viewer ─────────────────────────── -->
      <div class="reports-main">
        <!-- Empty state -->
        <div v-if="!store.generatedReports.length" class="card empty-card">
          <div class="empty-glyph">⊡</div>
          <p class="empty-title">Sin reportes generados</p>
          <p class="empty-sub">
            Los reportes PDF aparecerán aquí una vez generados.<br />
            Podrás visualizarlos directamente sin salir de la app.
          </p>
        </div>

        <template v-else>
          <!-- Reports list -->
          <div class="card reports-list-card">
            <div class="card-section-title">Reportes generados</div>
            <div class="reports-list">
              <div
                v-for="(rep, i) in store.generatedReports"
                :key="i"
                class="report-item"
                :class="{ active: selectedReportIdx === i }"
                @click="selectedReportIdx = i"
              >
                <div class="report-item-icon">
                  <svg width="18" height="20" viewBox="0 0 18 20" fill="none">
                    <path
                      d="M10 1H3a2 2 0 00-2 2v14a2 2 0 002 2h12a2 2 0 002-2V7L10 1z"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M10 1v6h6"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linejoin="round"
                    />
                  </svg>
                </div>
                <div class="report-item-info">
                  <div class="report-item-name">{{ rep.filename }}</div>
                  <div class="report-item-date">{{ rep.timestamp }}</div>
                </div>
                <a
                  :href="rep.url"
                  :download="rep.filename"
                  class="report-item-dl"
                  title="Descargar"
                  @click.stop
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path
                      d="M7 1v8M4 7l3 3 3-3M2 12h10"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </a>
                <button
                  class="report-item-del"
                  title="Eliminar"
                  @click.stop="deleteReport(i)"
                >
                  <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
                    <path
                      d="M2 3.5h10M5.5 3.5V2.5h3v1M5 3.5l.5 8M9 3.5l-.5 8"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Inline PDF Viewer -->
          <div v-if="showReports" class="card viewer-card">
            <div class="viewer-header">
              <div class="card-section-title" style="margin-bottom: 0">
                Vista previa
                <span class="viewer-fname">— {{ activeReport?.filename }}</span>
              </div>
              <a
                :href="activeReport?.url"
                :download="activeReport?.filename"
                class="btn btn-sm viewer-dl"
              >
                <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
                  <path
                    d="M7 1v8M4 7l3 3 3-3M2 12h10"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                Descargar
              </a>
            </div>
            <iframe
              v-if="activeReport"
              :src="activeReport.url + '#toolbar=1&navpanes=0'"
              class="pdf-iframe"
              type="application/pdf"
            />
          </div>
        </template>
      </div>

      <!-- ── RIGHT SIDEBAR: TOC checks + Generate ───────────────────────── -->
      <div class="right-sidebar">
        <!-- Content checks -->
        <div class="card preview-card">
          <div class="card-section-title">Contenido del reporte</div>
          <div class="toc-list">
            <div class="toc-item" :class="{ inactive: !store.dataset }">
              <span class="toc-num">01</span>
              <div>
                <div class="toc-title">Datos del experimento</div>
                <div class="toc-desc">Instrumento, dataset, columna de frecuencia</div>
              </div>
              <span class="toc-status" :class="store.dataset ? 'ok' : 'pending'">
                {{ store.dataset ? "✓" : "○" }}
              </span>
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

            <div class="toc-item" :class="{ inactive: !store.hasTrainResults }">
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

            <div class="toc-item" :class="{ inactive: !store.hasTrainResults }">
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

        <!-- Generate card -->
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
            {{ store.loadingReport ? "Generando PDF…" : "Generar Reporte PDF" }}
          </button>

          <p class="pdf-hint">
            El PDF incluye ecuaciones, métricas y gráficos listos para entregar
            al docente.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, watch } from "vue";
import { useLabStore } from "@/stores/labStore";

const store = useLabStore();

const selectedReportIdx = ref(0);

function deleteReport(idx) {
  store.deleteReport(idx);
  // Keep selectedReportIdx in bounds after removal
  const len = store.generatedReports.length;
  if (selectedReportIdx.value >= len) {
    selectedReportIdx.value = Math.max(0, len - 1);
  }
}
const showReports = ref(true);

const activeReport = computed(
  () => store.generatedReports[selectedReportIdx.value] ?? null,
);

// Auto-select the newest report when a new one is added
watch(
  () => store.generatedReports.length,
  (len) => { if (len > 0) selectedReportIdx.value = len - 1; },
);

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
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
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

/* Toggle button */
.reports-toggle-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 7px 12px;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: all var(--transition);
  margin-top: 4px;
}

.reports-toggle-btn:hover {
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.15);
}

.reports-count-badge {
  background: rgba(78, 209, 180, 0.15);
  color: var(--teal);
  border-radius: 10px;
  padding: 1px 6px;
  font-size: 11px;
  font-weight: 600;
  font-family: var(--font-mono);
}

.toggle-chevron {
  transition: transform 200ms ease;
  color: var(--text-muted);
}

.toggle-chevron.rotated {
  transform: rotate(180deg);
}

.report-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 16px;
  align-items: start;
  flex: 1;
  min-height: 0;
}

/* ── Center: reports main ───────────────────────────────────────────────── */
.reports-main {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Empty state */
.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 56px 24px;
  text-align: center;
  gap: 10px;
  min-height: 260px;
}

.empty-glyph {
  font-size: 48px;
  color: var(--text-muted);
  opacity: 0.3;
  line-height: 1;
}

.empty-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.empty-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.6;
}

/* Reports list */
.reports-list-card {
  padding-bottom: 8px;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.report-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition);
  border: 1px solid transparent;
}

.report-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.report-item.active {
  background: rgba(78, 209, 180, 0.08);
  border-color: rgba(78, 209, 180, 0.2);
}

.report-item-icon {
  flex-shrink: 0;
  color: var(--text-muted);
  display: flex;
  align-items: center;
}

.report-item.active .report-item-icon {
  color: var(--teal);
}

.report-item-info {
  flex: 1;
  min-width: 0;
}

.report-item-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  font-family: var(--font-mono);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.report-item-date {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.report-item-dl {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border);
  text-decoration: none;
  transition: all var(--transition);
}

.report-item-dl:hover {
  color: var(--teal);
  border-color: var(--teal);
  background: rgba(78, 209, 180, 0.08);
}

.report-item-del {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all var(--transition);
  padding: 0;
}

.report-item-del:hover {
  color: var(--coral);
  border-color: rgba(255, 107, 107, 0.4);
  background: rgba(255, 107, 107, 0.08);
}

/* Viewer */
.viewer-card {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.viewer-fname {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
}

.viewer-dl {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  text-decoration: none;
  padding: 5px 10px;
  flex-shrink: 0;
}

.pdf-iframe {
  width: 100%;
  height: 560px;
  border: none;
  border-radius: var(--radius-sm);
  background: #1a1a1a;
}

/* ── Right sidebar ──────────────────────────────────────────────────────── */
.right-sidebar {
  display: flex;
  flex-direction: column;
  gap: 14px;
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
