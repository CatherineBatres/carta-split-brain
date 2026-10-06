"""Cliente del modelo en la nube (Gemini) y chequeo de conectividad.

Por qué Gemini (D-09): tiene capa gratuita en AI Studio (costo 0 para el curso),
buena redacción en español y es el mismo patrón del proyecto de referencia
(Excusa Legendaria). El modelo se configura por variable de entorno porque los
nombres de modelo cambian seguido.

La nube SOLO recibe un PayloadNube que ya pasó por router.preparar_envio().
"""
from __future__ import annotations

import os
import socket
import time

from .prompts import SISTEMA_CARTA, prompt_carta
from .router import PayloadNube

MODELO_NUBE = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
TIMEOUT_MS = int(os.getenv("GEMINI_TIMEOUT_MS", "20000"))


class NubeNoDisponible(RuntimeError):
    pass


def hay_conexion(host: str = "generativelanguage.googleapis.com", puerto: int = 443,
                 timeout: float = 2.0) -> bool:
    """Chequeo barato: ¿se puede abrir un socket al endpoint de Gemini?"""
    if os.getenv("FORZAR_SIN_CONEXION") == "1":
        return False
    try:
        with socket.create_connection((host, puerto), timeout=timeout):
            return True
    except OSError:
        return False


class ClienteGemini:
    def __init__(self, modelo: str = MODELO_NUBE, api_key: str | None = None):
        self.modelo = modelo
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def configurado(self) -> bool:
        return bool(self.api_key)

    def carta(self, payload: PayloadNube, temperatura: float = 0.7) -> tuple[str, dict]:
        if not self.api_key:
            raise NubeNoDisponible("Falta GEMINI_API_KEY en .env")
        try:
            from google import genai
            from google.genai import types
        except ImportError as e:
            raise NubeNoDisponible("Instala google-genai") from e

        cliente = genai.Client(api_key=self.api_key,
                               http_options=types.HttpOptions(timeout=TIMEOUT_MS))
        t0 = time.perf_counter()
        try:
            resp = cliente.models.generate_content(
                model=self.modelo,
                contents=prompt_carta(payload.campos),
                config=types.GenerateContentConfig(
                    system_instruction=SISTEMA_CARTA, temperature=temperatura,
                    # No usamos herramientas: se apaga para evitar el aviso de AFC.
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
        except Exception as e:  # red, cuota, timeout, modelo inexistente...
            raise NubeNoDisponible(f"{type(e).__name__}: {e}") from e
        uso = getattr(resp, "usage_metadata", None)
        metricas = {
            "latencia_total_s": round(time.perf_counter() - t0, 3),
            "tokens_entrada": getattr(uso, "prompt_token_count", None),
            "tokens_salida": getattr(uso, "candidates_token_count", None),
        }
        texto = (resp.text or "").strip()
        if not texto:
            raise NubeNoDisponible("Respuesta vacía")
        return texto, metricas
