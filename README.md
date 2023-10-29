# FastAPI Task Manager application
Task Manager FastAPI is a simple task management API built using FastAPI + PostgreSQL. It provides basic CRUD operations for tasks and includes real-time updates for task status changes via WebSocket.

## Features:
* User registration and authentication (OAuth2 + JWT)
* Access and refresh token usage
* Real-time updates for task status changes using WebSocket
* Custom logger
* Asynchronous routes
* Asynchronous database access (asyncpg)
* Easy to installation (poetry)

## Getting started
### Prerequisites
Before running the application, make sure you have the following prerequisites installed:

* Python 3.11
* PostgreSQL

### Installation
1. Clone the repository

   ```bash
   git clone https://github.com/m4xPatrol/fastapi_task_manager.git
   cd task_manager_fastapi
   ```

2. Install [Poetry](https://python-poetry.org/docs/#installation)
3. Create a virtual environment

   ```bash
   poetry install
   ```

## Usage
### Running the Application

To run the FastAPI application locally, use the following command:

```bash
poetry run python main.py
```
## Testing the application with PyTest
### Running the tests

1. Navigate to the `task_manager_fastapi` (root) directory using a terminal:

```bash
cd <your_path_to_project>/task_manager_fastapi
```

2. Run the tests by executing the following command:

```bash
poetry run pytest
```
