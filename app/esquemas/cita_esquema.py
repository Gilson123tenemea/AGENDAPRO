from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


# ── Lo que envía el PACIENTE al reservar ──────────────────────────────
class ReservarCitaEntrada(BaseModel):
    nombre_paciente: str
    telefono_paciente: str
    email_paciente: Optional[str] = None
    inicio: datetime
    motivo: str                              # obligatorio

    @field_validator("nombre_paciente")
    @classmethod
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator("telefono_paciente")
    @classmethod
    def telefono_valido(cls, v):
        digitos = v.replace("+", "").replace(" ", "").replace("-", "")
        if not digitos.isdigit() or len(digitos) < 7:
            raise ValueError("Teléfono inválido — solo números, mínimo 7 dígitos")
        return v

    @field_validator("motivo")
    @classmethod
    def motivo_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("El motivo de consulta es obligatorio")
        return v.strip()

    @field_validator("inicio")
    @classmethod
    def fecha_futura(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("La fecha de la cita debe ser en el futuro")
        return v


# ── Lo que llega al CANCELAR ───────────────────────────────────────────
class CancelarCitaEntrada(BaseModel):
    motivo_cancelacion: Optional[str] = None


# ── Lo que llega al REAGENDAR ──────────────────────────────────────────
class ReagendarCitaEntrada(BaseModel):
    nuevo_inicio: datetime

    @field_validator("nuevo_inicio")
    @classmethod
    def fecha_futura(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("El nuevo horario debe ser en el futuro")
        return v


# ── Lo que llega al MARCAR ASISTENCIA ─────────────────────────────────
class MarcarAsistenciaEntrada(BaseModel):
    asistio: bool


# ── Lo que llega al AGREGAR NOTA ──────────────────────────────────────
class NotaCitaEntrada(BaseModel):
    contenido: str
    es_privada: bool = True


# ── Lo que DEVUELVE la API ─────────────────────────────────────────────
class CitaSalida(BaseModel):
    id: int
    profesional_id: int
    paciente_id: int
    inicio: datetime
    fin: datetime
    estado: str
    motivo: str
    asistio: Optional[bool]
    token_reserva: str
    creado_en: datetime

    model_config = {"from_attributes": True}


class NotaCitaSalida(BaseModel):
    id: int
    contenido: str
    es_privada: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ── Slot disponible para el calendario ────────────────────────────────
class SlotDisponibleSalida(BaseModel):
    inicio: datetime
    fin: datetime