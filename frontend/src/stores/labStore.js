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
  const mlpEpocas = ref(500)
  const mlpUnidades = ref(10)
  const mlpLearningRate = ref('0.01')
  const mlpActivacion = ref('relu')
  const knnK = ref(2)
  const svrKernel = ref('rbf')
  const svrC = ref(1.0)
  const svrEpsilon = ref(0.1)
  const arbolProfundidad = ref(5)
  const bosqueEstimadores = ref(100)
  const bosqueProfundidad = ref(null)

  // ── Train results ─────────────────────────────────────────────────────────
  const trainHistory = ref([])      // list<TrainResponse>
  const loadingTrain = ref(false)
  const trainError = ref('')

  // ── Prediction ────────────────────────────────────────────────────────────
  const predictLength = ref(45)
  const predictResult = ref(null)   // PredictResponse
  const predictHistory = ref([])    // list<PredictEntry>
  const loadingPredict = ref(false)

  // ── Report ────────────────────────────────────────────────────────────────
  const loadingReport = ref(false)
  const reportError = ref('')
  const generatedReports = ref([])   // { url, filename, timestamp }

  // ── Computed ──────────────────────────────────────────────────────────────
  const columnOptions = computed(() =>
    dataset.value?.columnas_frecuencia ?? []
  )

  const trainResult = computed(() => trainHistory.value.at(-1) ?? null)

  const hasTrainResults = computed(() => trainHistory.value.length > 0)

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
      trainHistory.value = []
      predictResult.value = null
      predictHistory.value = []
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
              epocas: mlpEpocas.value,
              unidades: mlpUnidades.value,
              learning_rate: parseFloat(mlpLearningRate.value),
              activacion: mlpActivacion.value,
            }
          : null,
        config_svr: selectedModels.value.includes('svr')
          ? { kernel: svrKernel.value, C: svrC.value, epsilon: svrEpsilon.value }
          : null,
        config_knn: selectedModels.value.includes('knn')
          ? { n_vecinos: knnK.value }
          : null,
        config_arbol: selectedModels.value.includes('arbol')
          ? { max_profundidad: arbolProfundidad.value }
          : null,
        config_bosque: selectedModels.value.includes('bosque')
          ? { n_estimadores: bosqueEstimadores.value, max_profundidad: bosqueProfundidad.value }
          : null,
      }
      const { data } = await api.post('/models/train', payload)
      trainHistory.value.push(data)
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
      predictHistory.value.push({
        predict_id: Math.random().toString(16).slice(2, 10),
        timestamp: new Date().toLocaleTimeString('es-ES', {
          hour: '2-digit', minute: '2-digit', second: '2-digit',
        }),
        longitudes_originales: trainResult.value?.longitudes_originales ?? [],
        frecuencias_originales: trainResult.value?.frecuencias_originales ?? [],
        ...data,
      })
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
      trainHistory.value = []
      predictResult.value = null
      predictHistory.value = []
    } catch (e) {
      dataError.value = e.response?.data?.detail ?? e.message
    } finally {
      loadingData.value = false
    }
  }

  function deleteSession(sid) {
    const idx = trainHistory.value.findIndex((s) => s.session_id === sid)
    if (idx > -1) trainHistory.value.splice(idx, 1)
  }

  function deletePrediction(pid) {
    const idx = predictHistory.value.findIndex((p) => p.predict_id === pid)
    if (idx > -1) predictHistory.value.splice(idx, 1)
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
      const idx = generatedReports.value.length + 1
      const filename = `reporte_cuerdas_${idx}.pdf`
      const timestamp = new Date().toLocaleString('es-ES', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      })
      generatedReports.value.push({ url, filename, timestamp })
    } catch (e) {
      reportError.value = e.response?.data?.detail ?? e.message
    } finally {
      loadingReport.value = false
    }
  }

  function deleteReport(idx) {
    const rep = generatedReports.value[idx]
    if (rep) URL.revokeObjectURL(rep.url)
    generatedReports.value.splice(idx, 1)
  }

  return {
    dataset, selectedColumn, loadingData, dataError, columnOptions, isManual,
    selectedModels, polyGrado, mlpActivacion,
    mlpEpocas, mlpUnidades, mlpLearningRate,
    knnK, svrKernel, svrC, svrEpsilon, arbolProfundidad, bosqueEstimadores, bosqueProfundidad,
    trainHistory, trainResult, loadingTrain, trainError, hasTrainResults, bestModel,
    predictLength, predictResult, predictHistory, loadingPredict,
    loadingReport, reportError, generatedReports,
    showLoadingOverlay, reload,
    fetchDataset, uploadCSV, manualData, trainModels, runPredict, downloadReport, deleteReport, deleteSession, deletePrediction,
  }
})
