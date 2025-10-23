from config import logger, pwd_context
from fastapi import HTTPException, status
from database.dependencies import SessionDependancy
from database.models.users import User
from api.v1.users.services import get_user_by_username


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_user(session: SessionDependancy, user_data: dict) -> User:
    user = await get_user_by_username(
        session=session,
        username=user_data["username"]
    )
    if user is not None:
        logger.error("User already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    new_user = User(**user_data)
    session.add(new_user)
    await session.commit()

    return new_user
