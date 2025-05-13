from pydantic import BaseModel


class ChatResponse(BaseModel):
    response: str


class ErrorResponse(BaseModel):
    error: str
