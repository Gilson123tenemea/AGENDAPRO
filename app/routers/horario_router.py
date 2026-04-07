from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_profesional
from app.modelos.horario_modelo import Horario
from app.servicios.profesional_servicio import ProfesionalServicio
from app.esquemas.horario_esquema import HorarioCrear, HorarioSalida

router = APIRouter(prefix="/api/v1/horarios", tags=["Horarios"])


@router.post(
    "/",
    response_model=HorarioSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Agrega un horario al profesional"
)
def crear_horario(
    profesional_id: int,
    datos: HorarioCrear,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    # Verificar que el profesional pertenece a la organización
    ProfesionalServicio(db).obtener_por_id(profesional_id, usuario_actual.organizacion_id)

    horario = Horario(
        profesional_id=profesional_id,
        dia_semana=datos.dia_semana,
        hora_inicio=datos.hora_inicio,
        hora_fin=datos.hora_fin,
    )
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario


@router.get(
    "/{profesional_id}",
    response_model=list[HorarioSalida],
    summary="Lista horarios de un profesional"
)
def listar_horarios(
    profesional_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    ProfesionalServicio(db).obtener_por_id(profesional_id, usuario_actual.organizacion_id)
    return db.query(Horario).filter(
        Horario.profesional_id == profesional_id,
        Horario.esta_activo == True,
    ).all()


@router.patch(
    "/{horario_id}/estado",
    response_model=HorarioSalida,
    summary="Activa o desactiva un horario"
)
def cambiar_estado_horario(
    horario_id: int,
    esta_activo: bool,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if not horario:
        from app.core.excepciones import NoEncontradoExcepcion
        raise NoEncontradoExcepcion("Horario no encontrado")
    horario.esta_activo = esta_activo
    db.commit()
    db.refresh(horario)
    return horario


@router.delete(
    "/{horario_id}",
    summary="Elimina un horario"
)
def eliminar_horario(
    horario_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if not horario:
        from app.core.excepciones import NoEncontradoExcepcion
        raise NoEncontradoExcepcion("Horario no encontrado")
    db.delete(horario)
    db.commit()
    return {"mensaje": "Horario eliminado"}