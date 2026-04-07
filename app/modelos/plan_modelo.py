from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base

class Plan(Base):
    __tablename__ = "planes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    precio_mensual = Column(Numeric(10, 2), nullable=False)
    max_profesionales = Column(Integer, nullable=False)
    tiene_pagos = Column(Boolean, default=False)
    tiene_resenas = Column(Boolean, default=False)
    tiene_analiticas = Column(Boolean, default=False)
    stripe_price_id = Column(String(100), nullable=True)
    esta_activo = Column(Boolean, default=True)

    # Relaciones
    suscripciones = relationship("Suscripcion", back_populates="plan")