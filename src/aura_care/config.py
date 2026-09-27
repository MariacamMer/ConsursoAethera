from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

RISK_KEYWORDS = [
    "suicidio",
    "suicidarme",
    "quitarme la vida",
    "no quiero vivir",
    "hacerme dano",
    "hacer daño",
    "autolesion",
    "autolesionarme",
    "me quiero morir",
    "crisis",
]

MISSION_BASELINES = {
    "M1_ansiedad_moderada_alta": 0.41,
    "M5_sintomatologia_sin_consulta": 0.68,
    "M6_desconoce_servicios": 0.44,
    "M6_espera_consejeria_dias": 42.0,
    "M6_espera_consejeria_semanas": 6.0,
    "M2_sobrecarga_evaluaciones": 0.57,
}
