from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_profesional
from app.servicios.cita_servicio import CitaServicio
from app.servicios.profesional_servicio import ProfesionalServicio
from app.esquemas.cita_esquema import (
    CitaSalida, CancelarCitaEntrada,
    ReagendarCitaEntrada, MarcarAsistenciaEntrada,
    NotaCitaEntrada, NotaCitaSalida,
)

router = APIRouter(prefix="/api/v1/citas", tags=["Citas"])


@router.get(
    "/",
    response_model=list[CitaSalida],
    summary="Lista citas del profesional con filtros"
)
def listar_citas(
    profesional_id: int = Query(...),
    estado: str = Query(None),
    fecha_desde: datetime = Query(None),
    fecha_hasta: datetime = Query(None),
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    return CitaServicio(db).listar_por_profesional(
        profesional_id=profesional_id,
        organizacion_id=usuario_actual.organizacion_id,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get(
    "/{cita_id}",
    response_model=CitaSalida,
    summary="Detalle de una cita"
)
def obtener_cita(
    cita_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    return CitaServicio(db).obtener_por_id(cita_id, usuario_actual.organizacion_id)


@router.patch(
    "/{cita_id}/cancelar",
    response_model=CitaSalida,
    summary="Cancela una cita"
)
def cancelar(
    cita_id: int,
    datos: CancelarCitaEntrada,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    servicio = CitaServicio(db)
    cita = servicio.obtener_por_id(cita_id, usuario_actual.organizacion_id)
    return servicio.cancelar(cita, datos)


@router.patch(
    "/{cita_id}/reagendar",
    response_model=CitaSalida,
    summary="Reagenda una cita"
)
def reagendar(
    cita_id: int,
    datos: ReagendarCitaEntrada,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    servicio = CitaServicio(db)
    cita = servicio.obtener_por_id(cita_id, usuario_actual.organizacion_id)
    profesional = ProfesionalServicio(db).obtener_por_id(
        cita.profesional_id, usuario_actual.organizacion_id
    )
    return servicio.reagendar(cita, profesional, datos)


@router.patch(
    "/{cita_id}/asistencia",
    response_model=CitaSalida,
    summary="Marca si el paciente asistió"
)
def marcar_asistencia(
    cita_id: int,
    datos: MarcarAsistenciaEntrada,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    servicio = CitaServicio(db)
    cita = servicio.obtener_por_id(cita_id, usuario_actual.organizacion_id)
    return servicio.marcar_asistencia(cita, datos)


@router.post(
    "/{cita_id}/notas",
    response_model=NotaCitaSalida,
    summary="Agrega nota clínica a una cita"
)
def agregar_nota(
    cita_id: int,
    datos: NotaCitaEntrada,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    servicio = CitaServicio(db)
    cita = servicio.obtener_por_id(cita_id, usuario_actual.organizacion_id)
    return servicio.agregar_nota(cita, usuario_actual.id, datos)


@router.get(
    "/{cita_id}/notas",
    response_model=list[NotaCitaSalida],
    summary="Lista notas de una cita"
)
def listar_notas(
    cita_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    servicio = CitaServicio(db)
    cita = servicio.obtener_por_id(cita_id, usuario_actual.organizacion_id)
    return cita.notas