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


import pytest

CUERPO = "Me interesa el puesto de Analista en DataCorp por mi experiencia. " * 20


@pytest.mark.parametrize("saludo,despedida,esperado", [
    ("Estimado equipo:", "Atentamente,", 1),
    ("Respetable equipo de selección:", "Un cordial saludo,", 1),   # antes daba 0 (D-23)
    ("Buenos días:", "Quedo a su disposición.", 1),
    ("", "Atentamente,", 0),            # sin saludo
    ("Estimado equipo:", "", 0),        # sin despedida
])
def test_saludo_y_despedida(saludo, despedida, esperado):
    carta = f"{saludo}\n{CUERPO}\n{despedida}\n[[NOMBRE]]"
    campos = {"puesto_objetivo": "Analista", "empresa_objetivo": "DataCorp"}
    assert rubrica.evaluar_carta(carta, campos)["saludo_y_despedida"] == esperado


def test_alerta_requisitos_sin_respaldo():
    """Caso real (c08, Gemini): la carta afirmó Salesforce e inglés fluido, que solo estaban
    en la OFERTA, no en lo que la persona dijo de sí misma."""
    campos = {"puesto_objetivo": "Key account manager", "empresa_objetivo": "SaaS Latam",
              "puesto_actual": "Ejecutivo de ventas", "logros": "Cerré contratos en 2024.",
              "resumen_experiencia": "Llevo 5 años en ventas."}
    carta = ("Estimado equipo de SaaS Latam: aplico a Key account manager. Cuento con experiencia "
             "en el uso de Salesforce y me comunico con fluidez en inglés. Un cordial saludo, [[NOMBRE]]")
    r = rubrica.evaluar_carta(carta, campos, ["crm", "salesforce", "negociación", "inglés"])
    assert r["cuales_sin_respaldo"] == "salesforce; inglés"
    # Si la persona SÍ lo dijo, no hay alerta:
    campos["resumen_experiencia"] = "Llevo 5 años en ventas usando Salesforce, en inglés."
    assert rubrica.evaluar_carta(carta, campos, ["salesforce", "inglés"])["requisitos_sin_respaldo"] == 0


# ---- D-28: casos reales de la corrida 2 -------------------------------------------------
def test_puesto_se_reconoce_aunque_cambie_la_forma():
    """Gemma escribió 'Coordinación Académica' y el puesto era 'Coordinadora académica'."""
    norm = rubrica._normalizar("un rol de Coordinación Académica en el Colegio Horizonte")
    assert rubrica.menciona("Coordinadora académica", norm)
    assert rubrica.menciona("Colegio Horizonte", norm)
    assert not rubrica.menciona("Analista GIS", norm)


def test_alerta_usa_palabras_completas_y_no_cuenta_el_titulo():
    campos = {"puesto_objetivo": "Project manager de construcción", "puesto_actual": "",
              "resumen_experiencia": "10 años supervisando obra civil.", "logros": ""}
    carta = ("Aplico a Project Manager de construcción. Aprendo rápidamente y busco la "
             "excelencia. Me interesa capacitarme en AutoCAD.")
    # 'rápidamente' no es 'api', 'excelencia' no es 'excel', y el título no es 'MS Project'
    assert rubrica.requisitos_sin_respaldo(carta, campos, ["api", "excel", "project", "autocad"]) \
        == ["autocad"]


def test_hoja_ciega_guardada_por_excel(tmp_path):
    """Excel en español guarda con punto y coma, en cp1252 y la gente escribe 'Sí'."""
    import json
    from bench.hoja import resumir_ciega
    hoja = tmp_path / "hoja.csv"
    hoja.write_bytes(("id;caso;texto;naturalidad_1a5;persuasion_1a5;lista_para_enviar_1a5;"
                      "inventa_datos_si_no;comentario\r\n"
                      "C000;c01;\"Estimado equipo; un saludo\";4;3;5;Sí;ok\r\n"
                      "C001;c01;\"Hola\";2;;3;no;\r\n"
                      "C002;c02;\"Sin calificar\";;;;;\r\n").encode("cp1252"))
    clave = tmp_path / "clave.json"
    clave.write_text(json.dumps({"C000": "gemma", "C001": "qwen", "C002": "gemini"}))
    resumen, hechas, total = resumir_ciega(
        hoja, clave, ["naturalidad_1a5", "persuasion_1a5", "lista_para_enviar_1a5"],
        "inventa_datos_si_no")
    assert (hechas, total) == (2, 3)
    por = {r["modelo"]: r for r in resumen}
    assert por["gemma"]["lista_para_enviar_1a5"] == 5 and por["gemma"]["inventa_n"] == 1
    assert por["qwen"]["persuasion_1a5"] is None and por["qwen"]["inventa_n"] == 0


# ---- D-30: reglas de la NOTA que fallaban por diseño -------------------------------------
@pytest.mark.parametrize("pct,texto,esperado", [
    (16.67, "un aumento del 16.7 % es razonable", True),    # antes exigía "17"
    (16.67, "un aumento del 17% es razonable", True),
    (77.78, "pides un 77,8 % más", True),
    (-13.3, "una reducción del 13.3 %", True),
    (0.0, "es un cambio de 0.0 %", True),
    (16.67, "un aumento del 30 % es razonable", False),     # cifra equivocada
    (16.67, "un aumento del 116.7 %", False),               # no vale como parte de otro número
])
def test_cita_el_porcentaje(pct, texto, esperado):
    assert rubrica.cita_el_porcentaje(texto, pct) is esperado


def test_iso_14001_no_es_una_cifra_inventada(perfil):
    h = reglas.analizar(perfil)
    assert rubrica.cifras_inventadas("La oferta pide ISO 14001 y 3 años de experiencia.", h) == []
    assert rubrica.cifras_inventadas("Pide Q20,000 de entrada.", h) == ["Q20,000"]
    assert rubrica.cifras_inventadas("Pasar de Q12,500 a Q16,000 es viable.", h) == []
