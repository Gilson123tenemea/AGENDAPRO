from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import re


# ── Lo que llega al REGISTRAR ──────────────────────────────────────────
class OrganizacionCrear(BaseModel):
    nombre: str
    slug: str
    email: EmailStr
    telefono: Optional[str] = None
    # Datos del primer usuario admin
    admin_email: EmailStr
    admin_password: str

    @field_validator("slug")
    @classmethod
    def slug_valido(cls, v):
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("El slug solo acepta minúsculas, números y guiones")
        return v

    @field_validator("admin_password")
    @classmethod
    def password_longitud(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        return v


# ── Lo que llega al ACTUALIZAR ─────────────────────────────────────────
class OrganizacionActualizar(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None


# ── Lo que DEVUELVE la API ─────────────────────────────────────────────
class OrganizacionSalida(BaseModel):
    id: int
    nombre: str
    slug: str
    email: str
    telefono: Optional[str]
    logo_url: Optional[str]
    esta_activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}