import jwt
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from database.dependencies import SessionDependancy
from database.models.users import User
from config import ACCESS_TOKEN_EXPIRE_HOURS, SECRET_KEY, ALGORITHM


async def get_user_by_username(
    session: SessionDependancy,
    username: str
) -> User:
    query = select(User).filter(User.username == username)
    orm_obj = await session.scalar(query)
    return orm_obj


async def create_access_token(user_obj: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        hours=ACCESS_TOKEN_EXPIRE_HOURS
    )
    to_encode = {
        "sub": str(user_obj.id),
        "username": user_obj.username,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
