# app/servicios/administrador_servicio.py
from sqlalchemy.orm import Session
from app.modelos.administrador_modelo import Administrador
from app.esquemas.administrador_esquema import AdminLoginEntrada, AdminTokenSalida
from app.core.seguridad import (
    verificar_password,
    crear_access_token,
    crear_refresh_token,
    decodificar_token,
)
from app.core.excepciones import NoAutorizadoExcepcion
from app.esquemas.auth_esquema import RefrescarTokenEntrada


class AdministradorServicio:

    def __init__(self, db: Session):
        self.db = db

    def login(self, datos: AdminLoginEntrada) -> AdminTokenSalida:
        admin = self.db.query(Administrador).filter(
            Administrador.email == datos.email,
            Administrador.esta_activo == True,
        ).first()

        if not admin or not verificar_password(datos.password, admin.password_hasheado):
            raise NoAutorizadoExcepcion("Email o contraseña incorrectos")

        payload = {
            "sub": str(admin.id),
            "rol": "superadmin",
        }

        return AdminTokenSalida(
            access_token=crear_access_token(payload),
            refresh_token=crear_refresh_token(payload),
        )

    def refrescar(self, datos: RefrescarTokenEntrada) -> AdminTokenSalida:
        payload = decodificar_token(datos.refresh_token)
        if not payload or payload.get("tipo") != "refresh":
            raise NoAutorizadoExcepcion("Refresh token inválido o expirado")

        admin = self.db.query(Administrador).filter(
            Administrador.id == int(payload.get("sub")),
            Administrador.esta_activo == True,
        ).first()

        if not admin:
            raise NoAutorizadoExcepcion("Administrador no encontrado")

        nuevo_payload = {
            "sub": str(admin.id),
            "rol": "superadmin",
        }

        return AdminTokenSalida(
            access_token=crear_access_token(nuevo_payload),
            refresh_token=crear_refresh_token(nuevo_payload),
        )