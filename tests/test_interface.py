"""
Testes da interface (Streamlit AppTest): cada app roda sem erro com os filtros
padrão e com combinações extremas de filtros.

    python -m pytest tests -q
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]


def _rodar(caminho, acoes=()):
    at = AppTest.from_file(str(RAIZ / caminho), default_timeout=180)
    at.run()
    for acao in acoes:
        acao(at)
        at.run()
    assert not at.exception, [e.message for e in at.exception]
    return at


def _widget(at, tipo, rotulo):
    return next(w for w in getattr(at, tipo) if w.label == rotulo)


@pytest.mark.parametrize("acoes", [
    (),
    (lambda at: _widget(at, "radio", "Indicador").set_value("taxa_informalidade"),),
    (lambda at: _widget(at, "multiselect", "Regiões").set_value(["Nordeste"]),),
    (lambda at: _widget(at, "select_slider", "Comparar os anos").set_value((2016, 2020)),),
    (lambda at: _widget(at, "multiselect", "Regiões").set_value([]),),
])
def test_grupo(acoes):
    _rodar("tests/app_grupo_teste.py", acoes)


@pytest.mark.parametrize("acoes", [
    (),
    (lambda at: _widget(at, "multiselect", "Regiões").set_value(["Norte"]),
     lambda at: _widget(at, "multiselect", "Sexo").set_value(["Mulheres"])),
    (lambda at: _widget(at, "multiselect", "Situação do domicílio").set_value(["Rural"]),
     lambda at: _widget(at, "select_slider", "Faixa etária (início do grupo)").set_value((15, 60))),
    (lambda at: _widget(at, "radio", "Ano (análise por UF)").set_value(2010),),
    (lambda at: _widget(at, "multiselect", "Cor ou raça").set_value([]),),
    (lambda at: _widget(at, "multiselect", "Sexo").set_value([]),),
])
def test_arthur(acoes):
    _rodar("individuais/arthur_souza_populacao/app.py", acoes)


@pytest.mark.parametrize("acoes", [
    (),
    (lambda at: _widget(at, "radio", "Medida").set_value("Taxa de alfabetização"),),
    (lambda at: _widget(at, "radio", "População (análise por UF)").set_value("Pessoas quilombolas"),),
    (lambda at: _widget(at, "multiselect", "Regiões").set_value(["Sul"]),),
    (lambda at: _widget(at, "multiselect", "Cor ou raça").set_value(["Indígena"]),
     lambda at: _widget(at, "multiselect", "Faixas etárias").set_value(["65 anos ou mais"])),
    (lambda at: _widget(at, "select_slider", "Ano (recortes por cor e região)").set_value(2010),),
])
def test_clara(acoes):
    _rodar("individuais/clara_lima_alfabetizacao/app.py", acoes)


@pytest.mark.parametrize("acoes", [
    (),
    (lambda at: _widget(at, "multiselect", "Regiões").set_value(["Sudeste"]),),
    (lambda at: _widget(at, "multiselect", "Situação do domicílio").set_value(["Rural"]),
     lambda at: _widget(at, "select_slider", "Faixa etária (início do grupo)").set_value((60, 70))),
    (lambda at: _widget(at, "select_slider", "Ano (projeção populacional)").set_value(2010),),
    (lambda at: _widget(at, "multiselect", "Dimensões dos indicadores sociais").set_value(["Educação"]),),
    (lambda at: _widget(at, "multiselect", "Cor ou raça").set_value([]),),
])
def test_gustavo(acoes):
    _rodar("individuais/gustavo_henrique_mulheres/app.py", acoes)
