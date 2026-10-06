"""Reglas heurísticas deterministas (componente local SIN modelo).

Por qué aquí no hay un modelo (docs/decisiones.md, D-05):
- La aritmética tiene que ser exacta: un 3B/4B puede decir que 12,000 -> 15,000 es
  un 30 % de aumento (es 25 %). Un cálculo nunca se equivoca.
- Es instantáneo (microsegundos) y funciona sin Ollama ni internet.
- Es 100 % reproducible y se prueba con pytest en milisegundos.
El modelo local solo REDACTA la nota a partir de estos hechos ya calculados.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .perfil import Perfil

# ---------------------------------------------------------------------------
# Detección y lectura de montos
# ---------------------------------------------------------------------------
_MONEDA = r"(?:GTQ|US\$|USD|EUR|MXN|Q\.?|\$|€)"
_NUM = r"\d{1,3}(?:[.,  ]\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d+)?"
MONTO_RE = re.compile(
    rf"(?P<moneda>{_MONEDA})?\s?(?P<num>{_NUM})\s?(?P<suf>k\b|K\b|mil\b|miles\b)?",
    re.IGNORECASE,
)


def _a_float(num: str) -> float:
    """Convierte '12,500.50', '12.500', '12 500', '12,5' a float."""
    s = num.replace(" ", " ").replace(" ", "")
    if "," in s and "." in s:
        dec = "," if s.rfind(",") > s.rfind(".") else "."
        mil = "." if dec == "," else ","
        s = s.replace(mil, "").replace(dec, ".")
    elif "," in s or "." in s:
        sep = "," if "," in s else "."
        partes = s.split(sep)
        if all(len(p) == 3 for p in partes[1:]):
            s = "".join(partes)  # separador de miles
        else:
            s = "".join(partes[:-1]) + "." + partes[-1]  # separador decimal
    return float(s)


@dataclass
class Monto:
    valor: float
    texto: str
    inicio: int
    fin: int
    con_moneda: bool
    con_sufijo: bool

    @property
    def parece_anio(self) -> bool:
        return (
            not self.con_moneda
            and not self.con_sufijo
            and self.valor.is_integer()
            and 1900 <= self.valor <= 2100
            and re.fullmatch(r"\d{4}", self.texto.strip()) is not None
        )

    @property
    def es_dinero_probable(self) -> bool:
        """Heurística: moneda, sufijo k/mil, o un número >= 1000 que no es año."""
        if self.con_moneda or self.con_sufijo:
            return True
        return self.valor >= 1000 and not self.parece_anio


def extraer_montos(texto: str) -> list[Monto]:
    montos = []
    for m in MONTO_RE.finditer(texto or ""):
        try:
            valor = _a_float(m.group("num"))
        except ValueError:
            continue
        suf = m.group("suf")
        if suf:
            valor *= 1000
        montos.append(
            Monto(
                valor=valor,
                texto=m.group(0),
                inicio=m.start(),
                fin=m.end(),
                con_moneda=bool(m.group("moneda")),
                con_sufijo=bool(suf),
            )
        )
    return montos


def equivalentes_salariales(salario: float) -> list[float]:
    """Formas en que un salario mensual podría reaparecer en un texto.

    En Guatemala se habla de salario mensual, anual x12 y anual x14
    (aguinaldo + bono 14). Si cualquiera aparece, se considera fuga.
    """
    if not salario or salario <= 0:
        return []
    return [salario, salario * 12, salario * 14]


def es_mismo_monto(a: float, b: float, tolerancia: float = 0.005) -> bool:
    return b > 0 and abs(a - b) / b <= tolerancia


# ---------------------------------------------------------------------------
# Hechos para la nota de negociación
# ---------------------------------------------------------------------------
@dataclass
class Hechos:
    moneda: str
    salario_actual: float
    salario_deseado: float
    incremento_pct: float | None
    clasificacion: str
    rango_oferta: tuple[float, float] | None
    posicion_vs_rango: str | None
    momento: str
    recordatorios: list[str] = field(default_factory=list)

    def fmt(self, valor: float) -> str:
        return f"{self.moneda}{valor:,.0f}"

    def numeros_permitidos(self) -> set[float]:
        """Números que la nota puede citar (se usan para detectar alucinaciones)."""
        nums = {self.salario_actual, self.salario_deseado}
        if self.incremento_pct is not None:
            nums.add(round(self.incremento_pct))
            nums.add(round(self.incremento_pct, 1))
        if self.rango_oferta:
            nums.update(self.rango_oferta)
        return {n for n in nums if n}


# Umbrales heurísticos (ajustables). Ver D-05: son una convención explícita y
# probada, no una verdad de mercado; el valor está en que son predecibles.
UMBRALES = [  # (máximo % de incremento, etiqueta)
    (10, "conservadora"),
    (25, "razonable"),
    (40, "ambiciosa"),
]


def clasificar_incremento(pct: float | None) -> str:
    if pct is None:
        return "sin datos suficientes"
    if pct < 0:
        return "por debajo de lo que ganas hoy"
    for tope, etiqueta in UMBRALES:
        if pct <= tope:
            return etiqueta
    return "muy ambiciosa"


def rango_de_oferta(oferta: str) -> tuple[float, float] | None:
    """Toma los montos con pinta de salario (>= 1000) de la oferta."""
    candidatos = [
        m.valor for m in extraer_montos(oferta)
        if (m.con_moneda or m.con_sufijo) and m.valor >= 1000
    ]
    if not candidatos:
        return None
    primeros = candidatos[:2]
    return (min(primeros), max(primeros))


def analizar(perfil: Perfil) -> Hechos:
    actual, deseado = perfil.salario_actual, perfil.salario_deseado
    pct = ((deseado - actual) / actual * 100) if actual > 0 and deseado > 0 else None
    clasificacion = clasificar_incremento(pct)
    rango = rango_de_oferta(perfil.oferta_texto)

    posicion = None
    if rango and deseado:
        if deseado < rango[0]:
            posicion = "por debajo del rango publicado"
        elif deseado > rango[1]:
            posicion = "por encima del rango publicado"
        else:
            posicion = "dentro del rango publicado"

    # Reglas de "cuándo mencionarlo"
    if posicion == "por debajo del rango publicado":
        momento = ("Tu expectativa está por debajo de lo que la empresa ya ofrece: "
                   "no la menciones primero y, cuando pregunten, ancla cerca del máximo del rango.")
    elif posicion == "dentro del rango publicado":
        momento = ("Puedes compartirla cuando RR. HH. la pida en la primera llamada; "
                   "ancla en la mitad superior del rango.")
    elif posicion == "por encima del rango publicado":
        momento = ("No la pongas por escrito todavía: espera a que valoren tu perfil "
                   "(después de la entrevista técnica) y justifícala con tus logros.")
    elif clasificacion in ("ambiciosa", "muy ambiciosa"):
        momento = ("Deja que la empresa dé el primer número; menciónala después de la "
                   "primera entrevista, apoyada en logros medibles.")
    else:
        momento = "Puedes compartirla cuando te la pidan en la primera conversación con RR. HH."

    recordatorios = ["No incluyas ninguna cifra salarial en la carta de interés."]
    if pct is not None and pct < 0:
        recordatorios.append("Estás pidiendo menos de lo que ganas hoy: confirma que es intencional.")

    return Hechos(
        moneda=perfil.moneda,
        salario_actual=actual,
        salario_deseado=deseado,
        incremento_pct=pct,
        clasificacion=clasificacion,
        rango_oferta=rango,
        posicion_vs_rango=posicion,
        momento=momento,
        recordatorios=recordatorios,
    )


def nota_por_reglas(h: Hechos) -> str:
    """Nota 100 % determinista: el último nivel de degradación (sin Ollama)."""
    lineas = ["Nota privada de negociación (generada por reglas, sin modelo)", ""]
    if h.incremento_pct is not None:
        lineas.append(
            f"- Pasar de {h.fmt(h.salario_actual)} a {h.fmt(h.salario_deseado)} "
            f"es un cambio de {h.incremento_pct:+.1f} %: expectativa {h.clasificacion}."
        )
    else:
        lineas.append("- Faltan datos de salario para evaluar tu expectativa.")
    if h.rango_oferta:
        lineas.append(
            f"- La oferta publica {h.fmt(h.rango_oferta[0])}–{h.fmt(h.rango_oferta[1])}; "
            f"tu expectativa está {h.posicion_vs_rango}."
        )
    lineas.append(f"- Cuándo mencionarla: {h.momento}")
    lineas.extend(f"- {r}" for r in h.recordatorios)
    return "\n".join(lineas)


def problemas_en_carta(carta: str, perfil: Perfil) -> list[str]:
    """Revisión determinista de la carta final (venga de la nube o de local)."""
    problemas = []
    objetivos = equivalentes_salariales(perfil.salario_actual) + equivalentes_salariales(
        perfil.salario_deseado
    )
    for m in extraer_montos(carta):
        if any(es_mismo_monto(m.valor, o) for o in objetivos):
            problemas.append(f"La carta menciona una cifra salarial ({m.texto.strip()}).")
    if re.search(r"pretensi[oó]n salarial|salario actual|gano actualmente", carta, re.I):
        problemas.append("La carta habla de salario; eso va en la negociación, no en la carta.")
    if "[[" in carta or re.search(r"\[(MONTO|CORREO|TELÉFONO|DPI)\]", carta):
        problemas.append("Quedaron marcadores sin reemplazar en la carta.")
    return problemas
