from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.base_datos.conexion import Base
from datetime import datetime


class Profesional(Base):
    __tablename__ = "profesionales"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Claves foráneas ───────────────────────────────────────────────
    organizacion_id = Column(Integer, ForeignKey("organizaciones.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # ── Datos básicos (se llenan al crear) ────────────────────────────
    nombre_completo = Column(String(150), nullable=False)
    telefono = Column(String(20), nullable=True)
    foto_url = Column(String(500), nullable=True)       # foto de perfil

    # ── Perfil profesional (se completa después) ──────────────────────
    titulo_profesional = Column(String(200), nullable=True)  # Ej: Médico General
    descripcion = Column(Text, nullable=True)                # bio corta visible al paciente
    experiencia_anios = Column(Integer, nullable=True)       # años de experiencia
    educacion = Column(Text, nullable=True)                  # universidad, titulo, año
    certificaciones = Column(Text, nullable=True)            # certificados, cursos
    idiomas = Column(String(200), nullable=True)             # español, inglés, etc.
    atiende_en = Column(String(300), nullable=True)          # consultorio, domicilio, virtual
    direccion_consultorio = Column(String(300), nullable=True)

    # ── Configuración de agenda ───────────────────────────────────────
    token_publico = Column(String(64), unique=True, nullable=False, index=True)
    duracion_cita_min = Column(Integer, default=30)
    requiere_pago = Column(Boolean, default=False)
    precio = Column(Numeric(10, 2), nullable=True)
    moneda = Column(String(3), default="USD")

    # ── Métricas (calculadas automáticamente) ─────────────────────────
    promedio_calif = Column(Numeric(3, 2), default=0.0)
    total_citas = Column(Integer, default=0)

    # ── Control ───────────────────────────────────────────────────────
    esta_activo = Column(Boolean, default=True)
    perfil_completo = Column(Boolean, default=False)   # indica si completó el perfil
    eliminado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # ── Relaciones ────────────────────────────────────────────────────
    organizacion = relationship(
        "Organizacion", back_populates="profesionales"
    )
    usuario = relationship(
        "Usuario", back_populates="profesional"
    )
    horarios = relationship(
        "Horario", back_populates="profesional", cascade="all, delete-orphan"
    )
    fechas_bloqueadas = relationship(
        "FechaBloqueada", back_populates="profesional", cascade="all, delete-orphan"
    )
    especialidades = relationship(
        "ProfEspecialidad", back_populates="profesional", cascade="all, delete-orphan"
    )
    citas = relationship(
        "Cita", back_populates="profesional"
    )
    notas = relationship(
        "NotaCita", back_populates="profesional"
    )
    calificaciones = relationship(
        "Calificacion", back_populates="profesional"
    )