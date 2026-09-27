from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .config import DATA_DIR, PROJECT_ROOT


@dataclass(frozen=True)
class DataPack:
    students: pd.DataFrame
    service_use: pd.DataFrame
    academic: pd.DataFrame
    services: pd.DataFrame
    calendar: pd.DataFrame
    source: str


def find_official_data_dir(project_root: Path = PROJECT_ROOT) -> Path | None:
    candidates = [p for p in project_root.rglob("DataPack_Aethera_Oleada1") if p.is_dir()]
    return candidates[0] if candidates else None


def ensure_demo_data(
    data_dir: Path = DATA_DIR,
    seed: int = 42,
    n_students: int = 640,
    overwrite: bool = False,
) -> DataPack:
    official = find_official_data_dir()
    if official is not None:
        return load_data_pack(official)

    data_dir.mkdir(parents=True, exist_ok=True)
    expected = [
        data_dir / "students.csv",
        data_dir / "service_use.csv",
        data_dir / "services.csv",
        data_dir / "calendar.csv",
    ]
    if overwrite or not all(path.exists() for path in expected):
        generate_demo_data(data_dir=data_dir, seed=seed, n_students=n_students)
    return load_data_pack(data_dir)


def load_data_pack(data_dir: Path = DATA_DIR) -> DataPack:
    data_dir = Path(data_dir)
    if (data_dir / "D1_wellbeing_survey.csv").exists():
        return _load_official_pack(data_dir)

    return DataPack(
        students=pd.read_csv(data_dir / "students.csv"),
        service_use=pd.read_csv(data_dir / "service_use.csv"),
        academic=pd.DataFrame(),
        services=pd.read_csv(data_dir / "services.csv"),
        calendar=pd.read_csv(data_dir / "calendar.csv"),
        source="synthetic_demo",
    )


def _load_official_pack(data_dir: Path) -> DataPack:
    return DataPack(
        students=pd.read_csv(data_dir / "D1_wellbeing_survey.csv"),
        service_use=pd.read_csv(data_dir / "D2_support_services.csv"),
        academic=pd.read_csv(data_dir / "D3_academic_trajectory.csv"),
        services=_load_services_geojson(data_dir / "D6_services_map.geojson"),
        calendar=pd.read_csv(data_dir / "D7_calendar.csv"),
        source="official_oleada_1",
    )


def _load_services_geojson(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)

    rows = []
    for feature in payload.get("features", []):
        props = dict(feature.get("properties", {}))
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates") or [None, None]
        props["longitude"] = coords[0]
        props["latitude"] = coords[1]
        props["channels"] = ",".join(props.get("channels", []))
        rows.append(props)

    services = pd.DataFrame(rows)
    if not services.empty:
        services["description"] = services.apply(
            lambda row: (
                f"{row.get('name')} es un servicio ficticio de tipo {row.get('service_type')} "
                f"en {row.get('district_id')}, con horario {row.get('schedule')}, capacidad semanal "
                f"{row.get('capacity')} y canales {row.get('channels')}. "
                f"Derivacion: {row.get('referral_information')}."
            ),
            axis=1,
        )
    return services


def generate_demo_data(data_dir: Path = DATA_DIR, seed: int = 42, n_students: int = 640) -> None:
    rng = np.random.default_rng(seed)
    student_ids = [f"AET-{i:04d}" for i in range(1, n_students + 1)]
    faculties = np.array(["Ingenieria", "Salud", "Educacion", "Negocios", "Humanidades", "Ciencias"])
    countries = np.array(["Chile", "Peru"])
    cycles = np.arange(1, 11)

    country = rng.choice(countries, size=n_students, p=[0.52, 0.48])
    faculty = rng.choice(faculties, size=n_students, p=[0.23, 0.18, 0.16, 0.16, 0.14, 0.13])
    cycle = rng.choice(cycles, size=n_students)
    migrant_internal = rng.binomial(1, 0.24, size=n_students).astype(bool)
    works_while_studying = rng.binomial(1, 0.36, size=n_students).astype(bool)
    support_network = rng.choice(["alta", "media", "baja"], size=n_students, p=[0.31, 0.38, 0.31])
    knows_services = rng.binomial(1, 0.56, size=n_students).astype(bool)

    academic_load = np.clip(rng.normal(58, 18, size=n_students), 0, 100)
    academic_load += np.where(works_while_studying, 8, 0)
    academic_load += np.where(np.isin(faculty, ["Ingenieria", "Salud"]), 6, 0)
    academic_load = np.clip(academic_load, 0, 100)

    loneliness = np.clip(rng.normal(42, 21, size=n_students), 0, 100)
    loneliness += np.where(migrant_internal, 12, 0)
    loneliness += np.where(support_network == "baja", 16, 0)
    loneliness -= np.where(support_network == "alta", 10, 0)
    loneliness = np.clip(loneliness, 0, 100)

    anxiety_score = (
        0.44 * academic_load
        + 0.36 * loneliness
        + rng.normal(0, 13, size=n_students)
        + np.where(cycle >= 8, 5, 0)
    )
    anxiety_score = np.clip(anxiety_score, 0, 100)
    threshold = np.quantile(anxiety_score, 0.59)
    anxious_moderate_high = anxiety_score >= threshold

    p_help = np.where(anxious_moderate_high, 0.28, 0.18)
    p_help += np.where(knows_services, 0.09, -0.09)
    p_help += np.where(support_network == "alta", 0.05, 0)
    p_help = np.clip(p_help, 0.03, 0.75)
    help_sought = rng.binomial(1, p_help).astype(bool)

    students = pd.DataFrame(
        {
            "student_id": student_ids,
            "country": country,
            "faculty": faculty,
            "cycle": cycle,
            "migrant_internal": migrant_internal,
            "works_while_studying": works_while_studying,
            "support_network": support_network,
            "knows_services": knows_services,
            "academic_load_score": np.round(academic_load, 1),
            "loneliness_score": np.round(loneliness, 1),
            "anxiety_score": np.round(anxiety_score, 1),
            "anxious_symptoms_moderate_high": anxious_moderate_high,
            "help_sought": help_sought,
        }
    )

    service_rows = []
    service_names = ["consejeria", "taller_estres", "mentoria_pares", "orientacion_academica"]
    for sid, sought in zip(student_ids, help_sought):
        if not sought:
            continue
        service = rng.choice(service_names, p=[0.46, 0.22, 0.18, 0.14])
        wait = max(0.5, rng.normal(6.0 if service == "consejeria" else 2.1, 1.8))
        service_rows.append(
            {
                "student_id": sid,
                "service": service,
                "wait_weeks": round(float(wait), 1),
                "channel": rng.choice(["presencial", "remoto", "hibrido"], p=[0.36, 0.34, 0.30]),
                "completed_first_contact": bool(rng.binomial(1, 0.74)),
            }
        )
    service_use = pd.DataFrame(service_rows)

    services = pd.DataFrame(
        [
            {
                "service_id": "S1",
                "name": "Consejeria universitaria",
                "mission": "M1,M6",
                "audience": "Estudiantes que requieren apoyo humano especializado",
                "description": "Atencion por profesionales de bienestar. No es un servicio de emergencia. Permite agendar una primera entrevista y evaluar derivacion.",
                "access": "Agenda online o unidad de bienestar. Espera media de referencia: 6 semanas.",
                "tags": "ansiedad estres apoyo humano consejeria derivacion",
            },
            {
                "service_id": "S2",
                "name": "Taller breve de manejo de estres academico",
                "mission": "M1",
                "audience": "Estudiantes con sobrecarga en semanas de evaluacion",
                "description": "Sesiones grupales de orientacion preventiva sobre planificacion, pausas, habitos de estudio y busqueda temprana de apoyo.",
                "access": "Inscripcion semanal con cupos abiertos por facultad.",
                "tags": "estres evaluaciones sobrecarga taller planificacion",
            },
            {
                "service_id": "S3",
                "name": "Mentoria de pares AETHERA",
                "mission": "M4,M5",
                "audience": "Estudiantes que se sienten aislados o no saben por donde empezar",
                "description": "Acompanamiento por estudiantes mentores capacitados para orientar sobre vida universitaria y recursos disponibles.",
                "access": "Formulario simple sin requisito clinico.",
                "tags": "aislamiento pares migrante red apoyo estigma",
            },
            {
                "service_id": "S4",
                "name": "Mapa de servicios de bienestar",
                "mission": "M5,M6",
                "audience": "Estudiantes que desconocen canales de apoyo",
                "description": "Directorio de beneficios, horarios, canales remotos, talleres, consejeria, orientacion academica y preguntas frecuentes.",
                "access": "Disponible 24/7 en portal universitario.",
                "tags": "desconocimiento servicios acceso informacion bienestar",
            },
            {
                "service_id": "S5",
                "name": "Orientacion academica preventiva",
                "mission": "M1,M2,M6",
                "audience": "Estudiantes con alta carga, ausentismo o dificultad para organizar evaluaciones",
                "description": "Apoyo para ordenar calendario, priorizar evaluaciones y coordinar alternativas institucionales cuando corresponde.",
                "access": "Solicitud por escuela o bienestar estudiantil.",
                "tags": "academico carga evaluaciones ausentismo organizacion",
            },
            {
                "service_id": "S6",
                "name": "Ruta de ayuda inmediata",
                "mission": "M1,M6",
                "audience": "Situaciones de crisis o riesgo",
                "description": "Canales humanos de urgencia definidos por la institucion. AURA Care debe entregar estos canales cuando una consulta excede su alcance.",
                "access": "Contacto directo con bienestar, seguridad universitaria o servicios de emergencia locales.",
                "tags": "crisis emergencia riesgo ayuda inmediata humano",
            },
        ]
    )

    calendar = pd.DataFrame(
        [
            {"week": 1, "period": "inicio_semestre", "event": "Induccion y matricula", "pressure_level": 25},
            {"week": 4, "period": "primeras_evaluaciones", "event": "Controles y trabajos iniciales", "pressure_level": 58},
            {"week": 8, "period": "mitad_semestre", "event": "Pruebas solemnes y entregas", "pressure_level": 82},
            {"week": 12, "period": "pre_finales", "event": "Acumulacion de trabajos", "pressure_level": 76},
            {"week": 15, "period": "finales", "event": "Examenes finales", "pressure_level": 91},
            {"week": 17, "period": "cierre", "event": "Cierre de semestre", "pressure_level": 49},
        ]
    )

    students.to_csv(data_dir / "students.csv", index=False)
    service_use.to_csv(data_dir / "service_use.csv", index=False)
    services.to_csv(data_dir / "services.csv", index=False)
    calendar.to_csv(data_dir / "calendar.csv", index=False)
