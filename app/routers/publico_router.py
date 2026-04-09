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


@router.get(
    "/citas/{token_reserva}",
    response_model=CitaSalida,
    summary="El paciente consulta su cita",
)
def consultar_cita(token_reserva: str, db: Session = Depends(get_db)):
    return CitaServicio(db).obtener_por_token(token_reserva)


@router.delete(
    "/citas/{token_reserva}",
    summary="El paciente cancela su cita",
)
def cancelar_cita_paciente(
    token_reserva: str,
    datos: CancelarCitaEntrada,
    db: Session = Depends(get_db),
):
    servicio = CitaServicio(db)
    cita = servicio.obtener_por_token(token_reserva)
    return servicio.cancelar(cita, datos)


# ======================================================================
# 🧪 ENDPOINTS DE PRUEBA — ELIMINAR ANTES DE PRODUCCIÓN
# ======================================================================

@router.post(
    "/test/whatsapp",
    tags=["Test"],
    summary="Prueba envío directo de WhatsApp",
)
def probar_whatsapp(
    telefono: str = Query(..., description="Formato: +593991234567"),
    db: Session = Depends(get_db),
):
    from app.servicios.notificacion_servicio import NotificacionServicio
    notif = NotificacionServicio(db)
    exito = notif._enviar_whatsapp(
        telefono,
        "✅ Prueba de AgendaPro — WhatsApp funciona correctamente.",
    )
    return {"exito": exito, "telefono": telefono}


@router.post(
    "/test/scheduler",
    tags=["Test"],
    summary="Fuerza ejecución del scheduler de recordatorios",
)
def forzar_scheduler():
    from main import procesar_recordatorios
    procesar_recordatorios()
    return {"mensaje": "Scheduler ejecutado — revisa tu WhatsApp"}


@router.post(
    "/test/resumen-diario",
    tags=["Test"],
    summary="Fuerza el resumen diario del profesional",
)
def forzar_resumen_diario():
    from main import enviar_resumenes_diarios
    enviar_resumenes_diarios()
    return {"mensaje": "Resumen diario ejecutado — revisa tu WhatsApp"}