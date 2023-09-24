from httpx import AsyncClient
import pytest

jwt_token = None
task_id = None


def auth_header():
    global jwt_token
    return {"Authorization": f"Bearer {jwt_token}"}


@pytest.mark.anyio
async def test_async_create_user(async_client: AsyncClient):
    response = await async_client.post("/register", json={"username": "test123456",
                                                          "full_name": "Test User",
                                                          "password": "passw0rd",
                                                          "age": 23,
                                                          "email": "test123456@test3.com"})
    assert response.status_code == 200
    assert "username" in response.json()
    assert "email" in response.json()
    assert "password" not in response.json()


@pytest.mark.anyio
async def test_login(async_client: AsyncClient):
    global jwt_token

    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    response = await async_client.post("/login", data={"username": "test123456", "password": "passw0rd"},
                                       headers=headers)
    jwt_token = response.json().get("access_token")
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json().get("token_type") == "bearer"


@pytest.mark.anyio
async def test_read_user(async_client: AsyncClient):
    response = await async_client.get("/about_me", headers=auth_header())
    assert response.status_code == 200
    assert response.json()["username"] == "test123456"
    assert response.json()["age"] == 23
    assert response.json()["email"] == "test123456@test3.com"


@pytest.mark.anyio
async def test_create_task(async_client: AsyncClient):
    global task_id
    response = await async_client.post("/tasks", headers=auth_header(), json={"title": "Test Title",
                                                                              "description": "12345"})
    assert response.status_code == 200
    assert "id" in response.json()
    task_id = response.json()["id"]
    assert response.json()["completed"] is False
    assert response.json()["title"] == "Test Title"
    assert response.json()["description"] == "12345"


@pytest.mark.anyio
async def test_read_task(async_client: AsyncClient):
    response = await async_client.get(f"/tasks/{task_id}", headers=auth_header())
    assert response.json()["title"] == "Test Title"
    assert response.json()["description"] == "12345"
    assert response.json()["completed"] is False


@pytest.mark.anyio
async def test_read_tasks(async_client: AsyncClient):
    response = await async_client.get("/tasks", headers=auth_header())
    testing_task = [task for task in response.json() if task["id"] == task_id][0]
    assert testing_task["title"] == "Test Title"
    assert testing_task["description"] == "12345"
    assert testing_task["completed"] is False


@pytest.mark.anyio
async def test_update_task(async_client: AsyncClient):
    response = await async_client.put(f"/tasks/{task_id}", headers=auth_header(), json={"title": "Test Title",
                                                                                        "description": "12345",
                                                                                        "completed": True})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Title"
    assert response.json()["description"] == "12345"
    assert response.json()["completed"] is True
    pass


@pytest.mark.anyio
async def test_delete_task(async_client: AsyncClient):
    response = await async_client.delete(f"tasks/{task_id}", headers=auth_header())
    assert response.json()["title"] == "Test Title"
    assert response.json()["description"] == "12345"
    assert response.json()["completed"] is True
    pass
