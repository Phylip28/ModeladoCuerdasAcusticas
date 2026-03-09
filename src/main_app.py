"""Interfaz gráfica principal para el Modelado de Cuerdas Acústicas.

Integra ``data_loader``, ``ModeladorMaestro``, ``AnalizadorAudio``
y ``report_generator`` en una aplicación de escritorio con CustomTkinter.
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Agregar src/ al path para imports locales ---
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from audio_capture import AnalizadorAudio, AudioNoDisponibleError
from data_loader import cargar_datos, _DEFAULT_DATASET_PATH, COLUMNA_LONGITUD, COLUMNAS_FRECUENCIA
from models import ModeladorMaestro, ResultadoMLP, ResultadoPolinomial
from report_generator import generar_pdf_reporte

# ---------------------------------------------------------------------------
# Constantes de UI
# ---------------------------------------------------------------------------
_PROJECT_ROOT = _SRC_DIR.parent
_REPORTS_DIR = _PROJECT_ROOT / "reports"
_APP_TITLE = "Modelado de Cuerdas Acústicas"
_DEFAULT_GRADO = 3
_COLUMNAS_FRECUENCIA = COLUMNAS_FRECUENCIA

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ═══════════════════════════════════════════════════════════════════════════
# Aplicación principal
# ═══════════════════════════════════════════════════════════════════════════
class AplicacionPrincipal(ctk.CTk):
    """Ventana principal de la aplicación de modelado acústico."""

    def __init__(self) -> None:
        super().__init__()
        self.title(_APP_TITLE)
        self.geometry("1100x700")
        self.minsize(900, 600)

        # --- Estado interno ---
        self._modelador = ModeladorMaestro()
        self._analizador = AnalizadorAudio()
        self._X: np.ndarray | None = None
        self._y: np.ndarray | None = None
        self._resultado_poly: ResultadoPolinomial | None = None
        self._resultado_mlp: ResultadoMLP | None = None
        self._ruta_grafico: Path | None = None

        self._construir_layout()

    # -------------------------------------------------------------------
    # Layout
    # -------------------------------------------------------------------
    def _construir_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_panel_lateral()
        self._crear_area_central()

    # --- Panel lateral ------------------------------------------------
    def _crear_panel_lateral(self) -> None:
        panel = ctk.CTkFrame(self, width=260, corner_radius=0)
        panel.grid(row=0, column=0, sticky="nswe")
        panel.grid_rowconfigure(10, weight=1)

        # Título
        ctk.CTkLabel(
            panel, text="⚙  Configuración",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10))

        # Selector de columna
        ctk.CTkLabel(panel, text="Columna de frecuencia:").grid(
            row=1, column=0, padx=20, pady=(15, 0), sticky="w",
        )
        self._combo_columna = ctk.CTkComboBox(
            panel, values=_COLUMNAS_FRECUENCIA, width=220,
        )
        self._combo_columna.set(_COLUMNAS_FRECUENCIA[0])
        self._combo_columna.grid(row=2, column=0, padx=20, pady=5)

        # Grado del polinomio
        ctk.CTkLabel(panel, text="Grado del polinomio:").grid(
            row=3, column=0, padx=20, pady=(15, 0), sticky="w",
        )
        self._entry_grado = ctk.CTkEntry(panel, width=220, placeholder_text="3")
        self._entry_grado.insert(0, str(_DEFAULT_GRADO))
        self._entry_grado.grid(row=4, column=0, padx=20, pady=5)

        # Botón ejecutar modelos
        ctk.CTkButton(
            panel,
            text="▶  Ejecutar Modelos",
            command=self._ejecutar_modelos,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=5, column=0, padx=20, pady=(25, 10))

        # Separador visual
        ctk.CTkLabel(panel, text="─" * 30, text_color="gray50").grid(
            row=6, column=0, padx=20, pady=5,
        )

        # Botón generar PDF
        ctk.CTkButton(
            panel,
            text="📄  Generar Informe PDF",
            command=self._generar_pdf,
            height=40,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=7, column=0, padx=20, pady=10)

        # Info
        ctk.CTkLabel(
            panel, text="Modelado Cuerdas Acústicas\nv1.0",
            font=ctk.CTkFont(size=11), text_color="gray60",
        ).grid(row=11, column=0, padx=20, pady=(0, 15))

    # --- Área central con pestañas ------------------------------------
    def _crear_area_central(self) -> None:
        self._tabview = ctk.CTkTabview(self)
        self._tabview.grid(row=0, column=1, padx=15, pady=15, sticky="nswe")

        self._tab_entrada = self._tabview.add("📡 Entrada de Datos")
        self._tab_visual = self._tabview.add("📊 Visualización")
        self._tab_resultados = self._tabview.add("📋 Resultados")

        self._construir_tab_entrada()
        self._construir_tab_visualizacion()
        self._construir_tab_resultados()

    # --- Pestaña 1: Entrada de Datos ----------------------------------
    def _construir_tab_entrada(self) -> None:
        tab = self._tab_entrada
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tab, text="Captura de Audio en Vivo",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, pady=(10, 5))

        ctk.CTkLabel(
            tab,
            text="Pulsa el botón, toca la cuerda de la guitarra y espera a que\n"
                 "se detecte la frecuencia fundamental.",
            text_color="gray60",
        ).grid(row=1, column=0, pady=5)

        self._btn_capturar = ctk.CTkButton(
            tab,
            text="🎤  Capturar Frecuencia",
            command=self._capturar_audio,
            height=50,
            width=280,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#c62828",
            hover_color="#b71c1c",
        )
        self._btn_capturar.grid(row=2, column=0, pady=20)

        self._lbl_frecuencia = ctk.CTkLabel(
            tab, text="— Hz",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#64b5f6",
        )
        self._lbl_frecuencia.grid(row=3, column=0, pady=10)

        self._lbl_estado_audio = ctk.CTkLabel(
            tab, text="Listo para capturar", text_color="gray50",
        )
        self._lbl_estado_audio.grid(row=4, column=0, pady=5)

    # --- Pestaña 2: Visualización -------------------------------------
    def _construir_tab_visualizacion(self) -> None:
        tab = self._tab_visual
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        self._fig, self._ax = plt.subplots(figsize=(8, 5))
        self._fig.patch.set_facecolor("#2b2b2b")
        self._ax.set_facecolor("#1e1e1e")
        self._ax.tick_params(colors="white")
        self._ax.xaxis.label.set_color("white")
        self._ax.yaxis.label.set_color("white")
        self._ax.title.set_color("white")
        for spine in self._ax.spines.values():
            spine.set_color("gray")

        self._canvas = FigureCanvasTkAgg(self._fig, master=tab)
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

    # --- Pestaña 3: Resultados ----------------------------------------
    def _construir_tab_resultados(self) -> None:
        tab = self._tab_resultados
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tab, text="Métricas y Ecuaciones",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, pady=(10, 15))

        self._txt_resultados = ctk.CTkTextbox(
            tab, width=700, height=450, font=ctk.CTkFont(family="Consolas", size=13),
        )
        self._txt_resultados.grid(row=1, column=0, padx=10, pady=5, sticky="nswe")
        tab.grid_rowconfigure(1, weight=1)

        self._txt_resultados.insert("end", "Ejecuta los modelos para ver los resultados aquí.\n")
        self._txt_resultados.configure(state="disabled")

    # -------------------------------------------------------------------
    # Lógica de negocio
    # -------------------------------------------------------------------
    def _obtener_grado(self) -> int:
        """Lee y valida el grado del polinomio desde la UI."""
        try:
            grado = int(self._entry_grado.get())
            if grado < 1:
                raise ValueError
            return grado
        except ValueError:
            messagebox.showwarning("Grado inválido", "Ingresa un número entero positivo.")
            raise

    def _ejecutar_modelos(self) -> None:
        """Carga datos, entrena los modelos y actualiza la UI."""
        try:
            columna = self._combo_columna.get()
            grado = self._obtener_grado()
        except ValueError:
            return

        try:
            self._X, self._y = cargar_datos(columna)
        except (FileNotFoundError, KeyError, ValueError) as exc:
            messagebox.showerror("Error al cargar datos", str(exc))
            return

        # Ajuste polinomial
        self._resultado_poly = self._modelador.ajuste_polinomial(
            self._X, self._y, grado=grado,
        )

        # Red neuronal MLP
        self._resultado_mlp = self._modelador.red_neuronal_mlp(self._X, self._y)

        self._actualizar_grafico(columna, grado)
        self._actualizar_resultados(columna, grado)
        self._tabview.set("📊 Visualización")

    def _actualizar_grafico(self, columna: str, grado: int) -> None:
        """Dibuja puntos reales vs curvas de los modelos."""
        ax = self._ax
        ax.clear()

        X_sorted = np.sort(self._X)
        X_plot = X_sorted.reshape(-1, 1)

        # Puntos reales
        ax.scatter(
            self._X, self._y,
            color="#64b5f6", edgecolors="white", s=60, zorder=5,
            label="Datos reales",
        )

        # Curva polinomial
        y_poly = self._resultado_poly.modelo.predict(X_plot)
        ax.plot(
            X_sorted, y_poly, color="#ffa726", linewidth=2.5,
            label=f"Polinomio grado {grado} (R²={self._resultado_poly.r2:.4f})",
        )

        # Curva MLP
        y_mlp = self._resultado_mlp.modelo.predict(X_plot)
        ax.plot(
            X_sorted, y_mlp, color="#ef5350", linewidth=2.5, linestyle="--",
            label=f"MLP (MSE={self._resultado_mlp.mse:.4f})",
        )

        ax.set_xlabel("Longitud (cm)")
        ax.set_ylabel(f"Frecuencia – {columna} (Hz)")
        ax.set_title("Datos Reales vs Modelos de Regresión")
        ax.legend(facecolor="#2b2b2b", edgecolor="gray", labelcolor="white")
        ax.grid(True, alpha=0.2)

        self._fig.tight_layout()
        self._canvas.draw()

        # Guardar gráfico para el PDF
        _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self._ruta_grafico = _REPORTS_DIR / "grafico_comparativo.png"
        self._fig.savefig(self._ruta_grafico, dpi=150, bbox_inches="tight")

    def _actualizar_resultados(self, columna: str, grado: int) -> None:
        """Actualiza la pestaña de resultados con métricas y ecuaciones."""
        self._txt_resultados.configure(state="normal")
        self._txt_resultados.delete("1.0", "end")

        lines = [
            f"{'═' * 55}",
            f"  RESULTADOS — Columna: {columna}",
            f"{'═' * 55}\n",
            f"  ┌─────────────────────────────────────────────────┐",
            f"  │  REGRESIÓN POLINOMIAL (grado {grado})               │",
            f"  ├─────────────────────────────────────────────────┤",
            f"  │  MSE  : {self._resultado_poly.mse:<38.6f}  │",
            f"  │  R²   : {self._resultado_poly.r2:<38.6f}  │",
            f"  └─────────────────────────────────────────────────┘\n",
        ]

        # Ecuación polinomial
        regresion = self._resultado_poly.modelo.named_steps["regresion"]
        coefs = regresion.coef_
        intercepto = regresion.intercept_
        terminos: list[str] = []
        for i, c in enumerate(coefs, start=1):
            if abs(c) < 1e-12:
                continue
            signo = "+" if c >= 0 else "-"
            if i == 1:
                terminos.append(f"{signo} {abs(c):.6g}·x")
            else:
                terminos.append(f"{signo} {abs(c):.6g}·x^{i}")
        signo_i = "+" if intercepto >= 0 else "-"
        terminos.append(f"{signo_i} {abs(intercepto):.6g}")
        ecuacion = "  f(x) = " + " ".join(terminos).lstrip("+ ")

        lines.append("  Ecuación del polinomio:")
        lines.append(f"  {ecuacion}\n")

        lines += [
            f"  ┌─────────────────────────────────────────────────┐",
            f"  │  RED NEURONAL MLP (10-10, relu, adam)            │",
            f"  ├─────────────────────────────────────────────────┤",
            f"  │  MSE  : {self._resultado_mlp.mse:<38.6f}  │",
            f"  └─────────────────────────────────────────────────┘\n",
            f"{'═' * 55}",
        ]

        self._txt_resultados.insert("end", "\n".join(lines))
        self._txt_resultados.configure(state="disabled")

    # --- Captura de audio ---------------------------------------------
    def _capturar_audio(self) -> None:
        """Inicia la captura de audio en un hilo separado."""
        self._btn_capturar.configure(state="disabled", text="🎤  Grabando...")
        self._lbl_estado_audio.configure(text="Grabando… toca la cuerda ahora", text_color="#ffa726")
        threading.Thread(target=self._hilo_captura, daemon=True).start()

    def _hilo_captura(self) -> None:
        """Hilo de captura para no bloquear la UI."""
        try:
            frecuencia = self._analizador.capturar_frecuencia(duracion=2, fs=44100)
            self.after(0, self._mostrar_frecuencia, frecuencia)
        except (AudioNoDisponibleError, ValueError) as exc:
            self.after(0, self._mostrar_error_audio, str(exc))

    def _mostrar_frecuencia(self, frecuencia: float) -> None:
        self._lbl_frecuencia.configure(text=f"{frecuencia:.2f} Hz")
        self._lbl_estado_audio.configure(
            text="Frecuencia detectada correctamente ✔", text_color="#66bb6a",
        )
        self._btn_capturar.configure(state="normal", text="🎤  Capturar Frecuencia")

    def _mostrar_error_audio(self, mensaje: str) -> None:
        self._lbl_frecuencia.configure(text="— Hz")
        self._lbl_estado_audio.configure(text=f"Error: {mensaje}", text_color="#ef5350")
        self._btn_capturar.configure(state="normal", text="🎤  Capturar Frecuencia")

    # --- Generación de PDF --------------------------------------------
    def _generar_pdf(self) -> None:
        """Genera el informe PDF con los resultados actuales."""
        if self._resultado_poly is None or self._resultado_mlp is None:
            messagebox.showwarning(
                "Sin resultados",
                "Primero ejecuta los modelos antes de generar el informe.",
            )
            return

        grado = self._obtener_grado()
        columna = self._combo_columna.get()

        datos_modelos = [
            {
                "nombre": f"Polinomio grado {grado}",
                "mse": self._resultado_poly.mse,
                "r2": self._resultado_poly.r2,
                "pipeline": self._resultado_poly.modelo,
                "grado": grado,
            },
            {
                "nombre": "Red Neuronal MLP (10-10)",
                "mse": self._resultado_mlp.mse,
                "r2": None,
                "pipeline": None,
                "grado": None,
            },
        ]

        try:
            ruta_pdf = generar_pdf_reporte(
                datos_modelos=datos_modelos,
                ruta_grafico=self._ruta_grafico,
                nombre_archivo=f"reporte_{columna}.pdf",
            )
            messagebox.showinfo(
                "PDF Generado",
                f"Informe guardado en:\n{ruta_pdf}",
            )
            os.startfile(ruta_pdf)
        except Exception as exc:
            messagebox.showerror("Error al generar PDF", str(exc))


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════
def main() -> None:
    app = AplicacionPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()
