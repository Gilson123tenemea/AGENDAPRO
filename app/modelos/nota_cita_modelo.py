from sqlalchemy import Column, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class NotaCita(Base):
    __tablename__ = "notas_citas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cita_id = Column(Integer, ForeignKey("citas.id"), nullable=False, index=True)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    es_privada = Column(Boolean, default=True)
    eliminado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    cita = relationship("Cita", back_populates="notas")
    profesional = relationship("Profesional", back_populates="notas")