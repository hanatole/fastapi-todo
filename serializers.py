from typing import Literal

from pydantic import BaseModel


class TodoCreateRequest(BaseModel):
    title: str


class TodoUpdateRequest(BaseModel):
    title: str
    status: Literal["new", "doing", "completed"]


class TodoResponse(BaseModel):
    id: int
    title: str
    status: str
