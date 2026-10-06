"""Detección y sanitización de datos sensibles con reglas (regex), no con modelos.

Por qué regex y no un modelo (D-06): la condición 3 del reto exige que la
decisión de qué se envía sea explícita y probable. Una regex siempre da el mismo
resultado para la misma entrada; un modelo pequeño puede "olvidar" un dato.
Límite conocido: no detecta cifras escritas en letras ("doce mil"); por eso el
salario no se escribe en campos de texto libre: tiene su propio campo numérico
que nunca se envía (ver D-08).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from .perfil import Perfil
from .reglas import extraer_montos

MARCA_NOMBRE = "[[NOMBRE]]"
MARCA_EMPLEADOR = "[[EMPLEADOR_ACTUAL]]"

CORREO_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
DPI_RE = re.compile(r"\b\d{4}\s?\d{5}\s?\d{4}\b")  # CUI/DPI guatemalteco: 13 dígitos
TELEFONO_RE = re.compile(r"(?:\+502[\s-]?\d{4}[\s-]?\d{4})|\b\d{4}-\d{4}\b|\b\d{8}\b")

_VARIANTES = {
    "a": "aáàäâ", "e": "eéèëê", "i": "iíìïî", "o": "oóòöô", "u": "uúùüû", "n": "nñ",
}


def _sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def patron_flexible(texto: str) -> re.Pattern:
    """Regex que encuentra `texto` ignorando mayúsculas y tildes ('Jose' == 'José')."""
    partes = []
    for c in _sin_acentos(texto.strip()).lower():
        if c.isspace():
            partes.append(r"\s+")
        elif c in _VARIANTES:
            partes.append(f"[{_VARIANTES[c]}]")
        else:
            partes.append(re.escape(c))
    return re.compile(r"(?<!\w)" + "".join(partes) + r"(?!\w)", re.IGNORECASE)


def _es_rango_de_anios(m: re.Match) -> bool:
    """'2019-2023' parece teléfono (dddd-dddd) pero es un rango de años."""
    txt = m.group(0)
    if re.fullmatch(r"\d{4}-\d{4}", txt):
        a, b = (int(x) for x in txt.split("-"))
        return 1900 <= a <= 2100 and 1900 <= b <= 2100
    return False


@dataclass
class ResultadoSanitizado:
    texto: str
    reemplazos: dict[str, int] = field(default_factory=dict)

    def contar(self, tipo: str, n: int = 1) -> None:
        if n:
            self.reemplazos[tipo] = self.reemplazos.get(tipo, 0) + n


def sanitizar(texto: str, perfil: Perfil) -> ResultadoSanitizado:
    res = ResultadoSanitizado(texto=texto or "")
    t = res.texto

    t, n = CORREO_RE.subn("[CORREO]", t); res.contar("correo", n)
    t, n = DPI_RE.subn("[DPI]", t); res.contar("dpi", n)

    def _tel(m: re.Match) -> str:
        if _es_rango_de_anios(m):
            return m.group(0)
        res.contar("telefono")
        return "[TELÉFONO]"

    t = TELEFONO_RE.sub(_tel, t)

    # Nombre completo primero, luego cada parte (>= 3 letras) por si aparece suelta.
    if perfil.nombre.strip():
        candidatos = [perfil.nombre] + [p for p in perfil.nombre.split() if len(p) >= 3]
        for c in candidatos:
            t, n = patron_flexible(c).subn(MARCA_NOMBRE, t); res.contar("nombre", n)
    if perfil.empleador_actual.strip():
        t, n = patron_flexible(perfil.empleador_actual).subn(MARCA_EMPLEADOR, t)
        res.contar("empleador", n)

    # Montos: se reemplazan de derecha a izquierda para no romper índices.
    for m in reversed(extraer_montos(t)):
        if m.es_dinero_probable:
            cola = " " if m.texto[-1:].isspace() else ""
            t = t[: m.inicio] + "[MONTO]" + cola + t[m.fin:]
            res.contar("monto")

    res.texto = t
    return res


def rehidratar(texto: str, perfil: Perfil) -> str:
    """Devuelve los marcadores a su valor real. Corre SOLO en el dispositivo."""
    t = texto.replace(MARCA_NOMBRE, perfil.nombre or "")
    t = t.replace(MARCA_EMPLEADOR, perfil.empleador_actual or "mi empleador actual")
    return t
