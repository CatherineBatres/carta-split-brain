"""La rúbrica también se prueba: si mide mal, el benchmark concluye mal."""
from bench import rubrica
from splitbrain import reglas


def test_nota_buena_vs_nota_que_inventa(perfil):
    h = reglas.analizar(perfil)
    buena = ("Pasar de Q12,500 a Q16,000 es un aumento de 28 % y está dentro del rango. "
             "Menciónala cuando RR. HH. te la pida en la primera llamada y apóyate en tus "
             "logros, como la automatización de reportes. " * 3)
    mala = buena.replace("28 %", "35 %").replace("Q16,000", "Q20,000")
    assert rubrica.evaluar_nota(buena, h)["sin_cifras_inventadas"] == 1
    r = rubrica.evaluar_nota(mala, h)
    assert r["sin_cifras_inventadas"] == 0 and r["calidad"] < rubrica.evaluar_nota(buena, h)["calidad"]


def test_extraccion_json_invalido_da_cero():
    assert rubrica.evaluar_extraccion("no es json", {"requisitos": ["sql"], "modalidad": "remoto"})["calidad"] == 0


def test_extraccion_recall():
    r = rubrica.evaluar_extraccion('{"puesto":"x","requisitos":["Python avanzado","SQL"],"modalidad":"Remoto"}',
                                   {"requisitos": ["python", "sql", "git"], "modalidad": "remoto"})
    assert r["recall_requisitos"] == round(2 / 3, 3) and r["modalidad_ok"] == 1
