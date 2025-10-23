import jwt
from auth_schemes import oauth2_scheme
from typing import Annotated
from fastapi import Depends, HTTPException, status

from config import SECRET_KEY, ALGORITHM, logger, pwd_context

from database.models.users import User
from database.dependencies import SessionDependancy

from api.v1.users.errors import user_not_found_exception
from api.v1.users.authorization.errors import invalid_token_exception
from api.v1.users.authorization.schemas import TokenDataSchema
from api.v1.users.services import get_user_by_username


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


async def authenticate_user(
    session: SessionDependancy,
    user_data: dict
) -> User:
    user = await get_user_by_username(session, user_data["username"])
    if not user:
        logger.error(f"User not found {user_data['username']}")
        raise user_not_found_exception

    if not verify_password(user_data["password"], user.hashed_password):
        logger.error(f"Incorrect password when verifying user {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDependancy
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        if payload is None:
            logger.error("Invalid token when decrypting")
            raise invalid_token_exception
        token_data = TokenDataSchema(username=payload.get("username"))

    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        raise invalid_token_exception

    user = await get_user_by_username(session, token_data.username)

    if user is None:
        logger.error("User not found")
        raise user_not_found_exception
    return user
