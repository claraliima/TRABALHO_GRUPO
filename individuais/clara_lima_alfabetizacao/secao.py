"""
Seção individual — Indicador 2: Alfabetização por sexo e raça.
Responsável: Clara Lima.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import estatistica as est
from core import ui
from core.carregamento import REGIOES, UFS, Esquema
from individuais.clara_lima_alfabetizacao.etl_alfabetizacao import carregar

AUTOR = "Clara Lima"
RACAS = ["Branca", "Preta", "Amarela", "Parda", "Indígena"]
CORES_RACA = {"Branca": ui.AZUL, "Parda": ui.LARANJA, "Preta": ui.VIOLETA, "Amarela": ui.AMARELO,
              "Indígena": ui.VERDE_AGUA, "Total": ui.CINZA}
FAIXAS = ["15 a 19 anos", "20 a 24 anos", "25 a 34 anos", "35 a 44 anos", "45 a 54 anos", "55 a 64 anos",
          "65 anos ou mais"]

ESQ_UF = Esquema("alfabetizacao_uf", ["uf", "analfabetismo_total"],
                 ["analfabetismo_total", "alfabetizacao_total", "analfabetismo_quilombolas", "alfabetizacao_quilombolas",
                  "ano"],
                 {"uf": ["unidade da federação", "estado", "sigla"],
                  "analfabetismo_total": ["taxa de analfabetismo", "analfabetismo", "taxa_de_analfabetismo_total", "valor"],
                  "analfabetismo_quilombolas": ["taxa de analfabetismo - pessoas quilombolas", "quilombolas"]},
                 usa_uf=True)
ESQ_REC = Esquema("alfabetizacao_recortes", ["recorte", "grupo", "subgrupo", "ano", "taxa_alfabetizacao"],
                  ["ano", "taxa_alfabetizacao", "taxa_analfabetismo"], {"taxa_alfabetizacao": ["valor", "taxa"]})

NOTICIAS = [
    {"titulo": "Censo 2022: taxa de analfabetismo cai de 9,6% para 7,0% em 12 anos, mas desigualdades persistem",
     "fonte": "Agência IBGE Notícias", "data": "mai/2024",
     "resumo": "Analfabetismo é maior entre idosos, pretos, pardos e indígenas e no Nordeste.",
     "url": "https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-denoticias/40098-censo-2022-taxa-de-analfabetismo-cai-de-9-6-para-7-0-em-12-anos-mas-desifualdades-persistem"},
    {"titulo": "Censo 2022: taxa de analfabetismo no Nordeste é o dobro da média do Brasil; veja ranking",
     "fonte": "Exame", "data": "mai/2024",
     "resumo": "Ranking das 27 UFs: Santa Catarina lidera; Alagoas e Piauí têm as menores taxas.",
     "url": "https://exame.com/brasil/censo-2022-taxa-de-analfabetismo-no-nordeste-e-o-dobro-da-media-do-brasil-veja-ranking/"},
    {"titulo": "A situação do analfabetismo no Brasil em 6 gráficos",
     "fonte": "Nexo Jornal", "data": "mai/2024",
     "resumo": "Gráficos que explicam o analfabetismo no Brasil a partir dos resultados do Censo 2022.",
     "url": "https://www.nexojornal.com.br/grafico/2024/05/17/analfabetismo-no-brasil-grafico"},
    {"titulo": "11,4 milhões de brasileiros ainda não sabem ler e escrever um bilhete simples",
     "fonte": "Poder360", "data": "mai/2024",
     "resumo": "Panorama dos resultados de alfabetização do Censo 2022.",
     "url": "https://www.poder360.com.br/brasil/114-milhoes-de-brasileiros-nao-sabem-ler-e-escrever-bilhete-simples/"},
    {"titulo": "O que o Censo 2022 tem a dizer sobre alfabetização?",
     "fonte": "IBGE Educa", "data": "2024",
     "resumo": "Material didático do IBGE explicando o conceito e os principais resultados.",
     "url": "https://educa.ibge.gov.br/professores/educa-noticias/22316-o-que-o-censo-2022-tem-a-dizer-sobre-alfabetizacao.html"},
    {"titulo": "Censo 2022 — Alfabetização: resultados do universo (publicação oficial)",
     "fonte": "IBGE", "data": "mai/2024",
     "resumo": "Publicação com taxas por idade, cor ou raça, regiões e tamanho de município.",
     "url": "https://biblioteca.ibge.gov.br/visualizacao/periodicos/3108/cd_2022_alfabetizacao.pdf"},
]
IMAGENS = [("alfabetizacao_livro.png", "93% da população de 15+ é alfabetizada"),
           ("alfabetizacao_desigualdade.png", "A desigualdade racial do analfabetismo")]


def render(chave: str = "clara"):
    tabelas = carregar()
    bases = ui.painel_upload(chave, {
        "Taxas por UF (2022)": (ESQ_UF, tabelas["alfabetizacao_uf"]),
        "Recortes nacionais (sexo, cor, idade, região)": (ESQ_REC, tabelas["alfabetizacao_recortes"]),
    })
    uf = bases["Taxas por UF (2022)"].copy()
    rec = bases["Recortes nacionais (sexo, cor, idade, região)"].copy()
    if "alfabetizacao_total" not in uf.columns or uf["alfabetizacao_total"].isna().all():
        uf["alfabetizacao_total"] = 100 - uf["analfabetismo_total"]
    for c in ["analfabetismo_quilombolas", "alfabetizacao_quilombolas"]:
        if c not in uf.columns:
            uf[c] = float("nan")
    uf["alfabetizacao_quilombolas"] = uf["alfabetizacao_quilombolas"].fillna(100 - uf["analfabetismo_quilombolas"])
    if "taxa_analfabetismo" not in rec.columns or rec["taxa_analfabetismo"].isna().all():
        rec["taxa_analfabetismo"] = 100 - rec["taxa_alfabetizacao"]

    # ------------------------------------------------------------------ Filtros
    sb = st.sidebar
    sb.subheader("Filtros — Alfabetização")
    medida = sb.radio("Medida", ["Taxa de analfabetismo", "Taxa de alfabetização"], key=f"{chave}_medida")
    col_rec = "taxa_analfabetismo" if "anal" in medida else "taxa_alfabetizacao"
    pop = sb.radio("População (análise por UF)", ["Total", "Pessoas quilombolas"], key=f"{chave}_pop")
    sufixo = "total" if pop == "Total" else "quilombolas"
    col_uf = ("analfabetismo_" if "anal" in medida else "alfabetizacao_") + sufixo
    regioes = sb.multiselect("Regiões", REGIOES, default=REGIOES, key=f"{chave}_reg")
    ufs_disp = UFS[UFS["regiao"].isin(regioes)]["sigla"].tolist()
    ufs = sb.multiselect("UFs", ufs_disp, default=ufs_disp, key=f"{chave}_ufs_{'-'.join(regioes)}")
    racas = sb.multiselect("Cor ou raça", RACAS, default=RACAS, key=f"{chave}_raca")
    faixas = sb.multiselect("Faixas etárias", FAIXAS, default=FAIXAS, key=f"{chave}_faixas")
    anos = sorted(rec[rec["recorte"] == "Cor ou raça"]["ano"].unique().tolist()) or [2022]
    ano = sb.select_slider("Ano (recortes por cor e região)", anos, value=anos[-1], key=f"{chave}_ano")

    fuf = uf[uf["sigla"].isin(ufs)]
    ui.botao_download_bases({"uf_filtrado": fuf, "recortes": rec}, "alfabetizacao_filtrada", chave)

    ui.cabecalho_secao("Alfabetização por sexo e raça", "Indicador 2 · Censo Demográfico 2022 (IBGE) · pessoas de 15 anos ou mais",
                       AUTOR, ["Indicador 2", "Censo 2022", "Educação"])
    ui.caixa_persona(
        "Por que isso importa para o Ministério do Trabalho, o Sebrae e a Indústria?",
        "Quem não sabe ler e escrever fica de fora do emprego formal, de cursos técnicos e até da abertura de um MEI. "
        "A alfabetização é o primeiro degrau da qualificação profissional. Perguntas: <b>(a)</b> Quais estados têm "
        "as maiores taxas de analfabetismo e quão desiguais são as UFs? <b>(b)</b> Qual a diferença entre homens e "
        "mulheres? <b>(c)</b> E entre os grupos de cor ou raça — em todas as idades? <b>(d)</b> Onde concentrar "
        "programas de alfabetização de adultos ligados à qualificação para o trabalho?")

    abas = st.tabs(["🗺️ UFs", "📐 Estatística e outliers", "⚖️ Sexo e cor ou raça", "📈 Idade e evolução",
                    "💡 Respostas", "📰 Notícias"])

    # ------------------------------------------------------------------ Aba 1
    with abas[0]:
        d = fuf.dropna(subset=[col_uf])
        c = st.columns(5)
        c[0].metric("Brasil — alfabetização", "93,0%", help="Censo 2022, pessoas de 15 anos ou mais")
        c[1].metric("Analfabetos (15+)", "11,4 mi", delta="−2,6 p.p. vs 2010", delta_color="inverse")
        if not d.empty:
            pior = d.loc[d["analfabetismo_" + sufixo].idxmax()]
            melhor = d.loc[d["analfabetismo_" + sufixo].idxmin()]
            c[2].metric("Maior analfabetismo", f"{pior['sigla']} · {ui.fmt(pior['analfabetismo_' + sufixo], 1, '%')}")
            c[3].metric("Menor analfabetismo", f"{melhor['sigla']} · {ui.fmt(melhor['analfabetismo_' + sufixo], 1, '%')}")
            c[4].metric("Razão maior ÷ menor",
                        ui.fmt(pior["analfabetismo_" + sufixo] / melhor["analfabetismo_" + sufixo], 1, "×"))
        c1, c2 = st.columns([1.3, 1])
        with c1:
            o = fuf.sort_values("analfabetismo_total", ascending=False)
            fig = go.Figure()
            fig.add_bar(x=o["sigla"], y=o["analfabetismo_total"], name="Total da população", marker_color=ui.AZUL,
                        customdata=o["uf"], hovertemplate="%{customdata}<br>Total: %{y:.2f}%<extra></extra>")
            fig.add_bar(x=o["sigla"], y=o["analfabetismo_quilombolas"], name="Pessoas quilombolas",
                        marker_color=ui.LARANJA, customdata=o["uf"],
                        hovertemplate="%{customdata}<br>Quilombolas: %{y:.2f}%<extra></extra>")
            fig.add_hline(y=7.0, line=dict(color=ui.CINZA, dash="dot"), annotation_text="Brasil 7,0%")
            ui.estilizar(fig, "Taxa de analfabetismo (15+) por UF — total × quilombolas, 2022", "UF",
                         "Taxa de analfabetismo (%)", altura=440)
            fig.update_layout(barmode="group")
            st.plotly_chart(fig, key=f"{chave}_barras")
            st.caption("AC e RR não têm taxa calculada para quilombolas.")
        with c2:
            escala = ["#fde3d6", "#f6b89c", "#eb6834", "#b5461b", "#7a2b0c"] if "anal" in medida else ui.SEQ_AZUL
            mapa = ui.mapa_ufs(d, col_uf, f"Mapa — {medida} ({pop.lower()})", f"{medida} (%)", escala=escala, casas=2,
                               altura=440)
            st.plotly_chart(mapa, key=f"{chave}_mapa")
        ui.fonte("IBGE, Censo Demográfico 2022 — Alfabetização (SIDRA 9793; ranking de UFs).")

    # ------------------------------------------------------------------ Aba 2
    with abas[1]:
        st.subheader(f"{medida} — {pop.lower()}: medidas entre as UFs selecionadas")
        ui.bloco_estatistico(fuf, col_uf, "sigla", f"{medida} ({pop.lower()})", "%", 2, "UF",
                             eixo=f"{medida} (%)", chave=f"{chave}_est")
        st.plotly_chart(ui.boxplot(fuf.dropna(subset=[col_uf]).sort_values("regiao"), col_uf, "sigla",
                                   f"{medida} por região ({pop.lower()})", f"{medida} (%)", grupo="regiao",
                                   cores=ui.COR_REGIAO, casas=2), key=f"{chave}_box_reg")
        t = ui.tabela_outliers_por_grupo(fuf, col_uf, "sigla", "regiao", 2)
        if not t.empty:
            st.markdown("**Outliers dentro de cada região (1,5×IQR)**")
            st.dataframe(t, hide_index=True)
            if t["Outliers"].str.contains("DF").any() and pop == "Total":
                st.caption("No Centro-Oeste, o Distrito Federal destoa dos vizinhos (analfabetismo de 2,8% contra "
                           "5,4–5,8% "
                           "em GO, MS e MT): é uma unidade quase toda urbana, com renda e escolaridade muito acima da "
                           "região. Por isso a média do Centro-Oeste se afasta da mediana, e a mediana representa melhor "
                           "a região.")

        st.markdown("#### Recortes cor ou raça × idade (2022): onde estão os valores extremos?")
        ci = rec[(rec["recorte"] == "Cor ou raça x idade") & rec["grupo"].isin(racas) & rec["subgrupo"].isin(faixas)].copy()
        ci["rotulo"] = ci["grupo"] + " · " + ci["subgrupo"]
        if len(ci) >= 3:
            ui.bloco_estatistico(ci, col_rec, "rotulo", f"{medida} por cor ou raça e idade", "%", 1, "grupo",
                                 eixo=f"{medida} (%)", chave=f"{chave}_est_ci")

    # ------------------------------------------------------------------ Aba 3
    with abas[2]:
        c1, c2 = st.columns(2)
        with c1:
            sx = rec[rec["recorte"].isin(["Sexo", "Sexo x grupo étnico"])].copy()
            sx["recorte_txt"] = sx["subgrupo"].replace({"Total": "Total 15+", "65 anos ou mais": "Idosos 65+",
                                                         "Pessoas indígenas": "Indígenas",
                                                         "Indígenas em Terras Indígenas": "Indígenas em TI",
                                                         "Pessoas quilombolas": "Quilombolas"})
            fig = px.bar(sx, x="recorte_txt", y=col_rec, color="grupo", barmode="group", color_discrete_map=ui.COR_SEXO,
                         text=sx[col_rec].map(lambda v: ui.fmt(v, 1)))
            ui.estilizar(fig, f"{medida} por sexo — 2022", "Grupo populacional", f"{medida} (%)", altura=430)
            if "anal" not in medida:
                fig.update_yaxes(range=[70, 100])
            st.plotly_chart(fig, key=f"{chave}_sexo")
            st.caption("Na população total, as mulheres são um pouco mais alfabetizadas; entre indígenas (sobretudo em "
                       "Terras Indígenas) a vantagem se inverte e as mulheres ficam para trás.")
        with c2:
            cr = rec[(rec["recorte"] == "Cor ou raça") & (rec["grupo"].isin(racas + ["Total"]))].copy()
            cr["ano"] = cr["ano"].astype(str)
            fig = px.bar(cr, x="grupo", y=col_rec, color="ano", barmode="group",
                         color_discrete_sequence=[ui.AZUL, ui.LARANJA], text=cr[col_rec].map(lambda v: ui.fmt(v, 1)))
            ui.estilizar(fig, f"{medida} por cor ou raça — 2010 × 2022", "Cor ou raça", f"{medida} (%)", altura=430)
            st.plotly_chart(fig, key=f"{chave}_cor")
        ci = rec[(rec["recorte"] == "Cor ou raça x idade") & rec["grupo"].isin(racas) & rec["subgrupo"].isin(faixas)]
        fig = px.line(ci, x="subgrupo", y=col_rec, color="grupo", markers=True, color_discrete_map=CORES_RACA,
                      category_orders={"subgrupo": FAIXAS})
        fig.update_traces(line_width=2, marker_size=8)
        ui.estilizar(fig, f"{medida} por idade, segundo a cor ou raça — 2022", "Grupo de idade", f"{medida} (%)", altura=430)
        st.plotly_chart(fig, key=f"{chave}_cor_idade")
        ui.fonte("IBGE, Censo 2022 — Alfabetização; Indígenas e Quilombolas: alfabetização (resultados do universo).")

    # ------------------------------------------------------------------ Aba 4
    with abas[3]:
        c1, c2 = st.columns(2)
        with c1:
            ida = rec[rec["recorte"] == "Idade"].copy()
            ida["ano"] = ida["ano"].astype(str)
            fig = px.line(ida, x="subgrupo", y=col_rec, color="ano", markers=True,
                          color_discrete_sequence=[ui.CINZA, ui.AZUL, ui.LARANJA])
            fig.update_traces(line_width=2, marker_size=7)
            ui.estilizar(fig, f"{medida} por idade — 2000, 2010 e 2022", "Grupo de idade", f"{medida} (%)", altura=420)
            st.plotly_chart(fig, key=f"{chave}_idade_ano")
        with c2:
            ri = rec[(rec["recorte"] == "Região x idade") & rec["grupo"].isin(regioes) & rec["subgrupo"].isin(faixas)]
            fig = px.line(ri, x="subgrupo", y=col_rec, color="grupo", markers=True, color_discrete_map=ui.COR_REGIAO,
                          category_orders={"subgrupo": FAIXAS})
            fig.update_traces(line_width=2, marker_size=7)
            ui.estilizar(fig, f"{medida} por idade e região — 2022", "Grupo de idade", f"{medida} (%)", altura=420)
            st.plotly_chart(fig, key=f"{chave}_reg_idade")
        c3, c4 = st.columns(2)
        with c3:
            h = rec[rec["recorte"] == "Histórico"]
            fig = go.Figure(go.Scatter(x=h["ano"], y=h[col_rec], mode="lines+markers+text", line=dict(color=ui.AZUL, width=2),
                                       marker=dict(size=8), text=h[col_rec].map(lambda v: ui.fmt(v, 1)),
                                       textposition="top center"))
            ui.estilizar(fig, f"{medida} no Brasil — Censos 1940 a 2022", "Ano do Censo", f"{medida} (%)", altura=380,
                         legenda=False)
            st.plotly_chart(fig, key=f"{chave}_hist")
        with c4:
            tm = rec[rec["recorte"] == "Tamanho do município"]
            fig = go.Figure(go.Bar(x=tm["grupo"], y=tm[col_rec], marker_color=ui.VERDE_AGUA,
                                   text=tm[col_rec].map(lambda v: ui.fmt(v, 1)), textposition="outside"))
            ui.estilizar(fig, f"{medida} por tamanho do município — 2022", "Tamanho do município", f"{medida} (%)",
                         altura=380, legenda=False)
            st.plotly_chart(fig, key=f"{chave}_mun")
        rg = rec[(rec["recorte"] == "Região") & (rec["ano"] == ano)]
        st.dataframe(rg[["grupo", "ano", "taxa_alfabetizacao", "taxa_analfabetismo"]].rename(columns={
            "grupo": "Região", "ano": "Ano", "taxa_alfabetizacao": "Alfabetização (%)",
            "taxa_analfabetismo": "Analfabetismo (%)"}), hide_index=True)

    with abas[4]:
        _respostas(uf, rec)

    with abas[5]:
        st.subheader("Notícias e contexto")
        ui.bloco_noticias(NOTICIAS, IMAGENS, chave)


def _respostas(uf, rec):
    st.caption("Respostas calculadas com as 27 UFs e os recortes nacionais do Censo 2022.")
    r = est.resumo(uf["analfabetismo_total"].tolist(), uf["sigla"].tolist())
    top = uf.nlargest(5, "analfabetismo_total")
    top_txt = ", ".join(f"{s} ({ui.fmt(v, 1)}%)" for s, v in zip(top["sigla"], top["analfabetismo_total"]))
    ne = uf[uf["regiao"] == "Nordeste"]["analfabetismo_total"].median()
    sul = uf[uf["regiao"] == "Sul"]["analfabetismo_total"].median()
    ui.resposta("(a) Quais estados têm mais analfabetismo e quão desiguais são as UFs?",
                f"Maiores taxas: {top_txt} — todos do Nordeste. Entre as 27 UFs: média {ui.fmt(r['media'], 2)}%, mediana "
                f"{ui.fmt(r['mediana'], 2)}%, desvio padrão {ui.fmt(r['desvio_pop'], 2)} p.p., IQR {ui.fmt(r['iqr'], 2)} p.p., "
                f"amplitude {ui.fmt(r['amplitude'], 2)} p.p. A média está acima da mediana (assimetria à direita): o bloco "
                f"nordestino forma uma 'segunda corcova' de valores altos. A mediana do Nordeste ({ui.fmt(ne, 1)}%) é "
                f"{ui.fmt(ne / sul, 1)} vezes a do Sul ({ui.fmt(sul, 1)}%). Não há outlier entre as 27 UFs porque os "
                "valores altos são muitos (9 estados) e não um caso isolado.")
    sx = rec[rec["recorte"].isin(["Sexo", "Sexo x grupo étnico"])].set_index(["grupo", "subgrupo"])["taxa_alfabetizacao"]
    ui.resposta("(b) Há diferença entre homens e mulheres?",
                f"Na população total as mulheres são levemente mais alfabetizadas ({ui.fmt(sx[('Mulheres', 'Total')], 2)}% "
                f"× {ui.fmt(sx[('Homens', 'Total')], 2)}%), e entre quilombolas a vantagem feminina é maior "
                f"({ui.fmt(sx[('Mulheres', 'Pessoas quilombolas')], 1)}% × {ui.fmt(sx[('Homens', 'Pessoas quilombolas')], 1)}%). "
                f"Mas entre indígenas em Terras Indígenas a situação se inverte: mulheres "
                f"{ui.fmt(sx[('Mulheres', 'Indígenas em Terras Indígenas')], 1)}% × homens "
                f"{ui.fmt(sx[('Homens', 'Indígenas em Terras Indígenas')], 1)}% — gap de "
                f"{ui.fmt(sx[('Homens', 'Indígenas em Terras Indígenas')] - sx[('Mulheres', 'Indígenas em Terras Indígenas')], 1)} p.p.")
    cr = rec[(rec["recorte"] == "Cor ou raça") & (rec["ano"] == 2022)].set_index("grupo")["taxa_analfabetismo"]
    ci = rec[(rec["recorte"] == "Cor ou raça x idade")]
    ri = est.resumo(ci["taxa_analfabetismo"].tolist(), (ci["grupo"] + " " + ci["subgrupo"]).tolist())
    outs = ", ".join(f"{n} ({ui.fmt(v, 1)}%)" for n, v, _ in ri["outliers"]) or "nenhum"
    ui.resposta("(c) E entre os grupos de cor ou raça?",
                f"Analfabetismo em 2022: branca {ui.fmt(cr['Branca'], 1)}%, parda {ui.fmt(cr['Parda'], 1)}%, preta "
                f"{ui.fmt(cr['Preta'], 1)}% e indígena {ui.fmt(cr['Indígena'], 1)}% ({ui.fmt(cr['Indígena'] / cr['Branca'], 1)}× "
                f"a taxa dos brancos). A desigualdade cresce com a idade: nos 35 recortes cor × idade, os outliers "
                f"(1,5×IQR) são {outs}. A média desses recortes ({ui.fmt(ri['media'], 1)}%) é puxada por esses extremos, "
                f"enquanto a mediana ({ui.fmt(ri['mediana'], 1)}%) mostra que a maioria dos recortes jovens já tem taxas "
                "baixas — o analfabetismo é, sobretudo, uma herança das gerações mais velhas e não brancas.")
    ui.resposta("(d) Onde concentrar programas de alfabetização ligados ao trabalho?",
                "1) <b>Nordeste</b> (AL, PI, PB, MA, CE), público de 45 anos ou mais; 2) populações <b>indígenas e "
                "quilombolas</b>, com atenção às mulheres indígenas; 3) <b>municípios pequenos</b> (até 20 mil hab., "
                "analfabetismo de 11–14%). <b>Para o Sebrae e o Ministério do Trabalho:</b> unir alfabetização de adultos "
                "(EJA) a cursos de qualificação e formalização (MEI) aumenta a empregabilidade justamente nos estados "
                "com maior desocupação e informalidade do Tema 6.")
