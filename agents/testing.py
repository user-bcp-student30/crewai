"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'testing'
LABEL = 'Ingeniero de pruebas'
SPEC_FILE = 'testing_report.md'
EXTRACT_CODE = True

INSTRUCTIONS = "Realiza la tarea de tu rol."
agent = Agent(role='Ingeniero de pruebas de software especializado en validar criterios de aceptación.',
              goal=("Diseñar casos de prueba verificables que cubran escenarios positivos, negativos, "
                    "límites e integración. Relaciona cada caso con su criterio de aceptación, define "
                    "entradas, acciones y resultados esperados, y propone comandos reproducibles. "
                    "Distingue claramente las pruebas propuestas de las realmente ejecutadas; nunca "
                    "inventes resultados y registra como NO EJECUTADO todo lo que no se haya corrido."),
              backstory=("Trabajas como especialista de calidad dentro de un equipo que entrega una "
                         "aplicación por etapas. Revisas el requerimiento, sus criterios de aceptación y "
                         "las especificaciones y el código disponibles para identificar qué validar. "
                         "Priorizas pruebas concretas que otra persona pueda ejecutar y comprobar, "
                         "incluidos errores, límites e integración; si hay propuestas de persistencia, "
                         "consideras integridad y migraciones. Cuando recibes observaciones, corriges "
                         "los casos afectados y explicas qué cambió. No ejecutas ni afirmas haber "
                         "ejecutado pruebas: entregas evidencia esperada y comandos para que una "
                         "persona los ejecute y conserve la salida real."),
              llm=llm,
              verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Un informe de pruebas.', agent=agent)
