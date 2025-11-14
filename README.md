# DflayerApi

API REST desarrollada con FastAPI para el proyecto **Multiplux** - Plataforma de monetización de contenido.

## 📋 Descripción

DflayerApi es la capa de backend que gestiona toda la lógica de negocio del proyecto Multiplux, incluyendo:

- Gestión de usuarios (afiliados, comercios, administradores)
- Gestión de contenidos y monetización
- Sistema de bonos y transacciones
- Planes multiplicadores
- Distribución de fondos por niveles

## 🏗️ Estructura del Proyecto

```
DflayerApi/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación principal FastAPI
│   ├── dependencies.py         # Dependencias comunes
│   ├── api/
│   │   ├── v1/                 # API versión 1
│   │   │   ├── api.py          # Router principal v1
│   │   │   └── endpoints/      # Endpoints por dominio
│   │   │       ├── health.py
│   │   │       ├── usuarios.py
│   │   │       └── comercios.py
│   ├── core/
│   │   ├── config.py           # Configuración de la app
│   │   └── security.py         # Utilidades de seguridad
│   ├── models/                 # Modelos SQLAlchemy
│   │   └── base.py
│   ├── schemas/                # Schemas Pydantic
│   │   └── base.py
│   ├── services/               # Lógica de negocio
│   │   └── base.py
│   ├── db/                     # Configuración de BD
│   │   └── base.py
│   └── utils/                  # Utilidades
│       └── helpers.py
├── tests/                      # Tests del proyecto
│   └── test_api/
├── .env.example                # Ejemplo de variables de entorno
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clonar el repositorio** (si aplica) o navegar al directorio:
```bash
cd DflayerApi
```

2. **Crear un entorno virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar la aplicación**:
```bash
uvicorn app.main:app --reload
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## 🐳 Docker

El proyecto está completamente dockerizado y listo para ejecutarse con Docker Compose, incluyendo PostgreSQL.

### Prerrequisitos

- Docker 20.10 o superior
- Docker Compose 2.0 o superior

### Inicio Rápido con Docker

1. **Configurar variables de entorno** (opcional):
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

2. **Construir y levantar los servicios**:
```bash
docker-compose up -d --build
```

Esto levantará:
- **PostgreSQL** en el puerto 5432 (configurable)
- **FastAPI API** en el puerto 8000

3. **Ver los logs**:
```bash
# Ver todos los logs
docker-compose logs -f

# Ver solo logs de la API
docker-compose logs -f api

# Ver solo logs de la base de datos
docker-compose logs -f db
```

4. **Detener los servicios**:
```bash
docker-compose down
```

5. **Detener y eliminar volúmenes** (incluye datos de BD):
```bash
docker-compose down -v
```

### Comandos Útiles de Docker

```bash
# Reconstruir solo la API
docker-compose build api

# Reiniciar un servicio específico
docker-compose restart api

# Ejecutar comandos dentro del contenedor
docker-compose exec api bash
docker-compose exec db psql -U dflayer_user -d dflayer_db

# Ver estado de los servicios
docker-compose ps

# Ejecutar migraciones manualmente
docker-compose exec api alembic upgrade head

# Crear una nueva migración
docker-compose exec api alembic revision --autogenerate -m "Migration name"
```

### Configuración de Docker Compose

El archivo `docker-compose.yml` incluye:

- **Servicio `db`**: PostgreSQL 16 Alpine
  - Puerto: 5432 (configurable con `POSTGRES_PORT`)
  - Usuario: `dflayer_user` (configurable)
  - Base de datos: `dflayer_db` (configurable)
  - Volumen persistente para datos
  - Health check configurado

- **Servicio `api`**: FastAPI Application
  - Puerto: 8000 (configurable con `API_PORT`)
  - Auto-reload en desarrollo
  - Ejecuta migraciones automáticamente al iniciar
  - Conectado a PostgreSQL automáticamente

### Variables de Entorno para Docker

Puedes configurar las siguientes variables en tu archivo `.env`:

```bash
# PostgreSQL
POSTGRES_USER=dflayer_user
POSTGRES_PASSWORD=dflayer_password
POSTGRES_DB=dflayer_db
POSTGRES_PORT=5432

# API
API_PORT=8000

# Otras variables (ver .env.example)
```

### Producción con Docker

Para producción, usa el archivo `docker-compose.prod.yml`:

```bash
# Construir y levantar en modo producción
docker-compose -f docker-compose.prod.yml up -d --build
```

**Diferencias en producción**:
- No monta código local (usa la imagen)
- Restart policy: `always`
- Variables de entorno deben estar todas configuradas
- Base de datos solo expuesta en localhost

### Estructura de Docker

```
DflayerApi/
├── Dockerfile              # Imagen de la aplicación
├── .dockerignore           # Archivos a ignorar en build
├── docker-compose.yml      # Desarrollo
└── docker-compose.prod.yml # Producción
```

### Troubleshooting Docker

**Problema**: El contenedor de la API no puede conectarse a la base de datos
```bash
# Verificar que la BD esté saludable
docker-compose ps
docker-compose logs db

# Verificar la URL de conexión
docker-compose exec api env | grep DATABASE_URL
```

**Problema**: Las migraciones fallan
```bash
# Ejecutar migraciones manualmente
docker-compose exec api alembic upgrade head

# Ver logs de migraciones
docker-compose logs api | grep -i migration
```

**Problema**: Puerto ya en uso
```bash
# Cambiar el puerto en .env
API_PORT=8001
POSTGRES_PORT=5433

# Recrear servicios
docker-compose down
docker-compose up -d
```

## 📚 Versionado de API

El proyecto utiliza versionado de API mediante prefijos de ruta:

- **v1**: `/api/v1/*` - Versión actual
- **v2**: `/api/v2/*` - Futuras versiones

Esto permite mantener compatibilidad con versiones anteriores mientras se desarrollan nuevas funcionalidades.

## 🔧 Configuración

### Variables de Entorno

Las principales variables de entorno se configuran en el archivo `.env`:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `PROJECT_NAME` | Nombre del proyecto | DflayerApi |
| `VERSION` | Versión de la API | 0.1.0 |
| `API_V1_STR` | Prefijo de la API v1 | /api/v1 |
| `SECRET_KEY` | Clave secreta para JWT | (generar una segura) |
| `DATABASE_URL` | URL de conexión a BD | postgresql://user:pass@localhost/db |
| `BACKEND_CORS_ORIGINS` | Orígenes permitidos CORS | http://localhost:3000 |
| `DEBUG` | Modo debug | True/False |

### Configuración de Email

El sistema soporta dos proveedores de email: **SMTP** (Gmail compatible) y **SendGrid**. Por defecto, el sistema usa **SMTP**. Puedes cambiar el proveedor mediante la variable `EMAIL_PROVIDER` en tu archivo `.env`.

#### Usando SMTP (Gmail) - **Predeterminado**

El sistema usa SMTP por defecto. Para configurar Gmail o cualquier servidor SMTP compatible, configura las siguientes variables en tu `.env`:

```bash
# Seleccionar SMTP como proveedor (ya es el predeterminado)
EMAIL_PROVIDER=smtp

# Configuración SMTP para Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password-de-gmail
SMTP_FROM_EMAIL=tu-email@gmail.com
SMTP_FROM_NAME=DflayerApi
SMTP_USE_TLS=True
```

**Nota:** Si no configuras `EMAIL_PROVIDER`, el sistema usará SMTP automáticamente.

**Configuración de Gmail:**

1. **Habilitar verificación en 2 pasos** en tu cuenta de Google
2. **Generar una Contraseña de aplicación**:
   - Ve a [Google Account Settings](https://myaccount.google.com/)
   - Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones
   - Genera una nueva contraseña para "Correo"
   - Usa esta contraseña en `SMTP_PASSWORD` (no tu contraseña regular)

**Otros proveedores SMTP:**

- **Outlook/Hotmail**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Servidor personalizado**: Configura `SMTP_SERVER` y `SMTP_PORT` según tu proveedor

#### Usando SendGrid

Para usar SendGrid como proveedor de email:

```bash
# Seleccionar SendGrid como proveedor
EMAIL_PROVIDER=sendgrid

# Configuración SendGrid
SENDGRID_API_KEY=tu-api-key-de-sendgrid
SENDGRID_FROM_EMAIL=noreply@tudominio.com
SENDGRID_FROM_NAME=DflayerApi
```

**Obtener API Key de SendGrid:**

1. Crea una cuenta en [SendGrid](https://sendgrid.com/)
2. Ve a Settings → API Keys
3. Crea una nueva API Key con permisos de "Mail Send"
4. Copia la API Key y úsala en `SENDGRID_API_KEY`

#### Servicio Unificado

El sistema usa automáticamente el proveedor configurado en `EMAIL_PROVIDER`. El servicio unificado (`UnifiedEmailService`) selecciona automáticamente entre SMTP y SendGrid según tu configuración.

**Archivos relacionados:**
- `app/services/email_smtp_service.py` - Servicio SMTP
- `app/services/email_service.py` - Servicio SendGrid
- `app/services/email_service_factory.py` - Factory para selección automática

## 📖 Endpoints Principales

### Health Check
- `GET /health` - Verificación básica de salud
- `GET /api/v1/health/` - Health check detallado

### Usuarios (En desarrollo)
- `GET /api/v1/usuarios/` - Listar usuarios
- `GET /api/v1/usuarios/{id}` - Obtener usuario
- `POST /api/v1/usuarios/` - Crear usuario

### Comercios (En desarrollo)
- `GET /api/v1/comercios/` - Listar comercios
- `GET /api/v1/comercios/{id}` - Obtener comercio
- `POST /api/v1/comercios/` - Crear comercio

## 🧪 Testing

Ejecutar tests con pytest:

```bash
pytest
```

Ejecutar tests con cobertura:

```bash
pytest --cov=app tests/
```

## 🏛️ Arquitectura

El proyecto sigue una arquitectura limpia y modular:

- **API Layer**: Endpoints y routers (`app/api/`)
- **Business Logic**: Servicios (`app/services/`)
- **Data Layer**: Modelos y acceso a datos (`app/models/`, `app/db/`)
- **Schemas**: Validación y serialización (`app/schemas/`)
- **Core**: Configuración y utilidades centrales (`app/core/`)

## 📝 Buenas Prácticas Implementadas

✅ **Separación de responsabilidades**: Cada capa tiene su propósito específico  
✅ **Versionado de API**: Facilita evolución sin romper compatibilidad  
✅ **Type hints**: Uso de tipos para mejor mantenibilidad  
✅ **Schemas Pydantic**: Validación automática de datos  
✅ **Configuración centralizada**: Variables de entorno con Pydantic Settings  
✅ **Seguridad**: JWT, hashing de contraseñas, CORS configurado  
✅ **Documentación automática**: Swagger/OpenAPI integrado  
✅ **Testing**: Estructura preparada para tests  

## 🔐 Seguridad

- Autenticación JWT implementada
- Hashing de contraseñas con bcrypt
- CORS configurado
- Variables sensibles en `.env` (no commitear)

## 📦 Dependencias Principales

- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para base de datos
- **Pydantic**: Validación de datos
- **python-jose**: Manejo de tokens JWT
- **passlib**: Hashing de contraseñas

## 🗄️ Base de Datos

La configuración de base de datos está preparada para usar SQLAlchemy. Actualmente se requiere configurar `DATABASE_URL` en el archivo `.env`.

Modelos de base de datos se definirán en `app/models/` según el esquema del proyecto Multiplux.

### Migraciones con Alembic

El proyecto utiliza **Alembic** para gestionar las migraciones de base de datos de forma versionada y controlada.

#### 📋 Configuración

Alembic está completamente configurado y listo para usar:

- **Archivo de configuración**: `alembic.ini`
- **Directorio de migraciones**: `alembic/`
- **Versiones de migraciones**: `alembic/versions/`
- **Configuración del entorno**: `alembic/env.py`

#### 🚀 Uso Básico

##### 1. Inicializar Alembic (ya está inicializado)
```bash
# Si necesitas reinicializar (no necesario si ya está configurado)
alembic init alembic
```

##### 2. Configurar Base de Datos

**IMPORTANTE**: Antes de generar migraciones, debes configurar `DATABASE_URL` en tu archivo `.env`:

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y configurar DATABASE_URL
# Para PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/dflayer_db

# Para SQLite (desarrollo):
DATABASE_URL=sqlite:///./app.db
```

Si no configuras `DATABASE_URL`, Alembic usará una base de datos SQLite temporal por defecto.

##### 3. Crear una Migración Inicial
```bash
# Genera la migración inicial basada en todos los modelos
alembic revision --autogenerate -m "Initial migration"
```

Esto creará un archivo en `alembic/versions/` con todas las tablas basadas en los modelos SQLAlchemy.

##### 4. Revisar la Migración Generada
```bash
# Ver el contenido de la última migración generada
# Edita el archivo en alembic/versions/ si necesitas ajustes
```

**Importante**: Siempre revisa las migraciones autogeneradas antes de aplicarlas, especialmente:
- Verifica que las relaciones y foreign keys estén correctas
- Revisa los tipos de datos
- Confirma que los índices y constraints sean correctos

##### 5. Aplicar Migraciones
```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar hasta una versión específica
alembic upgrade <revision_id>

# Ver el estado actual de las migraciones
alembic current

# Ver el historial de migraciones
alembic history
```

##### 6. Revertir Migraciones
```bash
# Revertir la última migración
alembic downgrade -1

# Revertir hasta una versión específica
alembic downgrade <revision_id>

# Revertir todas las migraciones
alembic downgrade base
```

#### 🔄 Flujo de Trabajo Recomendado

##### Desarrollo de Nuevas Funcionalidades

1. **Crear o modificar modelos** en `app/models/`
2. **Generar migración automática**:
   ```bash
   alembic revision --autogenerate -m "Add new feature models"
   ```
3. **Revisar la migración generada** en `alembic/versions/`
4. **Aplicar la migración**:
   ```bash
   alembic upgrade head
   ```
5. **Verificar** que todo funcione correctamente

##### Ejemplo Completo

```bash
# 1. Modificas un modelo (ej: agregas un campo a User)
# app/models/user.py
# ... agregas nuevo campo ...

# 2. Generas la migración
alembic revision --autogenerate -m "Add phone_number to users"

# 3. Revisas el archivo generado
# alembic/versions/xxxx_add_phone_number_to_users.py

# 4. Aplicas la migración
alembic upgrade head

# 5. Verificas el estado
alembic current
```

#### 📝 Comandos Útiles

##### Crear Migración Manual
```bash
# Si necesitas crear una migración sin autogenerar
alembic revision -m "Custom migration description"
```

##### Ver Diferencias
```bash
# Ver qué cambios detecta Alembic sin crear migración
alembic check
```

##### Generar SQL sin Aplicar
```bash
# Generar SQL de la migración sin ejecutarla
alembic upgrade head --sql
```

##### Migración a Versión Específica
```bash
# Ver todas las revisiones disponibles
alembic history

# Migrar a una revisión específica
alembic upgrade <revision_id>
alembic downgrade <revision_id>
```

#### ⚙️ Configuración Avanzada

##### Variables de Entorno

Alembic usa automáticamente `DATABASE_URL` de tu archivo `.env`:

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost/dflayer_db
```

##### Personalizar la Configuración

El archivo `alembic/env.py` está configurado para:
- ✅ Importar automáticamente todos los modelos
- ✅ Usar `DATABASE_URL` de settings
- ✅ Generar migraciones basadas en `Base.metadata`

##### Estructura de Archivos de Migración

Cada migración en `alembic/versions/` contiene:

```python
"""Add new feature

Revision ID: abc123
Revises: xyz789
Create Date: 2024-01-15 10:30:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'xyz789'

def upgrade():
    # Cambios a aplicar
    op.add_column('users', sa.Column('phone_number', sa.String(20)))

def downgrade():
    # Cambios a revertir
    op.drop_column('users', 'phone_number')
```

#### 🚨 Mejores Prácticas

1. **Siempre revisa las migraciones autogeneradas** antes de aplicarlas
2. **Usa mensajes descriptivos** en las migraciones: `-m "Add user phone number"`
3. **Haz backup de la BD** antes de aplicar migraciones en producción
4. **Prueba las migraciones** en un entorno de desarrollo primero
5. **No edites migraciones ya aplicadas** - crea nuevas migraciones
6. **Mantén las migraciones pequeñas** - una funcionalidad por migración
7. **Documenta migraciones complejas** con comentarios en el código

#### 🔍 Troubleshooting

##### Error: "Target database is not up to date"
```bash
# Ver el estado actual
alembic current

# Aplicar migraciones pendientes
alembic upgrade head
```

##### Error: "Can't locate revision identified by 'xxxx'"
```bash
# Ver el historial completo
alembic history

# Verificar la cadena de revisiones
alembic branches
alembic heads
```

##### Autogenerate no detecta cambios
```bash
# Asegúrate de que:
# 1. Los modelos están importados en alembic/env.py
# 2. Los modelos heredan de Base
# 3. La base de datos está actualizada
alembic check
```

##### Resetear migraciones (solo desarrollo)
```bash
# ⚠️ SOLO EN DESARROLLO - Esto elimina todas las migraciones
# 1. Eliminar todas las tablas manualmente
# 2. Eliminar archivos en alembic/versions/ (excepto .gitkeep)
# 3. Crear nueva migración inicial
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

#### 📊 Modelos Soportados

Alembic está configurado para detectar automáticamente cambios en todos los modelos:

- ✅ Location, TaxData, User
- ✅ Category, Content, Hashtag, ContentHashtag
- ✅ ContentMetrics, MultimediaFile, FileVersion
- ✅ TranscodingJob, TranscodingProfile, TranscodingQueue, TranscodingLog
- ✅ Follow, Like, Comment
- ✅ MonetizableAction, Interaction
- ✅ Transaction, PaymentDistribution, DistributionLevel
- ✅ Voucher, MultiplierPlan, UserPlan
- ✅ Notification, FeedItem
- ✅ UserPreferences, UserCategory
- ✅ EventFund, AdvertisingCampaign, SalesCommission

Todos los modelos están importados en `alembic/env.py` para autogeneración.

## 🎬 Sistema de Transcodificación

El sistema de transcodificación permite convertir videos y audio a diferentes formatos, resoluciones y calidades para optimizar la entrega de contenido multimedia.

### 📋 Descripción General

Cuando un usuario sube un archivo multimedia (video o audio), el sistema automáticamente:

1. **Almacena el archivo original** en S3
2. **Crea trabajos de transcodificación** para generar múltiples versiones
3. **Procesa las versiones** según perfiles predefinidos
4. **Gestiona la cola de procesamiento** con prioridades
5. **Genera logs detallados** de cada proceso
6. **Almacena las versiones transcodificadas** en S3

### 🏗️ Arquitectura del Sistema

```
┌─────────────────┐
│  MultimediaFile │ (Archivo original subido)
│   (Original)    │
└────────┬────────┘
         │
         │ Crea
         ▼
┌─────────────────┐
│ TranscodingJob  │ (Trabajo de transcodificación)
│  + Profile      │
└────────┬────────┘
         │
         │ Se encola
         ▼
┌─────────────────┐
│TranscodingQueue │ (Cola de procesamiento)
└────────┬────────┘
         │
         │ Procesa
         ▼
┌─────────────────┐
│  Worker/FFmpeg  │ (Procesador de transcodificación)
└────────┬────────┘
         │
         │ Genera
         ▼
┌─────────────────┐
│  MultimediaFile │ (Versión transcodificada)
│   (Transcoded)  │
└─────────────────┘
```

### 📊 Modelos Involucrados

#### 1. **TranscodingJob**
Gestiona cada trabajo de transcodificación individual.

**Estados del Job:**
- `PENDING`: Esperando ser procesado
- `QUEUED`: En cola de procesamiento
- `PROCESSING`: Actualmente siendo procesado
- `COMPLETED`: Transcodificación completada exitosamente
- `FAILED`: Error en la transcodificación
- `CANCELLED`: Trabajo cancelado

**Prioridades:**
- `LOW`: Baja prioridad
- `NORMAL`: Prioridad normal (default)
- `HIGH`: Alta prioridad
- `URGENT`: Urgente (procesar inmediatamente)

**Información rastreada:**
- Progreso (0-100%)
- Tiempos de inicio y finalización
- Tiempo estimado de finalización
- Archivo fuente y archivo de salida
- Errores y reintentos
- Worker que procesa el job

#### 2. **TranscodingProfile**
Define configuraciones reutilizables de transcodificación.

**Configuraciones de Video:**
- Codec: h264, h265, vp9, etc.
- Bitrate: kbps
- Resolución: ancho x alto (1920x1080, 1280x720, etc.)
- FPS: Frames por segundo
- Keyframe interval: Tamaño del GOP

**Configuraciones de Audio:**
- Codec: aac, mp3, opus, etc.
- Bitrate: kbps
- Sample rate: Hz
- Canales: mono, estéreo, etc.

**Otras Configuraciones:**
- Formato de contenedor: mp4, webm, mkv
- Preset de calidad: fast, medium, slow
- CRF (Constant Rate Factor)
- Generación de thumbnails
- Soporte HLS/DASH para streaming

**Ejemplos de Perfiles Predefinidos:**
- `1080p_h264`: Video 1080p con H.264, audio AAC
- `720p_h264`: Video 720p con H.264, audio AAC
- `480p_h264`: Video 480p con H.264, audio AAC
- `360p_h264`: Video 360p con H.264, audio AAC
- `hls_master`: Perfil maestro para HLS con múltiples calidades

#### 3. **TranscodingQueue**
Gestiona la cola de trabajos pendientes.

- Priorización automática según `priority` del job
- Timestamps de encolado e inicio
- Permite procesamiento en paralelo de múltiples workers

#### 4. **TranscodingLog**
Registra todos los eventos y logs del proceso.

**Niveles de Log:**
- `INFO`: Información general
- `WARNING`: Advertencias
- `ERROR`: Errores
- `DEBUG`: Información de depuración

### 🔄 Flujo de Transcodificación Completo

#### Paso 1: Subida de Archivo
```python
# Usuario sube un video
multimedia_file = MultimediaFile(
    content_id=content.content_id,
    file_type=FileType.VIDEO,
    bucket_name="my-bucket",
    s3_key="uploads/video_123_original.mp4",
    format="mp4",
    # ... metadata
)
```

#### Paso 2: Creación de Trabajos de Transcodificación
```python
# Sistema crea trabajos para múltiples calidades
profiles = [
    TranscodingProfile.get_by_name("1080p_h264"),
    TranscodingProfile.get_by_name("720p_h264"),
    TranscodingProfile.get_by_name("480p_h264"),
]

for profile in profiles:
    job = TranscodingJob(
        source_file_id=multimedia_file.file_id,
        profile_id=profile.profile_id,
        priority=TranscodingPriority.NORMAL,
        status=TranscodingStatus.PENDING
    )
    # Se encola automáticamente
```

#### Paso 3: Procesamiento en Cola
```python
# Worker toma el job de la cola
job = TranscodingQueue.get_next_job()
job.status = TranscodingStatus.PROCESSING
job.started_at = datetime.utcnow()
job.worker_id = "worker-001"

# Procesa con FFmpeg o servicio externo
# Actualiza progreso periódicamente
job.progress_percentage = 45.0
```

#### Paso 4: Generación de Versión Transcodificada
```python
# Al completar, se crea el archivo transcodificado
output_file = MultimediaFile(
    content_id=content.content_id,
    file_type=FileType.VIDEO,
    bucket_name="my-bucket",
    s3_key="transcoded/video_123_720p.mp4",
    format="mp4",
    resolution="720p",
    # ... metadata de la versión transcodificada
)

# Se actualiza el job
job.status = TranscodingStatus.COMPLETED
job.output_file_id = output_file.file_id
job.completed_at = datetime.utcnow()
job.progress_percentage = 100.0
```

#### Paso 5: Generación de Thumbnails
```python
# Si el perfil tiene generate_thumbnail=True
# Se crean trabajos adicionales para thumbnails
thumbnail_job = TranscodingJob(
    source_file_id=multimedia_file.file_id,
    profile_id=thumbnail_profile.profile_id,
    # Genera thumbnails cada X segundos
)
```

### 🎯 Casos de Uso

#### 1. Streaming Adaptativo (HLS/DASH)
```python
# Crear perfil maestro HLS
hls_profile = TranscodingProfile(
    name="hls_master",
    enable_hls=True,
    segment_duration=10,  # 10 segundos por segmento
    # Genera múltiples calidades
)

# El sistema genera:
# - master.m3u8 (playlist maestro)
# - video_1080p.m3u8 + segmentos
# - video_720p.m3u8 + segmentos
# - video_480p.m3u8 + segmentos
```

#### 2. Optimización para Móviles
```python
# Perfil optimizado para móviles
mobile_profile = TranscodingProfile(
    name="mobile_optimized",
    resolution_width=640,
    resolution_height=360,
    video_bitrate=800,  # Bajo bitrate para ahorrar datos
    audio_bitrate=64,
    container_format="mp4"
)
```

#### 3. Procesamiento en Lote
```python
# Procesar múltiples videos con prioridad alta
for video in pending_videos:
    job = TranscodingJob(
        source_file_id=video.file_id,
        profile_id=standard_profile.profile_id,
        priority=TranscodingPriority.HIGH
    )
```

### ⚙️ Configuración

#### Variables de Entorno Necesarias

```bash
# AWS S3 para almacenamiento
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET_NAME=multimedia-bucket

# Transcodificación
TRANSCODING_WORKER_COUNT=4  # Número de workers paralelos
TRANSCODING_MAX_RETRIES=3   # Reintentos en caso de error
TRANSCODING_QUEUE_SIZE=100  # Tamaño máximo de cola

# FFmpeg (si se usa procesamiento local)
FFMPEG_PATH=/usr/bin/ffmpeg
FFPROBE_PATH=/usr/bin/ffprobe

# O AWS MediaConvert (si se usa servicio AWS)
AWS_MEDIACONVERT_ROLE_ARN=arn:aws:iam::...
AWS_MEDIACONVERT_QUEUE=default
```

### 🔧 Integración con Procesadores

El sistema soporta múltiples procesadores de transcodificación:

#### 1. **FFmpeg (Local/EC2)**
```python
# Procesamiento con FFmpeg
ffmpeg_command = f"""
ffmpeg -i {input_file} 
  -c:v libx264 
  -preset medium 
  -crf 23 
  -c:a aac 
  -b:a 128k 
  {output_file}
"""
```

#### 2. **AWS MediaConvert**
```python
# Procesamiento con AWS MediaConvert
# Se crea un job en MediaConvert
# El sistema rastrea el estado del job
# Al completar, se descarga el resultado a S3
```

#### 3. **Servicios Externos**
```python
# Integración con servicios como:
# - Cloudinary
# - Mux
# - Zencoder
# - Bitmovin
```

### 📈 Monitoreo y Logs

#### Consultar Estado de un Job
```python
job = TranscodingJob.get(job_id)
print(f"Estado: {job.status}")
print(f"Progreso: {job.progress_percentage}%")
print(f"Tiempo estimado: {job.estimated_completion}")
```

#### Ver Logs de un Job
```python
logs = TranscodingLog.filter_by(job_id=job_id)
for log in logs:
    print(f"[{log.log_level}] {log.message}")
```

#### Estadísticas de Transcodificación
```python
# Jobs completados hoy
completed_today = TranscodingJob.filter(
    status=TranscodingStatus.COMPLETED,
    completed_at >= today
).count()

# Tiempo promedio de procesamiento
avg_time = TranscodingJob.filter(
    status=TranscodingStatus.COMPLETED
).avg('processing_time_seconds')
```

### 🚨 Manejo de Errores

El sistema incluye manejo robusto de errores:

1. **Reintentos Automáticos**: Hasta 3 intentos por defecto
2. **Logs Detallados**: Cada error se registra con código y mensaje
3. **Notificaciones**: Se pueden enviar notificaciones en caso de fallos críticos
4. **Recuperación**: Los jobs fallidos pueden ser reprocesados manualmente

```python
# Reprocesar un job fallido
failed_job = TranscodingJob.get(job_id)
if failed_job.status == TranscodingStatus.FAILED:
    failed_job.status = TranscodingStatus.PENDING
    failed_job.retry_count = 0
    failed_job.error_message = None
    # Se vuelve a encolar
```

### 🎨 Mejores Prácticas

1. **Crear Perfiles Predefinidos**: Define perfiles comunes al inicio
2. **Priorizar Contenido Importante**: Usa `URGENT` para contenido destacado
3. **Monitorear la Cola**: Evita que la cola se sature
4. **Optimizar para el Caso de Uso**: Diferentes perfiles para diferentes necesidades
5. **Generar Thumbnails**: Siempre genera thumbnails para previews
6. **Usar CDN**: Configura CDN para servir archivos transcodificados

### 📝 Ejemplo Completo

```python
# 1. Usuario sube video
original_file = upload_video_to_s3(video_file)

# 2. Sistema crea trabajos automáticamente
profiles = get_standard_profiles()  # 1080p, 720p, 480p
for profile in profiles:
    create_transcoding_job(original_file, profile)

# 3. Worker procesa (automático)
# El sistema actualiza progreso y estado

# 4. Al completar, se pueden servir las versiones
content = Content.get(content_id)
versions = content.multimedia_files.filter(
    MultimediaFile.file_id != original_file.file_id
)

# 5. Cliente selecciona versión según ancho de banda
if bandwidth > 5000:  # 5 Mbps
    serve_version(versions.filter(resolution="1080p"))
elif bandwidth > 2500:  # 2.5 Mbps
    serve_version(versions.filter(resolution="720p"))
else:
    serve_version(versions.filter(resolution="480p"))
```

## 📅 Próximos Pasos

- [ ] Implementar modelos de base de datos según el esquema ER
- [ ] Implementar autenticación y autorización completa
- [ ] Crear endpoints CRUD para todas las entidades
- [ ] Implementar lógica de negocio (monetización, distribución, etc.)
- [ ] Agregar tests unitarios y de integración
- [ ] Configurar migraciones de base de datos (Alembic)
- [ ] Implementar logging estructurado
- [ ] Configurar CI/CD

## 🤝 Contribución

Este es un proyecto en desarrollo. La documentación se actualizará conforme avance el desarrollo.

## 📄 Licencia

[Especificar licencia si aplica]

---

**Versión**: 0.1.0  
**Última actualización**: 2024

