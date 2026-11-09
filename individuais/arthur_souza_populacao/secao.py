"""
Seção individual — Indicador 1: População por Grupo de Idade, Sexo e Raça.
Responsável: Arthur de Souza.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import estatistica as est
from core import ui
from core.carregamento import REGIOES, Esquema
from individuais.arthur_souza_populacao.etl_populacao import carregar

AUTOR = "Arthur de Souza"
CORES_RACA = {"Branca": ui.AZUL, "Parda": ui.LARANJA, "Preta": ui.VIOLETA, "Amarela": ui.AMARELO,
              "Indígena": ui.VERDE_AGUA, "Sem declaração": ui.CINZA}
ORDEM_RACA = ["Branca", "Parda", "Preta", "Amarela", "Indígena", "Sem declaração"]

ESQ_IDADE = Esquema("pop_idade_sexo", ["regiao", "grupo_idade", "sexo", "situacao", "populacao"],
                    ["populacao", "idade_inicio", "amplitude_classe"],
                    {"regiao": ["grandes regioes", "região"], "grupo_idade": ["grupo de idade", "idade", "faixa etaria"],
                     "populacao": ["valor", "pessoas", "população"]})
ESQ_UF = Esquema("pop_uf", ["uf", "ano", "populacao"], ["ano", "populacao", "densidade"],
                 {"uf": ["unidade da federação", "estado", "sigla"], "populacao": ["população", "valor"]},
                 usa_uf=True, valor_formato_largo="populacao")
ESQ_COR = Esquema("pop_cor_raca", ["regiao", "situacao", "sexo", "cor_raca", "populacao"], ["populacao"],
                  {"cor_raca": ["cor ou raça", "cor", "raca"], "populacao": ["valor", "pessoas"]})

NOTICIAS = [
    {"titulo": "Censo 2022: pela primeira vez desde 1991, a maior parte da população se declara parda",
     "fonte": "Agência IBGE Notícias", "data": "dez/2023",
     "resumo": "Pardos são 45,3% da população; brancos, 43,5%; pretos, 10,2%.",
     "url": "https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agenciade-noticias/noticias/38719-censo-2022-pela-primeira-vez-desde-1991a-maior-parte-da-populacao-do-brasil-se-declara-parda"},
    {"titulo": "Censo 2022 mostra um Brasil com maior proporção de mulheres e mais velho",
     "fonte": "CNN Brasil", "data": "out/2023",
     "resumo": "A idade mediana subiu de 29 para 35 anos e o índice de envelhecimento quase dobrou.",
     "url": "https://www.cnnbrasil.com.br/nacional/censo-2022-mostra-um-brasil-com-maior-proporcao-de-mulheres-e-mais-velho/"},
    {"titulo": "Índice de envelhecimento de amarelos e pretos é o maior entre as categorias de cor ou raça",
     "fonte": "Folha Vitória", "data": "2023",
     "resumo": "Estrutura etária muda conforme a cor ou raça: indígenas e pardos são os grupos mais jovens.",
     "url": "https://www.folhavitoria.com.br/geral/indice-de-envelhecimento-de-amarelos-e-pretos-e-o-maior-entre-categorias-de-cor-ou-raca/"},
    {"titulo": "Sul é a região com mais brancos proporcionalmente; Norte, com mais negros",
     "fonte": "Poder360", "data": "dez/2023",
     "resumo": "A composição por cor ou raça varia muito entre as regiões do país.",
     "url": "https://poder360.com.br/brasil/sul-e-a-regiao-com-mais-brancos-proporcionalmente-norte-com-mais-negros"},
    {"titulo": "Censo 2022 — População por idade e sexo (publicação oficial)",
     "fonte": "IBGE", "data": "out/2023",
     "resumo": "Publicação com pirâmides etárias, razão de sexo e idade mediana do Brasil e regiões.",
     "url": "https://biblioteca.ibge.gov.br/visualizacao/periodicos/3102/cd_2022_populacao_idade_sexo_br.pdf"},
    {"titulo": "Censo 2022 — Identificação étnico-racial da população (publicação oficial)",
     "fonte": "IBGE", "data": "dez/2023",
     "resumo": "Resultados do universo por cor ou raça, sexo e idade.",
     "url": "https://biblioteca.ibge.gov.br/visualizacao/periodicos/3105/cd_2022_etnico_racial.pdf"},
]
IMAGENS = [("populacao_piramide.png", "Envelhecimento: a pirâmide está se estreitando na base"),
           ("populacao_cor_raca.png", "Composição por cor ou raça no Censo 2022")]


def _estatisticas_agrupadas(g: pd.DataFrame) -> dict:
    """g: grupo_idade, idade_inicio, amplitude_classe, populacao (ordenado por idade)."""
    pm = (g["idade_inicio"] + g["amplitude_classe"] / 2).tolist()
    f = g["populacao"].tolist()
    L, h = g["idade_inicio"].tolist(), g["amplitude_classe"].tolist()
    q1 = est.quartil_agrupado(L, h, f, 0.25)
    q3 = est.quartil_agrupado(L, h, f, 0.75)
    return {
        "media": est.media_agrupada(pm, f), "mediana": est.mediana_agrupada(L, h, f), "q1": q1, "q3": q3,
        "iqr": q3 - q1, "desvio": est.desvio_padrao_agrupado(pm, f),
        "modal": est.classe_modal(g["grupo_idade"].tolist(), h, f), "pm": pm,
    }


def render(chave: str = "arthur"):
    tabelas = carregar()
    bases = ui.painel_upload(chave, {
        "População por idade, sexo e situação (regiões)": (ESQ_IDADE, tabelas["pop_idade_sexo"]),
        "População por UF (2010 e 2022)": (ESQ_UF, tabelas["pop_uf"]),
        "População por cor ou raça (regiões)": (ESQ_COR, tabelas["pop_cor_raca"]),
    })
    idade = bases["População por idade, sexo e situação (regiões)"].copy()
    pop_uf = bases["População por UF (2010 e 2022)"].copy()
    cor = bases["População por cor ou raça (regiões)"].copy()
    ind_cor = tabelas["indicadores_cor"]
    if "crescimento_2010_2022_pct" not in pop_uf.columns and {2010, 2022} <= set(pop_uf["ano"].dropna().astype(int)):
        larg = pop_uf.pivot_table(index="sigla", columns="ano", values="populacao")
        pop_uf = pop_uf.merge(((larg[2022] / larg[2010] - 1) * 100).rename("crescimento_2010_2022_pct"),
                              left_on="sigla", right_index=True, how="left")
    if "idade_inicio" not in idade.columns or idade["idade_inicio"].isna().all():
        from individuais.arthur_souza_populacao.etl_populacao import limites_idade
        lim = idade["grupo_idade"].map(limites_idade)
        idade["idade_inicio"], idade["amplitude_classe"] = lim.map(lambda t: t[0]), lim.map(lambda t: t[1])

    # ------------------------------------------------------------------ Filtros
    sb = st.sidebar
    sb.subheader("Filtros — População")
    regioes = sb.multiselect("Regiões", REGIOES, default=REGIOES, key=f"{chave}_reg")
    sexos = sb.multiselect("Sexo", ["Homens", "Mulheres"], default=["Homens", "Mulheres"], key=f"{chave}_sexo")
    situacoes = sb.multiselect("Situação do domicílio", ["Urbana", "Rural"], default=["Urbana", "Rural"],
                               key=f"{chave}_sit")
    inicios = sorted(idade["idade_inicio"].dropna().astype(int).unique().tolist())
    faixa = sb.select_slider("Faixa etária (início do grupo)", options=inicios, value=(inicios[0], inicios[-1]),
                             format_func=lambda v: f"{v}+" if v == inicios[-1] else f"{v} anos", key=f"{chave}_faixa")
    racas = sb.multiselect("Cor ou raça", ORDEM_RACA, default=ORDEM_RACA[:-1], key=f"{chave}_raca")
    ano_uf = sb.radio("Ano (análise por UF)", [2022, 2010], horizontal=True, key=f"{chave}_ano")
    if not (regioes and sexos and situacoes):
        st.warning("Selecione ao menos uma região, um sexo e uma situação do domicílio.")
        return

    f_idade = idade[idade["regiao"].isin(regioes) & idade["sexo"].isin(sexos) & idade["situacao"].isin(situacoes)
                    & idade["idade_inicio"].between(faixa[0], faixa[1])]
    f_cor = cor[cor["regiao"].isin(regioes) & cor["sexo"].isin(sexos) & cor["situacao"].isin(situacoes)
                & cor["cor_raca"].isin(racas)]
    f_uf = pop_uf[pop_uf["regiao"].isin(regioes)]
    ui.botao_download_bases({"idade_filtrado": f_idade, "cor_filtrado": f_cor, "uf_filtrado": f_uf}, "populacao_filtrada",
                            chave)

    ui.cabecalho_secao("População por grupo de idade, sexo e raça", "Indicador 1 · Censo Demográfico 2022 (IBGE)",
                       AUTOR, ["Indicador 1", "Censo 2022", "Estrutura etária"])
    ui.caixa_persona(
        "Por que isso importa para o Ministério do Trabalho, o Sebrae e a Indústria?",
        "A estrutura etária define <b>quem estará em idade de trabalhar</b> nos próximos anos. Um país que envelhece "
        "precisa de mais produtividade, requalificação de trabalhadores maduros e novos mercados (economia prateada). "
        "Perguntas: <b>(a)</b> Qual é a idade típica da população e quão dispersas estão as idades? "
        "<b>(b)</b> Quanto da população está em idade ativa (15 a 64 anos) em cada região? "
        "<b>(c)</b> Como a composição por cor ou raça e sexo varia entre regiões? "
        "<b>(d)</b> Quais estados são outliers em tamanho, densidade e crescimento populacional?")

    abas = st.tabs(["🔺 Pirâmide etária", "📐 Estatística das faixas", "🎨 Cor ou raça", "🗺️ UFs 2010 × 2022",
                    "💡 Respostas", "📰 Notícias"])

    g_sexo = f_idade.groupby(["grupo_idade", "idade_inicio", "amplitude_classe", "sexo"], as_index=False)["populacao"].sum()
    g_tot = f_idade.groupby(["grupo_idade", "idade_inicio", "amplitude_classe"], as_index=False)["populacao"].sum() \
        .sort_values("idade_inicio").reset_index(drop=True)
    total = g_tot["populacao"].sum()
    # Indicadores de estrutura usam o recorte completo de idades (independe do filtro de faixa)
    base_full = idade[idade["regiao"].isin(regioes) & idade["sexo"].isin(sexos) & idade["situacao"].isin(situacoes)]
    tot_full = base_full["populacao"].sum()
    jovens = base_full[base_full["idade_inicio"] < 15]["populacao"].sum()
    ativos = base_full[base_full["idade_inicio"].between(15, 64)]["populacao"].sum()
    idosos65 = base_full[base_full["idade_inicio"] >= 65]["populacao"].sum()
    idosos60 = base_full[base_full["idade_inicio"] >= 60]["populacao"].sum()
    hom = base_full[base_full["sexo"] == "Homens"]["populacao"].sum()
    mul = base_full[base_full["sexo"] == "Mulheres"]["populacao"].sum()

    # ------------------------------------------------------------------ Aba 1
    with abas[0]:
        c = st.columns(5)
        c[0].metric("População no recorte", ui.fmt_mi(total, 2))
        c[1].metric("Razão de sexo", ui.fmt(hom / mul * 100, 1) if hom and mul else "—",
                    help="Homens para cada 100 mulheres")
        c[2].metric("Em idade ativa (15–64)", ui.fmt(ativos / tot_full * 100, 1, "%"))
        c[3].metric("Idosos (65+)", ui.fmt(idosos65 / tot_full * 100, 1, "%"))
        c[4].metric("Índice de envelhecimento", ui.fmt(idosos60 / jovens * 100, 1) if jovens else "—",
                    help="Pessoas de 60+ para cada 100 de 0 a 14 anos")

        piramide = g_sexo.sort_values("idade_inicio")
        fig = go.Figure()
        for sx in ["Homens", "Mulheres"]:
            d = piramide[piramide["sexo"] == sx]
            if d.empty:
                continue
            pct = d["populacao"] / total * 100
            fig.add_bar(y=d["grupo_idade"], x=-pct if sx == "Homens" else pct, orientation="h", name=sx,
                        marker_color=ui.COR_SEXO[sx], customdata=d["populacao"],
                        hovertemplate=sx + " · %{y}<br>%{customdata:,.0f} pessoas<extra></extra>")
        m = max(5, (g_sexo["populacao"] / total * 100).max() + 0.5)
        ticks = [-m, -m / 2, 0, m / 2, m]
        fig.update_layout(barmode="relative", bargap=0.08)
        ui.estilizar(fig, "Pirâmide etária do recorte (% da população filtrada)", "% da população", "Grupo de idade",
                     altura=520)
        fig.update_xaxes(tickvals=ticks, ticktext=[ui.fmt(abs(t), 1) + "%" for t in ticks])
        st.plotly_chart(fig, key=f"{chave}_piramide")
        st.caption("A barra '70 anos ou mais' reúne quatro grupos de 5 anos (70 a 90+), por isso parece maior que as "
                   "vizinhas. Nas idades avançadas o lado feminino é mais largo: as mulheres vivem mais.")

        estrutura = base_full.assign(
            faixa=pd.cut(base_full["idade_inicio"], [-1, 14, 64, 200], labels=["0 a 14", "15 a 64", "65 ou mais"])
        ).groupby(["regiao", "faixa"], observed=True, as_index=False)["populacao"].sum()
        estrutura["pct"] = estrutura["populacao"] / estrutura.groupby("regiao")["populacao"].transform("sum") * 100
        fig = px.bar(estrutura, x="regiao", y="pct", color="faixa", barmode="group",
                     color_discrete_sequence=[ui.VERDE_AGUA, ui.AZUL, ui.LARANJA],
                     text=estrutura["pct"].map(lambda v: ui.fmt(v, 1)))
        ui.estilizar(fig, "Grandes grupos de idade por região (%)", "Região", "% da população da região", altura=400)
        st.plotly_chart(fig, key=f"{chave}_grupos")
        ui.fonte("IBGE, Censo Demográfico 2022 — Anuário Estatístico do Brasil 2024, Tabela 2.1.1.2.")

    # ------------------------------------------------------------------ Aba 2
    with abas[1]:
        if g_tot.empty:
            st.warning("Nenhum dado no recorte.")
        else:
            s = _estatisticas_agrupadas(g_tot)
            st.subheader("Idade da população: medidas para dados agrupados em classes")
            c = st.columns(5)
            c[0].metric("Idade média", ui.fmt(s["media"], 1, " anos"))
            c[1].metric("Idade mediana", ui.fmt(s["mediana"], 1, " anos"))
            c[2].metric("Desvio padrão", ui.fmt(s["desvio"], 1, " anos"))
            c[3].metric("IQR (Q3 − Q1)", ui.fmt(s["iqr"], 1, " anos"))
            c[4].metric("Classe modal", s["modal"])
            st.markdown(
                f"Q1 = **{ui.fmt(s['q1'], 1)} anos** e Q3 = **{ui.fmt(s['q3'], 1)} anos**: metade da população do recorte "
                f"tem entre {ui.fmt(s['q1'], 0)} e {ui.fmt(s['q3'], 0)} anos. A média ({ui.fmt(s['media'], 1)}) fica "
                f"{'acima' if s['media'] > s['mediana'] else 'abaixo'} da mediana ({ui.fmt(s['mediana'], 1)}): "
                f"{est.assimetria_texto(s['media'], s['mediana'])}. A cauda de idosos (classe aberta 70+) puxa a média; "
                "a mediana não depende da hipótese sobre essa classe, por isso é a medida preferida pelo IBGE "
                "(idade mediana oficial do Brasil em 2022: 35 anos).")
            tab = g_tot[["grupo_idade", "idade_inicio", "amplitude_classe", "populacao"]].copy()
            tab["ponto_medio"] = s["pm"]
            tab["freq_relativa_%"] = tab["populacao"] / total * 100
            tab["freq_acumulada"] = tab["populacao"].cumsum()
            tab["freq_acum_%"] = tab["freq_acumulada"] / total * 100
            tab["xi_fi"] = tab["ponto_medio"] * tab["populacao"]
            with st.expander("🧮 Passo a passo do cálculo (tabela de distribuição de frequências)"):
                st.latex(r"\bar{x}=\frac{\sum x_i f_i}{\sum f_i}\qquad Md = L + \frac{\frac{n}{2}-F_{ant}}{f_{Md}}\cdot h"
                         r"\qquad \sigma=\sqrt{\frac{\sum f_i (x_i-\bar{x})^2}{\sum f_i}}")
                st.dataframe(tab.style.format({"populacao": "{:,.0f}", "freq_relativa_%": "{:.2f}", "freq_acumulada": "{:,.0f}",
                                               "freq_acum_%": "{:.2f}", "xi_fi": "{:,.0f}", "ponto_medio": "{:.1f}"}),
                             hide_index=True)
                st.caption("Hipótese: a classe aberta '70 anos ou mais' foi fechada em 90 anos (ponto médio 80). Ela afeta "
                           "a média e o desvio padrão, mas não a mediana nem os quartis.")

            st.markdown("#### Dispersão do tamanho das faixas etárias")
            st.caption("Cada ponto é um grupo quinquenal de idade (exceto 70+). Mostra quais faixas concentram mais "
                       "pessoas no recorte — base para planejar escolas, empregos e previdência.")
            g5 = g_tot[g_tot["amplitude_classe"] == 5].copy()
            g5["populacao_mi"] = g5["populacao"] / 1e6
            ui.bloco_estatistico(g5, "populacao_mi", "grupo_idade", "Pessoas por grupo de 5 anos (milhões)", " mi", 2,
                                 "faixa etária", eixo="População (milhões)", chave=f"{chave}_faixas")

    # ------------------------------------------------------------------ Aba 3
    with abas[2]:
        if f_cor.empty:
            st.warning("Selecione pelo menos uma cor ou raça.")
        else:
            comp = f_cor.groupby(["regiao", "cor_raca"], as_index=False)["populacao"].sum()
            comp["pct"] = comp["populacao"] / comp.groupby("regiao")["populacao"].transform("sum") * 100
            comp["cor_raca"] = pd.Categorical(comp["cor_raca"], ORDEM_RACA)
            comp = comp.sort_values("cor_raca")
            fig = px.bar(comp, y="regiao", x="pct", color="cor_raca", orientation="h", color_discrete_map=CORES_RACA,
                         category_orders={"regiao": REGIOES[::-1]},
                         custom_data=["populacao"], text=comp["pct"].map(lambda v: ui.fmt(v, 0) if v >= 4 else ""))
            fig.update_traces(marker_line_color="white", marker_line_width=2,
                              hovertemplate="%{y} · %{fullData.name}<br>%{x:.1f}% (%{customdata[0]:,.0f} pessoas)<extra></extra>")
            fig.update_layout(barmode="stack")
            ui.estilizar(fig, "Composição por cor ou raça em cada região (% da população do recorte)",
                         "% da população", "Região", altura=420)
            st.plotly_chart(fig, key=f"{chave}_cor_comp")

            c1, c2 = st.columns(2)
            with c1:
                rs = f_cor.pivot_table(index="cor_raca", columns="sexo", values="populacao", aggfunc="sum")
                if {"Homens", "Mulheres"} <= set(rs.columns):
                    rs["razao"] = rs["Homens"] / rs["Mulheres"] * 100
                    rs = rs.reindex([r for r in ORDEM_RACA if r in rs.index]).dropna()
                    fig = go.Figure(go.Bar(x=rs.index, y=rs["razao"], marker_color=[CORES_RACA[r] for r in rs.index],
                                           text=rs["razao"].map(lambda v: ui.fmt(v, 1)), textposition="outside"))
                    fig.add_hline(y=100, line=dict(color=ui.CINZA, dash="dot"))
                    ui.estilizar(fig, "Razão de sexo por cor ou raça (linha = equilíbrio, 100)", "Cor ou raça",
                                 "Homens por 100 mulheres", altura=400, legenda=False)
                    st.plotly_chart(fig, key=f"{chave}_rs_cor")
                else:
                    st.info("Selecione os dois sexos para ver a razão de sexo.")
            with c2:
                d = ind_cor[ind_cor["cor_raca"] != "Total"]
                fig = go.Figure(go.Bar(x=d["cor_raca"], y=d["idade_mediana"],
                                       marker_color=[CORES_RACA[r] for r in d["cor_raca"]],
                                       text=d["idade_mediana"].map(lambda v: f"{v:.0f} anos"), textposition="outside"))
                fig.add_hline(y=35, line=dict(color=ui.CINZA, dash="dot"))
                ui.estilizar(fig, "Idade mediana por cor ou raça — 2022 (linha = Brasil, 35 anos)", "Cor ou raça", "Idade mediana (anos)",
                             altura=400, legenda=False)
                st.plotly_chart(fig, key=f"{chave}_idade_cor")
            sit = f_cor.groupby(["situacao", "cor_raca"], as_index=False)["populacao"].sum()
            sit["pct"] = sit["populacao"] / sit.groupby("situacao")["populacao"].transform("sum") * 100
            tab_sit = sit.pivot(index="cor_raca", columns="situacao", values="pct").round(1) \
                .reindex([r for r in ORDEM_RACA if r in sit["cor_raca"].unique()])
            tab_sit = tab_sit[[c for c in ["Urbana", "Rural"] if c in tab_sit.columns]]
            tab_sit.index.name = "Cor ou raça"
            st.dataframe(tab_sit.reset_index(), hide_index=True,
                         column_config={c: st.column_config.NumberColumn(f"{c} (%)", format="%.1f") for c in ["Urbana", "Rural"]})
            st.caption("Distribuição (%) por cor ou raça nas áreas urbanas e rurais do recorte. Indígenas: quesito cor ou "
                       "raça (1,23 mi); com o quesito 'se considera indígena', o total chega a 1,69 mi.")
        ui.fonte("IBGE, Censo 2022 — Anuário Estatístico 2024, Tabela 2.1.4.1; Identificação étnico-racial (dez/2023).")

    # ------------------------------------------------------------------ Aba 4
    with abas[3]:
        opcoes = {"populacao": "População residente", "densidade": "Densidade demográfica (hab/km²)",
                  "crescimento_2010_2022_pct": "Crescimento 2010→2022 (%)"}
        var = st.radio("Indicador por UF", list(opcoes), format_func=opcoes.get, horizontal=True, key=f"{chave}_var_uf")
        d = f_uf[f_uf["ano"] == ano_uf].copy()
        if var not in d.columns or d[var].isna().all():
            st.info("A base em uso não tem esse indicador.")
        else:
            if var == "populacao":
                d["valor"] = d["populacao"] / 1e6
                un, casas, eixo = " mi", 2, "População (milhões)"
            else:
                d["valor"] = d[var]
                un, casas, eixo = ("%" if "cresc" in var else ""), 1, opcoes[var]
            c1, c2 = st.columns([1.3, 1])
            with c1:
                o = d.sort_values("valor", ascending=False)
                fig = go.Figure(go.Bar(x=o["sigla"], y=o["valor"], marker_color=[ui.COR_REGIAO[r] for r in o["regiao"]],
                                       customdata=o["uf"], hovertemplate="%{customdata}: %{y:.2f}<extra></extra>"))
                ui.estilizar(fig, f"{opcoes[var]} por UF — {ano_uf}", "UF", eixo, altura=420, legenda=False)
                st.plotly_chart(fig, key=f"{chave}_uf_bar")
                st.caption("Cores = regiões: azul Norte · laranja Nordeste · verde-água Sudeste · violeta Sul · "
                           "rosa Centro-Oeste.")
            with c2:
                mapa = ui.mapa_ufs(d, "valor", f"Mapa — {opcoes[var]}", eixo, casas=casas, altura=420)
                st.plotly_chart(mapa, key=f"{chave}_uf_mapa")
            ui.bloco_estatistico(d, "valor", "sigla", f"{opcoes[var]} — {ano_uf}", un, casas, "UF", eixo=eixo,
                                 chave=f"{chave}_uf_est")
        ui.fonte("IBGE, Censos Demográficos 2010 e 2022; Anuário Estatístico do Brasil 2024, Tabela 2.1.3.1.")

    # ------------------------------------------------------------------ Aba 5
    with abas[4]:
        _respostas(idade, pop_uf, cor, ind_cor)

    with abas[5]:
        st.subheader("Notícias e contexto")
        ui.bloco_noticias(NOTICIAS, IMAGENS, chave)


def _respostas(idade, pop_uf, cor, ind_cor):
    st.caption("Respostas calculadas com o Brasil inteiro (todas as regiões, sexos e situações).")
    g = idade.groupby(["grupo_idade", "idade_inicio", "amplitude_classe"], as_index=False)["populacao"].sum() \
        .sort_values("idade_inicio")
    s = _estatisticas_agrupadas(g)
    ui.resposta("(a) Qual é a idade típica e quão dispersas são as idades?",
                f"Pela tabela de frequências, a idade mediana é {ui.fmt(s['mediana'], 1)} anos (IBGE oficial: 35) e a média "
                f"{ui.fmt(s['media'], 1)} anos; Q1 = {ui.fmt(s['q1'], 1)} e Q3 = {ui.fmt(s['q3'], 1)} anos "
                f"(IQR = {ui.fmt(s['iqr'], 1)} anos) e desvio padrão ≈ {ui.fmt(s['desvio'], 1)} anos. A média acima da "
                "mediana mostra a cauda longa de idosos. <b>Para a Indústria e o Sebrae:</b> a metade central da população "
                f"tem entre {ui.fmt(s['q1'], 0)} e {ui.fmt(s['q3'], 0)} anos — a força de trabalho está amadurecendo, o que "
                "pede requalificação de trabalhadores de 40+ e produtos/serviços para um público mais velho.")
    reg = idade.assign(ativa=idade["idade_inicio"].between(15, 64), idoso=idade["idade_inicio"] >= 65)
    t = reg.groupby("regiao").apply(lambda d: pd.Series({
        "ativa": d.loc[d["ativa"], "populacao"].sum() / d["populacao"].sum() * 100,
        "idosos": d.loc[d["idoso"], "populacao"].sum() / d["populacao"].sum() * 100}), include_groups=False)
    txt = "; ".join(f"{r}: {ui.fmt(t.loc[r, 'ativa'], 1)}% ativos e {ui.fmt(t.loc[r, 'idosos'], 1)}% com 65+" for r in t.index)
    ui.resposta("(b) Quanto da população está em idade ativa em cada região?",
                f"{txt}. O Centro-Oeste tem a maior parcela em idade ativa; Sudeste e Sul, a maior de idosos; o Norte é a "
                "região mais jovem. <b>Para o Ministério do Trabalho:</b> no Norte, a prioridade é gerar o primeiro "
                "emprego para muitos jovens; no Sul/Sudeste, manter idosos ativos e preparar a reposição de mão de obra.")
    tot = cor.groupby("cor_raca")["populacao"].sum()
    pp = (tot.get("Preta", 0) + tot.get("Parda", 0)) / tot.sum() * 100
    sul = cor[cor["regiao"] == "Sul"].groupby("cor_raca")["populacao"].sum()
    norte = cor[cor["regiao"] == "Norte"].groupby("cor_raca")["populacao"].sum()
    ic = ind_cor.set_index("cor_raca")
    ui.resposta("(c) Como a composição por cor ou raça e sexo varia?",
                f"Pretos e pardos somam {ui.fmt(pp, 1)}% da população. A composição é muito diferente entre regiões: no "
                f"Sul, brancos são {ui.fmt(sul['Branca'] / sul.sum() * 100, 1)}%; no Norte, pardos são "
                f"{ui.fmt(norte['Parda'] / norte.sum() * 100, 1)}%. A razão de sexo também varia por cor ou raça: "
                f"{ui.fmt(ic.loc['Preta', 'razao_sexo'], 1)} entre pretos (mais homens) e {ui.fmt(ic.loc['Branca', 'razao_sexo'], 1)} "
                f"entre brancos. Indígenas têm idade mediana de {ic.loc['Indígena', 'idade_mediana']:.0f} anos, contra "
                f"{ic.loc['Branca', 'idade_mediana']:.0f} dos brancos. <b>Leitura:</b> programas de emprego precisam de metas "
                "regionais e raciais, não só nacionais.")
    d = pop_uf[pop_uf["ano"] == 2022]
    partes = []
    for col, nome, un in [("populacao", "população", ""), ("densidade", "densidade", " hab/km²"),
                          ("crescimento_2010_2022_pct", "crescimento 2010-2022", "%")]:
        v = d[col] / 1e6 if col == "populacao" else d[col]
        r = est.resumo(v.tolist(), d["sigla"].tolist())
        imp = est.impacto_outliers(v.tolist(), d["sigla"].tolist())
        u = " mi" if col == "populacao" else un
        outs = ", ".join(f"{n} ({ui.fmt(x, 1)}{u})" for n, x, _ in r["outliers"]) or "nenhum"
        partes.append(f"<b>{nome.capitalize()}</b>: outliers {outs}; média {ui.fmt(imp['media_com'], 1)}{u} × mediana "
                      f"{ui.fmt(imp['mediana_com'], 1)}{u} (sem outliers, média {ui.fmt(imp['media_sem'], 1)}{u})")
    ui.resposta("(d) Quais estados são outliers em tamanho, densidade e crescimento?",
                "<br>".join(partes) + ".<br>Nos três casos a média fica bem acima da mediana porque poucos estados "
                "extremos (SP e MG em população; DF e RJ em densidade; Roraima — com a imigração venezuelana — em "
                "crescimento) puxam a média. A <b>mediana</b> é a medida que descreve o estado 'típico'.")
