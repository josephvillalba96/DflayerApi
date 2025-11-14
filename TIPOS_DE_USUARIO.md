# Tipos de Usuario en el Sistema Multiplux

## Explicación de los Tipos de Usuario

### 1. **CLIENT (Cliente)** - `"client"`
**Rol por defecto al registrarse**

**Características:**
- Todos los usuarios se registran como `client` automáticamente
- Usuario normal de la plataforma tipo red social
- Puede interactuar con contenido (likes, comentarios, compartir)
- Puede seguir a otros usuarios
- Puede ganar dinero por interacciones (compartir, ver videos, responder encuestas)
- Puede comprar bonos de comercios
- Puede retirar fondos acumulados

**Permisos actuales en el código:**
- ❌ NO puede crear contenido (actualmente restringido)
- ✅ Puede ver feed personalizado
- ✅ Puede interactuar con contenido
- ✅ Puede gestionar datos fiscales
- ✅ Puede comprar bonos

**Propósito:** Usuario base de la plataforma, consumidor de contenido y participante en la monetización.

---

### 2. **MERCHANT (Comercio)** - `"merchant"`
**Asignado por administradores**

**Características:**
- Comercio o empresa que quiere promocionar productos/servicios
- Puede crear contenido promocional
- Puede crear y vender bonos digitales
- Puede crear campañas publicitarias
- Tiene presupuesto asignado para publicidad y comisiones
- Puede ver analytics de sus campañas

**Permisos actuales en el código:**
- ✅ Puede crear contenido (HU006)
- ✅ Puede crear bonos (HU012)
- ✅ Puede gestionar campañas publicitarias
- ✅ Puede ver dashboard de comercio (HU019)

**Propósito:** Negocios que quieren promocionarse y vender en la plataforma.

---

### 3. **AFFILIATE (Afiliado)** - `"affiliate"`
**Asignado por administradores**

**Características:**
- Creador de contenido o influencer
- Puede crear contenido para promocionar productos
- Puede ganar comisiones por promociones
- Similar a merchant pero enfocado en creación de contenido

**Permisos actuales en el código:**
- ✅ Puede crear contenido (HU006)
- ✅ Puede ver métricas de contenido
- ✅ Puede recibir pagos por contenido promocional

**Propósito:** Creadores de contenido que promocionan productos/servicios de comercios.

---

### 4. **ADMIN (Administrador)** - `"admin"`
**Asignado manualmente en base de datos**

**Características:**
- Control total del sistema
- Puede gestionar usuarios y cambiar sus tipos
- Puede gestionar categorías
- Puede validar identidades de usuarios (HU003)
- Puede gestionar fondos de eventos (HU024)
- Puede ver dashboard administrativo (HU020)
- Puede generar reportes fiscales

**Permisos actuales en el código:**
- ✅ Puede gestionar categorías (crear, actualizar, eliminar)
- ✅ Acceso a endpoints administrativos
- ✅ Puede cambiar tipos de usuario (a implementar)

**Propósito:** Administración y control del sistema.

---

## Situación Actual vs. Propuesta

### ❌ **Situación Actual (Incorrecta):**
- Solo `merchant` y `affiliate` pueden crear contenido
- Los `client` NO pueden crear contenido
- Esto limita la plataforma a solo contenido comercial

### ✅ **Propuesta (Tipo TikTok/Instagram):**
- **TODOS los usuarios** (client, merchant, affiliate, admin) pueden crear contenido
- La diferencia entre tipos sería:
  - **CLIENT**: Crea contenido personal/entretenimiento
  - **MERCHANT**: Crea contenido comercial + puede crear bonos + campañas
  - **AFFILIATE**: Crea contenido promocional + puede recibir comisiones
  - **ADMIN**: Todo lo anterior + permisos administrativos

---

## Recomendación

Para una plataforma tipo TikTok/Instagram donde **todos pueden crear contenido**, deberíamos:

1. **Permitir que todos los tipos de usuario creen contenido**
2. **Mantener las diferencias en otras funcionalidades:**
   - Solo MERCHANT puede crear bonos
   - Solo MERCHANT puede crear campañas publicitarias
   - Solo AFFILIATE puede recibir comisiones por promociones
   - Solo ADMIN puede gestionar categorías y usuarios

¿Quieres que haga este cambio para permitir que todos los usuarios creen contenido?

