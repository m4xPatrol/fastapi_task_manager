from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.api.dependencies.websocket import ws_manager
from app.core.jwt import get_user_by_token
from app.db.crud.task import task_crud
from app.db.crud.user import user_crud
from app.db.database import get_session
from app.api.schemas.websocket import WebSocketResponse

router = APIRouter()

active_connections: list[WebSocket] = []


@router.websocket("/ws/tasks/{client_id}")
async def websocket_endpoint(client_id: int, websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)

    try:
        while True:
            response: WebSocketResponse = await ws_manager.get_message(websocket)
            print(f"Response: {response}")
            await ws_manager.broadcast(response)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_session),
    username: str = Depends(get_user_by_token),
) -> TaskResponse:
    user_db = await user_crud.get_user_by_username(db, username)
    task_db = await task_crud.add_task(db, task, user_db.id)

    try:
        await ws_manager.broadcast(
            WebSocketResponse(message=f"New task created: {task_db.title}")
        )
        return task_db

    except IntegrityError:
        pass


@router.get("/tasks", response_model=list[TaskResponse])
async def read_tasks(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0)] = 10,
    db: AsyncSession = Depends(get_session),
) -> list[TaskResponse]:
    tasks = await task_crud.get_tasks(db, skip, limit)
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: int, db: AsyncSession = Depends(get_session)
) -> TaskResponse:
    task = await task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_session)
) -> TaskResponse:
    db_task = await task_crud.update_task(db, task_id, task_update)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    try:
        await ws_manager.broadcast(
            WebSocketResponse(message=f"Task {db_task.id} updated")
        )
        return db_task

    except IntegrityError:
        pass


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(
    task_id: int, db: AsyncSession = Depends(get_session)
) -> TaskResponse:
    task = await task_crud.delete_task(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    try:
        await ws_manager.broadcast(WebSocketResponse(message=f"Task {task.id} deleted"))
        return task

    except IntegrityError:
        pass
