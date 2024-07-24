from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.transaction_repository import add_transaction, get_transaction_by_id
from crud.user_repository import get_user_by_id
from db.database import get_session
from schemas.accounts_schema import InboxTransaction, TransactionDone
from transaction_security.transaction_checking import signature_is_correct


transactionsrouter = APIRouter()


@transactionsrouter.post("/")
async def do_transaction(
    transaction_data: InboxTransaction,
    session: AsyncSession = Depends(get_session)
):
    if signature_is_correct(transaction_data):
        transaction = await get_transaction_by_id(
            session, transaction_data.transaction_id
        )
        if transaction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction already exists"
            )

        user = await get_user_by_id(session, transaction_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't exist"
            )
        new_transaction = await add_transaction(session, transaction_data)
        serialized_transaction = TransactionDone(
            transaction_id=new_transaction.transaction_id,
            user_id=new_transaction.account.user_id,
            account_id=new_transaction.account.user_account_id,
            amount=new_transaction.amount,
            transaction_date=new_transaction.transaction_date
        )

        return serialized_transaction

    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="signature is not correct"
        )
