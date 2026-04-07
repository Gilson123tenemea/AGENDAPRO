from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime

class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes.id"), nullable=False)
    stripe_sus_id = Column(String(100), unique=True, nullable=True)
    estado = Column(String(20), nullable=False, default="en_prueba")
    periodo_inicio = Column(DateTime, nullable=True)
    periodo_fin = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    organizacion = relationship("Organizacion", back_populates="suscripcion")
    plan = relationship("Plan", back_populates="suscripciones")