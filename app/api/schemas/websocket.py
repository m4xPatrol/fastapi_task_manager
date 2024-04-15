from pydantic import BaseModel


class WebSocketResponse(BaseModel):
    message: str
