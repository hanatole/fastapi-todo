from sqlmodel import Field

from settings import SQLModel


class Todo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    status: str
