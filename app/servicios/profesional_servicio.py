# ¿De dónde sale cada método?
# crear()                   → RF-03 Gestión de profesionales
# obtener_por_id()          → base para todos los endpoints
# obtener_por_token()       → RF-06 el paciente llega por link público
# listar_por_organizacion() → panel del admin
# actualizar()              → RF-03 editar perfil
# eliminar()                → RF-03 borrado lógico

import secrets
from sqlalchemy.orm import Session
from datetime import datetime
from app.modelos.profesional_modelo import Profesional
from app.modelos.usuario_modelo import Usuario
from app.esquemas.profesional_esquema import ProfesionalCrear, ProfesionalActualizar
from app.core.seguridad import encriptar_password
from app.core.excepciones import NoEncontradoExcepcion, ConflictoExcepcion
from app.core.enumeraciones import RolUsuario


class ProfesionalServicio:

    def __init__(self, db: Session):
        self.db = db

    def crear(self, organizacion_id: int, datos: ProfesionalCrear) -> Profesional:
        if self.db.query(Usuario).filter(Usuario.email == datos.email_acceso).first():
            raise ConflictoExcepcion(f"El email '{datos.email_acceso}' ya está registrado")

        try:
            usuario = Usuario(
                organizacion_id=organizacion_id,
                email=datos.email_acceso,
                password_hasheado=encriptar_password(datos.password_acceso),
                rol=RolUsuario.PROFESIONAL,
            )
            self.db.add(usuario)
            self.db.flush()

            profesional = Profesional(
                organizacion_id=organizacion_id,
                usuario_id=usuario.id,
                nombre_completo=datos.nombre_completo,
                token_publico=secrets.token_hex(32),  # 64 caracteres aleatorios
                duracion_cita_min=datos.duracion_cita_min,
                requiere_pago=datos.requiere_pago,
                precio=datos.precio,
            )
            self.db.add(profesional)
            self.db.commit()
            self.db.refresh(profesional)
            return profesional

        except Exception:
            self.db.rollback()
            raise

    def obtener_por_id(self, profesional_id: int, organizacion_id: int) -> Profesional:
        pro = self.db.query(Profesional).filter(
            Profesional.id == profesional_id,
            Profesional.organizacion_id == organizacion_id,
            Profesional.esta_activo == True,
            Profesional.eliminado_en == None,
        ).first()
        if not pro:
            raise NoEncontradoExcepcion("Profesional no encontrado")
        return pro

    def obtener_por_token(self, token: str) -> Profesional:
        pro = self.db.query(Profesional).filter(
            Profesional.token_publico == token,
            Profesional.esta_activo == True,
            Profesional.eliminado_en == None,
        ).first()
        if not pro:
            raise NoEncontradoExcepcion("Profesional no encontrado")
        return pro

    def listar_por_organizacion(self, organizacion_id: int):
        return self.db.query(Profesional).filter(
            Profesional.organizacion_id == organizacion_id,
            Profesional.esta_activo == True,
            Profesional.eliminado_en == None,
        ).all()

    def actualizar(self, profesional_id: int, organizacion_id: int, datos: ProfesionalActualizar) -> Profesional:
        pro = self.obtener_por_id(profesional_id, organizacion_id)
        campos = datos.model_dump(exclude_none=True)
        for campo, valor in campos.items():
            setattr(pro, campo, valor)
        self.db.commit()
        self.db.refresh(pro)
        return pro

    def eliminar(self, profesional_id: int, organizacion_id: int):
        pro = self.obtener_por_id(profesional_id, organizacion_id)
        pro.esta_activo = False
        pro.eliminado_en = datetime.utcnow()
        self.db.commit()
        return {"mensaje": "Profesional eliminado correctamente"}