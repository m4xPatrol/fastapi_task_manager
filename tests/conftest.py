import pytest
from httpx import AsyncClient
from main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000/api/v1") as async_client:
        print("Client is ready")
        yield async_client
