from typing import Optional
from uuid import UUID

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import Account, Transaction
from schemas.accounts_schema import InboxTransaction


async def get_transaction_by_id(
    session: AsyncSession, transaction_id: UUID
) -> Optional[Transaction]:
    query = select(Transaction).filter_by(transaction_id=transaction_id)
    result = await session.execute(query)
    return result.scalars().first()


async def add_transaction(
        session: AsyncSession,
        transaction_data: InboxTransaction
) -> Transaction:
    query = select(Account).filter_by(
        user_id=transaction_data.user_id,
        user_account_id=transaction_data.account_id
    )
    result = await session.execute(query)
    account = result.scalar()

    if not account:
        account = Account(
            user_id=transaction_data.user_id,
            user_account_id=transaction_data.account_id,
            balance=transaction_data.amount
        )
        session.add(account)
        await session.flush()
    else:
        account.balance += transaction_data.amount
        await session.flush()

    new_transaction = Transaction(
        transaction_id=transaction_data.transaction_id,
        account_id=account.id,
        amount=transaction_data.amount
    )
    session.add(new_transaction)

    await session.commit()
    await session.refresh(new_transaction, attribute_names=["account"])

    return new_transaction
