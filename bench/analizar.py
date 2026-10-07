"""Resume el benchmark: tablas en Markdown + gráficas PNG para el artículo.

Uso:
    python -m bench.analizar                 # usa resultados/bench_metricas.csv
    python -m bench.analizar --simulado      # usa resultados/simulado/
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from bench.hoja import resumir_ciega  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
COLORES = ["#2a78d6", "#eb6834"]  # paleta categórica validada (azul, naranja)
TINTA, TINTA_2, REJILLA = "#1f1f1e", "#5f5e58", "#e6e5df"


def _barras(df: pd.DataFrame, columna: str, titulo: str, unidad: str, archivo: Path) -> None:
    tabla = df.groupby(["tarea", "modelo"])[columna].median().unstack("modelo")
    modelos = list(tabla.columns)
    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=150)
    ancho = 0.8 / len(modelos)
    for i, m in enumerate(modelos):
        xs = [x + i * ancho for x in range(len(tabla))]
        barras = ax.bar(xs, tabla[m], width=ancho - 0.03, color=COLORES[i % 2], label=m)
        ax.bar_label(barras, fmt="%.2f", fontsize=8, color=TINTA_2, padding=2)
    ax.set_xticks([x + ancho * (len(modelos) - 1) / 2 for x in range(len(tabla))], tabla.index)
    ax.set_title(titulo, loc="left", color=TINTA, fontsize=11)
    ax.set_ylabel(unidad, color=TINTA_2)
    ax.grid(axis="y", color=REJILLA)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)


def tramos_lentos(serie: pd.Series, umbral: float = 0.6) -> pd.Series:
    """Marca las respuestas generadas a menos del 60 % de la velocidad normal del modelo."""
    return serie < umbral * serie.median()


def grafica_ritmo(df: pd.DataFrame, archivo: Path, titulo: str) -> None:
    """Tokens por segundo de cada respuesta, en el orden en que se generaron.

    Si el equipo se calienta y baja el rendimiento, aquí se ve como un escalón (D-30).
    """
    fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=160)
    for i, (modelo, g) in enumerate(df.groupby("modelo", sort=False)):
        g = g.reset_index(drop=True)
        ax.plot(g.index + 1, g["tokens_por_s"], color=COLORES[i % 2], lw=2, marker="o", ms=3.5,
                label=modelo)
        lentos = tramos_lentos(g["tokens_por_s"])
        if lentos.any():
            ini, fin = lentos[lentos].index.min() + 1, lentos[lentos].index.max() + 1
            ax.axvspan(ini - 0.5, fin + 0.5, color="#f1f0ea", zorder=0)
            v = g.loc[lentos, "tokens_por_s"].median()
            ax.text((ini + fin) / 2, v + g["tokens_por_s"].max() * 0.08,
                    f"tramo lento: {v:.0f} tokens/s", ha="center", fontsize=8.5, color=TINTA)
    ax.set_ylim(0, df["tokens_por_s"].max() * 1.25)
    ax.set_xlabel("respuesta número (en orden de ejecución)", color=TINTA_2, fontsize=9)
    ax.set_ylabel("tokens por segundo", color=TINTA_2, fontsize=9)
    ax.set_title(titulo, loc="left", color=TINTA, fontsize=11)
    ax.grid(axis="y", color=REJILLA)
    ax.set_axisbelow(True)
    ax.tick_params(colors=TINTA_2, length=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    if df["modelo"].nunique() > 1:
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(archivo)
    plt.close(fig)


def _humana(dir_: Path) -> pd.DataFrame | None:
    """Une la hoja ciega calificada (las NOTAS) con la clave, si ya la llenaste."""
    hoja, clave = dir_ / "evaluacion_ciega.csv", dir_ / "crudo" / "clave_ciega.json"
    if not hoja.exists() or not clave.exists():
        return None
    resumen, hechas, _ = resumir_ciega(hoja, clave, ["claridad_1a5", "utilidad_1a5"],
                                       "inventa_datos_si_no")
    if not hechas:
        return None
    return pd.DataFrame(resumen).set_index("modelo")


def main(simulado: bool) -> None:
    dir_ = RAIZ / "resultados" / ("simulado" if simulado else "")
    df = pd.read_csv(dir_ / "bench_metricas.csv")
    img = (RAIZ / "docs" / "img" / ("simulado" if simulado else ""))
    img.mkdir(parents=True, exist_ok=True)

    if "orden" in df:
        df = df.sort_values("orden").reset_index(drop=True)
    agregados = {"calidad": "mean", "latencia_total_s": "median",
                 "tokens_por_s": "median", "ps_size_mb": "median", "ps_vram_mb": "median"}
    agregados = {k: v for k, v in agregados.items() if k in df}
    resumen = df.groupby(["tarea", "modelo"]).agg(agregados).round(3)
    resumen["latencia_max_s"] = df.groupby(["tarea", "modelo"])["latencia_total_s"].max().round(3)
    # D-30: el tiempo al primer token solo vale en la primera repetición. En las siguientes el
    # prompt es idéntico, Ollama lo tiene en caché y el número sale artificialmente bajo.
    if "ttft_s" in df:
        resumen["primer_token_s"] = (df[df["rep"] == 0].groupby(["tarea", "modelo"])["ttft_s"]
                                     .median().round(3))
    lentas = df.groupby("modelo", sort=False)["tokens_por_s"].transform(tramos_lentos)
    ritmo = pd.DataFrame({
        "respuestas": df.groupby("modelo", sort=False).size(),
        "a_ritmo_lento": lentas.groupby(df["modelo"], sort=False).sum().astype(int),
        "tokens_s_normal": df[~lentas].groupby("modelo", sort=False)["tokens_por_s"].median(),
        "tokens_s_lento": df[lentas].groupby("modelo", sort=False)["tokens_por_s"].median(),
    }).round(1)

    criterios = [c for c in ["longitud_ok", "cita_porcentaje", "sin_cifras_inventadas", "dice_cuando",
                             "en_espanol", "marcador_nombre", "sin_dinero",
                             "menciona_puesto_y_empresa", "saludo_y_despedida", "json_valido",
                             "recall_requisitos", "modalidad_ok"] if c in df]
    por_criterio = df.groupby(["tarea", "modelo"])[criterios].mean().round(2)

    _barras(df, "calidad", "Calidad por tarea (rúbrica automática, 0–1)", "calidad", img / "calidad.png")
    _barras(df, "latencia_total_s", "Latencia total por tarea (mediana)", "segundos", img / "latencia.png")
    # D-27: la memoria que vale es la que reporta Ollama (/api/ps), no el RSS del proceso:
    # con el modelo en la tarjeta gráfica, el RSS sale en ~100 MB y no dice nada.
    if "ps_size_mb" in df and df["ps_size_mb"].notna().any():
        _barras(df, "ps_size_mb", "Memoria del modelo cargado, según Ollama (mediana)", "MB",
                img / "memoria.png")

    grafica_ritmo(df, img / "ritmo.png", "Velocidad de cada respuesta, en orden de ejecución")

    frio_path = dir_ / "arranque_en_frio.json"
    frio = json.loads(frio_path.read_text()) if frio_path.exists() else {}
    humana = _humana(dir_)

    md = ["# Resultados del benchmark" + (" (SIMULADO: no usar)" if simulado else ""), "",
          "## Resumen por tarea y modelo", "", resumen.to_markdown(), "",
          "## Criterios de la rúbrica (proporción que cumple)", "", por_criterio.to_markdown(), "",
          "## Ritmo: ¿bajó la velocidad durante la corrida?", "", ritmo.to_markdown(), "",
          "*A ritmo lento*: respuestas generadas a menos del 60 % de la velocidad normal del "
          "modelo (señal de que el equipo se calentó o estaba ocupado).", "",
          "## Arranque en frío", "", "```json", json.dumps(frio, indent=2), "```", ""]
    if humana is not None:
        md += ["## Evaluación humana ciega de las notas (1–5)", "", humana.to_markdown(), ""]
    rel = "../" * (len(dir_.relative_to(RAIZ).parts)) + str(img.relative_to(RAIZ)).replace("\\", "/")
    md += ["## Gráficas", "", f"![calidad]({rel}/calidad.png)", f"![latencia]({rel}/latencia.png)",
           f"![memoria]({rel}/memoria.png)", f"![ritmo]({rel}/ritmo.png)"]
    (dir_ / "resumen.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:12]))
    print(ritmo.to_string())
    print(f"\nEscrito {dir_ / 'resumen.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    main(ap.parse_args().simulado)
