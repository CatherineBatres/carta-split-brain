"""Orquestador: une las piezas y aplica la degradación elegante (D-11).

Carta:  nube (Gemini)  ->  modelo local (Ollama)  ->  plantilla determinista
Nota:   modelo local   ->  reglas deterministas          (NUNCA la nube)

Así, sin internet y hasta sin Ollama, la app sigue entregando algo útil (cond. 4).
"""
from __future__ import annotations

import json
import re

from dataclasses import dataclass, field

from . import reglas
from .local_llm import ClienteOllama, OllamaNoDisponible
from .nube import ClienteGemini, NubeNoDisponible, hay_conexion
from .perfil import Perfil

from .prompts import (SISTEMA_CARTA, SISTEMA_EXTRACCION, SISTEMA_NOTA, prompt_carta,
                      prompt_extraccion, prompt_nota)
from .router import FugaDetectada, PayloadNube, construir_payload, preparar_envio
from .sensibles import MARCA_NOMBRE, rehidratar


@dataclass
class Resultado:
    carta: str
    nota: str
    origen_carta: str          # "nube" | "local" | "plantilla"
    origen_nota: str           # "local" | "reglas"
    payload: PayloadNube | None  # exactamente lo que salió (o habría salido) a la nube
    envio_nube: bool
    requisitos: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    metricas: dict = field(default_factory=dict)


_MARCAS_CIEGAS = re.compile(r"\[(MONTO|CORREO|TELÉFONO|DPI)\]")


def sin_frases_censuradas(texto: str) -> str:
    """Quita las frases que quedaron con [MONTO], [CORREO]... (no aportan a una carta)."""
    frases = re.split(r"(?<=[.!?;])\s+", texto.strip())
    limpio = " ".join(f for f in frases if not _MARCAS_CIEGAS.search(f)).strip()
    return re.sub(r";$", ".", limpio)


def carta_plantilla(campos: dict[str, str]) -> str:
    puesto = campos.get("puesto_objetivo", "el puesto")
    empresa = campos.get("empresa_objetivo", "su organización")
    exp = sin_frases_censuradas(campos.get("resumen_experiencia", ""))
    logros = sin_frases_censuradas(campos.get("logros", ""))
    return (
        f"Estimado equipo de selección de {empresa}:\n\n"
        f"Me interesa postularme al puesto de {puesto}. "
        + (f"{exp} " if exp else "")
        + (f"Entre mis logros recientes destaco: {logros} " if logros else "")
        + (f"Cuento con experiencia en lo que el puesto requiere: {campos['requisitos_detectados']}. "
           if campos.get("requisitos_detectados") else "")
        + "\n\nCreo que mi experiencia puede aportar valor a su equipo y me encantaría "
        "conversar sobre cómo contribuir a sus objetivos. Adjunto mi CV.\n\n"
        f"Atentamente,\n{MARCA_NOMBRE}\n\n"
        "(Carta generada con plantilla sin conexión: revísala y personalízala.)"
    )


def generar(
    perfil: Perfil,
    local: ClienteOllama | None = None,
    nube: ClienteGemini | None = None,
    usar_nube: bool = True,
) -> Resultado:
    local = local or ClienteOllama()
    nube = nube or ClienteGemini()
    avisos: list[str] = []
    metricas: dict = {}

    # 1) Hechos: reglas locales, instantáneas.
    hechos = reglas.analizar(perfil)

    # 1b) Requisitos de la oferta: modelo local (lenguaje libre, no hay regla que sirva).
    requisitos: list[str] = []
    if perfil.oferta_texto.strip():
        try:
            g = local.generar(prompt_extraccion(perfil.oferta_texto), SISTEMA_EXTRACCION,
                              formato_json=True)
            datos = json.loads(g.texto)
            requisitos = [str(x) for x in datos.get("requisitos", [])][:6]
            metricas["extraccion"] = g.metricas
        except (OllamaNoDisponible, ValueError, AttributeError, TypeError):
            avisos.append("No se pudieron extraer los requisitos de la oferta en local.")

    # 2) Nota privada: modelo local -> reglas. Jamás toca la red externa.
    try:
        g = local.generar(prompt_nota(hechos, requisitos), SISTEMA_NOTA)
        nota, origen_nota = g.texto, "local"
        metricas["nota"] = g.metricas
    except OllamaNoDisponible as e:
        nota, origen_nota = reglas.nota_por_reglas(hechos), "reglas"
        avisos.append(f"Ollama no respondió ({str(e)[:80]}); la nota se generó con reglas.")

    # 3) Payload: router determinista + guardián.
    payload: PayloadNube | None = None
    try:
        payload = preparar_envio(perfil)
    except FugaDetectada as e:
        avisos.append(f"Envío a la nube bloqueado por el guardián: {e.motivos}")

    # 4) Carta: nube -> local -> plantilla.
    carta, origen_carta, envio = None, None, False
    en_linea = usar_nube and payload is not None and nube.configurado() and hay_conexion()
    if en_linea:
        try:
            carta, metricas["carta"] = nube.carta(payload)
            origen_carta, envio = "nube", True
        except NubeNoDisponible as e:
            avisos.append(f"La nube falló ({e}); se usa el modelo local.")
    elif usar_nube:
        avisos.append("Sin conexión o sin API key: la carta se genera en el dispositivo.")

    # Para la generación LOCAL se usan los mismos campos sanitizados aunque el
    # guardián haya bloqueado el envío: nunca salen del equipo.
    campos = dict(payload.campos if payload else construir_payload(perfil).campos)
    if requisitos:  # solo para generación local; no está en CAMPOS_NUBE
        campos["requisitos_detectados"] = ", ".join(requisitos)
    if carta is None:
        try:
            g = local.generar(prompt_carta(campos), SISTEMA_CARTA)
            carta, origen_carta = g.texto, "local"
            metricas["carta"] = g.metricas
        except OllamaNoDisponible:
            pass
    if carta is None:
        carta, origen_carta = carta_plantilla(campos), "plantilla"

    # 5) Rehidratación y revisión final: solo en el dispositivo.
    carta = rehidratar(carta, perfil)
    avisos.extend(reglas.problemas_en_carta(carta, perfil))

    return Resultado(carta, nota, origen_carta, origen_nota, payload, envio, requisitos, avisos,
                     metricas)
