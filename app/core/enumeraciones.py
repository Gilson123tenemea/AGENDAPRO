from enum import Enum

class RolUsuario(str, Enum):
    SUPERADMIN  = "superadmin"
    ADMIN_ORG   = "admin_org"
    PROFESIONAL = "profesional"

class EstadoCita(str, Enum):
    PENDIENTE   = "pendiente"
    CONFIRMADA  = "confirmada"
    CANCELADA   = "cancelada"
    COMPLETADA  = "completada"
    NO_ASISTIO  = "no_asistio"