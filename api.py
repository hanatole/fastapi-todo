from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Path, HTTPException
from fastapi.routing import APIRouter
from pydantic import Field, BaseModel
from sqlmodel import Session, select

from models import Todo
from serializers import TodoResponse, TodoCreateRequest, TodoUpdateRequest
from settings import create_db_and_tables, get_session


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Task manager API",
    description="Simple task manager API",
    version="1.0.0",
    redoc_url="/api/v1/redoc",
    docs_url="/api/v1/docs",
)
router = APIRouter(prefix="/api/v1")


class FilterParams(BaseModel):
    status: str | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=25)


@router.get("/healthcheck", response_model=dict)
async def healthcheck():
    return {"status": "ok"}


@router.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(item: TodoCreateRequest, session: Session = Depends(get_session)):
    todo = Todo(**item.model_dump(), status="new")
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return TodoResponse(**todo.model_dump())


@router.put("/todos/{pk}", response_model=TodoResponse)
async def update_todo(
    pk: Annotated[int, Path(title="ID of the task")],
    item: TodoUpdateRequest,
    session: Session = Depends(get_session),
):
    task = session.get(Todo, pk)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = item.title
    task.status = item.status
    session.commit()
    session.refresh(task)
    return task


@router.get("/todos/{pk}", response_model=TodoResponse)
async def get_todo(
    pk: Annotated[int, Path(title="ID of the task")],
    session: Session = Depends(get_session),
):
    response = session.get(Todo, pk)
    if response:
        return response

    raise HTTPException(status_code=404, detail="Task not found")


@router.get("/todos", response_model=list[TodoResponse])
async def get_all(q: FilterParams = Depends(), session: Session = Depends(get_session)):
    stmt = select(Todo)

    if status := q.status:
        stmt = stmt.where(Todo.status == status)

    stmt = stmt.offset(q.offset).limit(q.limit)
    tasks = session.exec(stmt).all()

    return tasks


@router.post("/todos/{pk}", response_model=TodoResponse)
async def complete_todo(
    pk: Annotated[int, Path(title="ID of the task")],
    session: Session = Depends(get_session),
):
    task = session.get(Todo, pk)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "completed"
    session.commit()
    session.refresh(task)
    return task


@router.delete("/todos/{pk}", response_model=None, status_code=204)
async def delete_todo(
    pk: Annotated[int, Path(title="ID of the task")],
    session: Session = Depends(get_session),
):
    task = session.get(Todo, pk)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return None


app.include_router(router)
