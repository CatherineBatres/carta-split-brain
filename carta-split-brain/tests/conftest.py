import pytest

from splitbrain.local_llm import Generacion, OllamaNoDisponible
from splitbrain.nube import NubeNoDisponible
from splitbrain.perfil import Perfil


@pytest.fixture
def perfil():
    return Perfil(
        nombre="María José López",
        empleador_actual="Banco Ficticio de Guatemala",
        salario_actual=12500,
        salario_deseado=16000,
        moneda="Q",
        puesto_actual="Analista de datos",
        puesto_objetivo="Científica de datos",
        empresa_objetivo="DataCorp",
        resumen_experiencia=(
            "Soy María José López, analista en Banco Ficticio de Guatemala desde 2019-2023, "
            "hoy gano Q12,500 al mes. Escríbeme a maria.lopez@correo.com o al 5555-1234."
        ),
        logros="Automaticé reportes y ahorré 20 horas al mes; ahorré Q150,000 al año.",
        oferta_texto="Buscamos Científica de datos con Python y SQL. Salario Q14,000 - Q18,000.",
    )


class LocalFalso:
    """Simula Ollama y registra cada prompt que recibe."""

    def __init__(self, falla=False):
        self.falla = falla
        self.prompts = []
        self.modelo = "falso:1b"

    def generar(self, prompt, sistema="", formato_json=False):
        self.prompts.append(prompt)
        if self.falla:
            raise OllamaNoDisponible("apagado")
        return Generacion(texto="Estimado equipo...\n[[NOMBRE]]", modelo=self.modelo)

    def disponible(self):
        return not self.falla


class NubeFalsa:
    """Simula Gemini y guarda TODO lo que se le envía, para auditarlo."""

    def __init__(self, falla=False):
        self.falla = falla
        self.recibido = []

    def configurado(self):
        return True

    def carta(self, payload):
        self.recibido.append(payload.como_texto())
        if self.falla:
            raise NubeNoDisponible("timeout")
        return "Carta desde la nube. Atentamente, [[NOMBRE]]", {}


@pytest.fixture
def en_linea(monkeypatch):
    monkeypatch.setattr("splitbrain.orquestador.hay_conexion", lambda: True)


@pytest.fixture
def sin_conexion(monkeypatch):
    monkeypatch.setattr("splitbrain.orquestador.hay_conexion", lambda: False)
