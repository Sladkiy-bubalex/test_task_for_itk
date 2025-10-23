from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated


SessionDependancy = Annotated[
    AsyncSession, Depends(get_session, use_cache=True)
]
