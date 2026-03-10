"""Esquemas Pydantic para la API REST del Modelado de Cuerdas Acústicas."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ─── Datos ─────────────────────────────────────────────────────────────────


class PuntoDataset(BaseModel):
    traste: int
    longitud_cm: float
    frecuencias: dict[str, Optional[float]]


class DatasetResponse(BaseModel):
    columnas_frecuencia: list[str]
    puntos: list[PuntoDataset]
    total: int
    is_manual: bool = False


# ─── Entrada manual ─────────────────────────────────────────────────────────


class PuntoManual(BaseModel):
    traste: Optional[int] = None
    longitud_cm: float
    frecuencias: dict[str, Optional[float]]  # columna -> valor


class ManualDataRequest(BaseModel):
    puntos: list[PuntoManual]
    columnas: list[str]  # nombres de columnas en orden


# ─── Entrenamiento ──────────────────────────────────────────────────────────


class ConfigPolinomial(BaseModel):
    grado: int = Field(default=2, ge=1, le=5)


class ConfigMLP(BaseModel):
    capas_ocultas: list[int] = Field(default=[10, 10])
    activacion: str = Field(default="relu")
    max_iter: int = Field(default=5000)


class TrainRequest(BaseModel):
    columna_frecuencia: str
    modelos: list[str] = Field(
        description="Lista de modelos a entrenar: 'polinomial', 'mlp', 'svr'"
    )
    config_polinomial: Optional[ConfigPolinomial] = None
    config_mlp: Optional[ConfigMLP] = None


class CurvaAjuste(BaseModel):
    longitudes: list[float]
    frecuencias_pred: list[float]


class MetricasModelo(BaseModel):
    mse: float
    r2: Optional[float] = None
    mae: float


class ResultadoModelo(BaseModel):
    nombre: str
    etiqueta: str
    metricas: MetricasModelo
    curva_ajuste: CurvaAjuste
    residuos: list[float]
    ecuacion: Optional[str] = None
    loss_curve: Optional[list[float]] = None


class TrainResponse(BaseModel):
    columna_frecuencia: str
    longitudes_originales: list[float]
    frecuencias_originales: list[float]
    resultados: list[ResultadoModelo]


# ─── Predicción ─────────────────────────────────────────────────────────────


class PredictRequest(BaseModel):
    longitud_cm: float = Field(gt=0, description="Longitud de cuerda en cm")


class PrediccionModelo(BaseModel):
    nombre: str
    etiqueta: str
    frecuencia_hz: float
    confianza: Optional[str] = None


class PredictResponse(BaseModel):
    longitud_cm: float
    predicciones: list[PrediccionModelo]
    mejor_modelo: str


# ─── Reporte ────────────────────────────────────────────────────────────────


class ReportRequest(BaseModel):
    columna_frecuencia: str
    modelos: list[str]
    config_polinomial: Optional[ConfigPolinomial] = None
    config_mlp: Optional[ConfigMLP] = None
