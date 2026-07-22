"""Database configuration for EnergyShield."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = Path(BASE_DIR) / "energyshield.db"
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'energyshield.db')}"


class Base(DeclarativeBase):
    """Single declarative base shared by every ORM model."""


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    """Yield a database session and always close it after the request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
