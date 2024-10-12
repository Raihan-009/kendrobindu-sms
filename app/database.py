from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

SQLALCHEMY_DATABASE_URL = "sqlite:///./kendrobindu.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def reset_database():
    global engine
    global SessionLocal

    # Close all connections
    engine.dispose()

    # Remove the database file
    if os.path.exists("./kendrobindu.db"):
        os.remove("./kendrobindu.db")

    # Recreate the engine and session
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Recreate tables
    create_tables()
