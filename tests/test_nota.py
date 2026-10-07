"""D-31: el modelo redacta la nota; las reglas ponen las cifras y revisan lo que escribió.

Las frases de estas pruebas salen de respuestas reales de la evaluación B
(resultados/crudo/progreso.jsonl), con perfiles ficticios.
"""
from bench import rubrica
from splitbrain import reglas
from splitbrain.local_llm import Generacion
from splitbrain.orquestador import generar
from splitbrain.perfil import Perfil

from .conftest import LocalFalso, NubeFalsa

# Perfil c08 del benchmark: Q11,000 -> Q13,000 (+18.2 %), oferta sin rango.
C08 = Perfil(nombre="José Ángel Barrios", empleador_actual="Distribuidora Ficticia",
             salario_actual=11000, salario_deseado=13000, moneda="Q",
             puesto_actual="Ejecutivo de ventas", puesto_objetivo="KAM B2B",
             empresa_objetivo="SaaS Latam", resumen_experiencia="5 años en ventas.",
             logros="Cerré contratos en 2024.", oferta_texto="")


class LocalQueEscribe(LocalFalso):
    """Modelo falso que devuelve la nota que se le indique."""

    def __init__(self, nota):
        super().__init__()
        self.nota = nota

    def generar(self, prompt, sistema="", formato_json=False):
        if "nota privada" in prompt:
            return Generacion(texto=self.nota, modelo=self.modelo)
        return super().generar(prompt, sistema, formato_json)


def test_detecta_el_salario_mal_copiado():
    """Error real: el modelo escribió Q1,100 donde el salario era Q11,000."""
    h = reglas.analizar(C08)
    nota = "Mi salario actual es de Q1,100 mensuales y busco una actualización al 18.2%."
    problemas = reglas.problemas_en_nota(nota, h)
    assert any("Q1,100" in p for p in problemas)


def test_detecta_un_monto_sugerido_que_nadie_dio():
    """Error real: 'anclaré en Q14,000' con un rango de Q12,000 a Q15,000."""
    p = Perfil(nombre="Ana", empleador_actual="X", salario_actual=10000, salario_deseado=13500,
               moneda="Q", puesto_actual="Diseñadora", puesto_objetivo="UX", empresa_objetivo="Y",
               oferta_texto="Diseñadora UX. Salario Q12,000 - Q15,000.")
    h = reglas.analizar(p)
    assert reglas.cifras_ajenas("Ancla en Q14,000, dentro del rango Q12,000–Q15,000.", h) == ["Q14,000"]


def test_avisa_si_la_nota_esta_escrita_para_la_empresa():
    h = reglas.analizar(C08)
    para_la_empresa = "Estimado equipo de RR.HH.: mi salario actual es de Q11,000 y busco Q13,000."
    assert any("mensaje para la empresa" in p for p in reglas.problemas_en_nota(para_la_empresa, h))


def test_una_nota_correcta_no_dispara_avisos():
    h = reglas.analizar(C08)
    buena = ("Tu expectativa de Q13,000 (+18.2 %) es razonable. Menciónala cuando RR. HH. te la "
             "pida en la primera conversación y defiéndela con los contratos que cerraste.")
    assert reglas.problemas_en_nota(buena, h) == []


def test_la_app_siempre_tiene_las_cifras_exactas_aunque_el_modelo_las_omita(sin_conexion):
    """Hallazgo real: 19 de 20 notas de un modelo no citaban ninguna cifra."""
    sin_cifras = "Tu expectativa es razonable. Espera a que RR. HH. pregunte y habla de tu valor."
    r = generar(C08, local=LocalQueEscribe(sin_cifras), nube=NubeFalsa())
    assert r.origen_nota == "local" and "18.2" not in r.nota
    assert "+18.2 %" in r.datos_exactos and "Q11,000" in r.datos_exactos
    assert not r.datos_exactos.startswith("Nota privada")  # sin el título de la nota por reglas


def test_la_app_avisa_cuando_el_modelo_cambia_una_cifra(sin_conexion):
    mala = "Tu salario actual es de Q1,100 y pides Q13,000: es razonable."
    r = generar(C08, local=LocalQueEscribe(mala), nube=NubeFalsa())
    assert r.nota == mala  # no se oculta lo que escribió el modelo: se avisa
    assert any("Q1,100" in a for a in r.avisos)


def test_las_alertas_no_cambian_la_nota_de_calidad():
    """Las dos columnas nuevas son informativas: la calidad se calcula igual que antes."""
    h = reglas.analizar(C08)
    r = rubrica.evaluar_nota("Mi salario actual es de Q11,000 y mi expectativa sube un 18.2%. "
                             "Lo diré cuando RR. HH. pregunte en la primera llamada. " * 4, h)
    assert r["primera_persona"] == 1 and r["cita_alguna_cifra"] == 1
    assert r["calidad"] == 1.0
    assert rubrica.evaluar_nota("Tu expectativa es razonable. " * 20, h)["cita_alguna_cifra"] == 0


def test_la_alerta_de_primera_persona_no_marca_un_consejo_en_segunda_persona():
    assert not reglas.habla_en_primera_persona("Tu expectativa es ambiciosa; tu salario actual no se menciona.")
    assert reglas.habla_en_primera_persona("Considero que mi expectativa es realista.")


def test_el_analisis_avisa_si_una_columna_de_la_hoja_ciega_no_distingue_nada():
    """Caso real: 'inventa' quedó en 'Sí' en las 20 notas y 'claridad' quedó vacía."""
    from bench.analizar import avisos_hoja
    filas = [{"claridad_1a5": "", "utilidad_1a5": str(n), "inventa_datos_si_no": "Sí"}
             for n in (1, 3, 5, 5)]
    avisos = avisos_hoja(filas)
    assert len(avisos) == 2
    assert any("claridad_1a5" in a and "vacía" in a for a in avisos)
    assert any("inventa_datos_si_no" in a and "mismo valor" in a for a in avisos)
    assert not any("utilidad_1a5" in a for a in avisos)
