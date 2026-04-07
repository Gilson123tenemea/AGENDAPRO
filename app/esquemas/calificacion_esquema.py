from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class CalificacionEntrada(BaseModel):
    puntuacion: int
    comentario: Optional[str] = None

    @field_validator("puntuacion")
    @classmethod
    def rango_valido(cls, v):
        if v < 1 or v > 5:
            raise ValueError("La puntuación debe estar entre 1 y 5")
        return v


class CalificacionSalida(BaseModel):
    id: int
    puntuacion: int
    comentario: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}