import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DB_USER     = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "3306")
DB_NAME     = os.getenv("DB_NAME", "agendapro")

print(f"🔧 Conectando a: {DB_HOST}:{DB_PORT}/{DB_NAME}")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?charset=utf8mb4"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def verificar_conexion() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ MySQL: Conexión exitosa")
            return True
    except Exception as e:
        print(f"⚠️ MySQL Error: {str(e)[:150]}")
        return False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()