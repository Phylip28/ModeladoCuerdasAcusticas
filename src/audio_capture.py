"""Módulo de captura y análisis de audio para detección de frecuencia fundamental."""

import numpy as np
from scipy.fft import rfft, rfftfreq


class AudioNoDisponibleError(Exception):
    """Se lanza cuando no se detecta un dispositivo de audio de entrada."""


class AnalizadorAudio:
    """Captura audio desde el micrófono y detecta la frecuencia fundamental.

    Utiliza ``sounddevice`` para la grabación, ventana de Hanning para
    suavizar bordes y FFT real (``scipy.fft.rfft``) para obtener el espectro.

    Parameters
    ----------
    umbral_magnitud : float, optional
        Magnitud mínima del pico para considerar que hay señal válida
        (por defecto 1.0).

    Examples
    --------
    >>> analizador = AnalizadorAudio()
    >>> frecuencia = analizador.capturar_frecuencia(duracion=2, fs=44100)
    >>> print(f"Frecuencia detectada: {frecuencia:.2f} Hz")
    """

    def __init__(self, umbral_magnitud: float = 1.0) -> None:
        self._umbral_magnitud = umbral_magnitud

    @staticmethod
    def _verificar_microfono() -> None:
        """Verifica que exista al menos un dispositivo de entrada disponible.

        Raises
        ------
        AudioNoDisponibleError
            Si no se encuentra ningún micrófono o ``sounddevice`` no está instalado.
        """
        try:
            import sounddevice as sd
        except ImportError as exc:
            raise AudioNoDisponibleError(
                "La librería 'sounddevice' no está instalada. "
                "Ejecuta: pip install sounddevice"
            ) from exc

        try:
            dispositivo = sd.query_devices(kind="input")
            if dispositivo is None:
                raise AudioNoDisponibleError("No se detectó micrófono de entrada.")
        except sd.PortAudioError as exc:
            raise AudioNoDisponibleError(
                f"Error al consultar dispositivos de audio: {exc}"
            ) from exc

    @staticmethod
    def _grabar(duracion: float, fs: int) -> np.ndarray:
        """Graba audio mono desde el micrófono.

        Parameters
        ----------
        duracion : float
            Duración de la grabación en segundos.
        fs : int
            Frecuencia de muestreo en Hz.

        Returns
        -------
        np.ndarray
            Señal de audio 1-D (mono).
        """
        import sounddevice as sd

        grabacion = sd.rec(
            frames=int(duracion * fs),
            samplerate=fs,
            channels=1,
            dtype="float64",
        )
        sd.wait()
        return grabacion.flatten()

    def _detectar_frecuencia(self, señal: np.ndarray, fs: int) -> float:
        """Aplica ventana de Hanning + FFT para encontrar la frecuencia dominante.

        Parameters
        ----------
        señal : np.ndarray
            Señal de audio 1-D.
        fs : int
            Frecuencia de muestreo en Hz.

        Returns
        -------
        float
            Frecuencia fundamental detectada en Hz.

        Raises
        ------
        ValueError
            Si la señal no contiene energía significativa (posible silencio).
        """
        ventana = np.hanning(len(señal))
        señal_ventaneada = señal * ventana

        espectro = np.abs(rfft(señal_ventaneada))
        frecuencias = rfftfreq(len(señal_ventaneada), d=1.0 / fs)

        # Ignorar componente DC (índice 0)
        espectro[0] = 0.0

        pico_idx = np.argmax(espectro)
        magnitud_pico = espectro[pico_idx]

        if magnitud_pico < self._umbral_magnitud:
            raise ValueError(
                "No se detectó señal con energía suficiente. "
                "Verifica que la cuerda esté sonando cerca del micrófono."
            )

        return float(frecuencias[pico_idx])

    def capturar_frecuencia(self, duracion: float = 2, fs: int = 44100) -> float:
        """Graba audio y devuelve la frecuencia fundamental detectada.

        Parameters
        ----------
        duracion : float, optional
            Duración de la grabación en segundos (por defecto 2).
        fs : int, optional
            Frecuencia de muestreo en Hz (por defecto 44 100).

        Returns
        -------
        float
            Frecuencia fundamental en Hz.

        Raises
        ------
        AudioNoDisponibleError
            Si no hay micrófono disponible.
        ValueError
            Si la señal capturada no tiene energía suficiente.
        """
        self._verificar_microfono()
        señal = self._grabar(duracion, fs)
        return self._detectar_frecuencia(señal, fs)
