from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.websockets import WebSocket, WebSocketDisconnect

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.db.database import get_session
from app.api.models.task import Task
from app.api.models.user import User
from app.core.security import get_user_by_token


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
    user = await db.execute(select(User).where(User.username == username))
    user = user.scalars().first()

    db_task = Task(**task.model_dump(), owner_id=user.id)
    db.add(db_task)

    try:
        await db.commit()
        for connection in active_connections:
            await connection.send_text(f"New task created: {db_task.title}")
        return db_task

    except IntegrityError as e:
        await db.rollback()


@router.get("/tasks", response_model=List[TaskResponse])
async def read_tasks(skip: Annotated[int, Query(ge=0)] = 0,
                     limit: Annotated[int, Query(ge=0)] = 10,
                     db: AsyncSession = Depends(get_session)):
    tasks = await db.execute(select(Task).offset(skip).limit(limit))
    return tasks.scalars()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int, db: AsyncSession = Depends(get_session)):
    task = await db.execute(select(Task).where(Task.id == task_id))
    task = task.scalars().first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_session)):
    db_task = await db.execute(select(Task).where(Task.id == task_id))
    db_task = db_task.scalars().first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    for key, value in task_update.model_dump().items():
        setattr(db_task, key, value)

    try:
        await db.commit()
        await db.refresh(db_task)
        await db.commit()
        for connection in active_connections:
            await connection.send_text(f"Task {db_task.id} updated")
        return db_task

    except IntegrityError as e:
        await db.rollback()


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_session)):
    task = await db.execute(select(Task).where(Task.id == task_id))
    task = task.scalars().first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    try:
        await db.delete(task)
        await db.commit()
        for connection in active_connections:
            await connection.send_text(f"Task {task.id} deleted")
        return task

    except IntegrityError as e:
        await db.rollback()


