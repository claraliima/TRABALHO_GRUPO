# Script auxiliar usado só nos testes automatizados (AppTest) da seção do grupo
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from grupo_trabalho_emprego.secao import render  # noqa: E402
render("t6")
