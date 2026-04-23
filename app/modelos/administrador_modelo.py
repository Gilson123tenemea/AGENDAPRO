# app/modelos/administrador_modelo.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Administrador(Base):
    __tablename__ = "administradores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(200), unique=True, nullable=False)
    password_hasheado = Column(String(500), nullable=False)
    esta_activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)