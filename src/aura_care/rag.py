from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RetrievedService:
    service_id: str
    name: str
    mission: str
    description: str
    access: str
    score: float


class ServiceRAG:
    def __init__(self, services: pd.DataFrame):
        self.services = services.reset_index(drop=True).copy()
        docs = self.services.apply(_service_document, axis=1)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", lowercase=True)
        self.matrix = self.vectorizer.fit_transform(docs)

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedService]:
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).ravel()
        order = scores.argsort()[::-1][:top_k]
        results = []
        for idx in order:
            row = self.services.iloc[int(idx)]
            results.append(
                RetrievedService(
                    service_id=str(row.get("service_id", "")),
                    name=str(row.get("name", "")),
                    mission=_infer_mission(row),
                    description=str(row.get("description", "")),
                    access=_access_text(row),
                    score=round(float(scores[idx]), 3),
                )
            )
        return results


def _service_document(row: pd.Series) -> str:
    fields = [
        "service_id",
        "name",
        "mission",
        "audience",
        "description",
        "access",
        "tags",
        "service_type",
        "district_id",
        "schedule",
        "channels",
        "eligibility",
        "referral_information",
    ]
    text = " ".join(str(row.get(field, "")) for field in fields)
    service_type = str(row.get("service_type", ""))
    enrichments = {
        "counseling": "orientacion consejeria ansiedad estres apoyo bienestar derivacion M1 M6",
        "peer_support": "pares red apoyo aislamiento migrante estigma primer contacto M4 M5",
        "career_guidance": "trayectoria empleabilidad carrera orientacion academica preocupacion futuro M3",
    }
    return f"{text} {enrichments.get(service_type, '')}"


def _access_text(row: pd.Series) -> str:
    if "access" in row and pd.notna(row.get("access")):
        return str(row.get("access"))
    schedule = row.get("schedule", "horario no informado")
    channels = row.get("channels", "canal no informado")
    referral = row.get("referral_information", "derivacion institucional")
    capacity = row.get("capacity", "sin capacidad informada")
    return f"Horario: {schedule}. Canales: {channels}. Capacidad semanal: {capacity}. Derivacion: {referral}."


def _infer_mission(row: pd.Series) -> str:
    if "mission" in row and pd.notna(row.get("mission")):
        return str(row.get("mission"))
    service_type = str(row.get("service_type", ""))
    return {
        "counseling": "M1,M6",
        "peer_support": "M4,M5",
        "career_guidance": "M3",
    }.get(service_type, "M1,M5,M6")
