"""Módulo de carga y limpieza de datos para el modelado de cuerdas acústicas."""

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

# Ruta base del proyecto (un nivel arriba de backend/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DATASET_PATH = _PROJECT_ROOT / "data" / "datos_guitarra.csv"

COLUMNA_LONGITUD = "Longitud (cm)"
COLUMNA_TRASTE = "Traste"

COLUMNAS_FRECUENCIA = [
    "Hz Spectroid (Android)",
    "Hz Spectroid (Iphone)",
    "Hz Phyphox (Android)",
    "Hz Phyphox (Iphone)",
    "Hz Decivel X (Android)",
    "Hz Decivel X (iPhone)",
]


def _limpiar_columna_numerica(serie: pd.Series) -> pd.Series:
    serie = serie.astype(str).str.strip()
    serie = serie.str.replace(",", ".", regex=False)
    return pd.to_numeric(serie, errors="coerce")


def cargar_datos(
    columna_frecuencia: str,
    ruta_csv: Path | str = _DEFAULT_DATASET_PATH,
) -> Tuple[np.ndarray, np.ndarray]:
    ruta_csv = Path(ruta_csv)
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el dataset en: {ruta_csv}")
    df = pd.read_csv(ruta_csv)
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    columnas_faltantes = {COLUMNA_LONGITUD, columna_frecuencia} - set(df.columns)
    if columnas_faltantes:
        raise KeyError(
            f"Columnas no encontradas: {columnas_faltantes}. Disponibles: {list(df.columns)}"
        )
    df[COLUMNA_LONGITUD] = _limpiar_columna_numerica(df[COLUMNA_LONGITUD])
    df[columna_frecuencia] = _limpiar_columna_numerica(df[columna_frecuencia])
    df = df[[COLUMNA_LONGITUD, columna_frecuencia]].dropna()
    if df.empty:
        raise ValueError("No quedan registros válidos tras la limpieza de datos.")
    return df[COLUMNA_LONGITUD].to_numpy(dtype=np.float64), df[
        columna_frecuencia
    ].to_numpy(dtype=np.float64)


def cargar_dataframe(ruta_csv: Path | str = _DEFAULT_DATASET_PATH) -> pd.DataFrame:
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
    df_original: pd.DataFrame, longitud_estimada: float
) -> dict:
    for col in (COLUMNA_TRASTE, COLUMNA_LONGITUD):
        if col not in df_original.columns:
            raise KeyError(f"Columna '{col}' no encontrada.")
    df = df_original[[COLUMNA_TRASTE, COLUMNA_LONGITUD]].dropna()
    idx = (df[COLUMNA_LONGITUD] - longitud_estimada).abs().idxmin()
    return {
        "Traste": int(df.loc[idx, COLUMNA_TRASTE]),
        "Longitud Real": float(df.loc[idx, COLUMNA_LONGITUD]),
    }


def obtener_traste_por_frecuencia(
    df_original: pd.DataFrame, frecuencia_capturada: float, columna_frecuencia: str
) -> dict:
    for col in (COLUMNA_TRASTE, COLUMNA_LONGITUD, columna_frecuencia):
        if col not in df_original.columns:
            raise KeyError(f"Columna '{col}' no encontrada.")
    df = df_original[[COLUMNA_TRASTE, COLUMNA_LONGITUD, columna_frecuencia]].dropna()
    idx = (df[columna_frecuencia] - frecuencia_capturada).abs().idxmin()
    return {
        "Traste": int(df.loc[idx, COLUMNA_TRASTE]),
        "Longitud Real": float(df.loc[idx, COLUMNA_LONGITUD]),
        "Frecuencia Real": float(df.loc[idx, columna_frecuencia]),
    }
