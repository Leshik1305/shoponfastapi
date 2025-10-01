from sqlalchemy.orm import Session
from fastapi import Depends
from collections.abc import Generator

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
