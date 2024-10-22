from typing import Optional

from pydantic import BaseModel


class AuthCollectRequest(BaseModel):
    code: str


class AuthCollectResponse(BaseModel):
    session: str


class GetSessionResponse(BaseModel):
    name: str
    picture: Optional[str] = None
    shouldRefreshToken: bool
    expireAt: str
