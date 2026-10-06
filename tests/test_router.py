"""Condición 3: la decisión de qué va a la nube es explícita y probable."""
from splitbrain.perfil import Perfil
from splitbrain.router import CAMPOS_NUBE, CAMPOS_SOLO_LOCAL, construir_payload


def test_todo_campo_esta_clasificado_una_sola_vez():
    todos = Perfil.nombres_de_campos()
    assert CAMPOS_NUBE | CAMPOS_SOLO_LOCAL == todos, "Hay un campo sin clasificar"
    assert not (CAMPOS_NUBE & CAMPOS_SOLO_LOCAL), "Un campo no puede estar en ambos lados"


def test_campos_solo_locales_nunca_aparecen_en_payload(perfil):
    payload = construir_payload(perfil)
    assert not (set(payload.campos) & CAMPOS_SOLO_LOCAL)


def test_router_es_determinista(perfil):
    a = construir_payload(perfil).como_texto()
    b = construir_payload(perfil).como_texto()
    assert a == b


def test_sanitizador_conserva_lo_util(perfil):
    t = construir_payload(perfil).campos["resumen_experiencia"]
    assert "2019-2023" in t          # rango de años NO es teléfono
    assert "[[NOMBRE]]" in t and "[[EMPLEADOR_ACTUAL]]" in t
    assert "[CORREO]" in t and "[TELÉFONO]" in t and "[MONTO]" in t
    assert "20 horas" in construir_payload(perfil).campos["logros"]  # números chicos se quedan
