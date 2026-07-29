from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from config.settings import settings
import os

# Base class for SQLAlchemy ORM models
Base = declarative_base()

# Determine engine parameters
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite requires check_same_thread=False for Streamlit's multi-threaded model
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create engine
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

def init_db():
    """Initializes the database and creates all tables."""
    # Ensure database folder is created if using local file path
    if settings.DATABASE_URL.startswith("sqlite"):
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Provides a transactional database session scope."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()