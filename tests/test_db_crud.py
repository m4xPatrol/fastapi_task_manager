from sqlalchemy import select

from app.api.schemas.task import TaskUpdate
from app.api.schemas.user import UserCreate
from app.core.security import verify_password
from app.db.crud.task import task_crud
from app.db.crud.user import user_crud
from app.db.models.task import Task
from app.db.models.user import User
from tests.conftest import async_session_maker

test_user = UserCreate(
    username="username",
    full_name="Full Name",
    email="email@test.com",
    age=29,
    password="t3$tp@ssw0rD",
)

test_task = Task(title="Test Title", description="Test description")

update_task = TaskUpdate(
    title="Updated Title", description="Updated Description", completed=True
)


async def test_add_user():
    async with async_session_maker() as db:
        crud_result = await user_crud.add_user(db, test_user)
        assert crud_result.username == test_user.username
        assert crud_result.full_name == test_user.full_name
        assert crud_result.email == test_user.email
        assert crud_result.age == test_user.age
        assert verify_password(test_user.password, crud_result.hashed_password)

        db_result = await db.execute(
            select(User).where(User.username == test_user.username)
        )
        db_result = db_result.scalar_one()
        assert crud_result == db_result


async def test_get_user():
    async with async_session_maker() as db:
        crud_result = await user_crud.get_user_by_username(db, test_user.username)
        assert crud_result.username == test_user.username
        assert crud_result.full_name == test_user.full_name
        assert crud_result.email == test_user.email
        assert crud_result.age == test_user.age

        db_result = await db.execute(
            select(User).where(User.username == test_user.username)
        )
        db_result = db_result.scalar_one()
        assert crud_result == db_result


async def test_add_task():
    async with async_session_maker() as db:
        crud_result = await task_crud.add_task(db, test_task, 1)
        assert crud_result.title == test_task.title
        assert crud_result.description == test_task.description

        db_result = await db.execute(select(Task).where(Task.id == crud_result.id))
        db_result = db_result.scalar_one()
        assert crud_result == db_result


async def test_get_tasks(skip=0, limit=10):
    async with async_session_maker() as db:
        crud_result = await task_crud.get_tasks(db, skip, limit)
        crud_result_one = crud_result.all()[0]
        assert crud_result_one.title == test_task.title
        assert crud_result_one.description == test_task.description

        db_result = await db.execute(select(Task).offset(skip).limit(limit))
        db_result_one = db_result.scalars().all()[0]
        assert db_result_one == crud_result_one


async def test_get_task():
    async with async_session_maker() as db:
        crud_result = await task_crud.get_task(db, 1)
        assert crud_result.title == test_task.title
        assert crud_result.description == test_task.description
        assert crud_result.completed is False

        db_result = await db.execute(select(Task).where(Task.id == 1))
        db_result = db_result.scalars().first()
        assert db_result == crud_result


async def test_update_task():
    async with async_session_maker() as db:
        crud_result = await task_crud.update_task(db, 1, update_task)
        assert crud_result.title == update_task.title
        assert crud_result.description == update_task.description
        assert crud_result.completed is update_task.completed

        db_result = await db.execute(select(Task).where(Task.id == 1))
        db_result = db_result.scalars().first()
        assert db_result == crud_result


async def test_delete_task():
    async with async_session_maker() as db:
        crud_result = await task_crud.delete_task(db, 1)
        assert crud_result.title == update_task.title
        assert crud_result.description == update_task.description
        assert crud_result.completed is update_task.completed

        db_result = await db.execute(select(Task).where(Task.id == 1))
        db_result = db_result.scalars().first()
        assert db_result is None
