"""Condición 2: el salario actual nunca sale del dispositivo (y otros datos sensibles)."""
import pytest

from splitbrain.orquestador import generar
from splitbrain.router import FugaDetectada, PayloadNube, preparar_envio, verificar_payload

from .conftest import LocalFalso, NubeFalsa

FORMAS_DEL_SALARIO = ["12500", "12,500", "12.500", "12 500", "Q12,500.00", "12.5k", "12.5 mil",
                      "150000", "150,000", "175,000"]  # x12 y x14 incluidos


def test_payload_no_contiene_salario_ni_identidad(perfil):
    texto = preparar_envio(perfil).como_texto()
    for prohibido in ["12,500", "12500", "María", "López", "Banco Ficticio", "@", "5555-1234"]:
        assert prohibido not in texto, prohibido


def test_lo_que_recibe_la_nube_no_tiene_salario(perfil, en_linea):
    """Prueba de extremo a extremo: auditamos lo que llega al cliente de la nube."""
    nube = NubeFalsa()
    r = generar(perfil, local=LocalFalso(), nube=nube)
    assert r.envio_nube and len(nube.recibido) == 1
    enviado = nube.recibido[0]
    assert "12,500" not in enviado and "12500" not in enviado
    assert "16,000" not in enviado and "16000" not in enviado


def test_la_nota_si_usa_el_salario_pero_solo_en_local(perfil, en_linea):
    local, nube = LocalFalso(), NubeFalsa()
    generar(perfil, local=local, nube=nube)
    assert any("Q12,500" in p for p in local.prompts)      # el modelo local sí lo ve
    assert not any("Q12,500" in p for p in nube.recibido)  # la nube no


@pytest.mark.parametrize("forma", FORMAS_DEL_SALARIO)
def test_guardian_atrapa_el_salario_en_cualquier_formato(perfil, forma):
    payload = PayloadNube(campos={"logros": f"Actualmente cobro {forma} mensuales"})
    with pytest.raises(FugaDetectada):
        verificar_payload(payload, perfil)


def test_guardian_atrapa_nombre_sin_tildes(perfil):
    payload = PayloadNube(campos={"logros": "Firmado: maria jose lopez"})
    with pytest.raises(FugaDetectada):
        verificar_payload(payload, perfil)


def test_guardian_rechaza_campos_no_permitidos(perfil):
    payload = PayloadNube(campos={"salario_actual": "algo"})
    with pytest.raises(FugaDetectada):
        verificar_payload(payload, perfil)


def test_si_el_guardian_bloquea_no_se_llama_a_la_nube(perfil, en_linea, monkeypatch):
    def fuga(_):
        raise FugaDetectada(["simulada"])

    monkeypatch.setattr("splitbrain.orquestador.preparar_envio", fuga)
    nube = NubeFalsa()
    r = generar(perfil, local=LocalFalso(), nube=nube)
    assert nube.recibido == [] and not r.envio_nube
    assert r.carta  # aun así hay carta (local)
