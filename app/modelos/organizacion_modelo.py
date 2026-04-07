from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Organizacion(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)
    logo_url = Column(String(500), nullable=True)
    esta_activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="organizacion", cascade="all, delete-orphan")
    profesionales = relationship("Profesional", back_populates="organizacion")
    pacientes = relationship("Paciente", back_populates="organizacion")
    suscripcion = relationship("Suscripcion", back_populates="organizacion", uselist=False)