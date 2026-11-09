"""
ENTREGA INDIVIDUAL — Clara Lima
Indicador 2 · Alfabetização por sexo e raça

Como executar (na raiz do repositório):
    pip install -r requirements.txt
    streamlit run individuais/clara_lima_alfabetizacao/app.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from core import ui  # noqa: E402
from individuais.clara_lima_alfabetizacao.secao import render  # noqa: E402

st.set_page_config(page_title="2 · Alfabetização por sexo e raça · Clara Lima", page_icon="📚", layout="wide")
ui.aplicar_estilo()
st.sidebar.title("📚 Lupa Dados")
st.sidebar.caption("Entrega individual · **Clara Lima**\n\nProjeto Integrador — Números que Falam")
render("clara")
