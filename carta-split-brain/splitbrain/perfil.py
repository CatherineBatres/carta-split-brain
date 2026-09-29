"""Modelo de datos de la persona usuaria.

Cada campo del perfil DEBE estar clasificado en `router.CAMPOS_NUBE` o en
`router.CAMPOS_SOLO_LOCAL`. Hay una prueba (tests/test_router.py) que falla si
alguien agrega un campo nuevo sin clasificarlo. Ver docs/decisiones.md (D-07).
"""
from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass
class Perfil:
    # --- Identidad (sensible) ---
    nombre: str = ""
    empleador_actual: str = ""

    # --- Dinero (sensible; el salario actual NUNCA sale del dispositivo) ---
    salario_actual: float = 0.0
    salario_deseado: float = 0.0
    moneda: str = "Q"

    # --- Contexto profesional (se envía a la nube ya sanitizado) ---
    puesto_actual: str = ""
    puesto_objetivo: str = ""
    empresa_objetivo: str = ""
    resumen_experiencia: str = ""
    logros: str = ""
    oferta_texto: str = ""
    tono: str = "profesional y cercano"

    @classmethod
    def nombres_de_campos(cls) -> set[str]:
        return {f.name for f in fields(cls)}
