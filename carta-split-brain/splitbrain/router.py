"""Router explícito: decide QUÉ sale a la nube. No usa ningún modelo (condición 3).

Diseño (D-07): lista de permitidos (allowlist), no lista de bloqueados.
- Un campo solo viaja si está en CAMPOS_NUBE. Si mañana alguien agrega
  `perfil.telefono`, por defecto NO sale, y la prueba de clasificación falla
  hasta que alguien decida conscientemente dónde va.
- Aun los campos permitidos pasan por el sanitizador y luego por un guardián
  (`verificar_payload`) que falla cerrado: si detecta una fuga, no se envía nada.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .perfil import Perfil
from .reglas import equivalentes_salariales, es_mismo_monto, extraer_montos
from .sensibles import CORREO_RE, patron_flexible, sanitizar

CAMPOS_NUBE: frozenset[str] = frozenset({
    "puesto_actual", "puesto_objetivo", "empresa_objetivo",
    "resumen_experiencia", "logros", "oferta_texto", "tono",
})
CAMPOS_SOLO_LOCAL: frozenset[str] = frozenset({
    "nombre", "empleador_actual", "salario_actual", "salario_deseado", "moneda",
})


class FugaDetectada(Exception):
    """Se lanza cuando el payload contiene algo que no debe salir del dispositivo."""

    def __init__(self, motivos: list[str]):
        self.motivos = motivos
        super().__init__("; ".join(motivos))


@dataclass
class PayloadNube:
    campos: dict[str, str]
    reemplazos: dict[str, int] = field(default_factory=dict)

    def como_texto(self) -> str:
        return json.dumps(self.campos, ensure_ascii=False, indent=2)


def construir_payload(perfil: Perfil) -> PayloadNube:
    campos: dict[str, str] = {}
    total: dict[str, int] = {}
    for nombre in sorted(CAMPOS_NUBE):
        valor = str(getattr(perfil, nombre) or "")
        if not valor.strip():
            continue
        r = sanitizar(valor, perfil)
        campos[nombre] = r.texto
        for k, v in r.reemplazos.items():
            total[k] = total.get(k, 0) + v
    return PayloadNube(campos=campos, reemplazos=total)


def verificar_payload(payload: PayloadNube, perfil: Perfil) -> None:
    """Guardián final. Falla cerrado: ante la duda, no se envía."""
    motivos: list[str] = []

    extra = set(payload.campos) - CAMPOS_NUBE
    if extra:
        motivos.append(f"Campos no permitidos en el payload: {sorted(extra)}")

    texto = payload.como_texto()

    objetivos = {
        "salario actual": equivalentes_salariales(perfil.salario_actual),
        "salario deseado": equivalentes_salariales(perfil.salario_deseado),
    }
    for m in extraer_montos(texto):
        for etiqueta, valores in objetivos.items():
            if any(es_mismo_monto(m.valor, v) for v in valores):
                motivos.append(f"Aparece el {etiqueta} ({m.texto.strip()}).")

    if perfil.nombre.strip() and patron_flexible(perfil.nombre).search(texto):
        motivos.append("Aparece el nombre de la persona.")
    if perfil.empleador_actual.strip() and patron_flexible(perfil.empleador_actual).search(texto):
        motivos.append("Aparece el empleador actual.")
    if CORREO_RE.search(texto):
        motivos.append("Aparece un correo electrónico.")

    if motivos:
        raise FugaDetectada(motivos)


def preparar_envio(perfil: Perfil) -> PayloadNube:
    """Único punto de salida hacia la nube: construir + verificar."""
    payload = construir_payload(perfil)
    verificar_payload(payload, perfil)
    return payload
