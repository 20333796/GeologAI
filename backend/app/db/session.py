"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
import os

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/geologai"
)

# Determine connect_args based on driver (SQLite doesn't accept charset/connect_timeout)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific args
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args=connect_args,
    )
else:
    # Default (MySQL / other) connection args and pooling
    connect_args = {
        "charset": "utf8mb4",
        "connect_timeout": 10,
    }
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=40,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False,
        connect_args=connect_args,
    )

# Create Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables - WARNING: This will delete all data
    """
    Base.metadata.drop_all(bind=engine)
