from __future__ import annotations

import pandas as pd

from .config import MISSION_BASELINES


def build_dashboard_metrics(students: pd.DataFrame, service_use: pd.DataFrame) -> pd.DataFrame:
    if "anxiety_band" in students.columns:
        return _official_dashboard_metrics(students, service_use)
    return _synthetic_dashboard_metrics(students, service_use)


def _official_dashboard_metrics(students: pd.DataFrame, service_use: pd.DataFrame) -> pd.DataFrame:
    symptomatic = students["anxiety_band"].isin(["moderate", "high"])
    students_with_event = set(service_use["student_id"])
    never_used = students["previous_support_use"].eq("never")
    no_recorded_event = ~students["student_id"].isin(students_with_event)
    m5_gap = (symptomatic & never_used & no_recorded_event).sum() / symptomatic.sum()
    wait_days = service_use["wait_days"].mean()
    rows = [
        {
            "mission": "M1",
            "metric": "Sintomatologia ansiosa moderada-alta",
            "value": symptomatic.mean(),
            "baseline": MISSION_BASELINES["M1_ansiedad_moderada_alta"],
            "format": "percent",
            "evidence": f"{symptomatic.sum():,} de {len(students):,} respuestas D1",
        },
        {
            "mission": "M5",
            "metric": "Sintomatologia y nunca consulto apoyo",
            "value": m5_gap,
            "baseline": MISSION_BASELINES["M5_sintomatologia_sin_consulta"],
            "format": "percent",
            "evidence": "D1 previous_support_use=never y ausencia de evento D2",
        },
        {
            "mission": "M6",
            "metric": "Desconoce servicios disponibles",
            "value": students["services_awareness"].eq("unaware").mean(),
            "baseline": MISSION_BASELINES["M6_desconoce_servicios"],
            "format": "percent",
            "evidence": "D1 services_awareness=unaware",
        },
        {
            "mission": "M6",
            "metric": "Espera media en servicios de apoyo",
            "value": wait_days,
            "baseline": MISSION_BASELINES["M6_espera_consejeria_dias"],
            "format": "days",
            "evidence": f"{len(service_use):,} eventos D2 con wait_days",
        },
        {
            "mission": "M2",
            "metric": "Sobrecarga en semanas de evaluacion",
            "value": students["evaluation_overload"].eq("yes").mean(),
            "baseline": MISSION_BASELINES["M2_sobrecarga_evaluaciones"],
            "format": "percent",
            "evidence": "Variable contextual usada para explicar M1",
        },
    ]
    return pd.DataFrame(rows)


def _synthetic_dashboard_metrics(students: pd.DataFrame, service_use: pd.DataFrame) -> pd.DataFrame:
    symptomatic = students["anxious_symptoms_moderate_high"]
    symptomatic_count = int(symptomatic.sum())
    non_consult = (~students.loc[symptomatic, "help_sought"]).mean() if symptomatic_count else 0.0
    counseling = service_use[service_use["service"] == "consejeria"]
    avg_wait = counseling["wait_weeks"].mean() if not counseling.empty else 0.0
    return pd.DataFrame(
        [
            {
                "mission": "M1",
                "metric": "Estudiantes con senales ansiosas moderadas-altas",
                "value": students["anxious_symptoms_moderate_high"].mean(),
                "baseline": MISSION_BASELINES["M1_ansiedad_moderada_alta"],
                "format": "percent",
                "evidence": "dataset sintetico local",
            },
            {
                "mission": "M5",
                "metric": "Estudiantes con sintomatologia que no consultaron apoyo",
                "value": non_consult,
                "baseline": MISSION_BASELINES["M5_sintomatologia_sin_consulta"],
                "format": "percent",
                "evidence": "dataset sintetico local",
            },
            {
                "mission": "M6",
                "metric": "Estudiantes que desconocen servicios",
                "value": (~students["knows_services"]).mean(),
                "baseline": MISSION_BASELINES["M6_desconoce_servicios"],
                "format": "percent",
                "evidence": "dataset sintetico local",
            },
            {
                "mission": "M6",
                "metric": "Espera media en consejeria",
                "value": avg_wait,
                "baseline": MISSION_BASELINES["M6_espera_consejeria_semanas"],
                "format": "weeks",
                "evidence": "dataset sintetico local",
            },
        ]
    )


def score_preventive_needs(
    students: pd.DataFrame,
    service_use: pd.DataFrame | None = None,
    academic: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if "anxiety_band" in students.columns:
        return _score_official(students, service_use, academic)
    return _score_synthetic(students)


def _score_official(
    students: pd.DataFrame,
    service_use: pd.DataFrame | None,
    academic: pd.DataFrame | None,
) -> pd.DataFrame:
    scored = students.copy()
    anxiety_map = {"low": 5, "mild": 22, "moderate": 52, "high": 80}
    stress_map = {"low": 5, "moderate": 44, "high": 76}
    support_penalty = scored["support_network"].map({"adequate": 0, "limited": 12, "none": 24}).fillna(8)
    awareness_penalty = scored["services_awareness"].eq("unaware").astype(int) * 14
    overload_penalty = scored["evaluation_overload"].eq("yes").astype(int) * 10
    previous_support_penalty = scored["previous_support_use"].eq("never").astype(int) * 8

    if service_use is not None and not service_use.empty:
        no_recent_event = ~scored["student_id"].isin(set(service_use["student_id"]))
    else:
        no_recent_event = pd.Series(True, index=scored.index)

    if academic is not None and not academic.empty:
        academic_features = (
            academic.groupby("student_id")
            .agg(
                avg_attendance=("attendance_rate", "mean"),
                avg_grade_change=("grade_change", "mean"),
                dropout_medium_high=("dropout_alert", lambda s: s.isin(["medium", "high"]).mean()),
                avg_credit_load=("credit_load", "mean"),
                avg_evaluation_count=("evaluation_count", "mean"),
            )
            .reset_index()
        )
        scored = scored.merge(academic_features, on="student_id", how="left")
    else:
        scored["avg_attendance"] = 0.85
        scored["avg_grade_change"] = 0.0
        scored["dropout_medium_high"] = 0.0
        scored["avg_credit_load"] = 24.0
        scored["avg_evaluation_count"] = 5.0

    attendance_penalty = (1 - scored["avg_attendance"].fillna(0.85)).clip(0, 1) * 18
    dropout_penalty = scored["dropout_medium_high"].fillna(0) * 12
    load_penalty = ((scored["avg_credit_load"].fillna(24) - 24).clip(lower=0) / 8) * 8
    eval_penalty = ((scored["avg_evaluation_count"].fillna(5) - 5).clip(lower=0) / 5) * 8
    no_help_gap = (
        scored["anxiety_band"].isin(["moderate", "high"])
        & scored["previous_support_use"].eq("never")
        & no_recent_event
    ).astype(int) * 16

    score = (
        scored["anxiety_band"].map(anxiety_map).fillna(10) * 0.30
        + scored["stress_band"].map(stress_map).fillna(10) * 0.24
        + support_penalty
        + awareness_penalty
        + overload_penalty
        + previous_support_penalty
        + attendance_penalty
        + dropout_penalty
        + load_penalty
        + eval_penalty
        + no_help_gap
    )
    scored["preventive_need_score"] = score.clip(0, 100).round(1)
    scored["priority_band"] = pd.cut(
        scored["preventive_need_score"],
        bins=[-1, 44, 69, 100],
        labels=["orientacion_general", "apoyo_preventivo", "derivacion_recomendada"],
    ).astype(str)
    scored["has_recent_support_event"] = ~no_recent_event
    return scored.sort_values("preventive_need_score", ascending=False)


def _score_synthetic(students: pd.DataFrame) -> pd.DataFrame:
    scored = students.copy()
    support_penalty = scored["support_network"].map({"alta": 0, "media": 8, "baja": 18}).fillna(8)
    access_penalty = (~scored["knows_services"]).astype(int) * 14
    help_gap = (scored["anxious_symptoms_moderate_high"] & ~scored["help_sought"]).astype(int) * 16
    migrant_penalty = scored["migrant_internal"].astype(int) * 5
    score = (
        0.32 * scored["academic_load_score"]
        + 0.30 * scored["loneliness_score"]
        + 0.20 * scored["anxiety_score"]
        + support_penalty
        + access_penalty
        + help_gap
        + migrant_penalty
    )
    scored["preventive_need_score"] = score.clip(0, 100).round(1)
    scored["priority_band"] = pd.cut(
        scored["preventive_need_score"],
        bins=[-1, 44, 69, 100],
        labels=["orientacion_general", "apoyo_preventivo", "derivacion_recomendada"],
    ).astype(str)
    return scored.sort_values("preventive_need_score", ascending=False)


def segment_summary(scored_students: pd.DataFrame) -> pd.DataFrame:
    if "country_context" in scored_students.columns:
        group_cols = ["country_context", "academic_stage", "priority_band"]
        symptomatic_col = scored_students["anxiety_band"].isin(["moderate", "high"])
        aware_col = scored_students["services_awareness"].eq("aware")
        support_gap = scored_students["support_network"].eq("none")
        help_col = scored_students["previous_support_use"].ne("never") | scored_students.get(
            "has_recent_support_event", False
        )
    else:
        group_cols = ["faculty", "priority_band"]
        symptomatic_col = scored_students["anxious_symptoms_moderate_high"]
        aware_col = scored_students["knows_services"]
        support_gap = scored_students["support_network"].eq("baja")
        help_col = scored_students["help_sought"]

    working = scored_students.copy()
    working["_symptomatic"] = symptomatic_col
    working["_aware"] = aware_col
    working["_support_gap"] = support_gap
    working["_help"] = help_col

    rows = []
    for keys, group in working.groupby(group_cols, observed=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        symptomatic = group[group["_symptomatic"]]
        no_help = 0.0 if symptomatic.empty else float((~symptomatic["_help"]).mean())
        row = {col: key for col, key in zip(group_cols, keys)}
        row.update(
            {
                "students": len(group),
                "avg_need_score": group["preventive_need_score"].mean(),
                "unknown_services": float((~group["_aware"]).mean()),
                "support_gap": float(group["_support_gap"].mean()),
                "no_help_among_symptoms": no_help,
            }
        )
        rows.append(row)
    return (
        pd.DataFrame(rows)
        .sort_values(["avg_need_score", "students"], ascending=False)
        .reset_index(drop=True)
    )


def build_evidence_summary(
    students: pd.DataFrame,
    service_use: pd.DataFrame,
    academic: pd.DataFrame,
    calendar: pd.DataFrame,
) -> dict[str, float]:
    metrics = build_dashboard_metrics(students, service_use)
    values = {row["metric"]: row["value"] for _, row in metrics.iterrows()}
    if "anxiety_band" not in students.columns:
        return values

    symptomatic = students["anxiety_band"].isin(["moderate", "high"])
    values["stress_moderate_high"] = students["stress_band"].isin(["moderate", "high"]).mean()
    values["sleep_high_anxiety"] = students.loc[students["anxiety_band"].eq("high"), "sleep_hours"].mean()
    values["sleep_low_anxiety"] = students.loc[students["anxiety_band"].eq("low"), "sleep_hours"].mean()
    values["support_none"] = students["support_network"].eq("none").mean()
    values["support_none_migrant"] = students.loc[
        students["migration_status"].eq("internal_migrant"), "support_network"
    ].eq("none").mean()
    if not academic.empty:
        ag = academic.groupby("student_id").agg(
            attendance_rate=("attendance_rate", "mean"),
            dropout_medium_high=("dropout_alert", lambda s: s.isin(["medium", "high"]).mean()),
        )
        merged = students[["student_id", "evaluation_overload"]].merge(ag, on="student_id", how="left")
        overloaded = merged["evaluation_overload"].eq("yes")
        values["attendance_overload_yes"] = merged.loc[overloaded, "attendance_rate"].mean()
        values["attendance_overload_no"] = merged.loc[~overloaded, "attendance_rate"].mean()
        values["dropout_alert_overload_yes"] = merged.loc[overloaded, "dropout_medium_high"].mean()
        values["dropout_alert_overload_no"] = merged.loc[~overloaded, "dropout_medium_high"].mean()
    if not calendar.empty and "evaluation_intensity" in calendar.columns:
        values["high_intensity_evaluation_events"] = int((calendar["evaluation_intensity"] >= 2).sum())
    values["symptomatic_count"] = int(symptomatic.sum())
    values["survey_count"] = int(len(students))
    values["support_event_count"] = int(len(service_use))
    return values
