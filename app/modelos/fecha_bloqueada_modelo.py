from sqlalchemy import Column, Integer, String, DateTime, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class FechaBloqueada(Base):
    __tablename__ = "fechas_bloqueadas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=True)   # NULL = día completo bloqueado
    hora_fin = Column(Time, nullable=True)
    motivo = Column(String(200), nullable=True)
    eliminado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    profesional = relationship("Profesional", back_populates="fechas_bloqueadas")