from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_admin, solo_superadmin
from app.servicios.organizacion_servicio import OrganizacionServicio
from app.esquemas.organizacion_esquema import (
    OrganizacionCrear, OrganizacionActualizar, OrganizacionSalida
)
from app.esquemas.usuario_esquema import UsuarioSalida

router = APIRouter(prefix="/api/v1/organizaciones", tags=["Organizaciones"])


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED,
    summary="Registra nueva organización y su admin"
)
def registrar(datos: OrganizacionCrear, db: Session = Depends(get_db)):
    servicio = OrganizacionServicio(db)
    org, usuario = servicio.registrar(datos)
    return {
        "organizacion": OrganizacionSalida.model_validate(org),
        "usuario": UsuarioSalida.model_validate(usuario),
    }


@router.get(
    "/yo",
    response_model=OrganizacionSalida,
    summary="Obtiene mi organización"
)
def obtener_mi_organizacion(
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    return OrganizacionServicio(db).obtener_por_id(usuario_actual.organizacion_id)


@router.put(
    "/yo",
    response_model=OrganizacionSalida,
    summary="Actualiza mi organización"
)
def actualizar_organizacion(
    datos: OrganizacionActualizar,
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    return OrganizacionServicio(db).actualizar(usuario_actual.organizacion_id, datos)


@router.get(
    "/",
    response_model=list[OrganizacionSalida],
    summary="[Superadmin] Lista todas las organizaciones"
)
def listar_todas(
    skip: int = 0,
    limit: int = 50,
    _=Depends(solo_superadmin),
    db: Session = Depends(get_db),
):
    return OrganizacionServicio(db).listar_todas(skip=skip, limit=limit)


@router.patch(
    "/{org_id}/estado",
    response_model=OrganizacionSalida,
    summary="[Superadmin] Activa o suspende organización"
)
def cambiar_estado(
    org_id: int,
    esta_activo: bool,
    _=Depends(solo_superadmin),
    db: Session = Depends(get_db),
):
    return OrganizacionServicio(db).cambiar_estado(org_id, esta_activo)