"""Esquemas Pydantic para la API REST del Modelado de Cuerdas Acústicas."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# Datos


class PuntoDataset(BaseModel):
    traste: int
    longitud_cm: float
    frecuencias: dict[str, Optional[float]]


class DatasetResponse(BaseModel):
    columnas_frecuencia: list[str]
    puntos: list[PuntoDataset]
    total: int
    is_manual: bool = False


# Entrada manual


class PuntoManual(BaseModel):
    traste: Optional[int] = None
    longitud_cm: float
    frecuencias: dict[str, Optional[float]]  # columna -> valor


class ManualDataRequest(BaseModel):
    puntos: list[PuntoManual]
    columnas: list[str]  # nombres de columnas en orden


# Entrenamiento


class ConfigPolinomial(BaseModel):
    grado: int = Field(default=2, ge=1, le=10)


class ConfigMLP(BaseModel):
    epocas: int = Field(default=500, ge=10)
    unidades: int = Field(default=10, ge=1, le=200)
    learning_rate: float = Field(default=0.01, gt=0)
    activacion: str = Field(default="relu")


class ConfigKNN(BaseModel):
    n_vecinos: int = Field(default=2, ge=1, le=50)


class ConfigSVR(BaseModel):
    kernel: str = Field(default="rbf")
    C: float = Field(default=1.0, gt=0)
    epsilon: float = Field(default=0.1, ge=0)


class ConfigArbol(BaseModel):
    max_profundidad: Optional[int] = Field(default=5)


class ConfigBosque(BaseModel):
    n_estimadores: int = Field(default=100, ge=10, le=500)
    max_profundidad: Optional[int] = Field(default=None)


class TrainRequest(BaseModel):
    columna_frecuencia: str
    modelos: list[str] = Field(
        description="Lista de modelos: 'polinomial', 'mlp', 'svr', 'knn', 'arbol', 'bosque'"
    )
    config_polinomial: Optional[ConfigPolinomial] = None
    config_mlp: Optional[ConfigMLP] = None
    config_svr: Optional[ConfigSVR] = None
    config_knn: Optional[ConfigKNN] = None
    config_arbol: Optional[ConfigArbol] = None
    config_bosque: Optional[ConfigBosque] = None


class CurvaAjuste(BaseModel):
    longitudes: list[float]
    frecuencias_pred: list[float]


class MetricasModelo(BaseModel):
    mse: float
    rmse: float
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
    session_id: str
    timestamp: str
    columna_frecuencia: str
    longitudes_originales: list[float]
    frecuencias_originales: list[float]
    resultados: list[ResultadoModelo]


# Predicción


class PredictRequest(BaseModel):
    longitud_cm: float = Field(gt=0, description="Longitud de cuerda en cm")
    session_id: Optional[str] = Field(default=None, description="ID de sesión de entrenamiento. Si es None usa la última.")


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
