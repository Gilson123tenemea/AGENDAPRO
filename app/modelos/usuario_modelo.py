from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hasheado = Column(String(500), nullable=False)
    rol = Column(String(20), nullable=False, default="admin_org")
    esta_activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    organizacion = relationship("Organizacion", back_populates="usuarios")
    profesional = relationship("Profesional", back_populates="usuario", uselist=False)