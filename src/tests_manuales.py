"""Script de pruebas manuales para validar los módulos principales.

Ejecutar desde la raíz del proyecto:
    python src/tests_manuales.py
"""

import sys
from pathlib import Path

# Forzar salida UTF-8 en terminales Windows (CP1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Asegurar que src/ esté en el path
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# ═══════════════════════════════════════════════════════════════════════════
# Utilidades de formato para consola
# ═══════════════════════════════════════════════════════════════════════════
_SEP = "=" * 60
_OK  = "  [OK] "
_FAIL = "  [!!] "


def _encabezado(titulo: str) -> None:
    print(f"\n{_SEP}")
    print(f"  {titulo}")
    print(_SEP)


def _exito(msg: str) -> None:
    print(f"{_OK}{msg}")


def _error(msg: str) -> None:
    print(f"{_FAIL}{msg}")


# ═══════════════════════════════════════════════════════════════════════════
# 1. Prueba de Carga de Datos
# ═══════════════════════════════════════════════════════════════════════════
def prueba_carga_datos(columna_frecuencia: str = "Hz Spectroid (Android)") -> tuple | None:
    """Carga el CSV, muestra las primeras filas y valida tipos de dato.

    Returns
    -------
    tuple[np.ndarray, np.ndarray] | None
        (X, y) si la prueba fue exitosa, None si falló.
    """
    _encabezado("1. PRUEBA DE CARGA DE DATOS (data_loader)")

    try:
        import numpy as np
        import pandas as pd
        from data_loader import cargar_datos, _DEFAULT_DATASET_PATH, COLUMNA_LONGITUD, COLUMNAS_FRECUENCIA

        print(f"  Archivo CSV : {_DEFAULT_DATASET_PATH}")
        print(f"  Columna X   : {COLUMNA_LONGITUD}")
        print(f"  Columna y   : {columna_frecuencia}")
        print(f"  Columnas disponibles de frecuencia: {COLUMNAS_FRECUENCIA}\n")

        # Mostrar vista previa del CSV crudo
        df = pd.read_csv(_DEFAULT_DATASET_PATH)
        print("  Primeras 5 filas del dataset:")
        print(df.head().to_string(index=False).replace("\n", "\n  "))
        print(f"\n  Tipos de dato originales:")
        for col, dtype in df.dtypes.items():
            print(f"    {col}: {dtype}")

        # Cargar datos limpios
        X, y = cargar_datos(columna_frecuencia)

        print(f"\n  Después de la limpieza:")
        print(f"    X (Longitud)   → dtype: {X.dtype}, shape: {X.shape}")
        print(f"    y ({columna_frecuencia}) → dtype: {y.dtype}, shape: {y.shape}")

        # Validar tipos
        assert X.dtype == np.float64, f"X no es float64, es {X.dtype}"
        assert y.dtype == np.float64, f"y no es float64, es {y.dtype}"

        _exito("Carga de datos exitosa. Ambas columnas son float64.")
        return X, y

    except FileNotFoundError as exc:
        _error(f"Archivo no encontrado: {exc}")
    except KeyError as exc:
        _error(f"Columna no encontrada: {exc}")
    except AssertionError as exc:
        _error(f"Validación de tipo fallida: {exc}")
    except Exception as exc:
        _error(f"Error inesperado en data_loader: {type(exc).__name__}: {exc}")

    return None


# ═══════════════════════════════════════════════════════════════════════════
# 2. Prueba de Modelado
# ═══════════════════════════════════════════════════════════════════════════
def prueba_modelado(X, y, grado: int = 2) -> bool:
    """Entrena un polinomio y una MLP, imprime métricas.

    Returns
    -------
    bool
        True si ambos modelos se entrenaron correctamente.
    """
    _encabezado("2. PRUEBA DE MODELADO (models)")
    exito = True

    # --- Regresión polinomial ---
    try:
        from models import ModeladorMaestro

        modelador = ModeladorMaestro()

        print(f"  Entrenando regresión polinomial de grado {grado}...")
        res_poly = modelador.ajuste_polinomial(X, y, grado=grado)

        print(f"    MSE : {res_poly.mse:.6f}")
        print(f"    R²  : {res_poly.r2:.6f}")
        _exito(f"Regresión polinomial (grado {grado}) entrenada correctamente.")

    except Exception as exc:
        _error(f"Fallo en ajuste_polinomial: {type(exc).__name__}: {exc}")
        exito = False

    # --- Red Neuronal MLP ---
    try:
        from models import ModeladorMaestro

        modelador = ModeladorMaestro()

        print(f"\n  Entrenando Red Neuronal MLP (10-10, relu, adam)...")
        res_mlp = modelador.red_neuronal_mlp(X, y)

        print(f"    MSE : {res_mlp.mse:.6f}")
        _exito("Red Neuronal MLP entrenada correctamente.")

    except Exception as exc:
        _error(f"Fallo en red_neuronal_mlp: {type(exc).__name__}: {exc}")
        exito = False

    return exito


# ═══════════════════════════════════════════════════════════════════════════
# 3. Prueba de Audio
# ═══════════════════════════════════════════════════════════════════════════
def prueba_audio(duracion: int = 3) -> bool:
    """Graba audio y detecta la frecuencia dominante.

    Returns
    -------
    bool
        True si se detectó una frecuencia válida.
    """
    _encabezado("3. PRUEBA DE AUDIO (audio_capture)")

    try:
        from audio_capture import AnalizadorAudio, AudioNoDisponibleError

        analizador = AnalizadorAudio()

        print(f"  Duración de grabación: {duracion} segundos")
        print(f"  Frecuencia de muestreo: 44100 Hz\n")
        print("  *** Por favor, silbe o toque una cuerda ahora ***\n")

        frecuencia = analizador.capturar_frecuencia(duracion=duracion, fs=44100)

        print(f"  Frecuencia dominante detectada: {frecuencia:.2f} Hz")
        _exito("Captura de audio exitosa.")
        return True

    except AudioNoDisponibleError as exc:
        _error(f"Micrófono no disponible: {exc}")
    except ValueError as exc:
        _error(f"Señal insuficiente: {exc}")
    except Exception as exc:
        _error(f"Error inesperado en audio_capture: {type(exc).__name__}: {exc}")

    return False


# ═══════════════════════════════════════════════════════════════════════════
# Ejecución principal
# ═══════════════════════════════════════════════════════════════════════════
def main() -> None:
    separador = "#" * 60
    print(f"\n{separador}")
    print("  PRUEBAS MANUALES - Modelado de Cuerdas Acusticas")
    print(f"{separador}")

    resultados: dict[str, bool] = {}

    # 1. Carga de datos
    datos = prueba_carga_datos()
    resultados["data_loader"] = datos is not None

    # 2. Modelado (solo si la carga fue exitosa)
    if datos is not None:
        X, y = datos
        resultados["models"] = prueba_modelado(X, y, grado=2)
    else:
        _encabezado("2. PRUEBA DE MODELADO (models)")
        _error("Omitida - la carga de datos fallo previamente.")
        resultados["models"] = False

    # 3. Audio
    resultados["audio_capture"] = prueba_audio(duracion=3)

    # --- Resumen final ---
    _encabezado("RESUMEN DE PRUEBAS")
    todas_ok = True
    for modulo, ok in resultados.items():
        estado = "PASO [OK]" if ok else "FALLO [!!]"
        print(f"  {modulo:<20} -> {estado}")
        if not ok:
            todas_ok = False

    print(f"\n{_SEP}")
    if todas_ok:
        print("  Todas las pruebas pasaron correctamente.")
    else:
        print("  Algunas pruebas fallaron. Revisa los mensajes de arriba.")
    print(f"{_SEP}\n")


if __name__ == "__main__":
    main()
