from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class PacienteSalida(BaseModel):
    id: int
    nombre_completo: str
    telefono: str
    email: Optional[str]
    notas: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}


class PacienteActualizar(BaseModel):
    notas: Optional[str] = None

class CitaResumenSalida(BaseModel):
    id: int
    inicio: datetime
    fin: datetime
    motivo: str
    estado: str
    asistio: Optional[bool] = None
    motivo_cancelacion: Optional[str] = None
    model_config = {"from_attributes": True}


class HistorialPacienteSalida(BaseModel):
    citas: list[CitaResumenSalida]
    total: int
    completadas: int
    no_asistio: int
    canceladas: int
    tasa_asistencia: float