from sqlalchemy.orm import Session
from .models import Base
from config import engine


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    from config import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
