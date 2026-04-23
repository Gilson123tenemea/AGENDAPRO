from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.dependencias import solo_admin, solo_superadmin
from app.servicios.organizacion_servicio import OrganizacionServicio
from app.esquemas.organizacion_esquema import (
    OrganizacionCrear,
    OrganizacionActualizar,
    OrganizacionCompletarPerfil,
    OrganizacionSalida,
    OrganizacionConUsuarioSalida,
    OrganizacionSuperadminSalida,
)

router = APIRouter(prefix="/api/v1/organizaciones", tags=["Organizaciones"])


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED,
    summary="Paso 1 — Registra nueva organización y crea su admin",
)
def registrar(datos: OrganizacionCrear, db: Session = Depends(get_db)):
    """
    Crea la organización y el primer usuario admin en una sola operación.
    No requiere autenticación — es el registro público.
    """
    servicio = OrganizacionServicio(db)
    org, usuario = servicio.registrar(datos)
    return {
        "organizacion": OrganizacionSalida.model_validate(org),
        "usuario": {
            "id": usuario.id,
            "email": usuario.email,
            "rol": usuario.rol,
        },
        "mensaje": "Organización registrada correctamente. Ya puedes iniciar sesión.",
    }


@router.get(
    "/yo",
    response_model=OrganizacionSalida,
    summary="Obtiene mi organización",
)
def obtener_mi_organizacion(
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    return OrganizacionServicio(db).obtener_por_id(usuario_actual.organizacion_id)


@router.put(
    "/yo",
    response_model=OrganizacionSalida,
    summary="Actualiza datos básicos de mi organización",
)
def actualizar_organizacion(
    datos: OrganizacionActualizar,
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    return OrganizacionServicio(db).actualizar(
        usuario_actual.organizacion_id, datos
    )


@router.put(
    "/yo/perfil",
    response_model=OrganizacionSalida,
    summary="Paso 2 — Completa el perfil de la organización",
)
def completar_perfil(
    datos: OrganizacionCompletarPerfil,
    usuario_actual=Depends(solo_admin),
    db: Session = Depends(get_db),
):
    """
    El admin completa el perfil después del registro.
    Agrega descripción, dirección, logo, redes sociales, etc.
    """
    return OrganizacionServicio(db).completar_perfil(
        usuario_actual.organizacion_id, datos
    )


@router.get(
    "/",
    response_model=list[OrganizacionSuperadminSalida],
    summary="[Superadmin] Lista todas las organizaciones",
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
    summary="[Superadmin] Activa o suspende una organización",
)
def cambiar_estado(
    org_id: int,
    esta_activo: bool,
    _=Depends(solo_superadmin),
    db: Session = Depends(get_db),
):
    return OrganizacionServicio(db).cambiar_estado(org_id, esta_activo)