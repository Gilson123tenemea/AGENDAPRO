from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import re


# ======================================================================
# REGISTRO — Paso 1 (datos mínimos obligatorios)
# Lo llena el admin cuando se registra en /registro
# ======================================================================
class OrganizacionCrear(BaseModel):
    # Datos de la organización
    nombre: str
    slug: str
    email: EmailStr
    telefono: Optional[str] = None

    # Credenciales del primer usuario admin
    admin_email: EmailStr
    admin_password: str

    @field_validator("slug")
    @classmethod
    def slug_valido(cls, v):
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "El slug solo acepta minúsculas, números y guiones. "
                "Ejemplo: mi-consultorio"
            )
        if len(v) < 3:
            raise ValueError("El slug debe tener mínimo 3 caracteres")
        return v

    @field_validator("admin_password")
    @classmethod
    def password_longitud(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


# ======================================================================
# COMPLETAR PERFIL — Paso 2 (opcional pero recomendado)
# El admin lo llena desde /admin/organizacion/completar
# El paciente verá esta información en el perfil público del profesional
# ======================================================================
class OrganizacionCompletarPerfil(BaseModel):
    descripcion: Optional[str] = None        # descripción de la clínica
    direccion: Optional[str] = None          # dirección física
    ciudad: Optional[str] = None             # ciudad donde opera
    sitio_web: Optional[str] = None          # página web si tiene
    redes_sociales: Optional[str] = None     # instagram, facebook, etc.
    logo_url: Optional[str] = None           # URL del logo subido


# ======================================================================
# ACTUALIZAR — datos básicos editables en cualquier momento
# El admin lo usa desde /admin/organizacion
# ======================================================================
class OrganizacionActualizar(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    descripcion: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    sitio_web: Optional[str] = None
    redes_sociales: Optional[str] = None
    logo_url: Optional[str] = None


# ======================================================================
# SALIDA INTERNA — lo que ve el admin en su panel
# ======================================================================
class OrganizacionSalida(BaseModel):
    id: int
    nombre: str
    slug: str
    email: str
    telefono: Optional[str]
    logo_url: Optional[str]
    descripcion: Optional[str]
    direccion: Optional[str]
    ciudad: Optional[str]
    sitio_web: Optional[str]
    redes_sociales: Optional[str]
    esta_activo: bool
    perfil_completo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ======================================================================
# SALIDA PÚBLICA — lo que ve el paciente del consultorio
# Solo información relevante, sin datos internos
# ======================================================================
class OrganizacionPublicaSalida(BaseModel):
    nombre: str
    descripcion: Optional[str]
    direccion: Optional[str]
    ciudad: Optional[str]
    telefono: Optional[str]
    sitio_web: Optional[str]
    logo_url: Optional[str]

    model_config = {"from_attributes": True}


# ======================================================================
# SALIDA SUPERADMIN — lo que ve el superadmin en su panel
# Incluye datos de control que el admin normal no ve
# ======================================================================
class OrganizacionSuperadminSalida(BaseModel):
    id: int
    nombre: str
    slug: str
    email: str
    telefono: Optional[str]
    ciudad: Optional[str]
    esta_activo: bool
    perfil_completo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ======================================================================
# RESPUESTA AL REGISTRAR
# Devuelve la organización y el usuario admin creados
# ======================================================================
class OrganizacionConUsuarioSalida(BaseModel):
    organizacion: OrganizacionSalida
    usuario: "UsuarioSalida"
    mensaje: str = "Organización registrada correctamente"


from app.esquemas.usuario_esquema import UsuarioSalida
OrganizacionConUsuarioSalida.model_rebuild()