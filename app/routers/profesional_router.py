from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_admin, solo_profesional
from app.servicios.profesional_servicio import ProfesionalServicio
from app.esquemas.profesional_esquema import (
    ProfesionalCrear, ProfesionalActualizar, ProfesionalSalida, ProfesionalCompletarPerfil, ProfesionalCompletarPerfil
)

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


# ✅ /yo DEBE ir antes de /{profesional_id}
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

