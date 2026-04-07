from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UsuarioCrear(BaseModel):
    email: EmailStr
    password: str
    rol: str = "profesional"


class UsuarioSalida(BaseModel):
    id: int
    email: str
    rol: str
    esta_activo: bool
    organizacion_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}