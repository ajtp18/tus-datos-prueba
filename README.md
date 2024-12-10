# Proyecto: Plataforma de Eventos con FastAPI y GraphQL

Este proyecto es una plataforma para gestionar eventos, sesiones, usuarios y asistentes. Utiliza **FastAPI** y **Strawberry GraphQL** para manejar las APIs y consultas.

## Tecnologías Principales

- **Backend**: FastAPI con integración de GraphQL mediante Strawberry.
- **Base de Datos**: PostgreSQL gestionada con SQLAlchemy y migraciones mediante Alembic.
- **Mensajería**: Logstash para procesar y enviar datos hacia ElasticSearch.
- **Autenticación**: JSON Web Tokens (JWT) para autenticar usuarios y controlar permisos.
- **Correo**: Envío de correos electrónicos con aiosmtplib.

## Estructura del Proyecto

### Carpeta `app`

#### **Adapters**

Los adapters de GraphQL gestionan las operaciones CRUD a través de consultas y mutaciones. A continuación, se describen los pasos lógicos para cada operación:

1. **Listar elementos**:

   - Endpoint: `list_<entity>`
   - Validaciones: Requiere permisos `list` sobre el recurso.
   - Lógica: Llama al servicio correspondiente para recuperar los elementos desde la base de datos.

2. **Obtener por ID**:

   - Endpoint: `get_<entity>_by_id`
   - Validaciones: Requiere permisos `get` sobre el recurso.
   - Lógica: Verifica que el ID exista en la base de datos antes de devolver los datos.

3. **Crear elemento**:

   - Endpoint: `create_<entity>`
   - Requerimientos:
     - Datos obligatorios para el nuevo elemento.
     - Validaciones específicas, como formato de correo o reglas de negocio.
   - Lógica: Realiza validaciones y luego utiliza el servicio para insertar el elemento en la base de datos.

4. **Actualizar elemento**:

   - Endpoint: `update_<entity>`
   - Requerimientos:
     - ID del elemento a actualizar.
     - Datos a modificar.
   - Validaciones: Verifica permisos `update` y la existencia del recurso.
   - Lógica: Actualiza solo los campos proporcionados.

5. **Eliminar elemento**:

   - Endpoint: `delete_<entity>`
   - Validaciones: Requiere permisos `delete`.
   - Lógica: Realiza una eliminación lógica, marcando el recurso como inactivo.

- \`\`: Define consultas y mutaciones relacionadas con asistentes.
- \`\`: Maneja operaciones de eventos como creación y actualización.
- \`\`: Implementa las operaciones CRUD para sesiones.
- \`\`: Gestión de usuarios, incluyendo autenticación y permisos.

#### **Services**

- \`\`: Lógica para manejar asistentes.
- \`\`: Funciones relacionadas con eventos, incluyendo validación de conflictos y límites.
- \`\`: Gestiona sesiones dentro de eventos.
- \`\`: Lógica para autenticación, gestión de roles y operaciones de usuario.
- \`\`: Administración de permisos y asignación de roles.

#### **Models**

- Define estructuras para manejar datos y respuestas en GraphQL:
  - `AssistantResponse`, `EventResponse`, `SessionResponse`, `UserResponse`.

### Carpeta `config`

Define configuraciones globales como:

- Variables de entorno (`.env`): Configuración de base de datos, correos, ElasticSearch, etc.
- URI de PostgreSQL y ElasticSearch.

### Carpeta `utils`

#### Submódulos:

- \`\`: Manejo de sesiones de base de datos con SQLAlchemy.
- \`\`: Configuración de cliente asíncrono para ElasticSearch.
- \`\`: Creación, validación y control de permisos mediante JWT.
- \`\`: Envío de correos electrónicos con soporte para texto y HTML.
- \`\`: Hashing y verificación de contraseñas utilizando bcrypt.

### Carpeta `alembic`

- \`\`: Configuración para ejecutar migraciones en modo "online" u "offline".
- \`\`: Configuración base de Alembic.

### Carpeta `logstach`

- \`\`: Configuración de Logstash para procesar y cargar eventos en ElasticSearch.
- \`\`: Define la imagen de Docker para ejecutar Logstash.

### Carpeta `test`

Incluye pruebas unitarias para todas las capas del sistema:

- Adapters: `test_assistants.py`, `test_events.py`, `test_sessions.py`, `test_users.py`.
- Utiliza `pytest` y `unittest.mock` para validar los casos de uso y los servicios.

## Configuración Inicial

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/ajtp18/tus-datos-prueba.git
   cd tus_datos_prueba
   ```

2. Instalar dependencias:

   ```bash
   poetry install
   ```

3. Configurar variables de entorno:

   - Crear un archivo `.env` basado en el ejemplo proporcionado.
   - ejemplo:
   - POSTGRES_DB=tusdatos
   - POSTGRES_USER=tusdatos
   - POSTGRES_PASSWORD=tusdatos
   - POSTGRES_HOST=localhost:5432
   - ADMIN_DOMAIN=eventos.com
   - DEBUG=yes
   - COMPOSE_PROJECT_NAME=tusdatos
   - ENABLE_METRICS=true

4. Ejecutar migraciones:

   ```bash
   poetry run python commands.py alembic_migrate | alembic upgrade head
   ```

5. Iniciar el servidor local:
   - crear un entorno virtual
   ```bash
   python -m venv .venv
   
   ```
   - iniciar el servicio
  
   ```bash
   poetry run dev
   ```

## Endpoints Clave

- **GraphQL**: `/graphql`
- **Ping**: `/ping`
- **Login**: `/login`

## Docker

El proyecto incluye un archivo `compose.yaml` para levantar servicios en contenedores:

- FastAPI
- Logstash
- ElasticSearch

Para iniciar los servicios:

```bash
docker-compose up
```

## Licencia

[MIT License](LICENSE)

