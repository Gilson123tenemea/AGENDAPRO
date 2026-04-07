from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base

class Especialidad(Base):
    __tablename__ = "especialidades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    esta_activo = Column(Boolean, default=True)

    # Relaciones
    profesionales = relationship("ProfEspecialidad", back_populates="especialidad")