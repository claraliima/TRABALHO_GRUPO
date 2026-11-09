"""
PAINEL UNIFICADO DO GRUPO — Projeto Integrador "Números que Falam: Descobrindo o Brasil"

Startup: Lupa Dados · Integrantes: Arthur de Souza, Clara Lima e Gustavo Henrique
Tema do grupo: 6 — Trabalho e Emprego (Ministério do Trabalho, Sebrae e Indústria)

Como executar (na raiz do repositório):
    pip install -r requirements.txt
    streamlit run app.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from core import ui  # noqa: E402

st.set_page_config(page_title="Números que Falam · Lupa Dados", page_icon="🔎", layout="wide")
ui.aplicar_estilo()


def pagina_inicio():
    from grupo_trabalho_emprego.etl_trabalho import carregar as c_trab
    from individuais.arthur_souza_populacao.etl_populacao import carregar as c_pop
    from individuais.clara_lima_alfabetizacao.etl_alfabetizacao import carregar as c_alf
    from individuais.gustavo_henrique_mulheres.etl_mulheres import carregar as c_mul

    st.markdown('<span class="nqf-tag">Projeto Integrador · Python & Matemática</span>'
                '<span class="nqf-tag">Etapa 3</span>', unsafe_allow_html=True)
    st.title("🔎 Lupa Dados — Números que Falam: Descobrindo o Brasil")
    st.markdown("Somos a **Lupa Dados**, uma startup de análise de dados contratada pelo **Ministério do Trabalho**, "
                "pelo **Sebrae** e pela **Indústria** para transformar dados públicos do IBGE em decisões. "
                "O painel reúne a análise do grupo (Tema 6 — Trabalho e Emprego) e os indicadores demográficos que cada "
                "integrante construiu individualmente.")

    t = c_trab()["trabalho_brasil_taxas"].set_index("ano")
    pop = c_pop()["pop_idade_sexo"]
    alf = c_alf()["alfabetizacao_recortes"]
    mul = c_mul()["mulheres_regiao_idade"]
    c = st.columns(5)
    c[0].metric("Desocupação 2012 → 2022", f"{ui.fmt(t.loc[2012, 'taxa_desocupacao'], 1)}% → "
                f"{ui.fmt(t.loc[2022, 'taxa_desocupacao'], 1)}%")
    c[1].metric("Informalidade 2022", ui.fmt(t.loc[2022, "taxa_informalidade"], 1, "%"))
    c[2].metric("População 2022 (Censo)", ui.fmt_mi(pop["populacao"].sum(), 1))
    a = alf[(alf["recorte"] == "Região") & (alf["grupo"] == "Brasil") & (alf["ano"] == 2022)]["taxa_alfabetizacao"]
    c[3].metric("Alfabetização (15+)", ui.fmt(a.iloc[0], 1, "%"))
    c[4].metric("Mulheres na população", ui.fmt(mul["mulheres"].sum() / (mul["mulheres"].sum() + mul["homens"].sum()) * 100,
                                                1, "%"))

    st.subheader("Equipe e responsabilidades")
    equipe = pd.DataFrame([
        ["Arthur de Souza, Clara Lima e Gustavo Henrique", "Tema 6 — Trabalho e Emprego (grupo)",
         "Taxa de desocupação 2012 × 2022 e informalidade", "PNAD Contínua"],
        ["Arthur de Souza", "1 — População por grupo de idade, sexo e raça",
         "Distribuição etária, composição por sexo/raça; média, mediana e dispersão das faixas", "Censo 2022"],
        ["Clara Lima", "2 — Alfabetização por sexo e raça",
         "Taxas de alfabetização e desigualdades entre grupos", "Censo 2022"],
        ["Gustavo Henrique", "4 — Mulheres", "Indicadores da população feminina; recortes e comparações territoriais",
         "Censo 2022, Projeções, Estatísticas de Gênero"],
    ], columns=["Responsável", "Indicador", "Foco", "Fonte IBGE"])
    st.dataframe(equipe, hide_index=True)

    st.subheader("Como navegar")
    st.markdown(
        "- Use o **menu da barra lateral** para alternar entre o painel do grupo e os indicadores individuais.\n"
        "- Cada página tem **filtros próprios** na barra lateral (anos, regiões/UFs, sexo, cor ou raça, faixa etária) e "
        "um bloco **📤 Upload de dados** para enviar outra base do IBGE em CSV ou XLSX (há um modelo para baixar).\n"
        "- As abas **📐 Estatística** trazem média, mediana, moda, quartis, IQR, amplitude, variância, desvio padrão, "
        "coeficiente de variação, boxplot e a análise de outliers (regra 1,5×IQR).\n"
        "- As abas **💡 Respostas** respondem às perguntas de negócio das personas; as abas **📰 Notícias** trazem "
        "reportagens e imagens ilustrativas.")
    c1, c2, c3 = st.columns(3)
    for col, (arq, leg) in zip((c1, c2, c3), [("trabalho_informalidade.png", "Tema 6 — Trabalho e Emprego"),
                                              ("populacao_piramide.png", "Estrutura etária"),
                                              ("mulheres_maioria.png", "Mulheres")]):
        col.image(str(ui.IMG / arq), caption=leg, width="stretch")


def pagina_metodologia():
    st.title("ℹ️ Metodologia, fontes e limitações")
    st.subheader("1. Pipeline de dados (ETL)")
    st.markdown(
        "1. **Coleta** — tabelas oficiais do IBGE (PNAD Contínua, Censo 2022, Anuário Estatístico, Estatísticas de "
        "Gênero) salvas em `dados/brutos/` no formato publicado (título, cabeçalho, notas de rodapé, vírgula decimal).\n"
        "2. **Tratamento** — os scripts `etl_*.py` (Pandas) localizam o cabeçalho, removem rodapés, convertem números "
        "(`'9,6'`, `'35 128'`, `'89.695'`), aplicam a convenção de sinais do IBGE (`-` = zero absoluto; `..`, `...` e "
        "`X` = dado ausente), padronizam UFs "
        "(nome ↔ sigla ↔ região), descartam subtotais que causariam contagem dupla e transformam tabelas largas em "
        "formato longo (*tidy*).\n"
        "3. **Conferência** — os ETLs checam totais (ex.: soma das regiões = 203.080.756 habitantes do Censo 2022).\n"
        "4. **Saída** — bases limpas em `dados/tratados/` (CSV + XLSX), lidas pelos dashboards.\n"
        "5. **Upload** — o mesmo pipeline é aplicado ao arquivo enviado pelo usuário no `st.file_uploader`.")
    st.subheader("2. Estatística")
    st.markdown(
        "- **Média** $\\bar{x}=\\frac{\\sum x_i}{n}$; **mediana** = valor central dos dados ordenados; **moda** = valor "
        "mais frequente (taxas arredondadas a 1 casa).\n"
        "- **Quartis** por interpolação linear na posição $(n-1)p$ (mesmo método do Excel `QUARTIL.INC`); "
        "**IQR** $=Q_3-Q_1$; **amplitude** $=\\max-\\min$.\n"
        "- **Variância** $\\sigma^2=\\frac{\\sum (x_i-\\bar{x})^2}{n}$ e **desvio padrão** $\\sigma=\\sqrt{\\sigma^2}$ "
        "(populacionais, pois analisamos todas as UFs; a versão amostral, com $n-1$, também é mostrada).\n"
        "- **Outliers**: abaixo de $Q_1-1{,}5\\cdot IQR$ ou acima de $Q_3+1{,}5\\cdot IQR$; comparamos média e mediana "
        "com e sem eles.\n"
        "- **Dados agrupados** (faixas de idade): média $\\frac{\\sum x_i f_i}{\\sum f_i}$ e mediana "
        "$L+\\frac{n/2-F_{ant}}{f}\\cdot h$.\n"
        "- **Correlação de Pearson** entre informalidade e desocupação.\n"
        "- Todas as fórmulas estão implementadas em `core/estatistica.py` e conferidas contra NumPy/Pandas em "
        "`tests/test_estatistica.py`.")
    st.subheader("3. Fontes")
    st.markdown(
        "- IBGE, PNAD Contínua — Retrospectiva 2012-2024 (fev/2025) e Retrospectiva 2012-2022.\n"
        "- IBGE, Censo Demográfico 2022 — População por idade e sexo; Identificação étnico-racial; Alfabetização; "
        "Quilombolas e Indígenas (alfabetização).\n"
        "- IBGE, Anuário Estatístico do Brasil 2024 — Tabelas 2.1.1.2, 2.1.1.3, 2.1.3.1 e 2.1.4.1.\n"
        "- IBGE, Estatísticas de Gênero: indicadores sociais das mulheres no Brasil, 3ª edição (2024).")
    st.subheader("4. Limitações")
    st.markdown(
        "- A série de desocupação por UF foi **reponderada** pelo IBGE em 2024 (novas projeções de população): os valores "
        "podem diferir de reportagens antigas (ex.: Brasil 2022 = 9,6% na série atual e 9,3% na antiga).\n"
        "- A taxa de informalidade (proxy) só existe a partir de 2016.\n"
        "- Os recortes de idade, cor ou raça e sexo do Censo usados nas páginas individuais estão por **Grande Região**; "
        "para UFs, envie a tabela do SIDRA pelo upload (tabelas 9514, 9606 e 9543 do Censo 2022).\n"
        "- As ilustrações são próprias do grupo, feitas com Matplotlib a partir dos dados oficiais.")


def pagina_trabalho():
    from grupo_trabalho_emprego.secao import render
    render("t6")


def pagina_arthur():
    from individuais.arthur_souza_populacao.secao import render
    render("arthur")


def pagina_clara():
    from individuais.clara_lima_alfabetizacao.secao import render
    render("clara")


def pagina_gustavo():
    from individuais.gustavo_henrique_mulheres.secao import render
    render("gustavo")


paginas = {
    "Painel do grupo": [
        st.Page(pagina_inicio, title="Início — Lupa Dados", icon="🏠", url_path="inicio", default=True),
        st.Page(pagina_trabalho, title="Tema 6 — Trabalho e Emprego", icon="💼", url_path="trabalho-emprego"),
    ],
    "Indicadores individuais": [
        st.Page(pagina_arthur, title="1 · População (Arthur)", icon="👥", url_path="populacao"),
        st.Page(pagina_clara, title="2 · Alfabetização (Clara)", icon="📚", url_path="alfabetizacao"),
        st.Page(pagina_gustavo, title="4 · Mulheres (Gustavo)", icon="♀️", url_path="mulheres"),
    ],
    "Sobre": [st.Page(pagina_metodologia, title="Metodologia e fontes", icon="ℹ️", url_path="metodologia")],
}
navegacao = st.navigation(paginas, position="sidebar", expanded=True)
st.sidebar.caption("Lupa Dados · Arthur de Souza · Clara Lima · Gustavo Henrique")
navegacao.run()
