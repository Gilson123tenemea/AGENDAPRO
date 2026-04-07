from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    nombre_completo = Column(String(150), nullable=False)   # obligatorio
    telefono = Column(String(20), nullable=False, index=True)  # obligatorio — identificador
    email = Column(String(200), nullable=True)
    notas = Column(Text, nullable=True)
    eliminado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    organizacion = relationship("Organizacion", back_populates="pacientes")
    citas = relationship("Cita", back_populates="paciente")
    calificaciones = relationship("Calificacion", back_populates="paciente")