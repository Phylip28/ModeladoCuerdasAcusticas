"""Router de entrenamiento: ajusta los modelos y devuelve métricas + curvas."""

from __future__ import annotations

import uuid
from datetime import datetime

import numpy as np
from fastapi import APIRouter, HTTPException
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
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

# Each session: {"session_id", "modelos_cache": dict[str, pipeline], "X", "y", "columna"}
# Latest session's modelos_cache is exposed as _modelos_cache for predict compatibility
_sessions: list[dict] = []
_X_cache: np.ndarray | None = None
_y_cache: np.ndarray | None = None
_columna_cache: str | None = None


def _get_modelos_cache() -> dict:
    """Returns the most recently trained models (for other routers)."""
    return _sessions[-1]["modelos_cache"] if _sessions else {}


def _get_X_cache() -> "np.ndarray | None":
    return _X_cache


def _get_y_cache() -> "np.ndarray | None":
    return _y_cache


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
    global _X_cache, _y_cache, _columna_cache

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
    session_modelos: dict = {}

    for nombre_modelo in req.modelos:
        if nombre_modelo == "polinomial":
            config = req.config_polinomial
            grado = config.grado if config else 2
            res = maestro.ajuste_polinomial(X, y, grado=grado)
            session_modelos["polinomial"] = res.modelo
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
                        longitudes=L_plot.tolist(), frecuencias_pred=curva_y
                    ),
                    residuos=(y - y_pred).tolist(),
                    ecuacion=_extraer_ecuacion(res.modelo, grado),
                )
            )

        elif nombre_modelo == "mlp":
            config = req.config_mlp
            unidades = config.unidades if config else 10
            act = config.activacion if config else "relu"
            epocas = config.epocas if config else 500
            lr = config.learning_rate if config else 0.01
            res = maestro.red_neuronal_mlp(
                X, y, unidades=unidades, activacion=act, epocas=epocas, learning_rate=lr
            )
            session_modelos["mlp"] = res.modelo
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
                        longitudes=L_plot.tolist(), frecuencias_pred=curva_y
                    ),
                    residuos=(y - y_pred).tolist(),
                    loss_curve=res.loss_curve,
                )
            )

        elif nombre_modelo == "svr":
            config = req.config_svr
            kernel = config.kernel if config else "rbf"
            C = config.C if config else 1.0
            epsilon = config.epsilon if config else 0.1
            svr_pipeline = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    ("svr", SVR(kernel=kernel, C=C, epsilon=epsilon)),
                ]
            )
            svr_pipeline.fit(X.reshape(-1, 1), y)
            session_modelos["svr"] = svr_pipeline
            y_pred = svr_pipeline.predict(X.reshape(-1, 1))
            curva_y = svr_pipeline.predict(L_plot.reshape(-1, 1)).tolist()
            resultados.append(
                ResultadoModelo(
                    nombre="svr",
                    etiqueta=f"SVR ({kernel}, C={C})",
                    metricas=MetricasModelo(
                        mse=float(mean_squared_error(y, y_pred)),
                        r2=float(r2_score(y, y_pred)),
                        mae=float(mean_absolute_error(y, y_pred)),
                    ),
                    curva_ajuste=CurvaAjuste(
                        longitudes=L_plot.tolist(), frecuencias_pred=curva_y
                    ),
                    residuos=(y - y_pred).tolist(),
                )
            )

        elif nombre_modelo == "knn":
            config = req.config_knn
            k = config.n_vecinos if config else 5
            knn_pipeline = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    ("knn", KNeighborsRegressor(n_neighbors=k)),
                ]
            )
            knn_pipeline.fit(X.reshape(-1, 1), y)
            session_modelos["knn"] = knn_pipeline
            y_pred = knn_pipeline.predict(X.reshape(-1, 1))
            curva_y = knn_pipeline.predict(L_plot.reshape(-1, 1)).tolist()
            resultados.append(
                ResultadoModelo(
                    nombre="knn",
                    etiqueta=f"KNN (k={k})",
                    metricas=MetricasModelo(
                        mse=float(mean_squared_error(y, y_pred)),
                        r2=float(r2_score(y, y_pred)),
                        mae=float(mean_absolute_error(y, y_pred)),
                    ),
                    curva_ajuste=CurvaAjuste(
                        longitudes=L_plot.tolist(), frecuencias_pred=curva_y
                    ),
                    residuos=(y - y_pred).tolist(),
                )
            )

        elif nombre_modelo == "arbol":
            config = req.config_arbol
            max_depth = config.max_profundidad if config else None
            arbol_pipeline = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "arbol",
                        DecisionTreeRegressor(max_depth=max_depth, random_state=42),
                    ),
                ]
            )
            arbol_pipeline.fit(X.reshape(-1, 1), y)
            session_modelos["arbol"] = arbol_pipeline
            y_pred = arbol_pipeline.predict(X.reshape(-1, 1))
            curva_y = arbol_pipeline.predict(L_plot.reshape(-1, 1)).tolist()
            depth_label = f"prof={max_depth}" if max_depth else "sin límite"
            resultados.append(
                ResultadoModelo(
                    nombre="arbol",
                    etiqueta=f"Árbol Decisión ({depth_label})",
                    metricas=MetricasModelo(
                        mse=float(mean_squared_error(y, y_pred)),
                        r2=float(r2_score(y, y_pred)),
                        mae=float(mean_absolute_error(y, y_pred)),
                    ),
                    curva_ajuste=CurvaAjuste(
                        longitudes=L_plot.tolist(), frecuencias_pred=curva_y
                    ),
                    residuos=(y - y_pred).tolist(),
                )
            )

        elif nombre_modelo == "bosque":
            config = req.config_bosque
            n_est = config.n_estimadores if config else 100
            max_depth = config.max_profundidad if config else None
            bosque_pipeline = Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "bosque",
                        RandomForestRegressor(
                            n_estimators=n_est, max_depth=max_depth, random_state=42
                        ),
                    ),
                ]
            )
            bosque_pipeline.fit(X.reshape(-1, 1), y)
            session_modelos["bosque"] = bosque_pipeline
            y_pred = bosque_pipeline.predict(X.reshape(-1, 1))
            curva_y = bosque_pipeline.predict(L_plot.reshape(-1, 1)).tolist()
            resultados.append(
                ResultadoModelo(
                    nombre="bosque",
                    etiqueta=f"Random Forest ({n_est} árboles)",
                    metricas=MetricasModelo(
                        mse=float(mean_squared_error(y, y_pred)),
                        r2=float(r2_score(y, y_pred)),
                        mae=float(mean_absolute_error(y, y_pred)),
                    ),
                    curva_ajuste=CurvaAjuste(
                        longitudes=L_plot.tolist(), frecuencias_pred=curva_y
                    ),
                    residuos=(y - y_pred).tolist(),
                )
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Modelo desconocido: '{nombre_modelo}'. Válidos: polinomial, mlp, svr, knn, arbol, bosque.",
            )

    session_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%H:%M:%S")
    _sessions.append(
        {
            "session_id": session_id,
            "modelos_cache": session_modelos,
            "X": X,
            "y": y,
            "columna": req.columna_frecuencia,
        }
    )

    return TrainResponse(
        session_id=session_id,
        timestamp=timestamp,
        columna_frecuencia=req.columna_frecuencia,
        longitudes_originales=X.tolist(),
        frecuencias_originales=y.tolist(),
        resultados=resultados,
    )
