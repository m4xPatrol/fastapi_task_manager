from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.websockets import WebSocket, WebSocketDisconnect

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.api.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.db.database import get_session
from app.core.jwt import get_user_by_token
from app.db.crud.user import user_crud
from app.db.crud.task import task_crud


router = APIRouter()

active_connections: list[WebSocket] = []


@router.websocket('/ws/tasks/{client_id}')
async def websocket_endpoint(client_id: int, websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            for connection in active_connections:
                await connection.send_text(f"Client: {client_id} Message: {message}!")

    except WebSocketDisconnect:
        active_connections.remove(websocket)


@router.post('/tasks', response_model=TaskResponse)
async def create_task(task: TaskCreate,
                      db: AsyncSession = Depends(get_session),
                      username: str = Depends(get_user_by_token)):
    user_db = await user_crud.get_user(db, username)
    task_db = await task_crud.add_task(db, task, user_db.id)

    try:
        for connection in active_connections:
            await connection.send_text(f"New task created: {task_db.title}")
        return task_db

    except IntegrityError:
        pass


@router.get("/tasks", response_model=List[TaskResponse])
async def read_tasks(skip: Annotated[int, Query(ge=0)] = 0,
                     limit: Annotated[int, Query(ge=0)] = 10,
                     db: AsyncSession = Depends(get_session)):
    tasks = await task_crud.get_tasks(db, skip, limit)
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int, db: AsyncSession = Depends(get_session)):
    task = await task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_session)):
    db_task = await task_crud.update_task(db, task_id, task_update)

    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    try:
        for connection in active_connections:
            await connection.send_text(f"Task {db_task.id} updated")
        return db_task

    except IntegrityError:
        pass


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_session)):
    task = await task_crud.delete_task(db, task_id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    try:
        for connection in active_connections:
            await connection.send_text(f"Task {task.id} deleted")
        return task

    except IntegrityError:
        pass


