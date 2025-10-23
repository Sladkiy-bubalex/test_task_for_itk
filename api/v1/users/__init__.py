from fastapi import APIRouter
from .authorization.auth import router as auth_router
from .registration.registrations import router as registration_router


router = APIRouter()
router.include_router(auth_router, prefix="/authorization")
router.include_router(registration_router, prefix="/registration")
