import pathlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

path = pathlib.Path(__file__).parent.absolute()


SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgrespw@localhost:49153"


engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
