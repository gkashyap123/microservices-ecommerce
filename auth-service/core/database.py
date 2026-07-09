import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from .config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(retries: int = 10, delay: float = 3.0) -> None:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            with engine.connect():
                return
        except OperationalError as exc:
            last_error = exc
            time.sleep(delay)
    raise last_error
