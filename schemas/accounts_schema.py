from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class UserAccount(BaseModel):
    account_id: int
    balance: Decimal


class UserTransaction(BaseModel):
    transaction_id: UUID
    account_id: int
    amount: Decimal
    transaction_date: datetime


class InboxTransaction(BaseModel):
    transaction_id: UUID
    user_id: int
    account_id: int
    amount: Decimal
    signature: str


class TransactionDone(UserTransaction):
    user_id: int
