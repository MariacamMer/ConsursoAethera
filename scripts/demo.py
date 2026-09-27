from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from aura_care import AuraCareAgent, build_dashboard_metrics, ensure_demo_data, score_preventive_needs
from aura_care.analytics import build_evidence_summary, segment_summary


def _display_value(value: float, fmt: str) -> str:
    if fmt == "percent":
        return f"{value:.1%}"
    if fmt == "days":
        return f"{value:.1f} dias ({value / 7:.1f} semanas)"
    if fmt == "weeks":
        return f"{value:.1f} semanas"
    return f"{value:.2f}"


def main() -> None:
    pack = ensure_demo_data()
    metrics = build_dashboard_metrics(pack.students, pack.service_use)
    scored = score_preventive_needs(pack.students, pack.service_use, pack.academic)
    evidence = build_evidence_summary(pack.students, pack.service_use, pack.academic, pack.calendar)
    agent = AuraCareAgent(scored, pack.services)

    print("\nAURA Care PMV funcional con Data Pack Oleada 1")
    print("=" * 82)
    print(f"Fuente de datos: {pack.source}")
    print(
        f"D1={len(pack.students):,} respuestas | D2={len(pack.service_use):,} eventos | "
        f"D3={len(pack.academic):,} registros | D6={len(pack.services):,} servicios | "
        f"D7={len(pack.calendar):,} eventos"
    )

    print("\nIndicadores reconstruidos desde el Data Pack")
    shown = metrics.copy()
    shown["valor"] = shown.apply(lambda r: _display_value(r["value"], r["format"]), axis=1)
    shown["linea_base"] = shown.apply(lambda r: _display_value(r["baseline"], r["format"]), axis=1)
    print(shown[["mission", "metric", "valor", "linea_base", "evidence"]].to_string(index=False))

    print("\nEvidencia adicional para el diagnostico")
    print(f"- Estres moderado/alto: {evidence['stress_moderate_high']:.1%}")
    print(
        f"- Sueno promedio con ansiedad alta vs baja: "
        f"{evidence['sleep_high_anxiety']:.1f}h vs {evidence['sleep_low_anxiety']:.1f}h"
    )
    print(f"- Sin red de apoyo: {evidence['support_none']:.1%}")
    print(f"- Sin red entre migrantes internos: {evidence['support_none_migrant']:.1%}")
    print(
        f"- Asistencia promedio con sobrecarga vs sin sobrecarga: "
        f"{evidence['attendance_overload_yes']:.1%} vs {evidence['attendance_overload_no']:.1%}"
    )
    print(
        f"- Alerta academica media/alta con sobrecarga vs sin sobrecarga: "
        f"{evidence['dropout_alert_overload_yes']:.1%} vs {evidence['dropout_alert_overload_no']:.1%}"
    )

    print("\nTop 5 perfiles sinteticos priorizados")
    cols = [
        "student_id",
        "country_context",
        "academic_stage",
        "migration_status",
        "anxiety_band",
        "stress_band",
        "support_network",
        "services_awareness",
        "previous_support_use",
        "preventive_need_score",
        "priority_band",
    ]
    print(scored[cols].head(5).to_string(index=False))

    print("\nSegmentos priorizados")
    print(segment_summary(scored).head(8).to_string(index=False))

    print("\nDemo agente AURA Care")
    print("-" * 82)
    case_ids = scored.head(3)["student_id"].tolist()
    cases = [
        (case_ids[0], "Estoy muy sobrepasado con evaluaciones y no se a que servicio acudir."),
        (case_ids[1], "Soy estudiante migrante y me siento solo, me da verguenza pedir ayuda."),
        (case_ids[2], "Estoy en crisis y pienso en hacerme dano."),
    ]
    for student_id, message in cases:
        response = agent.answer(message, student_id=student_id)
        print(f"\nCaso {student_id}: {message}")
        print(f"Necesidad interpretada: {response.interpreted_need}")
        print(response.answer)
        print("Recursos:")
        for service in response.recommended_services:
            print(f"  - {service.name} [{service.mission}] score={service.score}: {service.access}")


if __name__ == "__main__":
    main()
