"""
Confere as fórmulas de core/estatistica.py contra NumPy/Pandas e contra
exemplos feitos à mão.

    python -m pytest tests -q
"""
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core import estatistica as est
from core.carregamento import para_numero

RAIZ = Path(__file__).resolve().parents[1]
TAXAS_2022 = pd.read_csv(RAIZ / "grupo_trabalho_emprego/dados/tratados/trabalho_uf.csv").query("ano == 2022")


def test_exemplo_de_aula():
    x = [2, 4, 4, 5, 7, 9, 30]  # 30 é um outlier evidente
    assert est.media(x) == pytest.approx(61 / 7)
    assert est.mediana(x) == 5
    assert est.moda(x) == [4]
    q1, q2, q3 = est.quartis(x)
    assert (q1, q2, q3) == (4, 5, 8)
    r = est.resumo(x, list("abcdefg"))
    assert r["iqr"] == 4 and r["limite_superior"] == 14
    assert [o[0] for o in r["outliers"]] == ["g"]
    imp = est.impacto_outliers(x, list("abcdefg"))
    assert imp["media_com"] > imp["media_sem"]           # outlier puxa a média
    assert abs(imp["variacao_mediana"]) < abs(imp["variacao_media"])  # mediana é robusta


def test_contra_numpy_pandas():
    x = TAXAS_2022["taxa_desocupacao"].to_numpy()
    s = pd.Series(x)
    assert est.media(x) == pytest.approx(np.mean(x))
    assert est.mediana(x) == pytest.approx(np.median(x))
    for p in (0.25, 0.5, 0.75):
        assert est.percentil(x, p) == pytest.approx(s.quantile(p))
    assert est.variancia(x) == pytest.approx(np.var(x))
    assert est.variancia(x, amostral=True) == pytest.approx(np.var(x, ddof=1))
    assert est.desvio_padrao(x) == pytest.approx(np.std(x))
    assert est.desvio_padrao(x, amostral=True) == pytest.approx(s.std())
    assert est.amplitude(x) == pytest.approx(np.ptp(x))


def test_correlacao():
    d = TAXAS_2022.dropna()
    assert est.correlacao_pearson(d["taxa_informalidade"], d["taxa_desocupacao"]) == pytest.approx(
        np.corrcoef(d["taxa_informalidade"], d["taxa_desocupacao"])[0, 1])


def test_dados_agrupados():
    # classes 0-10, 10-20, 20-30 com frequências 10, 20, 10 -> mediana 15, média 15
    L, h, f = [0, 10, 20], [10, 10, 10], [10, 20, 10]
    assert est.mediana_agrupada(L, h, f) == 15
    assert est.media_agrupada([5, 15, 25], f) == 15
    assert est.desvio_padrao_agrupado([5, 15, 25], f) == pytest.approx(math.sqrt(50))


def test_mediana_de_idade_bate_com_ibge():
    d = pd.read_csv(RAIZ / "individuais/arthur_souza_populacao/dados/tratados/pop_idade_sexo.csv")
    g = d.groupby(["idade_inicio", "amplitude_classe"], as_index=False)["populacao"].sum().sort_values("idade_inicio")
    md = est.mediana_agrupada(g["idade_inicio"], g["amplitude_classe"], g["populacao"])
    assert round(md) == 35  # idade mediana oficial do Brasil (Censo 2022)


def test_conversao_numeros_ibge():
    assert para_numero("9,6") == 9.6
    assert para_numero("35 128") == 35128
    assert para_numero("89.695") == 89695
    assert para_numero("1.234,5") == 1234.5
    assert para_numero("-") == 0  # convenção IBGE: zero absoluto
    assert math.isnan(para_numero("...")) and math.isnan(para_numero("..")) and math.isnan(para_numero("X"))
