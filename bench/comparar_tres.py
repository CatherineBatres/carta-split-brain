"""Compara la CARTA escrita por Gemma, Qwen (local) y Gemini (nube) con los mismos perfiles.

Uso:
    python -m bench.comparar_tres --simulado                 # prueba el script sin Ollama ni API key
    python -m bench.comparar_tres --casos c01 c02            # solo algunos perfiles (prueba rápida)
    python -m bench.comparar_tres                            # los 10 perfiles
    python -m bench.comparar_tres --reevaluar                # recalifica sin volver a generar
    python -m bench.comparar_tres --carpeta tres_modelos_v2  # guarda en otra carpeta (no pisa la anterior)
    python -m bench.comparar_tres --ciega --carpeta tres_modelos_v2   # resume tu evaluación a ciegas

Por qué solo la carta (D-22): es la única tarea que hacen tanto la nube como lo local.
La nota privada NUNCA se manda a Gemini, ni para comparar: contiene el salario.

A Gemini se le envía exactamente lo que enviaría la app: el payload que pasó por
router.preparar_envio() (allowlist + sanitizador + guardián).
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv

from bench import rubrica
from bench.hoja import resumir_ciega
from splitbrain.local_llm import ClienteOllama, OllamaNoDisponible
from splitbrain.nube import ClienteGemini, NubeNoDisponible
from splitbrain.perfil import Perfil
from splitbrain.prompts import SISTEMA_CARTA, prompt_carta
from splitbrain.router import FugaDetectada, PayloadNube, preparar_envio
from splitbrain.sensibles import rehidratar

RAIZ = Path(__file__).resolve().parent.parent
TEMPERATURA = 0.2  # la misma para los tres (los locales usan 0.2 en local_llm.OPCIONES)
PAUSA_NUBE_S = 4   # respiro entre llamadas para no chocar con el límite de la capa gratuita

# Métricas que se guardan por carta además de la latencia total (D-25).
EXTRA = ["ttft_s", "tokens_por_s", "tokens_entrada", "tokens_salida", "rss_pico_mb",
         "ps_size_mb", "ps_vram_mb"]
CRITERIOS = ["longitud_ok", "marcador_nombre", "sin_dinero", "menciona_puesto_y_empresa",
             "saludo_y_despedida", "en_espanol"]
COLORES = ["#2a78d6", "#eb6834", "#1baf7a"]  # paleta categórica validada; orden fijo por modelo
TINTA, TINTA_2, REJILLA = "#1f1f1e", "#5f5e58", "#e6e5df"

CARTA_SIMULADA = ("Estimado equipo:\n" + "Me interesa mucho el puesto y su empresa. " * 25
                  + "\nAtentamente,\n[[NOMBRE]]")


def generar_local(modelo: str, campos: dict, simulado: bool) -> tuple[str, dict]:
    if simulado:
        return CARTA_SIMULADA, {"latencia_total_s": round(random.uniform(5, 15), 2),
                                "rss_pico_mb": 5000.0, "tokens_por_s": 30.0, "ttft_s": 0.5}
    g = ClienteOllama(modelo).generar(prompt_carta(campos), SISTEMA_CARTA)
    return g.texto, g.metricas


def generar_nube(payload, simulado: bool) -> tuple[str, dict]:
    if simulado:
        return CARTA_SIMULADA, {"latencia_total_s": round(random.uniform(2, 5), 2),
                                "tokens_entrada": 400, "tokens_salida": 350}
    return ClienteGemini().carta(payload, temperatura=TEMPERATURA)


def _calentar(nombre: str, lugar: str) -> float:
    """Primera llamada, que no se mide como generación. Devuelve cuánto tardó (arranque)."""
    print(f"🔥 Calentando {nombre} (esta llamada no se mide)...")
    t0 = time.perf_counter()
    try:
        if lugar == "local":
            ClienteOllama(nombre).descargar()   # arranque en frío real (D-27)
            time.sleep(1)
            ClienteOllama(nombre).generar("Responde solo: listo")
        else:  # también la nube: la primera llamada paga la conexión (justicia, D-25)
            ClienteGemini().carta(PayloadNube(campos={"puesto_objetivo": "prueba"}),
                                  temperatura=TEMPERATURA)
            time.sleep(PAUSA_NUBE_S)
    except (OllamaNoDisponible, NubeNoDisponible) as e:
        print(f"   (el calentamiento falló: {str(e)[:80]})")
    seg = round(time.perf_counter() - t0 - (PAUSA_NUBE_S if lugar == "nube" else 0), 1)
    print(f"   arranque (carga + primera respuesta): {seg} s")
    return seg


def _calificar(texto: str, campos: dict, caso: dict) -> dict:
    if not texto:
        return {"calidad": 0}
    return rubrica.evaluar_carta(texto, campos, caso["oro"]["requisitos"])


def reevaluar(salida: Path, casos: list[dict]) -> None:
    """Recalifica las cartas ya generadas con la rúbrica actual (sin llamar a ningún modelo)."""
    crudo = salida / "cartas_crudas.jsonl"
    if not crudo.exists():
        raise SystemExit(f"No existe {crudo}. Corre primero la comparación completa.")
    por_id = {c["id"]: c for c in casos}
    filas, preparados, vistos, motores = [], [], set(), []
    for linea in crudo.read_text(encoding="utf-8").splitlines():
        f = json.loads(linea)
        caso = por_id[f["caso"]]
        perfil = Perfil(**caso["perfil"])
        payload = preparar_envio(perfil)
        if f["caso"] not in vistos:
            vistos.add(f["caso"])
            preparados.append((caso, perfil, payload))
        if (f["modelo"], f["lugar"]) not in motores:
            motores.append((f["modelo"], f["lugar"]))
        cal = _calificar(f["texto"], payload.campos, caso)
        filas.append({**f, **cal})
        if cal.get("cuales_sin_respaldo") or any(cal.get(k) == 0 for k in CRITERIOS):
            fallos = [k for k in CRITERIOS if cal.get(k) == 0]
            print(f"{f['caso']} · {f['modelo']:<12} calidad={cal['calidad']}"
                  f"{'  falló: ' + ', '.join(fallos) if fallos else ''}"
                  f"{'  ⚠️ sin respaldo: ' + cal['cuales_sin_respaldo'] if cal.get('cuales_sin_respaldo') else ''}")
    arr = salida / "arranque.json"
    arranque = json.loads(arr.read_text(encoding="utf-8")) if arr.exists() else {}
    _escribir(filas, preparados, motores, salida, arranque, hoja_ciega=False)


COLS_CIEGA = ["naturalidad_1a5", "persuasion_1a5", "lista_para_enviar_1a5"]


def ciega(salida: Path) -> None:
    """Une tu hoja ciega calificada con la clave y muestra el promedio por modelo."""
    hoja, clave = salida / "evaluacion_ciega_cartas.csv", salida / "clave_ciega_cartas.json"
    if not hoja.exists() or not clave.exists():
        raise SystemExit(f"No encuentro la hoja ciega o la clave en {salida}")
    resumen, hechas, total = resumir_ciega(hoja, clave, COLS_CIEGA, "inventa_datos_si_no")
    if not hechas:
        raise SystemExit("La hoja aún no tiene calificaciones. Pon números del 1 al 5, guarda "
                         "y vuelve a correr este comando.")

    def v(x):
        return "—" if x is None else f"{x:.2f}"

    lineas = [f"# Evaluación humana a ciegas ({hechas} de {total} cartas calificadas)", "",
              "| Modelo | Cartas | Naturalidad | Persuasión | Lista para enviar | Inventa datos |",
              "|---|---|---|---|---|---|"]
    for r in sorted(resumen, key=lambda r: -(r["lista_para_enviar_1a5"] or 0)):
        inv = "—" if r["inventa_n"] is None else f"{r['inventa_n']} de {r['inventa_de']}"
        lineas.append(f"| {r['modelo']} | {r['n']} | {v(r['naturalidad_1a5'])} | "
                      f"{v(r['persuasion_1a5'])} | {v(r['lista_para_enviar_1a5'])} | {inv} |")
    lineas += ["", "Escala 1–5 (5 = mejor). *Inventa datos*: cartas marcadas con \"sí\"."]
    (salida / "evaluacion_humana.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))
    if hechas < total:
        print(f"\n⚠️ Faltan {total - hechas} cartas por calificar.")
    print(f"\n📁 Guardado en {salida / 'evaluacion_humana.md'}")


def main(modelos_locales: list[str], ids: list[str] | None, simulado: bool,
         solo_reevaluar: bool = False, carpeta: str = "tres_modelos",
         sobrescribir: bool = False, solo_ciega: bool = False) -> None:
    load_dotenv()
    casos = json.loads((RAIZ / "bench" / "casos.json").read_text(encoding="utf-8"))
    if ids:
        casos = [c for c in casos if c["id"] in ids]

    salida = RAIZ / "resultados" / ("simulado" if simulado else "") / carpeta
    salida.mkdir(parents=True, exist_ok=True)
    if solo_ciega:
        return ciega(salida)
    if solo_reevaluar:
        return reevaluar(salida, casos)
    if (salida / "cartas_crudas.jsonl").exists() and not (simulado or sobrescribir):
        # D-27: una corrida anterior se perdió por regenerar en la misma carpeta.
        raise SystemExit(
            f"⚠️ Ya hay una corrida guardada en {salida}.\n"
            "   Para no perderla, usa otra carpeta:   --carpeta tres_modelos_v3\n"
            "   Si de verdad quieres reemplazarla:    --sobrescribir")

    if not simulado:
        for m in modelos_locales:
            if not ClienteOllama(m).disponible():
                raise SystemExit(f"❌ Falta el modelo {m}. Corre:  ollama pull {m}")
        if not ClienteGemini().configurado():
            raise SystemExit("❌ Falta GEMINI_API_KEY en el archivo .env")

    # Se preparan los payloads una sola vez (lo MISMO que haría la app).
    preparados = []
    for caso in casos:
        perfil = Perfil(**caso["perfil"])
        try:
            preparados.append((caso, perfil, preparar_envio(perfil)))
        except FugaDetectada as e:
            print(f"⚠️ {caso['id']}: el guardián bloqueó el envío ({e}); se salta este caso.")

    # Un modelo a la vez, con calentamiento previo (D-22): así no medimos la carga
    # del modelo a memoria ni recargas por alternar modelos.
    motores = [(m, "local") for m in modelos_locales] + [("gemini", "nube")]
    filas, arranque = [], {}
    for nombre, lugar in motores:
        if not simulado:
            arranque[nombre] = _calentar(nombre, lugar)
        for caso, perfil, payload in preparados:
            campos = payload.campos
            try:
                if lugar == "local":
                    texto, met = generar_local(nombre, campos, simulado)
                else:
                    texto, met = generar_nube(payload, simulado)
                    if not simulado:
                        time.sleep(PAUSA_NUBE_S)
                error = ""
            except (OllamaNoDisponible, NubeNoDisponible) as e:
                texto, met, error = "", {}, str(e)[:200]

            cal = _calificar(texto, campos, caso)
            fila = {"caso": caso["id"], "modelo": nombre, "lugar": lugar,
                    "latencia_total_s": met.get("latencia_total_s"),
                    **{k: met.get(k) for k in EXTRA},
                    "error": error, **cal, "texto": texto}
            filas.append(fila)
            fallos = [k for k in CRITERIOS if cal.get(k) == 0]
            print(f"{caso['id']} · {nombre:<12} calidad={cal['calidad']:<5} "
                  f"latencia={met.get('latencia_total_s')}s"
                  f"{'  falló: ' + ', '.join(fallos) if fallos else ''}"
                  f"{'  ⚠️ sin respaldo: ' + cal['cuales_sin_respaldo'] if cal.get('cuales_sin_respaldo') else ''}"
                  f"{'  ❌ ' + error if error else ''}")
        if lugar == "local" and not simulado:
            # Libera la memoria antes del siguiente modelo: si el anterior sigue cargado,
            # el nuevo puede quedar repartido entre GPU y CPU y parecer más lento (D-27).
            ClienteOllama(nombre).descargar()

    (salida / "arranque.json").write_text(json.dumps(arranque, indent=2), encoding="utf-8")
    _escribir(filas, preparados, motores, salida, arranque)


# --------------------------------------------------------------------------- salidas
def resumir(filas: list[dict], motores: list, arranque: dict) -> list[dict]:
    """Una fila por modelo con las estadísticas que van al README y al artículo."""
    def med(xs):
        xs = [x for x in xs if x is not None]
        return round(statistics.median(xs), 2) if xs else None

    resumen = []
    for nombre, lugar in motores:
        xs = [f for f in filas if f["modelo"] == nombre and not f.get("error")]
        if not xs:
            continue
        lat = [f["latencia_total_s"] for f in xs if f.get("latencia_total_s") is not None]
        resumen.append({
            "modelo": nombre, "lugar": lugar, "n": len(xs),
            "calidad_media": round(statistics.mean(f["calidad"] for f in xs), 3),
            "cartas_perfectas": sum(f["calidad"] == 1 for f in xs),
            "cartas_con_alerta": sum(bool(f.get("requisitos_sin_respaldo")) for f in xs),
            "lat_mediana_s": med(lat),
            "lat_min_s": round(min(lat), 2) if lat else None,
            "lat_max_s": round(max(lat), 2) if lat else None,
            "lat_desv_s": round(statistics.stdev(lat), 2) if len(lat) > 1 else None,
            "arranque_s": arranque.get(nombre),
            "ttft_mediana_s": med([f.get("ttft_s") for f in xs]),
            "tokens_por_s": med([f.get("tokens_por_s") for f in xs]),
            "ram_pico_mb": max((f.get("rss_pico_mb") or 0 for f in xs), default=0) or None,
            "modelo_en_memoria_mb": med([f.get("ps_size_mb") for f in xs]),
            "modelo_en_gpu_mb": med([f.get("ps_vram_mb") for f in xs]),
            "tokens_entrada": med([f.get("tokens_entrada") for f in xs]),
            "tokens_salida": med([f.get("tokens_salida") for f in xs]),
        })
    return resumen


def grafica_latencia(filas: list[dict], motores: list, archivo: Path) -> None:
    """Un punto por carta y una marca en la mediana: muestra velocidad Y estabilidad."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    nombres = [n for n, _ in motores]
    fig, ax = plt.subplots(figsize=(7.5, 1.1 + 0.75 * len(nombres)), dpi=160)
    tope = 0
    for i, nombre in enumerate(nombres):
        lat = [f["latencia_total_s"] for f in filas
               if f["modelo"] == nombre and f.get("latencia_total_s") is not None]
        if not lat:
            continue
        y = len(nombres) - 1 - i
        tope = max(tope, max(lat))
        ax.scatter(lat, [y] * len(lat), s=70, color=COLORES[i % 3], edgecolors="white",
                   linewidths=1.5, zorder=3, alpha=0.9)
        m = statistics.median(lat)
        ax.plot([m, m], [y - 0.28, y + 0.28], color=TINTA, lw=2, zorder=4)
        ax.text(m, y + 0.36, f"mediana {m:.1f} s", ha="center", va="bottom", fontsize=8.5,
                color=TINTA)
    ax.set_yticks(range(len(nombres)), list(reversed(nombres)), fontsize=10, color=TINTA)
    ax.set_ylim(-0.6, len(nombres) - 0.2)
    ax.set_xlim(0, tope * 1.08 if tope else 1)
    ax.set_xlabel("segundos por carta (cada punto es un perfil)", color=TINTA_2, fontsize=9)
    ax.set_title("Latencia por carta: velocidad y estabilidad", loc="left", color=TINTA,
                 fontsize=11)
    ax.grid(axis="x", color=REJILLA)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, colors=TINTA_2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(REJILLA)
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)


def _tabla_md(resumen: list[dict]) -> str:
    def v(x, suf=""):
        return "—" if x is None else f"{x}{suf}"
    filas = [
        "| Modelo | Dónde | Calidad (rúbrica) | Cartas 6/6 | Con alerta | Latencia mediana | Mín–máx | "
        "Desv. | Arranque | Tokens/s | Modelo en memoria | De eso, en GPU | RAM del proceso |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in resumen:
        filas.append(
            f"| {r['modelo']} | {'☁️ nube' if r['lugar'] == 'nube' else '🖥️ local'} | "
            f"{r['calidad_media']:.2f} | {r['cartas_perfectas']}/{r['n']} | "
            f"{r['cartas_con_alerta']}/{r['n']} | {v(r['lat_mediana_s'], ' s')} | "
            f"{v(r['lat_min_s'])}–{v(r['lat_max_s'])} s | {v(r['lat_desv_s'], ' s')} | "
            f"{v(r['arranque_s'], ' s')} | {v(r['tokens_por_s'])} | "
            f"{v(r['modelo_en_memoria_mb'], ' MB')} | {v(r['modelo_en_gpu_mb'], ' MB')} | "
            f"{v(r['ram_pico_mb'], ' MB')} |")
    return "\n".join(filas)


def _escribir(filas, preparados, motores, salida: Path, arranque: dict | None = None,
              hoja_ciega: bool = True) -> None:
    arranque = arranque or {}
    # 0) Textos crudos + métricas: permiten recalificar con --reevaluar sin llamar a los modelos
    claves = ["caso", "modelo", "lugar", "latencia_total_s", *EXTRA, "error", "texto"]
    (salida / "cartas_crudas.jsonl").write_text("\n".join(
        json.dumps({k: f.get(k) for k in claves}, ensure_ascii=False) for f in filas),
        encoding="utf-8")

    resultados = {(f["caso"], f["modelo"]): f for f in filas}
    lectura = ["# Cartas: Gemma vs Qwen vs Gemini", "",
               f"Temperatura {TEMPERATURA} para los tres. Mismos datos sanitizados.", ""]
    for caso, perfil, payload in preparados:
        lectura += [f"## {caso['id']} · {caso['descripcion']}", "",
                    f"**Puesto:** {perfil.puesto_objetivo} en {perfil.empresa_objetivo}", "",
                    "<details><summary>Lo que recibió Gemini</summary>", "", "```json",
                    payload.como_texto(), "```", "</details>", ""]
        for nombre, lugar in motores:
            f = resultados.get((caso["id"], nombre))
            if not f:
                continue
            alerta = (f"  · ⚠️ sin respaldo: {f['cuales_sin_respaldo']}"
                      if f.get("cuales_sin_respaldo") else "")
            lectura += [f"### {'☁️' if lugar == 'nube' else '🖥️'} {nombre} · calidad "
                        f"{f['calidad']} · {f['latencia_total_s']} s{alerta}", "",
                        rehidratar(f["texto"], perfil) if f["texto"] else f"*Error: {f['error']}*",
                        ""]

    # 1) Métricas por carta
    cols = ["caso", "modelo", "lugar", "latencia_total_s", *EXTRA, "calidad", "n_palabras",
            *CRITERIOS, "requisitos_sin_respaldo", "cuales_sin_respaldo", "error"]
    with open(salida / "metricas.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)

    # 2) Lado a lado para leer
    (salida / "cartas_lado_a_lado.md").write_text("\n".join(lectura), encoding="utf-8")

    # 3) Hoja ciega (sin nombres de modelo) + clave aparte.
    #    Al reevaluar NO se reescribe: borraría las calificaciones que ya pusiste.
    if hoja_ciega:
        ciegas = [f for f in filas if f["texto"]]
        random.Random(11).shuffle(ciegas)
        clave = {}
        with open(salida / "evaluacion_ciega_cartas.csv", "w", newline="",
                  encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "caso", "texto", "naturalidad_1a5", "persuasion_1a5",
                        "lista_para_enviar_1a5", "inventa_datos_si_no", "comentario"])
            for i, f in enumerate(ciegas):
                clave[f"C{i:03d}"] = f["modelo"]
                w.writerow([f"C{i:03d}", f["caso"], f["texto"], "", "", "", "", ""])
        (salida / "clave_ciega_cartas.json").write_text(json.dumps(clave, indent=2),
                                                        encoding="utf-8")

    # 4) Resumen por modelo: tabla (resumen.md) + gráfica (latencia.png) + pantalla
    resumen = resumir(filas, motores, arranque)
    grafica_latencia(filas, motores, salida / "latencia.png")
    (salida / "resumen.md").write_text(
        "# Resumen: carta en Gemma, Qwen y Gemini\n\n" + _tabla_md(resumen)
        + "\n\n- *Con alerta*: cartas que mencionan requisitos de la oferta que la persona no dijo "
          "tener (revisar a mano; NO es un puntaje).\n- *Arranque*: carga del modelo desde cero + "
          "primera respuesta; no entra en la latencia.\n- *Modelo en memoria*: lo que reporta Ollama "
          "(`/api/ps`); es el dato de memoria que vale. *RAM del proceso* es solo la memoria "
          "principal del proceso de Ollama: si el modelo corre en la tarjeta gráfica, casi todo "
          "está en la GPU y este número sale muy bajo.\n\n![latencia](latencia.png)\n",
        encoding="utf-8")

    print("\n=== Resumen por modelo ===")
    for r in resumen:
        print(f"{r['modelo']:<12} calidad={r['calidad_media']:.2f}  "
              f"mediana={r['lat_mediana_s']}s  (mín {r['lat_min_s']} · máx {r['lat_max_s']})  "
              f"alertas={r['cartas_con_alerta']}/{r['n']}"
              f"{'  memoria del modelo=' + str(r['modelo_en_memoria_mb']) + ' MB' if r['modelo_en_memoria_mb'] else ''}"
              f"{' (GPU: ' + str(r['modelo_en_gpu_mb']) + ' MB)' if r['modelo_en_gpu_mb'] else ''}"
              f"{'  tokens/s=' + str(r['tokens_por_s']) if r['tokens_por_s'] else ''}")
    print(f"\n📁 Revisa: {salida}")
    print("   · resumen.md             → tabla comparativa + gráfica")
    print("   · cartas_lado_a_lado.md  → léelas comparando")
    print("   · evaluacion_ciega_cartas.csv → califícalas sin saber el modelo")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", nargs="+", default=["gemma4:e4b", "qwen3.5:4b"])
    ap.add_argument("--casos", nargs="+", help="ids de bench/casos.json, p. ej. c01 c08")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--reevaluar", action="store_true",
                    help="recalifica las cartas ya guardadas con la rúbrica actual")
    ap.add_argument("--carpeta", default="tres_modelos",
                    help="subcarpeta de resultados/ donde se guarda o se lee la corrida")
    ap.add_argument("--sobrescribir", action="store_true",
                    help="permite reemplazar una corrida ya guardada en esa carpeta")
    ap.add_argument("--ciega", action="store_true",
                    help="resume tu hoja de evaluación ciega ya calificada")
    a = ap.parse_args()
    main(a.modelos, a.casos, a.simulado, a.reevaluar, a.carpeta, a.sobrescribir, a.ciega)
