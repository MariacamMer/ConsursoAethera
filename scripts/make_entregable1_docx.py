from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
import sys

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from aura_care import build_dashboard_metrics, ensure_demo_data
from aura_care.analytics import build_evidence_summary
from aura_care.config import DOCS_DIR


OUTPUT = DOCS_DIR / "entregable_1" / "Entregable_1_Diagnostico_AURA_Care_EDITABLE.docx"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
EMU_PER_INCH = 914400


def x(text: object) -> str:
    return escape(str(text), {'"': "&quot;"})


def pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".0%", "%")


def rpr(b=False, i=False, size=22):
    parts = [
        "<w:rPr>",
        '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>',
    ]
    if b:
        parts.append("<w:b/><w:bCs/>")
    if i:
        parts.append("<w:i/><w:iCs/>")
    parts.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/><w:color w:val="000000"/></w:rPr>')
    return "".join(parts)


def run(text: str, b=False, i=False, size=22) -> str:
    space = ' xml:space="preserve"' if text.startswith(" ") or text.endswith(" ") else ""
    return f"<w:r>{rpr(b=b, i=i, size=size)}<w:t{space}>{x(text)}</w:t></w:r>"


def p(text="", style=None, after=80, before=0, line=240, bold=False, italic=False, size=22, align=None):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    ppr.append(f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>')
    ppr_xml = f"<w:pPr>{''.join(ppr)}</w:pPr>"
    if isinstance(text, list):
        content = "".join(run(**item) for item in text)
    else:
        content = run(str(text), b=bold, i=italic, size=size)
    return f"<w:p>{ppr_xml}{content}</w:p>"


def heading(text: str) -> str:
    return p(text, style="Heading1", before=80, after=60, line=240)


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def cell(text: str, width: int, header=False):
    fill = "1F4E79" if header else "FFFFFF"
    color_rpr = rpr(b=header, size=20)
    paras = []
    for part in str(text).split("\n"):
        paras.append(
            f'<w:p><w:pPr><w:spacing w:after="20" w:line="220" w:lineRule="auto"/></w:pPr>'
            f'<w:r>{color_rpr}<w:t>{x(part)}</w:t></w:r></w:p>'
        )
    return f"""<w:tc>
<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:tcBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:left w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/></w:tcBorders><w:shd w:fill="{fill}"/><w:vAlign w:val="center"/><w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="90" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tcMar></w:tcPr>
{''.join(paras)}
</w:tc>"""


def table(rows: list[list[str]], widths: list[int]) -> str:
    trs = []
    for idx, row in enumerate(rows):
        header = idx == 0
        cells = "".join(cell(row[i], widths[i], header=header) for i in range(len(row)))
        trpr = "<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" if header else "<w:trPr><w:cantSplit/></w:trPr>"
        trs.append(f"<w:tr>{trpr}{cells}</w:tr>")
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    return f"""<w:tbl>
<w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:left w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:right w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="D9D9D9"/></w:tblBorders></w:tblPr>
<w:tblGrid>{grid}</w:tblGrid>{''.join(trs)}
</w:tbl>{p('', after=50)}"""


def image_paragraph(rid: str, filename: str, width_in: float, height_in: float) -> str:
    cx = int(width_in * EMU_PER_INCH)
    cy = int(height_in * EMU_PER_INCH)
    return f"""<w:p>
<w:pPr><w:jc w:val="center"/><w:spacing w:before="20" w:after="50"/></w:pPr>
<w:r><w:drawing>
<wp:inline distT="0" distB="0" distL="0" distR="0">
<wp:extent cx="{cx}" cy="{cy}"/>
<wp:effectExtent l="0" t="0" r="0" b="0"/>
<wp:docPr id="1" name="{x(filename)}"/>
<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic>
<pic:nvPicPr><pic:cNvPr id="0" name="{x(filename)}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
</pic:pic>
</a:graphicData></a:graphic>
</wp:inline>
</w:drawing></w:r>
</w:p>"""


def make_chart_png(path: Path, metrics) -> bytes:
    metric_lookup = {row["metric"]: row["value"] for _, row in metrics.iterrows()}
    bars = [
        ("M1 ansiedad moderada-alta", metric_lookup["Sintomatologia ansiosa moderada-alta"], 0.41),
        ("M5 no consulta apoyo", metric_lookup["Sintomatologia y nunca consulto apoyo"], 0.68),
        ("M6 desconoce servicios", metric_lookup["Desconoce servicios disponibles"], 0.44),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 2.5), dpi=180)
    labels = [row[0] for row in bars]
    values = [row[1] for row in bars]
    baselines = [row[2] for row in bars]
    y_pos = range(len(labels))
    ax.barh(list(y_pos), values, color="#1f4e79", label="Data Pack")
    ax.scatter(baselines, list(y_pos), color="#b03a2e", label="Linea base", zorder=5)
    ax.set_yticks(list(y_pos), labels, fontsize=8)
    ax.set_xlim(0, 0.8)
    ax.set_xlabel("Proporcion", fontsize=8)
    ax.set_title("Indicadores reconstruidos desde D1 y D2", fontsize=10, fontweight="bold")
    ax.legend(loc="lower right", fontsize=7)
    ax.grid(axis="x", alpha=0.25)
    for i, value in enumerate(values):
        ax.text(value + 0.015, i, pct(value), va="center", fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path.read_bytes()


def build_docx() -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    pack = ensure_demo_data()
    metrics = build_dashboard_metrics(pack.students, pack.service_use)
    evidence = build_evidence_summary(pack.students, pack.service_use, pack.academic, pack.calendar)
    m = {row["metric"]: row["value"] for _, row in metrics.iterrows()}
    chart_path = DOCS_DIR / "entregable_1" / "Entregable_1_indicadores.png"
    chart_bytes = make_chart_png(chart_path, metrics)

    parts = [
        p("Entregable 1 Diagnostico AURA Care", style="Title", align="center", after=60),
        p("Ciudad AETHERA - Concurso Binacional de Innovacion Chile Peru 2026", align="center", italic=True, size=20, after=90),
        heading("Misiones elegidas"),
        p(
            "AURA Care aborda M1 estres y ansiedad, M5 estigma y baja busqueda de ayuda, y M6 barreras de acceso. "
            "M2 presion academica se usa como evidencia contextual porque la sobrecarga de evaluaciones aparece asociada a menor asistencia y mas alertas academicas.",
            after=80,
        ),
        heading("Evidencia del Data Pack"),
        table(
            [
                ["Mision", "Indicador reconstruido", "Dato base", "Lectura para el problema"],
                [
                    "M1",
                    pct(m["Sintomatologia ansiosa moderada-alta"]),
                    f"{int(evidence['symptomatic_count']):,} de {int(evidence['survey_count']):,} respuestas D1",
                    "El deterioro de bienestar tiene escala suficiente para requerir prevencion temprana.",
                ],
                [
                    "M5",
                    pct(m["Sintomatologia y nunca consulto apoyo"]),
                    "D1 previous_support_use=never + ausencia de evento D2",
                    "La necesidad existe, pero no se convierte en busqueda efectiva de apoyo.",
                ],
                [
                    "M6",
                    f"{pct(m['Desconoce servicios disponibles'])}; {m['Espera media en servicios de apoyo']:.1f} dias",
                    "D1 services_awareness + D2 wait_days",
                    "El primer contacto falla por desconocimiento y por friccion operativa.",
                ],
            ],
            [1100, 2100, 3000, 3600],
        ),
        p("Figura 1 Indicadores reconstruidos desde D1 y D2 frente a la linea base del concurso.", italic=True, size=19, after=20),
        image_paragraph("rId2", "Entregable_1_indicadores.png", width_in=6.5, height_in=2.25),
        p(
            [
                {"text": "Evidencia complementaria. ", "b": True, "size": 22},
                {
                    "text": f"D1 indica {pct(evidence['stress_moderate_high'])} con estres moderado/alto; quienes reportan ansiedad alta duermen {evidence['sleep_high_anxiety']:.1f} horas promedio frente a {evidence['sleep_low_anxiety']:.1f} en ansiedad baja. Al cruzar D1 con D3, los perfiles con sobrecarga tienen asistencia promedio de {pct(evidence['attendance_overload_yes'])} frente a {pct(evidence['attendance_overload_no'])} sin sobrecarga, y alertas academicas media/alta de {pct(evidence['dropout_alert_overload_yes'])} frente a {pct(evidence['dropout_alert_overload_no'])}.",
                    "size": 22,
                },
            ],
            after=80,
        ),
        heading("Concepto de solucion"),
        p(
            "AURA Care es un agente preventivo con RAG y herramientas de analitica. Usa D1, D2, D3 y D7 para priorizar necesidades no clinicas y D6 para recomendar recursos concretos por horario, canal y tipo de servicio. El agente explica que es IA, entrega orientacion de primer contacto y deriva a apoyo humano cuando la consulta supera su alcance.",
            after=70,
        ),
        page_break(),
        p("AURA Care riesgos eticos y demostracion", style="Title", align="center", after=80),
        heading("Flujo funcional para el prototipo"),
        p(
            "1. Cargar Data Pack Oleada 1. 2. Reconstruir indicadores M1, M5 y M6. 3. Calcular un score preventivo no clinico. 4. Recuperar servicios desde D6 con RAG. 5. Generar una respuesta segura con limites explicitos. 6. Derivar a ayuda humana ante crisis o necesidad especializada.",
            after=80,
        ),
        heading("Primer analisis de riesgos eticos"),
        table(
            [
                ["Riesgo", "Mitigacion"],
                ["Diagnostico automatizado", "La salida usa lenguaje preventivo: senales, necesidades y recursos. No clasifica clinicamente ni prescribe tratamiento."],
                ["Privacidad", "Solo se usan datos sinteticos del Data Pack. No se agregan datos reales ni externos sensibles."],
                ["Sesgo", "Se revisan brechas por pais, etapa academica, migracion y red de apoyo. Las recomendaciones deben validarse con bienestar."],
                ["Respuesta incorrecta", "RAG limita respuestas al mapa D6. Cada recomendacion expone servicio, canal, horario y razon de derivacion."],
                ["Crisis", "Si aparece lenguaje de crisis o autolesion, la IA deja de recomendar automaticamente y prioriza contacto humano."],
            ],
            [2500, 7300],
        ),
        heading("Demo prevista para Entregable 2"),
        p(
            "En el video se mostrara el notebook ejecutando la carga de D1-D7, los indicadores, una lista priorizada de perfiles sinteticos y tres conversaciones: sobrecarga en evaluaciones, baja red de apoyo y crisis. En cada caso se vera la recuperacion RAG de D6 y la respuesta responsable del agente.",
            after=70,
        ),
        heading("Limite declarado"),
        p(
            "AURA Care no determina si una persona tiene ansiedad, depresion u otro cuadro. No decide cupos clinicos ni reemplaza a bienestar. Su aporte es reducir desconocimiento, ordenar el primer contacto y entregar evidencia agregada para acciones preventivas.",
            after=60,
        ),
    ]

    document_xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:body>{"".join(parts)}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'
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
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Entregable 1 Diagnostico AURA Care</dc:title><dc:creator>Equipo AURA Care</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">2026-09-24T00:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-24T00:00:00Z</dcterms:modified></cp:coreProperties>"""
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
