from sqlalchemy.orm import Session
from datetime import datetime
from app.modelos.organizacion_modelo import Organizacion
from app.modelos.usuario_modelo import Usuario
from app.esquemas.organizacion_esquema import (
    OrganizacionCrear,
    OrganizacionActualizar,
    OrganizacionCompletarPerfil,
)
from app.core.seguridad import encriptar_password
from app.core.excepciones import NoEncontradoExcepcion, ConflictoExcepcion
from app.core.enumeraciones import RolUsuario


class OrganizacionServicio:

    def __init__(self, db: Session):
        self.db = db

    def registrar(self, datos: OrganizacionCrear):
        """
        Paso 1 del registro.
        Crea la organización y el primer usuario admin.
        Todo en una sola transacción.
        """
        if self.db.query(Organizacion).filter(
            Organizacion.slug == datos.slug
        ).first():
            raise ConflictoExcepcion(
                f"El slug '{datos.slug}' ya está en uso. "
                f"Elige otro nombre para tu consultorio."
            )

        if self.db.query(Usuario).filter(
            Usuario.email == datos.admin_email
        ).first():
            raise ConflictoExcepcion(
                f"El email '{datos.admin_email}' ya está registrado."
            )

        try:
            org = Organizacion(
                nombre=datos.nombre,
                slug=datos.slug,
                email=datos.email,
                telefono=datos.telefono,
            )
            self.db.add(org)
            self.db.flush()

            usuario = Usuario(
                organizacion_id=org.id,
                email=datos.admin_email,
                password_hasheado=encriptar_password(datos.admin_password),
                rol=RolUsuario.ADMIN_ORG,
            )
            self.db.add(usuario)
            self.db.commit()
            self.db.refresh(org)
            self.db.refresh(usuario)
            return org, usuario

        except Exception:
            self.db.rollback()
            raise

    def completar_perfil(
        self, org_id: int, datos: OrganizacionCompletarPerfil
    ) -> Organizacion:
        """
        Paso 2 del registro — completar perfil de la organización.
        El admin lo hace desde su panel después de registrarse.
        """
        org = self.obtener_por_id(org_id)
        campos = datos.model_dump(exclude_none=True)
        for campo, valor in campos.items():
            setattr(org, campo, valor)
        org.perfil_completo = True
        self.db.commit()
        self.db.refresh(org)
        return org

    def obtener_por_id(self, org_id: int) -> Organizacion:
        org = self.db.query(Organizacion).filter(
            Organizacion.id == org_id,
            Organizacion.esta_activo == True,
        ).first()
        if not org:
            raise NoEncontradoExcepcion("Organización no encontrada")
        return org

    def obtener_por_slug(self, slug: str) -> Organizacion:
        org = self.db.query(Organizacion).filter(
            Organizacion.slug == slug,
            Organizacion.esta_activo == True,
        ).first()
        if not org:
            raise NoEncontradoExcepcion("Organización no encontrada")
        return org

    def actualizar(
        self, org_id: int, datos: OrganizacionActualizar
    ) -> Organizacion:
        org = self.obtener_por_id(org_id)
        campos = datos.model_dump(exclude_none=True)
        for campo, valor in campos.items():
            setattr(org, campo, valor)
        self.db.commit()
        self.db.refresh(org)
        return org

    def cambiar_estado(self, org_id: int, esta_activo: bool) -> Organizacion:
        org = self.db.query(Organizacion).filter(
            Organizacion.id == org_id
        ).first()
        if not org:
            raise NoEncontradoExcepcion("Organización no encontrada")
        org.esta_activo = esta_activo
        self.db.commit()
        self.db.refresh(org)
        return org

    def listar_todas(self, skip: int = 0, limit: int = 50):
        return self.db.query(Organizacion).offset(skip).limit(limit).all()