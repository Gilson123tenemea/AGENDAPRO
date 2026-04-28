from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.modelos.cita_modelo import Cita
from app.modelos.paciente_modelo import Paciente
from app.modelos.profesional_modelo import Profesional
from app.esquemas.cita_esquema import (
    CancelarCitaEntrada, CitaSalida,
    SlotDisponibleSalida, ReservarCitaEntrada,
)
from app.esquemas.profesional_esquema import ProfesionalPublicoSalida
from app.servicios.cita_servicio import CitaServicio
from app.servicios.profesional_servicio import ProfesionalServicio
from app.core.excepciones import NoEncontradoExcepcion
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/publico", tags=["Público"])


# ── Esquema público de cita ──────────────────────────────────────────
class CitaPublicaSalida(BaseModel):
    token_reserva: str
    estado: str
    inicio: datetime
    fin: datetime
    motivo: str
    motivo_cancelacion: Optional[str] = None
    nombre_paciente: str
    telefono_paciente: str
    nombre_profesional: str
    titulo_profesional: Optional[str] = None
    telefono_profesional: Optional[str] = None
    organizacion_nombre: str
    direccion_consultorio: Optional[str] = None
    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════
# PROFESIONALES (público, sin auth)
# ══════════════════════════════════════════════════

@router.get(
    "/profesionales/{token}",
    response_model=ProfesionalPublicoSalida,
    summary="Perfil público del profesional",
)
def perfil_publico(token: str, db: Session = Depends(get_db)):
    return ProfesionalServicio(db).obtener_por_token(token)


@router.get(
    "/profesionales/{token}/slots",
    response_model=list[SlotDisponibleSalida],
    summary="Slots disponibles para una fecha",
)
def slots_disponibles(
    token: str,
    fecha: datetime = Query(..., description="Formato: 2026-04-09T00:00:00"),
    db: Session = Depends(get_db),
):
    profesional = ProfesionalServicio(db).obtener_por_token(token)
    return CitaServicio(db).slots_disponibles(profesional, fecha)


@router.post(
    "/profesionales/{token}/reservar",
    response_model=CitaSalida,
    summary="El paciente reserva su cita",
)
def reservar_cita(
    token: str,
    datos: ReservarCitaEntrada,
    db: Session = Depends(get_db),
):
    profesional = ProfesionalServicio(db).obtener_por_token(token)
    return CitaServicio(db).reservar(profesional, datos)


# ══════════════════════════════════════════════════
# CITAS (público, sin auth)
# ══════════════════════════════════════════════════

@router.get(
    "/citas/{token}",
    response_model=CitaPublicaSalida,
    summary="Consulta pública de cita por token",
)
def estado_cita(token: str, db: Session = Depends(get_db)):
    cita = db.query(Cita).filter(Cita.token_reserva == token).first()
    if not cita:
        raise NoEncontradoExcepcion("Cita no encontrada")

    paciente    = db.query(Paciente).filter(Paciente.id == cita.paciente_id).first()
    profesional = db.query(Profesional).filter(Profesional.id == cita.profesional_id).first()

    return CitaPublicaSalida(
        token_reserva=cita.token_reserva,
        estado=cita.estado,
        inicio=cita.inicio,
        fin=cita.fin,
        motivo=cita.motivo,
        motivo_cancelacion=cita.motivo_cancelacion,
        nombre_paciente=paciente.nombre_completo if paciente else "Paciente",
        telefono_paciente=paciente.telefono if paciente else "",
        nombre_profesional=profesional.nombre_completo if profesional else "Profesional",
        titulo_profesional=profesional.titulo_profesional if profesional else None,
        telefono_profesional=profesional.telefono if profesional else None,
        organizacion_nombre=profesional.organizacion.nombre if profesional else "",
        direccion_consultorio=profesional.direccion_consultorio if profesional else None,
    )


@router.post(
    "/citas/{token}/cancelar",
    response_model=CitaPublicaSalida,
    summary="Cancela una cita pública por token",
)
def cancelar_cita_publica(
    token: str,
    datos: CancelarCitaEntrada,
    db: Session = Depends(get_db),
):
    svc  = CitaServicio(db)
    cita = svc.obtener_por_token(token)
    cita = svc.cancelar(cita, datos)

    paciente    = db.query(Paciente).filter(Paciente.id == cita.paciente_id).first()
    profesional = db.query(Profesional).filter(Profesional.id == cita.profesional_id).first()

    return CitaPublicaSalida(
        token_reserva=cita.token_reserva,
        estado=cita.estado,
        inicio=cita.inicio,
        fin=cita.fin,
        motivo=cita.motivo,
        motivo_cancelacion=cita.motivo_cancelacion,
        nombre_paciente=paciente.nombre_completo if paciente else "Paciente",
        telefono_paciente=paciente.telefono if paciente else "",
        nombre_profesional=profesional.nombre_completo if profesional else "Profesional",
        titulo_profesional=profesional.titulo_profesional if profesional else None,
        telefono_profesional=profesional.telefono if profesional else None,
        organizacion_nombre=profesional.organizacion.nombre if profesional else "",
        direccion_consultorio=profesional.direccion_consultorio if profesional else None,
    )