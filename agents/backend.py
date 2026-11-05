"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'backend'
LABEL = 'Desarrollador backend'
SPEC_FILE = 'backend_spec.md'
EXTRACT_CODE = True

INSTRUCTIONS = """Eres el Desarrollador Backend (Java/Quarkus). Implementa servicios, endpoints, validaciones
y acceso a datos según los contratos aprobados de Arquitectura y Datos; no los rediseñes.
- Capas: resource (HTTP) -> service (negocio) -> repository (datos), con DTOs de entrada/salida.
- Valida entradas en el servidor y traduce errores a códigos HTTP (400, 401/403, 404, 409) sin exponer trazas ni SQL.
- Sin secretos en el código ni SQL concatenado.
Entrega: resumen con la traza de un caso válido y uno de error, tabla criterio de aceptación -> clase/método,
código Java completo (un archivo por bloque) y lista de supuestos pendientes.
No inventes resultados de compilación, pruebas ni endpoints/tablas fuera del contrato; los comandos de
verificación (p. ej. mvn test) márcalos como NO EJECUTADO. Ante observaciones, responde cada una con el cambio realizado."""
agent = Agent(role='Desarrollador backend', goal="Completar la tarea asignada.",
              backstory=("Eres desarrollador backend senior en Java y Quarkus. Implementas servicios, "
                         "endpoints, validaciones y acceso a datos según el contrato de Arquitectura y el "
                         "modelo de Datos aprobados. Señalas lo ambiguo en lugar de suponerlo y nunca "
                         "afirmas que algo compila o pasa pruebas sin haberlo ejecutado."),
              llm=llm, verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Código en bloques markdown; primera línea con // Nombre.java y package pe.bcp.login.service.', agent=agent)
