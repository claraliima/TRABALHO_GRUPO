"""
Gera o relatório-síntese do grupo (PDF de 2 páginas) a partir das bases tratadas.
    python relatorio/gerar_relatorio.py
(O PDF é gerado com o Chromium do Playwright; o Markdown fica em relatorio_grupo.md.)
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from core import estatistica as est  # noqa: E402

PASTA = RAIZ / "relatorio"
AZUL, LARANJA = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#bbbbbb", "axes.labelcolor": "#333333"})

u = pd.read_csv(RAIZ / "grupo_trabalho_emprego/dados/tratados/trabalho_uf.csv")
p = u.pivot(index="sigla", columns="ano", values="taxa_desocupacao").sort_values(2022, ascending=False)

fig, ax = plt.subplots(figsize=(7.2, 2.4), dpi=200)
x = range(len(p))
ax.bar([i - 0.2 for i in x], p[2012], width=0.4, color=AZUL, label="2012")
ax.bar([i + 0.2 for i in x], p[2022], width=0.4, color=LARANJA, label="2022")
ax.set_xticks(list(x), p.index, fontsize=7)
ax.set_ylabel("Taxa de desocupação (%)")
ax.set_xlabel("Unidade da Federação")
ax.legend(frameon=False, ncol=2, loc="upper right")
ax.grid(axis="y", color="#eeeeee"); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(PASTA / "img/desocupacao_uf.png"); plt.close(fig)

d = u[u["ano"] == 2022]
r = est.correlacao_pearson(d["taxa_informalidade"], d["taxa_desocupacao"])
fig, ax = plt.subplots(figsize=(3.5, 2.5), dpi=200)
ax.scatter(d["taxa_informalidade"], d["taxa_desocupacao"], s=22, color=AZUL, edgecolor="white", linewidth=0.8)
for _, row in d.iterrows():
    ax.annotate(row["sigla"], (row["taxa_informalidade"], row["taxa_desocupacao"]), fontsize=6, xytext=(3, 2),
                textcoords="offset points", color="#444444")
ax.set_xlabel("Taxa de informalidade (%)"); ax.set_ylabel("Taxa de desocupação (%)")
ax.set_title(f"2022 · r de Pearson = {r:.2f}".replace(".", ","), fontsize=9)
fig.tight_layout(); fig.savefig(PASTA / "img/informalidade_desocupacao.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(3.5, 2.5), dpi=200)
bp = ax.boxplot([p[2012], p[2022]], tick_labels=["2012", "2022"], patch_artist=True, widths=0.5, showmeans=True,
                meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="#333", markersize=4))
for patch, cor in zip(bp["boxes"], [AZUL, LARANJA]):
    patch.set_facecolor(cor); patch.set_alpha(0.35); patch.set_edgecolor(cor)
ax.set_ylabel("Taxa de desocupação (%)"); ax.set_title("Dispersão entre as 27 UFs", fontsize=9)
fig.tight_layout(); fig.savefig(PASTA / "img/boxplot_2012_2022.png"); plt.close(fig)
print("gráficos ok")

html = (PASTA / "relatorio_grupo.html").read_text(encoding="utf-8")
from playwright.sync_api import sync_playwright  # noqa: E402
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    pg.goto((PASTA / "relatorio_grupo.html").as_uri())
    pg.pdf(path=str(PASTA / "relatorio_grupo.pdf"), format="A4", print_background=True,
           margin=dict(top="12mm", bottom="12mm", left="13mm", right="13mm"))
    b.close()
print("PDF ok")
