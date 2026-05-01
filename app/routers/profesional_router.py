from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_admin, solo_profesional
from app.servicios.profesional_servicio import ProfesionalServicio
from app.esquemas.profesional_esquema import (
    ProfesionalCrear, ProfesionalActualizar, ProfesionalSalida,
    ProfesionalCompletarPerfil,
)
from app.modelos.paciente_modelo import Paciente
from app.modelos.cita_modelo import Cita

router = APIRouter(prefix="/api/v1/profesionales", tags=["Profesionales"])


@router.post(
    "/",
    response_model=ProfesionalSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Crea nuevo profesional"
)
def crear(
    datos: ProfesionalCrear,
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    return ProfesionalServicio(db).crear(usuario_actual.organizacion_id, datos)


@router.get(
    "/",
    response_model=list[ProfesionalSalida],
    summary="Lista profesionales de mi organización"
)
def listar(
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    return ProfesionalServicio(db).listar_por_organizacion(usuario_actual.organizacion_id)


@router.get(
    "/yo",
    response_model=ProfesionalSalida,
    summary="Obtiene mi perfil de profesional"
)
def obtener_mi_perfil(
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    return ProfesionalServicio(db).obtener_por_usuario(usuario_actual.id)


@router.put(
    "/yo/perfil",
    response_model=ProfesionalSalida,
    summary="Completa el perfil del profesional autenticado"
)
def completar_mi_perfil(
    datos: ProfesionalCompletarPerfil,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    return ProfesionalServicio(db).completar_perfil(usuario_actual.id, datos)


@router.get(
    "/yo/pacientes",
    summary="Lista pacientes del profesional autenticado con estadísticas"
)
def listar_mis_pacientes(
    q: str = Query(None, description="Buscar por nombre o teléfono"),
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    profesional = ProfesionalServicio(db).obtener_por_usuario(usuario_actual.id)

    stats = (
        db.query(
            Cita.paciente_id,
            func.count(Cita.id).label("total_citas"),
            func.max(Cita.inicio).label("ultima_cita"),
        )
        .filter(
            Cita.profesional_id == profesional.id,
            Cita.estado != "cancelada",
        )
        .group_by(Cita.paciente_id)
        .subquery()
    )

    query = (
        db.query(
            Paciente.id,
            Paciente.nombre_completo,
            Paciente.telefono,
            func.coalesce(stats.c.total_citas, 0).label("total_citas"),
            stats.c.ultima_cita,
        )
        .outerjoin(stats, Paciente.id == stats.c.paciente_id)
        .filter(Paciente.organizacion_id == profesional.organizacion_id)
        .filter(stats.c.total_citas.isnot(None))
    )

    if q:
        like = f"%{q}%"
        query = query.filter(
            Paciente.nombre_completo.ilike(like) |
            Paciente.telefono.ilike(like)
        )

    resultados = query.order_by(stats.c.ultima_cita.desc()).all()

    return [
        {
            "id": r.id,
            "nombre_completo": r.nombre_completo,
            "telefono": r.telefono,
            "total_citas": r.total_citas,
            "ultima_cita": r.ultima_cita.isoformat() if r.ultima_cita else None,
        }
        for r in resultados
    ]


@router.get(
    "/{profesional_id}",
    response_model=ProfesionalSalida,
    summary="Detalle de un profesional"
)
def obtener(
    profesional_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    return ProfesionalServicio(db).obtener_por_id(
        profesional_id, usuario_actual.organizacion_id
    )


@router.put(
    "/{profesional_id}",
    response_model=ProfesionalSalida,
    summary="Actualiza datos del profesional"
)
def actualizar(
    profesional_id: int,
    datos: ProfesionalActualizar,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    return ProfesionalServicio(db).actualizar(
        profesional_id, usuario_actual.organizacion_id, datos
    )


@router.delete(
    "/{profesional_id}",
    summary="Elimina profesional (borrado lógico)"
)
def eliminar(
    profesional_id: int,
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    return ProfesionalServicio(db).eliminar(
        profesional_id, usuario_actual.organizacion_id
    )