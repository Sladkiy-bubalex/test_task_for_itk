from fastapi import APIRouter
from api.v1.users.authorization.dependencies import AccessDependancy
from api.v1.wallet.schemas import (
    UpdateWalletRequestSchema,
    UpdateWalletResponseSchema,
    GetWalletResponseSchema
)
from api.v1.wallet.services import get_wallet_by_uuid, deposit, withdraw
from api.v1.wallet.services import check_or_set_ik_in_redis
from api.v1.errors import ErrorResponse
from database.dependencies import SessionDependancy
from fastapi import HTTPException, status
from config import logger


router = APIRouter()


@router.get(
    "/{wallet_uuid}",
    response_model=GetWalletResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Invalid token"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "The user does not have access to this wallet."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Wallet not found"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal Server Error"
        }
    }
)
async def get_balance_wallet(
    user: AccessDependancy,
    wallet_uuid: str,
    session: SessionDependancy
):
    wallet = await get_wallet_by_uuid(session=session, wallet_uuid=wallet_uuid)
    if user.id != wallet.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have access to this wallet."
        )
    return {
        "balance": wallet.balance
    }

@router.post(
    "/{wallet_uuid}/operation",
    response_model=UpdateWalletResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorResponse,
            "description": "Invalid token"
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponse,
            "description": "Forbidden"
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Not found"
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Already processing or done"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ErrorResponse,
            "description": "Internal Server Error"
        }
    }
)
async def update_wallet(
    user: AccessDependancy,
    wallet_uuid: str,
    payload: UpdateWalletRequestSchema,
    session: SessionDependancy
):
    wallet = await get_wallet_by_uuid(session=session, wallet_uuid=wallet_uuid)
    data = payload.model_dump()
    data["wallet_uuid"] = wallet.uuid

    if data.get("idempotency_key"):
        redis_key = (
            f"idemp:{data.get('wallet_uuid')}:{data.get('idempotency_key')}"
        )
        exists = await check_or_set_ik_in_redis(redis_key=redis_key)
        if not exists:
            logger.error(
                f"Transaction already exists {data.get('idempotency_key')}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already processing or done"
            )
    else:
        logger.error(
            f"Idempotency key is required {data.get('idempotency_key')}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency key is required"
        )

    if data.get("operation_type").lower() == "deposit":
        return await deposit(data=data, session=session)
    elif data.get("operation_type").lower() == "withdraw":
        return await withdraw(data=data, redis_key=redis_key, session=session)
    else:
        logger.error(f"Invalid operation type {data.get('operation_type')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type"
        )
