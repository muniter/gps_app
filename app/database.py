from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DB_URL = "sqlite:///./app.db"
engine = None
if os.environ.get("POSTGRES_USER") and os.environ.get("POSTGRES_PASSWORD"):
    DB_URL = "postgresql://{}:{}@localhost:{}/database".format(
        os.environ.get("POSTGRES_USER"),
        os.environ.get("POSTGRES_PASSWORD"),
        os.environ.get("POSTGRES_PORT"),
    )
    engine = create_engine(DB_URL)
else:
    engine = create_engine(DB_URL, connect_args={"check_same_thread": True})

SessonLocal = sessionmaker(bind=engine, autocommit=False)
Base = declarative_base()
