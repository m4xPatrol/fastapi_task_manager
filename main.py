import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.endpoints import tasks, users
from app.core.jwt import get_user_by_token
from app.db.database import init_db
from app.log.log_config import LogConfig

app = FastAPI()


app.include_router(
    tasks.router,
    prefix="/api/v1",
    tags=["Tasks"],
    dependencies=[Depends(get_user_by_token)],
)
app.include_router(users.router, prefix="/api/v1", tags=["Users"])


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger = logging.getLogger("uvicorn.error")
    logger.exception("Global Exception handler raised")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Real-Time Task Manager API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_config=LogConfig().model_dump(),
        use_colors=True,
    )
