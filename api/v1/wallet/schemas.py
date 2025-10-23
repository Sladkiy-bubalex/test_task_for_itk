from pydantic import BaseModel
from decimal import Decimal


class GetWalletResponseSchema(BaseModel):
    balance: Decimal


class UpdateWalletRequestSchema(BaseModel):
    operation_type: str
    amount: Decimal
    idempotency_key: str


class UpdateWalletResponseSchema(BaseModel):
    status: str
    message: str
