"""D-32: los formularios de demostración son ficticios, completos y no filtran nada."""
import json
from dataclasses import fields
from pathlib import Path

from splitbrain import reglas
from splitbrain.perfil import Perfil
from splitbrain.router import CAMPOS_SOLO_LOCAL, preparar_envio

RAIZ = Path(__file__).resolve().parent.parent
FORMULARIOS = json.loads((RAIZ / "demo" / "formularios.json").read_text(encoding="utf-8"))
CAMPOS_FORM = {"nombre", "empleador_actual", "moneda", "salario_actual", "salario_deseado",
               "puesto_actual", "puesto_objetivo", "empresa_objetivo", "resumen_experiencia",
               "logros", "oferta_texto"}


def test_cada_formulario_llena_todos_los_campos_de_la_app():
    assert len(FORMULARIOS) >= 3
    for f in FORMULARIOS:
        assert set(f["perfil"]) == CAMPOS_FORM, f["id"]
        assert f["titulo"] and f["que_muestra"]
        assert f["perfil"]["moneda"] in ("Q", "US$", "€", "MXN$")
        Perfil(**f["perfil"])  # no debe faltar ni sobrar nada
    assert CAMPOS_FORM <= {c.name for c in fields(Perfil)}


def test_ningun_formulario_deja_salir_lo_privado():
    """Lo que saldría a la nube con cada ejemplo no trae nombre, empleador ni salarios."""
    for f in FORMULARIOS:
        p = Perfil(**f["perfil"])
        envio = preparar_envio(p)            # el guardián lanzaría FugaDetectada si algo pasa
        texto = envio.como_texto()
        assert p.nombre not in texto and p.empleador_actual not in texto, f["id"]
        for campo in CAMPOS_SOLO_LOCAL:
            assert campo not in envio.campos, f["id"]
        for salario in (p.salario_actual, p.salario_deseado):
            assert f"{salario:,.0f}" not in texto and f"{salario:.0f}" not in texto, f["id"]


def test_el_caso_base_esconde_cinco_tipos_de_dato_sensible():
    """El primer formulario existe para mostrar el sanitizador: debe disparar los cinco."""
    envio = preparar_envio(Perfil(**FORMULARIOS[0]["perfil"]))
    assert {"nombre", "empleador", "monto", "correo", "telefono"} <= set(envio.reemplazos)


def test_los_formularios_cubren_los_casos_que_promete_el_guion():
    clases = {reglas.analizar(Perfil(**f["perfil"])).clasificacion for f in FORMULARIOS}
    assert "razonable" in clases and "muy ambiciosa" in clases
    assert any(Perfil(**f["perfil"]).salario_deseado < Perfil(**f["perfil"]).salario_actual
               for f in FORMULARIOS)
    assert any(not reglas.analizar(Perfil(**f["perfil"])).rango_oferta for f in FORMULARIOS)
