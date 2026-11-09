"""
Seção do GRUPO — Tema 6: Trabalho e Emprego.
Personas: Ministério do Trabalho, Sebrae e Indústria.
Foco: taxa de desocupação (2012 × 2022) e informalidade.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import estatistica as est
from core import ui
from core.carregamento import REGIOES, UFS, Esquema
from grupo_trabalho_emprego.etl_trabalho import carregar

NOMES_INDICADOR = {"taxa_desocupacao": "Taxa de desocupação (%)", "taxa_informalidade": "Taxa de informalidade (%)"}

ESQ_UF = Esquema(
    nome="trabalho_uf",
    obrigatorias=["uf", "ano", "taxa_desocupacao"],
    numericas=["ano", "taxa_desocupacao", "taxa_informalidade"],
    apelidos={"uf": ["unidade da federação", "unidade_da_federacao", "estado", "sigla", "uf"],
              "taxa_desocupacao": ["taxa de desocupação", "desocupacao", "taxa_de_desocupacao", "valor"],
              "taxa_informalidade": ["taxa de informalidade", "informalidade", "taxa_de_informalidade"],
              "ano": ["ano", "periodo", "período"]},
    usa_uf=True, valor_formato_largo="taxa_desocupacao",
)
ESQ_ATIV = Esquema(
    nome="trabalho_atividade_posicao",
    obrigatorias=["tipo", "categoria", "ano", "mil_pessoas"],
    numericas=["ano", "mil_pessoas"],
    apelidos={"mil_pessoas": ["valor", "pessoas", "ocupados"]},
)

NOTICIAS = [
    {"titulo": "Em 2024, 14 unidades da federação registram a menor taxa de desocupação da série",
     "fonte": "Agência IBGE Notícias", "data": "fev/2025",
     "resumo": "Balanço anual da PNAD Contínua por UF: queda generalizada do desemprego após o pico da pandemia.",
     "url": "https://agenciadenoticias.ibge.gov.br/agencia-noticias/42707-em-2024-14-unidades-da-federacao-registram-a-menor-taxa-de-desocupacao-da-serie.html"},
    {"titulo": "Desemprego cai a 9,3% em 2022, menor índice desde 2015",
     "fonte": "Congresso em Foco", "data": "fev/2023",
     "resumo": "Média anual de 2022 marca a recuperação do mercado de trabalho depois de 2020-2021.",
     "url": "https://congressoemfoco.com.br/noticia/19813/desemprego-cai-a-93-em-2022-menor-indice-desde-2015"},
    {"titulo": "Emprego sem carteira assinada atingiu volume recorde em 2022",
     "fonte": "Movimento Econômico", "data": "fev/2023",
     "resumo": "Reportagem sobre o recorde de empregados sem carteira em 2022 — tema central para Ministério e Sebrae.",
     "url": "https://movimentoeconomico.com.br/geral/redacao/2023/02/28/emprego-sem-carteira-assinada-atingiu-volume-recorde-em-2022/"},
    {"titulo": "Desemprego segue maior entre mulheres, negros e jovens",
     "fonte": "Brasil de Fato", "data": "ago/2022",
     "resumo": "PNAD mostra que o desemprego não atinge todos da mesma forma; 30% procuravam emprego há mais de 2 anos.",
     "url": "https://www.brasildefato.com.br/2022/08/12/desemprego-segue-maior-entre-mulheres-negros-e-jovens-30-procuram-emprego-ha-mais-de-2-anos"},
    {"titulo": "Bahia registra 3º maior índice de informalidade e 2º menor rendimento do país",
     "fonte": "Bahia Notícias", "data": "2023",
     "resumo": "Reportagem sobre informalidade e rendimento na Bahia a partir da PNAD Contínua.",
     "url": "https://www.bahianoticias.com.br/noticia/314072-bahia-registra-3o-maior-indice-de-informalidade-e-2o-menor-rendimento-mensal-pais-aponta-ibge"},
    {"titulo": "PNAD Contínua — Retrospectiva 2012-2022 (publicação oficial)",
     "fonte": "IBGE", "data": "2023",
     "resumo": "Documento do IBGE com a evolução de uma década de mercado de trabalho no Brasil.",
     "url": "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Principais_destaques_PNAD_continua/2012_2022/PNAD_continua_retrospectiva_2012_2022.pdf"},
]
IMAGENS = [("trabalho_informalidade.png", "Informalidade: o desafio do Ministério do Trabalho"),
           ("trabalho_industria.png", "Indústria: emprego ainda abaixo de 2012"),
           ("trabalho_empreendedorismo.png", "Sebrae: formalização do conta própria")]


def _filtros(df: pd.DataFrame, chave: str):
    sb = st.sidebar
    sb.subheader("Filtros — Trabalho e Emprego")
    indicador = sb.radio("Indicador", list(NOMES_INDICADOR), format_func=NOMES_INDICADOR.get, key=f"{chave}_ind")
    anos = sorted(df.dropna(subset=[indicador])["ano"].unique().tolist())
    if not anos:
        st.error("A base não tem valores para este indicador.")
        st.stop()
    padrao_ini = 2012 if 2012 in anos else anos[0]
    padrao_fim = 2022 if 2022 in anos else anos[-1]
    ano_ini, ano_fim = sb.select_slider("Comparar os anos", options=anos, value=(padrao_ini, padrao_fim),
                                        key=f"{chave}_anos_{indicador}")
    regioes = sb.multiselect("Regiões", REGIOES, default=REGIOES, key=f"{chave}_reg")
    ufs_disp = UFS[UFS["regiao"].isin(regioes)]["sigla"].tolist()
    ufs = sb.multiselect("UFs", ufs_disp, default=ufs_disp, key=f"{chave}_ufs_{'-'.join(regioes)}")
    return indicador, int(ano_ini), int(ano_fim), regioes, ufs


def render(chave: str = "t6"):
    tabelas = carregar()
    bases = ui.painel_upload(chave, {
        "Taxas por UF e ano (desocupação/informalidade)": (ESQ_UF, tabelas["trabalho_uf"]),
        "Ocupados por atividade e posição (Brasil)": (ESQ_ATIV, tabelas["trabalho_atividade_posicao"]),
    })
    base = bases["Taxas por UF e ano (desocupação/informalidade)"].copy()
    if "taxa_informalidade" not in base.columns:
        base["taxa_informalidade"] = float("nan")
    ativ = bases["Ocupados por atividade e posição (Brasil)"]
    indic_br = tabelas["trabalho_brasil_indicadores"]
    taxas_br = tabelas["trabalho_brasil_taxas"]
    genero = tabelas["trabalho_genero_raca"]

    indicador, ano_ini, ano_fim, regioes, ufs = _filtros(base, chave)
    nome_ind = NOMES_INDICADOR[indicador]
    filt = base[base["sigla"].isin(ufs)]
    if filt.empty:
        st.warning("Nenhuma UF selecionada. Ajuste os filtros da barra lateral.")
        return
    ui.botao_download_bases({"uf_filtrado": filt, **tabelas}, "trabalho_emprego_filtrado", chave)

    ui.cabecalho_secao("Trabalho e Emprego: desocupação e informalidade",
                       "Tema 6 · PNAD Contínua (IBGE) · Painel do grupo", "Arthur de Souza, Clara Lima e Gustavo Henrique",
                       ["Tema 6", "PNAD Contínua", f"{ano_ini} × {ano_fim}"])
    ui.caixa_persona(
        "Cenário — reunião com Ministério do Trabalho, Sebrae e Indústria",
        "A <b>Ministra do Trabalho</b> quer saber onde o desemprego ficou mais grave entre 2012 e 2022 para "
        "direcionar programas de qualificação e intermediação de mão de obra. O <b>Sebrae</b> precisa localizar os "
        "estados com mais trabalhadores informais para priorizar ações de formalização (MEI/CNPJ). A "
        "<b>Indústria</b> quer entender se o emprego industrial se recuperou e onde há mão de obra disponível. "
        "Nossa startup cruzou as séries oficiais da PNAD Contínua para responder:<br>"
        "1) Como a taxa de desocupação mudou entre 2012 e 2022 em cada UF e região? "
        "2) O desemprego ficou mais desigual entre os estados? "
        "3) Onde a informalidade é maior e ela anda junto com o desemprego? "
        "4) O que aconteceu com o emprego industrial e com o trabalho por conta própria? "
        "5) Quem são os mais afetados (sexo e cor ou raça)?")

    abas = st.tabs(["📊 2012 × 2022", "📐 Estatística e outliers", "🧾 Informalidade", "🏭 Indústria e Sebrae",
                    "👥 Sexo e cor ou raça", "💡 Respostas às perguntas", "📰 Notícias"])

    ini = filt[filt["ano"] == ano_ini].set_index("sigla")
    fim = filt[filt["ano"] == ano_fim].set_index("sigla")
    comp = pd.DataFrame({"uf": fim["uf"], "regiao": fim["regiao"], "ini": ini[indicador], "fim": fim[indicador]})
    comp["var_pp"] = comp["fim"] - comp["ini"]
    comp = comp.dropna(subset=["ini", "fim"]).reset_index()

    # ------------------------------------------------------------------ Aba 1
    with abas[0]:
        br = taxas_br.set_index("ano")[indicador] if indicador in taxas_br.columns else pd.Series(dtype=float)
        c = st.columns(5)
        c[0].metric(f"Brasil {ano_ini}", ui.fmt(br.get(ano_ini), 1, "%"))
        c[1].metric(f"Brasil {ano_fim}", ui.fmt(br.get(ano_fim), 1, "%"),
                    delta=f"{ui.fmt(br.get(ano_fim, float('nan')) - br.get(ano_ini, float('nan')), 1)} p.p.",
                    delta_color="inverse")
        c[2].metric(f"Mediana das UFs {ano_fim}", ui.fmt(est.mediana(comp["fim"]), 1, "%"))
        if not comp.empty:
            pior = comp.loc[comp["fim"].idxmax()]
            c[3].metric(f"Maior taxa em {ano_fim}", f"{pior['sigla']} · {ui.fmt(pior['fim'], 1, '%')}")
            c[4].metric("UFs que pioraram", f"{int((comp['var_pp'] > 0).sum())} de {len(comp)}")

        ordem = comp.sort_values("fim", ascending=False)
        fig = go.Figure()
        fig.add_bar(x=ordem["sigla"], y=ordem["ini"], name=str(ano_ini), marker_color=ui.AZUL,
                    customdata=ordem["uf"], hovertemplate="%{customdata}<br>" + str(ano_ini) + ": %{y:.1f}%<extra></extra>")
        fig.add_bar(x=ordem["sigla"], y=ordem["fim"], name=str(ano_fim), marker_color=ui.LARANJA,
                    customdata=ordem["uf"], hovertemplate="%{customdata}<br>" + str(ano_fim) + ": %{y:.1f}%<extra></extra>")
        if ano_fim in br.index and pd.notna(br[ano_fim]):
            fig.add_hline(y=br[ano_fim], line=dict(color=ui.CINZA, dash="dot"),
                          annotation_text=f"Brasil {ano_fim}: {ui.fmt(br[ano_fim], 1, '%')}")
        ui.estilizar(fig, f"{nome_ind} por UF — {ano_ini} × {ano_fim} (ordenado por {ano_fim})",
                     "Unidade da Federação", nome_ind, altura=440)
        fig.update_layout(barmode="group", bargroupgap=0.08)
        st.plotly_chart(fig, key=f"{chave}_barras")

        g1, g2 = st.columns([1, 1])
        with g1:
            lim = max(abs(comp["var_pp"].min()), abs(comp["var_pp"].max()), 0.1)
            mapa = ui.mapa_ufs(comp, "var_pp", f"Variação {ano_ini}→{ano_fim} (p.p.) · laranja = piorou",
                               "Variação (p.p.)", escala=["#2a78d6", "#9ec5f4", "#e9e8e4", "#f6b89c", "#eb6834"],
                               faixa=(-lim, lim), altura=420)
            st.plotly_chart(mapa, key=f"{chave}_mapa")
        with g2:
            serie = filt.groupby(["regiao", "ano"], as_index=False)[indicador].median()
            fig2 = px.line(serie, x="ano", y=indicador, color="regiao", color_discrete_map=ui.COR_REGIAO, markers=True)
            if not br.dropna().empty:
                fig2.add_scatter(x=br.dropna().index, y=br.dropna().values, name="Brasil", mode="lines+markers",
                                 line=dict(color=ui.TINTA, width=3, dash="dot"))
            fig2.add_vrect(x0=ano_ini - 0.15, x1=ano_ini + 0.15, fillcolor=ui.AZUL, opacity=0.12, line_width=0)
            fig2.add_vrect(x0=ano_fim - 0.15, x1=ano_fim + 0.15, fillcolor=ui.LARANJA, opacity=0.12, line_width=0)
            fig2.update_traces(line_width=2, marker_size=7)
            ui.estilizar(fig2, "Evolução: mediana das UFs por região e média Brasil", "Ano", nome_ind, altura=420)
            st.plotly_chart(fig2, key=f"{chave}_linha")

        with st.expander("Tabela comparativa por UF"):
            t = comp.sort_values("var_pp", ascending=False).rename(columns={
                "sigla": "Sigla", "uf": "UF", "regiao": "Região", "ini": f"{ano_ini} (%)", "fim": f"{ano_fim} (%)",
                "var_pp": "Variação (p.p.)"})
            st.dataframe(t, hide_index=True)
        ui.fonte("IBGE, PNAD Contínua — Retrospectiva 2012-2024 (médias anuais).")

    # ------------------------------------------------------------------ Aba 2
    with abas[1]:
        st.subheader(f"{nome_ind}: medidas estatísticas entre as UFs selecionadas")
        ano_est = st.radio("Ano analisado", [ano_ini, ano_fim], index=1, horizontal=True, key=f"{chave}_ano_est")
        dados_ano = filt[filt["ano"] == ano_est]
        ui.bloco_estatistico(dados_ano, indicador, "sigla", f"{nome_ind} — {ano_est}", "%", 1, "UF",
                             eixo=nome_ind, chave=f"{chave}_est")

        st.markdown(f"#### Comparação da dispersão: {ano_ini} × {ano_fim}")
        r1 = est.resumo(comp["ini"].tolist(), comp["sigla"].tolist())
        r2 = est.resumo(comp["fim"].tolist(), comp["sigla"].tolist())
        medidas = [("Média", "media"), ("Mediana", "mediana"), ("Q1", "q1"), ("Q3", "q3"), ("IQR", "iqr"),
                   ("Amplitude", "amplitude"), ("Desvio padrão (pop.)", "desvio_pop"), ("Coef. de variação (%)", "cv")]
        tab = pd.DataFrame({"Medida": [m for m, _ in medidas],
                            str(ano_ini): [ui.fmt(r1[k], 2) for _, k in medidas],
                            str(ano_fim): [ui.fmt(r2[k], 2) for _, k in medidas],
                            "Diferença": [ui.fmt(r2[k] - r1[k], 2) for _, k in medidas]})
        cA, cB = st.columns([1, 1.3])
        cA.dataframe(tab, hide_index=True)
        longo = pd.concat([comp.assign(ano=str(ano_ini), valor=comp["ini"]), comp.assign(ano=str(ano_fim), valor=comp["fim"])])
        with cB:
            st.plotly_chart(ui.boxplot(longo, "valor", "sigla", f"Boxplot {ano_ini} × {ano_fim}", nome_ind, grupo="ano",
                                       cores={str(ano_ini): ui.AZUL, str(ano_fim): ui.LARANJA}), key=f"{chave}_box2")
        mais = "aumentou" if r2["desvio_pop"] > r1["desvio_pop"] else "diminuiu"
        st.info(f"O desvio padrão entre as UFs {mais} de {ui.fmt(r1['desvio_pop'], 2)} p.p. para "
                f"{ui.fmt(r2['desvio_pop'], 2)} p.p. e o IQR foi de {ui.fmt(r1['iqr'], 1)} para {ui.fmt(r2['iqr'], 1)} p.p.: "
                f"a desigualdade regional do indicador {mais} entre {ano_ini} e {ano_fim}.")

        st.markdown(f"#### Distribuição por região em {ano_est}")
        st.plotly_chart(ui.boxplot(dados_ano.sort_values("regiao"), indicador, "sigla",
                                   f"{nome_ind} por região — {ano_est}", nome_ind, grupo="regiao",
                                   cores=ui.COR_REGIAO), key=f"{chave}_box_reg")
        linhas = []
        for reg, dr in dados_ano.groupby("regiao"):
            if len(dr) < 4:
                continue
            rr = est.resumo(dr[indicador].tolist(), dr["sigla"].tolist())
            ii = est.impacto_outliers(dr[indicador].tolist(), dr["sigla"].tolist())
            linhas.append({"Região": reg, "n": rr["n"], "Média": ui.fmt(rr["media"], 2), "Mediana": ui.fmt(rr["mediana"], 1),
                           "Limite superior": ui.fmt(rr["limite_superior"], 1),
                           "Outliers": ", ".join(f"{n} ({ui.fmt(v, 1)})" for n, v, _ in rr["outliers"]) or "—",
                           "Média sem outliers": ui.fmt(ii["media_sem"], 2) if rr["outliers"] else "—"})
        if linhas:
            st.markdown("**Outliers dentro de cada região (regra 1,5×IQR aplicada às UFs da própria região)**")
            st.dataframe(pd.DataFrame(linhas), hide_index=True)
            tem_rj = any("RJ" in l["Outliers"] for l in linhas) and indicador == "taxa_desocupacao"
            st.caption("Mesmo quando as 27 UFs juntas não têm extremos, dentro de uma região um estado pode destoar dos "
                       "vizinhos. " + ("Aqui o Rio de Janeiro é outlier do Sudeste: reflexo da crise fiscal do estado e "
                                       "da retração da cadeia de petróleo e gás. Com o RJ, a média do Sudeste sobe e se "
                                       "afasta da mediana — por isso a mediana representa melhor a região."
                                       if tem_rj else "Quando há outlier, compare a média com e sem ele: se ela muda "
                                       "muito e a mediana não, a mediana é o melhor resumo da região."))

    # ------------------------------------------------------------------ Aba 3
    with abas[2]:
        anos_inf = sorted(filt.dropna(subset=["taxa_informalidade"])["ano"].unique().tolist())
        if not anos_inf:
            st.info("A base em uso não tem a coluna de informalidade.")
        else:
            ano_inf = st.select_slider("Ano da informalidade", anos_inf, value=2022 if 2022 in anos_inf else anos_inf[-1],
                                       key=f"{chave}_ano_inf")
            d = filt[filt["ano"] == ano_inf].dropna(subset=["taxa_informalidade", "taxa_desocupacao"])
            c1, c2 = st.columns(2)
            with c1:
                o = d.sort_values("taxa_informalidade")
                fig = go.Figure(go.Bar(x=o["taxa_informalidade"], y=o["sigla"], orientation="h",
                                       marker_color=[ui.COR_REGIAO.get(r, ui.AZUL) for r in o["regiao"]],
                                       customdata=o[["uf", "regiao"]],
                                       hovertemplate="%{customdata[0]} (%{customdata[1]})<br>%{x:.1f}%<extra></extra>",
                                       text=o["taxa_informalidade"].map(lambda v: ui.fmt(v, 1)), textposition="outside"))
                ui.estilizar(fig, f"Taxa de informalidade por UF — {ano_inf}", "Taxa de informalidade (%)", "UF",
                             altura=640, legenda=False)
                st.plotly_chart(fig, key=f"{chave}_inf_bar")
                st.caption("Cores = regiões: azul Norte · laranja Nordeste · verde-água Sudeste · violeta Sul · "
                           "rosa Centro-Oeste.")
            with c2:
                r = est.correlacao_pearson(d["taxa_informalidade"], d["taxa_desocupacao"])
                fig = px.scatter(d, x="taxa_informalidade", y="taxa_desocupacao", color="regiao", text="sigla",
                                 color_discrete_map=ui.COR_REGIAO, hover_name="uf")
                fig.update_traces(marker=dict(size=11, line=dict(width=2, color="white")), textposition="top center")
                ui.estilizar(fig, f"Informalidade × desocupação — {ano_inf} (r = {ui.fmt(r, 2)})",
                             "Taxa de informalidade (%)", "Taxa de desocupação (%)", altura=430)
                st.plotly_chart(fig, key=f"{chave}_disp")
                st.markdown(f"Correlação de Pearson **r = {ui.fmt(r, 2)}** ({_forca(r)}). Correlação não é causalidade: os dois indicadores "
                            "refletem a estrutura produtiva de cada estado (peso da agropecuária, serviços de baixa "
                            "produtividade e menor presença da indústria formal).")
            st.markdown(f"#### Estatística da informalidade entre as UFs — {ano_inf}")
            ui.bloco_estatistico(d, "taxa_informalidade", "sigla", f"Informalidade — {ano_inf}", "%", 1, "UF",
                                 eixo="Taxa de informalidade (%)", chave=f"{chave}_inf")
        ui.fonte("IBGE, PNAD Contínua — Retrospectiva 2012-2024. Taxa de informalidade (proxy) disponível desde 2016.")

    # ------------------------------------------------------------------ Aba 4
    with abas[3]:
        at = ativ[ativ["tipo"] == "Atividade"]
        anos_at = sorted(at["ano"].dropna().unique().astype(int).tolist())
        a0, a1 = (2012, 2022) if {2012, 2022} <= set(anos_at) else (anos_at[0], anos_at[-1])
        x = at[at["ano"].isin([a0, a1])].pivot_table(index="categoria", columns="ano", values="mil_pessoas")
        x["var_pct"] = (x[a1] / x[a0] - 1) * 100
        x = x.sort_values("var_pct")
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Bar(
                x=x["var_pct"], y=x.index, orientation="h",
                marker_color=[ui.LARANJA if v < 0 else ui.AZUL for v in x["var_pct"]],
                text=[f"{ui.fmt(v, 1)}%" for v in x["var_pct"]], textposition="outside",
                customdata=x[[a0, a1]].values,
                hovertemplate="%{y}<br>" + f"{a0}: " + "%{customdata[0]:,.0f} mil<br>" + f"{a1}: "
                              + "%{customdata[1]:,.0f} mil<extra></extra>"))
            ui.estilizar(fig, f"Variação dos ocupados por atividade, {a0}→{a1} (%)", "Variação (%)", None,
                         altura=470, legenda=False)
            fig.update_traces(cliponaxis=False)
            fig.update_xaxes(range=[min(x["var_pct"].min() * 1.45, -5), x["var_pct"].max() * 1.3])
            st.plotly_chart(fig, key=f"{chave}_ativ")
        with c2:
            pos = indic_br[indic_br["indicador"].isin(["Empregado no setor privado com carteira",
                                                       "Empregado no setor privado sem carteira",
                                                       "Trabalhador por conta própria"])].dropna()
            fig = px.line(pos, x="ano", y="valor", color="indicador", markers=True,
                          color_discrete_sequence=[ui.AZUL, ui.LARANJA, ui.VERDE_AGUA])
            fig.update_traces(line_width=2, marker_size=7)
            ui.estilizar(fig, "Carteira assinada × sem carteira × conta própria (Brasil)", "Ano", "Mil pessoas",
                         altura=470)
            st.plotly_chart(fig, key=f"{chave}_posicao")

        cnpj = ativ[ativ["categoria"].isin(["Conta própria com CNPJ", "Conta própria sem CNPJ"])].dropna()
        if not cnpj.empty:
            c3, c4 = st.columns([1.3, 1])
            with c3:
                fig = px.bar(cnpj, x="ano", y="mil_pessoas", color="categoria", barmode="stack",
                             color_discrete_map={"Conta própria com CNPJ": ui.VERDE_AGUA,
                                                 "Conta própria sem CNPJ": ui.CINZA})
                fig.update_traces(marker_line_color="white", marker_line_width=2)
                ui.estilizar(fig, "Trabalhadores por conta própria com e sem CNPJ (Brasil)", "Ano", "Mil pessoas",
                             altura=400)
                st.plotly_chart(fig, key=f"{chave}_cnpj")
            with c4:
                p = cnpj.pivot_table(index="ano", columns="categoria", values="mil_pessoas")
                p["% com CNPJ"] = p["Conta própria com CNPJ"] / p.sum(axis=1) * 100
                st.metric("Conta própria com CNPJ (2016 → 2022)",
                          f"{ui.fmt(p['Conta própria com CNPJ'].iloc[0] / 1000, 1)} → "
                          f"{ui.fmt(p['Conta própria com CNPJ'].iloc[-1] / 1000, 1)} mi")
                st.metric("Parcela formalizada do conta própria",
                          f"{ui.fmt(p['% com CNPJ'].iloc[0], 1)}% → {ui.fmt(p['% com CNPJ'].iloc[-1], 1)}%")
                st.caption("Ainda assim, cerca de 3 em cada 4 trabalhadores por conta própria não têm CNPJ — "
                           "público prioritário do Sebrae.")
        ui.fonte("IBGE, PNAD Contínua — Retrospectivas 2012-2022 e 2012-2024 (Brasil, médias anuais).")

    # ------------------------------------------------------------------ Aba 5
    with abas[4]:
        d = genero[genero["indicador"] == "Taxa de desocupação"]
        c1, c2 = st.columns(2)
        with c1:
            cores = [ui.AZUL if "Homens" in g else ui.LARANJA for g in d["grupo"]]
            fig = go.Figure(go.Bar(x=d["grupo"].str.replace(" ", "<br>", n=1), y=d["valor"], marker_color=cores,
                                   text=d["valor"].map(lambda v: ui.fmt(v, 1) + "%"), textposition="outside"))
            ui.estilizar(fig, "Taxa de desocupação por sexo e cor ou raça — 2022", "Grupo", "Taxa de desocupação (%)",
                         altura=420, legenda=False)
            st.plotly_chart(fig, key=f"{chave}_gen1")
        with c2:
            outros = genero[genero["indicador"].isin(["Taxa de informalidade", "Taxa de participação na força de trabalho",
                                                      "Trabalho em tempo parcial"])]
            fig = px.bar(outros, x="indicador", y="valor", color="grupo", barmode="group",
                         color_discrete_map=ui.COR_SEXO, text=outros["valor"].map(lambda v: ui.fmt(v, 1)))
            ui.estilizar(fig, "Outros indicadores por sexo — 2022", "Indicador", "%", altura=420)
            st.plotly_chart(fig, key=f"{chave}_gen2")
        st.markdown("A desocupação da **mulher preta ou parda (14,0%)** é mais que o dobro da do **homem branco (6,3%)**. "
                    "Políticas de emprego que olham apenas a média nacional (9,6%) escondem essa desigualdade.")
        ui.fonte("IBGE, Estatísticas de Gênero: indicadores sociais das mulheres no Brasil, 3ª ed. (2024), dados da "
                 "PNAD Contínua 2022.")

    # ------------------------------------------------------------------ Aba 6
    with abas[5]:
        _respostas(base, taxas_br, ativ, indic_br, genero)

    # ------------------------------------------------------------------ Aba 7
    with abas[6]:
        st.subheader("Notícias e contexto")
        ui.bloco_noticias(NOTICIAS, IMAGENS, chave)


def _forca(r: float) -> str:
    sinal = "positiva" if r > 0 else "negativa"
    nivel = "forte" if abs(r) >= 0.7 else "moderada" if abs(r) >= 0.4 else "fraca"
    return f"{sinal} e {nivel}"


def _respostas(base, taxas_br, ativ, indic_br, genero):
    """Respostas às perguntas de negócio, calculadas com TODAS as 27 UFs (2012 × 2022)."""
    st.caption("As respostas usam as 27 UFs e os anos 2012 e 2022 (foco do Tema 6), independentemente dos filtros.")
    a = base[base["ano"] == 2012].set_index("sigla")["taxa_desocupacao"]
    b = base[base["ano"] == 2022].set_index("sigla")["taxa_desocupacao"]
    if a.empty or b.empty:
        st.info("A base em uso não contém 2012 e 2022.")
        return
    var = (b - a).dropna().sort_values()
    r12, r22 = est.resumo(a.tolist(), a.index.tolist()), est.resumo(b.tolist(), b.index.tolist())
    br = taxas_br.set_index("ano")["taxa_desocupacao"]
    piores = ", ".join(f"{s} (+{ui.fmt(v, 1)} p.p.)" for s, v in var.tail(3)[::-1].items())
    melhores = ", ".join(f"{s} ({ui.fmt(v, 1)} p.p.)" for s, v in var.head(3).items())
    nreg = base[base["ano"].isin([2012, 2022])].pivot_table(index="regiao", columns="ano", values="taxa_desocupacao",
                                                            aggfunc="median")
    reg_txt = "; ".join(f"{r}: {ui.fmt(nreg.loc[r, 2012], 1)}% → {ui.fmt(nreg.loc[r, 2022], 1)}%" for r in nreg.index)

    ui.resposta("1) Ministério do Trabalho — onde o desemprego mais piorou entre 2012 e 2022?",
                f"A taxa do Brasil passou de {ui.fmt(br.get(2012), 1)}% para {ui.fmt(br.get(2022), 1)}% "
                f"(+{ui.fmt(br.get(2022) - br.get(2012), 1)} p.p.). <b>{int((var > 0).sum())} das 27 UFs pioraram</b>. "
                f"Maiores altas: {piores}. Melhoras: {melhores}. Medianas por região — {reg_txt}. "
                "<br><b>Recomendação:</b> priorizar programas de qualificação e intermediação (SINE) no Nordeste e no "
                "Rio de Janeiro, onde o aumento foi maior.")
    imp = est.impacto_outliers(b.tolist(), b.index.tolist())
    out_txt = ("sem outliers pela regra de 1,5×IQR" if not r22["outliers"] else
               "outlier(s): " + ", ".join(f"{n} ({ui.fmt(v, 1)}%)" for n, v, _ in r22["outliers"]))
    ui.resposta("2) O desemprego ficou mais desigual entre os estados?",
                f"Sim. O desvio padrão entre as UFs subiu de {ui.fmt(r12['desvio_pop'], 2)} para "
                f"{ui.fmt(r22['desvio_pop'], 2)} p.p.; o IQR, de {ui.fmt(r12['iqr'], 1)} para {ui.fmt(r22['iqr'], 1)} p.p.; "
                f"a amplitude, de {ui.fmt(r12['amplitude'], 1)} para {ui.fmt(r22['amplitude'], 1)} p.p. "
                f"Em 2022 a média das UFs foi {ui.fmt(r22['media'], 2)}% e a mediana {ui.fmt(r22['mediana'], 1)}% "
                f"({out_txt}" + (f"; média sem extremos: {ui.fmt(imp['media_sem'], 2)}%" if r22["outliers"] else
                                  " — média e mediana praticamente iguais") + "). "
                "<br><b>Leitura para a gestão:</b> uma meta nacional única não serve — os estados se afastaram uns dos "
                "outros; metas regionais são mais justas.")
    inf = base[base["ano"] == 2022].dropna(subset=["taxa_informalidade"])
    if not inf.empty:
        r = est.correlacao_pearson(inf["taxa_informalidade"], inf["taxa_desocupacao"])
        top = inf.nlargest(5, "taxa_informalidade")
        top_txt = ", ".join(f"{s} ({ui.fmt(v, 1)}%)" for s, v in zip(top["sigla"], top["taxa_informalidade"]))
        ri = est.resumo(inf["taxa_informalidade"].tolist(), inf["sigla"].tolist())
        ui.resposta("3) Sebrae — onde está a informalidade e ela anda junto com o desemprego?",
                    f"Em 2022 a informalidade do Brasil foi de 39,4%, mas entre as UFs vai de "
                    f"{ui.fmt(ri['minimo'], 1)}% a {ui.fmt(ri['maximo'], 1)}% (amplitude {ui.fmt(ri['amplitude'], 1)} p.p., "
                    f"mediana {ui.fmt(ri['mediana'], 1)}%). Maiores taxas: {top_txt} — todas no Norte/Nordeste. "
                    f"A correlação com a desocupação é r = {ui.fmt(r, 2)} ({_forca(r)}): "
                    f"{'estados mais informais tendem a ter mais desemprego' if r > 0 else 'não há relação direta'}. "
                    "<br><b>Recomendação:</b> concentrar ações de formalização (MEI, crédito orientado, compras "
                    f"públicas) em {', '.join(top['sigla'])}.")
    at = ativ[(ativ["tipo"] == "Atividade") & (ativ["categoria"] == "Indústria geral")].set_index("ano")["mil_pessoas"]
    cp = ativ[ativ["categoria"] == "Conta própria com CNPJ"].dropna().set_index("ano")["mil_pessoas"]
    sc = ativ[ativ["categoria"] == "Conta própria sem CNPJ"].dropna().set_index("ano")["mil_pessoas"]
    if not at.empty and 2012 in at.index and 2022 in at.index and not cp.empty:
        ui.resposta("4) Indústria e Sebrae — o que aconteceu com a indústria e com o conta própria?",
                    f"A indústria geral ocupava {ui.fmt(at[2012] / 1000, 1)} mi em 2012 e {ui.fmt(at[2022] / 1000, 1)} mi "
                    f"em 2022 ({ui.fmt((at[2022] / at[2012] - 1) * 100, 1)}%), ainda abaixo do patamar de 2012, enquanto "
                    f"o total de ocupados cresceu. Já o conta própria com CNPJ saltou de {ui.fmt(cp.iloc[0] / 1000, 1)} mi "
                    f"(2016) para {ui.fmt(cp.iloc[-1] / 1000, 1)} mi (2022), +{ui.fmt((cp.iloc[-1] / cp.iloc[0] - 1) * 100, 1)}%, "
                    f"mas {ui.fmt(sc.iloc[-1] / 1000, 1)} mi continuam sem CNPJ. <br><b>Leitura:</b> há mão de obra "
                    "disponível nos estados de maior desocupação; a indústria pode combinar qualificação (SENAI) com "
                    "o Ministério, e o Sebrae tem um público de ~19 milhões de potenciais formalizações.")
    g = genero.set_index("grupo")
    if "Mulheres pretas ou pardas" in g.index:
        dg = genero[genero["indicador"] == "Taxa de desocupação"].set_index("grupo")["valor"]
        ui.resposta("5) Quem são os mais afetados?",
                    f"Em 2022, a desocupação das mulheres ({ui.fmt(dg['Mulheres'], 1)}%) superou a dos homens "
                    f"({ui.fmt(dg['Homens'], 1)}%); entre mulheres pretas ou pardas chegou a {ui.fmt(dg['Mulheres pretas ou pardas'], 1)}%, "
                    f"contra {ui.fmt(dg['Homens brancos'], 1)}% entre homens brancos "
                    f"({ui.fmt(dg['Mulheres pretas ou pardas'] / dg['Homens brancos'], 1)} vezes). <br><b>Recomendação:</b> "
                    "programas de emprego com recorte de gênero e raça, e oferta de creches para ampliar a participação "
                    "feminina (53,3% contra 73,2% dos homens).")
