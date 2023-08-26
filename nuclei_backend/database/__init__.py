import pathlib
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

path = pathlib.Path(__file__).parent.absolute()


SQLALCHEMY_DATABASE_URI1 = "postgresql://postgres:postgrespw@localhost:5432"

SQLALCHEMY_DATABASE_URI_DEV = (
    "postgresql://postgres:postgrespw@170.64.180.130:5432/postgres"
)


engine = create_engine(
    SQLALCHEMY_DATABASE_URI_DEV,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()
