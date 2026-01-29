from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Path, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRouter
from pydantic import Field, BaseModel
from sqlmodel import Session, select
from starlette.responses import JSONResponse

from models import Todo
from serializers import TodoResponse, TodoCreateRequest, TodoUpdateRequest
from settings import create_db_and_tables, get_session, logger


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    if exc.errors()[0]["input"] is None:
        detail = "body: Body required"
    else:
        detail = f"{exc.errors()[0]['loc'][1]}: {exc.errors()[0]['msg']}"
    logger.error(detail)
    return JSONResponse(status_code=400, content={"detail": detail})


class FilterParams(BaseModel):
    status: str | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=25)


@router.get("/healthcheck", response_model=dict)
async def healthcheck():
    return {"status": "healthy"}


@router.post("/todos", response_model=TodoResponse, status_code=201)
async def create_todo(
        request: Request,
        response: Response,
        item: TodoCreateRequest,
        session: Session = Depends(get_session),
):
    logger.info(f"Creating new task: {item.title}")
    todo = Todo(**item.model_dump(), status="new")
    session.add(todo)
    session.commit()
    session.refresh(todo)
    logger.success("Task created successfully")
    location = request.url_for("get_todo", pk=todo.id)
    response.headers["Location"] = str(location)

    return TodoResponse(**todo.model_dump())


@router.put("/todos/{pk}", response_model=TodoResponse)
async def update_todo(
        pk: Annotated[int, Path(title="ID of the task")],
        item: TodoUpdateRequest,
        session: Session = Depends(get_session),
):
    logger.info(f"Updating task {pk}")
    task = session.get(Todo, pk)
    if not task:
        logger.error(f"Task {pk} not found")
        raise HTTPException(status_code=404, detail=f"Task {pk} not found")
    task.title = item.title
    task.status = item.status
    session.commit()
    session.refresh(task)
    logger.success(f"Task {pk} updated successfully")
    return task


@router.get("/todos/{pk}", response_model=TodoResponse, name="get_todo")
async def get_todo(
        pk: Annotated[int, Path(title="ID of the task")],
        session: Session = Depends(get_session),
):
    logger.info(f"Getting task {pk}")
    response = session.get(Todo, pk)
    if response:
        logger.success(f"Task {pk} found successfully")
        return response
    logger.error(f"Task {pk} not found")
    raise HTTPException(status_code=404, detail=f"Task {pk} not found")


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
    logger.info(f"Marking task {pk} as completed")
    task = session.get(Todo, pk)
    if not task:
        logger.error(f"Task {pk} not found")
        raise HTTPException(status_code=404, detail=f"Task {pk} not found")
    task.status = "completed"
    session.commit()
    session.refresh(task)
    logger.success(f"Task {pk} marked as completed successfully")
    return task


@router.delete("/todos/{pk}", response_model=None, status_code=204)
async def delete_todo(
        pk: Annotated[int, Path(title="ID of the task")],
        session: Session = Depends(get_session),
):
    logger.info(f"Deleting task {pk}")
    task = session.get(Todo, pk)
    if not task:
        logger.error(f"Task {pk} not found")
        raise HTTPException(status_code=404, detail=f"Task {pk} not found")
    session.delete(task)
    session.commit()
    logger.success(f"Task {pk} deleted successfully")
    return None


app.include_router(router)
