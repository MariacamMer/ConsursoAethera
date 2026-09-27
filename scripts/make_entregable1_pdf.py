from __future__ import annotations

from pathlib import Path
import textwrap
import sys

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from aura_care import build_dashboard_metrics, ensure_demo_data
from aura_care.analytics import build_evidence_summary
from aura_care.config import DOCS_DIR, FIGURES_DIR


OUTPUT = DOCS_DIR / "entregable_1" / "Entregable_1_Diagnostico_AURA_Care.pdf"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".0%", "%")


def wrap(text: str, width: int = 100) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def add_block(fig, x: float, y: float, title: str, body: str, width: int = 95, size: int = 10) -> float:
    fig.text(x, y, title, fontsize=11.5, fontweight="bold", family="Times New Roman", va="top")
    body_text = wrap(body, width)
    fig.text(x, y - 0.025, body_text, fontsize=size, family="Times New Roman", va="top", linespacing=1.18)
    return y - 0.045 - 0.018 * (body_text.count("\n") + 1)


def make_pdf() -> Path:
    pack = ensure_demo_data()
    metrics = build_dashboard_metrics(pack.students, pack.service_use)
    evidence = build_evidence_summary(pack.students, pack.service_use, pack.academic, pack.calendar)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    metric_lookup = {row["metric"]: row["value"] for _, row in metrics.iterrows()}
    bars = [
        ("M1 ansiedad moderada-alta", metric_lookup["Sintomatologia ansiosa moderada-alta"], 0.41),
        ("M5 no consulta apoyo", metric_lookup["Sintomatologia y nunca consulto apoyo"], 0.68),
        ("M6 desconoce servicios", metric_lookup["Desconoce servicios disponibles"], 0.44),
    ]

    with PdfPages(OUTPUT) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        fig.patch.set_facecolor("white")
        fig.text(
            0.07,
            0.955,
            "Entregable 1 Diagnostico AURA Care",
            fontsize=18,
            fontweight="bold",
            family="Times New Roman",
            va="top",
        )
        fig.text(
            0.07,
            0.925,
            "Ciudad AETHERA - Concurso Binacional de Innovacion Chile Peru 2026",
            fontsize=10.5,
            family="Times New Roman",
            va="top",
        )

        y = 0.875
        y = add_block(
            fig,
            0.07,
            y,
            "Misiones elegidas",
            "AURA Care aborda M1 estres y ansiedad, M5 estigma y baja busqueda de ayuda, y M6 barreras de acceso. "
            "M2 presion academica se usa como evidencia contextual porque la sobrecarga de evaluaciones aparece asociada a menor asistencia y mas alertas academicas.",
            width=105,
        )
        y = add_block(
            fig,
            0.07,
            y,
            "Problema fundamentado con Data Pack",
            f"D1 muestra {pct(metric_lookup['Sintomatologia ansiosa moderada-alta'])} de estudiantes con sintomatologia ansiosa moderada-alta "
            f"({int(evidence['symptomatic_count']):,} de {int(evidence['survey_count']):,} respuestas). Entre estudiantes con sintomatologia, "
            f"{pct(metric_lookup['Sintomatologia y nunca consulto apoyo'])} nunca consulto apoyo segun D1 y no registra evento en D2. "
            f"Ademas, {pct(metric_lookup['Desconoce servicios disponibles'])} declara desconocer servicios y D2 registra una espera promedio de "
            f"{metric_lookup['Espera media en servicios de apoyo']:.1f} dias, equivalente a 6 semanas.",
            width=105,
        )

        ax = fig.add_axes([0.13, 0.43, 0.74, 0.22])
        labels = [row[0] for row in bars]
        values = [row[1] for row in bars]
        baselines = [row[2] for row in bars]
        y_pos = range(len(labels))
        ax.barh(list(y_pos), values, color="#1f4e79", label="Data Pack")
        ax.scatter(baselines, list(y_pos), color="#b03a2e", label="Linea base", zorder=5)
        ax.set_yticks(list(y_pos), labels, fontsize=9)
        ax.set_xlim(0, 0.8)
        ax.set_xlabel("Proporcion")
        ax.set_title("")
        ax.legend(loc="lower right", fontsize=8)
        ax.grid(axis="x", alpha=0.25)
        for i, value in enumerate(values):
            ax.text(value + 0.015, i, pct(value), va="center", fontsize=9)

        y = 0.365
        y = add_block(
            fig,
            0.07,
            y,
            "Evidencia complementaria",
            f"El problema no es solo clinico: tambien es operativo e informacional. D1 indica {pct(evidence['stress_moderate_high'])} con estres moderado/alto; "
            f"quienes reportan ansiedad alta duermen {evidence['sleep_high_anxiety']:.1f} horas promedio frente a {evidence['sleep_low_anxiety']:.1f} horas en ansiedad baja. "
            f"La sobrecarga de evaluaciones alcanza {pct(metric_lookup['Sobrecarga en semanas de evaluacion'])}; al cruzar D1 con D3, los perfiles con sobrecarga tienen "
            f"asistencia promedio de {pct(evidence['attendance_overload_yes'])} frente a {pct(evidence['attendance_overload_no'])} sin sobrecarga, y alertas academicas media/alta de "
            f"{pct(evidence['dropout_alert_overload_yes'])} frente a {pct(evidence['dropout_alert_overload_no'])}.",
            width=105,
            size=9.6,
        )
        add_block(
            fig,
            0.07,
            y,
            "Concepto de solucion",
            "AURA Care es un agente preventivo con RAG y herramientas de analitica. Usa D1, D2, D3 y D7 para priorizar necesidades no clinicas y D6 para recomendar recursos concretos por horario, canal y tipo de servicio. "
            "El agente explica que es IA, entrega orientacion de primer contacto y deriva a apoyo humano cuando la consulta supera su alcance.",
            width=105,
            size=9.6,
        )
        fig.text(0.5, 0.035, "Pagina 1 de 2", ha="center", fontsize=8, family="Times New Roman")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig = plt.figure(figsize=(8.5, 11))
        fig.patch.set_facecolor("white")
        fig.text(
            0.07,
            0.955,
            "AURA Care riesgos eticos y demostracion",
            fontsize=17,
            fontweight="bold",
            family="Times New Roman",
            va="top",
        )
        y = 0.90
        y = add_block(
            fig,
            0.07,
            y,
            "Flujo funcional para el prototipo",
            "1. Cargar Data Pack Oleada 1. 2. Reconstruir indicadores M1, M5 y M6. 3. Calcular un score preventivo no clinico. "
            "4. Recuperar servicios desde D6 con RAG. 5. Generar una respuesta segura con limites explicitos. 6. Derivar a ayuda humana ante crisis o necesidad especializada.",
            width=105,
        )

        risks = [
            (
                "Riesgo de diagnostico automatizado",
                "La salida usa lenguaje preventivo: senales, necesidades y recursos. No clasifica clinicamente ni prescribe tratamiento.",
            ),
            (
                "Riesgo de privacidad",
                "Solo se usan datos sinteticos del Data Pack. No se agregan datos reales ni externos sensibles.",
            ),
            (
                "Riesgo de sesgo",
                "Se revisan brechas por pais, etapa academica, migracion y red de apoyo. Las recomendaciones deben validarse con bienestar.",
            ),
            (
                "Riesgo de respuestas incorrectas",
                "RAG limita respuestas al mapa D6. Cada recomendacion expone servicio, canal, horario y razon de derivacion.",
            ),
            (
                "Riesgo ante crisis",
                "Si aparece lenguaje de crisis o autolesion, la IA deja de recomendar de forma automatizada y prioriza contacto humano.",
            ),
        ]
        fig.text(0.07, y, "Primer analisis de riesgos eticos", fontsize=11.5, fontweight="bold", family="Times New Roman", va="top")
        y -= 0.035
        for risk, mitigation in risks:
            text = wrap(f"{risk}: {mitigation}", 98)
            fig.text(0.09, y, text, fontsize=9.7, family="Times New Roman", va="top", linespacing=1.15)
            y -= 0.023 * (text.count("\n") + 1) + 0.012

        y -= 0.01
        y = add_block(
            fig,
            0.07,
            y,
            "Por que esta estrategia compite bien",
            "La propuesta conecta evidencia dura del Data Pack con una solucion demostrable. Ataca tres misiones de alto impacto, usa los datasets oficiales de Oleada 1, prepara una ruta clara para IA generativa en Entregable 2 y evita la principal causal de descalificacion: sustituir atencion profesional de salud mental.",
            width=105,
        )
        y = add_block(
            fig,
            0.07,
            y,
            "Demo prevista para Entregable 2",
            "En el video se mostrara el notebook ejecutando la carga de D1-D7, los indicadores, una lista priorizada de perfiles sinteticos y tres conversaciones: sobrecarga en evaluaciones, baja red de apoyo y crisis. En cada caso se vera la recuperacion RAG de D6 y la respuesta responsable del agente.",
            width=105,
        )
        add_block(
            fig,
            0.07,
            y,
            "Limite declarado",
            "AURA Care no determina si una persona tiene ansiedad, depresion u otro cuadro. No decide cupos clinicos ni reemplaza a bienestar. Su aporte es reducir desconocimiento, ordenar el primer contacto y entregar evidencia agregada para acciones preventivas.",
            width=105,
        )
        fig.text(0.5, 0.035, "Pagina 2 de 2", ha="center", fontsize=8, family="Times New Roman")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

    return OUTPUT


if __name__ == "__main__":
    print(make_pdf().resolve())
