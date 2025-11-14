"""
Utilidades de seguridad: autenticación, autorización, tokens JWT
"""
import warnings
import logging
import sys
import io

# Solución para el error de compatibilidad entre passlib 1.7.4 y bcrypt 4.1.2
# passlib intenta leer bcrypt.__about__.__version__ que no existe en bcrypt 4.1.2
# Agregamos un monkey patch para evitar el error
try:
    import bcrypt
    # Agregar el atributo __about__ si no existe (para compatibilidad con passlib)
    if not hasattr(bcrypt, '__about__'):
        class _BcryptAbout:
            __version__ = getattr(bcrypt, '__version__', '4.1.2')
        bcrypt.__about__ = _BcryptAbout()
except ImportError:
    pass

# Suprimir warnings relacionados con bcrypt
warnings.filterwarnings("ignore", message=".*bcrypt.*")
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

# Configurar logger de passlib
logging.getLogger("passlib").setLevel(logging.ERROR)

# Redirigir stderr temporalmente durante la importación de passlib para evitar el traceback
_old_stderr = sys.stderr
sys.stderr = io.StringIO()

try:
    from passlib.context import CryptContext
finally:
    # Restaurar stderr
    sys.stderr = _old_stderr

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

# Configurar CryptContext con bcrypt
# bcrypt__rounds=12 es compatible con bcrypt 4.1.2 y passlib 1.7.4
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica y valida un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

