from pydantic import BaseModel, field_validator
from datetime import time
from typing import Optional


class HorarioCrear(BaseModel):
    dia_semana: int          # 0=Lunes, 6=Domingo
    hora_inicio: time
    hora_fin: time

    @field_validator("dia_semana")
    @classmethod
    def dia_valido(cls, v):
        if v < 0 or v > 6:
            raise ValueError("El día debe ser entre 0 (lunes) y 6 (domingo)")
        return v

    @field_validator("hora_fin")
    @classmethod
    def fin_mayor_inicio(cls, v, info):
        if "hora_inicio" in info.data and v <= info.data["hora_inicio"]:
            raise ValueError("La hora de fin debe ser mayor a la hora de inicio")
        return v


class HorarioSalida(BaseModel):
    id: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time
    esta_activo: bool

    model_config = {"from_attributes": True}