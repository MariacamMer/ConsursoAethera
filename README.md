# AURA Care PMV

PMV funcional para el Desafio Ciudad AETHERA del Concurso Binacional de Innovacion 2026.

## Misiones abordadas

- M1: estres y ansiedad.
- M5: estigma y baja busqueda de ayuda.
- M6: barreras de acceso.

M2 se usa como variable contextual porque la sobrecarga en semanas de evaluacion ayuda a explicar patrones de M1.

## Que hace la solucion

AURA Care analiza el Data Pack Oleada 1, reconstruye indicadores del problema, prioriza necesidades preventivas no clinicas y usa un agente con RAG sobre el mapa de servicios D6 para orientar al estudiante hacia recursos institucionales ficticios.

No diagnostica, no prescribe tratamientos y no reemplaza profesionales de salud mental. Su rol es orientar, informar y conectar con ayuda humana.

## Datasets utilizados

- D1 bienestar: ansiedad, estres, apoyo social, conocimiento de servicios y uso previo.
- D2 servicios: solicitudes, espera, canal y derivacion.
- D3 trayectoria academica: asistencia, carga, evaluaciones, notas y alertas academicas sinteticas.
- D6 mapa de servicios: servicios ficticios, horarios, canales y capacidad.
- D7 calendario: semanas de evaluacion y actividades.

El Data Pack es provisto por la organizacion y no debe redistribuirse en repositorios publicos.

## Modelos y herramientas de IA

- RAG local con `scikit-learn` TF-IDF sobre D6.
- Agente con herramientas para recuperar servicios, interpretar necesidad preventiva y aplicar reglas de seguridad.
- Preparado para conectar un LLM abierto o gratuito en Entregable 2 sin cambiar la arquitectura.

## Uso rapido

```powershell
& 'C:\Users\ataca\anaconda3\python.exe' scripts\demo.py
```

Regenerar notebook:

```powershell
& 'C:\Users\ataca\anaconda3\python.exe' scripts\make_notebook.py
```

Regenerar Entregable 1 editable:

```powershell
& 'C:\Users\ataca\anaconda3\python.exe' scripts\make_entregable1_docx.py
```

Abrir:

```text
notebooks/aura_care_demo.ipynb
notebooks/executed/aura_care_demo_executed.ipynb
docs/entregable_1/Entregable_1_Diagnostico_AURA_Care_EDITABLE.docx
docs/entregable_1/Entregable_1_Diagnostico_AURA_Care.pdf
```

## Estructura

```text
src/aura_care/                  Codigo de carga, metricas, RAG y agente
scripts/                        Generadores y demo de consola
notebooks/                      Notebook de demo editable
notebooks/executed/             Notebook ejecutado con salidas
docs/entregable_1/              Documento editable, PDF y figura del diagnostico
docs/propuesta_inicial/         Propuesta amplia inicial como respaldo
Bases/                          Bases y anexos del concurso
Entrega del Data Pack (Oleada 1)/ Data Pack oficial local, no redistribuir
```

## Evidencia reconstruida

Con Oleada 1, la demo reconstruye:

- 41% con sintomatologia ansiosa moderada-alta.
- 68% con sintomatologia que nunca consulto apoyo.
- 44% que desconoce servicios.
- 42 dias de espera media en servicios de apoyo, equivalente a 6 semanas.

## Video demostrativo

Pendiente agregar enlace cuando se grabe el video de Entregable 2.
