from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from make_entregable1_docx import (
    DOCS_DIR,
    R,
    REL,
    W,
    heading,
    image_paragraph,
    make_chart_png,
    p,
    pct,
    table,
    x,
)

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from aura_care import build_dashboard_metrics, ensure_demo_data
from aura_care.analytics import build_evidence_summary


OUTPUT = DOCS_DIR / "entregable_1" / "Propuesta_Integrada_AURA_Care_Entregable_1.docx"


def strong(label: str, text: str) -> list[dict[str, object]]:
    return [
        {"text": label, "b": True, "size": 22},
        {"text": text, "size": 22},
    ]


def build_docx() -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    pack = ensure_demo_data()
    metrics = build_dashboard_metrics(pack.students, pack.service_use)
    evidence = build_evidence_summary(pack.students, pack.service_use, pack.academic, pack.calendar)
    m = {row["metric"]: row["value"] for _, row in metrics.iterrows()}

    chart_path = DOCS_DIR / "entregable_1" / "Entregable_1_indicadores.png"
    chart_bytes = make_chart_png(chart_path, metrics)

    symptomatic_count = int(evidence["symptomatic_count"])
    survey_count = int(evidence["survey_count"])
    wait_days = m["Espera media en servicios de apoyo"]
    wait_weeks = wait_days / 7

    parts = [
        p("Propuesta integrada AURA Care Entregable 1", style="Title", align="center", after=50),
        p(
            "Agente inteligente para la prevencion temprana del deterioro del bienestar universitario",
            align="center",
            italic=True,
            size=20,
            after=50,
        ),
        p(
            "Concurso Binacional de Innovacion Puentes del Futuro Jovenes para la Ciencia y la Innovacion Chile Peru 2026",
            align="center",
            size=19,
            after=80,
        ),
        p("Grupo 9 | Bryan Silva | Maria Camila Mercado | 24 de septiembre de 2026", align="center", size=19, after=100),
        heading("Resumen ejecutivo"),
        p(
            "AURA Care propone un producto minimo viable basado en inteligencia artificial generativa y agentica para Ciudad AETHERA. "
            "La solucion analiza el Data Pack Oleada 1, identifica necesidades preventivas no clinicas y conecta a estudiantes con recursos institucionales de apoyo. "
            "El documento integra la propuesta inicial con los requisitos del Entregable 1: misiones elegidas, evidencia del Data Pack, concepto de solucion y primer analisis de riesgos eticos.",
            after=70,
        ),
        p(
            "La promesa central es reducir la friccion del primer contacto: que un estudiante que no sabe donde pedir ayuda pueda recibir orientacion clara, trazable y segura, mientras las unidades de bienestar observan patrones agregados para tomar decisiones preventivas.",
            after=80,
        ),
        heading("Caso elegido"),
        p(
            [
                {"text": "Caso elegido: ", "b": True, "size": 22},
                {
                    "text": "AURA Care y la prevencion temprana del deterioro del bienestar universitario mediante inteligencia artificial generativa.",
                    "size": 22,
                },
            ],
            after=60,
        ),
        p(
            "AURA Care se dedica a orientar de forma preventiva a estudiantes universitarios en contextos de estres, ansiedad, agotamiento, aislamiento social y baja busqueda de ayuda. "
            "No diagnostica enfermedades mentales, no prescribe tratamientos y no simula ser terapeuta. Funciona como un puente entre la necesidad del estudiante y los servicios humanos disponibles.",
            after=80,
        ),
        heading("Misiones elegidas"),
        table(
            [
                ["Mision", "Problema abordado", "Evidencia base", "Respuesta de AURA Care"],
                [
                    "M1",
                    "Estres y ansiedad",
                    f"{pct(m['Sintomatologia ansiosa moderada-alta'])} con sintomatologia ansiosa moderada alta",
                    "Reconocer senales preventivas y explicar recursos de apoyo sin clasificacion clinica.",
                ],
                [
                    "M5",
                    "Estigma y baja busqueda de ayuda",
                    f"{pct(m['Sintomatologia y nunca consulto apoyo'])} con sintomatologia no consulto apoyo",
                    "Ofrecer un primer contacto discreto, transparente y de baja friccion.",
                ],
                [
                    "M6",
                    "Barreras de acceso",
                    f"{pct(m['Desconoce servicios disponibles'])} desconoce servicios; espera media {wait_weeks:.1f} semanas",
                    "Recomendar rutas disponibles desde D6 y alternativas mientras se accede a consejeria.",
                ],
            ],
            [1000, 2300, 2700, 3600],
        ),
        heading("Evidencia del Data Pack"),
        p(
            "La decision de concentrar el PMV en M1, M5 y M6 se sustenta en indicadores reconstruidos desde los archivos oficiales D1 Encuesta de bienestar, D2 Uso de servicios, D3 Trayectoria academica, D6 Mapa de servicios y D7 Calendario universitario.",
            after=60,
        ),
        table(
            [
                ["Dato reconstruido", "Resultado", "Lectura para el problema"],
                [
                    "Sintomatologia ansiosa moderada alta",
                    f"{symptomatic_count:,} de {survey_count:,} respuestas D1",
                    "El deterioro de bienestar tiene escala suficiente para justificar intervencion preventiva temprana.",
                ],
                [
                    "Brecha de ayuda entre estudiantes con sintomatologia",
                    "D1 previous_support_use=never + ausencia de evento D2",
                    "La necesidad declarada no se transforma automaticamente en busqueda efectiva de apoyo.",
                ],
                [
                    "Desconocimiento y espera",
                    f"{pct(m['Desconoce servicios disponibles'])}; {wait_days:.1f} dias promedio",
                    "El problema combina desinformacion, estigma y friccion operativa.",
                ],
            ],
            [2700, 2600, 4500],
        ),
        p("Figura 1 Indicadores reconstruidos desde D1 y D2 frente a la linea base del concurso.", italic=True, size=19, after=20),
        image_paragraph("rId2", "Entregable_1_indicadores.png", width_in=6.5, height_in=2.25),
        p(
            strong(
                "Hallazgos complementarios. ",
                f"D1 indica {pct(evidence['stress_moderate_high'])} con estres moderado alto; quienes reportan ansiedad alta duermen {evidence['sleep_high_anxiety']:.1f} horas promedio frente a {evidence['sleep_low_anxiety']:.1f} en ansiedad baja. "
                f"Al cruzar D1 con D3, los perfiles con sobrecarga tienen asistencia promedio de {pct(evidence['attendance_overload_yes'])} frente a {pct(evidence['attendance_overload_no'])} sin sobrecarga, y alertas academicas media alta de {pct(evidence['dropout_alert_overload_yes'])} frente a {pct(evidence['dropout_alert_overload_no'])}.",
            ),
            after=70,
        ),
        p("Diseno de solucion y PMV", style="Title", align="center", after=80),
        heading("Preguntas de bienestar universitario"),
        p("1. Que factores academicos y sociales estan asociados con mayores senales de estres estudiantil?", after=30),
        p("2. Que perfiles presentan mas barreras para acceder a servicios de apoyo?", after=30),
        p("3. Que senales tempranas permiten orientar a estudiantes antes de una crisis?", after=30),
        p("4. Que recursos institucionales deben recomendarse segun necesidad, horario y canal?", after=30),
        p("5. Como puede una IA generativa facilitar el primer contacto sin reemplazar la atencion profesional?", after=70),
        heading("Concepto de solucion"),
        p(
            "AURA Care combina analitica de datos, recuperacion aumentada por generacion y reglas de seguridad. "
            "Usa D1, D2, D3 y D7 para detectar necesidades preventivas y D6 para recomendar servicios concretos por canal, horario, tipo de apoyo y pertinencia. "
            "El estudiante recibe una respuesta clara con limites declarados; bienestar recibe indicadores agregados, no diagnosticos individuales.",
            after=70,
        ),
        table(
            [
                ["Componente", "Funcion en el PMV", "Valor para el concurso"],
                ["Analitica preventiva", "Reconstruye indicadores, segmentos y score preventivo no clinico.", "Demuestra uso real del Data Pack desde la primera fase."],
                ["RAG institucional", "Recupera servicios, horarios, canales y criterios desde D6.", "Reduce respuestas inventadas y permite trazabilidad."],
                ["Agente IA", "Conversa, pregunta lo minimo necesario y explica rutas de apoyo.", "Muestra una experiencia funcional de bajo costo."],
                ["Reglas de seguridad", "Bloquea diagnostico, terapia simulada y decisiones clinicas automatizadas.", "Alinea la solucion con IA responsable."],
            ],
            [2100, 3900, 3800],
        ),
        heading("Quien decide"),
        table(
            [
                ["Usuario responsable", "Decision", "Frecuencia"],
                ["Unidad de bienestar universitario", "Identificar brechas generales de necesidad y acceso.", "Mensual"],
                ["Orientadores o profesionales de apoyo", "Validar rutas preventivas y derivaciones humanas.", "Semanal"],
                ["Administradores universitarios", "Ajustar campanas, cupos y estrategias preventivas.", "Trimestral"],
                ["Estudiantes", "Consultar recursos y decidir si solicita apoyo institucional.", "Segun necesidad"],
                ["Equipo tecnico", "Auditar calidad, sesgos, trazabilidad y limites del agente.", "Quincenal en piloto"],
            ],
            [2900, 5000, 1900],
        ),
        heading("Flujo funcional demostrable"),
        p(
            "1. Cargar Data Pack Oleada 1. 2. Reconstruir indicadores M1, M5 y M6. 3. Calcular un score preventivo no clinico. 4. Recuperar servicios desde D6 con RAG. 5. Generar una respuesta segura con limites explicitos. 6. Derivar a ayuda humana ante crisis o necesidad especializada.",
            after=80,
        ),
        heading("Alcance del demo"),
        p(
            "El demo en notebook ya puede mostrar carga de datos, metricas, segmentacion, recomendacion de recursos y una conversacion simulada con IA. Para el Entregable 2 se debe grabar el flujo completo con tres casos: sobrecarga en evaluaciones, desconocimiento de servicios y mensaje de crisis. En los tres se debe ver la fuente recuperada y el limite responsable del agente.",
            after=70,
        ),
        p("IA responsable impacto y escalabilidad", style="Title", align="center", after=80),
        heading("Primer analisis de riesgos eticos"),
        table(
            [
                ["Riesgo", "Como podria ocurrir", "Mitigacion propuesta"],
                [
                    "Diagnostico automatizado",
                    "El usuario interpreta una recomendacion como evaluacion clinica.",
                    "Lenguaje preventivo: senales, necesidades y recursos. Prohibicion explicita de diagnosticar o prescribir.",
                ],
                [
                    "Privacidad",
                    "Uso de informacion personal real o sensible fuera del alcance.",
                    "Solo Data Pack sintetico en el concurso; no se piden historiales clinicos ni datos reales.",
                ],
                [
                    "Sesgo",
                    "Recomendaciones desiguales por pais, etapa academica, genero, migracion o red de apoyo.",
                    "Auditoria por segmentos y validacion humana de bienestar antes de piloto.",
                ],
                [
                    "Alucinacion",
                    "La IA inventa servicios, horarios o criterios de acceso.",
                    "RAG acotado a D6 y documentos institucionales; cada salida muestra recurso, canal y razon.",
                ],
                [
                    "Crisis",
                    "La IA intenta resolver una situacion de riesgo por conversacion.",
                    "Derivacion inmediata a apoyo humano y canales definidos; suspension de recomendacion automatica.",
                ],
            ],
            [1900, 3500, 4400],
        ),
        heading("Impacto esperado"),
        p(
            "AURA Care no promete resultados clinicos. Sus metricas de exito son de orientacion, acceso y seguridad: mayor exposicion a servicios disponibles, mayor claridad del primer contacto, recomendaciones trazables desde D6, reduccion de respuestas inseguras y mejor lectura agregada de semanas o segmentos con mayor necesidad preventiva.",
            after=70,
        ),
        table(
            [
                ["Indicador de concurso", "Como lo aborda el PMV", "Evidencia de demostracion"],
                ["41% ansiedad moderada alta", "Orientacion temprana sin diagnostico.", "Score preventivo y rutas de apoyo."],
                ["68% no consulta apoyo", "Primer contacto discreto y de baja friccion.", "Conversacion simulada con recomendacion trazable."],
                ["44% desconoce servicios", "Mapa de recursos con RAG.", "Servicio recuperado desde D6."],
                ["6 semanas de espera", "Alternativas complementarias mientras espera atencion.", "Recursos escalonados y derivacion humana."],
            ],
            [2600, 3900, 3300],
        ),
        heading("Escalabilidad"),
        p(
            "La arquitectura puede replicarse en universidades de Chile, Peru y otras instituciones latinoamericanas porque separa datos, documentos, agente y reglas de seguridad. Para escalar se cambia el mapa local de servicios, el calendario academico, los protocolos de derivacion y el lenguaje institucional, sin entrenar un modelo desde cero.",
            after=70,
        ),
        heading("Cierre para evaluacion"),
        p(
            "AURA Care convierte el reto AETHERA en una propuesta demostrable: usa datos reales del concurso, enfoca misiones prioritarias, muestra un PMV funcional en Python y mantiene limites eticos claros. Su aporte competitivo no es reemplazar a bienestar, sino hacer que el primer paso hacia bienestar sea mas rapido, claro, seguro y medible.",
            after=60,
        ),
    ]

    document_xml = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W}" xmlns:r="{R}" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<w:body>{"".join(parts)}'
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="720" w:footer="720" w:gutter="0"/>'
        "</w:sectPr></w:body></w:document>"
    )
    styles_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W}">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:color w:val="000000"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="80" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="80" w:line="240" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:color w:val="000000"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:qFormat/><w:pPr><w:spacing w:after="70"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:b/><w:bCs/><w:sz w:val="30"/><w:szCs w:val="30"/><w:color w:val="000000"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="80" w:after="50"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/><w:b/><w:bCs/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="000000"/></w:rPr></w:style>
</w:styles>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
    rels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    doc_rels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/Entregable_1_indicadores.png"/></Relationships>'
    core = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Propuesta integrada AURA Care Entregable 1</dc:title><dc:creator>Equipo AURA Care</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2026-09-24T00:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-24T00:00:00Z</dcterms:modified></cp:coreProperties>"""
    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Word</Application></Properties>"""

    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("word/media/Entregable_1_indicadores.png", chart_bytes)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
    return OUTPUT


if __name__ == "__main__":
    print(build_docx().resolve())
