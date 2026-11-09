"""
ETL — Tema 6: Trabalho e Emprego (parte do GRUPO).

Transforma as tabelas brutas da PNAD Contínua (dados/brutos) em bases tratadas
no formato "tidy" (uma linha por observação), salvas em dados/tratados.

Execute a partir da raiz do repositório:
    python -m grupo_trabalho_emprego.etl_trabalho
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.carregamento import anexar_uf, ler_ibge, nome_coluna, para_numero, wide_para_long

PASTA = Path(__file__).resolve().parent
BRUTOS = PASTA / "dados" / "brutos"
TRATADOS = PASTA / "dados" / "tratados"


def tratar_taxa_uf(arquivo: str, nome_valor: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabela larga (UF x anos) -> longa. Retorna (UFs, Brasil)."""
    df = ler_ibge(BRUTOS / arquivo, ["Unidade da Federação", "2016", "2022"])
    df = df.rename(columns={df.columns[0]: "uf"})
    longo = wide_para_long(df, ["uf"], "ano", nome_valor)
    longo["ano"] = longo["ano"].astype(int)
    brasil = longo[longo["uf"] == "Brasil"].drop(columns="uf").reset_index(drop=True)
    ufs = anexar_uf(longo[longo["uf"] != "Brasil"], "uf")
    assert ufs["sigla"].notna().all(), "Alguma UF não foi reconhecida"
    assert ufs["uf"].nunique() == 27, "Era esperado 27 UFs"
    return ufs[["uf", "sigla", "regiao", "ano", nome_valor]], brasil


def tratar_indicadores_brasil() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "pnadc_indicadores_brasil_2012_2024.csv", ["Indicador", "Unidade", "2012"])
    df.columns = [nome_coluna(c) if not c.isdigit() else c for c in df.columns]
    longo = wide_para_long(df, ["indicador", "unidade"], "ano", "valor")
    longo["ano"] = longo["ano"].astype(int)
    return longo  # valores '-' e '...' viram NaN (sem dado)


def tratar_atividade_posicao() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "pnadc_ocupados_atividade_posicao_2012_2022.csv", ["Tipo", "Categoria", "2012"])
    df.columns = [nome_coluna(c) if not c.isdigit() else c for c in df.columns]
    longo = wide_para_long(df, ["tipo", "categoria"], "ano", "mil_pessoas")
    longo["ano"] = longo["ano"].astype(int)
    return longo


def tratar_genero() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "genero_raca_trabalho_2022.csv", ["Indicador", "Grupo", "Valor"])
    df.columns = [nome_coluna(c) for c in df.columns]
    df["valor"] = df["valor"].map(para_numero)
    df["ano"] = df["ano"].astype(int)
    return df


def executar() -> dict[str, pd.DataFrame]:
    deso_uf, deso_br = tratar_taxa_uf("pnadc_taxa_desocupacao_uf_2012_2024.csv", "taxa_desocupacao")
    info_uf, info_br = tratar_taxa_uf("pnadc_taxa_informalidade_uf_2016_2024.csv", "taxa_informalidade")
    base_uf = deso_uf.merge(info_uf, on=["uf", "sigla", "regiao", "ano"], how="left")
    base_uf = base_uf.sort_values(["ano", "sigla"]).reset_index(drop=True)
    brasil = deso_br.merge(info_br, on="ano", how="left")

    tabelas = {
        "trabalho_uf": base_uf,
        "trabalho_brasil_taxas": brasil,
        "trabalho_brasil_indicadores": tratar_indicadores_brasil(),
        "trabalho_atividade_posicao": tratar_atividade_posicao(),
        "trabalho_genero_raca": tratar_genero(),
    }
    TRATADOS.mkdir(parents=True, exist_ok=True)
    for nome, df in tabelas.items():
        df.to_csv(TRATADOS / f"{nome}.csv", index=False, encoding="utf-8")
    with pd.ExcelWriter(TRATADOS / "base_trabalho_emprego_tratada.xlsx") as w:
        for nome, df in tabelas.items():
            df.to_excel(w, sheet_name=nome[:31], index=False)
    return tabelas


def carregar() -> dict[str, pd.DataFrame]:
    """Lê as bases tratadas (gera novamente se ainda não existirem)."""
    nomes = ["trabalho_uf", "trabalho_brasil_taxas", "trabalho_brasil_indicadores",
             "trabalho_atividade_posicao", "trabalho_genero_raca"]
    if not all((TRATADOS / f"{n}.csv").exists() for n in nomes):
        return executar()
    return {n: pd.read_csv(TRATADOS / f"{n}.csv") for n in nomes}


if __name__ == "__main__":
    t = executar()
    for nome, df in t.items():
        print(f"{nome}: {df.shape[0]} linhas x {df.shape[1]} colunas")
