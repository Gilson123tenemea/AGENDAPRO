from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


# ── Paso 1: datos mínimos al crear (admin llena esto) ─────────────────
class ProfesionalCrear(BaseModel):
    nombre_completo: str
    telefono: Optional[str] = None
    duracion_cita_min: int = 30
    requiere_pago: bool = False
    precio: Optional[float] = None
    email_acceso: EmailStr
    password_acceso: str

    @field_validator("password_acceso")
    @classmethod
    def password_longitud(cls, v):
        if len(v) < 8:
            raise ValueError("Mínimo 8 caracteres")
        return v


# ── Paso 2: perfil completo (el profesional llena esto) ───────────────
class ProfesionalCompletarPerfil(BaseModel):
    foto_url: Optional[str] = None
    titulo_profesional: Optional[str] = None
    descripcion: Optional[str] = None
    experiencia_anios: Optional[int] = None
    educacion: Optional[str] = None
    certificaciones: Optional[str] = None
    idiomas: Optional[str] = None
    atiende_en: Optional[str] = None
    direccion_consultorio: Optional[str] = None


# ── Actualizar datos básicos ──────────────────────────────────────────
class ProfesionalActualizar(BaseModel):
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    duracion_cita_min: Optional[int] = None
    requiere_pago: Optional[bool] = None
    precio: Optional[float] = None


# ── Lo que devuelve la API (panel interno) ────────────────────────────
class ProfesionalSalida(BaseModel):
    id: int
    nombre_completo: str
    telefono: Optional[str]
    foto_url: Optional[str]
    titulo_profesional: Optional[str]
    token_publico: str
    duracion_cita_min: int
    requiere_pago: bool
    precio: Optional[float]
    promedio_calif: float
    total_citas: int
    esta_activo: bool
    perfil_completo: bool
    organizacion_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# ── Lo que ve el paciente (perfil público) ────────────────────────────
class ProfesionalPublicoSalida(BaseModel):
    nombre_completo: str
    foto_url: Optional[str]
    titulo_profesional: Optional[str]
    descripcion: Optional[str]
    experiencia_anios: Optional[int]
    educacion: Optional[str]
    certificaciones: Optional[str]
    idiomas: Optional[str]
    atiende_en: Optional[str]
    direccion_consultorio: Optional[str]
    duracion_cita_min: int
    requiere_pago: bool
    precio: Optional[float]
    promedio_calif: float
    total_citas: int

    model_config = {"from_attributes": True}