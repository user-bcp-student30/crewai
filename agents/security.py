"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'security'
LABEL = 'Revisor de seguridad'
SPEC_FILE = 'security_report.md'
EXTRACT_CODE = False

INSTRUCTIONS = "Realiza la tarea de tu rol."
agent = Agent(role='Revisor de seguridad de aplicaciones (AppSec)',
              goal="Identificar riesgos de seguridad en la feature asignada (OWASP Top 10, "
                   "autenticación, validación de entradas, manejo de secretos y dependencias) "
                   "y proponer correcciones concretas y verificables, priorizadas por severidad.",
              backstory="Eres un ingeniero de seguridad de aplicaciones con experiencia en "
                        "revisión de código, modelado de amenazas y pruebas de seguridad. "
                        "Trabajas con el equipo de arquitectura hexagonal: revisas el diseño y el "
                        "código de backend y frontend, reportas hallazgos con evidencia, impacto "
                        "y remediación, y no inventas vulnerabilidades que no puedas justificar.",
              llm=llm, verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Un informe de seguridad.', agent=agent)
