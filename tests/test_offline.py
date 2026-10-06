"""Condición 4: sin conexión la app sigue entregando algo útil."""
from splitbrain.orquestador import generar

from .conftest import LocalFalso, NubeFalsa


def test_sin_internet_carta_local(perfil, sin_conexion):
    nube = NubeFalsa()
    r = generar(perfil, local=LocalFalso(), nube=nube)
    assert r.origen_carta == "local" and nube.recibido == []
    assert "María José López" in r.carta  # rehidratado en el dispositivo


def test_sin_internet_ni_ollama_hay_plantilla_y_nota_por_reglas(perfil, sin_conexion):
    r = generar(perfil, local=LocalFalso(falla=True), nube=NubeFalsa())
    assert r.origen_carta == "plantilla" and r.origen_nota == "reglas"
    assert "+28.0 %" in r.nota
    assert "DataCorp" in r.carta


def test_si_la_nube_falla_cae_a_local(perfil, en_linea):
    r = generar(perfil, local=LocalFalso(), nube=NubeFalsa(falla=True))
    assert r.origen_carta == "local"
    assert any("nube falló" in a for a in r.avisos)


def test_con_internet_usa_la_nube(perfil, en_linea):
    r = generar(perfil, local=LocalFalso(), nube=NubeFalsa())
    assert r.origen_carta == "nube" and "María José López" in r.carta


def test_la_plantilla_no_deja_marcadores_censurados(perfil, sin_conexion):
    """Error real: la plantilla pegaba 'gano [MONTO]... [TELÉFONO]' dentro de la carta."""
    r = generar(perfil, local=LocalFalso(falla=True), nube=NubeFalsa())
    for marca in ("[MONTO]", "[TELÉFONO]", "[CORREO]"):
        assert marca not in r.carta
    assert "Automaticé reportes" in r.carta  # lo útil se conserva
