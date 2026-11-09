"""
Gera as imagens ilustrativas (infográficos) usadas na seção de conteúdo adicional.
As ilustrações são próprias do grupo (desenhadas com Matplotlib) e usam números
oficiais do IBGE — assim não dependemos de links externos de imagens.

    python scripts/gerar_imagens.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle, Wedge

SAIDA = Path(__file__).resolve().parents[1] / "assets" / "img"
SAIDA.mkdir(parents=True, exist_ok=True)

AZUL, LARANJA, AQUA, AMARELO, MAGENTA, VERDE, VIOLETA = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6")
FUNDO, TINTA, TINTA2 = "#f5f8fd", "#0b0b0b", "#52514e"


def tela(cor_fundo=FUNDO):
    fig = plt.figure(figsize=(8, 4.5), dpi=110)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 16, 9, color=cor_fundo, zorder=0))
    return fig, ax


def textos(ax, titulo, numero, legenda, fonte, x=8.6, cor=AZUL):
    ax.text(x, 7.3, titulo, fontsize=17, weight="bold", color=TINTA, va="center")
    ax.text(x, 5.2, numero, fontsize=40, weight="bold", color=cor, va="center")
    ax.text(x, 3.3, legenda, fontsize=12.5, color=TINTA2, va="center", wrap=True)
    ax.text(0.5, 0.5, fonte, fontsize=9, color="#8a8984")


def salvar(fig, nome):
    fig.savefig(SAIDA / nome, facecolor=fig.get_facecolor())
    plt.close(fig)


def pessoa(ax, x, y, cor, s=1.0):
    ax.add_patch(Circle((x, y + 1.25 * s), 0.38 * s, color=cor, zorder=3))
    ax.add_patch(FancyBboxPatch((x - 0.48 * s, y - 0.2 * s), 0.96 * s, 1.0 * s,
                                boxstyle="round,pad=0.05,rounding_size=0.35", color=cor, zorder=3))


# ---------------------------------------------------------------- Grupo: trabalho
def trabalho_carteira():
    fig, ax = tela()
    ax.add_patch(FancyBboxPatch((1.4, 1.6), 5.2, 6.2, boxstyle="round,pad=0.1,rounding_size=0.4", color="#184f95"))
    ax.add_patch(Rectangle((1.9, 2.1), 4.2, 0.12, color="#86b6ef"))
    ax.text(4.0, 6.2, "CARTEIRA DE\nTRABALHO", ha="center", va="center", fontsize=15, weight="bold", color="white")
    ax.add_patch(Circle((4.0, 4.0), 0.9, color="#86b6ef"))
    ax.text(4.0, 4.0, "?", ha="center", va="center", fontsize=30, weight="bold", color="#184f95")
    textos(ax, "Informalidade no Brasil", "38,2 mi", "trabalhadores informais em 2022\n(39,4% dos ocupados)",
           "Ilustração do grupo · Dados: IBGE, PNAD Contínua — Retrospectiva 2012-2024")
    salvar(fig, "trabalho_informalidade.png")


def trabalho_industria():
    fig, ax = tela()
    base = [(1, 1.6), (1, 5), (2.4, 5), (2.4, 6.6), (3.6, 5.6), (3.6, 6.6), (4.8, 5.6), (4.8, 6.6), (6, 5.6),
            (6, 8), (6.8, 8), (6.8, 1.6)]
    ax.add_patch(Polygon(base, closed=True, color="#256abf"))
    for i in range(3):
        for j in range(2):
            ax.add_patch(Rectangle((1.4 + i * 1.5, 2.3 + j * 1.3), 0.8, 0.7, color="#cde2fb"))
    for k, a in enumerate((0.45, 0.3, 0.18)):
        ax.add_patch(Circle((6.7 + k * 0.45, 8.25 + k * 0.15), 0.25 + k * 0.08, color="#9ec5f4", alpha=a + 0.3))
    textos(ax, "Emprego na indústria", "−4,9%", "13,3 mi (2012) → 12,6 mi (2022)\nde ocupados na indústria geral",
           "Ilustração do grupo · Dados: IBGE, PNAD Contínua — Retrospectiva 2012-2022")
    salvar(fig, "trabalho_industria.png")


def trabalho_empreender():
    fig, ax = tela()
    ax.add_patch(Rectangle((1.3, 1.6), 5.6, 4.0, color=AQUA))
    for i in range(7):
        cor = "white" if i % 2 == 0 else LARANJA
        ax.add_patch(Polygon([(1.1 + i * 0.86, 5.6), (1.96 + i * 0.86, 5.6), (1.53 + i * 0.86, 6.6)], color=cor))
    ax.add_patch(Rectangle((1.1, 6.6), 6.0, 0.9, color=LARANJA))
    ax.text(4.1, 7.05, "CNPJ", ha="center", va="center", color="white", fontsize=15, weight="bold")
    ax.add_patch(Rectangle((3.5, 1.6), 1.2, 2.4, color="white"))
    ax.add_patch(Rectangle((1.8, 3.0), 1.2, 1.2, color="#e6f7f0"))
    ax.add_patch(Rectangle((5.2, 3.0), 1.2, 1.2, color="#e6f7f0"))
    textos(ax, "Conta própria com CNPJ", "+55,5%", "4,2 mi (2016) → 6,6 mi (2022)\nformalização via MEI/CNPJ",
           "Ilustração do grupo · Dados: IBGE, PNAD Contínua — Retrospectiva 2012-2022", cor=AQUA)
    salvar(fig, "trabalho_empreendedorismo.png")


# ---------------------------------------------------------------- Arthur: população
def populacao_piramide():
    fig, ax = tela()
    larg_h = [2.3, 2.4, 2.5, 2.6, 2.5, 2.3, 2.0, 1.7, 1.3, 1.0]
    larg_m = [2.2, 2.3, 2.45, 2.65, 2.62, 2.45, 2.2, 1.95, 1.55, 1.35]
    for i, (h, m) in enumerate(zip(larg_h, larg_m)):
        y = 1.4 + i * 0.62
        ax.add_patch(Rectangle((4.0 - h, y), h - 0.05, 0.5, color=AZUL))
        ax.add_patch(Rectangle((4.05, y), m, 0.5, color=LARANJA))
    ax.text(2.0, 8.1, "Homens", color=AZUL, fontsize=12, weight="bold", ha="center")
    ax.text(6.0, 8.1, "Mulheres", color=LARANJA, fontsize=12, weight="bold", ha="center")
    textos(ax, "Brasil mais velho", "35 anos", "idade mediana em 2022\n(era 29 anos em 2010)",
           "Ilustração do grupo · Dados: IBGE, Censo Demográfico 2022")
    salvar(fig, "populacao_piramide.png")


def populacao_cor_raca():
    fig, ax = tela()
    cores = [(LARANJA, "Parda 45,3%", 9), (AZUL, "Branca 43,5%", 9), (VIOLETA, "Preta 10,2%", 2)]
    k = 0
    for cor, _, n in cores:
        for _ in range(n):
            pessoa(ax, 1.4 + (k % 5) * 1.3, 7.1 - (k // 5) * 1.55, cor, 0.62)
            k += 1
    for i, (cor, rot, _) in enumerate(cores):
        ax.add_patch(Rectangle((8.6, 2.1 - i * 0.55), 0.35, 0.35, color=cor))
        ax.text(9.1, 2.27 - i * 0.55, rot, fontsize=11, va="center", color=TINTA2)
    ax.text(8.6, 7.3, "Composição por cor ou raça", fontsize=17, weight="bold", color=TINTA, va="center")
    ax.text(8.6, 5.4, "55,5%", fontsize=40, weight="bold", color=LARANJA, va="center")
    ax.text(8.6, 3.7, "se declaram pretos ou pardos\n(cada figura ≈ 5% da população)", fontsize=12, color=TINTA2,
            va="center")
    ax.text(0.5, 0.35, "Ilustração do grupo · Dados: IBGE, Censo 2022 (amarelos 0,4% e indígenas 0,6% não representados)",
            fontsize=9, color="#8a8984")
    salvar(fig, "populacao_cor_raca.png")


# ---------------------------------------------------------------- Clara: alfabetização
def alfabetizacao_livro():
    fig, ax = tela()
    ax.add_patch(Polygon([(1.0, 2.0), (4.1, 1.4), (4.1, 7.0), (1.0, 7.6)], color=AZUL))
    ax.add_patch(Polygon([(4.1, 1.4), (7.2, 2.0), (7.2, 7.6), (4.1, 7.0)], color="#3987e5"))
    for i in range(5):
        y = 6.4 - i * 0.9
        ax.plot([1.5, 3.7], [y + 0.25, y - 0.15], color="white", lw=3, solid_capstyle="round")
        ax.plot([4.5, 6.7], [y - 0.15, y + 0.25], color="white", lw=3, solid_capstyle="round")
    textos(ax, "Ler e escrever", "93,0%", "das pessoas de 15 anos ou mais\nsão alfabetizadas (2022)",
           "Ilustração do grupo · Dados: IBGE, Censo Demográfico 2022")
    salvar(fig, "alfabetizacao_livro.png")


def alfabetizacao_desigualdade():
    fig, ax = tela()
    dados = [("Branca", 4.3, AZUL), ("Parda", 8.8, LARANJA), ("Preta", 10.1, VIOLETA), ("Indígena", 16.1, AQUA)]
    for i, (rot, v, cor) in enumerate(dados):
        x = 1.0 + i * 1.75
        h = v / 16.1 * 5.0
        ax.add_patch(FancyBboxPatch((x, 1.6), 1.2, h, boxstyle="round,pad=0,rounding_size=0.15", color=cor))
        ax.text(x + 0.6, 1.75 + h, f"{v:.1f}%".replace(".", ","), ha="center", va="bottom", fontsize=12,
                weight="bold", color=TINTA)
        ax.text(x + 0.6, 1.15, rot, ha="center", fontsize=10.5, color=TINTA2)
    textos(ax, "Analfabetismo por cor ou raça", "3,7×", "a taxa entre indígenas (16,1%)\nfrente à de brancos (4,3%)",
           "Ilustração do grupo · Dados: IBGE, Censo Demográfico 2022", cor=AQUA)
    salvar(fig, "alfabetizacao_desigualdade.png")


# ---------------------------------------------------------------- Gustavo: mulheres
def mulheres_maioria():
    fig, ax = tela()
    ax.add_patch(Wedge((4.0, 4.6), 2.9, 90, 90 + 360 * 0.515, color=LARANJA))
    ax.add_patch(Wedge((4.0, 4.6), 2.9, 90 + 360 * 0.515, 450, color=AZUL))
    ax.add_patch(Circle((4.0, 4.6), 1.6, color=FUNDO))
    ax.text(4.0, 4.6, "♀", ha="center", va="center", fontsize=44, color=LARANJA)
    textos(ax, "Mulheres são maioria", "51,5%", "da população em 2022: 104,5 mi\nde mulheres e 98,5 mi de homens",
           "Ilustração do grupo · Dados: IBGE, Censo Demográfico 2022", cor=LARANJA)
    salvar(fig, "mulheres_maioria.png")


def mulheres_trabalho():
    fig, ax = tela()
    for i, (rot, v, cor) in enumerate([("Homens", 2920, AZUL), ("Mulheres", 2303, LARANJA)]):
        y = 5.6 - i * 2.4
        w = v / 2920 * 6.2
        ax.add_patch(FancyBboxPatch((1.0, y), w, 1.3, boxstyle="round,pad=0,rounding_size=0.2", color=cor))
        ax.text(1.2, y + 0.65, f"{rot}: R$ {v:,}".replace(",", "."), va="center", fontsize=12.5, color="white",
                weight="bold")
    textos(ax, "Desigualdade de renda", "78,9%", "é quanto as mulheres recebem\nem relação aos homens (2022)",
           "Ilustração do grupo · Dados: IBGE, Estatísticas de Gênero, 3ª edição (2024)", cor=LARANJA)
    salvar(fig, "mulheres_renda.png")


if __name__ == "__main__":
    for f in (trabalho_carteira, trabalho_industria, trabalho_empreender, populacao_piramide, populacao_cor_raca,
              alfabetizacao_livro, alfabetizacao_desigualdade, mulheres_maioria, mulheres_trabalho):
        f()
    print("Imagens geradas em", SAIDA)
