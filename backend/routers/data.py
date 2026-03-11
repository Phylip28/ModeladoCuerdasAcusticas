"""Router de datos: carga y exposición del dataset CSV."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import numpy as np

from backend.data_loader import (
    cargar_dataframe,
    COLUMNAS_FRECUENCIA,
    COLUMNA_LONGITUD,
    _DEFAULT_DATASET_PATH,
)
from backend.schemas import DatasetResponse, PuntoDataset, ManualDataRequest

router = APIRouter(prefix="/data", tags=["dataset"])

# Estado en memoria del dataset activo (se puede reemplazar con un CSV subido)
_df_cache: pd.DataFrame | None = None
_active_path: Path = _DEFAULT_DATASET_PATH
_is_manual: bool = False  # True cuando los datos vienen de entrada manual


def get_active_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = cargar_dataframe(_active_path)
    return _df_cache


@router.get("/", response_model=DatasetResponse)
def obtener_dataset():
    """Devuelve el dataset activo con todas las columnas de frecuencia."""
    try:
        df = get_active_df()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Use ALL non-structural columns (supports both CSV and manual entry)
    cols_disponibles = [
        c for c in df.columns if c not in ("Traste", COLUMNA_LONGITUD)
    ]
    # For the default CSV, prefer known frequency columns in their original order
    if not _is_manual:
        ordered = [c for c in COLUMNAS_FRECUENCIA if c in df.columns]
        extras = [c for c in cols_disponibles if c not in ordered]
        cols_disponibles = ordered + extras

    puntos: list[PuntoDataset] = []
    for _, row in df.iterrows():
        freqs: dict[str, float | None] = {}
        for col in cols_disponibles:
            v = row.get(col)
            freqs[col] = None if (v is None or pd.isna(v)) else float(v)
        puntos.append(
            PuntoDataset(
                traste=int(row["Traste"]) if "Traste" in df.columns else 0,
                longitud_cm=float(row[COLUMNA_LONGITUD]),
                frecuencias=freqs,
            )
        )

    return DatasetResponse(
        columnas_frecuencia=cols_disponibles,
        puntos=puntos,
        total=len(puntos),
        is_manual=_is_manual,
    )


@router.post("/upload", response_model=DatasetResponse)
async def subir_csv(file: UploadFile = File(...)):
    """Sube un CSV personalizado y lo usa como dataset activo. Valida el esquema."""
    global _df_cache, _active_path, _is_manual

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .csv")

    content = await file.read()
    import io

    try:
        df = pd.read_csv(io.BytesIO(content))
        df = df.dropna(axis=1, how="all")
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error al parsear CSV: {e}")

    # ── Validación de esquema ────────────────────────────────────────────────
    if COLUMNA_LONGITUD not in df.columns:
        raise HTTPException(
            status_code=422,
            detail=(
                f"CSV inválido: falta la columna obligatoria '{COLUMNA_LONGITUD}'. "
                f"Columnas encontradas: {list(df.columns)}"
            ),
        )

    cols_extra = [c for c in df.columns if c not in ("Traste", COLUMNA_LONGITUD)]
    if not cols_extra:
        raise HTTPException(
            status_code=422,
            detail=(
                f"CSV inválido: no se encontró ninguna columna de frecuencia. "
                f"El archivo debe tener al menos una columna además de '{COLUMNA_LONGITUD}'."
            ),
        )

    # Intentar parsear longitud_cm; si falla el dataset es inútil
    try:
        df[COLUMNA_LONGITUD] = pd.to_numeric(df[COLUMNA_LONGITUD], errors="raise")
    except Exception:
        raise HTTPException(
            status_code=422,
            detail=f"CSV inválido: la columna '{COLUMNA_LONGITUD}' contiene valores no numéricos.",
        )

    df_valido = df.dropna(subset=[COLUMNA_LONGITUD])
    if len(df_valido) < 3:
        raise HTTPException(
            status_code=422,
            detail="CSV inválido: se requieren al menos 3 filas con datos de longitud válidos.",
        )
    # ── Fin validación ────────────────────────────────────────────────────────

    _df_cache = df_valido.reset_index(drop=True)
    _is_manual = False

    puntos: list[PuntoDataset] = []
    for _, row in _df_cache.iterrows():
        freqs = {
            col: (None if pd.isna(row.get(col)) else float(row[col]))
            for col in cols_extra
        }
        puntos.append(
            PuntoDataset(
                traste=int(row["Traste"]) if "Traste" in _df_cache.columns else 0,
                longitud_cm=float(row[COLUMNA_LONGITUD]),
                frecuencias=freqs,
            )
        )

    return DatasetResponse(
        columnas_frecuencia=cols_extra,
        puntos=puntos,
        total=len(puntos),
        is_manual=False,
    )


@router.post("/manual", response_model=DatasetResponse)
def ingresar_manual(req: ManualDataRequest):
    """Reemplaza el dataset activo con puntos ingresados manualmente (soporte multi-columna)."""
    global _df_cache, _is_manual

    if len(req.puntos) < 3:
        raise HTTPException(
            status_code=422,
            detail="Se requieren al menos 3 puntos para poder entrenar los modelos.",
        )

    if not req.columnas:
        raise HTTPException(
            status_code=422, detail="Debe definirse al menos una columna de frecuencia."
        )

    rows = []
    for p in req.puntos:
        row: dict = {COLUMNA_LONGITUD: p.longitud_cm}
        if p.traste is not None:
            row["Traste"] = p.traste
        for col in req.columnas:
            row[col] = p.frecuencias.get(col)
        rows.append(row)

    _df_cache = pd.DataFrame(rows)
    _is_manual = True

    puntos_out: list[PuntoDataset] = [
        PuntoDataset(
            traste=p.traste if p.traste is not None else 0,
            longitud_cm=p.longitud_cm,
            frecuencias={col: p.frecuencias.get(col) for col in req.columnas},
        )
        for p in req.puntos
    ]

    return DatasetResponse(
        columnas_frecuencia=req.columnas,
        puntos=puntos_out,
        total=len(puntos_out),
        is_manual=True,
    )
