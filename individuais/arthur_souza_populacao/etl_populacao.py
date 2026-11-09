"""
ETL — Indicador 1: População por Grupo de Idade, Sexo e Raça (Arthur de Souza).

Bases brutas (dados/brutos) -> bases tratadas (dados/tratados):
  * pop_idade_sexo.csv   : região x grupo de idade x sexo x situação (Censo 2022)
  * pop_cor_raca.csv     : região x cor ou raça x sexo x situação (Censo 2022)
  * pop_uf.csv           : população e densidade por UF (Censos 2010 e 2022)
  * indicadores_cor.csv  : razão de sexo, idade mediana e envelhecimento por cor ou raça

Execute a partir da raiz do repositório:
    python -m individuais.arthur_souza_populacao.etl_populacao
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from core.carregamento import REGIOES, anexar_uf, ler_ibge, nome_coluna, para_numero

PASTA = Path(__file__).resolve().parent
BRUTOS = PASTA / "dados" / "brutos"
TRATADOS = PASTA / "dados" / "tratados"

SUBGRUPOS = {"15 a 17 anos", "18 e 19 anos"}  # já contidos em "15 a 19 anos" -> evitar contagem dupla
LIMITE_CLASSE_ABERTA = 90  # hipótese para a classe "70 anos ou mais" (usada só na média agrupada)


def limites_idade(grupo: str) -> tuple[int, int]:
    """'20 a 24 anos' -> (20, 5); '70 anos ou mais' -> (70, 20)."""
    nums = [int(n) for n in re.findall(r"\d+", grupo)]
    if "mais" in grupo:
        return nums[0], LIMITE_CLASSE_ABERTA - nums[0]
    return nums[0], nums[1] - nums[0] + 1


def tratar_idade_sexo() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "censo2022_pop_regiao_idade_sexo_situacao.csv",
                  ["Grandes Regiões e grupos de idade", "Homens", "Mulheres"])
    df = df.rename(columns={df.columns[0]: "rotulo"})
    df["rotulo"] = df["rotulo"].str.strip()

    # As linhas de região funcionam como "títulos de bloco": propagamos para as faixas abaixo
    df["regiao"] = df["rotulo"].where(df["rotulo"].isin(["Brasil"] + REGIOES)).ffill()
    faixas = df[~df["rotulo"].isin(["Brasil"] + REGIOES) & ~df["rotulo"].isin(SUBGRUPOS)].copy()

    colunas = {"Urbana Homens": ("Urbana", "Homens"), "Urbana Mulheres": ("Urbana", "Mulheres"),
               "Rural Homens": ("Rural", "Homens"), "Rural Mulheres": ("Rural", "Mulheres")}
    partes = []
    for col, (situacao, sexo) in colunas.items():
        p = faixas[["regiao", "rotulo", col]].rename(columns={"rotulo": "grupo_idade", col: "populacao"})
        p["situacao"], p["sexo"] = situacao, sexo
        p["populacao"] = p["populacao"].map(para_numero)
        partes.append(p)
    longo = pd.concat(partes, ignore_index=True)

    # Conferência: soma das 5 regiões deve bater com o total Brasil
    brasil = longo[longo["regiao"] == "Brasil"]["populacao"].sum()
    regioes = longo[longo["regiao"] != "Brasil"]
    assert abs(regioes["populacao"].sum() - brasil) < 1, "Soma das regiões difere do Brasil"
    assert int(brasil) == 203_080_756, "Total Brasil diferente do Censo 2022"

    regioes = regioes.copy()
    lim = regioes["grupo_idade"].map(limites_idade)
    regioes["idade_inicio"] = lim.map(lambda t: t[0])
    regioes["amplitude_classe"] = lim.map(lambda t: t[1])
    regioes["populacao"] = regioes["populacao"].astype("int64")
    ordem = ["regiao", "grupo_idade", "idade_inicio", "amplitude_classe", "sexo", "situacao", "populacao"]
    return regioes[ordem].sort_values(["regiao", "idade_inicio", "sexo", "situacao"]).reset_index(drop=True)


def tratar_cor_raca() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "censo2022_pop_regiao_cor_raca_sexo_situacao.csv",
                  ["Grandes Regiões", "Situação do domicílio", "Sexo", "Branca"])
    df.columns = [nome_coluna(c) for c in df.columns]
    cores = ["branca", "preta", "amarela", "parda", "indigena", "sem_declaracao"]
    longo = df.melt(id_vars=["grandes_regioes", "situacao_do_domicilio", "sexo"], value_vars=cores,
                    var_name="cor_raca", value_name="populacao")
    longo["populacao"] = longo["populacao"].map(para_numero)
    longo = longo.rename(columns={"grandes_regioes": "regiao", "situacao_do_domicilio": "situacao"})
    nomes = {"branca": "Branca", "preta": "Preta", "amarela": "Amarela", "parda": "Parda",
             "indigena": "Indígena", "sem_declaracao": "Sem declaração"}
    longo["cor_raca"] = longo["cor_raca"].map(nomes)

    elementares = longo[(longo["regiao"] != "Brasil") & (longo["situacao"] != "Total") & (longo["sexo"] != "Total")]
    total_br = longo[(longo["regiao"] == "Brasil") & (longo["situacao"] == "Total") & (longo["sexo"] == "Total")]
    assert abs(elementares["populacao"].sum() - total_br["populacao"].sum()) < 1, "Conferência de cor/raça falhou"
    elementares = elementares.copy()
    elementares["populacao"] = elementares["populacao"].astype("int64")
    return elementares[["regiao", "situacao", "sexo", "cor_raca", "populacao"]].reset_index(drop=True)


def tratar_uf() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "censo_populacao_uf_2010_2022.csv", ["Unidade da Federação", "População 2010"])
    df = df.rename(columns={df.columns[0]: "uf"})
    linhas = []
    for ano in (2010, 2022):
        p = df[["uf", f"População {ano}", f"Densidade {ano} (hab/km2)"]].copy()
        p.columns = ["uf", "populacao", "densidade"]
        p["ano"] = ano
        linhas.append(p)
    longo = pd.concat(linhas, ignore_index=True)
    longo["populacao"] = longo["populacao"].map(para_numero).astype("int64")
    longo["densidade"] = longo["densidade"].map(para_numero)
    longo = anexar_uf(longo, "uf")
    largura = longo.pivot(index="uf", columns="ano", values="populacao")
    cresc = ((largura[2022] / largura[2010] - 1) * 100).rename("crescimento_2010_2022_pct")
    longo = longo.merge(cresc, left_on="uf", right_index=True)
    longo["participacao_brasil_pct"] = longo["populacao"] / longo.groupby("ano")["populacao"].transform("sum") * 100
    assert longo[longo["ano"] == 2022]["populacao"].sum() == 203_080_756
    return longo[["uf", "sigla", "regiao", "ano", "populacao", "densidade", "crescimento_2010_2022_pct",
                  "participacao_brasil_pct"]].sort_values(["ano", "sigla"]).reset_index(drop=True)


def tratar_indicadores_cor() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "censo2022_indicadores_cor_raca_brasil.csv", ["Cor ou raça", "Razão de sexo"])
    df.columns = ["cor_raca", "razao_sexo", "idade_mediana", "indice_envelhecimento", "part_2010_pct", "part_2022_pct"]
    for c in df.columns[1:]:
        df[c] = df[c].map(para_numero)
    return df


def executar() -> dict[str, pd.DataFrame]:
    tabelas = {
        "pop_idade_sexo": tratar_idade_sexo(),
        "pop_cor_raca": tratar_cor_raca(),
        "pop_uf": tratar_uf(),
        "indicadores_cor": tratar_indicadores_cor(),
    }
    TRATADOS.mkdir(parents=True, exist_ok=True)
    for nome, df in tabelas.items():
        df.to_csv(TRATADOS / f"{nome}.csv", index=False, encoding="utf-8")
    with pd.ExcelWriter(TRATADOS / "base_populacao_tratada.xlsx") as w:
        for nome, df in tabelas.items():
            df.to_excel(w, sheet_name=nome, index=False)
    return tabelas


def carregar() -> dict[str, pd.DataFrame]:
    nomes = ["pop_idade_sexo", "pop_cor_raca", "pop_uf", "indicadores_cor"]
    if not all((TRATADOS / f"{n}.csv").exists() for n in nomes):
        return executar()
    return {n: pd.read_csv(TRATADOS / f"{n}.csv") for n in nomes}


if __name__ == "__main__":
    for nome, df in executar().items():
        print(f"{nome}: {df.shape[0]} linhas x {df.shape[1]} colunas")
