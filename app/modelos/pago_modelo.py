from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cita_id = Column(Integer, ForeignKey("citas.id"), unique=True, nullable=False)
    stripe_payment_id = Column(String(100), unique=True, nullable=True)
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(3), default="usd")
    estado = Column(String(20), nullable=False, default="pendiente")
    pagado_en = Column(DateTime, nullable=True)
    reembolsado_en = Column(DateTime, nullable=True)

    # Relaciones
    cita = relationship("Cita", back_populates="pago")