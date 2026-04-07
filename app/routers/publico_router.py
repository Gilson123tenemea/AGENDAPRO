# Este router NO tiene autenticación
# Es el que usa el paciente desde el link público

from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.servicios.profesional_servicio import ProfesionalServicio
from app.servicios.cita_servicio import CitaServicio
from app.esquemas.profesional_esquema import ProfesionalPublicoSalida
from app.esquemas.cita_esquema import (
    ReservarCitaEntrada, CancelarCitaEntrada,
    CitaSalida, SlotDisponibleSalida,
)

router = APIRouter(prefix="/api/v1/publico", tags=["Público - Paciente"])


@router.get(
    "/profesionales/{token}",
    response_model=ProfesionalPublicoSalida,
    summary="Perfil público del profesional"
)
def perfil_publico(token: str, db: Session = Depends(get_db)):
    return ProfesionalServicio(db).obtener_por_token(token)


@router.get(
    "/profesionales/{token}/slots",
    response_model=list[SlotDisponibleSalida],
    summary="Slots disponibles para una fecha"
)
def slots_disponibles(
    token: str,
    fecha: datetime = Query(..., description="Formato: 2026-04-15T00:00:00"),
    db: Session = Depends(get_db),
):
    profesional = ProfesionalServicio(db).obtener_por_token(token)
    return CitaServicio(db).slots_disponibles(profesional, fecha)


@router.post(
    "/profesionales/{token}/reservar",
    response_model=CitaSalida,
    summary="El paciente reserva su cita"
)
def reservar_cita(
    token: str,
    datos: ReservarCitaEntrada,
    db: Session = Depends(get_db),
):
    profesional = ProfesionalServicio(db).obtener_por_token(token)
    return CitaServicio(db).reservar(profesional, datos)


@router.get(
    "/citas/{token_reserva}",
    response_model=CitaSalida,
    summary="El paciente consulta su cita"
)
def consultar_cita(token_reserva: str, db: Session = Depends(get_db)):
    return CitaServicio(db).obtener_por_token(token_reserva)


@router.delete(
    "/citas/{token_reserva}",
    summary="El paciente cancela su cita"
)
def cancelar_cita_paciente(
    token_reserva: str,
    datos: CancelarCitaEntrada,
    db: Session = Depends(get_db),
):
    servicio = CitaServicio(db)
    cita = servicio.obtener_por_token(token_reserva)
    return servicio.cancelar(cita, datos)