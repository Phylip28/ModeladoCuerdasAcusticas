"""Router de reporte: genera y devuelve el PDF con resultados del análisis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sklearn.metrics import mean_squared_error, r2_score

from backend.report_generator import generar_pdf_reporte
from backend.schemas import ReportRequest
from backend.routers.train import _modelos_cache, _X_cache, _y_cache

router = APIRouter(prefix="/report", tags=["report"])

MODEL_LABELS = {
    "polinomial": "Polinomial",
    "svr": "SVR (RBF)",
    "mlp": "Red Neuronal MLP",
}

MODEL_COLORS = {
    "polinomial": "#F5C842",
    "svr": "#00D4AA",
    "mlp": "#A78BFA",
}


def _generar_grafico_comparativo(reports_dir: Path) -> Path:
    """Genera el PNG del scatter + curvas de ajuste."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("#0C1327")

    ax1, ax2 = axes
    for ax in axes:
        ax.set_facecolor("#111A35")
        ax.tick_params(colors="#8899CC")
        ax.xaxis.label.set_color("#8899CC")
        ax.yaxis.label.set_color("#8899CC")
        ax.spines[:].set_color("#1E2D55")

    X = _X_cache.reshape(-1, 1)
    L_plot = np.linspace(_X_cache.min(), _X_cache.max(), 200).reshape(-1, 1)

    # Scatter datos reales
    ax1.scatter(
        _X_cache,
        _y_cache,
        color="#E8EDF8",
        s=40,
        zorder=5,
        label="Datos reales",
        alpha=0.85,
    )

    # Residuos
    x_labels = [f"{x:.1f}" for x in _X_cache]

    for nombre, modelo in _modelos_cache.items():
        y_pred_full = modelo.predict(L_plot)
        y_pred = modelo.predict(X)
        color = MODEL_COLORS.get(nombre, "#8899CC")
        label = MODEL_LABELS.get(nombre, nombre)

        ax1.plot(L_plot.ravel(), y_pred_full, color=color, lw=2, label=label)
        residuos = _y_cache - y_pred
        ax2.plot(
            _X_cache, residuos, "o-", color=color, lw=1.2, markersize=4, label=label
        )

    ax1.set_xlabel("Longitud L (cm)")
    ax1.set_ylabel("Frecuencia f (Hz)")
    ax1.set_title("Ajuste de Modelos", color="#E8EDF8", fontsize=12)
    ax1.legend(
        facecolor="#111A35", edgecolor="#1E2D55", labelcolor="#E8EDF8", fontsize=8
    )

    ax2.axhline(0, color="#4A5578", lw=1, ls="--")
    ax2.set_xlabel("Longitud L (cm)")
    ax2.set_ylabel("Residuo (Hz)")
    ax2.set_title("Análisis de Residuos", color="#E8EDF8", fontsize=12)
    ax2.legend(
        facecolor="#111A35", edgecolor="#1E2D55", labelcolor="#E8EDF8", fontsize=8
    )

    plt.tight_layout()
    ruta = reports_dir / "grafico_comparativo.png"
    fig.savefig(ruta, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return ruta


@router.post("/", response_class=StreamingResponse)
def generar_reporte(req: ReportRequest):
    """Genera el PDF de reporte y lo devuelve como stream descargable."""
    if not _modelos_cache:
        raise HTTPException(
            status_code=409,
            detail="No hay modelos entrenados. Entrena primero los modelos.",
        )
    if _X_cache is None or _y_cache is None:
        raise HTTPException(status_code=409, detail="No hay datos cargados en memoria.")

    reports_dir = Path(__file__).resolve().parent.parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    try:
        ruta_grafico = _generar_grafico_comparativo(reports_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando gráfico: {e}")

    # Construir datos_modelos en el formato que espera generar_pdf_reporte
    X2d = _X_cache.reshape(-1, 1)
    grado = req.config_polinomial.grado if req.config_polinomial else 2
    datos_modelos = []
    loss_curve = None

    for nombre, modelo in _modelos_cache.items():
        y_pred = modelo.predict(X2d)
        mse = float(mean_squared_error(_y_cache, y_pred))
        r2 = float(r2_score(_y_cache, y_pred))
        entry = {
            "nombre": MODEL_LABELS.get(nombre, nombre),
            "mse": mse,
            "r2": r2,
            "pipeline": modelo if nombre == "polinomial" else None,
            "grado": grado if nombre == "polinomial" else None,
        }
        datos_modelos.append(entry)

        if nombre == "mlp":
            mlp_step = modelo.named_steps.get("mlp")
            if mlp_step and hasattr(mlp_step, "loss_curve_"):
                loss_curve = list(mlp_step.loss_curve_)

    try:
        pdf_path = generar_pdf_reporte(
            datos_modelos=datos_modelos,
            ruta_grafico=ruta_grafico,
            nombre_archivo="reporte_api.pdf",
            directorio_salida=reports_dir,
            loss_curve=loss_curveg_polinomial.grado if req.config_polinomial else 2,
            columna_usada=req.columna_frecuencia,
            ruta_salida=pdf_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}")

    def iter_file():
        with open(pdf_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iter_file(),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="reporte_cuerdas.pdf"'},
    )
