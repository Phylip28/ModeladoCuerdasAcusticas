# Modelado de Cuerdas Acústicas

Aplicación web full-stack para modelar y analizar la relación entre la longitud de una cuerda de guitarra y su frecuencia fundamental. Usa una API REST en FastAPI (backend) y una SPA en Vue 3 + Vite (frontend) con 6 modelos de regresión: Polinomial, MLP, SVR, KNN, Árbol de Decisión y Random Forest.

---

## 📋 Requisitos Previos

| Herramienta | Versión mínima |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Phylip28/ModeladoCuerdasAcusticas.git
cd ModeladoCuerdasAcusticas
```

### 2. Backend — entorno Python

```bash
# Crear y activar entorno virtual
python -m venv .venv

# Linux / Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Frontend — dependencias Node

```bash
cd frontend
npm install
cd ..
```

---

## ▶️ Ejecución

Necesitas **dos terminales** abiertas simultáneamente, una para el backend y otra para el frontend.

### Terminal 1 — Backend (FastAPI)

Ejecutar **desde la raíz** del proyecto con el entorno virtual activo:

```bash
uvicorn backend.main:app --reload --port 8000
```

La API queda disponible en `http://localhost:8000`.  
Documentación interactiva (Swagger): `http://localhost:8000/docs`

### Terminal 2 — Frontend (Vite + Vue)

```bash
cd frontend
npm run dev
```

La aplicación queda disponible en `http://localhost:5173`.

> El frontend hace proxy automático de `/api/*` → `http://localhost:8000`, por lo que no necesitas configurar nada adicional.

---

## 📁 Estructura del Proyecto

```
ModeladoCuerdasAcusticas/
├── backend/                      # API REST (FastAPI)
│   ├── main.py                  # Punto de entrada de la API
│   ├── schemas.py               # Modelos Pydantic (request / response)
│   ├── models.py                # Lógica de entrenamiento de modelos
│   ├── report_generator.py      # Generación de reportes PDF
│   └── routers/
│       ├── data.py              # Endpoints de carga de datos
│       ├── train.py             # Endpoints de entrenamiento
│       ├── predict.py           # Endpoints de predicción
│       └── report.py            # Endpoint de generación de PDF
├── frontend/                     # SPA (Vue 3 + Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── DataPanel.vue    # Panel de carga y edición de datos
│   │   │   ├── ModelConfig.vue  # Configuración y entrenamiento de modelos
│   │   │   ├── ChartPanel.vue   # Panel de análisis y gráficas
│   │   │   ├── PredictPanel.vue # Panel de predicción interactiva
│   │   │   └── ReportPanel.vue  # Panel de reportes PDF
│   │   ├── stores/
│   │   │   └── labStore.js      # Estado global (Pinia)
│   │   ├── App.vue              # Componente raíz + navegación
│   │   └── style.css            # Tema oscuro osciloscópico
│   ├── vite.config.js           # Configuración Vite (proxy /api)
│   └── package.json
├── data/
│   └── datos_guitarra.csv       # Dataset con mediciones reales de guitarra
├── reports/                      # PDFs generados
├── requirements.txt              # Dependencias Python
└── README.md
```

---

## 🧑‍🔬 Flujo de Uso

1. **Datos** — Carga el CSV incluido, sube uno propio o ingresa puntos manualmente.
2. **Modelos** — Selecciona uno o varios modelos, ajusta sus parámetros y entrena.
3. **Análisis** — Visualiza las curvas de ajuste, residuos y métricas (R², MSE, MAE). Múltiples sesiones de entrenamiento quedan en el historial y puedes compararlas con el selector de sesión.
4. **Predicción** — Mueve el slider de longitud y predice la frecuencia con todos los modelos entrenados. Cada predicción queda guardada en el historial.
5. **Reportes** — Genera y descarga un PDF comparativo con gráficas y métricas.

---

## 📊 Dataset

El archivo `data/datos_guitarra.csv` contiene mediciones reales de una guitarra acústica:

| Columna | Tipo | Descripción |
|---|---|---|
| `Traste` | int | Número de traste (0–19) |
| `Longitud (cm)` | float | Longitud de cuerda vibrante en cm |
| `Hz Spectroid (Android)` | float | Frecuencia medida con Spectroid |
| `Hz Phyphox (Android)` | float | Frecuencia medida con Phyphox |
| `Hz Spectroid (Iphone)` | float | Frecuencia medida con Spectroid iOS |
| `Hz Phyphox (Iphone)` | float | Frecuencia medida con Phyphox iOS |

---

## 🐛 Troubleshooting

| Problema | Solución |
|---|---|
| `ModuleNotFoundError` al iniciar el backend | Activar el entorno virtual y ejecutar `pip install -r requirements.txt` |
| `Error: connect ECONNREFUSED localhost:8000` en el frontend | Asegurarse de que el backend está corriendo en el puerto 8000 |
| `FileNotFoundError: datos_guitarra.csv` | Verificar que el archivo existe en `data/` |
| Puerto 8000 ocupado | Cambiar el puerto: `uvicorn backend.main:app --reload --port 8001` y actualizar el proxy en `frontend/vite.config.js` |
| Puerto 5173 ocupado | Vite asignará el siguiente puerto disponible automáticamente |

---

## 📝 Comandos de referencia rápida

```bash
# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Iniciar backend
uvicorn backend.main:app --reload --port 8000

# Iniciar frontend (en otra terminal)
cd frontend && npm run dev

# Build de producción del frontend
cd frontend && npm run build

# Ver documentación de la API
xdg-open http://localhost:8000/docs  # Linux
open http://localhost:8000/docs      # Mac
```

---

## 📄 Licencia

MIT License — Ver archivo `LICENSE`

---

**Última actualización:** Marzo 10, 2026
