from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Calificacion(Base):
    __tablename__ = "calificaciones"    

    __table_args__ = (
        CheckConstraint("puntuacion BETWEEN 1 AND 5", name="chk_puntuacion"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cita_id = Column(Integer, ForeignKey("citas.id"), unique=True, nullable=False)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False, index=True)
    puntuacion = Column(Integer, nullable=False)
    comentario = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    cita = relationship("Cita", back_populates="calificacion")
    paciente = relationship("Paciente", back_populates="calificaciones")
    profesional = relationship("Profesional", back_populates="calificaciones")