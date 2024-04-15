from fastapi.websockets import WebSocket
from app.api.schemas.websocket import WebSocketResponse


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def get_message(self, websocket: WebSocket) -> WebSocketResponse:
        message = await websocket.receive_json()
        print(f"Message: {message}")
        return WebSocketResponse(**message)

    async def send_personal_message(
        self, response: WebSocketResponse, websocket: WebSocket
    ) -> None:
        await websocket.send_json(response.model_dump())

    async def broadcast(self, response: WebSocketResponse) -> None:
        for connection in self.active_connections:
            await self.send_personal_message(response, connection)


ws_manager = ConnectionManager()
