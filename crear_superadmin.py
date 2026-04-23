from app.base_datos.conexion import SessionLocal, engine, Base
from app.modelos.administrador_modelo import Administrador
from app.core.seguridad import encriptar_password
import os
from dotenv import load_dotenv

load_dotenv()

def crear_superadmin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existe = db.query(Administrador).filter(
            Administrador.email == os.getenv("SUPERADMIN_EMAIL")
        ).first()

        if existe:
            print(f"⚠️  Ya existe: {existe.email}")
            return

        admin = Administrador(
            email=os.getenv("SUPERADMIN_EMAIL"),
            password_hasheado=encriptar_password(os.getenv("SUPERADMIN_PASSWORD")),
        )
        db.add(admin)
        db.commit()

        print("✅ Superadmin creado")
        print(f"   Email:    {os.getenv('SUPERADMIN_EMAIL')}")
        print(f"   Password: {os.getenv('SUPERADMIN_PASSWORD')}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    crear_superadmin()