from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_profesional
from app.modelos.paciente_modelo import Paciente
from app.modelos.cita_modelo import Cita
from app.esquemas.paciente_esquema import PacienteSalida, PacienteActualizar
from app.esquemas.cita_esquema import CitaSalida
from app.core.excepciones import NoEncontradoExcepcion

router = APIRouter(prefix="/api/v1/pacientes", tags=["Pacientes"])


@router.get(
    "/",
    response_model=list[PacienteSalida],
    summary="Lista pacientes de la organización"
)
def listar_pacientes(
    buscar: str = Query(None, description="Buscar por nombre o teléfono"),
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    query = db.query(Paciente).filter(
        Paciente.organizacion_id == usuario_actual.organizacion_id,
        Paciente.eliminado_en == None,
    )
    if buscar:
        query = query.filter(
            Paciente.nombre_completo.ilike(f"%{buscar}%") |
            Paciente.telefono.ilike(f"%{buscar}%")
        )
    return query.all()


@router.get(
    "/{paciente_id}",
    response_model=PacienteSalida,
    summary="Perfil de un paciente"
)
def obtener_paciente(
    paciente_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id,
        Paciente.organizacion_id == usuario_actual.organizacion_id,
        Paciente.eliminado_en == None,
    ).first()
    if not paciente:
        raise NoEncontradoExcepcion("Paciente no encontrado")
    return paciente


@router.get(
    "/{paciente_id}/citas",
    response_model=list[CitaSalida],
    summary="Historial de citas del paciente"
)
def historial_citas(
    paciente_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    return db.query(Cita).filter(
        Cita.paciente_id == paciente_id,
        Cita.organizacion_id == usuario_actual.organizacion_id,
    ).order_by(Cita.inicio.desc()).all()


@router.put(
    "/{paciente_id}/notas",
    response_model=PacienteSalida,
    summary="Actualiza notas del paciente"
)
def actualizar_notas(
    paciente_id: int,
    datos: PacienteActualizar,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    paciente = db.query(Paciente).filter(
        Paciente.id == paciente_id,
        Paciente.organizacion_id == usuario_actual.organizacion_id,
        Paciente.eliminado_en == None,
    ).first()
    if not paciente:
        raise NoEncontradoExcepcion("Paciente no encontrado")
    paciente.notas = datos.notas
    db.commit()
    db.refresh(paciente)
    return paciente