from decimal import Decimal
from database.database import BaseModel, Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    UUID as UUIDType, ForeignKey,
    Numeric, CheckConstraint, UniqueConstraint
)
from uuid import UUID, uuid4
from enum import Enum


class OperationTypeEnum(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class PendingEnum(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    wallets: Mapped[list["Wallet"]] = relationship(
        "Wallet",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"


class Wallet(Base):
    __tablename__ = "wallets"

    uuid: Mapped[UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal(0.0)
    )
    user: Mapped[User] = relationship("User", back_populates="wallets")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="non_negative_balance"),
    )

    def __repr__(self):
        return (f"Wallet(uuid={self.uuid}, user_id={self.user_id}, "
                f"balance={self.balance})")


class Transaction(BaseModel):
    __tablename__ = "transactions"

    wallet_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("wallets.uuid"),
        nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    type_operation: Mapped[OperationTypeEnum] = mapped_column(
        String,
        nullable=False
    )
    status: Mapped[PendingEnum] = mapped_column(String, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(
        String,
        nullable=True,
        unique=True
    )
    wallet: Mapped["Wallet"] = relationship(
        "Wallet",
        back_populates="transactions",
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint(
            "wallet_uuid",
            "idempotency_key",
            name="uix_wallet_uuid_idemp"
        ),
    )

    def __repr__(self):
        return (f"Transaction(id={self.id}, wallet_uuid={self.wallet_uuid}, "
                f"amount={self.amount}, type_operation={self.type_operation}, "
                f"status={self.status})")
