"""Router de predicción: usa modelos entrenados para predecir frecuencia."""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
from fastapi import APIRouter, HTTPException

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_DIR = _PROJECT_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from backend.schemas import PredictRequest, PredictResponse, PrediccionModelo
from backend.routers.train import _modelos_cache

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/", response_model=PredictResponse)
def predecir(req: PredictRequest):
    """Predice la frecuencia para una longitud dada usando todos los modelos entrenados."""
    if not _modelos_cache:
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
    }

    for nombre, modelo in _modelos_cache.items():
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

    # El "mejor modelo" se define como el que tenga menor MSE (comparado de los trains anteriores)
    # Por ahora simplemente reportamos el primero; en producción se guardarían las métricas.
    mejor = predicciones[0].nombre if predicciones else ""

    return PredictResponse(
        longitud_cm=req.longitud_cm,
        predicciones=predicciones,
        mejor_modelo=mejor,
    )
