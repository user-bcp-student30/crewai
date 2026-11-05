# testing_report.md

## Resumen del Issue

**Feature:** H-AUTH-01 — Usar consultas parametrizadas en el login de auth.  
**Componente:** `auth`. **Severidad reportada:** alta.

El Issue describe que `LegacyDatabase.findByCredentials` concatena `username` y `password` en el SQL, lo cual permitiría alterar la consulta. Se debe verificar el uso de `PreparedStatement` sin cambiar el contrato existente de `POST /auth/login`.

El material recibido incluye la descripción del hallazgo y propuestas de Arquitectura, Backend y Frontend, pero **no incluye el código del producto, `pom.xml`, pruebas actuales ni configuración de base de datos**. Backend informa que no modificó código por falta de esos archivos. Por eso, los casos de este informe son propuestas reproducibles sujetas a confirmar el framework, los fixtures y el formato real del request.

**Estado general: NO EJECUTADO.** No se proporcionó salida de comandos ni evidencia de cambios implementados.

## Matriz de trazabilidad

| Criterio de aceptación | Caso(s) | Tipo | Resultado esperado observable | Estado |
|---|---|---|---|---|
| `findByCredentials` usa `PreparedStatement` para ambos valores y no concatena valores en el SQL. | T-PERSIST-01 | Persistencia / revisión de código | La consulta conserva el SQL y el mapeo existentes; los dos valores se enlazan como parámetros y no forman parte del texto SQL. | **NO EJECUTADO**; falta el archivo fuente. |
| Login con `student` y `Workshop123!` responde 200 con `user.username` y `token`. | T-API-OK-01 | Positivo / integración | HTTP 200; la respuesta contiene `user.username` igual a `student` y un campo `token`. | **NO EJECUTADO**; falta endpoint y fixture verificables. |
| `' OR '1'='1` como usuario o contraseña responde 401 y no devuelve `token`. | T-API-INJ-U-01, T-API-INJ-P-01 | Negativo / seguridad / borde / integración | HTTP 401 en ambos casos; el cuerpo no contiene una propiedad `token`. | **NO EJECUTADO**; falta endpoint y datos verificables. |
| `AuthResourceTest` incluye una prueba de inyección y `mvn test` pasa desde `auth/`. | T-SUITE-01, T-API-INJ-U-01, T-API-INJ-P-01 | Integración / regresión | La clase de prueba del proyecto incluye los casos; Maven termina con código de salida 0 y reporte de pruebas satisfactorias. | **NO EJECUTADO**; falta la prueba actual y no hay salida de Maven. |

## Casos de prueba propuestos

### T-PERSIST-01 — Parametrización de las credenciales

- **Criterio:** uso de `PreparedStatement` para `username` y `password`, sin concatenarlos.
- **Tipo:** persistencia; revisión estática del código.
- **Precondiciones:** disponer de `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java` y conocer el método completo.
- **Datos:** `username = student`; `password = Workshop123!`. Para la inspección también considerar el valor literal `' OR '1'='1`.
- **Pasos:**
  1. Inspeccionar `findByCredentials` y la consulta que ejecuta.
  2. Confirmar que la consulta conserva las condiciones y el mapeo previos.
  3. Confirmar que el objeto es un `PreparedStatement` y que ambos valores se enlazan como parámetros —por ejemplo, con `setString`— en posiciones correspondientes.
  4. Confirmar que la construcción del SQL no incorpora los valores de entrada por concatenación o interpolación.
- **Resultado esperado:** el SQL es independiente de los valores recibidos; ambos valores se transmiten como parámetros. No se propone cambiar el esquema ni las restricciones de la base de datos.
- **Estado:** **NO EJECUTADO.** El archivo no está disponible. Esta inspección tampoco sustituye la prueba HTTP del login.

### T-API-OK-01 — Login válido

- **Criterio:** login válido conserva 200 e incluye `user.username` y `token`.
- **Tipo:** positivo; integración HTTP.
- **Precondiciones:** backend disponible y base de datos de pruebas con el usuario conocido por el criterio; confirmar el formato real del body y la forma de iniciar el servicio. El ejemplo JSON siguiente es **provisional**: Backend no confirmó el contrato de entrada.
- **Datos:** `student` / `Workshop123!`.
- **Pasos:** enviar `POST /auth/login` con las credenciales y el `Content-Type` que confirme el contrato existente.
- **Resultado esperado:** HTTP 200; respuesta con `user.username = "student"` y una propiedad `token`. No se valida el formato ni contenido del token, que no están especificados.
- **Estado:** **NO EJECUTADO.**

### T-API-INJ-U-01 — Intento de inyección en el usuario

- **Criterio:** el valor de inyección como usuario no produce autenticación ni token.
- **Tipo:** negativo; borde de entrada; integración.
- **Precondiciones:** las mismas que T-API-OK-01. Confirmar que la combinación de prueba no es una credencial legítima almacenada.
- **Datos:** usuario literal `' OR '1'='1`; contraseña `Workshop123!`.
- **Pasos:** enviar el login con esos valores; registrar status y cuerpo.
- **Resultado esperado:** HTTP 401 y cuerpo sin propiedad `token`. El formato restante del error no está definido por el Issue.
- **Estado:** **NO EJECUTADO.**

### T-API-INJ-P-01 — Intento de inyección en la contraseña

- **Criterio:** el valor de inyección como contraseña no produce autenticación ni token.
- **Tipo:** negativo; borde de entrada; integración.
- **Precondiciones:** las mismas que T-API-OK-01. Confirmar que `student` no tiene esa contraseña como credencial válida.
- **Datos:** usuario `student`; contraseña literal `' OR '1'='1`.
- **Pasos:** enviar el login con esos valores; registrar status y cuerpo.
- **Resultado esperado:** HTTP 401 y cuerpo sin propiedad `token`. No se presupone un payload de error concreto.
- **Estado:** **NO EJECUTADO.**

### T-SUITE-01 — Prueba del proyecto

- **Criterio:** `AuthResourceTest` incluye el intento de inyección y `mvn test` pasa desde `auth/`.
- **Tipo:** integración / regresión.
- **Precondiciones:** proyecto, `pom.xml`, test framework, fixtures y servicios de prueba disponibles; integración de los casos negativos en la clase existente sin eliminar sus pruebas actuales.
- **Datos:** los de T-API-OK-01 y ambos casos de inyección.
- **Pasos:** ejecutar `mvn test` desde `auth/` y conservar la salida completa y el código de terminación.
- **Resultado esperado:** ejecución finalizada con código 0; el reporte confirma la ejecución de los casos pertinentes, sin fallos.
- **Estado:** **NO EJECUTADO.**

**Cobertura de borde:** los dos campos se prueban por separado con el valor literal indicado por el Issue. No se proponen casos de valores vacíos, largos, normalización u otros formatos porque el Issue no define ese comportamiento. No aplica una prueba de restricciones o integridad de escritura: no se entregó contrato de esquema y el cambio descrito concierne una búsqueda de credenciales.

## Revisión de contratos

### API

- Confirmado por el Issue: método `POST`, ruta `/auth/login`; en éxito HTTP 200 con `user.username` y `token`; en los dos intentos indicados, HTTP 401 sin `token`.
- No confirmado: `Content-Type`, estructura y nombres del request, payload de error, otros estados HTTP y formato del token.
- Arquitectura propone JSON con `username` y `password`, pero lo marca como pendiente de cotejar. Por tanto, el código de prueba de abajo usa esa forma solo como **propuesta condicionada** y debe ajustarse al contrato real antes de integrarlo.
- No se añaden requisitos sobre mensajes, cabeceras de respuesta o formato del token.

### Persistencia

- El Issue exige parametrizar ambos valores y no concatenarlos.
- Arquitectura propone conservar la consulta y el mapeo existentes. No se entregaron SQL, esquema, restricciones, datos semilla ni implementación JDBC; no es posible validar su compatibilidad ni diseñar una prueba de integridad concreta.
- No se propone crear o modificar registros para estos casos. Debe usarse el mecanismo de fixtures existente, una vez disponible.

### Correcciones y entregables anteriores

- **Backend:** declara que el cambio está bloqueado y que no modificó código. No hay corrección que validar.
- **Arquitectura:** la propuesta de parametrización y conservación del endpoint se puede comprobar con T-PERSIST-01 y los casos HTTP; sus detalles pendientes de cotejo no se tratan como contrato confirmado.
- **Frontend:** los entregables descritos no verifican la parametrización SQL ni la respuesta real del servidor. No forman parte de la evidencia de estos criterios backend.
- No se recibió `LegacyDatabase.java`, `AuthResourceTest`, `pom.xml` ni el código del endpoint. No se puede verificar implementación, framework, dependencias, compilación ni compatibilidad de las correcciones.

## Preparación del entorno y datos

1. Obtener el checkout del proyecto con el directorio `auth/` y sus fuentes y pruebas.
2. Revisar `auth/pom.xml` para identificar versión de Java, framework de pruebas, dependencias, perfiles y configuración de Maven. **Pendiente:** esos artefactos no se proporcionaron.
3. Identificar y arrancar el servicio y la base de datos usando el procedimiento documentado por el proyecto. **Pendiente:** no se proporcionaron comandos de arranque, URL, configuración ni migraciones; no se inventa un puerto.
4. Confirmar que el entorno de pruebas tiene disponible el usuario `student` con la contraseña `Workshop123!`, según el criterio del Issue.
5. Confirmar que las combinaciones de prueba con `' OR '1'='1` no son credenciales válidas almacenadas.
6. Si se usa el código de prueba de abajo, establecer `AUTH_BASE_URL` a la URL base real del servicio. No incluir credenciales reales ni usar una base de datos de producción.
7. Confirmar el contrato real del body antes de ejecutar la prueba HTTP.

## Código de prueba propuesto

El siguiente ejemplo es una prueba de contrato HTTP en Java. **No se afirma que compile en este proyecto:** requiere JUnit 5, Java 11 o posterior y un endpoint de pruebas ya iniciado. La disponibilidad de esas dependencias y versiones no fue verificada. Está presentado como propuesta para integrar o adaptar a la `AuthResourceTest` existente; **no debe reemplazarla sin revisar su contenido y fixtures**. La forma JSON es la propuesta pendiente de confirmación descrita arriba.

```java
// archivo: auth/src/test/java/com/bcp/workshop/auth/AuthResourceTest.java
package com.bcp.workshop.auth;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.regex.Pattern;

import org.junit.jupiter.api.Test;

/**
 * Propuesta de pruebas de contrato HTTP.
 *
 * Requiere AUTH_BASE_URL apuntando a un servicio de pruebas ya iniciado.
 * Confirmar el formato JSON con Backend antes de integrar esta prueba.
 */
class AuthResourceTest {
    private static final String INJECTION = "' OR '1'='1";

    private final HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    @Test
    void loginValidoDevuelveUsernameYToken() throws Exception {
        HttpResponse<String> response = login("student", "Workshop123!");

        assertEquals(200, response.statusCode(), response.body());
        assertTrue(
                Pattern.compile("\"user\"\\s*:\\s*\\{[^}]*\"username\"\\s*:\\s*\"student\"")
                        .matcher(response.body())
                        .find(),
                "La respuesta debe incluir user.username igual a student");
        assertTrue(
                Pattern.compile("\"token\"\\s*:")
                        .matcher(response.body())
                        .find(),
                "La respuesta debe incluir token");
    }

    @Test
    void intentoDeInyeccionEnUsuarioDevuelve401SinToken() throws Exception {
        HttpResponse<String> response = login(INJECTION, "Workshop123!");

        assertEquals(401, response.statusCode(), response.body());
        assertFalse(
                Pattern.compile("\"token\"\\s*:")
                        .matcher(response.body())
                        .find(),
                "Una respuesta 401 no debe incluir token");
    }

    @Test
    void intentoDeInyeccionEnContrasenaDevuelve401SinToken() throws Exception {
        HttpResponse<String> response = login("student", INJECTION);

        assertEquals(401, response.statusCode(), response.body());
        assertFalse(
                Pattern.compile("\"token\"\\s*:")
                        .matcher(response.body())
                        .find(),
                "Una respuesta 401 no debe incluir token");
    }

    private HttpResponse<String> login(String username, String password) throws Exception {
        String baseUrl = System.getenv("AUTH_BASE_URL");
        if (baseUrl == null || baseUrl.isBlank()) {
            throw new IllegalStateException(
                    "Defina AUTH_BASE_URL con la URL base del servicio de pruebas");
        }

        String url = baseUrl.replaceAll("/+$", "") + "/auth/login";
        String body = "{\"username\":\"" + escapeJson(username)
                + "\",\"password\":\"" + escapeJson(password) + "\"}";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofSeconds(10))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8))
                .build();

        return client.send(
                request,
                HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
```

Este ejemplo comprueba status y presencia/ausencia de campos; no valida el payload de error ni la estructura completa del JSON, que no están especificados. Tampoco sustituye la revisión de `PreparedStatement` en el código de persistencia. Para que `mvn test` funcione con un endpoint externo, el proyecto debe soportar esta configuración; se desconoce si lo hace. Si la suite existente inicia un servidor de pruebas internamente, las solicitudes deben adaptarse a sus fixtures en lugar de depender de `AUTH_BASE_URL`.

## Comandos reproducibles

Desde la raíz del repositorio:

**Localizar e inspeccionar el método de persistencia** — localiza el código para la revisión manual de T-PERSIST-01; no es una prueba automática:

```sh
cd auth && grep -n -A60 -B5 'findByCredentials' src/main/java/com/bcp/workshop/auth/LegacyDatabase.java
```

**Ejecutar la suite requerida por el Issue:**

```sh
cd auth && mvn test
```

**Ejecutar la clase de prueba propuesta contra un servicio ya iniciado** — requiere que la clase esté integrada, que el test framework sea compatible y que el proyecto acepte el test externo:

```sh
cd auth && test -n "${AUTH_BASE_URL:-}" && mvn -Dtest=AuthResourceTest test
```

No se proporciona un comando de arranque del servicio: faltan el framework de aplicación y la configuración del proyecto. Si la suite exige que el servicio o la base de datos se inicien de otra manera, usar el procedimiento real documentado en el repositorio y registrar esos pasos.

## Limpieza

- Los casos propuestos solo envían solicitudes de login; no proponen insertar ni modificar datos.
- Confirmar con la implementación que el flujo de login de pruebas no produce otros cambios persistentes antes de ejecutarlos.
- Detener el servicio y la base de datos de pruebas con el procedimiento del proyecto. **Comando pendiente:** no se proporcionó uno.
- Si se configuró la URL únicamente para esta ejecución, limpiar la variable en esa shell:

```sh
unset AUTH_BASE_URL
```

No eliminar datos ni alterar registros hasta conocer las reglas y fixtures reales del proyecto.

## Limitaciones y resultados reales

- Todos los casos están **propuestos y NO EJECUTADOS**.
- No se recibió salida de `mvn test`, ni del endpoint, ni del código de pruebas.
- No se puede afirmar que `PreparedStatement` ya esté implementado, que la prueba exista, que Maven compile o que algún criterio haya pasado.
- La dependencia y versión de JUnit, la versión de Java, el contrato de request, el arranque de la aplicación y la preparación de la base de datos están pendientes de verificar con los artefactos del repositorio.
- La prueba Java incluida es candidata de integración, no una corrección ya incorporada a `AuthResourceTest`. La clase existente debe revisarse antes de integrarla para evitar reemplazar fixtures o pruebas previas.