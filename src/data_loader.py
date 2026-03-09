"""Módulo de carga y limpieza de datos para el modelado de cuerdas acústicas."""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

# Ruta base del proyecto (dos niveles arriba de src/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DATASET_PATH = _PROJECT_ROOT / "data" / "datos_guitarra.csv"

COLUMNA_LONGITUD = "Longitud (cm)"

# Columnas de frecuencia disponibles en el dataset
COLUMNAS_FRECUENCIA = [
    "Hz Spectroid (Android)",
    "Hz Spectroid (Iphone)",
    "Hz Phyphox (Android)",
    "Hz Phyphox (Iphone)",
    "Hz Decivel X (Android)",
    "Hz Decivel X (iPhone)",
]


def _limpiar_columna_numerica(serie: pd.Series) -> pd.Series:
    """Convierte una serie a float, manejando comas decimales y valores nulos.

    Parameters
    ----------
    serie : pd.Series
        Serie con valores numéricos posiblemente mal formateados.

    Returns
    -------
    pd.Series
        Serie convertida a float con nulos propagados.
    """
    serie = serie.astype(str).str.strip()
    serie = serie.str.replace(",", ".", regex=False)
    return pd.to_numeric(serie, errors="coerce")


def cargar_datos(
    columna_frecuencia: str,
    ruta_csv: Path | str = _DEFAULT_DATASET_PATH,
) -> Tuple[np.ndarray, np.ndarray]:
    """Carga el dataset de guitarra y devuelve X (Longitud) e y (frecuencia).

    Parameters
    ----------
    columna_frecuencia : str
        Nombre de la columna de frecuencia a usar como variable objetivo
        (ej. ``'Spectroid_Android'``).
    ruta_csv : Path | str, optional
        Ruta al archivo CSV. Por defecto apunta a ``data/dataset_guitarra.csv``.

    Returns
    -------
    X : np.ndarray
        Arreglo 1-D con los valores de longitud.
    y : np.ndarray
        Arreglo 1-D con los valores de frecuencia seleccionados.

    Raises
    ------
    FileNotFoundError
        Si el archivo CSV no existe en la ruta indicada.
    KeyError
        Si ``columna_frecuencia`` o ``'Longitud'`` no existen en el dataset.
    ValueError
        Si después de limpiar los datos no quedan registros válidos.
    """
    ruta_csv = Path(ruta_csv)
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el dataset en: {ruta_csv}")

    df = pd.read_csv(ruta_csv)

    # Eliminar columnas completamente vacías o sin nombre (artefactos del CSV)
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    columnas_requeridas = {COLUMNA_LONGITUD, columna_frecuencia}
    columnas_faltantes = columnas_requeridas - set(df.columns)
    if columnas_faltantes:
        raise KeyError(
            f"Columnas no encontradas en el dataset: {columnas_faltantes}. "
            f"Columnas disponibles: {list(df.columns)}"
        )

    df[COLUMNA_LONGITUD] = _limpiar_columna_numerica(df[COLUMNA_LONGITUD])
    df[columna_frecuencia] = _limpiar_columna_numerica(df[columna_frecuencia])

    df = df[[COLUMNA_LONGITUD, columna_frecuencia]].dropna()

    if df.empty:
        raise ValueError(
            "No quedan registros válidos tras la limpieza de datos. "
            "Revisa el formato del CSV."
        )

    X = df[COLUMNA_LONGITUD].to_numpy(dtype=np.float64)
    y = df[columna_frecuencia].to_numpy(dtype=np.float64)

    return X, y


COLUMNA_TRASTE = "Traste"


def cargar_dataframe(
    ruta_csv: Path | str = _DEFAULT_DATASET_PATH,
) -> pd.DataFrame:
    """Carga el CSV completo como DataFrame limpio.

    Parameters
    ----------
    ruta_csv : Path | str, optional
        Ruta al archivo CSV.

    Returns
    -------
    pd.DataFrame
        DataFrame con columnas vacías eliminadas y tipos numéricos limpios.
    """
    ruta_csv = Path(ruta_csv)
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el dataset en: {ruta_csv}")

    df = pd.read_csv(ruta_csv)
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    if COLUMNA_LONGITUD in df.columns:
        df[COLUMNA_LONGITUD] = _limpiar_columna_numerica(df[COLUMNA_LONGITUD])
    if COLUMNA_TRASTE in df.columns:
        df[COLUMNA_TRASTE] = _limpiar_columna_numerica(df[COLUMNA_TRASTE])

    return df


def obtener_traste_mas_cercano(
    df_original: pd.DataFrame,
    longitud_estimada: float,
) -> dict:
    """Encuentra el traste cuya longitud real es la más cercana a la estimada.

    Parameters
    ----------
    df_original : pd.DataFrame
        DataFrame completo con columnas ``'Traste'`` y ``'Longitud (cm)'``.
    longitud_estimada : float
        Longitud en cm predicha por el modelo inverso.

    Returns
    -------
    dict
        Diccionario con claves ``'Traste'`` (int) y ``'Longitud Real'`` (float).

    Raises
    ------
    KeyError
        Si las columnas requeridas no existen en el DataFrame.
    """
    for col in (COLUMNA_TRASTE, COLUMNA_LONGITUD):
        if col not in df_original.columns:
            raise KeyError(f"Columna '{col}' no encontrada en el DataFrame.")

    df = df_original[[COLUMNA_TRASTE, COLUMNA_LONGITUD]].dropna()
    diferencias = (df[COLUMNA_LONGITUD] - longitud_estimada).abs()
    idx_minimo = diferencias.idxmin()

    return {
        "Traste": int(df.loc[idx_minimo, COLUMNA_TRASTE]),
        "Longitud Real": float(df.loc[idx_minimo, COLUMNA_LONGITUD]),
    }
