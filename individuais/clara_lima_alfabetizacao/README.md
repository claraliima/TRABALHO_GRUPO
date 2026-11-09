# Entrega individual — Clara Lima

**Indicador demográfico:** 2 — Alfabetização por sexo e raça
**Projeto Integrador:** Números que Falam — Descobrindo o Brasil (Python & Matemática)
**Grupo:** Lupa Dados — Tema 6, Trabalho e Emprego (Arthur de Souza, Clara Lima e Gustavo Henrique)

## O que está nesta pasta (checklist do entregável individual)

| Item exigido | Arquivo |
|---|---|
| Código Python do módulo: ETL | `etl_alfabetizacao.py` |
| Código Python do módulo: estatísticas | `secao.py` (usa as funções de `core/estatistica.py`) |
| Base IBGE bruta (como publicada) | `dados/brutos/` |
| Base IBGE tratada (CSV/XLSX limpo) | `dados/tratados/` — alfabetizacao_uf.csv, alfabetizacao_recortes.csv e base_alfabetizacao_tratada.xlsx |
| Análise descritiva (interpretação dos dados) | `analise_descritiva.md` |
| Seção do dashboard (Streamlit) | `app.py` (versão individual) e `secao.py` (integrada ao painel do grupo) |

## Como executar

Na **raiz do repositório**:

```bash
pip install -r requirements.txt
python -m individuais.clara_lima_alfabetizacao.etl_alfabetizacao      # (opcional) refaz o ETL: brutos -> tratados
streamlit run individuais/clara_lima_alfabetizacao/app.py
```

## O que o dashboard tem

- **Barra lateral:** filtros (região/UF, sexo, cor ou raça, faixa etária, ano, situação do domicílio — conforme o indicador) e bloco **📤 Upload de dados** (CSV/XLSX) com modelo para download.
- **KPIs** e gráficos interativos (barras comparativas, boxplot, histograma, linhas, mapa por UF).
- **Estatística:** média, mediana, moda, quartis, IQR, amplitude, variância, desvio padrão, coeficiente de variação e outliers (regra 1,5×IQR), com o efeito dos outliers na média × mediana.
- **Respostas** às perguntas de análise ligadas às personas (Ministério do Trabalho, Sebrae e Indústria).
- **Notícias** com links reais e imagens ilustrativas.
