from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import RISK_KEYWORDS
from .rag import RetrievedService, ServiceRAG


@dataclass
class AgentResponse:
    user_message: str
    is_crisis: bool
    interpreted_need: str
    answer: str
    recommended_services: list[RetrievedService]
    responsible_ai_notes: list[str]

    def as_markdown(self) -> str:
        services = "\n".join(
            f"- **{svc.name}** ({svc.mission}, score RAG {svc.score}): {svc.access}"
            for svc in self.recommended_services
        )
        notes = "\n".join(f"- {note}" for note in self.responsible_ai_notes)
        return (
            "### Respuesta AURA Care\n\n"
            f"{self.answer}\n\n"
            "### Recursos sugeridos\n"
            f"{services}\n\n"
            "### IA responsable\n"
            f"{notes}"
        )


class AuraCareAgent:
    """Agente preventivo con RAG y reglas de seguridad."""

    def __init__(self, students: pd.DataFrame, services: pd.DataFrame):
        self.students = students
        self.rag = ServiceRAG(services)
        self._student_ids = set(students["student_id"]) if "student_id" in students.columns else set()

    def answer(self, message: str, student_id: str | None = None) -> AgentResponse:
        normalized = message.lower()
        crisis = any(keyword in normalized for keyword in RISK_KEYWORDS)
        profile = self._profile_text(student_id)

        if crisis:
            query = f"{message} crisis riesgo ayuda inmediata consejeria orientacion humano"
            services = self.rag.retrieve(query, top_k=2)
            answer = (
                "Soy AURA Care, una IA de orientacion preventiva, no un servicio de emergencia ni un terapeuta. "
                "Por lo que escribes, lo mas importante es contactar ahora a una persona o canal humano de ayuda. "
                "Usa los canales institucionales de bienestar, seguridad universitaria o servicios de emergencia locales. "
                "Si estas con alguien de confianza, pide que se quede contigo mientras haces ese contacto."
            )
            need = "posible situacion de crisis o riesgo que excede el alcance de la IA"
        else:
            query = f"{message} {profile}"
            services = self.rag.retrieve(query, top_k=3)
            need = self._interpret_need(normalized, profile)
            answer = self._compose_safe_answer(need, services, profile)

        notes = [
            "La respuesta informa explicitamente que AURA Care es IA.",
            "No entrega diagnostico, tratamiento ni clasificacion clinica.",
            "Las recomendaciones se basan en recursos del Data Pack recuperados por RAG.",
            "Si aparece riesgo o crisis, se prioriza derivacion a ayuda humana.",
        ]
        return AgentResponse(
            user_message=message,
            is_crisis=crisis,
            interpreted_need=need,
            answer=answer,
            recommended_services=services,
            responsible_ai_notes=notes,
        )

    def _profile_text(self, student_id: str | None) -> str:
        if not student_id or student_id not in self._student_ids:
            return ""
        row = self.students.loc[self.students["student_id"] == student_id].iloc[0]
        if "anxiety_band" in row.index:
            return (
                f"perfil {row['country_context']} etapa {row['academic_stage']} "
                f"migracion {row['migration_status']} modalidad {row['study_mode']} "
                f"ansiedad {row['anxiety_band']} estres {row['stress_band']} "
                f"sobrecarga evaluacion {row['evaluation_overload']} red apoyo {row['support_network']} "
                f"conocimiento servicios {row['services_awareness']} uso previo apoyo {row['previous_support_use']} "
                f"score preventivo {row.get('preventive_need_score', 'NA')} prioridad {row.get('priority_band', 'NA')}"
            )
        return (
            f"perfil facultad {row['faculty']} ciclo {row['cycle']} "
            f"carga academica {row['academic_load_score']} soledad {row['loneliness_score']} "
            f"conoce servicios {row['knows_services']} red apoyo {row['support_network']} "
            f"busco ayuda {row['help_sought']}"
        )

    def _interpret_need(self, normalized: str, profile: str) -> str:
        if "evaluacion" in normalized or "examen" in normalized or "sobrecarga" in normalized:
            return "sobrecarga academica y necesidad de orientacion preventiva para semanas de evaluacion"
        if "solo" in normalized or "sola" in normalized or "aislado" in normalized or "migrante" in normalized:
            return "aislamiento o red de apoyo insuficiente con posible barrera de primer contacto"
        if "no se" in normalized or "servicio" in normalized or "donde" in normalized:
            return "desconocimiento de servicios y barrera de acceso"
        if "futuro" in normalized or "empleabilidad" in normalized or "trabajo" in normalized:
            return "preocupacion por trayectoria y empleabilidad"
        if profile:
            return "necesidad preventiva estimada a partir del perfil sintetico y la consulta"
        return "orientacion general de bienestar universitario"

    def _compose_safe_answer(self, need: str, services: list[RetrievedService], profile: str) -> str:
        primary = services[0] if services else None
        service_text = primary.name if primary else "un recurso de bienestar universitario"
        access_text = primary.access if primary else "consulta el mapa institucional de servicios"
        profile_hint = (
            " Tambien considere el perfil sintetico del Data Pack para priorizar una ruta de apoyo."
            if profile
            else ""
        )
        return (
            "Soy AURA Care, una IA de orientacion preventiva. No puedo diagnosticar ni reemplazar a un profesional, "
            f"pero puedo ayudarte a ordenar el siguiente paso. Interpreto tu necesidad como: {need}.{profile_hint} "
            f"Para partir, revisaria {service_text}. Acceso sugerido: {access_text} "
            "Si la situacion aumenta, si hay riesgo o si necesitas apoyo especializado, contacta a bienestar "
            "universitario para hablar con una persona."
        )
