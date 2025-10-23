from fastapi import Depends
from typing import Annotated
from database.models.users import User
from api.v1.users.authorization.services import get_current_user


AccessDependancy = Annotated[User, Depends(get_current_user)]
