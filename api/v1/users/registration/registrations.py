from fastapi import APIRouter, status, HTTPException

from database.dependencies import SessionDependancy

from api.v1.wallet.services import create_wallet

from api.v1.users.services import create_access_token
from api.v1.users.registration.services import create_user
from api.v1.users.registration.schemas import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
)
from api.v1.errors import ErrorResponse
from config import logger


router = APIRouter()


@router.post(
    "",
    response_model=CreateUserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "User already exists"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal Server Error"
        }
    }
)
async def registration(
    user_data: CreateUserRequestSchema,
    session: SessionDependancy
):
    data = user_data.model_dump()
    try:
        user = await create_user(session=session, user_data=data)
        wallet = await create_wallet(session=session, user_id=user.id)
        token = await create_access_token(user_obj=user)

        return {
            "id": user.id,
            "access_token": token,
            "wallet_uuid": wallet.uuid,
            "token_type": "Bearer"
        }

    except HTTPException:
        raise

    except Exception as error:
        await session.rollback()
        logger.error(f"Error creating user: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
