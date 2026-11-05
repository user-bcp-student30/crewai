# H-AUTH-01 — Usar consultas parametrizadas en el login de auth

## 1) Solución propuesta

Como persona usuaria de auth, quiero que mis credenciales se consulten mediante parámetros SQL para que una entrada que parezca SQL no permita iniciar sesión sin credenciales válidas.

El cambio se limita a `auth/` y conserva `POST /auth/login`. `LegacyDatabase.findByCredentials` debe mantener la consulta y el mapeo de resultados que ya tenga, sustituyendo la concatenación de valores por una consulta parametrizada: `username` y `password` se enlazan mediante `PreparedStatement` (por ejemplo, con `setString`). Los valores de entrada no se incorporan al texto SQL.

La autenticación debe continuar usando el flujo existente para emitir la respuesta y el token en caso de éxito. No se propone cambiar el mecanismo, formato ni contenido del token.

**Lo que se puede confirmar del material disponible:** el Issue identifica `LegacyDatabase.findByCredentials`, `POST /auth/login` y `AuthResourceTest`. No se proporcionó el código fuente del producto. Por tanto, no es posible verificar aquí la forma actual del body, el SQL completo, el esquema de respuesta ni la organización actual de capas. Los detalles no confirmados se indican como pendientes o como propuestas.

## 2) Componentes y límites

| Componente | Estado según el Issue | Responsabilidad propuesta |
|---|---|---|
| `AuthResource` o componente equivalente de entrada | El Issue confirma el endpoint, pero no aporta su implementación. | Recibir `POST /auth/login`, validar o delegar la validación del request y traducir el resultado del caso de uso a la respuesta HTTP. |
| Caso de uso de login (`domain/port/input/`) | No se confirma su nombre ni existencia. | Definir la operación de autenticación invocada desde el adaptador de entrada. |
| Servicio de autenticación (`application/service/`) | No se confirma su nombre ni existencia. | Coordinar la consulta de credenciales mediante un puerto de salida y conservar el flujo existente de éxito y emisión de token. Debe depender de puertos del dominio, no de infraestructura. |
| Puerto de salida para buscar credenciales (`domain/port/output/`) | No se confirma su existencia. | Abstraer la búsqueda de usuario por credenciales. |
| `LegacyDatabase.findByCredentials` | El Issue lo identifica como el lugar donde se concatena SQL; su implementación no está disponible para esta revisión. | Actuar como adaptador de salida de persistencia. Usar `PreparedStatement` con parámetros para ambos valores y conservar el mapeo existente. No decidir aquí cambios de esquema o de autenticación. |
| Emisión del token | El criterio de éxito confirma que la respuesta debe incluir `token`; no identifica el componente que lo produce. | Reutilizar el mecanismo existente. No se propone una implementación ni un formato nuevos. |
| `AuthResourceTest` | El Issue identifica esta prueba y exige añadir un caso de inyección. | Verificar el login válido y los intentos de inyección, incluido que una respuesta 401 no contenga `token`. |

**Límite arquitectónico propuesto:** el adaptador REST depende del puerto de entrada; el servicio de aplicación depende de puertos de salida; `LegacyDatabase` implementa el puerto de persistencia. Las dependencias apuntan hacia adentro: `infrastructure → application → domain`. No se debe incorporar dependencia de `domain` hacia infraestructura.

No se puede determinar si el código actual ya sigue esta separación. La implementación debe reutilizar las interfaces y componentes existentes si están presentes, en vez de crear duplicados.

## 3) Contrato de API (entradas, respuestas, errores)

### Endpoint

- **Método y ruta:** `POST /auth/login`.
- **Alcance:** se conserva el endpoint existente. No se propone ningún endpoint adicional.
- **Formato del request:** el Issue no especifica `Content-Type` ni el esquema actual del body. La forma siguiente es una **propuesta pendiente de cotejar con el código existente**; no debe considerarse confirmación del contrato actual.

### Entrada propuesta

Si el contrato actual utiliza JSON, el body mínimo propuesto sería:

```json
{
  "username": "student",
  "password": "Workshop123!"
}
```

- `username`: string; requerido.
- `password`: string; requerido.
- No se propone recortar, normalizar ni transformar los valores, especialmente la contraseña, sin confirmar que ese comportamiento ya existe.
- El usuario o contraseña con el valor `' OR '1'='1` debe tratarse como valor literal de entrada. No debe alterar el SQL ni producir autenticación por sí mismo.

**Pendiente de confirmar con Backend:** el formato real del body, los nombres de campos, las reglas de validación existentes, el `Content-Type` y si se admiten valores vacíos.

### Respuestas

**200 OK — autenticación válida**

El Issue exige que la respuesta contenga `user.username` y `token`, pero no define el resto de la estructura. El siguiente ejemplo muestra únicamente una forma mínima propuesta, pendiente de verificar contra la respuesta existente:

```json
{
  "user": {
    "username": "student"
  },
  "token": "<token existente>"
}
```

Debe preservarse el formato real que ya use el endpoint. El contenido y formato del token no se especifican en el Issue.

**401 Unauthorized — credenciales no válidas**

Debe aplicarse a credenciales incorrectas, incluidos los valores de intento de inyección cuando no correspondan a credenciales válidas. La respuesta no debe incluir `token`.

El Issue no define el body de error. Como propuesta para confirmación, podría usarse:

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Credenciales inválidas"
  }
}
```

No se afirma que este sea el formato actual; debe preservarse el formato de error existente si lo hay.

### Otros errores

El Issue no establece el comportamiento para body malformado, campos ausentes, errores internos o indisponibilidad de la base de datos. No se puede afirmar qué códigos, mensajes o payloads devuelve actualmente el endpoint. Backend debe cotejarlos con la implementación y acordar si se conservan o se especifican aparte. No deben convertirse errores internos en 200 ni devolverse tokens cuando la autenticación no se haya completado correctamente.

## 4) Ejemplo de petición y respuesta

### Caso válido

**Petición** — ejemplo basado en el formato JSON propuesto; confirmar que coincide con el contrato actual:

```http
POST /auth/login
Content-Type: application/json

{
  "username": "student",
  "password": "Workshop123!"
}
```

**Respuesta esperada según el criterio del Issue:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "user": {
    "username": "student"
  },
  "token": "<token existente>"
}
```

**Recorrido:** el adaptador de entrada recibe el login y delega en el caso de uso. El servicio de aplicación solicita la búsqueda de credenciales a través de un puerto de salida. El adaptador `LegacyDatabase` ejecuta la consulta con `PreparedStatement`, enlazando `username` y `password` como parámetros separados. Si la autenticación resulta válida, el flujo existente construye la respuesta de éxito y entrega el token. La estructura precisa de las capas y los componentes de token debe cotejarse con el código.

### Caso de error representativo: intento de inyección en la contraseña

**Petición** — se presupone el formato JSON del ejemplo anterior:

```http
POST /auth/login
Content-Type: application/json

{
  "username": "student",
  "password": "' OR '1'='1"
}
```

**Respuesta exigida por el Issue:**

```http
HTTP/1.1 401 Unauthorized
```

La respuesta no debe incluir `token`. El body de error no está definido por el Issue; si se confirma la propuesta de la sección anterior, podría ser:

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Credenciales inválidas"
  }
}
```

**Recorrido:** el valor se transmite como dato del parámetro de la consulta, no como parte del SQL. La autenticación solo tiene éxito si las credenciales corresponden a un usuario válido según el comportamiento existente. En caso contrario, el adaptador de entrada responde 401 sin token. El mismo requisito se aplica si el valor de inyección se envía como `username`.

## 5) Criterios de aceptación verificables

1. **Consulta parametrizada:** `LegacyDatabase.findByCredentials` usa `PreparedStatement` y enlaza `username` y `password` como parámetros. Verificar que sus valores no se concatenen al texto SQL.
2. **Login válido:** una prueba de `POST /auth/login` con `student` y `Workshop123!` recibe 200 y contiene `user.username` y `token`, respetando la estructura real del endpoint.
3. **Intento de inyección:** `AuthResourceTest` incluye pruebas de inyección en usuario o contraseña; la autenticación responde 401 y la respuesta no contiene `token`.
4. **Regresión:** ejecutar `mvn test` desde `auth/` y confirmar que pasa.

El diseño permite cumplir los cuatro criterios sin modificar el endpoint ni exigir cambios de esquema. Sin el código y sin ejecutar pruebas, no se puede afirmar que la implementación actual los cumpla ni que `mvn test` pase; ambas verificaciones quedan pendientes de la implementación.

## 6) Supuestos y decisiones pendientes para otros roles

### Backend

- Confirmar la forma real del body, sus nombres de campos, validaciones y `Content-Type` antes de fijar el contrato JSON propuesto.
- Confirmar la estructura actual de las respuestas 200 y 401, incluido el formato del error. Preservarla salvo que se acuerde explícitamente un cambio.
- Confirmar qué componentes existentes gestionan el caso de uso, la consulta y la emisión del token; reutilizarlos y mantener las dependencias hexagonales.
- Confirmar el manejo de campos ausentes o malformados y de errores de persistencia, ya que el Issue no lo define.
- Añadir la prueba de inyección a `AuthResourceTest` y ejecutar `mvn test` desde `auth/`.

### Datos

- El Issue no informa tablas, columnas, tipos, esquema ni restricciones de unicidad. No se propone cambiar ninguno de ellos.
- Confirmar que la consulta actual y su mapeo pueden conservarse usando placeholders y que los tipos de parámetros son compatibles con la base de datos.
- Confirmar, si resulta relevante para la consulta existente, cómo se manejan valores nulos, collation o diferencias de mayúsculas y minúsculas. No se presume ninguna política.
- La concurrencia y las transacciones no están especificadas por el Issue; confirmar si el flujo existente requiere alguna consideración adicional.

### Frontend

- Confirmar que se mantienen el endpoint y los campos de petición que ya consume el cliente.
- Confirmar que el frontend trata 401 como credenciales no válidas y no depende de un token en esa respuesta.
- El Issue no define mensajes de interfaz ni el esquema del payload de error; no se propone cambiar la experiencia de usuario sin esa confirmación.