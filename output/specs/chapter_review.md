# Revisión final — H-AUTH-01

## Resumen

La entrega disponible contiene propuestas y planes de verificación, pero Backend declara que no modificó código. No se aportaron los archivos fuente, una actualización de `AuthResourceTest` ni salidas reales de pruebas. Por tanto, no hay evidencia de que se haya corregido la vulnerabilidad alta reportada ni de que el comportamiento del endpoint cumpla los criterios.

La ruta `POST /auth/login` coincide en las propuestas, pero el formato del request sigue sin confirmación de Backend. Tampoco se pueden cotejar los DTOs, el SQL, el modelo de datos ni los códigos de error contra una implementación real.

## Matriz de criterios

| Criterio | Estado | Evidencia |
|---|---|---|
| `findByCredentials` usa `PreparedStatement` para `username` y `password`, sin concatenar valores en el SQL. | **Sin cubrir** | El Issue reporta concatenación en `LegacyDatabase.java:32`. Arquitectura especifica la corrección propuesta; Backend declara que no modificó código y que no dispone del archivo. Seguridad confirma que no pudo verificar una corrección. |
| El login con `student` y `Workshop123!` responde 200 con `user.username` y `token`. | **Parcial** | El criterio y la propuesta de Arquitectura definen el resultado esperado. Frontend modela una respuesta con esos campos, pero el body de entrada es un supuesto y no se aportaron implementación backend ni resultado de prueba. |
| La inyección como usuario o contraseña responde 401 y no devuelve `token`. | **Parcial** | Frontend describe el envío literal; Pruebas y Seguridad proponen casos separados para ambos campos. No hay evidencia de ejecución contra el backend ni respuesta real que confirme 401 y ausencia de `token`. |
| `AuthResourceTest` incluye la prueba de inyección y `mvn test` pasa desde `auth/`. | **Sin cubrir** | Backend informa que no pudo actualizar la prueba. Pruebas marca los casos como no ejecutados; no se adjunta salida de `mvn test`. |

## Hallazgos

### 1. Alta — Hallazgo de inyección SQL sin corrección verificable

**Ubicación:** `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java:32`, método `findByCredentials`, según el Issue.

El Issue describe concatenación de credenciales en SQL. No se entregó código corregido que demuestre el uso de parámetros; Backend confirma que no hizo cambios. El hallazgo de seguridad permanece abierto.

**Corrección concreta:** Backend debe parametrizar ambos valores con `PreparedStatement` —sin incorporarlos al texto SQL—, conservar la consulta y el mapeo existentes, y aportar el cambio para revisión. Después debe verificar los casos de login válido e inyección en cada campo.

### 2. Media — Contrato de request sin confirmar entre capas

**Ubicación:** contrato de `POST /auth/login`; propuesta de Arquitectura y `login.models.ts` / `login.service.ts` descritos por Frontend.

Frontend asume un body JSON `{ username, password }`, mientras Arquitectura indica que el formato real está pendiente de cotejo y Backend no pudo confirmarlo. No se demuestra una incompatibilidad efectiva, pero tampoco que el consumidor Angular use el contrato vigente.

**Corrección concreta:** Backend debe confirmar el formato real del request y Arquitectura/Frontend deben alinearse con él antes de integrar. Confirmar también la configuración de `HttpClient` y la URL base o el enrutamiento de `/auth/login`.

### 3. Media — Pruebas requeridas sin implementación ni salida real

**Ubicación:** `AuthResourceTest`; verificación `cd auth && mvn test`.

Los casos de regresión e inyección están propuestos, no implementados o acreditados como ejecutados. En particular, falta evidencia para los dos campos por separado y para la ausencia de `token` en cada respuesta 401.

**Corrección concreta:** Backend debe añadir o actualizar `AuthResourceTest` con login válido, inyección en `username` e inyección en `password`. El rol responsable de pruebas debe adjuntar la salida real y el código de terminación de `cd auth && mvn test`. Hasta entonces, la prueba queda pendiente.

### 4. Baja — Calidad y operación del frontend no verificables en el workspace

**Ubicación:** servicio Angular y configuración de la aplicación, según `frontend_spec.md`.

La propuesta usa una ruta relativa y no se aportaron workspace, versión de Angular ni configuración de `HttpClient` para comprobar integración o compilación. Frontend también deja pendiente cómo se usa el token tras un login válido. No se afirma que esos aspectos estén defectuosos; son riesgos no verificados.

**Corrección concreta:** antes de integrar la parte Angular, confirmar configuración y destino de la API, y documentar el flujo de sesión/token que corresponda al alcance aprobado. No se aportaron resultados de `ng test --watch=false` ni `ng build`.

## Pendientes antes de integrar

- **Backend:** entregar el cambio de `LegacyDatabase.findByCredentials` con ambos parámetros SQL y actualizar `AuthResourceTest`.
- **Backend y Frontend:** confirmar el contrato real del body y la respuesta de `POST /auth/login`; alinear DTOs y manejo de 401.
- **Pruebas:** adjuntar resultados reales de los casos positivo y negativos y de `cd auth && mvn test`. Las pruebas propuestas no sustituyen esa evidencia.
- **Seguridad:** revisar el cambio y confirmar que el hallazgo H-AUTH-01 quedó resuelto; actualmente sigue abierto.
- **Frontend:** confirmar configuración de API y, si forma parte del alcance de integración, el uso del token. No se aportaron archivos para verificar el build.
- **Mantenibilidad y operación:** no se proporcionaron `pom.xml`, modelo de datos ni configuración de despliegue; no es posible valorar dependencias o compatibilidad de esquema con la evidencia disponible.

VEREDICTO: RECHAZADO