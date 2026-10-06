"""Lectura tolerante de las hojas de evaluación ciega.

Excel en español suele guardar los CSV con punto y coma y en codificación Windows-1252, y
la gente escribe "Sí", "si", "x" o "1". Esta función acepta todo eso para que calificar
en Excel no rompa el análisis (D-28).
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

SI = {"si", "sí", "s", "x", "1", "yes", "y", "true", "verdadero"}
NO = {"no", "n", "0", "false", "falso"}


def leer_hoja(ruta: Path) -> list[dict]:
    crudo = Path(ruta).read_bytes()
    for cod in ("utf-8-sig", "cp1252"):
        try:
            texto = crudo.decode(cod)
            break
        except UnicodeDecodeError:
            continue
    primera = texto.split("\n", 1)[0]
    sep = ";" if primera.count(";") > primera.count(",") else ("\t" if "\t" in primera else ",")
    return [{(k or "").strip(): (v or "").strip() for k, v in fila.items()}
            for fila in csv.DictReader(texto.splitlines(keepends=True), delimiter=sep)]


def _numero(v: str) -> float | None:
    try:
        x = float(v.replace(",", "."))
    except ValueError:
        return None
    return x if 1 <= x <= 5 else None


def resumir_ciega(hoja: Path, clave: Path, columnas_1a5: list[str],
                  columna_si_no: str | None = None) -> tuple[list[dict], int, int]:
    """Une la hoja calificada con la clave y promedia por modelo.

    Devuelve (resumen por modelo, textos calificados, textos en total).
    """
    filas = leer_hoja(hoja)
    quien = json.loads(Path(clave).read_text(encoding="utf-8"))
    por_modelo: dict[str, list[dict]] = {}
    calificadas = 0
    for f in filas:
        notas = {c: _numero(f.get(c, "")) for c in columnas_1a5}
        if all(v is None for v in notas.values()):
            continue
        calificadas += 1
        modelo = quien.get(f.get("id", ""))
        if not modelo:
            continue
        if columna_si_no:
            v = f.get(columna_si_no, "").lower()
            notas[columna_si_no] = 1.0 if v in SI else (0.0 if v in NO else None)
        por_modelo.setdefault(modelo, []).append(notas)

    resumen = []
    for modelo, notas in por_modelo.items():
        r = {"modelo": modelo, "n": len(notas)}
        for c in columnas_1a5:
            xs = [n[c] for n in notas if n[c] is not None]
            r[c] = round(statistics.mean(xs), 2) if xs else None
        if columna_si_no:
            xs = [n[columna_si_no] for n in notas if n.get(columna_si_no) is not None]
            r["inventa_n"] = int(sum(xs)) if xs else None
            r["inventa_de"] = len(xs)
        resumen.append(r)
    return resumen, calificadas, len(filas)
