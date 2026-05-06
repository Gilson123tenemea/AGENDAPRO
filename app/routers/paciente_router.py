from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_profesional
from app.modelos.paciente_modelo import Paciente
from app.modelos.cita_modelo import Cita
from app.esquemas.paciente_esquema import PacienteSalida, PacienteActualizar, CitaResumenSalida, HistorialPacienteSalida
from app.esquemas.cita_esquema import CitaSalida
from app.core.excepciones import NoEncontradoExcepcion
from app.servicios.profesional_servicio import ProfesionalServicio 
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


@router.get("/{paciente_id}/citas", response_model=HistorialPacienteSalida, summary="Historial de citas del paciente con estadísticas")
def historial_citas(
    paciente_id: int,
    usuario_actual=Depends(solo_profesional),
    db: Session = Depends(get_db),
):
    # Solo citas de este paciente con el profesional autenticado
    profesional = ProfesionalServicio(db).obtener_por_usuario(usuario_actual.id)

    citas = (
        db.query(Cita)
        .filter(
            Cita.paciente_id == paciente_id,
            Cita.profesional_id == profesional.id,
        )
        .order_by(Cita.inicio.desc())
        .all()
    )

    completadas = sum(1 for c in citas if c.estado == "completada")
    no_asistio  = sum(1 for c in citas if c.estado == "no_asistio")
    canceladas  = sum(1 for c in citas if c.estado == "cancelada")
    relevantes  = completadas + no_asistio
    tasa        = round((completadas / relevantes) * 100, 1) if relevantes > 0 else 0.0

    return HistorialPacienteSalida(
        citas=citas,
        total=len(citas),
        completadas=completadas,
        no_asistio=no_asistio,
        canceladas=canceladas,
        tasa_asistencia=tasa,
    )


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