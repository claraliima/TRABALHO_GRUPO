# 🔎 Lupa Dados — Números que Falam: Descobrindo o Brasil

Projeto Integrador · Python & Matemática · Etapa 3
Dashboard em **Streamlit** com dados oficiais do **IBGE**, estatística descritiva e análise para personas do setor público e produtivo.

## Identificação do grupo

| Integrante | Responsabilidade | Indicador | Pasta |
|---|---|---|---|
| Arthur de Souza, Clara Lima e Gustavo Henrique | **Parte do grupo** | **Tema 6 — Trabalho e Emprego**: taxa de desocupação (2012 × 2022) e informalidade · Personas: Ministério do Trabalho, Sebrae e Indústria | `grupo_trabalho_emprego/` |
| **Arthur de Souza** | Entrega individual | 1 — População por Grupo de Idade, Sexo e Raça | `individuais/arthur_souza_populacao/` |
| **Clara Lima** | Entrega individual | 2 — Alfabetização por sexo e raça | `individuais/clara_lima_alfabetizacao/` |
| **Gustavo Henrique** | Entrega individual | 4 — Mulheres | `individuais/gustavo_henrique_mulheres/` |

## Como executar

```bash
pip install -r requirements.txt

# Painel unificado do grupo (todas as seções, com menu na barra lateral)
streamlit run app.py

# Dashboards individuais
streamlit run individuais/arthur_souza_populacao/app.py
streamlit run individuais/clara_lima_alfabetizacao/app.py
streamlit run individuais/gustavo_henrique_mulheres/app.py
```

Para refazer o ETL (brutos → tratados) e rodar os testes:

```bash
python -m grupo_trabalho_emprego.etl_trabalho
python -m individuais.arthur_souza_populacao.etl_populacao
python -m individuais.clara_lima_alfabetizacao.etl_alfabetizacao
python -m individuais.gustavo_henrique_mulheres.etl_mulheres
python scripts/gerar_imagens.py
python -m pytest tests -q
```

## Estrutura do repositório

```
├── app.py                      # PAINEL UNIFICADO DO GRUPO (menu de navegação)
├── requirements.txt
├── core/                       # código compartilhado pelo grupo
│   ├── estatistica.py          # média, mediana, moda, quartis, IQR, variância, desvio padrão, outliers...
│   ├── carregamento.py         # ETL genérico + upload CSV/XLSX (st.file_uploader)
│   └── ui.py                   # layout, gráficos, boxplot, mapa por UF, notícias
├── grupo_trabalho_emprego/     # TEMA 6 (parte do grupo)
│   ├── secao.py · etl_trabalho.py · analise_descritiva.md
│   └── dados/brutos · dados/tratados
├── individuais/
│   ├── arthur_souza_populacao/     # entrega individual — Arthur
│   ├── clara_lima_alfabetizacao/   # entrega individual — Clara
│   └── gustavo_henrique_mulheres/  # entrega individual — Gustavo
├── relatorio/                  # relatório-síntese do grupo (1–2 páginas, PDF e Markdown)
├── assets/                     # imagens ilustrativas e mapa das UFs
├── scripts/gerar_imagens.py
└── tests/                      # testes das fórmulas e da interface
```

## Como o projeto atende à rubrica

| Critério | Onde está |
|---|---|
| **1. ETL e interface (0,75)** | `st.file_uploader` em todas as páginas (CSV/XLSX; detecta cabeçalho do SIDRA, remove rodapés, converte vírgula decimal e milhar, aplica a convenção de sinais do IBGE (`-` = zero; `..`/`...`/`X` = ausente), padroniza UF, aceita formato largo com anos nas colunas, remove duplicadas e valida colunas, com modelo para download). Filtros na barra lateral: anos, regiões, UFs, sexo, cor ou raça, faixa etária, situação do domicílio. Bases tratadas em `dados/tratados/` (CSV + XLSX) e download dos dados filtrados. |
| **2. Rigor estatístico e perguntas de negócio (0,90)** | Abas **📐 Estatística**: média, mediana, moda, Q1/Q2/Q3, IQR, amplitude, variância, desvio padrão (populacional e amostral), CV, limites de 1,5×IQR, outliers e efeito na média × mediana; dados agrupados (mediana de idade); correlação de Pearson. Abas **💡 Respostas** respondem às perguntas das personas com números calculados. Fórmulas conferidas em `tests/test_estatistica.py`. |
| **3. Visualização e conteúdo adicional (0,60)** | Barras comparativas 2012 × 2022, boxplots com outliers rotulados, histogramas com média/mediana, linhas temporais, pirâmides etárias, dispersão, mapas por UF; todos com eixos rotulados e fonte. Abas **📰 Notícias** com reportagens reais e imagens ilustrativas próprias. |

## Fontes (IBGE)

- PNAD Contínua — Retrospectiva 2012-2024 (fev/2025) e Retrospectiva 2012-2022.
- Censo Demográfico 2022 — População por idade e sexo; Identificação étnico-racial; Alfabetização; Quilombolas e Indígenas.
- Anuário Estatístico do Brasil 2024 — tabelas 2.1.1.2, 2.1.1.3, 2.1.3.1 e 2.1.4.1.
- Estatísticas de Gênero: indicadores sociais das mulheres no Brasil, 3ª ed. (2024).

## Como enviar para o GitHub

```bash
git init
git add .
git commit -m "Projeto Integrador - Números que Falam (Lupa Dados)"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/numeros-que-falam.git
git push -u origin main
```

Se cada integrante precisar entregar a parte individual em um repositório próprio, use o ZIP individual correspondente (já contém `core/`, `requirements.txt` e a pasta do integrante).
