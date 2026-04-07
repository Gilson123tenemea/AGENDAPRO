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