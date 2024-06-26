FROM python:3.11

RUN mkdir /fastapi_task_manager

WORKDIR /fastapi_task_manager

RUN pip install poetry

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install

COPY . /fastapi_task_manager
