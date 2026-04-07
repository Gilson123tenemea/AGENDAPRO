from sqlalchemy import Column, Integer, Boolean, ForeignKey, Time, DateTime
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False)
    dia_semana = Column(Integer, nullable=False)  # 0=Lunes, 6=Domingo
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    esta_activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    profesional = relationship("Profesional", back_populates="horarios")