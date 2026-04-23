from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime


class Organizacion(Base):
    __tablename__ = "organizaciones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Datos básicos ─────────────────────────────────────────────────
    nombre = Column(String(150), nullable=False)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)

    # ── Perfil completo (se completa después del registro) ────────────
    logo_url = Column(String(500), nullable=True)
    descripcion = Column(Text, nullable=True)          # descripción de la clínica
    direccion = Column(String(300), nullable=True)     # dirección física
    ciudad = Column(String(100), nullable=True)        # ciudad
    sitio_web = Column(String(200), nullable=True)     # página web si tiene
    redes_sociales = Column(String(500), nullable=True) # instagram, facebook, etc.

    # ── Control ───────────────────────────────────────────────────────
    esta_activo = Column(Boolean, default=True)
    perfil_completo = Column(Boolean, default=False)   # indica si completó el perfil
    creado_en = Column(DateTime, default=datetime.utcnow)

    # ── Relaciones ────────────────────────────────────────────────────
    usuarios = relationship(
        "Usuario", back_populates="organizacion", cascade="all, delete-orphan"
    )
    profesionales = relationship(
        "Profesional", back_populates="organizacion"
    )
    pacientes = relationship(
        "Paciente", back_populates="organizacion"
    )
    suscripcion = relationship(
        "Suscripcion", back_populates="organizacion", uselist=False
    )