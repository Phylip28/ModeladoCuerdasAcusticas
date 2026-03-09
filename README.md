# Modelado de Cuerdas Acústicas

Aplicación de escritorio para modelar y analizar la relación entre la longitud de una cuerda de guitarra y su frecuencia fundamental usando regresión polinomial y redes neuronales artificiales.

## 📋 Requisitos Previos

- **Python 3.10+** (verificar con `python --version`)
- **pip** (gestor de paquetes de Python)
- **Micrófono conectado** (opcional, para captura de audio en vivo)
- **Git** (para clonar el repositorio)

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd ModeladoCuerdasAcusticas
```

O descargar el ZIP desde GitHub/GitLab y extraer.

### 2. Crear un entorno virtual (Recomendado)

```bash
python -m venv venv
```

**Activar el entorno virtual:**

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

- **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `numpy` - Computación numérica
- `pandas` - Manipulación de datos
- `scikit-learn` - Modelado de regresión y redes neuronales
- `scipy` - Análisis de Fourier
- `sounddevice` - Captura de audio
- `fpdf2` - Generación de reportes PDF
- `customtkinter` - Interfaz gráfica moderna
- `matplotlib` - Visualización de gráficos

## 📁 Estructura del Proyecto

```
ModeladoCuerdasAcusticas/
├── src/                          # Código fuente
│   ├── main_app.py              # Aplicación principal (GUI)
│   ├── data_loader.py           # Carga y limpieza de datos
│   ├── models.py                # Modelos de regresión (polinomial + MLP + inverso)
│   ├── audio_capture.py         # Captura de audio y detección de frecuencia
│   ├── report_generator.py      # Generación de reportes PDF
│   └── tests_manuales.py        # Pruebas sin GUI
├── data/
│   └── datos_guitarra.csv       # Dataset con mediciones reales
├── reports/                      # Reportes PDF generados
├── requirements.txt              # Dependencias del proyecto
├── README.md                     # Este archivo
└── LICENSE                       # MIT License
```

## ▶️ Ejecución

### Opción 1: GUI Completa (Recomendado)

```bash
python src/main_app.py
```

**Flujo de uso:**
1. Selecciona columna de frecuencia (dropdown)
2. Define grado del polinomio (por defecto 3)
3. Pulsa **"▶ Ejecutar Modelos"** para entrenar
4. Ve a pestañas para ver gráficos y resultados
5. En "Entrada de Datos", pulsa **"🎤 Capturar Frecuencia"** (6 segundos)
6. Toca una cuerda de guitarra cerca del micrófono
7. Verás el traste detectado y la longitud estimada
8. Genera el PDF con **"📄 Generar Informe PDF"**

### Opción 2: Pruebas Manuales (Sin GUI)

Valida que todos los módulos funcionen:

```bash
python src/tests_manuales.py
```

Prueba:
- ✓ Carga de datos
- ✓ Entrenamiento de modelos
- ✓ Captura de audio (grabará 3 segundos)

## 📊 Datos Esperados

El archivo `data/datos_guitarra.csv` debe contener:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `Traste` | int | Número de traste (0-19) |
| `Longitud (cm)` | float | Longitud de cuerda en cm |
| `Hz Spectroid (Android)` | float | Frecuencia medida con Spectroid |
| `Hz Phyphox (Android)` | float | Frecuencia medida con Phyphox |
| `Hz Spectroid (Iphone)` | float | Frecuencia medida con Spectroid iOS |
| `Hz Phyphox (Iphone)` | float | Frecuencia medida con Phyphox iOS |
| ... | float | Otras columnas de frecuencia |

**Columnas de frecuencia disponibles:**
- `Hz Spectroid (Android)`
- `Hz Spectroid (Iphone)`
- `Hz Phyphox (Android)`
- `Hz Phyphox (Iphone)`
- `Hz Decivel X (Android)`
- `Hz Decivel X (iPhone)`

## 🔍 Módulos Principales

### `data_loader.py`
- `cargar_datos()` - Carga X (longitud) e y (frecuencia)
- `cargar_dataframe()` - Carga DataFrame completo
- `obtener_traste_mas_cercano()` - Busca traste por longitud estimada

### `models.py`
- `ModeladorMaestro.ajuste_polinomial()` - Regresión polinomial
- `ModeladorMaestro.red_neuronal_mlp()` - Red neuronal (MLP)
- `ModeladorMaestro.crear_modelo_inverso()` - Modelo inverso (Hz → longitud)

### `audio_capture.py`
- `AnalizadorAudio.capturar_frecuencia()` - Captura audio y detecta frecuencia fundamental

### `report_generator.py`
- `generar_pdf_reporte()` - Genera PDF con gráficos, ecuaciones y convergencia

### `main_app.py`
- Aplicación GUI principal con 3 pestañas

## ⚠️ Notas Importantes para Colaboradores

1. **Asegúrate de usar Python 3.10+**
   ```bash
   python --version
   ```

2. **Usa siempre un entorno virtual** para evitar conflictos
   ```bash
   source venv/bin/activate  # Mac/Linux o venv\Scripts\activate en Windows
   ```

3. **Los datos deben estar en `data/datos_guitarra.csv`**
   - Si no existe, la carga de datos fallará
   - Verifica que el CSV esté en la ruta correcta

4. **El micrófono es opcional**
   - La GUI funciona sin micrófono (solo verás los gráficos)
   - Para capturar audio, conecta un micrófono funcionando

5. **Git workflow recomendado:**
   ```bash
   git pull origin main              # Descargar cambios
   pip install -r requirements.txt   # Actualizar dependencias si cambiaron
   python src/main_app.py            # Ejecutar
   ```

6. **No hacer commit de:**
   - Carpeta `venv/`
   - Carpeta `__pycache__/`
   - Archivos `.pyc`
   - Carpeta `.idea/` (IDE settings)
   - PDFs generados en `reports/`

   (Ya están en `.gitignore`)

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'customtkinter'` | Ejecutar `pip install -r requirements.txt` |
| `FileNotFoundError: datos_guitarra.csv` | Verificar que el archivo existe en `data/` |
| `AttributeError: '_tkinter.tkapp'` | Reiniciar la app, puede ser bug de threading |
| Micrófono no detectado | Verificar que sounddevice está instalado: `pip install sounddevice` |
| GPU issues (sklearn) | Ignorar, scikit-learn usa CPU por defecto (está bien) |

## 📝 Scripts Útiles

```bash
# Limpiar cache de Python
python -m py_compile src/*.py

# Ejecutar solo pruebas
python src/tests_manuales.py

# Ver columnas disponibles del CSV
python -c "import pandas as pd; df = pd.read_csv('data/datos_guitarra.csv'); print(df.columns.tolist())"
```

## 📄 Licencia

MIT License - Ver archivo `LICENSE`

## 👥 Colaboradores

- Juan Felipe Rendon Herrera

---

**Última actualización:** Marzo 9, 2026