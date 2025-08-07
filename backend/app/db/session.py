# db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependencia para obtener una sesión de base de datos (modo síncrono)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
