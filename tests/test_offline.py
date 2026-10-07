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


def test_si_la_nube_falla_se_dice_que_los_datos_si_salieron(perfil, en_linea):
    """Caso real (D-33): Gemini respondió 504 y el panel decía 'No se envió'.

    La petición ya había salido: la app debe distinguir 'no se envió' de
    'se envió, pero la nube no devolvió la carta'.
    """
    r = generar(perfil, local=LocalFalso(), nube=NubeFalsa(falla=True))
    assert r.origen_carta == "local" and not r.envio_nube
    assert r.envio_intentado


def test_en_modo_local_no_se_intenta_ningun_envio(perfil, sin_conexion):
    r = generar(perfil, local=LocalFalso(), nube=NubeFalsa())
    assert not r.envio_intentado and not r.envio_nube


def test_los_espacios_sobrantes_no_llegan_a_la_carta(en_linea):
    """Caso real (D-33): 'Universidad Galileo ' con un espacio al final quedaba como
    'Universidad Galileo , he desarrollado…' al volver a poner el nombre del empleador."""
    from splitbrain.perfil import Perfil
    p = Perfil(nombre=" María Ficticia ", empleador_actual="Colegio Ficticio ",
               salario_actual=5000, salario_deseado=5500, puesto_objetivo="Coordinadora ")
    assert (p.nombre, p.empleador_actual, p.puesto_objetivo) == (
        "María Ficticia", "Colegio Ficticio", "Coordinadora")
