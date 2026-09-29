"""Prompts. Son los MISMOS para Gemma y Qwen (requisito del benchmark) y la carta
usa el mismo prompt en la nube y en local, para comparar solo el modelo."""
from __future__ import annotations

from .reglas import Hechos
from .sensibles import MARCA_EMPLEADOR, MARCA_NOMBRE

SISTEMA_CARTA = (
    "Eres una redactora experta en cartas de interés en español para Latinoamérica. "
    "Escribe cartas concretas, sin clichés, de 180 a 300 palabras."
)


def prompt_carta(campos: dict[str, str]) -> str:
    datos = "\n".join(f"- {k}: {v}" for k, v in campos.items())
    return f"""Escribe una carta de interés para acompañar un CV.

Datos (ya anonimizados):
{datos}

Reglas obligatorias:
1. Firma con el marcador {MARCA_NOMBRE} tal cual, sin cambiarlo.
2. Si mencionas el empleador actual, usa el marcador {MARCA_EMPLEADOR} tal cual.
3. NO menciones salarios, cifras de dinero, ni expectativas económicas.
4. No inventes empresas, títulos ni logros que no estén en los datos.
5. Omite cualquier frase que contenga [MONTO], [CORREO], [TELÉFONO] o [DPI].
6. Entre 180 y 300 palabras. Incluye saludo y despedida.
Devuelve solo la carta."""


SISTEMA_NOTA = (
    "Eres una asesora de negociación salarial. Hablas en segunda persona, directo y "
    "con empatía. Nunca inventas cifras."
)


def prompt_nota(h: Hechos, requisitos: list[str] | None = None) -> str:
    rango = (
        f"{h.fmt(h.rango_oferta[0])} a {h.fmt(h.rango_oferta[1])} ({h.posicion_vs_rango})"
        if h.rango_oferta else "la oferta no publica rango"
    )
    pct = f"{h.incremento_pct:+.1f} %" if h.incremento_pct is not None else "sin dato"
    return f"""Redacta una nota privada de negociación (80 a 160 palabras) con estos HECHOS
ya calculados. No recalcules ni agregues cifras nuevas.

HECHOS
- Salario actual: {h.fmt(h.salario_actual)}
- Salario deseado: {h.fmt(h.salario_deseado)}
- Cambio: {pct} -> expectativa {h.clasificacion}
- Rango de la oferta: {rango}
- Cuándo mencionarla: {h.momento}
- Recordatorios: {' '.join(h.recordatorios)}
- Requisitos de la oferta: {', '.join(requisitos) if requisitos else 'no disponibles'}

Incluye: qué tan realista es la expectativa, cuándo mencionarla y un argumento para
defenderla. Devuelve solo la nota."""


SISTEMA_EXTRACCION = "Extraes información de ofertas de empleo y respondes SOLO JSON válido."


def prompt_extraccion(oferta: str) -> str:
    return f"""Lee esta oferta de trabajo y devuelve un JSON con esta forma exacta:
{{"puesto": str, "requisitos": [str], "modalidad": "remoto"|"presencial"|"híbrido"|"no indica"}}
- "requisitos": habilidades o experiencia pedidas, en frases cortas (máx. 6).

OFERTA:
{oferta}"""
