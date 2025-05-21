from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str


class ErrorResponse(BaseModel):
    error: str


class Message(BaseModel):
    role: str
    parts: list[str]


class ChatHistoryResponse(BaseModel):
    user_id: str
    history: list[Message]
