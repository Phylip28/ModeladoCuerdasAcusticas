import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const useLabStore = defineStore('lab', () => {
  // ── Dataset ──────────────────────────────────────────────────────────────
  const dataset = ref(null)         // DatasetResponse
  const selectedColumn = ref('')    // columna_frecuencia activa
  const loadingData = ref(false)
  const dataError = ref('')
  const showLoadingOverlay = ref(false)
  const isManual = ref(false)       // true cuando los datos vienen de entrada manual

  // ── Model config ─────────────────────────────────────────────────────────
  const selectedModels = ref(['polinomial'])
  const polyGrado = ref(2)
  const mlpCapas = ref('10,10')
  const mlpActivacion = ref('relu')
  const mlpMaxIter = ref(5000)

  // ── Train results ─────────────────────────────────────────────────────────
  const trainResult = ref(null)     // TrainResponse
  const loadingTrain = ref(false)
  const trainError = ref('')

  // ── Prediction ────────────────────────────────────────────────────────────
  const predictLength = ref(45)
  const predictResult = ref(null)   // PredictResponse
  const loadingPredict = ref(false)

  // ── Report ────────────────────────────────────────────────────────────────
  const loadingReport = ref(false)
  const reportError = ref('')

  // ── Computed ──────────────────────────────────────────────────────────────
  const columnOptions = computed(() =>
    dataset.value?.columnas_frecuencia ?? []
  )

  const hasTrainResults = computed(() => trainResult.value !== null)

  const bestModel = computed(() => {
    if (!trainResult.value) return null
    return trainResult.value.resultados.reduce((best, cur) =>
      cur.metricas.mse < best.metricas.mse ? cur : best
    , trainResult.value.resultados[0])
  })

  // ── Actions ───────────────────────────────────────────────────────────────
  /** Shows the loading overlay for at least 1500ms, then fetches data. */
  async function reload() {
    showLoadingOverlay.value = true
    const minWait = new Promise((r) => setTimeout(r, 1500))
    await Promise.all([fetchDataset(), minWait])
    showLoadingOverlay.value = false
  }

  async function fetchDataset() {
    loadingData.value = true
    dataError.value = ''
    try {
      const { data } = await api.get('/data/')
      dataset.value = data
      isManual.value = data.is_manual ?? false
      if (!selectedColumn.value && data.columnas_frecuencia.length) {
        selectedColumn.value = data.columnas_frecuencia[0]
      }
    } catch (e) {
      dataError.value = e.response?.data?.detail ?? e.message
    } finally {
      loadingData.value = false
    }
  }

  async function uploadCSV(file) {
    loadingData.value = true
    dataError.value = ''
    const form = new FormData()
    form.append('file', file)
    try {
      const { data } = await api.post('/data/upload', form)
      dataset.value = data
      isManual.value = false
      if (data.columnas_frecuencia.length) {
        selectedColumn.value = data.columnas_frecuencia[0]
      }
      trainResult.value = null
      predictResult.value = null
    } catch (e) {
      dataError.value = e.response?.data?.detail ?? e.message
    } finally {
      loadingData.value = false
    }
  }

  async function trainModels() {
    if (!selectedColumn.value || !selectedModels.value.length) return
    loadingTrain.value = true
    trainError.value = ''
    try {
      const payload = {
        columna_frecuencia: selectedColumn.value,
        modelos: selectedModels.value,
        config_polinomial: selectedModels.value.includes('polinomial')
          ? { grado: polyGrado.value }
          : null,
        config_mlp: selectedModels.value.includes('mlp')
          ? {
              capas_ocultas: mlpCapas.value.split(',').map(Number).filter(Boolean),
              activacion: mlpActivacion.value,
              max_iter: mlpMaxIter.value,
            }
          : null,
      }
      const { data } = await api.post('/models/train', payload)
      trainResult.value = data
      predictResult.value = null
    } catch (e) {
      trainError.value = e.response?.data?.detail ?? e.message
    } finally {
      loadingTrain.value = false
    }
  }

  async function runPredict() {
    loadingPredict.value = true
    try {
      const { data } = await api.post('/predict/', { longitud_cm: predictLength.value })
      predictResult.value = data
    } catch (e) {
      console.error(e)
    } finally {
      loadingPredict.value = false
    }
  }

  async function manualData(puntos, columnas) {
    loadingData.value = true
    dataError.value = ''
    try {
      const { data } = await api.post('/data/manual', { puntos, columnas })
      dataset.value = data
      isManual.value = true
      selectedColumn.value = columnas[0] ?? ''
      trainResult.value = null
      predictResult.value = null
    } catch (e) {
      dataError.value = e.response?.data?.detail ?? e.message
    } finally {
      loadingData.value = false
    }
  }

  async function downloadReport() {
    loadingReport.value = true
    reportError.value = ''
    try {
      const payload = {
        columna_frecuencia: selectedColumn.value,
        modelos: selectedModels.value,
        config_polinomial: selectedModels.value.includes('polinomial')
          ? { grado: polyGrado.value }
          : null,
      }
      const resp = await api.post('/report/', payload, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = 'reporte_cuerdas.pdf'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      reportError.value = e.response?.data?.detail ?? e.message
    } finally {
      loadingReport.value = false
    }
  }

  return {
    dataset, selectedColumn, loadingData, dataError, columnOptions, isManual,
    selectedModels, polyGrado, mlpCapas, mlpActivacion, mlpMaxIter,
    trainResult, loadingTrain, trainError, hasTrainResults, bestModel,
    predictLength, predictResult, loadingPredict,
    loadingReport, reportError,
    showLoadingOverlay, reload,
    fetchDataset, uploadCSV, manualData, trainModels, runPredict, downloadReport,
  }
})
