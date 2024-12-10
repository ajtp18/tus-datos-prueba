# Documentación de la API

## Login
Por medio de este endpoint puede obtener el token de autenticación para acceder al **GraphQL** y sus recursos. Por defecto, al ejecutar las migraciones se genera un usuario super administrador con las siguientes credenciales:

```json
{
    "email": "admin@admin.com",
    "password": "password"
}
```

Este usuario puede utilizarse para gestionar todos los recursos y realizar pruebas en los métodos de GraphQL.

```http
POST /users/login
Content-Type: application/json

{
    "email": "<email del usuario>",
    "password": "<password del usuario>"
}
```

## GraphQL
El servicio GraphQL está autenticado mediante Bearer token en los headers. Asegúrate de incluir:

```yaml
Authorization: Bearer <token de /login>
```

## Mutaciones y Consultas

### Usuarios
#### Crear Usuario
Esta mutación crea un nuevo usuario en la aplicación.

```graphql
mutation {
    userCreate(
        email: "",
        password: "",
        role: "",
        metadata: {
            full_name: "",
            job: ""
        }
    )
}
```

**Requisitos:**
- **email**: Debe coincidir con el dominio configurado para roles de administrador.
- **password**: Al menos 8 caracteres, incluyendo una mayúscula, una minúscula, un número y un carácter especial.
- **role**: Rol del usuario basado en los slugs disponibles (`user`, `administrator`, etc.).
- **metadata**:
  - **full_name**: Nombre completo del usuario.
  - **job**: Cargo o función del usuario.

**Respuesta esperada:**
```json
{
    "data": {
        "userCreate": "<uuid del usuario creado>"
    }
}
```

#### Actualizar Usuario
Permite actualizar los datos de un usuario existente.

```graphql
mutation {
    userUpdate(
        id: "<uuid del usuario>",
        email: "",
        role: "",
        metadata: {
            full_name: "",
            job: ""
        }
    )
}
```

**Requisitos:**
- **id**: Identificador único del usuario.
- **email**: Nuevo correo electrónico (opcional).
- **role**: Nuevo rol (opcional).
- **metadata**: Información adicional (opcional):
  - **full_name**: Nuevo nombre completo.
  - **job**: Nuevo cargo o función.

#### Eliminar Usuario
Elimina un usuario existente.

```graphql
mutation {
    userDelete(id: "<uuid del usuario>")
}
```

**Requisitos:**
- **id**: Identificador único del usuario.

#### Consultar Usuarios
Obtiene una lista de usuarios registrados.

```graphql
query {
    userList(limit: 10, offset: 0) {
        id
        email
        role {
            slug
        }
        metadata {
            full_name
            job
        }
    }
}
```

**Requisitos:**
- **limit** (opcional): Número máximo de usuarios a devolver.
- **offset** (opcional): Desplazamiento para paginación.


### Asistentes
#### Crear Asistente
Registra un nuevo asistente en un evento.

```graphql
mutation {
    assistantCreate(
        event_id: "<uuid del evento>",
        email: "",
        full_name: "",
        type: 1,
        metadata: {
            theme: ""
        },
        contact_metadata: {
            phone: ""
        }
    )
}
```

**Requisitos:**
- **event_id**: Identificador único del evento.
- **email**: Correo electrónico del asistente.
- **full_name**: Nombre completo del asistente.
- **type**: Tipo de asistente (`1` para ponentes, etc.).
- **metadata**: Información adicional (requerido para ponentes).
- **contact_metadata**:
  - **phone**: Número de teléfono (obligatorio).

#### Actualizar Asistente
Permite modificar los datos de un asistente existente.

```graphql
mutation {
    assistantUpdate(
        id: "<uuid del asistente>",
        email: "",
        full_name: "",
        type: 1,
        metadata: {
            theme: ""
        },
        contact_metadata: {
            phone: ""
        }
    )
}
```

**Requisitos:**
- **id**: Identificador único del asistente.
- **email**: Nuevo correo electrónico (opcional).
- **full_name**: Nuevo nombre completo (opcional).
- **type**: Nuevo tipo de asistente (opcional).
- **metadata**: Nueva información adicional (opcional).
- **contact_metadata**: Nuevo número de contacto (opcional).

#### Eliminar Asistente
Elimina un asistente existente de un evento.

```graphql
mutation {
    assistantDelete(id: "<uuid del asistente>")
}
```

**Requisitos:**
- **id**: Identificador único del asistente.

### Eventos
#### Crear Evento
Esta mutación permite crear un nuevo evento.

```graphql
mutation {
    eventCreate(
        title: "",
        description: "",
        start_date: "",
        end_date: "",
        meta: {},
        assitant_limit: 20
    )
}
```

**Requisitos:**
- **title**: Título del evento.
- **description**: Descripción (máximo 500 palabras).
- **start_date** y **end_date**: Fechas en formato ISO (el fin debe ser mayor al inicio).
- **assitant_limit**: Mínimo 10 asistentes permitidos.

#### Actualizar Evento
Permite modificar los datos de un evento existente.

```graphql
mutation {
    eventUpdate(
        id: "<uuid del evento>",
        title: "",
        description: "",
        start_date: "",
        end_date: "",
        meta: {},
        assitant_limit: 50,
        status: 1
    )
}
```

**Requisitos:**
- **id**: Identificador único del evento.
- **title**: Nuevo título del evento (opcional).
- **description**: Nueva descripción (opcional).
- **start_date** y **end_date**: Nuevas fechas (opcional).
- **meta**: Nueva metadata del evento (opcional).
- **assitant_limit**: Nuevo límite de asistentes (opcional).
- **status**: Nuevo estado del evento (`1`: En progreso, etc.).

#### Eliminar Evento
Elimina un evento existente.

```graphql
mutation {
    eventDelete(id: "<uuid del evento>")
}
```

**Requisitos:**
- **id**: Identificador único del evento.

### Sesiones
#### Crear Sesión
Permite crear una sesión dentro de un evento.

```graphql
mutation {
    sessionCreate(
        event_id: "<uuid del evento>",
        title: "",
        description: "",
        start_date: "",
        end_date: "",
        meta: {},
        speaker_id: "<uuid del ponente>"
    )
}
```

**Requisitos:**
- **event_id**: Identificador del evento.
- **title**: Título de la sesión.
- **description**: Descripción (máximo 500 palabras).
- **start_date** y **end_date**: Fechas en formato ISO dentro del rango del evento.
- **speaker_id**: Identificador único del ponente (debe ser tipo `SPEAKER`).

#### Actualizar Sesión
Permite modificar los datos de una sesión existente.

```graphql
mutation {
    sessionUpdate(
        id: "<uuid de la sesión>",
        title: "",
        description: "",
        start_date: "",
        end_date: "",
        meta: {},
        speaker_id: "<uuid del ponente>"
    )
}
```

**Requisitos:**
- **id**: Identificador único de la sesión.
- **title**: Nuevo título de la sesión (opcional).
- **description**: Nueva descripción (opcional).
- **start_date** y **end_date**: Nuevas fechas de la sesión (opcional).
- **meta**: Nueva metadata asociada (opcional).
- **speaker_id**: Nuevo identificador del ponente asignado (opcional).

#### Eliminar Sesión
Elimina una sesión existente de un evento.

```graphql
mutation {
    sessionDelete(id: "<uuid de la sesión>")
}
```

**Requisitos:**
- **id**: Identificador único de la sesión.

### Consultar Documentación

Para más información, visita los endpoints adicionales:

- **Graphql**: `/graphql`
- **Prometheus Metrics**: `/metrics`

