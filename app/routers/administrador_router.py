# app/routers/administrador_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.base_datos.conexion import get_db
from app.servicios.administrador_servicio import AdministradorServicio
from app.esquemas.administrador_esquema import AdminLoginEntrada, AdminTokenSalida
from app.esquemas.auth_esquema import RefrescarTokenEntrada

router = APIRouter(prefix="/api/v1/admin", tags=["Administrador"])


@router.post("/login", response_model=AdminTokenSalida)
def login_admin(datos: AdminLoginEntrada, db: Session = Depends(get_db)):
    return AdministradorServicio(db).login(datos)


@router.post("/refresh", response_model=AdminTokenSalida)
def refrescar_token_admin(datos: RefrescarTokenEntrada, db: Session = Depends(get_db)):
    return AdministradorServicio(db).refrescar(datos)