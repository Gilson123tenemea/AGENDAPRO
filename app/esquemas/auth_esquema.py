from pydantic import BaseModel, EmailStr


# ── Lo que llega al HACER LOGIN ────────────────────────────────────────
class LoginEntrada(BaseModel):
    email: EmailStr
    password: str


# ── Lo que DEVUELVE el login ───────────────────────────────────────────
class TokenSalida(BaseModel):
    access_token: str
    refresh_token: str
    tipo_token: str = "bearer"
    rol: str
    organizacion_id: int


# ── Lo que llega al REFRESCAR el token ────────────────────────────────
class RefrescarTokenEntrada(BaseModel):
    refresh_token: str