# Guía de Configuración Rápida para Colaboradores

## ⚡ Setup en 5 minutos

### Paso 1: Clonar el repositorio
```bash
git clone <URL>
cd ModeladoCuerdasAcusticas
```

### Paso 2: Crear entorno virtual
```bash
python -m venv venv
```

### Paso 3: Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Paso 4: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 5: Ejecutar la aplicación
```bash
python src/main_app.py
```

---

## ✅ Checklist Antes de Empezar

- [ ] Python 3.10+ instalado
- [ ] Git instalado
- [ ] Micrófono conectado (opcional, pero recomendado para las pruebas)
- [ ] Entorno virtual activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `data/datos_guitarra.csv` presente

---

## 🔄 Flujo de Trabajo Colaborativo

### Para actualizar cambios del repositorio:
```bash
git pull origin main
pip install -r requirements.txt  # En caso de nuevas dependencias
python src/main_app.py
```

### Antes de hacer push:
```bash
git status                       # Ver cambios
git add .
git commit -m "Descripción del cambio"
git push origin main
```

---

## 📱 Probando la Aplicación

### 1. Entrenar modelos (Requerido)
- Pulsa **"▶ Ejecutar Modelos"** en el panel lateral
- Espera a que terminen los entrenamientos (≈30s)

### 2. Ver gráficos
- Ve a la pestaña **"📊 Visualización"**
- Deberías ver datos reales vs polinomio vs MLP

### 3. Capturar audio (Opcional, requiere micrófono)
- Ve a **"📡 Entrada de Datos"**
- Pulsa **"🎤 Capturar Frecuencia"**
- Toca una cuerda de guitarra cerca del micrófono
- Verás el traste detectado

### 4. Generar PDF
- Pulsa **"📄 Generar Informe PDF"**
- Se abrirá automáticamente el PDF en tu navegador/lector

---

## ❌ Problemas Comunes

| Síntoma | Causa | Solución |
|---------|-------|----------|
| `ModuleNotFoundError` | Dependencias no instaladas | `pip install -r requirements.txt` |
| Archivo CSV no encontrado | Ruta incorrecta del archivo | Verifica `data/datos_guitarra.csv` existe |
| La app no abre | Entorno virtual no activado | Ejecuta `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Mac/Linux) |
| Micrófono no detectado | sounddevice no instalado | `pip install sounddevice` |
| Advertencia de convergencia | Normal en MLP | Solo una advertencia, el modelo funciona bien |

---

## 📞 Si necesitas ayuda

1. Revisa el `README.md` (documentación completa)
2. Ejecuta `python src/tests_manuales.py` para validar todo
3. Verifica que todas las dependencias están instaladas: `pip list`
4. Pregunta al equipo en el chat/issue tracker

---

**¡Listo! Ya deberías poder ejecutar `python src/main_app.py` sin problemas.**
