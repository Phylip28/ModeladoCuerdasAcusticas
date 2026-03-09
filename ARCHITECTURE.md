# Arquitectura del Proyecto

## 📦 Estructura General

```
ModeladoCuerdasAcusticas/
├── src/
│   ├── main_app.py               ← Punto de entrada (GUI CustomTkinter)
│   ├── data_loader.py            ← Carga y limpieza de datos
│   ├── models.py                 ← Modelos ML (Polinomial, MLP, Inverso)
│   ├── audio_capture.py          ← Captura FFT y detección de frecuencia
│   ├── report_generator.py       ← Generación de PDF con fpdf2
│   └── tests_manuales.py         ← Suite de pruebas sin GUI
├── data/
│   └── datos_guitarra.csv        ← Dataset real
├── reports/                       ← Reportes PDF generados
├── requirements.txt
├── README.md
├── SETUP.md
└── ARCHITECTURE.md (este archivo)
```

---

## 🔗 Flujo de Datos

```
datos_guitarra.csv
        ↓
   data_loader.py
        ↓
   (X, y, DataFrame)
        ↓
   ┌────────────────────┐
   │   models.py        │
   ├────────────────────┤
   │ - Polinomio (grado 3)
   │ - MLP (10-10)      │
   │ - Modelo Inverso   │
   └────────────────────┘
        ↓
   ┌────────────────────┐
   │ Entrenamiento OK   │
   └────────────────────┘
        ↓
   ┌──────────────────────────────┐
   │   main_app.py (GUI)          │
   ├──────────────────────────────┤
   │ • Pestaña "Visualización"    │
   │   → matplotlib graph         │
   │ • Pestaña "Entrada de Datos" │
   │   → audio_capture            │
   │   → Inverso (Hz → cm)        │
   │   → obtener_traste_cercano   │
   │ • Pestaña "Resultados"       │
   │   → Mostrar métricas         │
   └──────────────────────────────┘
        ↓
   report_generator.py
        ↓
   reporte_*.pdf
```

---

## 📊 Módulos Principales

### 1. **data_loader.py** (Responsabilidad: Carga de datos)
```
Funciones públicas:
├── cargar_datos(columna_frecuencia) → (X, y)
│   └─ Lee CSV, limpia, retorna arrays de numpy
├── cargar_dataframe() → DataFrame
│   └─ Carga todo el CSV para búsqueda de trastes
└── obtener_traste_mas_cercano(df, longitud_estimada) → dict
    └─ Busca el traste cuya longitud es más cercana

Variables:
├── COLUMNA_LONGITUD = "Longitud (cm)"
└── COLUMNAS_FRECUENCIA = [lista de 6 columnas disponibles]
```

### 2. **models.py** (Responsabilidad: Modelado ML)
```
Clases:
├── ResultadoPolinomial (dataclass)
│   ├── modelo: Pipeline
│   ├── mse: float
│   └── r2: float
├── ResultadoMLP (dataclass)
│   ├── modelo: Pipeline
│   ├── mse: float
│   └── loss_curve: list[float]  ← Curva de convergencia
├── ResultadoInverso (dataclass)
│   ├── modelo: Pipeline
│   └── mse: float
└── ModeladorMaestro
    ├── _validar_entradas(X, y) → (X, y)  [static]
    ├── ajuste_polinomial(X, y, grado) → ResultadoPolinomial
    ├── red_neuronal_mlp(X, y) → ResultadoMLP
    └── crear_modelo_inverso(X_freq, y_long) → ResultadoInverso
```

### 3. **audio_capture.py** (Responsabilidad: Detección de frecuencia)
```
Clases:
└── AnalizadorAudio
    ├── _verificar_microfono() [static]
    │   └─ Lanza AudioNoDisponibleError si no hay micrófono
    ├── _grabar(duracion, fs) → signal (1-D array)
    │   └─ Usa sounddevice para capturar mono
    ├── _detectar_frecuencia(signal, fs) → frecuencia_hz
    │   └─ Aplica Hanning FFT + detecta pico dominante
    └── capturar_frecuencia(duracion=6, fs=44100) → float
        └─ Orquesta: grabar → detectar frecuencia

Excepciones:
└── AudioNoDisponibleError
```

### 4. **report_generator.py** (Responsabilidad: Generación de PDF)
```
Funciones:
├── _agregar_portada(pdf)
│   └─ Título + integrantes
├── _agregar_tabla_errores(pdf, filas)
│   └─ MSE y R² comparativos
├── _agregar_ecuaciones(pdf, ecuaciones)
│   └─ Ecuaciones polinomiales extraídas
├── _agregar_grafico(pdf, ruta_grafico)
│   └─ Gráfico comparativo de modelos
├── _generar_grafico_loss_curve(loss_curve, dir) → Path
│   └─ Genera PNG de convergencia MLP
├── _agregar_loss_curve(pdf, ruta_loss)
│   └─ Inserta gráfica de convergencia
└── generar_pdf_reporte(..., loss_curve=None) → Path
    └─ Orquesta todo y genera PDF final

(Usa matplotlib backend "Agg" sin GUI)
```

### 5. **main_app.py** (Responsabilidad: Interfaz y orquestación)
```
Clase:
└── AplicacionPrincipal (ctk.CTk)
    ├─ _construir_layout()
    │  ├─ _crear_panel_lateral()
    │  │  └─ Selección de columna + grado + botones
    │  └─ _crear_area_central()
    │     ├─ Tab "Entrada de Datos"
    │     ├─ Tab "Visualización"
    │     └─ Tab "Resultados"
    ├─ _ejecutar_modelos()
    │  └─ Carga datos, entrena poly/MLP/inverso
    ├─ _capturar_audio() → hilo
    │  └─ _hilo_captura() → frecuencia → longitud → traste
    ├─ _actualizar_grafico()
    │  └─ Dibuja scatter plot + 2 curvas
    ├─ _actualizar_resultados()
    │  └─ Rellena textbox con métricas/ecuaciones
    └─ _generar_pdf()
       └─ Orquesta report_generator

Estado interno:
├── _X, _y: arrays de datos
├── _resultado_poly, _resultado_mlp, _resultado_inverso
├── _df_original: DataFrame completo
└── _ruta_grafico: Path al PNG
```

---

## 🔄 Flujos Principales

### Flujo A: Entrenar Modelos
```
Usuario pulsa "▶ Ejecutar Modelos"
    ↓
main_app._ejecutar_modelos()
    ↓
data_loader.cargar_datos()          ← Lee CSV
    ↓
models.ModeladorMaestro:
  - ajuste_polinomial(X, y, 3)      ← Regresión clásica
  - red_neuronal_mlp(X, y)          ← Red neuronal
  - crear_modelo_inverso(y, X)      ← Hz → cm
    ↓
data_loader.cargar_dataframe()      ← Para búsqueda de trastes
    ↓
main_app._actualizar_grafico()      ← Matplotlib
main_app._actualizar_resultados()   ← Tabla métricas
```

### Flujo B: Capturar Audio
```
Usuario pulsa "🎤 Capturar Frecuencia"
    ↓
main_app._capturar_audio()
    ↓
threading.Thread(_hilo_captura)     ← No bloquea UI
    ↓
audio_capture.AnalizadorAudio.capturar_frecuencia(6s)
    ↓
sounddevice.rec()                   ← Graba 6s a 44100 Hz
  → np.hanning window                ← Suaviza bordes
  → scipy.fft.rfft                   ← Espectro magnitud
  → np.argmax(espectro)              ← Pico dominante
    ↓
main_app._mostrar_resultado_completo()
  → modelo_inverso.predict(Hz)       ← Predice longitud
  → data_loader.obtener_traste_mas_cercano()  ← Busca traste
  → Actualiza UI con Traste + longitud
```

### Flujo C: Generar PDF
```
Usuario pulsa "📄 Generar Informe PDF"
    ↓
main_app._generar_pdf()
    ↓
report_generator.generar_pdf_reporte()
    ↓
_PDFReporte()                       ← Subclase de FPDF
  ├─ _agregar_portada()
  ├─ _agregar_tabla_errores()
  ├─ _agregar_ecuaciones()
  ├─ _agregar_grafico()
  ├─ _generar_grafico_loss_curve()
  └─ _agregar_loss_curve()
    ↓
PDF guardado en reports/
    ↓
os.startfile() → Abre en PDF reader
```

---

## 🛡️ Principios de Diseño

### Separación de Responsabilidades (SRP)
- `data_loader`: Solo carga y limpieza
- `models`: Solo ML (sin UI)
- `audio_capture`: Solo captura de audio (sin UI)
- `report_generator`: Solo PDF (sin UI)
- `main_app`: Solo UI y orquestación

### DRY (Don't Repeat Yourself)
- Validación de entradas centralizada en `_validar_entradas()`
- Limpieza de datos centralizada en `_limpiar_columna_numerica()`

### Manejo de Errores
- Excepciones específicas: `AudioNoDisponibleError`, `FileNotFoundError`, `KeyError`
- Try-except en puntos críticos (captura audio, carga CSV)

### Threading
- Captura de audio en hilo separado para no bloquear UI
- `self.after(0, callback)` para actualizar UI desde hilo

### Reproducibilidad
- `random_state=42` en todos los modelos ML
- Semillas fijas garantizan resultados consistentes

---

## 📈 Dependencias y por qué

| Librería | Rol | Razón |
|----------|-----|-------|
| `numpy` | Computación numérica | Arrays eficientes |
| `pandas` | Manipulación de data | Lee/limpia CSV |
| `scikit-learn` | Machine Learning | Polinomio + MLP + métricas |
| `scipy` | FFT | Análisis de frecuencia |
| `sounddevice` | Captura de audio | Micrófono multiplataforma |
| `fpdf2` | Generación de PDF | Reportes profesionales |
| `customtkinter` | GUI moderna | Interfaz oscura moderna |
| `matplotlib` | Visualización | Gráficos interactivos |

---

## 🔐 Integridad de Datos

- CSV se carga y limpia automáticamente
- Los modelos se entrenan en RAM (sin persistencia temporal)
- Los PDFs se generan sin sobrescribir usuarios existentes
- Validaciones en cada paso (tipos, dimensiones, filas vacías)

---

## 🚀 Posibles Mejoras Futuras

1. **Persistencia**: Guardar/cargar modelos entrenados (.pkl)
2. **Base de datos**: SQLite en lugar de CSV
3. **API REST**: Exponer modelos vía FastAPI
4. **Tests unitarios**: pytest + cobertura
5. **Logging**: logging.py para auditoría
6. **Caché**: Evitar reentrenamiento innecesario
7. **GPU**: Usar cupy en lugar de numpy (si disponible)

---

**Documento generado:** Marzo 9, 2026
