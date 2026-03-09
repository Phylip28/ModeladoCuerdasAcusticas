"""Módulo de generación de reportes PDF para el modelado de cuerdas acústicas.

Usa ``fpdf2`` para construir un PDF limpio y profesional con tabla
comparativa, ecuaciones y gráficos.
"""

from pathlib import Path
from typing import Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF

# ---------------------------------------------------------------------------
# Constantes de diseño
# ---------------------------------------------------------------------------
_TITULO_TRABAJO = "Modelado Matemático de Cuerdas Acústicas"
_INTEGRANTES = [
    "Juan Felipe Rendon Herrera",
]
_FONT_FAMILY = "Helvetica"
_COLOR_ENCABEZADO = (41, 65, 122)   # Azul oscuro
_COLOR_FILA_PAR = (234, 240, 251)   # Azul claro
_COLOR_BLANCO = (255, 255, 255)


class _PDFReporte(FPDF):
    """Subclase de FPDF con header/footer personalizados."""

    def header(self) -> None:
        self.set_font(_FONT_FAMILY, "B", 10)
        self.set_text_color(*_COLOR_ENCABEZADO)
        self.cell(0, 8, _TITULO_TRABAJO, align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font(_FONT_FAMILY, "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extraer_ecuacion_polinomial(modelo_pipeline, grado: int) -> str:
    """Extrae la ecuación del modelo polinomial como string legible.

    Parameters
    ----------
    modelo_pipeline : sklearn.pipeline.Pipeline
        Pipeline entrenado (PolynomialFeatures → LinearRegression).
    grado : int
        Grado del polinomio ajustado.

    Returns
    -------
    str
        Ecuación en formato ``f(x) = a·x^n + b·x^(n-1) + ... + c``.
    """
    regresion = modelo_pipeline.named_steps["regresion"]
    coefs = regresion.coef_
    intercepto = regresion.intercept_

    terminos: list[str] = []
    for i, c in enumerate(coefs, start=1):
        exp = i
        if abs(c) < 1e-12:
            continue
        signo = "+" if c >= 0 else "-"
        valor = abs(c)
        if exp == 1:
            terminos.append(f"{signo} {valor:.6g}·x")
        else:
            terminos.append(f"{signo} {valor:.6g}·x^{exp}")

    signo_inter = "+" if intercepto >= 0 else "-"
    terminos.append(f"{signo_inter} {abs(intercepto):.6g}")

    ecuacion = " ".join(terminos).lstrip("+ ").replace("- ", "- ")
    return f"f(x) = {ecuacion}"


def _agregar_portada(pdf: _PDFReporte) -> None:
    """Agrega la sección de portada al PDF."""
    pdf.set_font(_FONT_FAMILY, "B", 22)
    pdf.set_text_color(*_COLOR_ENCABEZADO)
    pdf.ln(30)
    pdf.cell(0, 15, _TITULO_TRABAJO, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(_FONT_FAMILY, "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.ln(10)
    pdf.cell(0, 8, "Integrantes:", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(_FONT_FAMILY, "I", 12)
    for nombre in _INTEGRANTES:
        pdf.cell(0, 7, nombre, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font(_FONT_FAMILY, "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(
        0, 7,
        "Comparación de Regresión Polinomial vs Red Neuronal Artificial (MLP)",
        align="C", new_x="LMARGIN", new_y="NEXT",
    )


def _agregar_tabla_errores(
    pdf: _PDFReporte,
    filas: Sequence[tuple[str, float, str]],
) -> None:
    """Agrega tabla comparativa de métricas al PDF.

    Parameters
    ----------
    filas : Sequence[tuple[str, float, str]]
        Lista de tuplas ``(nombre_modelo, mse, r2_str)``.
    """
    pdf.add_page()
    pdf.set_font(_FONT_FAMILY, "B", 14)
    pdf.set_text_color(*_COLOR_ENCABEZADO)
    pdf.cell(0, 10, "Tabla Comparativa de Errores", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    col_widths = [70, 50, 50]
    headers = ["Modelo", "MSE", "R²"]

    # Encabezado de tabla
    pdf.set_fill_color(*_COLOR_ENCABEZADO)
    pdf.set_text_color(*_COLOR_BLANCO)
    pdf.set_font(_FONT_FAMILY, "B", 10)
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 9, h, border=1, align="C", fill=True)
    pdf.ln()

    # Filas
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(_FONT_FAMILY, "", 10)
    for idx, (nombre, mse, r2_str) in enumerate(filas):
        if idx % 2 == 0:
            pdf.set_fill_color(*_COLOR_FILA_PAR)
        else:
            pdf.set_fill_color(*_COLOR_BLANCO)
        pdf.cell(col_widths[0], 8, nombre, border=1, align="L", fill=True)
        pdf.cell(col_widths[1], 8, f"{mse:.6f}", border=1, align="C", fill=True)
        pdf.cell(col_widths[2], 8, r2_str, border=1, align="C", fill=True)
        pdf.ln()


def _agregar_ecuaciones(
    pdf: _PDFReporte,
    ecuaciones: Sequence[tuple[str, str]],
) -> None:
    """Agrega sección de ecuaciones polinomiales al PDF.

    Parameters
    ----------
    ecuaciones : Sequence[tuple[str, str]]
        Lista de tuplas ``(titulo, ecuacion_str)``.
    """
    pdf.ln(10)
    pdf.set_font(_FONT_FAMILY, "B", 14)
    pdf.set_text_color(*_COLOR_ENCABEZADO)
    pdf.cell(0, 10, "Ecuaciones de los Modelos Polinomiales", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_text_color(0, 0, 0)
    for titulo, ecuacion in ecuaciones:
        pdf.set_font(_FONT_FAMILY, "B", 10)
        pdf.cell(0, 7, titulo, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 9)
        pdf.multi_cell(0, 6, ecuacion)
        pdf.ln(3)


def _agregar_grafico(pdf: _PDFReporte, ruta_grafico: Path) -> None:
    """Agrega una imagen de gráfico al PDF."""
    pdf.add_page()
    pdf.set_font(_FONT_FAMILY, "B", 14)
    pdf.set_text_color(*_COLOR_ENCABEZADO)
    pdf.cell(0, 10, "Grafico Comparativo", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    ancho_disponible = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.image(str(ruta_grafico), x=pdf.l_margin, w=ancho_disponible)


def _generar_grafico_loss_curve(
    loss_curve: list[float],
    directorio: Path,
) -> Path:
    """Genera una imagen PNG de la curva de pérdida de la red neuronal.

    Parameters
    ----------
    loss_curve : list[float]
        Lista de valores de loss por época (``MLPRegressor.loss_curve_``).
    directorio : Path
        Carpeta donde guardar la imagen.

    Returns
    -------
    Path
        Ruta al archivo PNG generado.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(loss_curve, color="#ef5350", linewidth=1.5)
    ax.set_xlabel("Iteracion")
    ax.set_ylabel("Loss (MSE)")
    ax.set_title("Convergencia de la Red Neuronal")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    ruta = directorio / "loss_curve.png"
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta


def _agregar_loss_curve(pdf: _PDFReporte, ruta_loss: Path) -> None:
    """Agrega la gráfica de convergencia de la red neuronal al PDF."""
    pdf.add_page()
    pdf.set_font(_FONT_FAMILY, "B", 14)
    pdf.set_text_color(*_COLOR_ENCABEZADO)
    pdf.cell(0, 10, "Convergencia de la Red Neuronal", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font(_FONT_FAMILY, "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6,
        "La siguiente grafica muestra la curva de perdida (loss) del MLPRegressor "
        "durante el entrenamiento. Un descenso estable indica buena convergencia."
    )
    pdf.ln(4)

    ancho_disponible = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.image(str(ruta_loss), x=pdf.l_margin, w=ancho_disponible)


# ---------------------------------------------------------------------------
# Función pública
# ---------------------------------------------------------------------------

def generar_pdf_reporte(
    datos_modelos: Sequence[dict],
    ruta_grafico: str | Path,
    nombre_archivo: str = "reporte_modelado.pdf",
    directorio_salida: str | Path | None = None,
    loss_curve: list[float] | None = None,
) -> Path:
    """Genera un PDF profesional con los resultados del modelado.

    Parameters
    ----------
    datos_modelos : Sequence[dict]
        Lista de diccionarios con la información de cada modelo::

            {
                "nombre": str,        # Ej. "Polinomio grado 3"
                "mse": float,
                "r2": float | None,   # None para modelos sin R²
                "pipeline": Pipeline | None,  # Para extraer ecuación
                "grado": int | None,  # Grado del polinomio (None si es MLP)
            }

    ruta_grafico : str | Path
        Ruta a la imagen PNG/JPG del gráfico comparativo.
    nombre_archivo : str, optional
        Nombre del archivo PDF de salida (por defecto ``'reporte_modelado.pdf'``).
    directorio_salida : str | Path | None, optional
        Directorio donde guardar el PDF. Si es ``None``, usa ``reports/``.
    loss_curve : list[float] | None, optional
        Curva de pérdida del MLPRegressor para incluir en el reporte.

    Returns
    -------
    Path
        Ruta absoluta al PDF generado.
    """
    ruta_grafico = Path(ruta_grafico)
    if not ruta_grafico.exists():
        raise FileNotFoundError(f"No se encontró el gráfico en: {ruta_grafico}")

    if directorio_salida is None:
        directorio_salida = Path(__file__).resolve().parent.parent / "reports"
    directorio_salida = Path(directorio_salida)
    directorio_salida.mkdir(parents=True, exist_ok=True)

    ruta_pdf = directorio_salida / nombre_archivo

    pdf = _PDFReporte(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()

    # --- Portada ---
    pdf.add_page()
    _agregar_portada(pdf)

    # --- Tabla comparativa ---
    filas: list[tuple[str, float, str]] = []
    ecuaciones: list[tuple[str, str]] = []

    for modelo in datos_modelos:
        r2_str = f"{modelo['r2']:.6f}" if modelo.get("r2") is not None else "N/A"
        filas.append((modelo["nombre"], modelo["mse"], r2_str))

        if modelo.get("pipeline") is not None and modelo.get("grado") is not None:
            ecuacion = _extraer_ecuacion_polinomial(modelo["pipeline"], modelo["grado"])
            ecuaciones.append((modelo["nombre"], ecuacion))

    _agregar_tabla_errores(pdf, filas)

    # --- Ecuaciones ---
    if ecuaciones:
        _agregar_ecuaciones(pdf, ecuaciones)

    # --- Gráfico ---
    _agregar_grafico(pdf, ruta_grafico)

    # --- Curva de convergencia ---
    if loss_curve:
        ruta_loss = _generar_grafico_loss_curve(loss_curve, directorio_salida)
        _agregar_loss_curve(pdf, ruta_loss)

    pdf.output(str(ruta_pdf))
    return ruta_pdf
