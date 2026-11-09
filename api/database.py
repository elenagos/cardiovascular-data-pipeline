import os
from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        os.environ.get(
            "DATABASE_URL", "postgresql+psycopg2://localhost/cardio_pipeline"
        ),
        pool_pre_ping=True,
    )
    return sessionmaker(bind=engine)


def get_db() -> Iterator[Session]:
    with get_session_factory()() as session:
        yield session
