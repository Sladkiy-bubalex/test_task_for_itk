from database.models.users import Wallet
from database.dependencies import SessionDependancy
from fastapi import HTTPException, status
from config import logger, async_redis_client
from sqlalchemy import text, select


async def check_or_set_ik_in_redis(redis_key: str) -> bool:
    """
    Проверка в Redis

    :param redis_key: ключ в Redis
    :return: True если ключ не существует и установлен,
    False если ключ существует
    """
    exists = await async_redis_client.set(
        name=redis_key,
        value="1",
        ex=60,
        nx=True
    )
    return exists is True


async def create_wallet(session: SessionDependancy, user_id: int) -> Wallet:
    wallet = Wallet(user_id=user_id)
    session.add(wallet)
    await session.commit()
    return wallet


async def get_wallet_by_uuid(
    session: SessionDependancy,
    wallet_uuid: str
) -> Wallet:
    query = select(Wallet).where(Wallet.uuid == wallet_uuid)
    result = await session.execute(query)
    wallet = result.unique().scalar_one_or_none()
    if wallet is None:
        logger.error(f"Wallet not found {wallet_uuid}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    return wallet


async def deposit(data: dict, session: SessionDependancy):
    """
    Добавление средств на кошелек

    :param data: данные транзакции
    :param session: сессия базы данных
    :return: статус транзакции
    """

    result = await session.execute(
        text(
            """
            SELECT id FROM transactions
            WHERE wallet_uuid = :wallet_uuid AND
            idempotency_key = :idempotency_key
            """
        ),
        {
            "wallet_uuid": data.get("wallet_uuid"),
            "idempotency_key": data.get("idempotency_key"),
        },
    )
    if result.scalar():
        logger.error(
            f"Transaction already exists {data.get('idempotency_key')}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already processing or done",
        )

    await session.execute(
        text(
            """
            SELECT uuid FROM wallets
            WHERE uuid = :wallet_uuid
            FOR UPDATE
            """
        ),
        {"wallet_uuid": data.get("wallet_uuid")},
    )

    await session.execute(
        text(
            """
            UPDATE wallets
            SET balance = balance + :amount
            WHERE uuid = :wallet_uuid
            """
        ),
        {
            "wallet_uuid": data.get("wallet_uuid"),
            "amount": data.get("amount"),
        },
    )

    await session.execute(
        text(
            """
            INSERT INTO transactions (
                wallet_uuid, amount, type_operation, status, idempotency_key
            )
            VALUES (
                :wallet_uuid, :amount, 'deposit', 'completed', :idempotency_key
            )
            """
        ),
        {
            "wallet_uuid": data.get("wallet_uuid"),
            "amount": data.get("amount"),
            "idempotency_key": data.get("idempotency_key"),
        },
    )
    await session.commit()

    return {"status": "success", "message": "Deposit completed"}


async def withdraw(data: dict, redis_key: str, session: SessionDependancy):
    """
    Возврат средств на кошелек

    :param data: данные транзакции
    :param redis_key: ключ в Redis
    :param session: сессия базы данных
    :return: статус транзакции
    """

    # Дополнительная проверка в БД
    result = await session.execute(
        text(
            """
            SELECT id FROM transactions
            WHERE wallet_uuid = :wallet_uuid AND
            idempotency_key = :idempotency_key
            """
        ),
        {
            "wallet_uuid": data.get("wallet_uuid"),
            "idempotency_key": data.get("idempotency_key"),
        },
    )
    if result.scalar():
        logger.error(
            f"Transaction already exists {data.get('idempotency_key')}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already processing or done",
        )

    await session.execute(
        text(
            """
            SELECT uuid FROM wallets
            WHERE uuid = :wallet_uuid
            FOR UPDATE
            """
        ),
        {"wallet_uuid": data.get("wallet_uuid")},
    )

    result = await session.execute(
        text(
            """
            UPDATE wallets
            SET balance = balance - :amount
            WHERE uuid = :wallet_uuid AND balance >= :amount
            RETURNING uuid
            """
        ),
        {
            "wallet_uuid": data.get("wallet_uuid"),
            "amount": data.get("amount"),
        },
    )

    if not result.first():
        await async_redis_client.delete(redis_key)
        logger.error(f"Insufficient funds {data.get('idempotency_key')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds",
        )

    await session.execute(
        text(
            """
            INSERT INTO transactions (
                wallet_uuid, amount, type_operation, status, idempotency_key
            )
            VALUES (
                :wallet_uuid,
                :amount,
                'withdraw',
                'completed',
                :idempotency_key
            )
            """
        ),
        {
            "wallet_uuid": data.get("wallet_uuid"),
            "amount": -data.get("amount"),
            "idempotency_key": data.get("idempotency_key"),
        },
    )
    await session.commit()

    return {"status": "success", "message": "Withdraw completed"}
