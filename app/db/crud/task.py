from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.schemas.task import TaskCreate, TaskUpdate
from app.db.models.task import Task


class TaskCRUD:
    async def add_task(self, db: AsyncSession, task: TaskCreate, user_id: int) -> Task:
        db_task = Task(
            title=task.title,
            description=task.description,
            owner_id=user_id
        )
        db.add(db_task)
        try:
            await db.commit()
            return db_task
        except IntegrityError as e:
            await db.rollback()
            raise e

    async def get_tasks(self, db: AsyncSession, skip: int, limit: int):
        tasks = await db.execute(select(Task).offset(skip).limit(limit))
        return tasks.scalars()

    async def get_task(self, db: AsyncSession, task_id: int):
        task = await db.execute(select(Task).where(Task.id == task_id))
        return task.scalars().first()

    async def update_task(self, db: AsyncSession, task_id: int, task_update: TaskUpdate) -> Task:
        db_task = await task_crud.get_task(db, task_id)
        for key, value in task_update.model_dump().items():
            setattr(db_task, key, value)
        try:
            await db.commit()
            await db.refresh(db_task)
            return db_task

        except IntegrityError as e:
            await db.rollback()
            raise e

    async def delete_task(self, db: AsyncSession, task_id: int) -> Task:
        try:
            db_task = await task_crud.get_task(db, task_id)
            await db.delete(db_task)
            await db.commit()
            return db_task
        except IntegrityError as e:
            await db.rollback()
            raise e


task_crud = TaskCRUD()
