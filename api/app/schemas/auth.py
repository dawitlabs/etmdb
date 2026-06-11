from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    email: str


class RegisterResponse(BaseModel):
    api_key: str
    name: str
    email: str
    rate_limit: int
    message: str
