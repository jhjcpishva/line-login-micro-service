from pydantic import BaseModel


class AuthCollectRequest(BaseModel):
    code: str


class AuthCollectResponse(BaseModel):
    session: str
