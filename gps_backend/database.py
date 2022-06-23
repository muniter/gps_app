from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from . import utils
import urllib.parse
from os import environ

DB_URL = "sqlite:///./app.db"
engine = None

env = utils.dotenv_load() or environ
if env.get("POSTGRES_USER") and env.get("POSTGRES_PASSWORD"):
    user = env.get("POSTGRES_USER")
    password = urllib.parse.quote_plus(env.get("POSTGRES_PASSWORD", ''))
    host = env.get("POSTGRES_HOST")
    dbname = env.get("POSTGRES_DB")
    DB_URL = f"postgresql://{user}:{password}@{host}/{dbname}"
    engine = create_engine(DB_URL, echo=True, future=True)
else:
    print("Using sqlite database")
    engine = create_engine(DB_URL, connect_args={"check_same_thread": True})

print(DB_URL)
Base = declarative_base()
session_factory = sessionmaker(bind=engine, autocommit=False)
Session = scoped_session(session_factory)
