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

