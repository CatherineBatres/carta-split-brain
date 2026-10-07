"""Ninguna clave real puede terminar en un archivo que se sube a GitHub (D-30).

Error real: la clave de Gemini quedó pegada en .env.example (la plantilla, que sí se sube) y
GitHub bloqueó el push. La clave va SOLO en .env, que está en .gitignore.
Corre  pytest  antes de cada  git push.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCADOR = "pega_tu_clave_de_aistudio_aqui"
CLAVE_RE = re.compile(r"AIza[0-9A-Za-z_\-]{30,}|AQ\.[0-9A-Za-z_\-]{30,}")
TEXTO = {".py", ".md", ".txt", ".json", ".jsonl", ".csv", ".toml", ".example", ".yml", ".yaml"}
IGNORAR = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}


def test_la_plantilla_no_trae_una_clave_real():
    lineas = (RAIZ / ".env.example").read_text(encoding="utf-8").splitlines()
    claves = [ln for ln in lineas if ln.startswith("GEMINI_API_KEY=")]
    assert claves == [f"GEMINI_API_KEY={MARCADOR}"], (
        ".env.example debe traer el texto de ejemplo. Tu clave real va en .env")


def test_env_esta_ignorado_por_git():
    assert ".env" in (RAIZ / ".gitignore").read_text(encoding="utf-8").split()


def test_ningun_archivo_del_proyecto_contiene_algo_que_parezca_una_clave():
    sospechosos = []
    for f in RAIZ.rglob("*"):
        if (not f.is_file() or f.name == ".env" or f.suffix.lower() not in TEXTO
                or IGNORAR & set(f.relative_to(RAIZ).parts)):
            continue
        if CLAVE_RE.search(f.read_text(encoding="utf-8", errors="ignore")):
            sospechosos.append(str(f.relative_to(RAIZ)))
    assert not sospechosos, f"Parece haber una clave en: {sospechosos}"
