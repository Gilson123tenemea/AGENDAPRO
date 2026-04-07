# ¿De dónde sale cada método?
# login()           → RF-02 Autenticación
# refrescar()       → RF-02 Refresh token

from sqlalchemy.orm import Session
from app.modelos.usuario_modelo import Usuario
from app.esquemas.auth_esquema import LoginEntrada, TokenSalida, RefrescarTokenEntrada
from app.core.seguridad import (
    verificar_password,
    crear_access_token,
    crear_refresh_token,
    decodificar_token,
)
from app.core.excepciones import NoAutorizadoExcepcion


class AuthServicio:

    def __init__(self, db: Session):
        self.db = db

    def login(self, datos: LoginEntrada) -> TokenSalida:
        usuario = self.db.query(Usuario).filter(
            Usuario.email == datos.email,
            Usuario.esta_activo == True,
        ).first()

        if not usuario or not verificar_password(datos.password, usuario.password_hasheado):
            raise NoAutorizadoExcepcion("Email o contraseña incorrectos")

        payload = {
            "sub": str(usuario.id),
            "org": str(usuario.organizacion_id),
            "rol": usuario.rol,
        }

        return TokenSalida(
            access_token=crear_access_token(payload),
            refresh_token=crear_refresh_token(payload),
            rol=usuario.rol,
            organizacion_id=usuario.organizacion_id,
        )

    def refrescar(self, datos: RefrescarTokenEntrada) -> TokenSalida:
        payload = decodificar_token(datos.refresh_token)
        if not payload or payload.get("tipo") != "refresh":
            raise NoAutorizadoExcepcion("Refresh token inválido o expirado")

        usuario = self.db.query(Usuario).filter(
            Usuario.id == int(payload.get("sub")),
            Usuario.esta_activo == True,
        ).first()

        if not usuario:
            raise NoAutorizadoExcepcion("Usuario no encontrado")

        nuevo_payload = {
            "sub": str(usuario.id),
            "org": str(usuario.organizacion_id),
            "rol": usuario.rol,
        }

        return TokenSalida(
            access_token=crear_access_token(nuevo_payload),
            refresh_token=crear_refresh_token(nuevo_payload),
            rol=usuario.rol,
            organizacion_id=usuario.organizacion_id,
        )