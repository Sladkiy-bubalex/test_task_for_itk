from fastapi import APIRouter
from .users import router as users_router
from .wallet.wallet import router as wallet_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])
