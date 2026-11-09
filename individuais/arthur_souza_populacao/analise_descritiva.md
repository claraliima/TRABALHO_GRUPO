# Análise descritiva — Indicador 1: População por Grupo de Idade, Sexo e Raça

**Entrega individual de: Arthur de Souza** · Grupo: Lupa Dados (Tema 6 — Trabalho e Emprego)
**Fonte:** IBGE, Censo Demográfico 2022 (Anuário Estatístico do Brasil 2024, tabelas 2.1.1.2, 2.1.3.1 e 2.1.4.1; Identificação étnico-racial, dez/2023); Censo 2010.

## 1. Estrutura etária (dados agrupados em faixas de idade)

A população de 2022 (203.080.756 pessoas) foi organizada numa tabela de distribuição de frequências com 15 classes de idade (14 de 5 anos e a classe aberta "70 anos ou mais", fechada em 90 anos para a média).

| Medida | Valor | Como foi calculada |
|---|---|---|
| Idade mediana | **35,2 anos** | Md = L + ((n/2 − Fant)/f)·h — bate com a idade mediana oficial do IBGE (35) |
| Idade média | 36,4 anos | Σ(ponto médio × frequência) / n |
| Q1 / Q3 | 18,7 / 52,2 anos | mesma fórmula com n/4 e 3n/4 |
| IQR | 33,5 anos | metade central da população tem entre 19 e 52 anos |
| Desvio padrão | 21,7 anos | √(Σ f·(x − média)² / n) |
| Classe modal | 35 a 39 anos | classe de maior densidade (frequência ÷ amplitude) |

**Leitura:** média > mediana → distribuição **assimétrica à direita**: a cauda de idosos puxa a média. A mediana não depende da hipótese sobre a classe aberta, por isso é a medida preferida.

Indicadores de estrutura (Brasil): razão de sexo 94,2 homens por 100 mulheres; 69,3% em idade ativa (15–64 anos); 10,9% com 65+; índice de envelhecimento 80 (pessoas de 60+ para cada 100 de 0–14 anos). Idade mediana por região: Norte 29,3 · Nordeste 33,7 · Centro-Oeste 33,7 · Sul 36,6 · Sudeste 37,1.

**Tamanho das faixas (14 grupos de 5 anos):** média 13,48 mi, mediana 13,71 mi, desvio padrão 2,33 mi, IQR 2,84 mi. **Outlier:** "65 a 69 anos" (7,88 mi, abaixo do limite de 8,36 mi) — sem ele a média sobe para 13,92 mi e a mediana quase não muda (13,75 mi).

## 2. Cor ou raça e sexo

Pardos 45,3%, brancos 43,5%, pretos 10,2%, indígenas 0,6% e amarelos 0,4% (pretos + pardos = 55,5%). A composição muda muito entre regiões: brancos são 72,6% no Sul e 20,7% no Norte; pardos são 67,2% no Norte. No campo, os pardos são 55,7%; nas cidades, 43,9%.

Razão de sexo por cor ou raça: pretos 103,9 (mais homens), pardos 96,4, indígenas 97,1, brancos 89,9, amarelos 89,2. Idade mediana: indígenas 25 anos, pardos 32, pretos 36, brancos 37, amarelos 44.

## 3. Comparação entre as 27 UFs (2022)

| Indicador | Média | Mediana | Desvio padrão | Outliers (1,5×IQR) | Média sem outliers |
|---|---|---|---|---|---|
| População (mi) | 7,52 | 3,94 | 8,76 | SP (44,4), MG (20,5) | 5,53 |
| Densidade (hab/km²) | 72,3 | 35,0 | 110,5 | DF (489,1), RJ (367,0) | 43,8 |
| Crescimento 2010-2022 (%) | 9,0 | 7,1 | 8,5 | RR (41,3%) | 7,8 |

Nos três casos a **média é muito maior que a mediana** porque poucos estados extremos puxam a média para cima (assimetria à direita). Roraima cresceu 41% em 12 anos, impulsionado pela imigração venezuelana. A mediana descreve melhor o estado "típico".

## 4. Conexão com as personas

- **Ministério do Trabalho:** o Norte, mais jovem, precisa de políticas de primeiro emprego; Sul e Sudeste, mais envelhecidos, de manutenção de trabalhadores maduros e reposição de mão de obra.
- **Indústria e Sebrae:** com metade da população entre 19 e 52 anos e idade mediana subindo (29 → 35 anos de 2010 a 2022), cresce a necessidade de requalificação de trabalhadores 40+ e de produtos/serviços para um público mais velho.
- Metas de emprego precisam considerar a composição racial regional (ex.: Norte e Nordeste majoritariamente pardos).

## 5. Limitações

Os cruzamentos idade × sexo × situação e cor × sexo estão por Grande Região (o Anuário não traz UF). Para UFs, a base pode ser substituída pelo upload de tabelas do SIDRA (ex.: tabelas 9514 e 9606 do Censo 2022).
