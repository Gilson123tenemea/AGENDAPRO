from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Profesional(Base):
    __tablename__ = "profesionales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    telefono = Column(String(20), nullable=True)
    token_publico = Column(String(64), unique=True, nullable=False, index=True)
    duracion_cita_min = Column(Integer, default=30)
    requiere_pago = Column(Boolean, default=False)
    precio = Column(Numeric(10, 2), nullable=True)
    promedio_calif = Column(Numeric(3, 2), default=0.0)
    esta_activo = Column(Boolean, default=True)
    eliminado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    organizacion = relationship("Organizacion", back_populates="profesionales")
    usuario = relationship("Usuario", back_populates="profesional")
    horarios = relationship("Horario", back_populates="profesional", cascade="all, delete-orphan")
    fechas_bloqueadas = relationship("FechaBloqueada", back_populates="profesional", cascade="all, delete-orphan")
    especialidades = relationship("ProfEspecialidad", back_populates="profesional", cascade="all, delete-orphan")
    citas = relationship("Cita", back_populates="profesional")
    notas = relationship("NotaCita", back_populates="profesional")
    calificaciones = relationship("Calificacion", back_populates="profesional")