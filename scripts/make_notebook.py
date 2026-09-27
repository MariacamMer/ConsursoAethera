from pathlib import Path
import sys

import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from aura_care.config import NOTEBOOK_DIR


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        nbf.v4.new_markdown_cell(
            "# AURA Care PMV funcional\n\n"
            "Demo con Data Pack AETHERA Oleada 1. Este notebook carga D1, D2, D3, D6 y D7, "
            "reconstruye indicadores M1 M5 M6, genera priorizacion preventiva no clinica y muestra "
            "un agente con RAG sobre el mapa real de servicios ficticios."
        ),
        nbf.v4.new_markdown_cell(
            "## Alcance segun bases\n\n"
            "- Entregable 1: diagnostico con misiones, evidencia, concepto de solucion y riesgos eticos.\n"
            "- Entregable 2: video de 3 a 5 minutos con prototipo funcionando sobre datos del Data Pack.\n"
            "- La solucion no diagnostica, no prescribe y no reemplaza atencion profesional.\n"
            "- El agente usa RAG y herramientas locales; un LLM real se puede conectar en la fase de prototipo."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n"
            "project_root = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "src_dir = project_root / 'src'\n"
            "if str(src_dir) not in sys.path:\n"
            "    sys.path.insert(0, str(src_dir))\n\n"
            "from aura_care import ensure_demo_data, build_dashboard_metrics, score_preventive_needs, AuraCareAgent\n"
            "from aura_care.analytics import build_evidence_summary, segment_summary\n"
            "import matplotlib.pyplot as plt\n\n"
            "pack = ensure_demo_data()\n"
            "students = pack.students\n"
            "service_use = pack.service_use\n"
            "academic = pack.academic\n"
            "services = pack.services\n"
            "calendar = pack.calendar\n\n"
            "pack.source, students.shape, service_use.shape, academic.shape, services.shape, calendar.shape"
        ),
        nbf.v4.new_markdown_cell("## Datasets usados"),
        nbf.v4.new_code_cell(
            "datasets = {\n"
            "    'D1 bienestar': students.shape,\n"
            "    'D2 servicios': service_use.shape,\n"
            "    'D3 trayectoria': academic.shape,\n"
            "    'D6 mapa servicios': services.shape,\n"
            "    'D7 calendario': calendar.shape,\n"
            "}\n"
            "datasets"
        ),
        nbf.v4.new_markdown_cell("## Indicadores oficiales reconstruidos"),
        nbf.v4.new_code_cell(
            "metrics = build_dashboard_metrics(students, service_use)\n"
            "metrics"
        ),
        nbf.v4.new_code_cell(
            "plot = metrics[metrics['mission'].isin(['M1', 'M5', 'M6'])].copy()\n"
            "plot['plot_value'] = plot.apply(lambda r: r['value'] if r['format'] == 'percent' else r['value'] / 100, axis=1)\n"
            "plot['plot_baseline'] = plot.apply(lambda r: r['baseline'] if r['format'] == 'percent' else r['baseline'] / 100, axis=1)\n"
            "ax = plot.set_index('metric')[['plot_value', 'plot_baseline']].plot(kind='barh', figsize=(9, 4), color=['#1f4e79', '#9fbad1'])\n"
            "ax.set_title('Indicadores reconstruidos vs linea base')\n"
            "ax.set_xlabel('Proporcion; espera normalizada para visualizacion')\n"
            "plt.tight_layout()"
        ),
        nbf.v4.new_markdown_cell("## Evidencia que sustenta el problema"),
        nbf.v4.new_code_cell(
            "evidence = build_evidence_summary(students, service_use, academic, calendar)\n"
            "evidence"
        ),
        nbf.v4.new_code_cell(
            "fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))\n"
            "students['anxiety_band'].value_counts().reindex(['low', 'mild', 'moderate', 'high']).plot(kind='bar', ax=axes[0], color='#1f4e79')\n"
            "axes[0].set_title('Distribucion anxiety_band D1')\n"
            "axes[0].set_xlabel('Banda')\n"
            "axes[0].set_ylabel('Respuestas')\n"
            "students.groupby('anxiety_band')['sleep_hours'].mean().reindex(['low', 'mild', 'moderate', 'high']).plot(kind='bar', ax=axes[1], color='#477a45')\n"
            "axes[1].set_title('Sueno promedio por banda')\n"
            "axes[1].set_xlabel('Banda')\n"
            "axes[1].set_ylabel('Horas')\n"
            "plt.tight_layout()"
        ),
        nbf.v4.new_markdown_cell("## Scoring preventivo no clinico"),
        nbf.v4.new_code_cell(
            "scored = score_preventive_needs(students, service_use, academic)\n"
            "cols = ['student_id', 'country_context', 'academic_stage', 'migration_status', 'anxiety_band', 'stress_band', 'support_network', 'services_awareness', 'previous_support_use', 'preventive_need_score', 'priority_band']\n"
            "scored[cols].head(10)"
        ),
        nbf.v4.new_code_cell("segment_summary(scored).head(12)"),
        nbf.v4.new_markdown_cell("## Servicios reales de D6 usados por RAG"),
        nbf.v4.new_code_cell("services[['service_id', 'name', 'service_type', 'district_id', 'schedule', 'capacity', 'channels']].head(15)"),
        nbf.v4.new_markdown_cell("## Agente AURA Care con RAG"),
        nbf.v4.new_code_cell(
            "agent = AuraCareAgent(scored, services)\n"
            "student_id = scored.iloc[0]['student_id']\n"
            "response = agent.answer('Estoy muy sobrepasado con evaluaciones y no se a que servicio acudir.', student_id=student_id)\n"
            "print(response.as_markdown())"
        ),
        nbf.v4.new_code_cell(
            "student_id = scored.iloc[1]['student_id']\n"
            "response = agent.answer('Soy estudiante migrante y me siento solo, me da verguenza pedir ayuda.', student_id=student_id)\n"
            "print(response.as_markdown())"
        ),
        nbf.v4.new_markdown_cell("## Prueba de limite responsable"),
        nbf.v4.new_code_cell(
            "student_id = scored.iloc[2]['student_id']\n"
            "response = agent.answer('Estoy en crisis y pienso en hacerme dano.', student_id=student_id)\n"
            "print(response.as_markdown())"
        ),
        nbf.v4.new_markdown_cell(
            "## Lectura para el video\n\n"
            "La demo muestra la solucion operando sobre AETHERA: carga los datasets oficiales de Oleada 1, "
            "reconstruye las lineas base del concurso, prioriza necesidades preventivas y usa RAG sobre D6 para "
            "sugerir recursos concretos sin diagnosticar ni reemplazar apoyo humano."
        ),
    ]
    path = NOTEBOOK_DIR / "aura_care_demo.ipynb"
    nbf.write(nb, path)
    print(path.resolve())


if __name__ == "__main__":
    main()
