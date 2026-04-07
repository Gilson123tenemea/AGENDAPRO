from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False, index=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False, index=True)
    inicio = Column(DateTime, nullable=False, index=True)
    fin = Column(DateTime, nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    motivo = Column(Text, nullable=False)            # obligatorio al reservar
    asistio = Column(Boolean, nullable=True)
    motivo_cancelacion = Column(Text, nullable=True)
    token_reserva = Column(String(64), unique=True, nullable=False, index=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    profesional = relationship("Profesional", back_populates="citas")
    paciente = relationship("Paciente", back_populates="citas")
    pago = relationship("Pago", back_populates="cita", uselist=False)
    notas = relationship("NotaCita", back_populates="cita", cascade="all, delete-orphan")
    notificaciones = relationship("Notificacion", back_populates="cita", cascade="all, delete-orphan")
    calificacion = relationship("Calificacion", back_populates="cita", uselist=False)