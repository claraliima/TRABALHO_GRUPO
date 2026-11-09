"""
ETL — Indicador 2: Alfabetização por sexo e raça (Clara Lima).

Bases brutas (dados/brutos) -> bases tratadas (dados/tratados):
  * alfabetizacao_uf.csv      : taxas de alfabetização/analfabetismo por UF (total e quilombolas), 2022
  * alfabetizacao_recortes.csv: recortes nacionais e regionais (sexo, cor ou raça, idade, região,
                                tamanho do município, série histórica 1940-2022)

Todas as taxas referem-se a pessoas de 15 anos ou mais. Como
alfabetização + analfabetismo = 100%, o ETL calcula a taxa que estiver faltando.

Execute a partir da raiz do repositório:
    python -m individuais.clara_lima_alfabetizacao.etl_alfabetizacao
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.carregamento import anexar_uf, ler_ibge, nome_coluna, para_numero

PASTA = Path(__file__).resolve().parent
BRUTOS = PASTA / "dados" / "brutos"
TRATADOS = PASTA / "dados" / "tratados"


def tratar_uf() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "censo2022_analfabetismo_uf.csv", ["Unidade da Federação", "analfabetismo"])
    df.columns = ["uf", "analfabetismo_total", "analfabetismo_quilombolas"]
    for c in df.columns[1:]:
        df[c] = df[c].map(para_numero)
    df = df[df["uf"] != "Brasil"]
    df = anexar_uf(df, "uf")
    assert df["sigla"].notna().all() and len(df) == 27
    df["alfabetizacao_total"] = (100 - df["analfabetismo_total"]).round(2)
    df["alfabetizacao_quilombolas"] = (100 - df["analfabetismo_quilombolas"]).round(2)
    df["gap_quilombola_pp"] = (df["analfabetismo_quilombolas"] - df["analfabetismo_total"]).round(2)
    df["ano"] = 2022
    return df[["uf", "sigla", "regiao", "ano", "alfabetizacao_total", "analfabetismo_total",
               "alfabetizacao_quilombolas", "analfabetismo_quilombolas", "gap_quilombola_pp"]] \
        .sort_values("sigla").reset_index(drop=True)


def tratar_recortes() -> pd.DataFrame:
    df = ler_ibge(BRUTOS / "censo_alfabetizacao_recortes.csv", ["Recorte", "Grupo", "Indicador", "Valor"])
    df.columns = [nome_coluna(c) for c in df.columns]
    df["valor"] = df["valor"].map(para_numero)
    df["ano"] = df["ano"].astype(int)
    # Padroniza tudo em duas colunas: taxa de alfabetização e taxa de analfabetismo
    alf = df["indicador"].eq("Taxa de alfabetização")
    df["taxa_alfabetizacao"] = df["valor"].where(alf, 100 - df["valor"]).round(2)
    df["taxa_analfabetismo"] = (100 - df["taxa_alfabetizacao"]).round(2)
    return df[["recorte", "grupo", "subgrupo", "ano", "taxa_alfabetizacao", "taxa_analfabetismo"]]


def executar() -> dict[str, pd.DataFrame]:
    tabelas = {"alfabetizacao_uf": tratar_uf(), "alfabetizacao_recortes": tratar_recortes()}
    TRATADOS.mkdir(parents=True, exist_ok=True)
    for nome, df in tabelas.items():
        df.to_csv(TRATADOS / f"{nome}.csv", index=False, encoding="utf-8")
    with pd.ExcelWriter(TRATADOS / "base_alfabetizacao_tratada.xlsx") as w:
        for nome, df in tabelas.items():
            df.to_excel(w, sheet_name=nome, index=False)
    return tabelas


def carregar() -> dict[str, pd.DataFrame]:
    nomes = ["alfabetizacao_uf", "alfabetizacao_recortes"]
    if not all((TRATADOS / f"{n}.csv").exists() for n in nomes):
        return executar()
    return {n: pd.read_csv(TRATADOS / f"{n}.csv") for n in nomes}


if __name__ == "__main__":
    for nome, df in executar().items():
        print(f"{nome}: {df.shape[0]} linhas x {df.shape[1]} colunas")
