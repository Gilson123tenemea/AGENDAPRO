from fastapi import HTTPException, status

class NoEncontradoExcepcion(HTTPException):
    def __init__(self, detalle="Recurso no encontrado"):
        super().__init__(status_code=404, detail=detalle)

class NoAutorizadoExcepcion(HTTPException):
    def __init__(self, detalle="No autorizado"):
        super().__init__(status_code=401, detail=detalle, headers={"WWW-Authenticate": "Bearer"})

class SinPermisoExcepcion(HTTPException):
    def __init__(self, detalle="Sin permiso para esta acción"):
        super().__init__(status_code=403, detail=detalle)

class ConflictoExcepcion(HTTPException):
    def __init__(self, detalle="Conflicto con datos existentes"):
        super().__init__(status_code=409, detail=detalle)

class SolicitudInvalidaExcepcion(HTTPException):
    def __init__(self, detalle="Solicitud inválida"):
        super().__init__(status_code=400, detail=detalle)

class HorarioNoDisponibleExcepcion(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="El horario seleccionado ya no está disponible")