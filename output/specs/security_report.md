# Informe de seguridad — H-AUTH-01

## Resumen

La feature aborda una vulnerabilidad de inyección SQL reportada en `LegacyDatabase.findByCredentials`: el Issue indica que el método concatena `username` y `password` en la consulta, lo que permitiría alterar el SQL y eludir la autenticación. La severidad asignada es **Alta**.

La información disponible no incluye el código fuente actual ni la configuración de dependencias. Backend declara que no modificó código y que no pudo ejecutar pruebas. Por ello, el hallazgo se basa en la evidencia descrita por el Issue; **no se pudo verificar de forma independiente su estado actual ni confirmar una corrección**.

No hay evidencia suficiente para afirmar vulnerabilidades en otras áreas revisadas. Esas áreas quedan indicadas como no verificadas.

## Activos, datos y puntos de entrada

- **Activos y datos sensibles:** credenciales de acceso (`username` y `password`), registros de usuarios consultados por la autenticación y el `token` devuelto en el flujo de éxito.
- **Puntos de entrada identificados:**
  - `POST /auth/login`, confirmado por la feature.
  - `LegacyDatabase.findByCredentials`, señalado como punto donde se forma la consulta SQL.
  - La interfaz de login descrita por Frontend recibe usuario y contraseña y envía la solicitud; la implementación no fue verificada.
- **Integración:** acceso SQL a la base de datos desde `LegacyDatabase`. No se proporcionaron detalles de configuración o infraestructura.
- **Archivos:** no se reportan cargas ni procesamiento de archivos en esta feature.

## Revisión OWASP y criterios de aceptación

| Área | Evaluación basada en la información disponible |
|---|---|
| Inyección SQL | El Issue reporta concatenación de credenciales en SQL en `findByCredentials`; es el hallazgo principal. No se proporcionó el archivo fuente para verificarlo o revisar una corrección. |
| Control de acceso | No se proporcionó información suficiente sobre autorización para recursos posteriores al login. No se afirma un hallazgo en esta área. |
| Autenticación y sesiones | El criterio define el resultado del login y menciona un `token`, pero no se especifican su generación, validación, expiración, renovación o revocación. No se puede evaluar su seguridad. |
| Validación y sanitización | La parametrización es la defensa exigida contra esta inyección. No se proporcionaron reglas de validación del servidor; las validaciones del frontend descritas no sustituyen esa verificación. |
| XSS e inyección de comandos | No hay evidencia de salida HTML no segura ni de ejecución de comandos. No se afirma un hallazgo en estas áreas. |
| Secretos y credenciales de configuración | No se proporcionaron archivos de configuración ni código de despliegue. No es posible verificar el almacenamiento de credenciales de base de datos o secretos de token. |
| Exposición de datos y registros | Los criterios exigen que un login fallido no devuelva `token`. No se aportaron respuestas reales ni registros para comprobarlo. No hay evidencia sobre exposición de contraseñas en logs. |
| Dependencias vulnerables | No se proporcionaron `pom.xml`, inventario de dependencias ni resultados de análisis. El estado queda sin verificar. |

Los criterios actuales cubren la parametrización, el login válido y los intentos de inyección. Para que la cobertura sea inequívoca, conviene especificar que la prueba negativa debe ejercitar **por separado** la inyección en `username` y en `password`, y comprobar en ambos casos el 401 y la ausencia de `token`.

## Hallazgos

| ID | Severidad | Descripción y ubicación | Impacto | Corrección concreta y verificación |
|---|---|---|---|---|
| H-AUTH-01 | **Alta** | El Issue reporta que `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32`, en `findByCredentials`, concatena `username` y `password` en el SQL. El código no está disponible en el material revisado, por lo que la condición no pudo comprobarse de forma independiente. | Según el Issue, una entrada especialmente construida podría modificar la consulta y permitir autenticarse sin conocer la contraseña. | Sustituir la concatenación por un `PreparedStatement`, enlazando ambos valores como parámetros —por ejemplo, con `setString`— y conservando la consulta y el mapeo actuales. Verificar el código y añadir en `AuthResourceTest` pruebas separadas para la entrada indicada en cada campo. Comprobar que ambas devuelvan 401 sin `token`, y ejecutar `cd auth && mvn test`. No se aportaron código ni resultados que demuestren que la corrección ya se implementó o pasó las pruebas. |

## Recomendaciones

1. **Aplicar la parametrización en el adaptador de persistencia.** Los valores de entrada deben permanecer fuera del texto SQL. Conservar la consulta y el mapeo existentes, según la propuesta de Arquitectura.
2. **Completar la cobertura de `AuthResourceTest`.** Incluir casos independientes con `' OR '1'='1` como usuario y como contraseña. Para cada uno, comprobar HTTP 401 y que la respuesta no contenga una propiedad `token`. Mantener también la regresión del login válido exigida por el Issue.
3. **Verificar el contrato existente antes de probar el endpoint.** La forma del body y los detalles de la respuesta de error no están confirmados; no asumir el JSON propuesto por Arquitectura como contrato vigente.
4. **No tratar la validación del cliente como control de seguridad del servidor.** La prueba debe comprobar el comportamiento de backend y de la consulta, no solo el envío de valores desde Angular.
5. **Completar revisiones pendientes cuando estén disponibles los archivos:** revisar el manejo de errores y logs para descartar exposición de credenciales o detalles internos; revisar configuración de secretos y ejecutar un análisis de dependencias sobre el `pom.xml`. La información recibida no permite concluir que existan problemas en estas áreas.
6. **Añadir como criterio explícito de verificación** que los dos campos se prueben por separado. El criterio actual dice “como usuario o contraseña”, pero no detalla si la prueba debe cubrir ambos casos.

## Checklist de verificación

- [ ] Revisar `LegacyDatabase.findByCredentials` y confirmar que usa `PreparedStatement` para `username` y `password`, sin concatenar esos valores en el SQL.
- [ ] Confirmar que se conserva la consulta y el mapeo de resultados existentes.
- [ ] Confirmar que el login válido con `student` y `Workshop123!` devuelve 200 e incluye `user.username` y `token`.
- [ ] Probar la entrada de inyección en `username` y confirmar 401 sin `token`.
- [ ] Probar la entrada de inyección en `password` y confirmar 401 sin `token`.
- [ ] Confirmar que `AuthResourceTest` cubre los dos intentos por separado.
- [ ] Ejecutar `cd auth && mvn test` y conservar el resultado.
- [ ] Revisar logs, manejo de errores y configuración de secretos cuando se disponga del código correspondiente.
- [ ] Analizar las dependencias cuando se disponga del archivo de construcción y de la configuración de análisis.

**Estado de verificación:** no se proporcionaron cambios de código ni resultados de ejecución; los puntos anteriores están pendientes.