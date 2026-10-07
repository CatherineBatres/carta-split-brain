"""Cliente del componente local: Ollama por su API REST en localhost.

Por qué `requests` contra la API REST y no el paquete `ollama` (D-10): queremos
ver y medir cada campo de la respuesta (load_duration, eval_count, eval_duration)
y el tiempo al primer token con streaming; con HTTP plano no hay capas ocultas y
el README puede mostrar exactamente la llamada.
"""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field

import requests

HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
MODELO_POR_DEFECTO = os.getenv("MODELO_LOCAL", "gemma4:e4b")

# Opciones idénticas para cualquier modelo (justicia del benchmark, D-13).
OPCIONES = {"temperature": 0.2, "seed": 42, "num_ctx": 4096, "num_predict": 700}


class OllamaNoDisponible(RuntimeError):
    pass


@dataclass
class Generacion:
    texto: str
    modelo: str
    metricas: dict = field(default_factory=dict)


def _rss_ollama_mb() -> float | None:
    """Memoria residente (MB) de los procesos de Ollama, si psutil está instalado."""
    try:
        import psutil
    except ImportError:
        return None
    total = 0
    for p in psutil.process_iter(["name", "memory_info"]):
        try:
            if "ollama" in (p.info["name"] or "").lower():
                total += p.info["memory_info"].rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return round(total / 1024 / 1024, 1) if total else None


class _MuestreadorMemoria(threading.Thread):
    """Muestrea el RSS de Ollama cada 100 ms para obtener el pico durante la generación."""

    def __init__(self):
        super().__init__(daemon=True)
        self.pico = 0.0
        self._alto = threading.Event()

    def run(self):
        while not self._alto.is_set():
            v = _rss_ollama_mb()
            if v:
                self.pico = max(self.pico, v)
            time.sleep(0.1)

    def detener(self) -> float | None:
        self._alto.set()
        self.join(timeout=1)
        return self.pico or None


class ClienteOllama:
    def __init__(self, modelo: str = MODELO_POR_DEFECTO, host: str = HOST, timeout: float = 180):
        self.modelo = modelo
        self.host = host.rstrip("/")
        self.timeout = timeout

    def disponible(self) -> bool:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=2)
            nombres = {m["name"] for m in r.json().get("models", [])}
            return self.modelo in nombres or f"{self.modelo}:latest" in nombres
        except (requests.RequestException, ValueError):
            return False

    def descargar(self) -> None:
        """Saca el modelo de memoria (keep_alive=0). Sirve para medir un arranque en frío real
        y para que un modelo no le quite memoria al siguiente."""
        try:
            requests.post(f"{self.host}/api/generate",
                          json={"model": self.modelo, "keep_alive": 0}, timeout=30)
        except requests.RequestException:
            pass

    def memoria_modelo(self) -> dict:
        """Lo que Ollama reporta del modelo cargado (/api/ps): tamaño total y en VRAM."""
        try:
            for m in requests.get(f"{self.host}/api/ps", timeout=2).json().get("models", []):
                if m.get("name", "").startswith(self.modelo):
                    return {
                        "ps_size_mb": round(m.get("size", 0) / 1024 / 1024, 1),
                        "ps_vram_mb": round(m.get("size_vram", 0) / 1024 / 1024, 1),
                    }
        except (requests.RequestException, ValueError):
            pass
        return {}

    def generar(self, prompt: str, sistema: str = "", formato_json: bool = False,
                semilla: int | None = None) -> Generacion:
        cuerpo = {
            "model": self.modelo,
            "messages": ([{"role": "system", "content": sistema}] if sistema else [])
            + [{"role": "user", "content": prompt}],
            "stream": True,
            "options": OPCIONES if semilla is None else {**OPCIONES, "seed": semilla},
            "think": False,  # D-12: sin razonamiento visible, mismo trato a ambos modelos
        }
        if formato_json:
            cuerpo["format"] = "json"

        muestreador = _MuestreadorMemoria()
        muestreador.start()
        t0 = time.perf_counter()
        ttft = None
        trozos: list[str] = []
        final: dict = {}
        try:
            r = self._post(cuerpo)
            for linea in r.iter_lines():
                if not linea:
                    continue
                dato = json.loads(linea)
                if "error" in dato:
                    raise OllamaNoDisponible(dato["error"])
                contenido = dato.get("message", {}).get("content", "")
                if contenido and ttft is None:
                    ttft = time.perf_counter() - t0
                trozos.append(contenido)
                if dato.get("done"):
                    final = dato
        except requests.RequestException as e:
            raise OllamaNoDisponible(str(e)) from e
        finally:
            pico = muestreador.detener()

        total = time.perf_counter() - t0
        ns = 1e9
        eval_count = final.get("eval_count", 0)
        eval_dur = final.get("eval_duration", 0) / ns
        metricas = {
            "latencia_total_s": round(total, 3),
            "ttft_s": round(ttft, 3) if ttft else None,
            "carga_modelo_s": round(final.get("load_duration", 0) / ns, 3),
            "tokens_entrada": final.get("prompt_eval_count"),
            "tokens_salida": eval_count,
            "tokens_por_s": round(eval_count / eval_dur, 1) if eval_dur else None,
            "rss_pico_mb": pico,
            **self.memoria_modelo(),
        }
        return Generacion(texto="".join(trozos).strip(), modelo=self.modelo, metricas=metricas)

    def _post(self, cuerpo: dict) -> requests.Response:
        r = requests.post(f"{self.host}/api/chat", json=cuerpo, stream=True, timeout=self.timeout)
        if r.status_code == 400 and "think" in r.text.lower():
            # Algunos modelos no aceptan el parámetro think: se reintenta sin él.
            cuerpo = {k: v for k, v in cuerpo.items() if k != "think"}
            r = requests.post(f"{self.host}/api/chat", json=cuerpo, stream=True, timeout=self.timeout)
        if r.status_code != 200:
            raise OllamaNoDisponible(f"HTTP {r.status_code}: {r.text[:200]}")
        return r
