from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.servicios.auth_servicio import AuthServicio
from app.esquemas.auth_esquema import (
    LoginEntrada, TokenSalida, RefrescarTokenEntrada
)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenSalida)
def login(datos: LoginEntrada, db: Session = Depends(get_db)):
    """
    Recibe email y password.
    Devuelve access_token y refresh_token.
    """
    return AuthServicio(db).login(datos)


@router.post("/refresh", response_model=TokenSalida)
def refrescar_token(datos: RefrescarTokenEntrada, db: Session = Depends(get_db)):
    """
    Recibe el refresh_token.
    Devuelve un nuevo par de tokens.
    """
    return AuthServicio(db).refrescar(datos)