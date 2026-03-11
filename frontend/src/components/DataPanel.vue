<template>
  <div class="panel">
    <header class="panel-header">
      <div>
        <h1 class="panel-title">DATASET</h1>
        <p class="panel-sub">Carga y selección de columna de frecuencia</p>
      </div>
      <div class="header-actions">
        <label class="btn btn-outline" title="Subir CSV personalizado">
          <svg
            width="14"
            height="14"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          Subir CSV
          <input
            type="file"
            accept=".csv"
            class="hidden-input"
            @change="handleUpload"
          />
        </label>
        <button
          class="btn btn-ghost"
          @click="store.reload()"
          :disabled="store.loadingData"
        >
          <div
            v-if="store.loadingData"
            class="spinner"
            style="width: 12px; height: 12px"
          />
          <span v-else>↺</span>
          Recargar
        </button>
        <!-- Manual-only buttons -->
        <template v-if="store.isManual">
          <button
            class="btn btn-ghost btn-manual-action"
            @click="openManual(false)"
            title="Editar registros ingresados"
          >
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Editar
          </button>
          <button
            class="btn btn-ghost btn-manual-action"
            @click="openManual(true)"
            title="Agregar nueva columna de medición"
          >
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <rect x="3" y="3" width="7" height="18" rx="1"/>
              <rect x="14" y="3" width="7" height="18" rx="1"/>
              <line x1="17.5" y1="9" x2="17.5" y2="15"/>
              <line x1="14.5" y1="12" x2="20.5" y2="12"/>
            </svg>
            + Columna
          </button>
        </template>
        <button
          class="btn btn-teal"
          @click="openManual(false)"
          v-if="!store.isManual"
          title="Ingresar datos manualmente"
        >
          <svg
            width="14"
            height="14"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
          >
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Entrada Manual
        </button>
      </div>
    </header>

    <!-- Error -->
    <div v-if="store.dataError" class="error-banner">
      ⚠ {{ store.dataError }}
    </div>

    <!-- Loading skeleton -->
    <div v-if="store.loadingData" class="loading-area">
      <div class="spinner" />
      <span>Cargando dataset…</span>
    </div>

    <template v-else-if="store.dataset">
      <!-- Column selector -->
      <section class="column-selector">
        <div class="section-label">Columna de frecuencia activa</div>
        <div class="col-chips">
          <button
            v-for="col in store.columnOptions"
            :key="col"
            class="col-chip"
            :class="{ active: store.selectedColumn === col }"
            @click="store.selectedColumn = col"
          >
            {{ col }}
          </button>
        </div>
      </section>

      <!-- Stats bar -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-val mono">{{ store.dataset.total }}</span>
          <span class="stat-label">Puntos</span>
        </div>
        <div class="stat-item">
          <span class="stat-val mono">{{ minL.toFixed(1) }}</span>
          <span class="stat-label">L min (cm)</span>
        </div>
        <div class="stat-item">
          <span class="stat-val mono">{{ maxL.toFixed(1) }}</span>
          <span class="stat-label">L max (cm)</span>
        </div>
        <div class="stat-item" v-if="activeMean">
          <span class="stat-val mono">{{ activeMean.toFixed(1) }}</span>
          <span class="stat-label">f̄ (Hz)</span>
        </div>
      </div>

      <!-- Data table -->
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Traste</th>
              <th>L (cm)</th>
              <th
                v-for="col in store.columnOptions.slice(0, 6)"
                :key="col"
                :class="{ 'col-active': col === store.selectedColumn }"
              >
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(pt, i) in store.dataset.puntos" :key="i">
              <td class="mono">{{ pt.traste }}</td>
              <td class="mono text-gold">{{ pt.longitud_cm.toFixed(1) }}</td>
              <td
                v-for="col in store.columnOptions.slice(0, 6)"
                :key="col"
                class="mono"
                :class="{
                  'col-active': col === store.selectedColumn,
                  'null-val': pt.frecuencias[col] == null,
                }"
              >
                {{
                  pt.frecuencias[col] != null
                    ? pt.frecuencias[col].toFixed(1)
                    : "—"
                }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else class="empty-state">
      <div class="empty-icon">⊞</div>
      <p>No hay datos cargados</p>
      <button class="btn btn-primary" @click="store.fetchDataset()">
        Cargar dataset
      </button>
    </div>
  </div>

  <!-- ── Manual entry modal ─────────────────────────────────────────────── -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="showManual"
        class="modal-overlay"
        @click.self="showManual = false"
      >
        <div class="modal-box modal-box--wide" role="dialog" aria-modal="true">
          <header class="modal-header">
            <h2 class="modal-title">
              {{ isEditMode ? 'EDITAR DATOS' : 'ENTRADA MANUAL' }}
            </h2>
            <button class="btn btn-ghost icon-btn" @click="showManual = false">✕</button>
          </header>

          <div class="manual-table-wrap">
            <table class="manual-table">
              <thead>
                <tr>
                  <th class="th-fixed">Traste</th>
                  <th class="th-fixed">L (cm) <span class="req-star">*</span></th>
                  <th v-for="(col, ci) in manualCols" :key="ci" class="th-col-name">
                    <div class="col-name-wrap">
                      <input
                        v-model="manualCols[ci]"
                        class="col-name-input"
                        :placeholder="'Col ' + (ci + 1)"
                        spellcheck="false"
                      />
                      <button
                        v-if="manualCols.length > 1"
                        class="del-col-btn"
                        @click="removeManualCol(ci)"
                        title="Eliminar columna"
                      >✕</button>
                    </div>
                  </th>
                  <th class="th-add-col">
                    <button class="add-col-btn" @click="addManualCol" title="Agregar columna">+</button>
                  </th>
                  <th class="th-del-row"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, ri) in manualRows" :key="ri">
                  <td>
                    <input
                      v-model.number="row.traste"
                      type="number"
                      class="mini-input"
                      placeholder="—"
                      min="0"
                    />
                  </td>
                  <td>
                    <input
                      v-model.number="row.longitud_cm"
                      type="number"
                      class="mini-input"
                      :class="{ 'input-err': row._touched && row.longitud_cm == null }"
                      placeholder="0.0"
                      step="0.1"
                      min="0"
                      @blur="row._touched = true"
                    />
                  </td>
                  <td v-for="(col, ci) in manualCols" :key="ci">
                    <input
                      v-model.number="row.values[ci]"
                      type="number"
                      class="mini-input"
                      placeholder="—"
                      step="0.1"
                      min="0"
                    />
                  </td>
                  <td></td>
                  <td>
                    <button
                      class="del-btn"
                      @click="removeManualRow(ri)"
                      title="Eliminar fila"
                    >✕</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <button class="btn btn-ghost add-row-btn" @click="addManualRow">
            + Agregar fila
          </button>

          <p class="hint-text">
            Al menos 3 filas con longitud requeridas. Los Hz en blanco se guardan como sin dato.
          </p>

          <div v-if="manualError" class="error-banner" style="margin-top: 10px">
            ⚠ {{ manualError }}
          </div>

          <footer class="modal-footer">
            <button class="btn btn-outline" @click="showManual = false">Cancelar</button>
            <button
              class="btn btn-primary"
              @click="confirmManual"
              :disabled="store.loadingData"
            >
              <div v-if="store.loadingData" class="spinner" style="width: 12px; height: 12px" />
              <span v-else>Confirmar</span>
            </button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref } from "vue";
import { useLabStore } from "@/stores/labStore";

const store = useLabStore();

// ── Manual entry state ────────────────────────────────────────────────────
const showManual = ref(false);
const isEditMode = ref(false);
const manualError = ref("");
const manualCols = ref(["Hz Manual"]);

const newRow = () => ({
  traste: null,
  longitud_cm: null,
  values: manualCols.value.map(() => null),
  _touched: false,
});

const manualRows = ref([newRow(), newRow(), newRow()]);

function openManual(addColumn = false) {
  isEditMode.value = store.isManual && !!store.dataset;
  if (isEditMode.value) {
    // Pre-fill from existing manual dataset
    manualCols.value = [...store.dataset.columnas_frecuencia];
    if (addColumn) {
      manualCols.value.push("Hz Nueva " + (manualCols.value.length + 1));
    }
    manualRows.value = store.dataset.puntos.map((p) => ({
      traste: p.traste || null,
      longitud_cm: p.longitud_cm,
      values: manualCols.value.map((c) => p.frecuencias[c] ?? null),
      _touched: false,
    }));
  } else {
    manualCols.value = ["Hz Manual"];
    manualRows.value = [newRow(), newRow(), newRow()];
  }
  manualError.value = "";
  showManual.value = true;
}

function addManualCol() {
  manualCols.value.push("Hz Nueva " + (manualCols.value.length + 1));
  manualRows.value.forEach((r) => r.values.push(null));
}

function removeManualCol(ci) {
  if (manualCols.value.length <= 1) return;
  manualCols.value.splice(ci, 1);
  manualRows.value.forEach((r) => r.values.splice(ci, 1));
}

function addManualRow() {
  manualRows.value.push({
    traste: null,
    longitud_cm: null,
    values: manualCols.value.map(() => null),
    _touched: false,
  });
}

function removeManualRow(i) {
  if (manualRows.value.length > 1) manualRows.value.splice(i, 1);
}

async function confirmManual() {
  manualError.value = "";
  manualRows.value.forEach((r) => (r._touched = true));
  const valid = manualRows.value.filter((r) => r.longitud_cm != null);
  if (valid.length < 3) {
    manualError.value = "Completa al menos 3 filas con longitud (cm).";
    return;
  }
  const columnas = manualCols.value.map((c, i) => c.trim() || `Columna ${i + 1}`);
  const puntos = valid.map((r) => ({
    traste: r.traste ?? null,
    longitud_cm: r.longitud_cm,
    frecuencias: Object.fromEntries(
      columnas.map((c, ci) => [c, r.values[ci] ?? null]),
    ),
  }));
  await store.manualData(puntos, columnas);
  if (!store.dataError) {
    showManual.value = false;
  } else {
    manualError.value = store.dataError;
  }
}
// ── end manual entry ──

const minL = computed(() =>
  store.dataset
    ? Math.min(...store.dataset.puntos.map((p) => p.longitud_cm))
    : 0,
);
const maxL = computed(() =>
  store.dataset
    ? Math.max(...store.dataset.puntos.map((p) => p.longitud_cm))
    : 0,
);
const activeMean = computed(() => {
  if (!store.dataset || !store.selectedColumn) return null;
  const vals = store.dataset.puntos
    .map((p) => p.frecuencias[store.selectedColumn])
    .filter((v) => v != null);
  return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
});

function handleUpload(e) {
  const file = e.target.files?.[0];
  if (file) store.uploadCSV(file);
}
</script>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
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
  gap: 8px;
  align-items: center;
}

.hidden-input {
  display: none;
}

.error-banner {
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: var(--coral);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 13px;
  flex-shrink: 0;
}

.loading-area {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  padding: 20px 0;
}

.column-selector {
  flex-shrink: 0;
}

.section-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.col-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.col-chip {
  padding: 4px 12px;
  border-radius: 99px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 11px;
  font-family: var(--font-mono);
  cursor: pointer;
  transition: all var(--transition);
}

.col-chip:hover {
  border-color: var(--border-bright);
  color: var(--text-primary);
}

.col-chip.active {
  background: rgba(245, 200, 66, 0.12);
  border-color: var(--gold);
  color: var(--gold);
}

.stats-bar {
  display: flex;
  gap: 20px;
  flex-shrink: 0;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 12px 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-val {
  font-size: 20px;
  color: var(--gold);
  line-height: 1;
}

.stat-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.table-wrap {
  flex: 1;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  position: sticky;
  top: 0;
  background: var(--bg-surface);
  padding: 8px 14px;
  text-align: right;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

.data-table th:first-child,
.data-table td:first-child {
  text-align: center;
}

.data-table td {
  padding: 7px 14px;
  text-align: right;
  border-bottom: 1px solid rgba(100, 126, 200, 0.07);
  color: var(--text-secondary);
  transition: background var(--transition);
}

.data-table tbody tr:hover td {
  background: var(--bg-card-hover);
}

.col-active {
  color: var(--teal) !important;
}

.null-val {
  color: var(--text-muted) !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  flex: 1;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 48px;
  opacity: 0.3;
}

/* ── field-label helper ─────────────────────────────────────────────────── */
.field-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

/* ── Manual-only header buttons ─────────────────────────────────────────── */
.btn-manual-action {
  color: var(--teal);
  border-color: rgba(0, 212, 170, 0.2);
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.btn-manual-action:hover {
  background: rgba(0, 212, 170, 0.08);
  border-color: var(--teal);
}

/* ── btn-teal variant ───────────────────────────────────────────────────── */
.btn-teal {
  background: rgba(0, 212, 170, 0.1);
  border: 1px solid rgba(0, 212, 170, 0.35);
  color: var(--teal);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
}
.btn-teal:hover {
  background: rgba(0, 212, 170, 0.18);
  border-color: var(--teal);
}

/* ── Modal overlay ──────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(6, 11, 24, 0.82);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.modal-box {
  background: var(--bg-surface);
  border: 1px solid var(--border-bright);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 560px;
  max-height: 80vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 24px 28px;
  box-shadow:
    0 24px 60px rgba(0, 0, 0, 0.6),
    0 0 0 1px rgba(0, 212, 170, 0.06);
}

.modal-box--wide {
  max-width: 820px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 22px;
  letter-spacing: 0.12em;
  color: var(--teal);
  margin: 0;
}

.icon-btn {
  padding: 4px 10px;
  font-size: 14px;
  line-height: 1;
}

.manual-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  margin-bottom: 12px;
}

.manual-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.manual-table th {
  background: var(--bg-deep);
  padding: 8px 12px;
  text-align: left;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

/* Fixed-width cols (Traste, Longitud) */
.th-fixed {
  min-width: 80px;
}

/* Editable column name header */
.th-col-name {
  min-width: 130px;
}

.col-name-wrap {
  display: flex;
  align-items: center;
  gap: 4px;
}

.col-name-input {
  flex: 1;
  min-width: 0;
  background: rgba(0, 212, 170, 0.07);
  border: 1px solid rgba(0, 212, 170, 0.25);
  color: var(--teal);
  border-radius: var(--radius-sm);
  padding: 3px 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  outline: none;
  transition: border-color var(--transition);
}

.col-name-input:focus {
  border-color: var(--teal);
  background: rgba(0, 212, 170, 0.12);
}

.del-col-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 10px;
  padding: 2px 4px;
  border-radius: 3px;
  flex-shrink: 0;
  transition: color var(--transition);
  line-height: 1;
}
.del-col-btn:hover { color: var(--coral); }

/* Add column header */
.th-add-col {
  width: 36px;
  text-align: center;
  padding: 4px 6px !important;
}

.add-col-btn {
  background: rgba(0, 212, 170, 0.1);
  border: 1px solid rgba(0, 212, 170, 0.3);
  color: var(--teal);
  border-radius: 4px;
  width: 22px;
  height: 22px;
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}
.add-col-btn:hover {
  background: rgba(0, 212, 170, 0.2);
  border-color: var(--teal);
}

.th-del-row {
  width: 28px;
}

.manual-table td {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(100, 126, 200, 0.08);
}

.manual-table tbody tr:last-child td {
  border-bottom: none;
}

.mini-input {
  width: 100%;
  min-width: 90px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  padding: 5px 8px;
  font-family: var(--font-mono);
  font-size: 12px;
  transition: border-color var(--transition);
}

.mini-input:focus {
  outline: none;
  border-color: var(--teal);
}

.mini-input.input-err {
  border-color: var(--coral);
}

.req-star {
  color: var(--coral);
}

.del-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  transition: color var(--transition);
}

.del-btn:hover {
  color: var(--coral);
}

.add-row-btn {
  font-size: 12px;
  padding: 5px 12px;
  margin-bottom: 10px;
  color: var(--teal);
  border-color: rgba(0, 212, 170, 0.2);
}

.hint-text {
  font-size: 11px;
  color: var(--text-muted);
  margin: 0 0 4px 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

/* Modal transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.18s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-box,
.modal-fade-leave-active .modal-box {
  transition: transform 0.18s ease;
}

.modal-fade-enter-from .modal-box,
.modal-fade-leave-to .modal-box {
  transform: translateY(-12px) scale(0.97);
}
</style>
