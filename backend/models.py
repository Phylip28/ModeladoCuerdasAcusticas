"""Módulo de modelos para el modelado de cuerdas acústicas.

Contiene ``ModeladorMaestro``, clase que encapsula el ajuste polinomial
clásico y el entrenamiento de una Red Neuronal Artificial (MLP) para
comparar ambos enfoques de regresión.
"""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


@dataclass
class ResultadoPolinomial:
    """Resultado del ajuste polinomial."""

    modelo: Pipeline
    mse: float
    r2: float


@dataclass
class ResultadoMLP:
    """Resultado del entrenamiento de la red neuronal MLP."""

    modelo: Pipeline
    mse: float
    loss_curve: list[float] = field(default_factory=list)


@dataclass
class ResultadoInverso:
    """Resultado del modelo inverso (frecuencia -> longitud)."""

    modelo: Pipeline
    mse: float


class ModeladorMaestro:
    """Clase maestra de modelado para regresión sobre datos acústicos."""

    @staticmethod
    def _validar_entradas(
        X: np.ndarray, y: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if X.shape[0] != y.shape[0]:
            raise ValueError(
                f"X tiene {X.shape[0]} muestras pero y tiene {y.shape[0]}."
            )
        return X, y

    def ajuste_polinomial(
        self, X: np.ndarray, y: np.ndarray, grado: int = 2
    ) -> ResultadoPolinomial:
        X, y = self._validar_entradas(X, y)
        pipeline = Pipeline(
            [
                ("poly_features", PolynomialFeatures(degree=grado, include_bias=False)),
                ("regresion", LinearRegression()),
            ]
        )
        pipeline.fit(X, y)
        y_pred = pipeline.predict(X)
        return ResultadoPolinomial(
            modelo=pipeline,
            mse=mean_squared_error(y, y_pred),
            r2=r2_score(y, y_pred),
        )

    def red_neuronal_mlp(
        self,
        X: np.ndarray,
        y: np.ndarray,
        *,
        capas_ocultas: tuple[int, ...] = (10, 10),
        activacion: str = "relu",
        optimizador: str = "adam",
        max_iter: int = 5000,
        random_state: int = 42,
    ) -> ResultadoMLP:
        X, y = self._validar_entradas(X, y)
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "mlp",
                    MLPRegressor(
                        hidden_layer_sizes=capas_ocultas,
                        activation=activacion,
                        solver=optimizador,
                        max_iter=max_iter,
                        random_state=random_state,
                    ),
                ),
            ]
        )
        pipeline.fit(X, y)
        y_pred = pipeline.predict(X)
        mlp_step = pipeline.named_steps["mlp"]
        loss_curve = (
            list(mlp_step.loss_curve_) if hasattr(mlp_step, "loss_curve_") else []
        )
        return ResultadoMLP(
            modelo=pipeline,
            mse=mean_squared_error(y, y_pred),
            loss_curve=loss_curve,
        )

    def crear_modelo_inverso(
        self,
        X_frecuencia: np.ndarray,
        y_longitud: np.ndarray,
        *,
        capas_ocultas: tuple[int, ...] = (50, 50),
        max_iter: int = 10000,
        learning_rate_init: float = 0.01,
        random_state: int = 42,
    ) -> ResultadoInverso:
        X_frecuencia, y_longitud = self._validar_entradas(X_frecuencia, y_longitud)
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "mlp",
                    MLPRegressor(
                        hidden_layer_sizes=capas_ocultas,
                        activation="relu",
                        solver="adam",
                        max_iter=max_iter,
                        learning_rate_init=learning_rate_init,
                        random_state=random_state,
                    ),
                ),
            ]
        )
        pipeline.fit(X_frecuencia, y_longitud)
        y_pred = pipeline.predict(X_frecuencia)
        return ResultadoInverso(
            modelo=pipeline,
            mse=mean_squared_error(y_longitud, y_pred),
        )
