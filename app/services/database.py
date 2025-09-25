from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.services.env_config_service import get_env_configs

settings = get_env_configs()
base_url = settings.postgres_url.unicode_string()
connection_string = f"{base_url}?options=-c%20search_path%3D{settings.PSQL_CHAT_SESSIONS_SCHEMA}"

engine = create_engine(connection_string)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()
