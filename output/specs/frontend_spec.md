# frontend_spec.md

## Estado y alcance

La interfaz Angular puede capturar las credenciales y llamar a `POST /auth/login`, pero **no implementa ni verifica la parametrización SQL**. Los criterios de seguridad de base de datos y de prueba de `AuthResourceTest` corresponden al backend.

El endpoint y los campos `username` y `password` se toman del material de la feature. **SUPUESTO PENDIENTE:** la forma JSON `{ username, password }` fue propuesta por Arquitectura, pero Backend no confirmó que sea el body vigente. El código la usa provisionalmente; confirmar el formato antes de integrarlo. También está pendiente confirmar cómo la aplicación debe conservar o utilizar el token después del login. Esta propuesta no lo almacena ni lo muestra.

## Recorrido y criterios de aceptación

1. La persona ingresa usuario y contraseña.
2. El formulario muestra validaciones locales de campos requeridos.
3. Al enviar, la interfaz llama a `POST /auth/login` y muestra progreso; no transforma los valores.
4. Si recibe una respuesta exitosa con `user.username` y `token`, muestra una confirmación usando el username, sin presentar ni guardar el token.
5. Si recibe 401, muestra un mensaje de credenciales no válidas. Otros errores muestran un mensaje genérico, sin exponer el body técnico de la respuesta.

| Criterio de aceptación | Relación con frontend | Evidencia y comprobación |
|---|---|---|
| `findByCredentials` usa `PreparedStatement` para ambos parámetros y no concatena valores en SQL. | **Backend únicamente.** La interfaz no puede demostrar ni implementar esta propiedad. | Revisar `LegacyDatabase.findByCredentials` y probarlo en backend. **NO VERIFICADO.** |
| Login válido responde 200 con `user.username` y `token`. | El servicio envía las credenciales y el componente consume la respuesta tipada. No demuestra que el servidor responda así. | `login.service.ts`, `login.component.ts`. Probar con el backend disponible y verificar respuesta en Network. **NO EJECUTADO.** |
| `' OR '1'='1` como usuario o contraseña responde 401 y no devuelve `token`. | El formulario transmite literalmente el valor; el componente no muestra ni almacena el token en el camino de error. La ausencia de token en la respuesta debe probarla el backend. | `login.service.spec.ts` verifica el envío literal al endpoint, no la seguridad del servidor. Probar ambos campos contra backend y comprobar 401 sin token. **NO EJECUTADO.** |
| `AuthResourceTest` incluye prueba de inyección y `mvn test` pasa desde `auth/`. | **Backend únicamente.** | Añadir/verificar la prueba en `AuthResourceTest`; ejecutar `cd auth && mvn test`. **NO EJECUTADO.** |

## Campos y validaciones visibles

| Campo | Tipo | Validación de cliente | Accesibilidad |
|---|---|---|---|
| `username` | Texto | Requerido; mensaje al intentar enviar vacío. Sin normalización ni reglas de formato inventadas. | Etiqueta asociada, `autocomplete="username"`, estado inválido y descripción de error. |
| `password` | Contraseña | Requerido; mensaje al intentar enviar vacío. No se recorta ni modifica. | Etiqueta asociada, `autocomplete="current-password"`, estado inválido y descripción de error. |

La validación del cliente solo mejora la experiencia; el servidor debe validar las credenciales y autorizar el acceso.

## Estados de pantalla

- **Inicial/vacío:** formulario vacío con indicación para ingresar credenciales. El endpoint no representa una colección; no se inventa un estado de “sin resultados”.
- **Validación:** errores junto a los campos y foco en el primer campo inválido al enviar.
- **Carga:** se deshabilitan los campos y el botón; se anuncia el progreso.
- **Éxito:** confirmación accesible basada en `user.username`. No se define navegación ni sesión porque no hay contrato para ello.
- **Error:** mensaje accesible; ante 401 se informa que las credenciales no son válidas. No se muestra el contenido técnico devuelto por el servidor.

## Mapeo de errores

El material confirma el 401 para credenciales no válidas. No define los payloads ni el comportamiento de 400, 403, 404, 409 o 5xx. La implementación presenta un mensaje genérico para esos estados si ocurren, sin atribuirles una causa no confirmada.

| Estado recibido | Mensaje mostrado |
|---|---|
| 400 | No se pudo completar el inicio de sesión. Inténtalo de nuevo. |
| 401 | Usuario o contraseña incorrectos. |
| 403 | No se pudo completar el inicio de sesión. Inténtalo de nuevo. |
| 404 | No se pudo completar el inicio de sesión. Inténtalo de nuevo. |
| 409 | No se pudo completar el inicio de sesión. Inténtalo de nuevo. |
| 5xx | No se pudo completar el inicio de sesión. Inténtalo de nuevo más tarde. |
| Red u otro error | No se pudo completar el inicio de sesión. Inténtalo de nuevo. |

**Pendiente para Backend:** confirmar qué estados y significados forman parte del contrato, así como sus errores de validación y autenticación.

## Accesibilidad y seguridad en cliente

- Etiquetas explícitas, navegación nativa por teclado y foco visible.
- Errores anunciados con `role="alert"` y progreso/éxito con regiones vivas.
- Contraste definido mediante colores oscuros sobre fondo claro; el error también se comunica con texto, no solo color.
- No se usa `innerHTML`, ni se presenta el token, ni se persiste en almacenamiento local o de sesión.
- La integración con un servicio de sesión/router y la política de uso del token quedan **SUPUESTO PENDIENTE**.

## Supuestos pendientes

1. **Backend:** confirmar que el request es JSON con campos `username` y `password`, y el formato real de errores.
2. **Integración Angular:** confirmar versión de Angular, configuración de `HttpClient`, origen/base URL de API y ubicación del componente.
3. **Arquitectura de aplicación:** definir cómo se usa el token tras un login válido. No se inventa su persistencia ni navegación en este código.

Verificación propuesta, no ejecutada: `ng test --watch=false` y `ng build`. Requieren el workspace Angular y su configuración, no incluidos aquí.

```typescript
// login.models.ts

/**
 * SUPUESTO PENDIENTE: Backend debe confirmar que el body actual de
 * POST /auth/login es JSON con estos nombres de campo.
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * Basado en los elementos de respuesta exigidos por los criterios:
 * user.username y token.
 */
export interface LoginResponse {
  user: {
    username: string;
  };
  token: string;
}
```

```typescript
// login.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { LoginRequest, LoginResponse } from './login.models';

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  constructor(private readonly http: HttpClient) {}

  /**
   * Usa la ruta confirmada por la feature.
   * SUPUESTO PENDIENTE: el despliegue enruta esta ruta relativa al backend.
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>('/auth/login', credentials);
  }
}
```

```typescript
// login.component.ts

import { ChangeDetectorRef, Component, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { LoginService } from './login.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  readonly form = new FormGroup({
    username: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
    }),
    password: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
    }),
  });

  loading = false;
  submitted = false;
  apiErrorMessage: string | null = null;
  successMessage: string | null = null;

  @ViewChild('usernameInput')
  private usernameInput?: ElementRef<HTMLInputElement>;

  @ViewChild('passwordInput')
  private passwordInput?: ElementRef<HTMLInputElement>;

  @ViewChild('errorSummary')
  private errorSummary?: ElementRef<HTMLDivElement>;

  constructor(
    private readonly loginService: LoginService,
    private readonly changeDetector: ChangeDetectorRef,
  ) {}

  submit(): void {
    this.submitted = true;
    this.form.markAllAsTouched();
    this.clearServerMessages();

    if (this.form.invalid) {
      this.focusFirstInvalidField();
      return;
    }

    this.loading = true;
    const credentials = this.form.getRawValue();

    this.loginService.login(credentials).subscribe({
      next: (response) => {
        this.loading = false;
        this.successMessage =
          `Inicio de sesión correcto para ${response.user.username}.`;

        // El token no se muestra ni se persiste.
        // Su integración con el estado de autenticación está pendiente de definición.
      },
      error: (error: unknown) => {
        this.loading = false;
        this.apiErrorMessage = this.messageForError(error);

        // Hace presente el resumen condicional antes de mover el foco.
        this.changeDetector.detectChanges();
        this.errorSummary?.nativeElement.focus();
      },
    });
  }

  clearServerMessages(): void {
    this.apiErrorMessage = null;
    this.successMessage = null;
  }

  showUsernameError(): boolean {
    const control = this.form.get('username');
    return Boolean(control?.invalid && (control.touched || this.submitted));
  }

  showPasswordError(): boolean {
    const control = this.form.get('password');
    return Boolean(control?.invalid && (control.touched || this.submitted));
  }

  private focusFirstInvalidField(): void {
    if (this.form.get('username')?.invalid) {
      this.usernameInput?.nativeElement.focus();
      return;
    }

    if (this.form.get('password')?.invalid) {
      this.passwordInput?.nativeElement.focus();
    }
  }

  private messageForError(error: unknown): string {
    if (error instanceof HttpErrorResponse && error.status === 401) {
      return 'Usuario o contraseña incorrectos.';
    }

    // Los significados/payloads de estos estados no están especificados
    // en el contrato disponible. No se expone el error técnico del servidor.
    if (
      error instanceof HttpErrorResponse &&
      error.status >= 500
    ) {
      return 'No se pudo completar el inicio de sesión. Inténtalo de nuevo más tarde.';
    }

    return 'No se pudo completar el inicio de sesión. Inténtalo de nuevo.';
  }
}
```

```html
<!-- login.component.html -->

<main class="login-page">
  <section class="login-card" aria-labelledby="login-title">
    <h1 id="login-title">Iniciar sesión</h1>
    <p id="login-instructions">Ingresa tu usuario y contraseña.</p>

    <div
      *ngIf="apiErrorMessage"
      #errorSummary
      class="message message-error"
      role="alert"
      aria-live="assertive"
      tabindex="-1"
    >
      {{ apiErrorMessage }}
    </div>

    <p *ngIf="successMessage" class="message message-success" role="status" aria-live="polite">
      {{ successMessage }}
    </p>

    <p *ngIf="loading" class="progress-message" role="status" aria-live="polite">
      Iniciando sesión…
    </p>

    <form [formGroup]="form" (ngSubmit)="submit()" novalidate>
      <fieldset [disabled]="loading">
        <legend class="visually-hidden">Credenciales</legend>

        <div class="form-field">
          <label for="username">Usuario</label>
          <input
            #usernameInput
            id="username"
            name="username"
            type="text"
            formControlName="username"
            autocomplete="username"
            aria-describedby="username-hint username-error"
            [attr.aria-invalid]="showUsernameError() ? 'true' : 'false'"
            (input)="clearServerMessages()"
          />
          <span id="username-hint" class="field-hint">Escribe tu usuario.</span>
          <span
            *ngIf="showUsernameError()"
            id="username-error"
            class="field-error"
          >
            El usuario es obligatorio.
          </span>
        </div>

        <div class="form-field">
          <label for="password">Contraseña</label>
          <input
            #passwordInput
            id="password"
            name="password"
            type="password"
            formControlName="password"
            autocomplete="current-password"
            aria-describedby="password-hint password-error"
            [attr.aria-invalid]="showPasswordError() ? 'true' : 'false'"
            (input)="clearServerMessages()"
          />
          <span id="password-hint" class="field-hint">Escribe tu contraseña.</span>
          <span
            *ngIf="showPasswordError()"
            id="password-error"
            class="field-error"
          >
            La contraseña es obligatoria.
          </span>
        </div>
      </fieldset>

      <button type="submit" [disabled]="loading">
        {{ loading ? 'Iniciando sesión…' : 'Iniciar sesión' }}
      </button>
    </form>
  </section>
</main>
```

```css
/* login.component.css */

:host {
  display: block;
  color: #172033;
  background: #f4f6fa;
  min-height: 100%;
}

.login-page {
  box-sizing: border-box;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
}

.login-card {
  box-sizing: border-box;
  width: min(100%, 28rem);
  padding: 2rem;
  background: #fff;
  border: 1px solid #687386;
  border-radius: 0.5rem;
}

.form-field {
  display: grid;
  gap: 0.4rem;
  margin: 1.25rem 0;
}

label {
  font-weight: 700;
}

input {
  box-sizing: border-box;
  width: 100%;
  min-height: 2.75rem;
  padding: 0.6rem 0.75rem;
  color: #172033;
  background: #fff;
  border: 1px solid #455168;
  border-radius: 0.25rem;
  font: inherit;
}

input[aria-invalid='true'] {
  border: 2px solid #a31621;
}

button {
  min-height: 2.75rem;
  padding: 0.6rem 1rem;
  color: #fff;
  background: #173b70;
  border: 2px solid #173b70;
  border-radius: 0.25rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  cursor: wait;
  background: #455168;
  border-color: #455168;
}

input:focus-visible,
button:focus-visible,
[tabindex='-1']:focus-visible {
  outline: 3px solid #b54708;
  outline-offset: 3px;
}

.field-hint {
  color: #39465d;
}

.field-error,
.message-error {
  color: #8b101b;
}

.message {
  margin: 1rem 0;
  padding: 0.75rem;
  border: 1px solid currentColor;
  border-radius: 0.25rem;
}

.message-success {
  color: #14532d;
}

.progress-message {
  color: #173b70;
  font-weight: 700;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

```typescript
// login.service.spec.ts

import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { LoginService } from './login.service';
import { LoginRequest, LoginResponse } from './login.models';

describe('LoginService', () => {
  let service: LoginService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [LoginService],
    });

    service = TestBed.inject(LoginService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('envía las credenciales a POST /auth/login y recibe la respuesta tipada', () => {
    const credentials: LoginRequest = {
      username: 'student',
      password: 'Workshop123!',
    };
    const response: LoginResponse = {
      user: { username: 'student' },
      token: 'token-de-prueba',
    };

    service.login(credentials).subscribe((result) => {
      expect(result.user.username).toBe('student');
      expect(result.token).toBe('token-de-prueba');
    });

    const request = httpMock.expectOne('/auth/login');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(credentials);
    request.flush(response);
  });

  [
    { username: "' OR '1'='1", password: 'cualquier-valor' },
    { username: 'student', password: "' OR '1'='1" },
  ].forEach((credentials) => {
    it('transmite literalmente el valor recibido, sin probar la seguridad del servidor', () => {
      service.login(credentials).subscribe({
        error: (error) => {
          expect(error.status).toBe(401);
        },
      });

      const request = httpMock.expectOne('/auth/login');
      expect(request.request.method).toBe('POST');
      expect(request.request.body).toEqual(credentials);
      request.flush({}, { status: 401, statusText: 'Unauthorized' });
    });
  });
});
```

```text
// verificacion.md

Estado de ejecución: NO EJECUTADO. No se proporcionó el workspace Angular ni se ejecutaron herramientas.

Verificación propuesta en el workspace:
- ng test --watch=false
- ng build

Prueba manual propuesta, una vez confirmados el body y el entorno de API:
1. Abrir la pantalla y enviar el formulario vacío; comprobar los mensajes y el foco en el primer campo.
2. Enviar credenciales válidas; comprobar progreso, solicitud POST a /auth/login y respuesta 200 con user.username y token. Verificar que la interfaz no muestra ni persiste el token.
3. Probar el literal "' OR '1'='1" como usuario y como contraseña; comprobar que el cliente envía el valor sin transformarlo y que el servidor responde 401 sin token.
4. Probar navegación por teclado y comprobar anuncios de progreso y errores con lector de pantalla.

Las pruebas de parametrización SQL, la respuesta real del servidor, AuthResourceTest y mvn test deben verificarse desde el backend; no quedan demostradas por las pruebas Angular.
```