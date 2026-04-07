from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encriptar_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(plano: str, hasheado: str) -> bool:
    return pwd_context.verify(plano, hasheado)

def crear_access_token(datos: dict) -> str:
    payload = datos.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_MIN), "tipo": "access"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def crear_refresh_token(datos: dict) -> str:
    payload = datos.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(days=REFRESH_DAYS), "tipo": "refresh"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None