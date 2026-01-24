from typing import Literal

from pydantic import BaseModel, Field


class TodoCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)


class TodoUpdateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    status: Literal["new", "doing", "completed"]


class TodoResponse(BaseModel):
    id: int
    title: str
    status: str
