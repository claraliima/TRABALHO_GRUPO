# Análise descritiva — Tema 6: Trabalho e Emprego (parte do grupo)

**Startup:** Lupa Dados · **Equipe:** Arthur de Souza, Clara Lima e Gustavo Henrique
**Personas:** Ministério do Trabalho, Sebrae e Indústria
**Foco:** taxa de desocupação (2012 × 2022) e informalidade
**Fonte:** IBGE, PNAD Contínua — Retrospectiva 2012-2024 (médias anuais por UF) e Retrospectiva 2012-2022 (ocupados por atividade e posição na ocupação); Estatísticas de Gênero, 3ª ed. (2024).

## 1. Desocupação nas 27 UFs — 2012 × 2022

| Medida | 2012 | 2022 | Diferença |
|---|---|---|---|
| Brasil (taxa nacional) | 7,4% | 9,6% | +2,2 p.p. |
| Média das UFs | 7,90% | 9,61% | +1,71 |
| Mediana | 7,8% | 9,7% | +1,9 |
| Moda | multimodal (5,0; 7,4; 7,9; 11,4) | multimodal (4,9; 7,7; 12,4; 13,1) | — |
| Q1 / Q3 | 6,05% / 9,45% | 7,0% / 12,4% | — |
| IQR | 3,4 p.p. | 5,4 p.p. | +2,0 |
| Amplitude | 9,9 p.p. (SC 3,4 – AP 13,3) | 12,1 p.p. (SC 3,8 – PE 15,9) | +2,2 |
| Desvio padrão (populacional) | 2,31 p.p. | 3,51 p.p. | +1,20 |
| Coeficiente de variação | 29,2% | 36,5% | +7,3 |

**Leitura:** o desemprego subiu e ficou **mais desigual** entre os estados — todas as medidas de dispersão aumentaram. 22 das 27 UFs pioraram. As maiores altas foram em Pernambuco (+6,6 p.p.), Rio de Janeiro (+5,7) e Piauí (+4,0); melhoraram Roraima (−3,1), Rondônia (−1,5), Mato Grosso do Sul (−1,2), Mato Grosso (−1,1) e Tocantins (−0,3).

**Outliers:** entre as 27 UFs juntas não há outliers (limites de 1,5×IQR: −1,1% e 20,5% em 2022). Por isso média (9,61%) e mediana (9,7%) praticamente coincidem. Mas **dentro das regiões** aparecem extremos: **Pernambuco (15,9%)** no Nordeste e **Rio de Janeiro (13,3%)** no Sudeste. Sem o RJ, a média do Sudeste cai de 9,65% para 8,43% — a mediana (8,8%) representa melhor a região.

Medianas regionais em 2022: Nordeste 12,0% · Norte 9,7% · Sudeste 8,8% · Centro-Oeste 6,3% · Sul 6,0%.

## 2. Informalidade (2022)

Média das UFs 43,8%, mediana 44,1%, Q1 36,6%, Q3 52,1%, IQR 15,5 p.p., desvio padrão 9,76 p.p., amplitude 35,3 p.p. (SC 27,4% a PA 62,7%). Sem outliers. As cinco maiores taxas estão no Norte/Nordeste: PA 62,7%, MA 58,5%, AM 57,4%, PI 54,8%, BA 54,5%.

A correlação de Pearson entre informalidade e desocupação em 2022 é **r = 0,53** (positiva e moderada): estados mais informais tendem a ter mais desemprego — os dois refletem uma estrutura produtiva com menos empregos formais.

## 3. Indústria e trabalho por conta própria (Brasil)

- Indústria geral: 13,3 milhões de ocupados em 2012 → 12,6 milhões em 2022 (**−4,9%**), enquanto o total de ocupados cresceu.
- Conta própria com CNPJ: 4,2 milhões (2016) → 6,6 milhões (2022), **+55,5%**; a parcela formalizada passou de 19,1% para 25,7%. Mesmo assim, 19,0 milhões ainda trabalham por conta própria **sem CNPJ**.
- Empregados sem carteira no setor privado chegaram a 12,7 milhões em 2022.

## 4. Quem é mais afetado (2022)

Desocupação: homens 7,9% × mulheres 11,8%; homens brancos 6,3% × mulheres pretas ou pardas 14,0% (2,2 vezes). Participação na força de trabalho: homens 73,2% × mulheres 53,3%.

## 5. Recomendações às personas

- **Ministério do Trabalho:** metas regionais (a média nacional esconde a dispersão crescente); prioridade a PE, BA, RJ e demais estados do Nordeste; programas com recorte de gênero e raça e oferta de creches.
- **Sebrae:** formalização (MEI, crédito orientado, compras públicas) em PA, MA, AM, PI e BA — onde a informalidade passa de 54%.
- **Indústria:** o emprego industrial ainda não voltou ao nível de 2012; há mão de obra disponível nos estados de maior desocupação — parcerias de qualificação (SENAI) com o Ministério.

## 6. Limitações

A série por UF foi reponderada pelo IBGE em 2024 (Brasil 2022 = 9,6% na série atual; 9,3% na publicação original). A informalidade (proxy) só existe a partir de 2016. Os dados de atividade/posição seguem a ponderação anterior (Retrospectiva 2012-2022).
