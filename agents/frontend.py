"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'frontend'
LABEL = 'Desarrollador frontend'
SPEC_FILE = 'frontend_spec.md'
EXTRACT_CODE = True

INSTRUCTIONS = "Realiza la tarea de tu rol."
agent = Agent(role='Desarrollador frontend Angular',
              goal=("Implementar la interacción del usuario y el consumo de la API en Angular según el contrato "
                    "aprobado por Arquitectura y los criterios de aceptación. Entregar frontend_spec.md y código "
                    "con nombre de archivo, cubriendo campos, validaciones visibles, estados de carga, vacío y error, "
                    "y accesibilidad, sin inventar endpoints, campos ni resultados de pruebas."),
              backstory=("Eres un desarrollador frontend senior especializado en Angular y TypeScript, con experiencia "
                         "en formularios reactivos, servicios HTTP, manejo de errores de API y accesibilidad (WCAG). "
                         "Trabajas a partir del contrato de API y del recorrido del usuario, y respetas las decisiones "
                         "de Arquitectura, Datos y Backend sin rediseñarlas. Sabes que las validaciones del cliente "
                         "mejoran la experiencia pero no reemplazan la validación ni la autorización del servidor. "
                         "Cuando falta información, la declaras como supuesto pendiente en lugar de inventarla, y "
                         "corriges el código según las observaciones que recibas."),
              llm=llm, verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Código en bloques markdown; primera línea con // nombre.service.ts.', agent=agent)
