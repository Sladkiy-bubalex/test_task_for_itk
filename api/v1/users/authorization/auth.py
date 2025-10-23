from fastapi import APIRouter, status

from database.dependencies import SessionDependancy

from api.v1.users.services import create_access_token
from api.v1.users.authorization.services import authenticate_user
from api.v1.users.authorization.schemas import (
    LoginUserRequestSchema,
    LoginUserResponseSchema
)
from api.v1.errors import ErrorResponse


router = APIRouter()


@router.post(
    "/login",
    response_model=LoginUserResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Unauthorized"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Not found"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal Server Error"
        }
    }
)
async def login(
    login_data: LoginUserRequestSchema,
    session: SessionDependancy
):
    data = login_data.model_dump()
    user = await authenticate_user(session=session, user_data=data)
    token = await create_access_token(user_obj=user)

    return {
        "access_token": token,
        "token_type": "Bearer"
    }
