from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base

class ProfEspecialidad(Base):
    __tablename__ = "prof_especialidades"

    # Clave primaria propia + restricción única en la combinación
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profesional_id = Column(Integer, ForeignKey("profesionales.id"), nullable=False)
    especialidad_id = Column(Integer, ForeignKey("especialidades.id"), nullable=False)
    es_principal = Column(Boolean, default=False)

    # Evita que el mismo profesional tenga la misma especialidad dos veces
    __table_args__ = (
        UniqueConstraint("profesional_id", "especialidad_id", name="uq_prof_especialidad"),
    )

    # Relaciones
    profesional = relationship("Profesional", back_populates="especialidades")
    especialidad = relationship("Especialidad", back_populates="profesionales")