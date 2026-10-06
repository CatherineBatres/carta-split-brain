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

    agregados = {"calidad": "mean", "latencia_total_s": "median", "ttft_s": "median",
                 "tokens_por_s": "median", "ps_size_mb": "median", "ps_vram_mb": "median"}
    agregados = {k: v for k, v in agregados.items() if k in df}
    resumen = df.groupby(["tarea", "modelo"]).agg(agregados).round(3)
    p95 = df.groupby(["tarea", "modelo"])["latencia_total_s"].quantile(0.95).round(3)
    resumen["latencia_p95_s"] = p95

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

    frio_path = dir_ / "arranque_en_frio.json"
    frio = json.loads(frio_path.read_text()) if frio_path.exists() else {}
    humana = _humana(dir_)

    md = ["# Resultados del benchmark" + (" (SIMULADO: no usar)" if simulado else ""), "",
          "## Resumen por tarea y modelo", "", resumen.to_markdown(), "",
          "## Criterios de la rúbrica (proporción que cumple)", "", por_criterio.to_markdown(), "",
          "## Arranque en frío", "", "```json", json.dumps(frio, indent=2), "```", ""]
    if humana is not None:
        md += ["## Evaluación humana ciega de las notas (1–5)", "", humana.to_markdown(), ""]
    md += ["## Gráficas", "", f"![calidad]({img.relative_to(RAIZ)}/calidad.png)",
           f"![latencia]({img.relative_to(RAIZ)}/latencia.png)",
           f"![memoria]({img.relative_to(RAIZ)}/memoria.png)"]
    (dir_ / "resumen.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:12]))
    print(f"\nEscrito {dir_ / 'resumen.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    main(ap.parse_args().simulado)
