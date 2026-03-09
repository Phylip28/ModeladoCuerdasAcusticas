"""Módulo de modelos para el modelado de cuerdas acústicas.

Contiene ``ModeladorMaestro``, clase que encapsula el ajuste polinomial
clásico y el entrenamiento de una Red Neuronal Artificial (MLP) para
comparar ambos enfoques de regresión.
"""

from dataclasses import dataclass
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


class ModeladorMaestro:
    """Clase maestra de modelado para regresión sobre datos acústicos.

    Ofrece dos estrategias de regresión:
    - **Polinomial**: ajuste clásico con ``PolynomialFeatures`` + ``LinearRegression``.
    - **Red Neuronal MLP**: ``MLPRegressor`` de scikit-learn.

    Examples
    --------
    >>> modelador = ModeladorMaestro()
    >>> resultado = modelador.ajuste_polinomial(X, y, grado=3)
    >>> print(resultado.r2)
    """

    @staticmethod
    def _validar_entradas(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Valida y reshapea las entradas para scikit-learn.

        Parameters
        ----------
        X : np.ndarray
            Variable independiente (1-D o 2-D).
        y : np.ndarray
            Variable objetivo (1-D).

        Returns
        -------
        X_2d : np.ndarray
            X con forma ``(n_samples, 1)`` si era 1-D.
        y : np.ndarray
            Copia sin modificar.

        Raises
        ------
        ValueError
            Si las dimensiones de X e y no son compatibles.
        """
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
        self,
        X: np.ndarray,
        y: np.ndarray,
        grado: int = 2,
    ) -> ResultadoPolinomial:
        """Realiza un ajuste de regresión polinomial.

        Parameters
        ----------
        X : np.ndarray
            Variable independiente (longitud de cuerda).
        y : np.ndarray
            Variable objetivo (frecuencia medida).
        grado : int, optional
            Grado del polinomio (por defecto 2).

        Returns
        -------
        ResultadoPolinomial
            Contiene el pipeline entrenado, el MSE y el R².
        """
        X, y = self._validar_entradas(X, y)

        pipeline = Pipeline([
            ("poly_features", PolynomialFeatures(degree=grado, include_bias=False)),
            ("regresion", LinearRegression()),
        ])

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
        """Entrena una Red Neuronal Artificial (MLPRegressor).

        Incluye escalado estándar de las características para mejorar
        la convergencia del optimizador.

        Parameters
        ----------
        X : np.ndarray
            Variable independiente (longitud de cuerda).
        y : np.ndarray
            Variable objetivo (frecuencia medida).
        capas_ocultas : tuple[int, ...], optional
            Arquitectura de capas ocultas (por defecto ``(10, 10)``).
        activacion : str, optional
            Función de activación (por defecto ``'relu'``).
        optimizador : str, optional
            Algoritmo de optimización (por defecto ``'adam'``).
        max_iter : int, optional
            Iteraciones máximas (por defecto 5000).
        random_state : int, optional
            Semilla para reproducibilidad (por defecto 42).

        Returns
        -------
        ResultadoMLP
            Contiene el pipeline entrenado y el MSE.
        """
        X, y = self._validar_entradas(X, y)

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("mlp", MLPRegressor(
                hidden_layer_sizes=capas_ocultas,
                activation=activacion,
                solver=optimizador,
                max_iter=max_iter,
                random_state=random_state,
            )),
        ])

        pipeline.fit(X, y)
        y_pred = pipeline.predict(X)

        return ResultadoMLP(
            modelo=pipeline,
            mse=mean_squared_error(y, y_pred),
        )
