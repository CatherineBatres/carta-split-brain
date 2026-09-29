"""Rúbrica automática de calidad (criterios explícitos y justificados en D-14).

Cada criterio es binario (0/1) para que sea fácil de explicar y de auditar; la
calidad de la tarea es el promedio. La evaluación humana ciega complementa lo
que una regla no puede medir (naturalidad, persuasión).
"""
from __future__ import annotations

import json
import re
import unicodedata

from splitbrain.reglas import Hechos, es_mismo_monto, extraer_montos

STOP_ES = {"de", "la", "que", "el", "en", "y", "a", "los", "se", "del", "las", "un", "por",
           "con", "no", "una", "su", "para", "es", "al", "lo", "como", "más", "tu", "te"}
MOMENTO_RE = re.compile(
    r"entrevista|rr\.?\s?hh|recursos humanos|pregunt|primer n[uú]mero|primera (llamada|conversaci)",
    re.I)


def _normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _palabras(s: str) -> list[str]:
    return re.findall(r"\w+", s)


def es_espanol(texto: str, umbral: float = 0.12) -> bool:
    ps = [p.lower() for p in _palabras(texto)]
    return bool(ps) and sum(p in STOP_ES for p in ps) / len(ps) >= umbral


def cifras_inventadas(texto: str, h: Hechos) -> list[str]:
    """Montos o porcentajes en la nota que NO vienen de los hechos calculados."""
    permitidos = h.numeros_permitidos()
    malas = []
    for m in extraer_montos(texto):
        if m.es_dinero_probable and not any(es_mismo_monto(m.valor, p, 0.01) for p in permitidos):
            malas.append(m.texto.strip())
    if h.incremento_pct is not None:
        for p in re.findall(r"(\d+(?:[.,]\d+)?)\s?%", texto):
            if abs(float(p.replace(",", ".")) - abs(h.incremento_pct)) > 1:
                malas.append(p + "%")
    return malas


def evaluar_nota(texto: str, h: Hechos) -> dict:
    n = len(_palabras(texto))
    pct_ok = h.incremento_pct is None or bool(
        re.search(rf"\b{abs(round(h.incremento_pct))}([.,]\d)?\s?%", texto))
    inventadas = cifras_inventadas(texto, h)
    c = {
        "n_palabras": n,
        "longitud_ok": int(60 <= n <= 200),
        "cita_porcentaje": int(pct_ok),
        "sin_cifras_inventadas": int(not inventadas),
        "dice_cuando": int(bool(MOMENTO_RE.search(texto))),
        "en_espanol": int(es_espanol(texto)),
        "cifras_inventadas": "; ".join(inventadas),
    }
    c["calidad"] = round(sum(c[k] for k in ("longitud_ok", "cita_porcentaje",
                         "sin_cifras_inventadas", "dice_cuando", "en_espanol")) / 5, 3)
    return c


def evaluar_carta(texto: str, campos: dict[str, str]) -> dict:
    n = len(_palabras(texto))
    norm = _normalizar(texto)
    puesto = _normalizar(campos.get("puesto_objetivo", ""))
    empresa = _normalizar(campos.get("empresa_objetivo", ""))
    c = {
        "n_palabras": n,
        "longitud_ok": int(150 <= n <= 350),
        "marcador_nombre": int("[[NOMBRE]]" in texto),
        "sin_dinero": int("[MONTO]" not in texto and not re.search(r"salar|sueldo|pretensi", norm)
                          and not any(m.es_dinero_probable for m in extraer_montos(texto))),
        "menciona_puesto_y_empresa": int((not puesto or puesto in norm) and (not empresa or empresa in norm)),
        "saludo_y_despedida": int(bool(re.search(r"estimad|apreciad|hola|a quien", norm))
                                  and bool(re.search(r"atentamente|saludos|cordialmente|gracias", norm))),
        "en_espanol": int(es_espanol(texto)),
    }
    c["calidad"] = round(sum(v for k, v in c.items() if k != "n_palabras") / 6, 3)
    return c


def evaluar_extraccion(texto: str, oro: dict) -> dict:
    try:
        datos = json.loads(texto)
        valido = isinstance(datos, dict) and isinstance(datos.get("requisitos"), list)
    except (json.JSONDecodeError, TypeError):
        datos, valido = {}, False
    reqs = _normalizar(" | ".join(map(str, datos.get("requisitos", [])))) if valido else ""
    gold = [_normalizar(g) for g in oro.get("requisitos", [])]
    recall = (sum(g in reqs for g in gold) / len(gold)) if gold else (1.0 if valido else 0.0)
    modalidad = int(valido and _normalizar(str(datos.get("modalidad", ""))) == _normalizar(oro["modalidad"]))
    c = {"json_valido": int(valido), "recall_requisitos": round(recall, 3), "modalidad_ok": modalidad}
    c["calidad"] = round((c["json_valido"] + c["recall_requisitos"] + c["modalidad_ok"]) / 3, 3)
    return c
