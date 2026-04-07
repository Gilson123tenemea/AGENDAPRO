from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.core.seguridad import decodificar_token
from app.core.excepciones import NoAutorizadoExcepcion, SinPermisoExcepcion
from app.core.enumeraciones import RolUsuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decodificar_token(token)
    if not payload or payload.get("tipo") != "access":
        raise NoAutorizadoExcepcion("Token inválido o expirado")

    from app.modelos.usuario_modelo import Usuario
    usuario = db.query(Usuario).filter(
        Usuario.id == int(payload.get("sub")),
        Usuario.esta_activo == True,
    ).first()

    if not usuario:
        raise NoAutorizadoExcepcion("Usuario no encontrado o inactivo")
    return usuario


def solo_profesional(usuario=Depends(obtener_usuario_actual)):
    roles = [RolUsuario.PROFESIONAL, RolUsuario.ADMIN_ORG, RolUsuario.SUPERADMIN]
    if usuario.rol not in roles:
        raise SinPermisoExcepcion()
    return usuario


def solo_admin(usuario=Depends(obtener_usuario_actual)):
    if usuario.rol not in [RolUsuario.ADMIN_ORG, RolUsuario.SUPERADMIN]:
        raise SinPermisoExcepcion()
    return usuario


def solo_superadmin(usuario=Depends(obtener_usuario_actual)):
    if usuario.rol != RolUsuario.SUPERADMIN:
        raise SinPermisoExcepcion("Solo el superadmin puede hacer esto")
    return usuario