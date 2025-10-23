from pydantic import BaseModel


class TokenDataSchema(BaseModel):
    username: str


class LoginUserRequestSchema(BaseModel):
    username: str
    password: str


class LoginUserResponseSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"
