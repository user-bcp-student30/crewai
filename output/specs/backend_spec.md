# backend_spec.md

## 1. Resumen de la implementación

**Estado: bloqueado; no se modificó código.**

El material recibido identifica `auth/src/main/java/com/bcp/workshop/auth/LegacyDatabase.java` y el método `findByCredentials`, pero no incluye su contenido ni el código del endpoint, sus DTOs, el acceso a la base de datos o las pruebas. Sin esos archivos no es posible sustituir la concatenación por parámetros conservando con certeza la consulta, el mapeo de resultados y el contrato existente.

No incluyo una clase Java inventada: hacerlo requeriría asumir firmas, esquema o comportamiento que no constan en el material, en contra de la instrucción de no inventarlos. Tampoco afirmo que el cambio compile o funcione.

## 2. Clases y responsabilidades

- **`LegacyDatabase`**: el Issue la identifica como propietaria de `findByCredentials`. El cambio requerido es parametrizar la consulta con `PreparedStatement`, sin concatenar los valores. Su SQL y mapeo actuales no están disponibles para producir una implementación completa y compatible.
- **Componente de `POST /auth/login`**: el Issue confirma la ruta y el método, pero no aporta el nombre de la clase ni su implementación. Debe conservar el flujo actual y no incluir un token cuando la autenticación falla.
- **`AuthResourceTest`**: el Issue exige añadir una prueba de inyección. No se proporcionó el archivo para actualizarlo.
- **Paquete**: el Issue sitúa `LegacyDatabase` en `com.bcp.workshop.auth`. No usaría `pe.bcp.login.service`, porque ese paquete no coincide con la ruta indicada y cambiarlo sin revisar el proyecto podría romper su estructura.

## 3. Recorrido de un caso válido y uno de error

**Caso válido esperado:** `POST /auth/login` recibe `student` y `Workshop123!`; el flujo existente consulta las credenciales mediante `findByCredentials`. La implementación pendiente debe enlazar ambos valores como parámetros SQL. Si las credenciales son válidas, el endpoint debe conservar la respuesta 200 con `user.username` y `token`. Este recorrido es el esperado según el Issue, no una verificación del código existente.

**Caso de error esperado:** se envía `' OR '1'='1` como usuario o contraseña. Con la consulta parametrizada, ese valor debe tratarse como dato y no alterar el SQL. Si las credenciales no son válidas, el endpoint debe responder 401 y no devolver `token`. Falta el código para confirmar que el flujo actual cumple ese comportamiento y que no existe una cuenta con esas credenciales literales.

## 4. Trazabilidad: criterio de aceptación → código

| Criterio | Código que debe cubrirlo | Estado |
|---|---|---|
| `findByCredentials` usa `PreparedStatement` para `username` y `password`, sin concatenarlos en SQL. | `LegacyDatabase.findByCredentials` | **No cubierto aquí**: falta el archivo y la consulta actual. |
| Login válido con `student` y `Workshop123!` responde 200 e incluye `user.username` y `token`. | Flujo existente de login y prueba de integración/recurso correspondiente | **No verificado**: faltan el código y la prueba. |
| Inyección como usuario o contraseña responde 401 y no devuelve `token`. | Flujo existente de login y prueba de inyección | **No cubierto aquí**: faltan el código y la prueba. |
| `AuthResourceTest` incluye la prueba de inyección y `mvn test` pasa desde `auth/`. | `AuthResourceTest` y ejecución de Maven | **No realizado**: falta el archivo y no se pueden ejecutar comandos. |

## 5. Comandos de verificación

- `cd auth && mvn test` — **NO EJECUTADO**.
- No se afirma que compile, que pase las pruebas o que el endpoint se comporte como se espera.

## 6. Supuestos y pendientes para otros roles

**Pendiente para Backend:** proporcionar el contenido actual de `LegacyDatabase.java`, el componente que implementa `POST /auth/login`, los DTOs o modelos usados y `AuthResourceTest`. Con esos archivos se puede preparar un cambio localizado que conserve la consulta, el mapeo y el contrato reales.

**Pendiente de verificación:** revisar los datos de prueba para confirmar que el valor de inyección no corresponde a credenciales válidas almacenadas.

**Pendiente para ejecución:** correr `mvn test` desde `auth/` cuando el entorno permita ejecutar comandos y registrar el resultado.