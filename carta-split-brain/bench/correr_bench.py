"""Benchmark Gemma vs Qwen en las TRES tareas locales de la app.

Uso:
    python -m bench.correr_bench --modelos gemma4:e4b qwen3.5:4b --reps 3
    python -m bench.correr_bench --simulado       # prueba el pipeline sin Ollama

Controles de justicia (D-13): mismos casos, mismos prompts, mismas opciones
(temperature, seed, num_ctx, num_predict), think desactivado, un modelo cargado a
la vez, arranque en frío medido aparte y descarga del modelo entre corridas.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import time
from pathlib import Path

import requests

from bench import rubrica
from splitbrain import reglas
from splitbrain.local_llm import HOST, ClienteOllama, Generacion
from splitbrain.perfil import Perfil
from splitbrain.prompts import (SISTEMA_CARTA, SISTEMA_EXTRACCION, SISTEMA_NOTA,
                                prompt_carta, prompt_extraccion, prompt_nota)
from splitbrain.router import construir_payload

RAIZ = Path(__file__).resolve().parent.parent
CASOS = RAIZ / "bench" / "casos.json"


def descargar(modelo: str) -> None:
    """keep_alive=0 saca el modelo de memoria: así medimos cada uno desde cero."""
    try:
        requests.post(f"{HOST}/api/generate", json={"model": modelo, "keep_alive": 0}, timeout=30)
    except requests.RequestException:
        pass


def arranque_en_frio(cliente: ClienteOllama) -> dict:
    descargar(cliente.modelo)
    time.sleep(1)
    g = cliente.generar("Responde solo: listo")
    return {"carga_modelo_s": g.metricas.get("carga_modelo_s"),
            "latencia_total_s": g.metricas.get("latencia_total_s"),
            "rss_pico_mb": g.metricas.get("rss_pico_mb"),
            "ps_size_mb": g.metricas.get("ps_size_mb"),
            "ps_vram_mb": g.metricas.get("ps_vram_mb")}


class ClienteSimulado:
    """Solo para verificar el código del benchmark. Sus números NO son resultados."""

    def __init__(self, modelo: str):
        self.modelo = modelo
        self.rng = random.Random(sum(map(ord, modelo)))

    def generar(self, prompt, sistema="", formato_json=False):
        lat = self.rng.uniform(1, 4)
        if formato_json:
            texto = json.dumps({"puesto": "x", "requisitos": ["python", "sql"], "modalidad": "remoto"})
        elif "nota privada" in prompt:
            texto = ("Tu expectativa es razonable. Menciónala cuando RR. HH. pregunte "
                     "en la primera llamada y apóyala en tus logros medibles. " * 3)
        else:
            texto = "Estimado equipo:\n" + "Me interesa mucho el puesto y la empresa. " * 25 + \
                    "\nAtentamente,\n[[NOMBRE]]"
        return Generacion(texto, self.modelo, {"latencia_total_s": round(lat, 3),
                          "ttft_s": round(lat / 5, 3), "tokens_por_s": round(self.rng.uniform(15, 40), 1),
                          "tokens_salida": 200, "carga_modelo_s": 0, "rss_pico_mb": 3000.0})


def correr(modelos: list[str], reps: int, tareas: list[str], simulado: bool) -> Path:
    casos = json.loads(CASOS.read_text(encoding="utf-8"))
    salida = RAIZ / "resultados" / ("simulado" if simulado else "")
    crudo = salida / "crudo"
    crudo.mkdir(parents=True, exist_ok=True)

    filas, textos, frio = [], [], {}
    for modelo in modelos:
        cliente = ClienteSimulado(modelo) if simulado else ClienteOllama(modelo)
        if not simulado:
            if not cliente.disponible():
                raise SystemExit(f"El modelo {modelo} no está en Ollama. Corre: ollama pull {modelo}")
            frio[modelo] = arranque_en_frio(cliente)
            print(f"[{modelo}] arranque en frío: {frio[modelo]}")
            cliente.generar("Hola")  # calentamiento: no se mide

        for caso in casos:
            perfil = Perfil(**caso["perfil"])
            hechos = reglas.analizar(perfil)
            campos = construir_payload(perfil).campos
            trabajos = {
                "nota": (prompt_nota(hechos, caso["oro"]["requisitos"]), SISTEMA_NOTA, False),
                "carta": (prompt_carta(campos), SISTEMA_CARTA, False),
                "extraccion": (prompt_extraccion(perfil.oferta_texto), SISTEMA_EXTRACCION, True),
            }
            for tarea in tareas:
                if tarea == "extraccion" and not perfil.oferta_texto:
                    continue
                prompt, sistema, js = trabajos[tarea]
                for rep in range(reps):
                    g = cliente.generar(prompt, sistema, formato_json=js)
                    if tarea == "nota":
                        cal = rubrica.evaluar_nota(g.texto, hechos)
                    elif tarea == "carta":
                        cal = rubrica.evaluar_carta(g.texto, campos)
                    else:
                        cal = rubrica.evaluar_extraccion(g.texto, caso["oro"])
                    filas.append({"modelo": modelo, "caso": caso["id"], "tarea": tarea, "rep": rep,
                                  **g.metricas, **cal})
                    if rep == 0:
                        textos.append({"modelo": modelo, "caso": caso["id"], "tarea": tarea,
                                       "texto": g.texto})
                    print(f"[{modelo}] {caso['id']} {tarea} r{rep}: calidad={cal['calidad']} "
                          f"lat={g.metricas.get('latencia_total_s')}s")
        if not simulado:
            descargar(modelo)

    columnas = sorted({k for f in filas for k in f}, key=lambda k: (k not in
                      ("modelo", "caso", "tarea", "rep"), k))
    with open(salida / "bench_metricas.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas)
    (salida / "arranque_en_frio.json").write_text(json.dumps(frio, indent=2), encoding="utf-8")
    (crudo / "salidas.jsonl").write_text(
        "\n".join(json.dumps(t, ensure_ascii=False) for t in textos), encoding="utf-8")
    _hoja_ciega(textos, salida, crudo)
    print(f"\nListo. Resultados en {salida}")
    return salida


def _hoja_ciega(textos: list[dict], salida: Path, crudo: Path) -> None:
    """Hoja para calificar a mano SIN saber qué modelo escribió cada texto (D-15)."""
    evaluables = [t for t in textos if t["tarea"] in ("nota", "carta")]
    random.Random(7).shuffle(evaluables)
    clave = {}
    with open(salida / "evaluacion_ciega.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "caso", "tarea", "texto", "naturalidad_1a5", "utilidad_1a5",
                    "persuasion_1a5", "comentario"])
        for i, t in enumerate(evaluables):
            id_ = f"T{i:03d}"
            clave[id_] = t["modelo"]
            w.writerow([id_, t["caso"], t["tarea"], t["texto"], "", "", "", ""])
    (crudo / "clave_ciega.json").write_text(json.dumps(clave, indent=2), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", nargs="+", default=["gemma4:e4b", "qwen3.5:4b"])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--tareas", nargs="+", default=["nota", "carta", "extraccion"])
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args()
    correr(a.modelos, a.reps, a.tareas, a.simulado)
