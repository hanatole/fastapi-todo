from sqlmodel import SQLModel
from sqlmodel import create_engine, Session

engine = create_engine(
    "sqlite:///db.sqlite3", echo=True, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
