from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.base_datos.conexion import Base, engine, verificar_conexion

# ── Importar todos los modelos ────────────────────────────────────────
from app.modelos import organizacion_modelo      # noqa
from app.modelos import plan_modelo              # noqa
from app.modelos import suscripcion_modelo       # noqa
from app.modelos import usuario_modelo           # noqa
from app.modelos import profesional_modelo       # noqa
from app.modelos import especialidad_modelo      # noqa
from app.modelos import prof_especialidad_modelo # noqa
from app.modelos import horario_modelo           # noqa
from app.modelos import fecha_bloqueada_modelo   # noqa
from app.modelos import paciente_modelo          # noqa
from app.modelos import cita_modelo              # noqa
from app.modelos import pago_modelo              # noqa
from app.modelos import nota_cita_modelo         # noqa
from app.modelos import calificacion_modelo      # noqa
from app.modelos import notificacion_modelo      # noqa
from app.modelos import administrador_modelo    # noqa  

# ── Crear tablas ──────────────────────────────────────────────────────
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas en MySQL")
except Exception as e:
    print(f"⚠️ Error al crear tablas: {e}")

# ── Importar routers ──────────────────────────────────────────────────
from app.routers import auth_router
from app.routers import organizacion_router
from app.routers import profesional_router
from app.routers import horario_router
from app.routers import cita_router
from app.routers import paciente_router
from app.routers import publico_router
from app.routers import administrador_router

# ── Scheduler ─────────────────────────────────────────────────────────
scheduler = BackgroundScheduler(timezone="America/Guayaquil")


def enviar_resumenes_diarios():
    """Corre todos los días a las 7am — resumen de citas del día."""
    from app.base_datos.conexion import SessionLocal
    from app.modelos.profesional_modelo import Profesional
    from app.modelos.cita_modelo import Cita
    from app.servicios.notificacion_servicio import NotificacionServicio
    from datetime import date
    db = SessionLocal()
    try:
        hoy_inicio = datetime.combine(date.today(), datetime.min.time())
        hoy_fin    = datetime.combine(date.today(), datetime.max.time())
        profesionales = db.query(Profesional).filter(
            Profesional.esta_activo == True,
            Profesional.eliminado_en == None,
            Profesional.telefono != None,
        ).all()
        for profesional in profesionales:
            citas_hoy = db.query(Cita).filter(
                Cita.profesional_id == profesional.id,
                Cita.estado == "confirmada",
                Cita.inicio >= hoy_inicio,
                Cita.inicio <= hoy_fin,
            ).all()
            NotificacionServicio(db).enviar_resumen_diario(
                nombre_profesional=profesional.nombre_completo,
                telefono_profesional=profesional.telefono,
                citas=citas_hoy,
            )
    except Exception as e:
        print(f"⚠️ Error en resumen diario: {str(e)}")
    finally:
        db.close()


# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgendaPro API",
    version="1.0.0",
    description="SaaS de agendamiento para profesionales",
    debug=True,
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar routers ─────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(organizacion_router.router)
app.include_router(profesional_router.router)
app.include_router(horario_router.router)
app.include_router(cita_router.router)
app.include_router(paciente_router.router)
app.include_router(publico_router.router)
app.include_router(administrador_router.router)

# ── Startup ───────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    print("\n" + "="*45)
    print("🚀 AGENDAPRO BACKEND INICIANDO")
    print("="*45)
    verificar_conexion()

    scheduler.add_job(
        enviar_resumenes_diarios,
        trigger="cron",
        hour=7,
        minute=0,
        id="resumen_diario",
        replace_existing=True,
    )
    scheduler.start()
    print("🕐 Scheduler iniciado — resumen diario a las 07:00")
    print("="*45 + "\n")


# ── Shutdown ──────────────────────────────────────────────────────────
@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown(wait=False)
    print("🔒 AgendaPro detenido")


# ── Health check ──────────────────────────────────────────────────────
@app.get("/", tags=["Sistema"])
def root():
    return {
        "app": "AgendaPro",
        "version": "1.0.0",
        "status": "running",
        "docs": "http://localhost:8000/docs"
    }


# ── Manejo global de errores ──────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "detalle": traceback.format_exc()
        }
    )