import logging

from app.log.log_config import LogConfig

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

import asyncio
import typer

from app.api.endpoints import tasks, users
from app.core.security import get_user_by_token
from app.db.database import init_models


app = FastAPI()

cli = typer.Typer()


app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"], dependencies=[Depends(get_user_by_token)])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
# app.middleware("http")(logging_middleware)


@cli.command()
def startup_db():
    asyncio.run(init_models())


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger = logging.getLogger("uvicorn.error")
    logger.exception("Global Exception handler raised")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


@app.get("/")
def read_root():
    return {"message": "Welcome to the Real-Time Task Manager API"}


if __name__ == "__main__":
    # cli()

    import uvicorn

    # logging.getLogger("uvicorn.access")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=LogConfig().model_dump(), use_colors=True)
