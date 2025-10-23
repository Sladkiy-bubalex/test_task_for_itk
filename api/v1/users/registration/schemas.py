from pydantic import BaseModel, field_validator
from uuid import UUID
from fastapi import HTTPException, status


class CreateUserRequestSchema(BaseModel):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 8 characters long"
            )
        return value


class CreateUserResponseSchema(BaseModel):
    id: int
    access_token: str
    wallet_uuid: UUID
    token_type: str = "Bearer"
