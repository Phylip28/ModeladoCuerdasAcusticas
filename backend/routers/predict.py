"""Router de predicción: usa modelos entrenados para predecir frecuencia."""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException

from backend.schemas import PredictRequest, PredictResponse, PrediccionModelo
from backend.routers.train import _get_modelos_cache, _sessions

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/", response_model=PredictResponse)
def predecir(req: PredictRequest):
    """Predice la frecuencia para una longitud dada usando los modelos de la sesión indicada."""
    if req.session_id:
        session = next((s for s in _sessions if s["session_id"] == req.session_id), None)
        modelos_cache = session["modelos_cache"] if session else _get_modelos_cache()
    else:
        modelos_cache = _get_modelos_cache()
    if not modelos_cache:
        raise HTTPException(
            status_code=409,
            detail="No hay modelos entrenados. Llama primero a POST /models/train.",
        )

    L = np.array([[req.longitud_cm]])
    predicciones: list[PrediccionModelo] = []

    etiquetas = {
        "polinomial": "Polinomial",
        "mlp": "Red Neuronal (MLP)",
        "svr": "SVR (RBF kernel)",
        "knn": "KNN",
        "arbol": "Árbol Decisión",
        "bosque": "Random Forest",
    }

    for nombre, modelo in modelos_cache.items():
        try:
            freq = float(modelo.predict(L)[0])
            predicciones.append(
                PrediccionModelo(
                    nombre=nombre,
                    etiqueta=etiquetas.get(nombre, nombre),
                    frecuencia_hz=round(freq, 3),
                )
            )
        except Exception as e:
            predicciones.append(
                PrediccionModelo(
                    nombre=nombre,
                    etiqueta=etiquetas.get(nombre, nombre),
                    frecuencia_hz=0.0,
                    confianza=f"Error: {e}",
                )
            )

    mejor = predicciones[0].nombre if predicciones else ""

    return PredictResponse(
        longitud_cm=req.longitud_cm,
        predicciones=predicciones,
        mejor_modelo=mejor,
    )
