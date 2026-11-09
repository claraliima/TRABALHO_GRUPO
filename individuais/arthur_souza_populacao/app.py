"""
ENTREGA INDIVIDUAL — Arthur de Souza
Indicador 1 · População por Grupo de Idade, Sexo e Raça

Como executar (na raiz do repositório):
    pip install -r requirements.txt
    streamlit run individuais/arthur_souza_populacao/app.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from core import ui  # noqa: E402
from individuais.arthur_souza_populacao.secao import render  # noqa: E402

st.set_page_config(page_title="1 · População por Grupo de Idade, Sexo e Raça · Arthur de Souza", page_icon="👥", layout="wide")
ui.aplicar_estilo()
st.sidebar.title("👥 Lupa Dados")
st.sidebar.caption("Entrega individual · **Arthur de Souza**\n\nProjeto Integrador — Números que Falam")
render("arthur")
