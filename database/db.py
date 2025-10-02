# database/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import SQLALCHEMY_DATABASE_URL

# Para SQLite: se necesita este parámetro extra
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



# ✅ ESTA ES LA FUNCIÓN QUE NECESITAMOS
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()