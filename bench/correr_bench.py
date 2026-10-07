"""Evaluación B: Gemma vs Qwen en las tareas que SOLO hacen los modelos locales.

Uso (versión ligera, recomendada en laptop):
    python -m bench.correr_bench --simulado                    # prueba el script sin Ollama
    python -m bench.correr_bench --modelos gemma4:e4b          # un modelo...
    python -m bench.correr_bench --modelos qwen3.5:4b          # ...y después el otro
    python -m bench.correr_bench --estado                      # ¿cuánto falta?
    python -m bench.correr_bench --armar                       # recalifica sin usar el modelo

Por defecto mide la NOTA y la EXTRACCIÓN, con 2 repeticiones. La carta ya se midió tres
veces en la evaluación A (comparar_tres); se puede agregar con  --tareas nota carta extraccion.

Se puede interrumpir y retomar (D-29): cada respuesta se guarda en disco al instante. Si la
computadora se apaga o cierras la ventana, vuelve a correr el mismo comando y sigue donde
se quedó. Entre respuestas hace pausas para que el equipo no se caliente.

Controles de justicia (D-13): mismos casos, mismos prompts, mismas opciones (temperature,
seed, num_ctx, num_predict), think desactivado, un modelo cargado a la vez, arranque en frío
medido aparte y descarga del modelo al terminar.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time
from pathlib import Path

from bench import rubrica
from bench.hoja import leer_hoja
from splitbrain import reglas
from splitbrain.local_llm import ClienteOllama, Generacion, OllamaNoDisponible
from splitbrain.perfil import Perfil
from splitbrain.prompts import (SISTEMA_CARTA, SISTEMA_EXTRACCION, SISTEMA_NOTA,
                                prompt_carta, prompt_extraccion, prompt_nota)
from splitbrain.router import construir_payload

RAIZ = Path(__file__).resolve().parent.parent
CASOS = RAIZ / "bench" / "casos.json"
TAREAS_POR_DEFECTO = ["nota", "extraccion"]
SEMILLA = 42


def arranque_en_frio(cliente: ClienteOllama) -> dict:
    cliente.descargar()
    time.sleep(1)
    g = cliente.generar("Responde solo: listo")
    return {"carga_modelo_s": g.metricas.get("carga_modelo_s"),
            "latencia_total_s": g.metricas.get("latencia_total_s"),
            "ps_size_mb": g.metricas.get("ps_size_mb"),
            "ps_vram_mb": g.metricas.get("ps_vram_mb")}


class ClienteSimulado:
    """Solo para verificar el código del benchmark. Sus números NO son resultados."""

    def __init__(self, modelo: str):
        self.modelo = modelo
        self.rng = random.Random(sum(map(ord, modelo)))

    def generar(self, prompt, sistema="", formato_json=False, semilla=None):
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
                          "tokens_salida": 200, "carga_modelo_s": 0, "ps_size_mb": 3000.0,
                          "ps_vram_mb": 3000.0})

    def descargar(self):
        pass


# --------------------------------------------------------------------------- progreso en disco
def _leer_progreso(archivo: Path) -> list[dict]:
    if not archivo.exists():
        return []
    filas = []
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        try:
            filas.append(json.loads(linea))
        except json.JSONDecodeError:
            continue  # una línea a medio escribir por un apagón: se ignora y se repite
    return filas


def _reparar(archivo: Path) -> None:
    """Si un apagón dejó la última línea a medias, la quita.

    Sin esto, la siguiente respuesta se pegaría a esa línea rota y se perdería también.
    """
    if not archivo.exists():
        return
    crudo = archivo.read_text(encoding="utf-8")
    buenas = [json.dumps(f, ensure_ascii=False) for f in _leer_progreso(archivo)]
    limpio = "\n".join(buenas) + ("\n" if buenas else "")
    if limpio != crudo:
        archivo.write_text(limpio, encoding="utf-8")


def _guardar(archivo: Path, fila: dict) -> None:
    """Agrega una línea y la fuerza a disco: si la máquina se apaga, esto ya quedó."""
    with open(archivo, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(fila, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def calificar(tarea: str, texto: str, caso: dict) -> dict:
    """Aplica la rúbrica VIGENTE. Se llama al armar los archivos, no al generar: así, si una
    regla se corrige, basta con  --armar  para recalificar sin volver a usar el modelo."""
    perfil = Perfil(**caso["perfil"])
    if tarea == "nota":
        return rubrica.evaluar_nota(texto, reglas.analizar(perfil))
    if tarea == "carta":
        return rubrica.evaluar_carta(texto, construir_payload(perfil).campos,
                                     caso["oro"]["requisitos"])
    return rubrica.evaluar_extraccion(texto, caso["oro"])


def _plan(casos: list[dict], modelos: list[str], tareas: list[str], reps: int) -> list[tuple]:
    plan = []
    for modelo in modelos:
        for caso in casos:
            for tarea in tareas:
                if tarea == "extraccion" and not caso["perfil"].get("oferta_texto"):
                    continue
                plan += [(modelo, caso["id"], tarea, rep) for rep in range(reps)]
    return plan


def correr(modelos: list[str], reps: int, tareas: list[str], simulado: bool,
           pausa: float = 3, cada: int = 15, descanso: float = 60,
           reiniciar: bool = False, solo_estado: bool = False, solo_armar: bool = False) -> Path:
    casos = json.loads(CASOS.read_text(encoding="utf-8"))
    por_id = {c["id"]: c for c in casos}
    salida = RAIZ / "resultados" / ("simulado" if simulado else "")
    crudo = salida / "crudo"
    crudo.mkdir(parents=True, exist_ok=True)
    progreso = crudo / "progreso.jsonl"
    frio_path = salida / "arranque_en_frio.json"
    if reiniciar or simulado:
        for f in (progreso, frio_path):
            f.unlink(missing_ok=True)

    _reparar(progreso)
    hechas = {(f["modelo"], f["caso"], f["tarea"], f["rep"]) for f in _leer_progreso(progreso)}
    plan = _plan(casos, modelos, tareas, reps)
    pendientes = [p for p in plan if p not in hechas]
    print(f"Plan: {len(plan)} respuestas · hechas: {len(plan) - len(pendientes)} · "
          f"faltan: {len(pendientes)}")
    for modelo in modelos:
        n = sum(1 for p in pendientes if p[0] == modelo)
        print(f"   {modelo}: faltan {n}")
    if solo_estado:
        return salida
    if solo_armar:
        _armar(progreso, salida, crudo)
        print(f"Archivos recalculados con la rúbrica actual en {salida}")
        return salida

    frio = json.loads(frio_path.read_text(encoding="utf-8")) if frio_path.exists() else {}
    contador = 0
    for modelo in modelos:
        mios = [p for p in pendientes if p[0] == modelo]
        if not mios:
            continue
        cliente = ClienteSimulado(modelo) if simulado else ClienteOllama(modelo)
        if not simulado:
            if not cliente.disponible():
                raise SystemExit(f"El modelo {modelo} no está en Ollama. Corre: ollama pull {modelo}")
            if modelo not in frio:
                frio[modelo] = arranque_en_frio(cliente)
                frio_path.write_text(json.dumps(frio, indent=2), encoding="utf-8")
                print(f"[{modelo}] arranque en frío: {frio[modelo]}")
            cliente.generar("Hola")  # calentamiento: no se mide

        for _, cid, tarea, rep in mios:
            caso = por_id[cid]
            perfil = Perfil(**caso["perfil"])
            hechos = reglas.analizar(perfil)
            campos = construir_payload(perfil).campos
            prompt, sistema, js = {
                "nota": (prompt_nota(hechos, caso["oro"]["requisitos"]), SISTEMA_NOTA, False),
                "carta": (prompt_carta(campos), SISTEMA_CARTA, False),
                "extraccion": (prompt_extraccion(perfil.oferta_texto), SISTEMA_EXTRACCION, True),
            }[tarea]
            try:
                # D-30: con la misma semilla, las repeticiones salían idénticas palabra por
                # palabra. Con 42 + rep, cada repetición es una muestra distinta y reproducible.
                g = cliente.generar(prompt, sistema, formato_json=js, semilla=SEMILLA + rep)
            except OllamaNoDisponible as e:
                print(f"⚠️ Ollama dejó de responder ({str(e)[:80]}). Lo hecho ya está guardado; "
                      "vuelve a correr el mismo comando para continuar.")
                _armar(progreso, salida, crudo)
                return salida
            cal = calificar(tarea, g.texto, caso)
            _guardar(progreso, {"modelo": modelo, "caso": cid, "tarea": tarea, "rep": rep,
                                "orden": len(hechas) + contador, **g.metricas, "texto": g.texto})
            contador += 1
            print(f"[{modelo}] {cid} {tarea} r{rep}: calidad={cal['calidad']} "
                  f"lat={g.metricas.get('latencia_total_s')}s   ({contador}/{len(pendientes)})")
            if not simulado:
                if cada and contador % cada == 0 and contador < len(pendientes):
                    print(f"   ⏸ descanso de {int(descanso)} s para que el equipo se enfríe...")
                    time.sleep(descanso)
                else:
                    time.sleep(pausa)
        if not simulado:
            cliente.descargar()

    _armar(progreso, salida, crudo)
    print(f"\nListo. Resultados en {salida}")
    return salida


# --------------------------------------------------------------------------- archivos finales
def _armar(progreso: Path, salida: Path, crudo: Path) -> None:
    """Construye el CSV, los textos y la hoja ciega a partir de lo guardado hasta ahora."""
    filas = _leer_progreso(progreso)
    if not filas:
        return
    por_id = {c["id"]: c for c in json.loads(CASOS.read_text(encoding="utf-8"))}
    metricas = [{**{k: v for k, v in f.items() if k != "texto"},
                 **calificar(f["tarea"], f["texto"], por_id[f["caso"]])} for f in filas]
    columnas = sorted({k for f in metricas for k in f}, key=lambda k: (k not in
                      ("modelo", "caso", "tarea", "rep"), k))
    with open(salida / "bench_metricas.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas)
        w.writeheader()
        w.writerows(metricas)
    textos = [{k: f[k] for k in ("modelo", "caso", "tarea", "texto")} for f in filas
              if f["rep"] == 0]
    (crudo / "salidas.jsonl").write_text(
        "\n".join(json.dumps(t, ensure_ascii=False) for t in textos), encoding="utf-8")
    _hoja_ciega(textos, salida, crudo)


COLS_HOJA = ["claridad_1a5", "utilidad_1a5", "inventa_datos_si_no", "comentario"]


def _hoja_ciega(textos: list[dict], salida: Path, crudo: Path) -> None:
    """Hoja para calificar a mano SIN saber qué modelo escribió cada texto (D-15)."""
    # D-28: solo las NOTAS. Las cartas ya se califican a ciegas en la evaluación A.
    evaluables = [t for t in textos if t["tarea"] == "nota"]
    hoja, clave_path = salida / "evaluacion_ciega.csv", crudo / "clave_ciega.json"

    # D-30: si ya existe una hoja, se conservan las calificaciones de las notas que siguen
    # siendo las mismas (se reconocen por su texto). Antes se comparaba solo la cantidad de
    # notas, y una hoja vieja de otro modelo podía pasar por actual.
    previas: dict[tuple, list[str]] = {}
    if hoja.exists():
        viejas = leer_hoja(hoja)
        for f in viejas:
            notas = [f.get(c, "") for c in COLS_HOJA]
            if any(notas):
                previas[(f.get("caso", ""), f.get("texto", ""))] = notas
        en_hoja = sorted((f.get("caso", ""), f.get("texto", "")) for f in viejas)
        if clave_path.exists() and en_hoja == sorted((t["caso"], t["texto"].strip())
                                                     for t in evaluables):
            return  # mismas notas: no se toca

    random.Random(7).shuffle(evaluables)
    clave = {}
    with open(hoja, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "caso", "tarea", "texto", *COLS_HOJA])
        for i, t in enumerate(evaluables):
            id_ = f"T{i:03d}"
            clave[id_] = t["modelo"]
            w.writerow([id_, t["caso"], t["tarea"], t["texto"],
                        *previas.get((t["caso"], t["texto"].strip()), [""] * len(COLS_HOJA))])
    clave_path.write_text(json.dumps(clave, indent=2), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", nargs="+", default=["gemma4:e4b", "qwen3.5:4b"])
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--tareas", nargs="+", default=TAREAS_POR_DEFECTO,
                    choices=["nota", "carta", "extraccion"])
    ap.add_argument("--pausa", type=float, default=3, help="segundos entre respuestas")
    ap.add_argument("--cada", type=int, default=15, help="descanso largo cada N respuestas")
    ap.add_argument("--descanso", type=float, default=60, help="segundos del descanso largo")
    ap.add_argument("--estado", action="store_true", help="solo muestra cuánto falta")
    ap.add_argument("--armar", action="store_true",
                    help="recalifica y reescribe los archivos con lo ya generado, sin usar el modelo")
    ap.add_argument("--reiniciar", action="store_true", help="borra el progreso y empieza de cero")
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args()
    correr(a.modelos, a.reps, a.tareas, a.simulado, a.pausa, a.cada, a.descanso,
           a.reiniciar, a.estado, a.armar)
