import pytest

from splitbrain import reglas
from splitbrain.perfil import Perfil


@pytest.mark.parametrize("texto,valor", [
    ("Q12,500", 12500), ("12.500", 12500), ("12 500", 12500), ("12,500.50", 12500.5),
    ("12.500,50", 12500.5), ("15k", 15000), ("12.5 mil", 12500), ("US$1,800", 1800),
])
def test_lectura_de_montos(texto, valor):
    assert reglas.extraer_montos(texto)[0].valor == pytest.approx(valor)


@pytest.mark.parametrize("pct,etiqueta", [
    (-5, "por debajo de lo que ganas hoy"), (0, "conservadora"), (10, "conservadora"),
    (20, "razonable"), (35, "ambiciosa"), (80, "muy ambiciosa"),
])
def test_clasificacion(pct, etiqueta):
    assert reglas.clasificar_incremento(pct) == etiqueta


def test_calculo_exacto_y_rango(perfil):
    h = reglas.analizar(perfil)
    assert h.incremento_pct == pytest.approx(28.0)
    assert h.rango_oferta == (14000, 18000)
    assert h.posicion_vs_rango == "dentro del rango publicado"


def test_sin_rango_y_muy_ambiciosa():
    h = reglas.analizar(Perfil(salario_actual=10000, salario_deseado=20000))
    assert h.clasificacion == "muy ambiciosa" and h.rango_oferta is None
    assert "primer número" in h.momento


def test_carta_con_salario_se_marca(perfil):
    assert reglas.problemas_en_carta("Mi pretensión salarial es Q16,000", perfil)
    assert reglas.problemas_en_carta("Estimados, ... Atentamente, María", perfil) == []
