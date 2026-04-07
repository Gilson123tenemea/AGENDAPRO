from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


class ProfesionalCrear(BaseModel):
    nombre_completo: str
    telefono: Optional[str] = None
    duracion_cita_min: int = 30
    requiere_pago: bool = False
    precio: Optional[float] = None
    email_acceso: EmailStr
    password_acceso: str

    @field_validator("duracion_cita_min")
    @classmethod
    def duracion_valida(cls, v):
        if v < 10 or v > 240:
            raise ValueError("La duración debe estar entre 10 y 240 minutos")
        return v

    @field_validator("precio")
    @classmethod
    def precio_valido(cls, v):
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v


# ── Lo que llega al ACTUALIZAR ─────────────────────────────────────────
class ProfesionalActualizar(BaseModel):
    nombre_completo: Optional[str] = None
    duracion_cita_min: Optional[int] = None
    requiere_pago: Optional[bool] = None
    precio: Optional[float] = None


# ── Lo que DEVUELVE la API ─────────────────────────────────────────────
class ProfesionalSalida(BaseModel):
    id: int
    nombre_completo: str
    telefono: Optional[str]
    token_publico: str
    duracion_cita_min: int
    requiere_pago: bool
    precio: Optional[float]
    promedio_calif: float
    esta_activo: bool
    organizacion_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# ── Lo que ve el PACIENTE (sin datos internos) ─────────────────────────
class ProfesionalPublicoSalida(BaseModel):
    nombre_completo: str
    duracion_cita_min: int
    requiere_pago: bool
    precio: Optional[float]
    promedio_calif: float

    model_config = {"from_attributes": True}