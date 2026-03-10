"""Router de entrenamiento: ajusta los modelos y devuelve métricas + curvas."""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.models import ModeladorMaestro
from backend.data_loader import COLUMNA_LONGITUD, _limpiar_columna_numerica
from backend.schemas import (
    TrainRequest,
    TrainResponse,
    ResultadoModelo,
    MetricasModelo,
    CurvaAjuste,
)
from backend.routers.data import get_active_df

router = APIRouter(prefix="/models", tags=["models"])

# Cache de modelos entrenados (se actualizan en cada llamada a /train)
_modelos_cache: dict[str, object] = {}
_X_cache: np.ndarray | None = None
_y_cache: np.ndarray | None = None
_columna_cache: str | None = None


def _extraer_ecuacion(pipeline: Pipeline, grado: int) -> str:
    """Extrae la ecuación polinomial como string."""
    try:
        regresion = pipeline.named_steps["regresion"]
        coefs = regresion.coef_
        intercepto = regresion.intercept_
        terminos = []
        for i, c in enumerate(coefs, start=1):
            if abs(c) < 1e-12:
                continue
            signo = "+" if c >= 0 else "-"
            valor = abs(c)
            if i == 1:
                terminos.append(f"{signo} {valor:.4g}·L")
            else:
                terminos.append(f"{signo} {valor:.4g}·L^{i}")
        ic_sign = "+" if intercepto >= 0 else "-"
        eq = f"f(L) = {' '.join(terminos)} {ic_sign} {abs(intercepto):.4g}"
        return eq.replace("+ -", "- ").strip()
    except Exception:
        return ""


@router.post("/train", response_model=TrainResponse)
def entrenar_modelos(req: TrainRequest):
    """Entrena los modelos seleccionados y devuelve métricas y curvas de ajuste."""
    global _modelos_cache, _X_cache, _y_cache, _columna_cache

    df = get_active_df()
    import pandas as pd

    if req.columna_frecuencia not in df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Columna '{req.columna_frecuencia}' no encontrada en el dataset.",
        )

    df = df[[COLUMNA_LONGITUD, req.columna_frecuencia]].copy()
    df[COLUMNA_LONGITUD] = _limpiar_columna_numerica(df[COLUMNA_LONGITUD])
    df[req.columna_frecuencia] = _limpiar_columna_numerica(df[req.columna_frecuencia])
    df = df.dropna()

    X = df[COLUMNA_LONGITUD].to_numpy(dtype=np.float64)
    y = df[req.columna_frecuencia].to_numpy(dtype=np.float64)

    _X_cache = X
    _y_cache = y
    _columna_cache = req.columna_frecuencia

    maestro = ModeladorMaestro()
    L_plot = np.linspace(X.min(), X.max(), 200)
    resultados: list[ResultadoModelo] = []

    for nombre_modelo in req.modelos:
        if nombre_modelo == "polinomial":
            config = req.config_polinomial
            grado = config.grado if config else 2

            res = maestro.ajuste_polinomial(X, y, grado=grado)
            _modelos_cache["polinomial"] = res.modelo
            y_pred = res.modelo.predict(X.reshape(-1, 1))
            curva_y = res.modelo.predict(L_plot.reshape(-1, 1)).tolist()

            resultados.append(
                ResultadoModelo(
                    nombre="polinomial",
                    etiqueta=f"Polinomial grado {grado}",
                    metricas=MetricasModelo(
                        mse=float(res.mse),
                        r2=float(res.r2),
                        mae=float(mean_absolute_error(y, y_pred)),
                    ),
                    curva_ajuste=CurvaAjuste(
                        longitudes=L_plot.tolist(),
                        frecuencias_pred=curva_y,
                    ),
                    residuos=(y - y_pred).tolist(),
                    ecuacion=_extraer_ecuacion(res.modelo, grado),
                )
            )

        elif nombre_modelo == "mlp":
            config = req.config_mlp
            capas = tuple(config.capas_ocultas) if config else (10, 10)
            act = config.activacion if config else "relu"
            max_it = config.max_iter if config else 5000

            res = maestro.red_neuronal_mlp(
                X, y, capas_ocultas=capas, activacion=act, max_iter=max_it
            )
            _modelos_cache["mlp"] = res.modelo
            y_pred = res.modelo.predict(X.reshape(-1, 1))
            curva_y = res.modelo.predict(L_plot.reshape(-1, 1)).tolist()

            resultados.append(
                ResultadoModelo(
                    nombre="mlp",
                    etiqueta="Red Neuronal (MLP)",
                    metricas=MetricasModelo(
                        mse=float(res.mse),
                        r2=float(r2_score(y, y_pred)),
                        mae=float(mean_absolute_error(y, y_pred)),
                    ),
                    curva_ajuste=CurvaAjuste(
                        longitudes=L_plot.tolist(),
                        frecuencias_pred=curva_y,
                    ),
                    residuos=(y - y_pred).tolist(),
                    loss_curve=res.loss_curve,
                )
            )

        elif nombre_modelo == "svr":
            svr_pipeline = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    ("svr", SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1)),
                ]
            )
            svr_pipeline.fit(X.reshape(-1, 1), y)
            _modelos_cache["svr"] = svr_pipeline
            y_pred = svr_pipeline.predict(X.reshape(-1, 1))
            curva_y = svr_pipeline.predict(L_plot.reshape(-1, 1)).tolist()

            resultados.append(
                ResultadoModelo(
                    nombre="svr",
                    etiqueta="SVR (RBF kernel)",
                    metricas=MetricasModelo(
                        mse=float(mean_squared_error(y, y_pred)),
                        r2=float(r2_score(y, y_pred)),
                        mae=float(mean_absolute_error(y, y_pred)),
                    ),
                    curva_ajuste=CurvaAjuste(
                        longitudes=L_plot.tolist(),
                        frecuencias_pred=curva_y,
                    ),
                    residuos=(y - y_pred).tolist(),
                )
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Modelo desconocido: '{nombre_modelo}'. Use 'polinomial', 'mlp' o 'svr'.",
            )

    return TrainResponse(
        columna_frecuencia=req.columna_frecuencia,
        longitudes_originales=X.tolist(),
        frecuencias_originales=y.tolist(),
        resultados=resultados,
    )
