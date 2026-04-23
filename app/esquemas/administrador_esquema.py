# app/esquemas/administrador_esquema.py
from pydantic import BaseModel, EmailStr
from datetime import datetime


class AdminLoginEntrada(BaseModel):
    email: EmailStr
    password: str
    

class AdminTokenSalida(BaseModel):
    access_token: str
    refresh_token: str
    rol: str = "superadmin"


class AdminSalida(BaseModel):
    id: int
    email: str
    esta_activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}