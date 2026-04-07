from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cita_id = Column(Integer, ForeignKey("citas.id"), nullable=False, index=True)
    telefono_dest = Column(String(20), nullable=False)
    tipo = Column(String(30), nullable=False)
    canal = Column(String(20), default="whatsapp")
    estado = Column(String(20), default="pendiente")
    programada_para = Column(DateTime, nullable=False)
    enviada_en = Column(DateTime, nullable=True)
    error_mensaje = Column(String(500), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    cita = relationship("Cita", back_populates="notificaciones")